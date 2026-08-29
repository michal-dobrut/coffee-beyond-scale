"""Turning four corners of the sheet into a plane a pixel has an area in.

Image coordinates are `(x, y)` in pixels of the plane the corners were
annotated in, `x` to the right and `y` down. Sheet coordinates are
millimetres from the sheet's top-left corner, `x` along its short edge and
`y` along its long one, so a rectified frame is always portrait however the
camera was held.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import cv2
import numpy as np


def order_corners(corners_px: np.ndarray) -> np.ndarray:
    """Put four corners into a consistent cycle.

    Takes (4, 2), (x, y), in any rotation or winding, and returns (4, 2)
    clockwise as the image is drawn, starting at the corner nearest the image
    origin. Only the cycle is assumed of the input: the four points have to
    walk around the quadrilateral rather than cross it.
    """
    corners_px = np.asarray(corners_px, dtype=np.float64).reshape(4, 2)
    centre = corners_px.mean(axis=0)
    offsets = corners_px - centre
    # Angles grow clockwise because y points down.
    angle = np.arctan2(offsets[:, 1], offsets[:, 0])
    walk = corners_px[np.argsort(angle)]
    start = int(np.argmin(walk.sum(axis=1)))
    return np.roll(walk, -start, axis=0)


@dataclass(frozen=True)
class Rectification:
    """The map from an annotated frame to the sheet, and the scale it fixes.

    `homography` is (3, 3) taking image `(x, y, 1)` to rectified `(x, y, 1)`.
    `corners_px` is (4, 2) ordered to match the sheet corners top-left,
    top-right, bottom-right, bottom-left.
    """

    homography: np.ndarray
    corners_px: np.ndarray
    size_mm: tuple[float, float]
    px_per_mm: float

    @property
    def size_px(self) -> tuple[int, int]:
        """Rectified size as (height, width), matching array order."""
        width_mm, height_mm = self.size_mm
        return round(height_mm * self.px_per_mm), round(width_mm * self.px_per_mm)

    @property
    def pixel_area_mm2(self) -> float:
        return 1.0 / (self.px_per_mm**2)

    @property
    def sheet_area_mm2(self) -> float:
        return self.size_mm[0] * self.size_mm[1]


def rectification_from_corners(
    corners_px: np.ndarray,
    *,
    size_mm: tuple[float, float],
    px_per_mm: float,
) -> Rectification:
    """Fit the homography that flattens the sheet.

    `size_mm` is the sheet as (short edge, long edge). Which pair of image
    edges is the long one is read off the quadrilateral rather than asked for,
    so the annotator need only walk around the sheet and not remember which
    way up it lay.
    """
    ordered = order_corners(corners_px)
    edge = np.linalg.norm(np.roll(ordered, -1, axis=0) - ordered, axis=1)
    if 0.5 * (edge[0] + edge[2]) > 0.5 * (edge[1] + edge[3]):
        # The edge leaving the starting corner is the long one, so the sheet
        # lies across the frame; roll once to make it the second edge.
        ordered = np.roll(ordered, -1, axis=0)

    width_mm, height_mm = size_mm
    height_px, width_px = round(height_mm * px_per_mm), round(width_mm * px_per_mm)
    destination = np.array(
        [[0.0, 0.0], [width_px, 0.0], [width_px, height_px], [0.0, height_px]],
        dtype=np.float64,
    )
    homography = cv2.getPerspectiveTransform(
        ordered.astype(np.float32), destination.astype(np.float32)
    )
    return Rectification(
        homography=homography,
        corners_px=ordered,
        size_mm=(width_mm, height_mm),
        px_per_mm=px_per_mm,
    )


def rectify(image: np.ndarray, rectification: Rectification) -> np.ndarray:
    """Warp an image into sheet coordinates.

    Sampling is area-averaging, so a rectified pixel is the mean of the
    photosites falling in it rather than one of them.
    """
    height_px, width_px = rectification.size_px
    return cv2.warpPerspective(
        image,
        rectification.homography,
        (width_px, height_px),
        flags=cv2.INTER_AREA,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=0,
    )


def sampling_px_per_mm(rectification: Rectification) -> tuple[float, float]:
    """How finely the sensor sampled the sheet, as (long edge, short edge).

    This is what the photograph carries, as against the `px_per_mm` the
    rectification resamples to. Rectifying finer than this invents nothing.
    """
    corners = rectification.corners_px
    edge = np.linalg.norm(np.roll(corners, -1, axis=0) - corners, axis=1)
    width_mm, height_mm = rectification.size_mm
    short = 0.5 * (edge[0] + edge[2]) / width_mm
    long = 0.5 * (edge[1] + edge[3]) / height_mm
    return long, short


# --- What four corners of a known rectangle say about the camera -------------
#
# A homography from a plane over-determines a camera carrying one unknown
# focal length, which is what makes these checks free: nothing beyond the
# corners already annotated goes into them.


def _centred_homography(
    corners_px: np.ndarray, principal_px: tuple[float, float]
) -> np.ndarray:
    """The homography from the unit square to image coordinates measured from
    the principal point."""
    ordered = order_corners(corners_px)
    unit = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]], dtype=np.float32)
    homography = cv2.getPerspectiveTransform(unit, ordered.astype(np.float32))
    centring = np.array(
        [[1.0, 0.0, -principal_px[0]], [0.0, 1.0, -principal_px[1]], [0.0, 0.0, 1.0]]
    )
    return centring @ homography


def focal_length_px(
    corners_px: np.ndarray, principal_px: tuple[float, float]
) -> float | None:
    """Focal length in pixels implied by the corners alone.

    The two in-plane directions of a rectangle are perpendicular, and that one
    constraint on the homography solves for focal length. It degenerates as
    the view approaches head-on, where a rectangle projects to a rectangle
    whatever the focal length; the result is then unsupported by the data and
    this returns None rather than a number.
    """
    homography = _centred_homography(corners_px, principal_px)
    first, second = homography[:, 0], homography[:, 1]
    denominator = first[2] * second[2]
    if abs(denominator) < 1e-15:
        return None
    squared = -(first[0] * second[0] + first[1] * second[1]) / denominator
    if squared <= 0.0:
        return None
    return math.sqrt(squared)


def rectangle_aspect(
    corners_px: np.ndarray, focal_px: float, principal_px: tuple[float, float]
) -> float:
    """The aspect ratio of the world rectangle the corners came from.

    Long edge over short edge, so an A4 sheet should return 297/210. It is a
    weak check on corner placement and a poor gate: it has directions it
    cannot see at all, in which a corner can move hundreds of pixels while the
    ratio moves by a thousandth of a percent. What it is good for is the
    systematic part, where a wrong focal length or uncorrected distortion
    shifts every frame of a session the same way.
    """
    homography = _centred_homography(corners_px, principal_px)
    first, second = homography[:, 0], homography[:, 1]
    weight = np.array([1.0 / focal_px**2, 1.0 / focal_px**2, 1.0])
    first_norm = math.sqrt(float(np.sum(weight * first * first)))
    second_norm = math.sqrt(float(np.sum(weight * second * second)))
    ratio = second_norm / first_norm
    return ratio if ratio >= 1.0 else 1.0 / ratio


@dataclass(frozen=True)
class Pose:
    """Where the camera stood, in the frame of the sheet.

    `distance_mm` is from the camera centre to the centre of the sheet;
    `tilt_deg` is the angle between the optical axis and the sheet normal.
    `reprojection_rms_px` is what the fit could not account for, in pixels of
    the plane the corners were annotated in.
    """

    distance_mm: float
    tilt_deg: float
    reprojection_rms_px: float


def pose_from_corners(
    corners_px: np.ndarray,
    *,
    size_mm: tuple[float, float],
    focal_px: float,
    principal_px: tuple[float, float],
) -> Pose:
    """Recover the stance of the camera from the corners and a focal length.

    Four corners give eight equations for a six-parameter pose, so two are
    left over and the fit does not in general close. What it cannot account
    for comes back as `reprojection_rms_px`, and that residual is the useful
    part: a corner placed `d` pixels from where the sheet actually is raises
    it to between a tenth and a third of `d`, so a residual of `r` puts some
    corner between `3r` and `10r` out. Unlike the aspect ratio it has no blind
    direction. Corner placement, lens distortion and a wrong focal length all
    land in it together, and it cannot say which.
    """
    ordered = order_corners(corners_px)
    edge = np.linalg.norm(np.roll(ordered, -1, axis=0) - ordered, axis=1)
    width_mm, height_mm = size_mm
    if 0.5 * (edge[0] + edge[2]) > 0.5 * (edge[1] + edge[3]):
        ordered = np.roll(ordered, -1, axis=0)
    object_mm = np.array(
        [
            [0.0, 0.0, 0.0],
            [width_mm, 0.0, 0.0],
            [width_mm, height_mm, 0.0],
            [0.0, height_mm, 0.0],
        ],
        dtype=np.float64,
    )
    camera_matrix = np.array(
        [
            [focal_px, 0.0, principal_px[0]],
            [0.0, focal_px, principal_px[1]],
            [0.0, 0.0, 1.0],
        ]
    )
    image_px = ordered.astype(np.float64)
    ok, rotation_vector, translation_mm = cv2.solvePnP(
        object_mm, image_px, camera_matrix, None, flags=cv2.SOLVEPNP_IPPE
    )
    if not ok:
        raise ValueError("the corners did not resolve to a camera pose")
    # The analytic solution is exact through the homography rather than least
    # squares, which leaves the residual it reports several times larger than
    # the corner error that caused it.
    rotation_vector, translation_mm = cv2.solvePnPRefineLM(
        object_mm, image_px, camera_matrix, None, rotation_vector, translation_mm
    )
    projected, _ = cv2.projectPoints(
        object_mm, rotation_vector, translation_mm, camera_matrix, None
    )
    residual_px = float(
        np.sqrt(((projected.reshape(4, 2) - image_px) ** 2).sum(axis=1).mean())
    )
    rotation, _ = cv2.Rodrigues(rotation_vector)
    centre_mm = np.array([width_mm / 2.0, height_mm / 2.0, 0.0])
    to_centre = rotation @ centre_mm + translation_mm.ravel()
    # The sheet normal in camera coordinates is the third column of R; the
    # optical axis is +z.
    normal = rotation[:, 2]
    return Pose(
        distance_mm=float(np.linalg.norm(to_centre)),
        tilt_deg=math.degrees(math.acos(min(1.0, abs(float(normal[2]))))),
        reprojection_rms_px=residual_px,
    )
