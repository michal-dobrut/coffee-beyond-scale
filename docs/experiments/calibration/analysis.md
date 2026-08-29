# Analysis

How a photograph becomes a mass in grams.

## Rectification

The ChArUco board gives the homography that removes perspective and the scale
in millimetres per pixel. Corner detection against the plain sheet runs beside
it: the board is the reference, and the plain-sheet route is the thing being
measured against it.

## The boundary convention

A bean's boundary is not a line but a gradient a few pixels wide, and where it
is placed sets the measured area. Boundary pixels contribute their fractional
coverage — a ramp between two levels in the segmentation channel, summed —
rather than being thresholded into a binary mask. A hard threshold is
implemented alongside it, because the choice between the two is settled by
measurement rather than by argument.

Individually weighed beans are what settles it. Each convention gives a
different area for the same bean, and the one whose areas predict the known
masses with less scatter and no trend against bean size is the one that keeps.

## Segmentation

Coffee against white paper separates in the `a*` channel of CIELAB. Connected
components give one region per bean, since the beans do not touch. Printed
rings are excluded geometrically from their known board coordinates rather
than by colour. A region whose area falls outside the range a single bean can
occupy fails the frame rather than being dropped from it.

## Four estimators

The same photograph is read four ways, ordered by how much of it each one
consumes. All fit their parameters on the same beans and are scored on the
same held-out beans.

| estimator | consumes | fitted |
|---|---|---|
| count | the number of beans | mean bean mass |
| coloured area | total coffee-coloured area | one ratio |
| per-bean area | every bean's area | the constant below |
| per-bean appearance | area and colour per bean | TODO |

Counting is the reason to keep the ladder. It touches none of the geometry —
not the scale in millimetres per pixel, not the homography, not the boundary
convention, not the height of a bean above the paper. It needs only the count
to be right, which holds here because the beans do not touch. If the per-bean
area estimator fails to beat it, the fault is in the geometry rather than in
the relation, and the ladder says so without a separate experiment.

The fourth rung is not fitted here. One bag holds one roast level, so there is
no roast variation to learn from. What is available is the residual: per-bean
mass, area and colour are measured on the same beans, so colour can be
regressed against what the area relation leaves over. Roasting within a bag is
uneven enough that a real effect is possible, and a clean null is worth as much
— it is the first evidence for or against building the rung at all. Per-bean
colour is the noisiest measurement on the frame, since illumination varies
across the sheet and bean curvature throws highlights, so a weak effect is
recorded as unresolved rather than as absent.

## From area to mass

Per-bean areas are summed under the relation in `method.md` and scaled by one
constant:

```
M = k · Σ aᵢ^β
```

Both parameters come from the individually weighed beans, as a log-log
regression of per-bean mass against per-bean area. The regression returns `β`
to be compared against the 3/2 the shape argument predicts, and the residual
scatter that sets how the error falls with dose. Holding `β` at 3/2 and fitting
`k` alone is the fallback if the fitted exponent is consistent with it.

## The split

Beans are the unit of splitting, not frames. The dose-ladder frames are
cumulative, so they share beans with each other and a frame-level split would
measure interpolation between near-duplicates. A bean-level split is available
here only because every bean carries its own mass: the relation is fitted on
one half of the beans and scored on doses assembled from the other half.

Held-out doses come in two kinds. Ones drawn at random from the held-out beans
have the same area distribution the fit saw. Ones assembled from the extremes
of measured area do not, and they are what separates the estimators — a dose of
small beans has a lower mean bean mass than the count estimator was given, and
a different `√E[a]` than the coloured-area estimator absorbed. The subset
frames test the same thing on a fresh photograph rather than on a re-reading of
one already taken.
