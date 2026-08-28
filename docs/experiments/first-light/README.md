# First light

The whole chain, run once, on one bag: photograph a spread of beans, recover
their projected areas, and predict the mass a balance reads. The number it
produces shows that the parts fit together. It measures nothing about coffee.

## What it establishes

A single constant relating summed projected area to mass, fitted on one bag at
one fixed camera pose, and the error that remains once it is fitted. Every bean
is weighed individually and placed at a known position, so the constant, the
exponent it is raised to, and the scatter about the relation are all measured
on the same beans.

The error is quoted on beans held out of the fit; the in-sample figure appears
beside it only to show the gap between them.

The same photograph is read by three estimators of increasing appetite — the
count alone, the total coffee-coloured area, and every bean's area — scored
against each other on the same held-out beans. Counting consumes none of the
geometry, which makes it the control that says whether a shortfall lies in the
relation or in the measurement of area.

## What it does not establish

The fitted constant absorbs every bias that multiplies every bean in the same
direction at this bench. It is therefore accurate here and carries no
guarantee anywhere else. Taking it apart is what `beanometry` is for;
generalising it across bags is what `field-campaign` is for.

Three things are excluded by construction:

- **Merging.** Beans are placed so that none touch, which removes the hardest
  segmentation problem from the chain. Crowded layouts belong where the
  labelled data to learn through them exists.
- **Roast level.** One bag holds one roast, so there is nothing for a roast
  model to learn from. Within-bag appearance is another matter: per-bean
  colour is measured beside per-bean mass and area, and regressed against what
  the area relation leaves over.
- **Pose variation.** The camera does not move, so pose is part of the constant
  rather than a per-frame correction.

## Results

TODO: the campaign has not been run.

## The documents

- `protocol.md` — the sheet carried to the bench, filled in as the run goes.
- `bench.md` — what is built, and why the run is shaped the way it is.
- `analysis.md` — how a photograph becomes a mass in grams.
- `error-budget.md` — what limits the result, written before the data exists.
