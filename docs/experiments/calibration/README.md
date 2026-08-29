# Calibration

Calibrate the bench instrumentation, and measure the floor beneath everything
built on it. One bag, every bean weighed, every condition held: what error
remains when nothing is allowed to vary is the error the method itself cannot
get below.

It is not trying to produce a number about coffee. It is trying to make the
instrument trustworthy before anything expensive is measured with it.

## What it establishes

**The error floor.** With mass known to 0.1 mg, pose fixed, lighting
stationary and a single bag, everything separating repeat estimates of one
unchanged sheet is placement, rest pose and segmentation. That spread is the
best the chain can do, and every later result is quoted against it.

**The instrument constants.** Millimetres per pixel, the boundary convention
and where it is cut, the inflation of a silhouette formed above the paper
plane, and the balance's own bias against a bean of density 0.7 g/cm³ rather
than the steel it was calibrated on.

**A labelled lot.** Every bean weighed individually and placed at a known
position, so mass, area and rest pose are paired per bean rather than per
frame. That lot is the raw material the campaigns after this one consume.

## A rehearsal of beanometry, at one bag

The techniques are beanometry's: per-bean weighing by difference, per-bean
areas, the area distribution, rest pose, the dose ladder, held-out scoring.
They are run here on one bag rather than many, and on a hundred beans rather
than thousands.

The point of the reduced scope is that a technique that fails does so cheaply.
Scaling a method that has never been run is how a campaign discovers its
mistakes at full price.

## Ordinary A4, on purpose

The substrate is a sheet of ISO 216 paper, not a machined calibration target.
A person estimating a dose in their kitchen has paper, and a bench that
replaces it with something better measures a method nobody can run.

Keeping the everyday substrate costs accuracy — the shakedown put numbers on
what: a sheet that is not flat outweighs the lens, and its short edge is not
the 210 mm its standard names. Both are measured here rather than removed, so
the error floor includes them.

## What it does not establish

The fitted constant absorbs every bias that multiplies every bean in the same
direction at this bench. It is therefore accurate here and carries no
guarantee anywhere else. Taking it apart is what `beanometry` is for;
generalising it across bags and conditions is what `field-campaign` is for.

Three things are excluded by construction:

- **Merging.** Beans are placed so that none touch, which removes the hardest
  segmentation problem from the chain. The shakedown measured what happens
  when they do touch: counting fails at a cliff rather than degrading.
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
