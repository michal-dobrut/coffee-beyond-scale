"""The annotation window, driven by fabricated clicks.

No photograph is read: the frames are painted in memory, so the test says
whether the window records what was clicked, not whether a camera was
plugged in.
"""

from __future__ import annotations

from datetime import date

import matplotlib
import numpy as np
import pytest

matplotlib.use("Agg")

from matplotlib.backend_bases import KeyEvent, MouseEvent  # noqa: E402

from beanometer.annotate import CornerAnnotator, _Rendered, open_window  # noqa: E402
from beanometer.corners import corners_path, load_corners  # noqa: E402
from beanometer.session import Frame, Session, Stage  # noqa: E402
from tests.test_geometry import A4_MM, NEAR_NADIR, PRINCIPAL_PX, project  # noqa: E402

RENDER_SCALE = 0.5
PLANE_PX = (8156, 6140)


@pytest.fixture
def annotator(tmp_path):
    frames = tuple(
        Frame(
            stem=f"FRAME_{index}",
            stage="sparse",
            mass_g=16.0,
            mass_source="balance",
            directory=tmp_path,
        )
        for index in range(3)
    )
    session = Session(
        id="test",
        directory=tmp_path,
        captured=date(2026, 8, 29),
        substrate_mm=A4_MM,
        stages=(Stage("sparse", 16.0, "balance", None, frames),),
        record={"camera": {"body": "Google Pixel 10 Pro", "lens": "main"}},
    )
    state = CornerAnnotator(
        session,
        list(frames),
        plane="dng",
        scale=RENDER_SCALE,
        residual_tolerance_px=5.0,
    )
    height, width = PLANE_PX
    blank = np.zeros(
        (round(height * RENDER_SCALE), round(width * RENDER_SCALE), 3), np.uint8
    )
    state._render = lambda frame: _Rendered(frame.stem, blank, RENDER_SCALE)
    return state


def click(figure, axes, x_data, y_data, button=1):
    x_px, y_px = axes.transData.transform((x_data, y_data))
    figure.canvas.callbacks.process(
        "button_press_event",
        MouseEvent("button_press_event", figure.canvas, x_px, y_px, button=button),
    )


def press(figure, key):
    figure.canvas.callbacks.process(
        "key_press_event", KeyEvent("key_press_event", figure.canvas, key)
    )


def place_corners(figure, state, corners_px):
    """Two clicks per corner, as a person makes them."""
    overview, zoom = figure.axes[0], figure.axes[1]
    for x_px, y_px in corners_px:
        click(figure, overview, x_px, y_px)
        click(figure, zoom, x_px, y_px)


def test_four_corners_are_saved_in_full_plane_coordinates(annotator, tmp_path):
    truth_px = project(*NEAR_NADIR)
    figure = open_window(annotator)
    place_corners(figure, annotator, truth_px * RENDER_SCALE)

    _, entries = load_corners(corners_path(tmp_path))
    saved = entries["FRAME_0"]
    assert saved.source == "manual"
    assert saved.plane_size_px == PLANE_PX
    # Clicks land on whole pixels of the rendered view, so the record comes
    # back to within that quantisation and no better.
    assert np.allclose(saved.corners_px, truth_px, atol=1.0 / RENDER_SCALE)


def test_a_clean_frame_steps_on_and_a_dirty_one_does_not(annotator):
    figure = open_window(annotator)
    place_corners(figure, annotator, project(*NEAR_NADIR) * RENDER_SCALE)
    assert annotator.index == 1

    wrong = project(*NEAR_NADIR)
    wrong[0] += np.array([300.0, 300.0])
    place_corners(figure, annotator, wrong * RENDER_SCALE)
    assert annotator.index == 1
    assert "px out" in annotator.message


def test_undo_and_restart_take_corners_back(annotator):
    figure = open_window(annotator)
    overview, zoom = figure.axes[0], figure.axes[1]
    corners = project(*NEAR_NADIR) * RENDER_SCALE
    click(figure, overview, *corners[0])
    click(figure, zoom, *corners[0])
    click(figure, overview, *corners[1])
    click(figure, zoom, *corners[1])
    assert len(annotator.clicked) == 2

    click(figure, overview, *corners[2], button=3)
    assert len(annotator.clicked) == 1
    press(figure, "u")
    assert annotator.clicked == []

    click(figure, overview, *corners[0])
    press(figure, "r")
    assert annotator.pending is None and annotator.clicked == []


def test_a_frame_can_be_marked_unusable(annotator, tmp_path):
    figure = open_window(annotator)
    press(figure, "x")
    _, entries = load_corners(corners_path(tmp_path))
    assert entries["FRAME_0"].source == "unusable"
    assert np.isnan(entries["FRAME_0"].corners_px).all()
