"""Separating the coffee on the sheet into beans, and counting them.

Where beans do not touch, a connected component is a bean and counting is
exact. Where they do, a component holds several, and a distance transform
with a watershed splits it on the waists between them. That works while the
waists exist; a heap does not have them, and no amount of tuning puts them
back.

So a region whose area falls outside what one bean can occupy is not counted
and not quietly divided into a plausible number either. Its area is reported
instead, as the share of the sheet the count could not resolve. A count
estimator that quietly guesses at crowded frames reads as slightly wrong
everywhere; one that says how much it could not see reads as right where it
works, and the crowding shows up as the thing it is.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import ndimage
from skimage.feature import peak_local_max
from skimage.morphology import remove_small_holes, remove_small_objects
from skimage.segmentation import watershed

# A roasted arabica bean of 0.145 g lies with a footprint near 50 mm2. The
# band is wide enough for the tails of one bag and narrow enough that two
# merged beans fall outside it.
MIN_BEAN_AREA_MM2 = 18.0
MAX_BEAN_AREA_MM2 = 130.0
# Two beans side by side leave a waist; the distance transform peaks either
# side of it are about this far apart.
MIN_SEPARATION_MM = 3.5
SPECK_AREA_MM2 = 4.0
HOLE_AREA_MM2 = 6.0


@dataclass(frozen=True)
class BeanField:
    """What separating one frame into beans found.

    `areas_mm2` holds one entry per counted bean. `unresolved_area_mm2` is
    coffee that landed in a region too large or too small to be one bean, and
    `blob_count` is how many connected components there were before splitting,
    so that the work the watershed did is visible.
    """

    count: int
    blob_count: int
    areas_mm2: np.ndarray
    unresolved_area_mm2: float
    labels: np.ndarray

    @property
    def median_area_mm2(self) -> float:
        return float(np.median(self.areas_mm2)) if self.count else float("nan")


def separate(
    coverage_fraction: np.ndarray,
    *,
    px_per_mm: float,
    inside: np.ndarray | None = None,
    threshold: float = 0.5,
    min_area_mm2: float = MIN_BEAN_AREA_MM2,
    max_area_mm2: float = MAX_BEAN_AREA_MM2,
    min_separation_mm: float = MIN_SEPARATION_MM,
) -> BeanField:
    """Split the coffee on a rectified sheet into individual beans.

    `coverage_fraction` is (h, w) in [0, 1] as `segment.coffee_coverage`
    returns it, and `inside` restricts the count to part of the sheet.
    """
    mask = coverage_fraction >= threshold
    if inside is not None:
        mask &= inside

    pixel_area_mm2 = 1.0 / px_per_mm**2
    # Both drop regions of at most `max_size` pixels.
    mask = remove_small_holes(mask, max_size=int(HOLE_AREA_MM2 / pixel_area_mm2))
    mask = remove_small_objects(mask, max_size=int(SPECK_AREA_MM2 / pixel_area_mm2))

    blob_count = int(ndimage.label(mask)[1])
    if blob_count == 0:
        return BeanField(0, 0, np.empty(0), 0.0, np.zeros(mask.shape, np.int32))

    distance = ndimage.distance_transform_edt(mask)
    peaks = peak_local_max(
        distance,
        labels=mask,
        min_distance=max(1, int(round(min_separation_mm * px_per_mm))),
        exclude_border=False,
    )
    seeds = np.zeros(mask.shape, dtype=np.int32)
    seeds[tuple(peaks.T)] = np.arange(1, len(peaks) + 1)
    labels = watershed(-distance, seeds, mask=mask).astype(np.int32)

    sizes = np.bincount(labels.ravel())
    sizes[0] = 0
    areas_mm2 = sizes * pixel_area_mm2
    counted = (areas_mm2 >= min_area_mm2) & (areas_mm2 <= max_area_mm2)
    unresolved = float(areas_mm2[(areas_mm2 > 0) & ~counted].sum())

    return BeanField(
        count=int(counted.sum()),
        blob_count=blob_count,
        areas_mm2=areas_mm2[counted],
        unresolved_area_mm2=unresolved,
        labels=labels,
    )
