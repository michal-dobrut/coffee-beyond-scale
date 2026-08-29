# Error budget

Written before the data exists, and compared against the result rather than
revised to match it.

## What the fitted constant absorbs

One constant is fitted at one bench, so every bias that multiplies every bean
in the same direction is swallowed by it: where a bean's boundary is placed,
the inflation of a silhouette formed above the paper plane, lens distortion
across the bean field, the 0.16% by which a balance calibrated against steel
reads a bean of density 0.7 g/cm³ high, and the rest-pose distribution this
bag happens to take.

Two consequences follow. The in-sample error is small for reasons unrelated to
the method being right, which is why the result is quoted on held-out beans.
And every absorbed term survives only while the bench does not move, which is
what the other campaigns exist to separate.

## Terms

- **Boundary localisation.** A systematic shift of one pixel changes a bean's
  area by perimeter times shift — near a square millimetre at this resolution,
  1.6% of area and 2.3% of mass. It carries the same sign on every bean and
  does not average away. It is absorbed into the constant while the bench
  holds, so it limits transfer rather than the result here.

- **Scatter of mass about the area relation.** Beans of equal footprint differ
  in thickness. This is the term that averages down as `1/√n`, and the only one
  that sets the error at a given dose. Every bean is weighed, so it is measured
  directly; at 8% it contributes 0.8% to a hundred-bean dose.

- **Ground truth.** Weighing by difference puts two readings into a dose, not a
  hundred, so the dose carries a few tenths of a milligram against 14.5 g. Per
  bean it is larger — the draft shield stands open — but a few tenths of a
  milligram against 145 mg is still 0.3%, well under the scatter it sits
  beside. Named here so that it is not carried any further.

- **Count error.** Beans do not touch and rings are excluded geometrically, so
  a miscount fails a frame instead of biasing it. Every frame checks its region
  count against the number of beans weighed into it.

- **Pose constancy.** A camera that does not move contributes nothing. The
  repeats bound what does move: five estimates of one dose held constant to
  0.1 mg, differing only in placement, rest pose and segmentation.

## What the controls separate

The dish read empty at the end of the run says whether beans or chaff left it.
A shortfall then has a size, and the frames it touches can be corrected or
discarded on evidence rather than on suspicion.

The six control beans and the inert dish are weighed against each other because
either alone is ambiguous. Beans moving while the dish holds still is real mass
change — degassing, moisture, static. Both moving together is the instrument.

The exponent is expected within its own uncertainty of 3/2. At a hundred beans
and 8% residual scatter that uncertainty is near 0.07, which separates 3/2 from
1 and from 2 and does not resolve a five per cent departure. A departure larger
than the uncertainty is a result about the beans.

## Predicted result

Held-out relative error on total mass, at a hundred beans, if the per-bean
scatter lands near 8%:

| estimator | on doses like the fit | on doses of extreme size |
|---|---|---|
| count | 1.5% | biased, by the shift in mean bean mass |
| coloured area | 0.8–1.0% | biased, by the shift in `√E[a]` |
| per-bean area | 0.8% | unchanged |

The first column is the honest expectation and it is a weak result: two of the
three estimators are predicted to be indistinguishable, because a hundred beans
drawn from one bag sample its area distribution well enough that the factor the
coloured-area route cannot observe barely moves. That is `method.md` being
right rather than the experiment failing — calibrated on one bag it is accurate
on that bag.

The second column is where the ladder earns its place. Assembling doses from
the extremes of measured area shifts the distribution without touching the
bench, and the estimators are predicted to separate in the order of how much of
the photograph each one reads. If they do not, the per-bean route is not doing
what the relation says it does.

A held-out error much larger than the table points at the bench rather than at
the method: light that moved, a sheet that lifted, or a frame whose count and
mass disagree.

TODO: propagate the terms above into one predicted interval rather than a list.
