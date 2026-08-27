# Uncertainty

The estimate is worth little without an interval around it, and the interval is
worth little unless it covers the truth as often as it claims.

## Why counting concentrates

A single roasted Arabica bean has a mass of roughly 0.145 g with a standard
deviation near 0.022 g. Summing `n` independent beans scales the standard
deviation by `sqrt(n)` while scaling the mean by `n`, so relative error falls as
`1/sqrt(n)`. At a hundred beans the sum carries about 0.22 g of spread against a
14.5 g mean — near 3% at 95% coverage, from bean variability alone.

## Error budget

Bean variability is the floor, not the total. The other terms:

- **Scale.** Corner localisation error in the homography scales every length,
  and so enters an area measurement squared.
- **Counting.** Touching beans merge and shadows split them; the two do not
  cancel.
- **Population mismatch.** A mean bean mass calibrated on one jar applied to a
  different roast level or bean size is a bias, not a variance.

## Calibration

An interval claiming 95% coverage is checked by measuring how often it contains
the scale reading across held-out sessions. Nominal and empirical coverage
diverging is the finding, not a defect to be tuned away.

TODO: the budget above is a list of terms, not yet a propagated total.
