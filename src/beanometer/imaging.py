"""Reading a captured frame into an array the rest of the pipeline can use.

A frame arrives in two planes that share a capture but not a coordinate
system. The raw plane is linear sensor data; the JPEG plane has been
demosaiced, tone-mapped and rotated by the camera. Everything downstream
states which plane it was measured in, because a position in one does not
carry to the other.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

# The DNG records its as-shot illuminant as `AsShotWhiteXY`, a chromaticity,
# where the more usual choice is `AsShotNeutral`. LibRaw reads the latter, so
# the as-shot multipliers arrive empty and the daylight ones stand in. Which
# fixed set is used barely matters: the sheet is a known reflectance in every
# frame, and photometry normalises against it. What matters is that the set is
# fixed, since a per-frame estimate would move with how much of the sheet the
# beans cover.
_DAYLIGHT_WB = "daylight"


@dataclass(frozen=True)
class Capture:
    """The pixels of one frame, and what they mean.

    `rgb` is (h, w, 3), float32, sRGB primaries, normalised so that 1.0 is the
    sensor's white level. It is scene-linear when `linear` is true, and
    display-referred otherwise.
    """

    rgb: np.ndarray
    plane: str
    linear: bool
    source: Path
    scale: float

    @property
    def shape_px(self) -> tuple[int, int]:
        return self.rgb.shape[0], self.rgb.shape[1]


def load_capture(path: Path | str, *, plane: str, scale: float = 1.0) -> Capture:
    """Read one frame, optionally at a fraction `scale` of its full size.

    Only `scale` of 1.0 and 0.5 are honoured on the raw plane, where halving
    is free: it takes one photosite quad to a pixel and skips demosaicing.
    """
    path = Path(path)
    if plane == "dng":
        return _load_dng(path, scale=scale)
    if plane == "jpeg":
        return _load_jpeg(path, scale=scale)
    raise ValueError(f"unknown plane {plane!r}")


def _load_dng(path: Path, *, scale: float) -> Capture:
    import rawpy

    if scale not in (1.0, 0.5):
        raise ValueError("the raw plane is read at full size or at half")

    with rawpy.imread(str(path)) as raw:
        rgb16 = raw.postprocess(
            # Linear, unbrightened, with a fixed white balance: the pipeline
            # wants sensor response, not a picture.
            gamma=(1.0, 1.0),
            no_auto_bright=True,
            output_bps=16,
            use_camera_wb=False,
            use_auto_wb=False,
            user_wb=list(raw.daylight_whitebalance),
            half_size=(scale == 0.5),
            # The orientation tag is applied here, so the array is upright and
            # matches what a person sees when annotating.
            user_flip=-1,
        )
    return Capture(
        rgb=(rgb16.astype(np.float32) / 65535.0),
        plane="dng",
        linear=True,
        source=path,
        scale=scale,
    )


def _load_jpeg(path: Path, *, scale: float) -> Capture:
    from PIL import Image

    with Image.open(path) as image:
        image = image.convert("RGB")
        if scale != 1.0:
            size = (round(image.width * scale), round(image.height * scale))
            image = image.resize(size, Image.Resampling.BOX)
        rgb = np.asarray(image, dtype=np.float32) / 255.0
    return Capture(rgb=rgb, plane="jpeg", linear=False, source=path, scale=scale)


def to_display(capture: Capture, *, exposure: float | None = None) -> np.ndarray:
    """An 8-bit sRGB view of a capture, for a person to look at.

    Linear captures are stretched so that the brightest few pixels reach the
    top of the range and then gamma-encoded. Nothing measured is taken from
    the result.
    """
    rgb = capture.rgb
    if capture.linear:
        if exposure is None:
            white = float(np.percentile(rgb, 99.9))
            exposure = 1.0 / max(white, 1e-6)
        rgb = np.clip(rgb * exposure, 0.0, 1.0) ** (1.0 / 2.2)
    return (np.clip(rgb, 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8)


def full_size_px(path: Path | str, *, plane: str) -> tuple[int, int]:
    """The (height, width) a plane has at full size, from its header alone.

    Annotated corners are stored in full-size coordinates, so this is what
    turns them into a principal point without decoding the frame.
    """
    path = Path(path)
    if plane == "jpeg":
        from PIL import Image

        with Image.open(path) as image:
            width, height = image.size
        return height, width
    if plane == "dng":
        import rawpy

        with rawpy.imread(str(path)) as raw:
            sizes = raw.sizes
        # Flips 5 and 6 are the quarter turns, which exchange the axes.
        if sizes.flip in (5, 6):
            return sizes.raw_width, sizes.raw_height
        return sizes.raw_height, sizes.raw_width
    raise ValueError(f"unknown plane {plane!r}")
