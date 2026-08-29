"""Command line over the pipeline.

One subcommand per stage, each reading what the stage before it wrote, so a
stage can be re-run without re-running the ones above it.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .corners import (
    DETECTED_FILE_NAME,
    FILE_NAME,
    corners_path,
    detect_session,
    load_corners,
    save_corners,
)
from .measure import (
    DEFAULT_MARGIN_MM,
    DEFAULT_PX_PER_MM,
    default_output,
    measure_session,
    to_frame,
)
from .session import load_session


def _add_session_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "session",
        type=Path,
        help="directory holding the session record and its photographs",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="beanometer", description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    annotate = subparsers.add_parser(
        "annotate", help="click the corners of the sheet in each frame"
    )
    _add_session_argument(annotate)
    annotate.add_argument("--plane", choices=("dng", "jpeg"), default="dng")
    annotate.add_argument(
        "--scale",
        type=float,
        default=0.5,
        help="fraction of full size to render for clicking (raw takes 1.0 or 0.5)",
    )
    annotate.add_argument("--stage", help="restrict to one stage of the session")
    annotate.add_argument(
        "--residual",
        type=float,
        default=5.0,
        help="reprojection residual in rendered pixels above which a frame is "
        "held for another look instead of stepped over (default 5)",
    )
    annotate.add_argument(
        "--redo",
        action="store_true",
        help="revisit frames that already have corners instead of skipping them",
    )

    detect = subparsers.add_parser(
        "detect", help="propose corners for every frame, into their own file"
    )
    _add_session_argument(detect)
    detect.add_argument("--plane", choices=("dng", "jpeg"), default="dng")
    detect.add_argument("--scale", type=float, default=0.5)

    measure = subparsers.add_parser(
        "measure", help="read every annotated frame into a table of observables"
    )
    _add_session_argument(measure)
    measure.add_argument("--corners", default=FILE_NAME)
    measure.add_argument("--plane", choices=("dng", "jpeg"), default="dng")
    measure.add_argument(
        "--px-per-mm",
        type=float,
        default=DEFAULT_PX_PER_MM,
        help="resolution the sheet is rectified to (default %(default)s)",
    )
    measure.add_argument(
        "--margin-mm",
        type=float,
        default=DEFAULT_MARGIN_MM,
        help="rim of the sheet left out of the measurement (default %(default)s)",
    )
    measure.add_argument("--convention", choices=("soft", "hard"), default="soft")
    measure.add_argument(
        "--overlays",
        action="store_true",
        help="write a picture of what each frame was resolved into",
    )
    measure.add_argument("--out", type=Path, help="where to write the table")

    results = subparsers.add_parser(
        "results", help="fit one constant per pathway and report what remains"
    )
    _add_session_argument(results)
    results.add_argument("--measurements", type=Path, help="table written by measure")

    corners = subparsers.add_parser(
        "corners", help="report what the annotated corners imply about each frame"
    )
    _add_session_argument(corners)
    corners.add_argument(
        "--corners",
        default=FILE_NAME,
        help=f"corner file under the annotations directory (default {FILE_NAME})",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    session = load_session(arguments.session)

    if arguments.command == "annotate":
        from . import annotate as annotate_module

        annotate_module.run(
            session,
            plane=arguments.plane,
            scale=arguments.scale,
            stage=arguments.stage,
            redo=arguments.redo,
            residual_tolerance_px=arguments.residual,
        )
        return 0

    if arguments.command == "detect":
        entries = detect_session(session, plane=arguments.plane, scale=arguments.scale)
        path = corners_path(session.directory, name=DETECTED_FILE_NAME)
        save_corners(path, entries, plane=arguments.plane)
        print(f"{len(entries)}/{len(session.frames)} frames proposed, written to {path}")
        return 0

    if arguments.command == "measure":
        plane, entries = load_corners(
            corners_path(session.directory, name=arguments.corners)
        )
        if not entries:
            print(f"no corners in {corners_path(session.directory, name=arguments.corners)}")
            return 1
        out = arguments.out or default_output(session)
        measurements = measure_session(
            session,
            entries,
            plane=plane,
            px_per_mm=arguments.px_per_mm,
            margin_mm=arguments.margin_mm,
            convention=arguments.convention,
            overlay_directory=out.parent / "overlays" if arguments.overlays else None,
        )
        out.parent.mkdir(parents=True, exist_ok=True)
        to_frame(measurements).to_csv(out, index=False)
        print(f"{len(measurements)} frames measured, written to {out}")
        return 0

    if arguments.command == "results":
        from .report import print_results

        print_results(session, arguments.measurements or default_output(session))
        return 0

    if arguments.command == "corners":
        from .report import print_corner_summary

        print_corner_summary(session, name=arguments.corners)
        return 0

    raise AssertionError(f"unhandled command {arguments.command!r}")
