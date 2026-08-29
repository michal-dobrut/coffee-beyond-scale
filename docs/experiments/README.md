# Experiments

Each subdirectory is one measurement campaign: a bench, a protocol, an error
budget written before the data, and what came out. The shakedown is the
exception, and its own README says why. The documents beside this directory
hold what is true across all of them and are cited rather than restated.

They are listed in dependency order. Each consumes the one above it, and
results from one reshape the design of the next.

## shakedown

What does the bench have to be? The chain run once on real photographs, before
there is a protocol to run it against, so that the error can be ranked before
anything is built to hold it. Measures the instrument, not the coffee.

Consumes nothing. Produces the ranked error budget the other campaigns are
designed against, and the requirements a bench has to meet to beat it.

## calibration

How good can this get? The bench instrumented properly and every condition
held: one bag, every bean weighed to 0.1 mg, fixed pose, stationary light,
beans placed so that none touch. What error survives that is the floor, and
every later result is quoted against it. Runs beanometry's techniques at one
bag, so a technique that fails does so cheaply.

Consumes the shakedown's bench requirements and its account of which terms
dominate. Produces the error floor, the instrument constants, and a labelled
lot of individually weighed beans.

## beanometry

What is that constant made of? Many beans, few bags, better optics. Takes the
single fitted number apart into the physical factors it absorbed: the exponent
measured rather than assumed, the projected-area distribution, bean shape and
rest pose, silhouette height, density against roast level.

Consumes calibration's protocol, its labelled lot, and its estimate of the
per-bean scatter, which is what sizes the campaign.

## field-campaign

Does any of it survive other people's beans? Few beans per contributor, many
bags, coarse scales, uncontrolled light. Measures between-bag and
between-condition variation and fits the corrections that turn the constant
into a function of what a photograph can observe.

Consumes beanometry's per-bean physics as a prior and its isolated bean
cutouts as the raw material for synthesising crowded scenes whose ground truth
is exact.
