"""How much of each pixel is coffee.

A pixel on the boundary of a bean is part bean and part paper, and where that
boundary is placed sets the measured area. Raw is linear in scene radiance,
so a boundary pixel is the straight mixture of the two things under it and
the fraction can be solved for rather than guessed:

    coverage = (paper - value) / (paper - coffee)

That is the soft convention. The hard one thresholds at the valley between
the two modes and counts whole pixels, and it is implemented beside the soft
one because which is better is a measurement rather than an argument.

The soft convention cannot ramp from paper at exactly 1.0, and finding that
out cost a bare sheet reading 3100 mm2 of coffee. Coverage is clipped below
at zero, so paper noise either side of 1.0 is rectified: the darker half
becomes coverage and the lighter half becomes nothing, and what should
average to zero averages to a fifth of a sixteen-gram dose. The ramp
therefore starts a few widths of the paper's own noise below 1.0, which
costs the faintest boundary pixels and is measured on the bare frames rather
than assumed away.

What neither convention separates is a shadow from a bean. A shadow is paper
under less light, so it darkens exactly as partial coverage does. The frames
of the bare sheet are what put a number on that too: whatever coverage they
report is the floor.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .photometry import luminance

CONVENTIONS = ("soft", "hard")

# Between the paper mode near 1.0 and the coffee mode near 0.1 the histogram
# is close to empty, and this is where the hard threshold sits.
VALLEY = 0.5

# A dark-roast bean returns about a tenth of what the paper does. The value
# only matters when a frame holds too few beans to measure it, which is when
# there is almost nothing to measure anyway.
FALLBACK_COFFEE_REFERENCE = 0.10
MIN_DARK_FRACTION = 0.002

# How far below the paper the soft ramp starts, in widths of the paper's own
# noise, and the range that ramp is allowed to sit in whatever the frame says.
NOISE_WIDTHS = 3.0
PAPER_REFERENCE_LIMITS = (0.80, 0.99)


@dataclass(frozen=True)
class Coverage:
    """Per-pixel coffee coverage over the sheet, and how it was arrived at.

    `fraction` is (h, w) in [0, 1]. The two references are the luminances,
    relative to paper, that the ramp runs between. `has_coffee` says whether
    the frame held enough dark pixels to measure the coffee end rather than
    fall back to a default.
    """

    fraction: np.ndarray
    convention: str
    paper_reference: float
    coffee_reference: float
    paper_noise: float
    has_coffee: bool


def coffee_coverage(
    normalised_rgb: np.ndarray,
    *,
    convention: str = "soft",
    coffee_reference: float | None = None,
    paper_reference: float | None = None,
    noise_widths: float = NOISE_WIDTHS,
) -> Coverage:
    """Resolve each pixel of a paper-normalised sheet into coffee and paper.

    `normalised_rgb` is (h, w, 3) with unobstructed paper at 1.0.
    """
    if convention not in CONVENTIONS:
        raise ValueError(f"unknown convention {convention!r}")

    grey = luminance(normalised_rgb)
    dark = grey < VALLEY
    has_coffee = float(dark.mean()) >= MIN_DARK_FRACTION
    if coffee_reference is None:
        coffee_reference = (
            float(np.median(grey[dark])) if has_coffee else FALLBACK_COFFEE_REFERENCE
        )

    noise = paper_noise(grey)
    if paper_reference is None:
        paper_reference = float(
            np.clip(1.0 - noise_widths * noise, *PAPER_REFERENCE_LIMITS)
        )

    if convention == "hard":
        fraction = (grey < VALLEY).astype(np.float32)
    else:
        span = max(paper_reference - coffee_reference, 1e-6)
        fraction = np.clip((paper_reference - grey) / span, 0.0, 1.0).astype(np.float32)

    return Coverage(
        fraction=fraction,
        convention=convention,
        paper_reference=float(paper_reference),
        coffee_reference=float(coffee_reference),
        paper_noise=noise,
        has_coffee=has_coffee,
    )


def paper_noise(grey: np.ndarray) -> float:
    """How much unobstructed paper varies about 1.0, as a standard deviation.

    Read from the median absolute deviation so that beans, their shadows and
    the darkened rim at the edge of the sheet do not widen it.
    """
    paper = grey[(grey > 0.8) & (grey < 1.2)]
    if paper.size < 1000:
        return 0.0
    return float(1.4826 * np.median(np.abs(paper - np.median(paper))))


def inset_mask(shape: tuple[int, int], *, px_per_mm: float, margin_mm: float) -> np.ndarray:
    """(h, w) bool, true inside the sheet once `margin_mm` is trimmed off.

    The trim is what keeps a corner placed a little outside the sheet from
    admitting a strip of table, which on a wooden table is the same colour as
    the beans. It costs whatever coffee stood in the trimmed ring, and that
    cost is measured rather than assumed.
    """
    height, width = shape
    margin_px = int(round(margin_mm * px_per_mm))
    mask = np.zeros((height, width), dtype=bool)
    if 2 * margin_px >= min(height, width):
        raise ValueError("the margin leaves no sheet to measure")
    mask[margin_px : height - margin_px, margin_px : width - margin_px] = True
    return mask
