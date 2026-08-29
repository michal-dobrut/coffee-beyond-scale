"""Fixed parameters of the instruments a session names.

The values and their standing are set out in the instrument background under
`docs/knowledge/`. They are held here rather than inline so that a session
record names an instrument and the pipeline looks up what that instrument is,
and so that one place changes when a figure is settled by calibration.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Camera:
    """One camera module, as its manufacturer and its own firmware describe it.

    `full_resolution_px` is (long side, short side) of the unbinned readout.
    `focal_length_mm` is the actual focal length, not the 35 mm equivalent.
    """

    body: str
    lens: str
    focal_length_mm: float
    pixel_pitch_um: float
    aperture_f: float
    full_resolution_px: tuple[int, int]

    @property
    def sensor_mm(self) -> tuple[float, float]:
        long_px, short_px = self.full_resolution_px
        return (
            long_px * self.pixel_pitch_um / 1000.0,
            short_px * self.pixel_pitch_um / 1000.0,
        )

    @property
    def sensor_diagonal_mm(self) -> float:
        long_mm, short_mm = self.sensor_mm
        return math.hypot(long_mm, short_mm)

    @property
    def crop_factor(self) -> float:
        """Against the 43.267 mm diagonal of a 36 by 24 mm frame."""
        return math.hypot(36.0, 24.0) / self.sensor_diagonal_mm

    @property
    def equivalent_focal_mm(self) -> float:
        return self.focal_length_mm * self.crop_factor

    def focal_px(self, *, scale: float = 1.0) -> float:
        """Focal length in pixels of an image read at `scale` of full size."""
        return (self.focal_length_mm * 1000.0 / self.pixel_pitch_um) * scale

    def distance_mm(self, span_mm: float) -> float:
        """How far back the camera stands for `span_mm` to fill the long side."""
        long_mm, _ = self.sensor_mm
        return span_mm * self.focal_length_mm / long_mm

    def depth_of_field_mm(self, distance_mm: float, *, circle_px: float = 2.0) -> float:
        """Total depth in focus at `distance_mm`, for a circle of confusion of
        `circle_px` pixels.

        The far side of the field is unbounded near the hyperfocal distance;
        this is the symmetric approximation, which holds while the subject
        distance is far short of it.
        """
        circle_mm = circle_px * self.pixel_pitch_um / 1000.0
        return (
            2.0
            * self.aperture_f
            * circle_mm
            * (distance_mm / self.focal_length_mm) ** 2
        )

    @property
    def airy_diameter_um(self) -> float:
        """Airy disk diameter at 550 nm."""
        return 2.44 * 0.55 * self.aperture_f


CAMERAS: dict[tuple[str, str], Camera] = {
    ("Google Pixel 10 Pro", "main"): Camera(
        body="Google Pixel 10 Pro",
        lens="main",
        focal_length_mm=6.90,
        pixel_pitch_um=1.2,
        aperture_f=1.68,
        full_resolution_px=(8156, 6140),
    ),
}


def camera_for(record: dict) -> Camera:
    """The camera a session record names."""
    camera = record.get("camera", {})
    key = (str(camera.get("body", "")), str(camera.get("lens", "")))
    try:
        return CAMERAS[key]
    except KeyError:
        known = ", ".join(f"{body} {lens}" for body, lens in CAMERAS)
        raise KeyError(
            f"no instrument record for {key[0]} {key[1]}; known cameras are {known}"
        ) from None


# Roasted arabica, as the project premise states it. Both are population
# figures for a bean, not for this bag.
MEAN_BEAN_MASS_G = 0.145
SD_BEAN_MASS_G = 0.022
