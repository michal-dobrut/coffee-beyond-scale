"""Clicking the corners of the sheet, frame by frame.

Two clicks place one corner. The first lands anywhere near it on the whole
frame and opens a magnified patch; the second places the corner inside that
patch, where a pixel is large enough to aim at. Four corners close a frame,
the file is written, and the next frame is already decoded and waiting.

The fourth corner is checked before the frame is left. Four corners of a
sheet of known size, seen through a lens of known focal length, over-determine
where the camera stood by two equations, and what that fit cannot account for
is a residual in pixels. It has no blind direction: a corner placed `d`
pixels out raises the residual to somewhere between a tenth and a third of
`d`. A frame that passes is stepped over automatically; one that fails holds
the window where it is, so the mistake is caught while the frame is still on
screen.

Matplotlib is needed here and nowhere else in the pipeline, so it is imported
where the window is opened rather than at module scope.
"""

from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass

import numpy as np

from .corners import Corners, corners_path, load_corners, save_corners
from .geometry import order_corners, pose_from_corners
from .imaging import load_capture, to_display
from .instruments import camera_for
from .session import Frame, Session

HELP = """\
  click        coarse, then again in the magnified patch, to place a corner
  space        place the corner where the coarse click landed, unmagnified
  right-click  undo                        u  undo the last corner
  r            restart this frame          x  mark this frame unusable
  n / enter    next frame                  p  previous frame
  [ ]          magnify less / more         q  save and quit
"""

ZOOM_HALF_PX = 130
CORNER_COLOURS = ("#ff3b30", "#ffcc00", "#34c759", "#0a84ff")


@dataclass
class _Rendered:
    """One frame as a person sees it, and the scale that view was made at."""

    stem: str
    display: np.ndarray
    scale: float


class CornerAnnotator:
    """What frame is on screen, which corners are down, and what comes next.

    Clicks arrive in the coordinates of the rendered view; corners are stored
    in the coordinates of the full-size plane, so the record does not depend
    on the scale the annotation happened to be done at.
    """

    def __init__(
        self,
        session: Session,
        frames: list[Frame],
        *,
        plane: str,
        scale: float,
        residual_tolerance_px: float,
    ) -> None:
        self.session = session
        self.frames = frames
        self.plane = plane
        self.scale = scale
        self.residual_tolerance_px = residual_tolerance_px
        self.path = corners_path(session.directory)
        _, self.entries = load_corners(self.path)
        self.index = 0
        self.clicked: list[tuple[float, float]] = []
        self.pending: tuple[float, float] | None = None
        self.zoom_half_px = ZOOM_HALF_PX
        self.message = ""
        self.rendered: _Rendered | None = None
        self._pool = ThreadPoolExecutor(max_workers=1)
        self._ahead: dict[str, Future[_Rendered]] = {}

    # --- the frame on screen --------------------------------------------

    @property
    def frame(self) -> Frame:
        return self.frames[self.index]

    def _render(self, frame: Frame) -> _Rendered:
        capture = load_capture(frame.path(self.plane), plane=self.plane, scale=self.scale)
        return _Rendered(stem=frame.stem, display=to_display(capture), scale=self.scale)

    def current(self) -> _Rendered:
        stem = self.frame.stem
        if self.rendered is not None and self.rendered.stem == stem:
            return self.rendered
        waiting = self._ahead.pop(stem, None)
        self.rendered = waiting.result() if waiting else self._render(self.frame)
        self._read_ahead()
        return self.rendered

    def _read_ahead(self) -> None:
        for offset in (1, 2):
            step = self.index + offset
            if step < len(self.frames):
                frame = self.frames[step]
                self._ahead.setdefault(frame.stem, self._pool.submit(self._render, frame))

    def close(self) -> None:
        self._pool.shutdown(wait=False, cancel_futures=True)

    def step(self, delta: int) -> None:
        self.index = max(0, min(len(self.frames) - 1, self.index + delta))
        self.clicked = []
        self.pending = None

    # --- corners --------------------------------------------------------

    def existing(self) -> Corners | None:
        return self.entries.get(self.frame.stem)

    def place(self, x_px: float, y_px: float) -> bool | None:
        """Put down one corner, saving the frame once four are down.

        Returns whether the saved frame passed its residual check, or None
        while corners are still being placed.
        """
        if len(self.clicked) >= 4:
            return None
        self.clicked.append((x_px, y_px))
        self.pending = None
        if len(self.clicked) < 4:
            return None
        return self._commit()

    def undo(self) -> None:
        if self.pending is not None:
            self.pending = None
        elif self.clicked:
            self.clicked.pop()
        self.message = ""

    def restart(self) -> None:
        self.clicked = []
        self.pending = None
        self.message = ""

    def _principal_px(self) -> tuple[float, float]:
        height, width = self.current().display.shape[:2]
        return width / 2.0, height / 2.0

    def _focal_px(self) -> float:
        """Focal length in pixels of the rendered view.

        Taken from the instrument rather than from the frame, because
        recovering it from four corners degenerates as the view approaches
        head-on, and this check has to hold on every frame.
        """
        return camera_for(self.session.record).focal_px(scale=self.scale)

    def residual_px(self, corners_px: np.ndarray) -> float:
        return pose_from_corners(
            corners_px,
            size_mm=self.session.substrate_mm,
            focal_px=self._focal_px(),
            principal_px=self._principal_px(),
        ).reprojection_rms_px

    def _commit(self) -> bool:
        rendered = self.current()
        corners = order_corners(np.asarray(self.clicked, dtype=np.float64))
        residual = self.residual_px(corners)
        height, width = rendered.display.shape[:2]
        self.entries[self.frame.stem] = Corners(
            stem=self.frame.stem,
            corners_px=corners / rendered.scale,
            source="manual",
            plane_size_px=(round(height / rendered.scale), round(width / rendered.scale)),
        )
        save_corners(self.path, self.entries, plane=self.plane)
        passed = residual <= self.residual_tolerance_px
        if passed:
            self.message = f"{self.frame.stem[-6:]} saved, residual {residual:.2f} px"
        else:
            self.message = (
                f"saved, but the four corners sit {residual:.1f} px from any A4"
                f" sheet seen through this lens, which puts one of them {3 * residual:.0f}"
                f" to {10 * residual:.0f} px out. Press r to place them again."
            )
        return passed

    def mark_unusable(self, reason: str = "sheet not fully framed") -> None:
        self.entries[self.frame.stem] = Corners(
            stem=self.frame.stem,
            corners_px=np.full((4, 2), np.nan),
            source="unusable",
            note=reason,
        )
        save_corners(self.path, self.entries, plane=self.plane)
        self.message = "marked unusable"

    def status(self) -> str:
        done = sum(1 for entry in self.entries.values() if entry.source != "unusable")
        existing = self.existing()
        mark = "" if existing is None else f"  [{existing.source}]"
        return (
            f"{self.index + 1}/{len(self.frames)}  {self.frame.stem}  "
            f"{self.frame.stage} {self.frame.mass_g:g} g{mark}   "
            f"corners {len(self.clicked)}/4   done {done}/{len(self.frames)}"
        )


def frames_to_annotate(
    session: Session, *, stage: str | None = None, redo: bool = False
) -> list[Frame]:
    """The frames the window steps through."""
    frames = [f for f in session.frames if stage is None or f.stage == stage]
    if redo:
        return frames
    _, existing = load_corners(corners_path(session.directory))
    remaining = [f for f in frames if f.stem not in existing]
    return remaining or frames


def open_window(state: CornerAnnotator):
    """Build the window and wire the clicks to it, returning the figure."""
    import matplotlib
    import matplotlib.pyplot as plt

    for name in (
        "keymap.save", "keymap.quit", "keymap.home", "keymap.back", "keymap.forward",
        "keymap.xscale", "keymap.yscale", "keymap.fullscreen", "keymap.grid",
        "keymap.grid_minor", "keymap.pan", "keymap.zoom", "keymap.copy",
    ):
        matplotlib.rcParams[name] = []

    figure, (overview_axes, zoom_axes) = plt.subplots(
        1, 2, figsize=(15.0, 8.5), gridspec_kw={"width_ratios": [2, 1]}
    )
    figure.canvas.manager.set_window_title(f"corners — {state.session.id}")

    def draw() -> None:
        rendered = state.current()
        height, width = rendered.display.shape[:2]
        overview_axes.clear()
        overview_axes.imshow(rendered.display, interpolation="antialiased")
        # A little room outside the frame, so a corner just off the edge of
        # the sensor can still be placed by eye along its two edges.
        overview_axes.set_xlim(-0.06 * width, 1.06 * width)
        overview_axes.set_ylim(1.06 * height, -0.06 * height)
        overview_axes.set_axis_off()

        previous = state.existing()
        if previous is not None and previous.source == "manual" and not state.clicked:
            marks = previous.corners_px * rendered.scale
            overview_axes.plot(
                np.append(marks[:, 0], marks[0, 0]),
                np.append(marks[:, 1], marks[0, 1]),
                "-", color="#8e8e93", linewidth=1.0,
            )
        for index, (x_px, y_px) in enumerate(state.clicked):
            overview_axes.plot(
                x_px, y_px, "+",
                color=CORNER_COLOURS[index], markersize=16, markeredgewidth=2,
            )

        zoom_axes.clear()
        zoom_axes.set_axis_off()
        if state.pending is None:
            zoom_axes.set_title("click near a corner", fontsize=10)
        else:
            x_px, y_px = state.pending
            half = state.zoom_half_px
            left, top = int(round(x_px - half)), int(round(y_px - half))
            patch = np.zeros((2 * half, 2 * half, 3), dtype=rendered.display.dtype)
            x0, y0 = max(0, left), max(0, top)
            x1, y1 = min(width, left + 2 * half), min(height, top + 2 * half)
            if x1 > x0 and y1 > y0:
                patch[y0 - top : y1 - top, x0 - left : x1 - left] = rendered.display[
                    y0:y1, x0:x1
                ]
            zoom_axes.imshow(
                patch,
                interpolation="nearest",
                extent=(left, left + 2 * half, top + 2 * half, top),
            )
            zoom_axes.plot(
                x_px, y_px, "+", color="#ff453a", markersize=12, markeredgewidth=1.0
            )
            zoom_axes.set_title(
                f"corner {len(state.clicked) + 1} of 4 — click to place", fontsize=10
            )

        figure.suptitle(
            f"{state.status()}\n{state.message}", fontsize=10, family="monospace"
        )
        figure.canvas.draw_idle()

    def advance_if_clean(passed: bool | None) -> None:
        if passed and state.index + 1 < len(state.frames):
            message = state.message
            state.step(1)
            state.message = message

    def on_click(event) -> None:
        if event.inaxes is None or event.xdata is None:
            return
        if event.button != 1:
            state.undo()
        elif event.inaxes is zoom_axes and state.pending is not None:
            advance_if_clean(state.place(float(event.xdata), float(event.ydata)))
        elif event.inaxes is overview_axes:
            state.pending = (float(event.xdata), float(event.ydata))
        draw()

    def on_key(event) -> None:
        key = event.key
        if key in ("enter", "n"):
            state.step(1)
        elif key in ("p", "backspace"):
            state.step(-1)
        elif key == "u":
            state.undo()
        elif key == "r":
            state.restart()
        elif key == "x":
            state.mark_unusable()
        elif key == " " and state.pending is not None:
            advance_if_clean(state.place(*state.pending))
        elif key == "[":
            state.zoom_half_px = min(600, int(state.zoom_half_px * 1.5))
        elif key == "]":
            state.zoom_half_px = max(30, int(state.zoom_half_px / 1.5))
        elif key in ("q", "escape"):
            plt.close(figure)
            return
        else:
            return
        draw()

    figure.canvas.mpl_connect("button_press_event", on_click)
    figure.canvas.mpl_connect("key_press_event", on_key)
    draw()
    return figure


def run(
    session: Session,
    *,
    plane: str = "dng",
    scale: float = 0.5,
    stage: str | None = None,
    redo: bool = False,
    residual_tolerance_px: float = 5.0,
) -> None:
    """Open the window and annotate, saving after every completed frame."""
    import matplotlib
    import matplotlib.pyplot as plt

    if matplotlib.get_backend().lower() == "agg":
        raise RuntimeError(
            "matplotlib has no interactive backend here, so there is nothing to "
            "click on. Install tkinter support, or run outside a headless shell."
        )

    frames = frames_to_annotate(session, stage=stage, redo=redo)
    if not frames:
        print("no frames to annotate")
        return

    state = CornerAnnotator(
        session,
        frames,
        plane=plane,
        scale=scale,
        residual_tolerance_px=residual_tolerance_px,
    )
    print(HELP)
    open_window(state)
    plt.show()
    state.close()
    print(f"corners written to {state.path}")
