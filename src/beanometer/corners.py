"""Where the sheet is in a frame, and the record of who said so.

Corners are the one input the pipeline cannot derive from the photograph
without also being the thing under test, so they are stored as a record
beside the session rather than recomputed. A hand-placed corner and a
detected one are both kept, distinguished by `source`, which is what lets the
detector be measured against the hand rather than trusted.

Coordinates are `(x, y)` in pixels of the full-size plane named by the file,
clockwise from the corner nearest the image origin.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import yaml

from .geometry import order_corners

FILE_NAME = "corners.yaml"
DETECTED_FILE_NAME = "corners-detected.yaml"


@dataclass(frozen=True)
class Corners:
    """Four corners of the sheet in one frame."""

    stem: str
    corners_px: np.ndarray
    source: str
    plane_size_px: tuple[int, int] | None = None
    note: str | None = None


def corners_path(session_directory: Path | str, *, name: str = FILE_NAME) -> Path:
    return Path(session_directory) / "annotations" / name


def load_corners(path: Path | str) -> tuple[str, dict[str, Corners]]:
    """Read a corner file, returning the plane it was annotated in and its
    entries by frame stem."""
    path = Path(path)
    if not path.exists():
        return "dng", {}
    record = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    plane = record.get("plane", "dng")
    entries = {}
    for stem, entry in (record.get("frames") or {}).items():
        size = entry.get("plane_size_px")
        entries[stem] = Corners(
            stem=stem,
            corners_px=np.asarray(entry["corners_px"], dtype=np.float64).reshape(4, 2),
            source=entry.get("source", "manual"),
            plane_size_px=None if size is None else (int(size[0]), int(size[1])),
            note=entry.get("note"),
        )
    return plane, entries


def save_corners(
    path: Path | str, entries: dict[str, Corners], *, plane: str
) -> None:
    """Write a corner file, ordering frames by stem so the diff is legible."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    body = {
        "plane": plane,
        "frames": {
            stem: {
                "source": entries[stem].source,
                **(
                    {"plane_size_px": list(entries[stem].plane_size_px)}
                    if entries[stem].plane_size_px
                    else {}
                ),
                **({"note": entries[stem].note} if entries[stem].note else {}),
                "corners_px": [
                    [round(float(x), 2), round(float(y), 2)]
                    for x, y in entries[stem].corners_px
                ],
            }
            for stem in sorted(entries)
        },
    }
    header = (
        "# Corners of the substrate in each frame.\n"
        f"# Pixel coordinates are (x, y) in the full-size {plane} plane,\n"
        "# clockwise from the corner nearest the image origin. The two planes\n"
        "# of a capture do not share a coordinate system, so these carry to\n"
        f"# the {plane} plane and to no other.\n"
    )
    text = yaml.safe_dump(body, sort_keys=False, default_flow_style=None, width=88)
    path.write_text(header + text, encoding="utf-8")


# --- Finding the sheet without being told ------------------------------------


def detect_sheet_corners(
    rgb: np.ndarray, *, work_px: int = 1200
) -> np.ndarray | None:
    """Best guess at the four corners of the sheet in a displayable image.

    `rgb` is (h, w, 3) uint8. The sheet is the largest bright, unsaturated
    region; beans darken its interior, so holes are filled before the outline
    is taken. Returns (4, 2), (x, y), in the coordinates of `rgb`, or None
    when no plausible quadrilateral is found.

    The detector is a proposal, not a measurement. A polished table returns a
    specular image of the sheet that is bright and only weakly coloured, and
    nothing here distinguishes that reflection from the sheet itself.
    """
    height, width = rgb.shape[:2]
    scale = work_px / max(height, width)
    small = cv2.resize(rgb, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

    lab = cv2.cvtColor(small, cv2.COLOR_RGB2LAB).astype(np.float32)
    lightness = lab[..., 0] * (100.0 / 255.0)
    chroma = np.hypot(lab[..., 1] - 128.0, lab[..., 2] - 128.0)
    # Bright and grey scores high; the brown table is dark and saturated.
    paperness = lightness - 2.0 * chroma
    paperness = cv2.GaussianBlur(paperness, (0, 0), 2.0)

    span = paperness.max() - paperness.min()
    if span <= 0:
        return None
    scaled = ((paperness - paperness.min()) * (255.0 / span)).astype(np.uint8)
    _, binary = cv2.threshold(scaled, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    if count < 2:
        return None
    largest = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    component = (labels == largest).astype(np.uint8)
    # Beans punch holes in the sheet; the outline wanted is the outer one.
    contours, _ = cv2.findContours(component, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        return None
    contour = max(contours, key=cv2.contourArea)

    quad = _quadrilateral_from_contour(contour)
    if quad is None:
        return None
    return order_corners(quad / scale)


def _quadrilateral_from_contour(contour: np.ndarray) -> np.ndarray | None:
    """Reduce a contour to four corners by fitting a line to each side.

    A polygon approximation gives the four sides; each side is then re-fitted
    to every contour point lying along it, and the corners are where
    consecutive fitted lines meet. Corners are the least reliable part of a
    contour and the sides the most, so the corner is inferred rather than
    picked.
    """
    perimeter = cv2.arcLength(contour, True)
    approximation = None
    for fraction in np.linspace(0.005, 0.08, 40):
        candidate = cv2.approxPolyDP(contour, fraction * perimeter, True)
        if len(candidate) == 4:
            approximation = candidate.reshape(4, 2).astype(np.float64)
            break
    if approximation is None:
        return None

    points = contour.reshape(-1, 2).astype(np.float64)
    corners = order_corners(approximation)
    lines = []
    for index in range(4):
        start, end = corners[index], corners[(index + 1) % 4]
        direction = end - start
        length = float(np.linalg.norm(direction))
        if length < 1.0:
            return None
        direction = direction / length
        normal = np.array([-direction[1], direction[0]])
        offset = points - start
        along = offset @ direction
        across = offset @ normal
        # Keep the points that run along this side, clear of both corners.
        on_side = (
            (along > 0.12 * length)
            & (along < 0.88 * length)
            & (np.abs(across) < 0.05 * length)
        )
        if on_side.sum() < 10:
            lines.append((start, direction))
            continue
        fitted = cv2.fitLine(
            points[on_side].astype(np.float32), cv2.DIST_HUBER, 0, 0.01, 0.01
        ).ravel()
        lines.append((np.array([fitted[2], fitted[3]]), np.array([fitted[0], fitted[1]])))

    refined = []
    for index in range(4):
        previous_point, previous_direction = lines[index - 1]
        point, direction = lines[index]
        crossing = _intersect(previous_point, previous_direction, point, direction)
        if crossing is None:
            return None
        refined.append(crossing)
    return np.asarray(refined)


def _intersect(
    first_point: np.ndarray,
    first_direction: np.ndarray,
    second_point: np.ndarray,
    second_direction: np.ndarray,
) -> np.ndarray | None:
    matrix = np.column_stack([first_direction, -second_direction])
    determinant = float(np.linalg.det(matrix))
    if abs(determinant) < 1e-9:
        return None
    parameters = np.linalg.solve(matrix, second_point - first_point)
    return first_point + parameters[0] * first_direction


def detect_session(
    session, *, plane: str = "dng", scale: float = 0.5
) -> dict[str, Corners]:
    """Run the detector over every frame of a session.

    Written to its own file rather than to the hand-annotated one, so that the
    two can be compared instead of one quietly standing in for the other.
    """
    from .imaging import load_capture, to_display

    entries: dict[str, Corners] = {}
    for frame in session.frames:
        capture = load_capture(frame.path(plane), plane=plane, scale=scale)
        display = to_display(capture)
        quad = detect_sheet_corners(display)
        if quad is None:
            continue
        height, width = display.shape[:2]
        entries[frame.stem] = Corners(
            stem=frame.stem,
            corners_px=quad / scale,
            source="detected",
            plane_size_px=(round(height / scale), round(width / scale)),
        )
    return entries
