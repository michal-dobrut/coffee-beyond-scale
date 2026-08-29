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
    save_corners,
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

    if arguments.command == "corners":
        from .report import print_corner_summary

        print_corner_summary(session, name=arguments.corners)
        return 0

    raise AssertionError(f"unhandled command {arguments.command!r}")
