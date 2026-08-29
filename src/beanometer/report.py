"""Tables a person reads, printed from what the stages wrote."""

from __future__ import annotations

import numpy as np

from .corners import FILE_NAME, corners_path, load_corners
from .geometry import (
    focal_length_px,
    pose_from_corners,
    rectangle_aspect,
    rectification_from_corners,
    sampling_px_per_mm,
)
from .imaging import full_size_px
from .instruments import camera_for
from .session import Session


def frame_geometry(session: Session, *, name: str = FILE_NAME) -> list[dict]:
    """What the annotated corners imply about each frame, one row per frame.

    Distances are to the centre of the sheet and tilt is against its normal.
    The recovered aspect ratio is the residual on the annotation: it uses the
    focal length the camera reports, so a sheet that comes back at anything
    but 297 by 210 is the corners, the lens distortion, or that focal length.
    """
    plane, entries = load_corners(corners_path(session.directory, name=name))
    camera = camera_for(session.record)
    rows = []
    for frame in session.frames:
        entry = entries.get(frame.stem)
        if entry is None or entry.source == "unusable":
            continue
        corners_px = entry.corners_px
        height_px, width_px = entry.plane_size_px or full_size_px(
            frame.path(plane), plane=plane
        )
        principal_px = (width_px / 2.0, height_px / 2.0)
        focal_px = camera.focal_px()
        rectification = rectification_from_corners(
            corners_px, size_mm=session.substrate_mm, px_per_mm=1.0
        )
        long_px_per_mm, short_px_per_mm = sampling_px_per_mm(rectification)
        pose = pose_from_corners(
            corners_px,
            size_mm=session.substrate_mm,
            focal_px=focal_px,
            principal_px=principal_px,
        )
        self_focal_px = focal_length_px(corners_px, principal_px)
        rows.append(
            {
                "stem": frame.stem,
                "stage": frame.stage,
                "mass_g": frame.mass_g,
                "source": entry.source,
                "px_per_mm_long": long_px_per_mm,
                "px_per_mm_short": short_px_per_mm,
                "aspect": rectangle_aspect(corners_px, focal_px, principal_px),
                "residual_px": pose.reprojection_rms_px,
                "self_focal_px": self_focal_px,
                "distance_mm": pose.distance_mm,
                "tilt_deg": pose.tilt_deg,
                "sheet_fraction_of_frame": _sheet_fraction(
                    corners_px, width_px, height_px
                ),
            }
        )
    return rows


def _sheet_fraction(corners_px: np.ndarray, width_px: int, height_px: int) -> float:
    """Share of the frame the sheet covers, by the shoelace area of its quad."""
    x, y = corners_px[:, 0], corners_px[:, 1]
    area = 0.5 * abs(float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))
    return area / (width_px * height_px)


def print_corner_summary(session: Session, *, name: str = FILE_NAME) -> None:
    rows = frame_geometry(session, name=name)
    if not rows:
        print(f"no corners in {corners_path(session.directory, name=name)}")
        return

    aspect_target = max(session.substrate_mm) / min(session.substrate_mm)
    header = (
        f"{'frame':<12}{'stage':<16}{'px/mm':>12}{'aspect':>9}{'err%':>7}"
        f"{'resid px':>9}{'f_self':>9}{'dist mm':>9}{'tilt':>7}{'sheet %':>9}"
    )
    print(header)
    print("-" * len(header))
    for row in rows:
        self_focal = row["self_focal_px"]
        print(
            f"{row['stem'][-6:]:<12}{row['stage']:<16}"
            f"{row['px_per_mm_long']:>6.1f}/{row['px_per_mm_short']:<5.1f}"
            f"{row['aspect']:>9.4f}"
            f"{100 * (row['aspect'] - aspect_target) / aspect_target:>7.2f}"
            f"{row['residual_px']:>9.1f}"
            f"{'—' if self_focal is None else f'{self_focal:.0f}':>9}"
            f"{row['distance_mm']:>9.0f}{row['tilt_deg']:>7.1f}"
            f"{100 * row['sheet_fraction_of_frame']:>9.1f}"
        )

    aspects = np.array([row["aspect"] for row in rows])
    residuals = np.array([row["residual_px"] for row in rows])
    print()
    print(
        f"aspect against {aspect_target:.4f}: median {np.median(aspects):.4f}, "
        f"spread {100 * np.std(aspects) / aspect_target:.2f}% of it, "
        f"worst {100 * np.max(np.abs(aspects - aspect_target)) / aspect_target:.2f}%"
    )
    print(
        f"reprojection residual: median {np.median(residuals):.1f} px, "
        f"worst {residuals.max():.1f} px, putting that frame's worst corner "
        f"{3 * residuals.max():.0f} to {10 * residuals.max():.0f} px out"
    )
    camera = camera_for(session.record)
    print(
        f"camera: {camera.body} {camera.lens}, f = {camera.focal_length_mm} mm "
        f"({camera.equivalent_focal_mm:.1f} mm equivalent), "
        f"{camera.focal_px():.0f} px at full resolution"
    )
