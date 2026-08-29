"""Making the sheet mean the same thing everywhere in the frame.

The sheet is a known reflectance in every photograph, which is what lets a
brightness be read as a coverage rather than as a lighting accident. It is
also the only white reference available, so the illumination is estimated
from the sheet itself: a grid of blocks, the paper averaged in each, filled
where a block held none, and divided out. After that, unobstructed paper
reads 1.0 and a brightness is comparable across the sheet and across frames.

Which pixels are paper is the thing being solved for, so the field is
estimated more than once. Illumination is multiplicative, so the first guess
is made in log space, where the light across the sheet is an offset and the
gap between paper and coffee is a constant wider than that offset. Later
passes ask the running field instead.

Three ways of getting this slightly wrong each cost more than the
segmentation that follows it:

- A field taken from the bright tail of the paper rather than from its middle
  sits above the paper, and every paper pixel then reads as coffee. On a bare
  sheet that was the entire measurement.
- Weighting blocks by how bright they are pulls a smoothed field towards its
  brighter blocks.
- Blurring the whole grid to reach the few blocks a bean covered flattens the
  illumination everywhere else, so only the blocks that need filling are
  filled.

What survives all three is a small overall offset, and the field is anchored
against it at the end.
"""

from __future__ import annotations

import cv2
import numpy as np

# Rec. 709 luminance, which is what the raw plane is rendered to.
LUMINANCE_WEIGHTS = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)

# Coffee returns about a tenth of what paper does, so anything above this
# share of the running estimate is paper. Set low enough to keep the darker
# corners of the sheet, and high enough to drop the shadow a bean casts,
# which is paper but is not lit like the rest of it.
PAPER_FLOOR = 0.75

# A block holding less than this share of paper is filled from its neighbours
# rather than trusted to speak for itself.
MIN_BLOCK_PAPER = 0.02


def luminance(rgb: np.ndarray) -> np.ndarray:
    """(h, w) luminance of an (h, w, 3) image, in the units of the input."""
    return rgb @ LUMINANCE_WEIGHTS


def paper_white_field(
    rgb: np.ndarray,
    *,
    blocks: int = 48,
    refine_passes: int = 2,
    smoothing_blocks: float = 0.5,
) -> np.ndarray:
    """The illumination across the sheet, as (h, w, 3) in the units of `rgb`.

    `rgb` is (h, w, 3) of the rectified sheet.
    """
    grey = luminance(rgb)
    edges = _block_edges(rgb.shape[:2], blocks)

    paper = _first_guess(grey)
    field = _from_blocks(rgb, paper, edges, smoothing_blocks)
    for _ in range(refine_passes):
        paper = grey > PAPER_FLOOR * luminance(field)
        field = _from_blocks(rgb, paper, edges, smoothing_blocks)
    return _anchored(field, grey)


def _first_guess(grey: np.ndarray) -> np.ndarray:
    """Where the paper is, before any field exists.

    Illumination multiplies, so in log space it is an offset that shifts both
    modes together while the gap between paper and coffee stays near a factor
    of ten. A threshold between them therefore survives a sheet lit three
    times as brightly at one end as at the other.
    """
    from skimage.filters import threshold_otsu

    lit = grey > 0.0
    if not lit.any():
        raise ValueError("the sheet is black")
    logged = np.log(np.maximum(grey, 1e-6))
    return logged > threshold_otsu(logged[lit])


def _block_edges(shape: tuple[int, int], blocks: int) -> tuple[np.ndarray, np.ndarray]:
    height, width = shape
    return (
        np.linspace(0, height, blocks + 1).astype(int)[:-1],
        np.linspace(0, width, blocks + 1).astype(int)[:-1],
    )


def _block_sum(values: np.ndarray, edges: tuple[np.ndarray, np.ndarray]) -> np.ndarray:
    rows, columns = edges
    return np.add.reduceat(np.add.reduceat(values, rows, axis=0), columns, axis=1)


def _from_blocks(
    rgb: np.ndarray,
    paper: np.ndarray,
    edges: tuple[np.ndarray, np.ndarray],
    smoothing_blocks: float,
) -> np.ndarray:
    """Average the paper in each block, fill the empty ones, smooth, upsample."""
    selected = paper.astype(np.float32)
    counts = _block_sum(selected, edges)
    sums = _block_sum(rgb * selected[..., None], edges)
    sizes = np.outer(
        np.diff(np.append(edges[0], rgb.shape[0])),
        np.diff(np.append(edges[1], rgb.shape[1])),
    ).astype(np.float32)

    values = sums / np.maximum(counts, 1.0)[..., None]
    grid = _fill_and_smooth(values, counts / sizes, sigma=smoothing_blocks)
    return _upsample(grid, rgb.shape[0], rgb.shape[1])


def _fill_and_smooth(
    values: np.ndarray,
    weights: np.ndarray,
    *,
    sigma: float,
    fill_sigma: float = 1.2,
    passes: int = 32,
) -> np.ndarray:
    """Fill the blocks that saw no paper, then smooth the grid lightly.

    Filling is normalised convolution restricted to the blocks that need it:
    values and weights are blurred together and the quotient is written only
    where nothing was observed, so a block that saw paper keeps what it saw.
    The smoothing afterwards is for block-to-block noise and is narrow enough
    to leave the illumination alone.
    """
    values = values.astype(np.float32).copy()
    weights = weights.astype(np.float32).copy()
    known = weights > MIN_BLOCK_PAPER
    if not known.any():
        raise ValueError("no block of the sheet showed any paper")
    weights[~known] = 0.0

    for _ in range(passes):
        if known.all():
            break
        blurred = cv2.GaussianBlur(values * weights[..., None], (0, 0), fill_sigma)
        carried = cv2.GaussianBlur(weights, (0, 0), fill_sigma)
        reachable = (~known) & (carried > 1e-6)
        if not reachable.any():
            break
        values[reachable] = blurred[reachable] / carried[reachable][..., None]
        # A filled block stands in for an observation without becoming one.
        weights[reachable] = MIN_BLOCK_PAPER
        known |= reachable

    smoothed = cv2.GaussianBlur(values * weights[..., None], (0, 0), sigma)
    carried = cv2.GaussianBlur(weights, (0, 0), sigma)
    return smoothed / np.maximum(carried, 1e-9)[..., None]


def _upsample(grid: np.ndarray, height: int, width: int) -> np.ndarray:
    blocks = grid.shape[0]
    # Block estimates sit at block centres, so the grid is resampled from
    # centre to centre rather than corner to corner.
    fine = cv2.resize(
        grid.astype(np.float32),
        (width + width // blocks, height + height // blocks),
        interpolation=cv2.INTER_CUBIC,
    )
    top, left = height // (2 * blocks), width // (2 * blocks)
    return fine[top : top + height, left : left + width]


def _anchored(field: np.ndarray, grey: np.ndarray) -> np.ndarray:
    """Scale the field so that the median paper pixel reads exactly 1.0.

    An offset is the one error the coverage cannot survive, since the ramp
    starts at the paper level: a field high by three per cent makes every
    paper pixel read as three per cent coffee.
    """
    paper = grey > PAPER_FLOOR * luminance(field)
    if paper.sum() < 1000:
        return field
    return field * float(np.median(grey[paper] / luminance(field)[paper]))


def normalise_to_paper(rgb: np.ndarray, field: np.ndarray) -> np.ndarray:
    """Divide out the illumination, so that unobstructed paper reads 1.0."""
    return rgb / np.maximum(field, 1e-9)
