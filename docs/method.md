# Method

The physics that holds whichever campaign is running, and the vocabulary for
what a measurement is worth. What any one campaign does with it is under
`experiments/`.

## Rectification

The beans are spread on a sheet of paper whose dimensions are known — A4, ISO
216. Its four corners in the image give the homography that removes
perspective, and its known width fixes the scale in millimetres per pixel.
Everything downstream works on the rectified image, where a pixel has a
constant physical area.

The same four corners, with the camera's focal length, also give the camera's
pose relative to the sheet. The homography alone does not need the focal
length; the height correction below does.

## Beans stand above the plane they are measured in

The homography calibrates the paper plane. The beans sit on top of it, and a
bean's silhouette is formed near its mid-height, two to three millimetres up.
A feature at height `h`, viewed from a camera at distance `H`, is magnified by
`H / (H - h)` relative to a feature in the plane. Held at arm's length, `H` is
300 to 400 mm, so lengths are inflated by around 0.7%, areas by 1.4%, and a
mass that scales as area to the 3/2 by roughly 2%.

Against a target of 3% this is not a rounding error, and it does not shrink
with more beans: it is a bias, applied to every bean in the frame in the same
direction. It is also exactly correctable, because the camera pose is
recoverable from the sheet. Under a tilted camera the correction varies across
the frame, which is what makes the tilt worth recording rather than avoiding.

## From area to mass

A bean resting on paper presents a projected area proportional to its length
times its width. If beans of different sizes have the same shape, thickness
scales as the square root of that area, and

```
m = k · A^(3/2)
```

The exponent is measured, not assumed: a log-log regression of per-bean mass
against per-bean projected area returns it. Agreement with 3/2 confirms shape
is size-independent across the population; a departure from it says beans of
different sizes are differently proportioned, which is a result about the
beans rather than a defect in the fit.

## What each observable is worth

One photograph can be read at several depths. Each reads more of it and
assumes less.

**The count alone.** A single roasted Arabica bean has a mass near 0.145 g with
a standard deviation near 0.022 g. Summing `n` independent beans scales the
standard deviation by `sqrt(n)` while scaling the mean by `n`, so relative
error falls as `1/sqrt(n)`. At a hundred beans the sum carries about 0.22 g of
spread against a 14.5 g mean — near 3% at 95% coverage, from bean variability
alone. That is the floor for a method whose only observable is the count. It is
not the floor for the problem.

**The total coffee-coloured area.** Summing the relation above over `n` beans
gives `k·n·E[a^1.5]`, while the coloured area is `n·E[a]`. Eliminating `n`:

```
M = k · S · E[a^1.5] / E[a]  ≈  k · S · sqrt(E[a])
```

The area route therefore carries a factor of the square root of the mean bean
area that it cannot observe. Calibrated on one bag it is accurate on that bag;
applied to beans of a different size it drifts, in a direction set by which way
the size moved.

**Every bean's area.** Separating the beans removes the unobserved factor,
because the area distribution is then measured rather than assumed. What
remains is the scatter of mass about the area relation, not the full spread of
the population, and that is what buys headroom below `1/sqrt(n)`.

**Every bean's appearance.** Unread. It is where the constant's remaining
dependence on roast and origin is written.

## Roast changes the constant

Roasting expands a bean and drives mass out of it, so bean density falls as
roast darkens — around 0.70 g/cm³ light against 0.55 g/cm³ dark. The
area-to-mass constant `k` inherits that spread. Estimating roast from the image
requires colour that means the same thing under different light, which is what
the white sheet supplies: it is a known reflectance in every frame, and
normalising against it is what makes colour comparable across sessions and
cameras.

## What the method assumes known

Three positions, in increasing order of how much the user has to supply and
decreasing order of error:

- **Universal.** Literature values for mean bean mass and its spread. No setup,
  worst accuracy, and wrong for any population that is not average.
- **Self-calibrating.** Nothing supplied per bag. The photograph contains the
  projected-area distribution of the very sample being dosed, so the population
  is observed rather than assumed; only the area-to-mass constant has to come
  from elsewhere, and roast is estimable from the same image.
- **User-calibrated.** The user weighs one sample of their bag once. Most
  accurate, and it concedes the premise — but it is also the diagnostic that
  separates pipeline error from population error, because it removes the
  population term entirely.

This is the axis the campaigns move along. `calibration` sits at the
user-calibrated end by construction, since it weighs every bean;
`field-campaign` is an attempt on the self-calibrating position.

## Error budget

Three terms, combined in quadrature, reported separately:

```
sigma_total² = sigma_population² + sigma_pipeline² + sigma_calibration²
```

- **Population.** Bean-to-bean variability. Shrinks when per-bean areas are
  measured rather than assumed.
- **Pipeline.** Corner localisation error scales every length and enters an area
  measurement squared. Touching beans merge and shadows split them; the two do
  not cancel.
- **Calibration.** The area-to-mass fit has its own uncertainty, and it widens
  away from the range of doses the fit was made over. A prediction interval, not
  a confidence interval on the fitted line, is what a new photograph needs.

A constant calibrated on one bag and applied to a different roast level or bean
size is not in this budget at all. It is a bias, and what addresses it is which
calibration position the method is operating in.

Each campaign instantiates these terms for its own bench, before it has data.

## Bias does not average away

Several of the largest errors have a sign, and `sqrt(n)` does not touch them:

- Height above the paper plane inflates every silhouette, always outward.
- Occlusion and merging remove beans and area, always downward.
- A threshold that admits boundary pixels adds area to every bean, always
  upward.
- Dark roasts are oily and throw specular highlights that threshold as paper,
  opening holes in masks; beans cast shadows that threshold as coffee. Both
  have a sign, and neither cancels the other.

Reporting a single scatter figure hides all of them. Bias and scatter are
therefore reported apart, and a method that is accurate on average because two
large biases cancel is recorded as what it is.

## Calibration of the interval

The estimate is worth little without an interval around it, and the interval is
worth little unless it covers the truth as often as it claims.

An interval claiming 95% coverage is checked by measuring how often it contains
the balance reading on held-out data, grouped so that nothing contributes to
both the fit and the check. What the unit of grouping is belongs to each
campaign, and it has to be coarser than the correlation in that campaign's
measurements: frames that share beans are not independent of one another, and
neither are sessions that share a bag.

Nominal and empirical coverage diverging is the finding, not a defect to be
tuned away.

## Reporting

Relative absolute error on total mass is the headline, quoted as a median and a
95th percentile rather than a mean, which a single merged blob distorts.
Agreement against the balance is shown as difference versus mean with limits of
agreement, the standard presentation for a new instrument measured against a
reference one, which makes a bias that varies with dose visible where a single
error figure would not.

TODO: mean bean mass is a per-bag constant here; predicting it from roast level
and bean size is the open problem.
