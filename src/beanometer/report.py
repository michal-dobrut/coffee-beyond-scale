"""Tables a person reads, printed from what the stages wrote."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .corners import FILE_NAME, corners_path, load_corners
from .geometry import (
    focal_length_px,
    pose_from_corners,
    rectangle_aspect,
    rectification_from_corners,
    sampling_px_per_mm,
)
from .estimate import PATHWAYS, Pathway, fit, residuals, spread_by_stage
from .imaging import full_size_px
from .instruments import camera_for
from .measure import FrameMeasurement, read_measurements
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
            f"{'-' if self_focal is None else f'{self_focal:.0f}':>9}"
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
    _print_substrate_fit(session, rows, name=name)


def _print_substrate_fit(session: Session, rows: list[dict], *, name: str) -> None:
    """What size of sheet the corners themselves say was photographed.

    The corners fix the ratio of the two edges but not their absolute length,
    so this recovers the short edge with the long one held at its nominal
    value. A sheet that is not the size the record claims puts a scale error
    into every area, and ISO 216 allows two millimetres either way.
    """
    from scipy.optimize import minimize_scalar

    plane, entries = load_corners(corners_path(session.directory, name=name))
    width_mm, height_mm = session.substrate_mm
    focal_px = camera_for(session.record).focal_px()
    placed = [
        (entries[row["stem"]].corners_px, entries[row["stem"]].plane_size_px)
        for row in rows
    ]

    def residual(candidate_mm: float) -> float:
        total = 0.0
        for corners_px, size_px in placed:
            principal_px = (size_px[1] / 2.0, size_px[0] / 2.0)
            total += (
                pose_from_corners(
                    corners_px,
                    size_mm=(candidate_mm, height_mm),
                    focal_px=focal_px,
                    principal_px=principal_px,
                ).reprojection_rms_px
                ** 2
            )
        return total

    span = (0.94 * width_mm, 1.06 * width_mm)
    fitted = minimize_scalar(residual, bounds=span, method="bounded").x
    before = np.sqrt(residual(width_mm) / len(placed))
    after = np.sqrt(residual(fitted) / len(placed))
    print(
        f"substrate: recorded as {width_mm:g} x {height_mm:g} mm. Holding the long "
        f"edge, the corners fit a short edge of {fitted:.2f} mm, which takes the "
        f"residual from {before:.2f} to {after:.2f} px. The corners fix the ratio "
        f"of the edges and not their length, so an error in both together is "
        f"invisible here and scales every area."
    )


def print_results(session: Session, measurements_path: Path) -> None:
    """Fit one constant per pathway and print what is left over."""
    measurements = read_measurements(Path(measurements_path))
    if not measurements:
        print(f"no measurements in {measurements_path}")
        return
    first = measurements[0]
    print(
        f"{session.id}: {len(measurements)} frames, {first.plane} plane, rectified at "
        f"{first.px_per_mm:g} px/mm, {first.margin_mm:g} mm rim left out, "
        f"{first.convention} boundary"
    )

    _print_observables(measurements)
    for pathway in PATHWAYS:
        _print_pathway(measurements, pathway)


def _print_observables(measurements: list[FrameMeasurement]) -> None:
    header = (
        f"\n{'frame':<8}{'stage':<16}{'g':>6}{'area mm2':>10}{'cover%':>8}"
        f"{'beans':>7}{'blobs':>7}{'unres mm2':>11}{'bean mm2':>10}{'rim mm2':>9}"
    )
    print(header)
    print("-" * len(header))
    for measurement in measurements:
        print(
            f"{measurement.stem[-6:]:<8}{measurement.stage:<16}"
            f"{measurement.mass_g:>6.1f}{measurement.covered_area_mm2:>10.0f}"
            f"{100 * measurement.coverage_fraction:>8.2f}"
            f"{measurement.bean_count:>7d}{measurement.blob_count:>7d}"
            f"{measurement.unresolved_area_mm2:>11.0f}"
            f"{measurement.median_bean_area_mm2:>10.1f}"
            f"{measurement.coverage_in_margin_mm2:>9.0f}"
        )


def _print_pathway(measurements: list[FrameMeasurement], pathway: Pathway) -> None:
    calibration = fit(measurements, pathway)
    print(
        f"\n=== {pathway.name} — {pathway.description} ===\n"
        f"one constant, fitted on {len(calibration.frames)} frames whose mass the "
        f"balance read:\n"
        f"  {calibration.grams_per_unit:.6g} g per {pathway.unit}, "
        f"in-sample scatter {100 * calibration.scatter_rel:.2f}%"
    )

    rows = residuals(measurements, calibration)
    scored = [
        abs(relative) for _, _, relative in rows if not np.isnan(relative)
    ]
    print(
        f"  relative error against the balance: median {100 * np.median(scored):.2f}%, "
        f"95th percentile {100 * np.percentile(scored, 95):.2f}%"
    )

    print(f"\n  {'frame':<8}{'stage':<16}{'balance g':>11}{'read g':>9}{'error':>9}")
    for measurement, estimate, relative in rows:
        error = "-" if np.isnan(relative) else f"{100 * relative:+.1f}%"
        print(
            f"  {measurement.stem[-6:]:<8}{measurement.stage:<16}"
            f"{measurement.mass_g:>11.1f}{estimate.mass_g:>9.2f}{error:>9}"
        )

    print(f"\n  one sheet, several photographs of it:")
    print(
        f"  {'stage':<16}{'g':>6}{'frames':>8}{'mean':>12}{'sd':>10}{'spread':>9}"
    )
    for entry in spread_by_stage(measurements, pathway):
        spread = (
            "-" if np.isnan(entry.spread_rel) else f"{100 * entry.spread_rel:.2f}%"
        )
        print(
            f"  {entry.stage:<16}{entry.mass_g:>6.1f}{entry.frames:>8}"
            f"{entry.mean:>12.1f}{entry.sd:>10.1f}{spread:>9}"
        )
