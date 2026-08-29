"""One photograph to one row of numbers.

Everything expensive happens here — decoding raw, warping the sheet flat,
resolving pixels into coffee — and everything after it works on the table
this writes. That seam is what lets the calibration and the reporting be
re-run in a second while the measuring stage takes minutes.

Two observables come out of the same rectified sheet, so that the two
pathways differ in what they read and in nothing else: the coffee-covered
area, and the number of beans.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from dataclasses import fields as fields_of
from pathlib import Path

import numpy as np

from . import beans as beans_module
from .corners import Corners
from .geometry import (
    pose_from_corners,
    rectangle_aspect,
    rectification_from_corners,
    rectify,
    sampling_px_per_mm,
)
from .imaging import load_capture
from .instruments import camera_for
from .photometry import normalise_to_paper, paper_white_field
from .segment import coffee_coverage, inset_mask
from .session import Frame, Session

DEFAULT_PX_PER_MM = 12.0
DEFAULT_MARGIN_MM = 2.0

# Derived artifacts live apart from the photographs, which are written once
# and never edited.
DERIVED_ROOT = Path("data/derived")


def default_output(session: Session) -> Path:
    return DERIVED_ROOT / session.directory.name / "measurements.csv"


@dataclass(frozen=True)
class FrameMeasurement:
    """What one frame yielded, in the units the calibration works in."""

    stem: str
    stage: str
    mass_g: float
    mass_source: str
    corner_source: str
    plane: str
    px_per_mm: float
    margin_mm: float
    convention: str
    # Where the camera stood, and how well the corners agree with a sheet.
    sampled_px_per_mm: float
    distance_mm: float
    tilt_deg: float
    residual_px: float
    aspect: float
    # What the sheet looked like.
    paper_reference: float
    coffee_reference: float
    paper_noise: float
    measured_area_mm2: float
    # The two observables.
    covered_area_mm2: float
    bean_count: int
    # What the observables could not account for.
    coverage_in_margin_mm2: float
    blob_count: int
    unresolved_area_mm2: float
    median_bean_area_mm2: float

    @property
    def coverage_fraction(self) -> float:
        return self.covered_area_mm2 / self.measured_area_mm2


def measure_frame(
    session: Session,
    frame: Frame,
    corners: Corners,
    *,
    plane: str = "dng",
    px_per_mm: float = DEFAULT_PX_PER_MM,
    margin_mm: float = DEFAULT_MARGIN_MM,
    convention: str = "soft",
    overlay_path: Path | None = None,
) -> FrameMeasurement:
    """Read one frame all the way to its observables."""
    capture = load_capture(frame.path(plane), plane=plane, scale=1.0)
    rectification = rectification_from_corners(
        corners.corners_px, size_mm=session.substrate_mm, px_per_mm=px_per_mm
    )
    sheet = rectify(capture.rgb, rectification)

    field = paper_white_field(sheet)
    coverage = coffee_coverage(
        normalise_to_paper(sheet, field), convention=convention
    )
    inside = inset_mask(
        coverage.fraction.shape, px_per_mm=px_per_mm, margin_mm=margin_mm
    )
    pixel_area_mm2 = rectification.pixel_area_mm2
    covered_area_mm2 = float(coverage.fraction[inside].sum()) * pixel_area_mm2
    in_margin_mm2 = float(coverage.fraction[~inside].sum()) * pixel_area_mm2

    field_of_beans = beans_module.separate(
        coverage.fraction, px_per_mm=px_per_mm, inside=inside
    )

    height_px, width_px = corners.plane_size_px or capture.shape_px
    principal_px = (width_px / 2.0, height_px / 2.0)
    focal_px = camera_for(session.record).focal_px()
    pose = pose_from_corners(
        corners.corners_px,
        size_mm=session.substrate_mm,
        focal_px=focal_px,
        principal_px=principal_px,
    )
    long_px_per_mm, short_px_per_mm = sampling_px_per_mm(
        rectification_from_corners(
            corners.corners_px, size_mm=session.substrate_mm, px_per_mm=1.0
        )
    )

    if overlay_path is not None:
        _write_overlay(overlay_path, sheet, field, coverage.fraction, field_of_beans)

    return FrameMeasurement(
        stem=frame.stem,
        stage=frame.stage,
        mass_g=frame.mass_g,
        mass_source=frame.mass_source,
        corner_source=corners.source,
        plane=plane,
        px_per_mm=px_per_mm,
        margin_mm=margin_mm,
        convention=convention,
        sampled_px_per_mm=0.5 * (long_px_per_mm + short_px_per_mm),
        distance_mm=pose.distance_mm,
        tilt_deg=pose.tilt_deg,
        residual_px=pose.reprojection_rms_px,
        aspect=rectangle_aspect(corners.corners_px, focal_px, principal_px),
        paper_reference=coverage.paper_reference,
        coffee_reference=coverage.coffee_reference,
        paper_noise=coverage.paper_noise,
        measured_area_mm2=float(inside.sum()) * pixel_area_mm2,
        covered_area_mm2=covered_area_mm2,
        bean_count=field_of_beans.count,
        coverage_in_margin_mm2=in_margin_mm2,
        blob_count=field_of_beans.blob_count,
        unresolved_area_mm2=field_of_beans.unresolved_area_mm2,
        median_bean_area_mm2=field_of_beans.median_area_mm2,
    )


def measure_session(
    session: Session,
    entries: dict[str, Corners],
    *,
    plane: str = "dng",
    px_per_mm: float = DEFAULT_PX_PER_MM,
    margin_mm: float = DEFAULT_MARGIN_MM,
    convention: str = "soft",
    overlay_directory: Path | None = None,
    progress: bool = True,
) -> list[FrameMeasurement]:
    """Measure every frame the corner file covers."""
    if overlay_directory is not None:
        overlay_directory.mkdir(parents=True, exist_ok=True)
    measurements = []
    for frame in session.frames:
        corners = entries.get(frame.stem)
        if corners is None or corners.source == "unusable":
            continue
        measurement = measure_frame(
            session,
            frame,
            corners,
            plane=plane,
            px_per_mm=px_per_mm,
            margin_mm=margin_mm,
            convention=convention,
            overlay_path=(
                None
                if overlay_directory is None
                else overlay_directory / f"{frame.stem}.jpg"
            ),
        )
        measurements.append(measurement)
        if progress:
            print(
                f"  {measurement.stem[-6:]}  {measurement.stage:<15}"
                f"{measurement.mass_g:5.1f} g"
                f"  area {measurement.covered_area_mm2:8.1f} mm2"
                f"  beans {measurement.bean_count:4d}",
                flush=True,
            )
    return measurements


def to_frame(measurements: list[FrameMeasurement]):
    """The measurements as a pandas table, one row per frame."""
    import pandas as pd

    return pd.DataFrame([asdict(measurement) for measurement in measurements])


def read_measurements(path: Path) -> list[FrameMeasurement]:
    """Read back a table this module wrote."""
    import pandas as pd

    table = pd.read_csv(path)
    fields = {field.name: field.type for field in fields_of(FrameMeasurement)}
    return [
        FrameMeasurement(
            **{
                name: (int(row[name]) if fields[name] is int else row[name])
                for name in fields
            }
        )
        for _, row in table.iterrows()
    ]


def _write_overlay(
    path: Path,
    sheet: np.ndarray,
    field: np.ndarray,
    fraction: np.ndarray,
    field_of_beans: beans_module.BeanField,
) -> None:
    """A picture of what the frame was resolved into, for a person to check."""
    import cv2

    normalised = np.clip(sheet / np.maximum(field, 1e-9), 0.0, 1.0) ** (1 / 2.2)
    view = (normalised * 255.0).astype(np.uint8)
    edges = cv2.Canny((fraction * 255).astype(np.uint8), 60, 160)
    view[edges > 0] = (255, 40, 40)
    boundaries = field_of_beans.labels != cv2.erode(
        field_of_beans.labels.astype(np.float32), np.ones((3, 3), np.uint8)
    ).astype(np.int32)
    view[boundaries & (field_of_beans.labels > 0)] = (40, 200, 255)
    scale = 1400 / max(view.shape[:2])
    small = cv2.resize(view, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    cv2.imwrite(str(path), small[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 88])
