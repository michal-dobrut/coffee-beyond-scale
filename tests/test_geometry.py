"""Geometry checked against a camera whose answer is known exactly."""

from __future__ import annotations

import cv2
import numpy as np
import pytest

from beanometer.geometry import (
    focal_length_px,
    order_corners,
    pose_from_corners,
    rectangle_aspect,
    rectification_from_corners,
    rectify,
    sampling_px_per_mm,
)

A4_MM = (210.0, 297.0)
FOCAL_PX = 5750.0
PRINCIPAL_PX = (3070.0, 4078.0)


def project(rotation_vector, translation_mm, size_mm=A4_MM):
    """Corners of a sheet as a known camera sees them, (4, 2), (x, y)."""
    width_mm, height_mm = size_mm
    object_mm = np.array(
        [[0, 0, 0], [width_mm, 0, 0], [width_mm, height_mm, 0], [0, height_mm, 0]],
        dtype=np.float64,
    )
    camera_matrix = np.array(
        [[FOCAL_PX, 0, PRINCIPAL_PX[0]], [0, FOCAL_PX, PRINCIPAL_PX[1]], [0, 0, 1]],
        dtype=np.float64,
    )
    points, _ = cv2.projectPoints(
        object_mm, np.asarray(rotation_vector, float), np.asarray(translation_mm, float),
        camera_matrix, None,
    )
    return points.reshape(4, 2)


OBLIQUE = ([0.25, -0.15, 0.05], [-100.0, -160.0, 250.0])
NEAR_NADIR = ([0.02, 0.01, 0.0], [-105.0, -148.0, 255.0])


@pytest.mark.parametrize("pose", [OBLIQUE, NEAR_NADIR])
def test_ordering_is_invariant_to_where_the_walk_starts(pose):
    corners = project(*pose)
    expected = order_corners(corners)
    for start in range(4):
        assert np.allclose(order_corners(np.roll(corners, start, axis=0)), expected)
    assert np.allclose(order_corners(corners[::-1]), expected)


def test_focal_length_comes_back_from_an_oblique_view():
    recovered = focal_length_px(project(*OBLIQUE), PRINCIPAL_PX)
    assert recovered == pytest.approx(FOCAL_PX, rel=1e-6)


@pytest.mark.parametrize("pose", [OBLIQUE, NEAR_NADIR])
def test_aspect_comes_back_from_any_view(pose):
    assert rectangle_aspect(project(*pose), FOCAL_PX, PRINCIPAL_PX) == pytest.approx(
        297.0 / 210.0, rel=1e-6
    )


def test_aspect_is_blind_along_some_directions():
    """The aspect ratio is a poor gate, and this records how poor.

    A corner dragged 300 px along the wrong direction moves it by under a
    tenth of a percent, which no usable threshold would catch.
    """
    corners = project(*NEAR_NADIR)
    corners[0] += np.array([120.0, 120.0])
    assert abs(rectangle_aspect(corners, FOCAL_PX, PRINCIPAL_PX) - 297.0 / 210.0) < 0.01


@pytest.mark.parametrize("pose", [OBLIQUE, NEAR_NADIR])
@pytest.mark.parametrize("shift_px", [5.0, 20.0, 100.0])
def test_the_residual_sees_a_corner_move_whichever_way_it_went(pose, shift_px):
    """A corner `d` out raises the residual to a tenth to a third of `d`.

    The width of that band is the price of having no blind direction, and it
    is what the message the annotator prints has to be honest about.
    """
    truth = project(*pose)
    for corner in range(4):
        for angle_deg in range(0, 360, 15):
            moved = truth.copy()
            moved[corner] += shift_px * np.array(
                [np.cos(np.radians(angle_deg)), np.sin(np.radians(angle_deg))]
            )
            recovered = pose_from_corners(
                moved, size_mm=A4_MM, focal_px=FOCAL_PX, principal_px=PRINCIPAL_PX
            )
            assert 0.09 * shift_px < recovered.reprojection_rms_px < 0.37 * shift_px


def test_a_frame_that_fits_leaves_no_residual():
    recovered = pose_from_corners(
        project(*OBLIQUE), size_mm=A4_MM, focal_px=FOCAL_PX, principal_px=PRINCIPAL_PX
    )
    assert recovered.reprojection_rms_px < 1e-3


@pytest.mark.parametrize(
    "pose,distance_mm,tilt_deg", [(OBLIQUE, 302.6, 16.7), (NEAR_NADIR, 256.9, 1.3)]
)
def test_pose_comes_back(pose, distance_mm, tilt_deg):
    recovered = pose_from_corners(
        project(*pose), size_mm=A4_MM, focal_px=FOCAL_PX, principal_px=PRINCIPAL_PX
    )
    assert recovered.distance_mm == pytest.approx(distance_mm, abs=0.2)
    assert recovered.tilt_deg == pytest.approx(tilt_deg, abs=0.1)


def test_rectification_undoes_the_projection():
    """A disc of known area on the sheet comes back with that area."""
    corners = project(*OBLIQUE)
    px_per_mm = 8.0
    rectification = rectification_from_corners(
        corners, size_mm=A4_MM, px_per_mm=px_per_mm
    )
    assert rectification.size_px == (round(297 * px_per_mm), round(210 * px_per_mm))

    # Paint the disc in sheet coordinates, project it into the camera, then
    # rectify it back and measure what survives the round trip.
    height_px, width_px = rectification.size_px
    truth = np.zeros((height_px, width_px), np.uint8)
    radius_mm = 20.0
    cv2.circle(
        truth,
        (round(105 * px_per_mm), round(148.5 * px_per_mm)),
        round(radius_mm * px_per_mm),
        255,
        -1,
    )
    frame = cv2.warpPerspective(
        truth, np.linalg.inv(rectification.homography), (6140, 8156)
    )
    recovered = rectify(frame, rectification)
    area_mm2 = float((recovered > 127).sum()) * rectification.pixel_area_mm2
    assert area_mm2 == pytest.approx(np.pi * radius_mm**2, rel=0.01)


def test_sampling_reports_what_the_sensor_carried():
    rectification = rectification_from_corners(
        project(*NEAR_NADIR), size_mm=A4_MM, px_per_mm=1.0
    )
    long, short = sampling_px_per_mm(rectification)
    assert long == pytest.approx(FOCAL_PX / 255.0, rel=0.05)
    assert short == pytest.approx(long, rel=0.02)
