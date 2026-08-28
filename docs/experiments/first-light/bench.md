# Bench

What is built once, and what is done in each run. Both are fixed at the moment
the first frame is taken; a bench described afterwards is not a record.

## The rig

The camera looks down at the sheet from directly above, at a height held
constant across every frame. A fixed pose is what turns perspective, lens
distortion and the height of a bean above the paper into parts of a single
fitted constant instead of per-frame corrections.

## The sheet

White A4, ISO 216, on a rigid flat backing. Paper that curls is no longer a
plane, and the homography absorbs the error silently.

A ChArUco border is printed inside the margin, with a rim of unmarked paper
between the outer markers and the sheet edge, so that no ink approaches the
boundary plain-sheet corner detection exists to find.

The bean field carries open rings printed in light grey at known board
coordinates, larger than a bean, one bean to a ring. Rings rather than filled
dots: ink under a bean thresholds as coffee and is partly occluded, so it
cannot be subtracted, where an open ring keeps the printing clear of the
silhouette. Because the board pose fixes their coordinates, the rings are
masked geometrically rather than by colour.

TODO: whether a ladder of coffee-brown ellipses of known area is printed among
the rings, which would measure boundary bias against perimeter in every frame.

TODO: ChArUco dictionary, square size and marker size.

## Lighting

Diffuse and stationary, with no window contributing. Both properties matter: a
directional source casts shadows that threshold as coffee, and light that
changes between frames moves a threshold the fitted constant assumes is held
fixed.

## Camera

Pixel 10 Pro, main lens, under the settings that keep photometry intact.

- Full sensor resolution, never a binned readout. Across the long edge of A4
  the full readout gives about 28 px/mm against 14, and a systematic
  one-pixel error in where a bean's boundary falls costs 2.3% of its mass at
  the former and 4.7% at the latter.
- Exposure merging off. Per-region tone mapping destroys the uniform white
  reference.
- White balance and exposure locked, and the values recorded.
- Raw alongside JPEG. JPEG is the working format; raw keeps linear sensor data
  available for colour work.
- No cropping, no auto-enhancement.

Images move by cable. Messaging apps and some cloud syncs recompress and strip
EXIF, and the focal length does not come back.

## Balance

Mettler-Toledo MS204TS, 0.1 mg readability, read over its serial link with
MT-SICS commands so that a reading is recorded rather than transcribed.

Beans are never weighed on the sheet. Every bean of a run starts in a dish on
the pan, and each is weighed by difference: lift one out, place it in its ring,
read the dish again. One handling operation per bean rather than two, and the
mass on the sheet is the difference of two direct readings instead of a sum of
a hundred, so it does not accumulate.

The dish is read empty at the end of the run. It returns to its tare unless a
bean was lost or chaff was shed, and at 0.1 mg it says by how much.

The draft shield stands open throughout, since a bean leaves the pan every few
seconds. Air currents cost a few tenths of a milligram against a bean of 145
mg, which the control repeatability measures rather than assumes.

## Environment

Relative humidity and temperature are recorded at each control point. A drift
observed without them is unattributable.

## The run

Beans come from a single bag. Every one of them is weighed individually and
placed in a known ring, which makes the run a single continuous operation
rather than several.

**Weigh and place.** Beans are removed from the dish one at a time and placed
in raster order, one to a ring, and the dish is read after each. Sorted
centroids recover the pairing between mass and position, and the sheet holds a
known cumulative mass after every bean.

A frame is taken every ten beans. Those frames are the dose ladder — a dozen
of them, spanning ten beans to a full sheet, each carrying an exact mass. They
are also the integrity check: a region count that disagrees with the number of
beans weighed localises a pairing error to the last ten placements instead of
losing the run.

A full A4 sheet inside the marker border holds around a hundred rings, which
is one espresso dose.

TODO: ring pitch and diameter, and the bean count that follows from them.

**The subset frames.** Beans are removed from the sheet by measured area — the
largest quarter, then the smallest quarter — and a frame is taken after each
removal. Their masses are known exactly, so these are independent frames whose
area distribution is deliberately shifted away from the one the constant was
fitted on. They do physically what the recorded per-bean areas also permit
numerically, and they carry a fresh photograph where the numerical version
does not.

**The repeats.** The beans of a full sheet are swept up, spread by hand so that
none touch, and photographed. Five times. Mass is held constant to 0.1 mg
across the five, so everything separating the five estimates is placement, rest
pose and segmentation. This comes last, since it destroys the ring placement.

**The off-protocol frames.** One already-weighed dose photographed hand-held,
off-axis, under room light, on a blank sheet. They are not analysed here. They
record what the bench is worth against the conditions the method is meant to
survive.

## Controls

The first six beans weighed are the control set. They are re-weighed at the
middle and at the end of the run, lifted from their rings and returned to them,
alongside an identical empty dish left uncovered in ambient air. The dish
separates instrument drift from real change in the beans; without it a shift is
ambiguous. Six beans by three time points leaves ten degrees of freedom on the
residual, enough to distinguish half a milligram from five, which is also the
repeatability of weighing with the shield open.

TODO: the threshold below which the three time points are aggregated, which
belongs here before the first reading.

## What is kept

- The weighed beans, labelled, with their masses. Re-measuring them is the only
  way to compare one campaign against another.
- The bag, sealed, with its roast date. Roasted coffee degasses and exchanges
  moisture, so the same beans are not the same mass a month later, which is why
  the inert dish is weighed beside them.
