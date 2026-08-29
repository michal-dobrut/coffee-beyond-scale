# coffee-beyond-scale

Every brewing method starts with "Weigh X g of coffee beans..." but what if you left your digital scale at home? As usual, math to the rescue!

There are big beans and small beans. Round and flat ones. But _on average_, an example roasted Arabica bean weighs 0.145 g with a standard deviation of 0.022 g. That means 125 beans go into the basket.

> Just count them? It cannot be true!

Well, standard deviation of sum of individual bean masses is as follows

$SD_{sum} = SD \cdot \sqrt{n}$

Mass grown 125x but its spread only 11x. Or, with 95% probability, you'll get your 18 g $\pm$ 0.5 g by just counting beans. That's only 3% error - should be enough for a tasty espresso in a crunch!

> But what if I don't weigh every coffee bean I own? 

Well, read on...

## Reading more of the photograph

Spread the beans on a sheet of paper of known size, take one photo. What happens next is a ladder — each rung reads more of the same picture and assumes less of it:

- **How many beans there are.** The 3% above. Still needs a mean bean mass from
  somewhere.
- **How much of the sheet is brown.** Cheap, and it quietly assumes your beans
  are the size mine were.
- **Every bean's outline.** The size distribution stops being an assumption and
  becomes a measurement. Done classically, and with a trained segmenter, so I
  can celebrate being 0.4% better than the classical one.
- **What each bean looks like.** Roast and variety move bean density by a fifth,
  and it's written on the bean. Not read yet.

Every new step is benchmarked against the previous one. Is it worth climbing to the top?

## Taking the error seriously

I wouldn't be myself if I gave you a number without accurate and honest error bars.

So bias is reported apart from scatter — a method that's accurate on average
because two large biases cancel is not accurate.

## Four stages

- [**shakedown**](docs/experiments/shakedown/) — try before deliberating, discover real problems cheaply. Shape processing pipeline, get a number at the end, throw it away, but keep the findings.

- [**callibration**](docs/experiments/calibration/) — one bag, but get most of that. Perfect instrumentation before investing time, gather data for error asessment.

- [**beanometry**](docs/experiments/#beanometry) — various coffees, many measurements; the analytical stage. Fitted constant taken apart into the physics it absorbed: shape, rest pose, density against roast, camera angle.

- [**field campaign**](docs/experiments/#field-campaign) — other people's beans, random camera angles, kitchen scales. Machine learning coffee on crowsd-sourced data. Improves accuracy for everyone but me.

## Results

- [**shakedown**](docs/reports/2026-08-29-run-zero-shakedown.md) — where the error actually lives. Half of it is the millimetre at a bean's edge, and the 50 MP sensor buys nothing at all.

