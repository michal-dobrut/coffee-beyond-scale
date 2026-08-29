"""The record a session leaves beside its photographs.

`session.yaml` is authored by hand and names every frame by the stem the
camera gave it. This module turns that record into objects, and resolves a
stem to the files on disk that carry it.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import yaml

# A capture leaves several files sharing one stem. The stem is the join
# between them, since the containers round their timestamps independently.
PLANE_SUFFIXES: dict[str, tuple[str, ...]] = {
    "dng": (".RAW-02.ORIGINAL.dng", ".dng"),
    "jpeg": (".RAW-01.jpg", ".jpg", ".jpeg"),
}


@dataclass(frozen=True)
class Frame:
    """One capture, and the mass the balance read for the stage it belongs to."""

    stem: str
    stage: str
    mass_g: float
    mass_source: str
    directory: Path

    def path(self, plane: str) -> Path:
        """The file holding this frame in `plane`, either `dng` or `jpeg`.

        The two planes do not share a pixel frame: they differ in orientation,
        in size, and in the ratio between their axes. A position measured in
        one does not carry to the other.
        """
        try:
            suffixes = PLANE_SUFFIXES[plane]
        except KeyError:
            raise ValueError(f"unknown plane {plane!r}") from None
        for suffix in suffixes:
            candidate = self.directory / f"{self.stem}{suffix}"
            if candidate.exists():
                return candidate
        raise FileNotFoundError(f"no {plane} file for {self.stem} in {self.directory}")


@dataclass(frozen=True)
class Stage:
    """A mass placed on the sheet, and the frames taken of it."""

    name: str
    mass_g: float
    mass_source: str
    note: str | None
    frames: tuple[Frame, ...]


@dataclass(frozen=True)
class Session:
    """One capture session, as its record describes it."""

    id: str
    directory: Path
    captured: date
    substrate_mm: tuple[float, float]
    stages: tuple[Stage, ...]
    record: dict[str, Any]

    @property
    def frames(self) -> tuple[Frame, ...]:
        return tuple(frame for stage in self.stages for frame in stage.frames)

    def frame(self, stem: str) -> Frame:
        for candidate in self.frames:
            if candidate.stem == stem:
                return candidate
        raise KeyError(stem)


def load_session(directory: Path | str) -> Session:
    """Read the `session.yaml` in `directory`."""
    directory = Path(directory)
    record = yaml.safe_load((directory / "session.yaml").read_text(encoding="utf-8"))

    substrate = record["substrate"]
    stages = []
    for entry in record["stages"]:
        frames = tuple(
            Frame(
                stem=stem,
                stage=entry["name"],
                mass_g=float(entry["mass_g"]),
                mass_source=entry["mass_source"],
                directory=directory,
            )
            for stem in entry["frames"]
        )
        stages.append(
            Stage(
                name=entry["name"],
                mass_g=float(entry["mass_g"]),
                mass_source=entry["mass_source"],
                note=entry.get("note"),
                frames=frames,
            )
        )

    captured = record["captured"]
    return Session(
        id=str(record["session"]),
        directory=directory,
        captured=captured if isinstance(captured, date) else date.fromisoformat(captured),
        substrate_mm=(float(substrate["width_mm"]), float(substrate["height_mm"])),
        stages=tuple(stages),
        record=record,
    )
