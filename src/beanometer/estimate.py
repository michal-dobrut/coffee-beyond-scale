"""From an observable to grams, and how far that is to be trusted.

Each pathway reads one number off a photograph and multiplies it by one
constant. Feature extraction and calibration are kept apart deliberately: a
pathway is a name and the column it reads, a calibration is a number fitted to
a set of frames, and adding a third pathway costs neither of them a change.

The constant is fitted as a geometric mean of the per-frame ratios rather than
by least squares on grams. Relative error is what the project reports, so the
fit should minimise relative residuals and weight a 16 g frame the same as a
50 g one; a fit through the origin in grams would let the heaviest frames set
the constant and then look accurate on them.

A constant fitted on the frames it is then scored against is in-sample, and
in-sample scatter understates. What it does measure honestly is how far two
photographs of the same sheet disagree with each other, which is the whole
question a shakedown is asked to answer.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .measure import FrameMeasurement


@dataclass(frozen=True)
class Pathway:
    """One way of reading a photograph, and the column it reads."""

    name: str
    observable: str
    unit: str
    description: str


PATHWAYS: tuple[Pathway, ...] = (
    Pathway(
        name="covered-area",
        observable="covered_area_mm2",
        unit="mm2",
        description="the coffee-covered area of the sheet",
    ),
    Pathway(
        name="bean-count",
        observable="bean_count",
        unit="beans",
        description="the number of beans separated on the sheet",
    ),
)


def pathway(name: str) -> Pathway:
    for candidate in PATHWAYS:
        if candidate.name == name:
            return candidate
    known = ", ".join(candidate.name for candidate in PATHWAYS)
    raise KeyError(f"unknown pathway {name!r}; known pathways are {known}")


@dataclass(frozen=True)
class Calibration:
    """One constant, and what it was fitted on.

    `grams_per_unit` converts the pathway's observable to mass. `scatter_rel`
    is the standard deviation of the log residuals, which for small residuals
    reads as a relative standard deviation.
    """

    pathway: Pathway
    grams_per_unit: float
    scatter_rel: float
    frames: tuple[str, ...]

    def estimate(self, measurement: FrameMeasurement) -> Estimate:
        observed = float(getattr(measurement, self.pathway.observable))
        mass_g = self.grams_per_unit * observed
        return Estimate(
            mass_g=mass_g,
            sigma_g=abs(mass_g) * self.scatter_rel,
            observable=observed,
            pathway=self.pathway.name,
        )


@dataclass(frozen=True)
class Estimate:
    """A mass and the spread around it, from one pathway on one frame."""

    mass_g: float
    sigma_g: float
    observable: float
    pathway: str


def fittable(measurements: list[FrameMeasurement], pathway: Pathway) -> list[FrameMeasurement]:
    """The frames a constant may be fitted on.

    A frame qualifies when the balance read its mass — a mass that was
    estimated by eye is a check on the result, not an input to it — and when
    the pathway saw anything at all.
    """
    return [
        measurement
        for measurement in measurements
        if measurement.mass_source == "balance"
        and measurement.mass_g > 0.0
        and float(getattr(measurement, pathway.observable)) > 0.0
    ]


def fit(measurements: list[FrameMeasurement], pathway: Pathway) -> Calibration:
    """Fit the one constant of a pathway to the frames that qualify."""
    usable = fittable(measurements, pathway)
    if not usable:
        raise ValueError(f"no frame carries both a balance mass and a {pathway.name}")
    log_ratio = np.array(
        [
            np.log(measurement.mass_g / float(getattr(measurement, pathway.observable)))
            for measurement in usable
        ]
    )
    return Calibration(
        pathway=pathway,
        grams_per_unit=float(np.exp(log_ratio.mean())),
        scatter_rel=float(log_ratio.std(ddof=1)) if len(log_ratio) > 1 else float("nan"),
        frames=tuple(measurement.stem for measurement in usable),
    )


def residuals(
    measurements: list[FrameMeasurement], calibration: Calibration
) -> list[tuple[FrameMeasurement, Estimate, float]]:
    """Each frame with its estimate and its relative error against the balance.

    Frames the constant was not fitted on are included, since a zero-mass
    frame has no relative error but its estimate is exactly the thing worth
    seeing.
    """
    out = []
    for measurement in measurements:
        estimate = calibration.estimate(measurement)
        relative = (
            (estimate.mass_g - measurement.mass_g) / measurement.mass_g
            if measurement.mass_g > 0.0
            else float("nan")
        )
        out.append((measurement, estimate, relative))
    return out


@dataclass(frozen=True)
class StageSpread:
    """How far frames of one unchanged sheet disagree with each other.

    Nothing about the coffee changes between them, so everything separating
    them is where the camera stood, how the sheet lay, and the pipeline.
    """

    stage: str
    mass_g: float
    frames: int
    mean: float
    sd: float

    @property
    def spread_rel(self) -> float:
        return self.sd / self.mean if self.mean else float("nan")


def spread_by_stage(
    measurements: list[FrameMeasurement], pathway: Pathway
) -> list[StageSpread]:
    """The within-stage spread of a pathway's observable."""
    stages: dict[str, list[FrameMeasurement]] = {}
    for measurement in measurements:
        stages.setdefault(measurement.stage, []).append(measurement)
    out = []
    for stage, group in stages.items():
        values = np.array(
            [float(getattr(measurement, pathway.observable)) for measurement in group]
        )
        out.append(
            StageSpread(
                stage=stage,
                mass_g=group[0].mass_g,
                frames=len(group),
                mean=float(values.mean()),
                sd=float(values.std(ddof=1)) if len(values) > 1 else float("nan"),
            )
        )
    return out
