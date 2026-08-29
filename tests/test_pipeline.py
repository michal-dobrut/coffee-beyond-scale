"""The measuring stages against a scene whose answer is known exactly.

Ellipses of known area, painted on paper of known reflectance, lit by a known
gradient, projected through a known camera. Nothing is estimated, so a
disagreement is the pipeline and not the photograph.
"""

from __future__ import annotations

import cv2
import numpy as np
import pytest

from beanometer.beans import separate
from beanometer.geometry import rectification_from_corners, rectify
from beanometer.photometry import normalise_to_paper, paper_white_field
from beanometer.segment import coffee_coverage, inset_mask
from tests.test_geometry import A4_MM, FOCAL_PX, NEAR_NADIR, PRINCIPAL_PX, project

PX_PER_MM = 12.0
PAPER_REFLECTANCE = 0.72
COFFEE_REFLECTANCE = 0.072
BEAN_SEMI_AXES_MM = (5.2, 3.3)
BEAN_AREA_MM2 = np.pi * BEAN_SEMI_AXES_MM[0] * BEAN_SEMI_AXES_MM[1]


def paint_sheet(bean_count: int, *, seed: int = 20260829, gradient: float = 3.0):
    """A rectified sheet carrying `bean_count` ellipses, and where they are.

    Returns (h, w, 3) float32 scene-linear radiance and the (n, 2) centres in
    millimetres. Beans are placed so that none touch, which is the condition
    the count is exact under.
    """
    width_mm, height_mm = A4_MM
    height_px = round(height_mm * PX_PER_MM)
    width_px = round(width_mm * PX_PER_MM)
    reflectance = np.full((height_px, width_px), PAPER_REFLECTANCE, np.float32)

    generator = np.random.default_rng(seed)
    centres_mm: list[tuple[float, float]] = []
    margin = 12.0
    clearance = 2.4 * BEAN_SEMI_AXES_MM[0]
    while len(centres_mm) < bean_count:
        candidate = (
            generator.uniform(margin, width_mm - margin),
            generator.uniform(margin, height_mm - margin),
        )
        if all(
            (candidate[0] - x) ** 2 + (candidate[1] - y) ** 2 > clearance**2
            for x, y in centres_mm
        ):
            centres_mm.append(candidate)
    for index, (x_mm, y_mm) in enumerate(centres_mm):
        cv2.ellipse(
            reflectance,
            (round(x_mm * PX_PER_MM), round(y_mm * PX_PER_MM)),
            (
                round(BEAN_SEMI_AXES_MM[0] * PX_PER_MM),
                round(BEAN_SEMI_AXES_MM[1] * PX_PER_MM),
            ),
            angle=index * 37 % 180,
            startAngle=0,
            endAngle=360,
            color=COFFEE_REFLECTANCE,
            thickness=-1,
            lineType=cv2.LINE_AA,
        )

    # An illumination that is brightest off-centre and falls away, which is
    # what a window through a roof does to a sheet on a table.
    rows, columns = np.mgrid[0:height_px, 0:width_px].astype(np.float32)
    radius = np.hypot(
        (columns - 0.38 * width_px) / width_px, (rows - 0.42 * height_px) / height_px
    )
    illumination = 1.0 / (1.0 + gradient * radius**2)
    radiance = (reflectance * illumination)[..., None] * np.array(
        [1.0, 0.98, 0.94], np.float32
    )
    return radiance.astype(np.float32), np.asarray(centres_mm)


def photograph(sheet: np.ndarray, *, noise: float = 0.004, seed: int = 7):
    """Project a rectified sheet through a known camera, as (h, w, 3)."""
    corners_px = project(*NEAR_NADIR)
    rectification = rectification_from_corners(
        corners_px, size_mm=A4_MM, px_per_mm=PX_PER_MM
    )
    frame = cv2.warpPerspective(
        sheet, np.linalg.inv(rectification.homography), (6140, 8156)
    )
    if noise:
        generator = np.random.default_rng(seed)
        frame += generator.normal(0.0, noise, frame.shape).astype(np.float32)
    return frame, corners_px


@pytest.fixture(scope="module")
def scene():
    sheet, centres_mm = paint_sheet(110)
    frame, corners_px = photograph(sheet)
    rectification = rectification_from_corners(
        corners_px, size_mm=A4_MM, px_per_mm=PX_PER_MM
    )
    recovered = rectify(frame, rectification)
    field = paper_white_field(recovered)
    return {
        "normalised": normalise_to_paper(recovered, field),
        "field": field,
        "recovered": recovered,
        "rectification": rectification,
        "beans": len(centres_mm),
    }


def test_the_paper_field_follows_the_illumination(scene):
    """Unobstructed paper comes back at 1.0 wherever it is on the sheet."""
    from beanometer.photometry import luminance

    grey = luminance(scene["normalised"])
    paper = grey > 0.75
    assert float(np.median(grey[paper])) == pytest.approx(1.0, abs=0.01)
    # The gradient spans a factor of two; what is left of it must not.
    height, width = grey.shape
    corner = grey[: height // 6, : width // 6]
    middle = grey[
        2 * height // 5 : 3 * height // 5, 2 * width // 5 : 3 * width // 5
    ]
    assert abs(np.median(corner[corner > 0.75]) - np.median(middle[middle > 0.75])) < 0.02


@pytest.mark.parametrize("convention", ["soft", "hard"])
def test_covered_area_comes_back(scene, convention):
    coverage = coffee_coverage(scene["normalised"], convention=convention)
    inside = inset_mask(coverage.fraction.shape, px_per_mm=PX_PER_MM, margin_mm=2.0)
    area_mm2 = float(coverage.fraction[inside].sum()) / PX_PER_MM**2
    assert area_mm2 == pytest.approx(scene["beans"] * BEAN_AREA_MM2, rel=0.03)


def test_the_count_is_exact_when_nothing_touches(scene):
    coverage = coffee_coverage(scene["normalised"])
    inside = inset_mask(coverage.fraction.shape, px_per_mm=PX_PER_MM, margin_mm=2.0)
    field_of_beans = separate(coverage.fraction, px_per_mm=PX_PER_MM, inside=inside)
    assert field_of_beans.count == scene["beans"]
    assert field_of_beans.unresolved_area_mm2 == 0.0
    assert field_of_beans.median_area_mm2 == pytest.approx(BEAN_AREA_MM2, rel=0.03)


def test_a_bare_sheet_reads_as_bare():
    """The floor of the area pathway, on a sheet with nothing on it."""
    sheet, _ = paint_sheet(0)
    frame, corners_px = photograph(sheet)
    rectification = rectification_from_corners(
        corners_px, size_mm=A4_MM, px_per_mm=PX_PER_MM
    )
    recovered = rectify(frame, rectification)
    normalised = normalise_to_paper(recovered, paper_white_field(recovered))
    inside = inset_mask(normalised.shape[:2], px_per_mm=PX_PER_MM, margin_mm=2.0)
    sheet_area_mm2 = float(inside.sum()) / PX_PER_MM**2
    for convention in ("soft", "hard"):
        coverage = coffee_coverage(normalised, convention=convention)
        area_mm2 = float(coverage.fraction[inside].sum()) / PX_PER_MM**2
        assert area_mm2 / sheet_area_mm2 < 0.002, convention


def test_the_soft_ramp_would_rectify_noise_without_its_dead_zone():
    """Why the ramp does not start at paper exactly.

    Clipping coverage below at zero turns symmetric noise about the paper
    level into one-sided coverage. This is the measurement that put the dead
    zone there, kept as a test so that removing it fails loudly.
    """
    sheet, _ = paint_sheet(0)
    frame, corners_px = photograph(sheet, noise=0.006)
    rectification = rectification_from_corners(
        corners_px, size_mm=A4_MM, px_per_mm=PX_PER_MM
    )
    recovered = rectify(frame, rectification)
    normalised = normalise_to_paper(recovered, paper_white_field(recovered))
    inside = inset_mask(normalised.shape[:2], px_per_mm=PX_PER_MM, margin_mm=2.0)
    sheet_area_mm2 = float(inside.sum()) / PX_PER_MM**2

    naive = coffee_coverage(normalised, paper_reference=1.0)
    guarded = coffee_coverage(normalised)
    naive_share = float(naive.fraction[inside].sum()) / PX_PER_MM**2 / sheet_area_mm2
    guarded_share = float(guarded.fraction[inside].sum()) / PX_PER_MM**2 / sheet_area_mm2
    assert naive_share > 20 * guarded_share
