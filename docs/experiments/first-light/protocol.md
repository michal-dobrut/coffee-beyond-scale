# Protocol — first light

The sheet carried to the bench and filled in as the run proceeds. It says what
to do and how to know it worked. Why it is shaped this way is in `bench.md`,
and what it is expected to return is in `error-budget.md`; neither repeats an
instruction, and this sheet gives no reasons.

Around two hours from setup to the last frame.

## Session

| | |
|---|---|
| session id | |
| date | |
| operator | |
| bag — roast, origin | |
| roast date | |
| beans in run | |
| frame ids | |
| balance log file | |

| | start | middle | end |
|---|---|---|---|
| time | | | |
| relative humidity | | | |
| temperature | | | |
| control beans, six masses | | | |
| inert dish | | | |

## Setup

Once per session, before the first frame.

- [ ] Sheet flat on its rigid backing, no lift at any corner
- [ ] Camera fixed, looking straight down, height set and locked
- [ ] Lighting on and warmed, no window contributing
- [ ] Main lens; ultrawide and tele not used
- [ ] Full sensor resolution, not a binned readout
- [ ] Exposure merging off, no auto-enhancement, no cropping
- [ ] White balance locked, value written on this sheet
- [ ] Exposure locked, value written on this sheet
- [ ] Raw alongside JPEG
- [ ] Balance levelled, internal adjustment run, dish tared
- [ ] Inert control dish set out uncovered, beside the balance

## The run

| # | do | record | check |
|---|---|---|---|
| 1 | Frame the empty sheet | frame id | board solves; every ring found |
| 2 | Load every run bean into the dish on the pan | dish total | |
| 3 | Weigh out beans 1–6, the control set, into rings 1–6 | six masses | |
| 4 | Weigh the inert dish; log humidity and temperature | start column above | |
| 5 | Lift one bean, place it in the next ring in raster order, read the dish | dish reading, logged | bean inside its ring, touching no other |
| 6 | Every tenth bean, take a frame | frame id, bean count | region count equals beans placed |
| 7 | At the halfway frame, re-weigh the control beans and the inert dish, and log humidity and temperature | middle column above | drift under TODO |
| 8 | Carry on to a full sheet, then frame it | frame id | region count equals beans placed |

## After the sheet is full

| # | do | record | check |
|---|---|---|---|
| 9 | Re-weigh the control beans and the inert dish; log humidity and temperature | end column above | drift under TODO |
| 10 | Read the dish empty | empty reading | at tare within TODO |
| 11 | Lift out the heaviest quarter by recorded mass, frame, return them | frame id, ring ids | region count equals beans left |
| 12 | Repeat for the lightest quarter | frame id, ring ids | region count equals beans left |
| 13 | Sweep the sheet, spread by hand so that none touch, frame. Five times | five frame ids | no two beans touching |
| 14 | One dose hand-held, off-axis, room light, blank sheet | frame ids | |
| 15 | Return the beans to a labelled container; seal the bag | container id | |

Steps 11 and 12 select on mass because that is what is known at the bench.
Subsets selected on area are formed afterwards from the recorded areas.

## Observations

Anything that departed from the above, and anything that looked wrong. The
failures worth having are never on the list.
