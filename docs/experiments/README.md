# Experiments

Each subdirectory is one measurement campaign: a bench, a protocol, an error
budget written before the data, and what came out. The documents beside this
directory hold what is true across all of them and are cited rather than
restated.

They are listed in dependency order. Each consumes the one above it, and
results from one reshape the design of the next.

## first-light

Does the whole chain run end to end, and what does it cost? One bag, one
bench, beans placed so that none touch. Fits a single constant relating
projected area to mass and measures the error that remains.

Consumes nothing. Produces the constant, the scatter of mass about the area
relation, and a labelled lot of individually weighed beans.

## beanometry

What is that constant made of? Many beans, few bags, better optics. Takes the
single fitted number apart into the physical factors it absorbed: the exponent
measured rather than assumed, the projected-area distribution, bean shape and
rest pose, silhouette height, density against roast level.

Consumes first-light's protocol, its labelled lot, and its estimate of the
per-bean scatter, which is what sizes the campaign.

## field-campaign

Does any of it survive other people's beans? Few beans per contributor, many
bags, coarse scales, uncontrolled light. Measures between-bag and
between-condition variation and fits the corrections that turn the constant
into a function of what a photograph can observe.

Consumes beanometry's per-bean physics as a prior and its isolated bean
cutouts as the raw material for synthesising crowded scenes whose ground truth
is exact.
