# Run zero: what the shakedown measured

Session `run-zero`, 29 frames, 2026-08-29. One bag of Brazylia Monte Carmelo,
espresso roast, roasted 2026-08-10, on unbacked A4, hand-held Pixel 10 Pro.

The pipeline runs end to end and both pathways return a mass. What the session
actually measured is the bench: where the error lives, what the camera is
worth, and which of these numbers will not survive contact with a second bag.

| | |
| --- | --- |
| Count repeatability | **0.00%** — nine photographs of one unchanged sheet returned 151 beans, nine times |
| Count linearity | **+48%** — the constant fitted at 16 g is wrong by half at 50 g, where beans touch |
| Area, median error | **2.5%** — in-sample, on the same beans the constant was fitted to |
| Boundary band | **1.12 mm** — the width of a bean's edge. It holds half the area being measured |

## The result

Two pathways read the same rectified sheet and differ only in what they take
from it. They fail in opposite directions, and that is the useful part.

| Pathway | Constant | Same sheet, 9 photos | Pose, +20° tilt | 16 g → 50 g | Bare sheet |
| --- | --- | --- | --- | --- | --- |
| covered-area | 0.001487 g/mm² | 1.20% | +5.1% | ±3.4% | 0.002–0.17 g |
| bean-count | 0.1058 g/bean at 16 g | 0.00% | +0.13% | +48% | 0.00 g |

The count is the more precise instrument and the less honest one. It touches
none of the geometry — not the millimetres per pixel, not the homography, not
the boundary convention — so tilting the camera twenty degrees moves it by a
thousandth. But it only works while beans stay apart. At 50 g the watershed
stopped finding waists between them and left a third of the covered area in
regions too large to be one bean, which is why its constant jumps by half. The
pathway does not degrade gracefully; it reports what it could not resolve and
stops.

The area pathway survives crowding and is linear across a threefold change in
dose, but it pays for it: it reads 5% high when the camera leans over, and 2.6%
high on the same 151 beans merely re-poured. Those are not noise. They are the
beans standing above the paper plane and lying in different poses, which is the
physics `docs/method.md` predicts and the fitted constant silently absorbs.

### What the calibration is worth

One constant per pathway, fitted on the frames it is then scored against. That
in-sample 2.5% is not an accuracy claim — it is a floor. The number that means
something is the 1.20% spread across nine photographs of a sheet that nothing
happened to, because everything separating those nine is the bench and the
pipeline.

## Where the error is

Ranked by how much of the area estimate each moves. The first three were
surprises; the last is the one everybody expects and it turned out not to
matter at all.

| Source | Moves the area by | How it was measured |
| --- | --- | --- |
| Where the boundary is cut | ~3.8% per pixel of threshold shift | the gap between the two conventions, at 12 px/mm |
| Camera tilt ≥ 20° | +5.1% | oblique frames against near-nadir, same beans |
| Re-pouring the same beans | +2.6% | `sparse-scatter` against `sparse-settled`, 151 beans both |
| Sheet flatness | 1.4–12 px of edge bow | straight-line fit per sheet edge |
| Sampling resolution | 0.1% | 6, 12, 20, 24 px/mm compared |

### 1. The boundary is a millimetre wide

A bean's edge is not a line. Measured on the rectified sheet, the band where
coverage runs between 5% and 95% is 1.12 mm across — and it comes back at
1.12 mm whether the sheet is rectified at 12 or 24 pixels per millimetre, so it
is the scene, not the sampling. That band contains 5 400 mm² against
10 500 mm² of total measured coffee. **Half of what is being measured is edge.**

It follows that where that ramp is cut is the largest single lever on the
answer, and no amount of resolution helps. A one-pixel shift of the boundary
costs 3.8% of the area at 12 px/mm and 1.9% at 24. Most of the millimetre is
not optical blur — it is the bean's own curved flank turning away from the
light, plus the penumbra it casts.

The soft convention unmixes linearly across the ramp but cannot start at paper
exactly: clipping coverage at zero rectifies paper noise into coverage.

| Ramp foot | Bare sheet reads |
| --- | --- |
| at paper level | 3 100 mm² — a fifth of a sixteen-gram dose |
| three noise widths below paper | 180 mm² |

### 2. Tilt costs 5%, and it is a bias

Frames shot at 20° or more from the sheet normal read 5.1% more area than
near-nadir frames of the same beans, and their spread among themselves is 6.6%
against 1.35% for the flat ones. This is the term `docs/method.md` derives: a
bean's silhouette forms two to three millimetres above the paper the homography
calibrates, so it is magnified, and under a tilted camera the magnification
varies across the frame. It has a sign, it is on every bean, and averaging more
beans does nothing to it.

### 3. The sheet was not flat, and that beat the lens

Walking each sheet edge and fitting a straight line leaves a bow of 8 to 24
pixels at the edge midpoints. The obvious culprit is barrel distortion, so it
was tested properly: a single radial coefficient fitted across fourteen frames
at once — a plumb-line calibration — took the residual straightness from 7.59
to 7.39 pixels. It removed almost nothing.

Per frame it varies threefold between frames shot at the same distance and
tilt, from 1.4 to 12 pixels. A lens cannot do that; a sheet of paper lying
loose on a table can. Run zero had no rigid backing, and that is the dominant
geometric error in the session. It is also why the reprojection residual has a
floor around 4.6 px that better clicking will not remove.

### 4. The sheet is not 210 mm

Four corners of a rectangle fix the ratio of its edges. Holding the long edge
at 297 mm, the annotated corners across all 29 frames fit a short edge of
**210.63 mm**, and adopting it halves the reprojection residual from 9.32 to
4.59 pixels. Independently, the recovered aspect ratio implies 210.87 ± 1.23 mm.

This is an ordinary sheet of paper, not a mistake — ISO 216 allows ±2 mm at
this size. But the corners can only see the ratio; an error in both edges
together is invisible here and scales every area measured. The fix is a caliper
on the actual sheet and the number written into the session record.

### 5. Resolution is not a limiting factor

Rectifying the sheet at 6, 12, 20 and 24 pixels per millimetre gives the same
covered area to within 0.1% and the same bean count exactly. Six pixels per
millimetre is a 1.3-megapixel sheet — about a fortieth of the sensor. The 50 MP
readout buys nothing for either pathway, because the 1.12 mm scene blur is two
orders of magnitude wider than the pixel grid.

That is worth knowing before spending anything on optics. What would buy
resolution is removing the blur — harder light, a flatter bean field, a longer
lens further back — not more pixels.

## The camera, measured against itself

Every figure below came out of these 29 frames, and several disagree with what
the instrument notes assume.

| Quantity | Assumed | This session | Standing |
| --- | --- | --- | --- |
| Working distance | 201 mm | 209 mm | corrected — the `/36` shortcut assumes a 3:2 sensor; this one is 4:3, so the 35 mm equivalence is by diagonal |
| Distance in use | — | 224–407 mm | measured from pose; EXIF `SubjectDistance` reports a flat 250 mm |
| Sampling on the sheet | 27.5 px/mm | 13.8–25.7 | the sheet never filled the long side |
| Camera tilt | 0° nominal | 0.4–39.9° | hand-held; nine frames are under 5°, the rest are not |
| Focal length | 5750 px (6.90 mm, firmware) | 6093 ± 224 px (7.31 mm implied) | unresolved — self-calibrated from twelve tilted frames; a non-flat sheet biases it, and adopting it barely moves the residual |
| Depth of field | 6.9 mm | 9.0 mm | clears at 230 mm, against beans 4–5 mm tall |
| Illumination across sheet | — | 3.4–4.6× | severe; no global threshold survives this, and the paper's own white field is what makes it tractable |
| Paper noise | — | 2.6% | standard deviation about the normalised paper level |
| Coffee reflectance | — | 0.108 | this bag, relative to the sheet, espresso roast |

### Two traps in the raw file

The DNG records its as-shot illuminant as `AsShotWhiteXY`, a chromaticity,
where LibRaw reads `AsShotNeutral`. So the as-shot white balance arrives as
`[0, 1, 0, 0]` — empty — and `rgb_xyz_matrix` comes back all zeros. Anything
trusting `use_camera_wb` silently gets something else. The pipeline pins a fixed
daylight balance and normalises against the sheet instead, which is more correct
anyway: the sheet is a known reflectance in every frame and the camera's guess
is not.

And the two planes of one capture are three different sizes — the raw plane is
8156 × 6140, the DNG's own default crop is 8140 × 6124, and the JPEG is
8160 × 6144. A corner clicked in one does not carry to another. The corner file
records which plane it was made in for exactly this reason.

## What will backfire

Ranked by how much trouble each causes, not by how easy it is to fix.

**The table is coffee-coloured, and glossy.** Dark wood thresholds as coffee, so
every pixel outside the sheet has to be excluded by the corners rather than by
colour — the segmentation has no defence of its own. Worse, the surface is
polished enough to return a specular image of the sheet beside it. That
reflection is bright and nearly neutral, which is exactly the test a paper
detector uses, and the automatic corner finder annexed it on a third of the
frames. *Fix: a matt, mid-grey, non-wooden surface. Not white, which would give
the sheet edge no contrast; not dark brown, which gives it the wrong kind.*

**The sheet has no rigid backing.** A loose sheet is not a plane, and the
homography absorbs the error without complaining. This is already the dominant
geometric term — larger than the lens, larger than corner placement — and it
varies frame to frame, so it cannot be calibrated out either. *Fix: tape or
clamp the sheet to something rigid and flat. The `calibration` bench document
already requires it; run zero is the measurement of what skipping it costs.*

**Counting stops working before it is expected to.** At 16 g on A4 the beans are
separate and the count is exact nine times out of nine. At 50 g it under-reads
by 40% and its constant moves by half. The failure is not gradual noise, it is a
cliff, and it sits between the two doses that happened to be shot. *Fix: find
the cliff deliberately, with a dose ladder at 10, 20, 30, 40 g on one sheet.
That curve is a result worth publishing, and it gives the maximum dose the count
pathway can carry.*

**Calibrating on the sample being measured.** One constant fitted to these
frames and scored on these frames gives 2.5%, and that number means almost
nothing. It absorbs the sheet size, the boundary convention, the height of a
bean above the paper, the rest-pose distribution of this pour, and the roast of
this bag — every one of them a bias that multiplies every bean in the same
direction. *Fix: weigh individual beans. The moment per-bean masses exist, the
split can be made on beans rather than frames, and the number becomes a claim
rather than a fit residual.*

**Hand-held pose spends accuracy that cannot be recovered.** Tilt ran from 0.4°
to 39.9° and distance from 224 to 407 mm across one session. The area pathway
reads 5% high on the tilted frames. A fixed rig turns that from a per-frame
error into part of a constant. *Fix: any fixed mount. Failing that, reject
frames on tilt — the pipeline already reports it per frame, so the rule can be a
filter rather than a discipline.*

**White balance moved mid-session.** The record notes auto white balance for the
first sixteen-gram stage and a locked 6050 K afterwards, and the paper's a*
shifts by five units between them. It does not hurt these two pathways, because
both normalise against the sheet. It would wreck any roast estimate, which is
the rung where colour has to mean the same thing twice. *Fix: lock it before the
first frame and write the value on the sheet, as the `calibration` protocol
already says.*

**Shadows are counted as coffee.** A shadow is paper under less light, and
neither convention can tell that from partial coverage. The bare-sheet frames
put a number on it: 0.002 to 0.17 g of phantom coffee, small here only because
the light was diffuse. A directional source would make this the largest term in
the budget. *Fix: keep shooting the bare sheet every session. It is the only
frame whose answer is known exactly, and it costs one exposure.*

## Reproducing this

Four stages, each reading what the one before it wrote, so re-fitting a constant
does not mean decoding raw again.

```
uv run beanometer annotate data/raw/sessions/2026-08-29-run-zero
uv run beanometer corners  data/raw/sessions/2026-08-29-run-zero
uv run beanometer measure  data/raw/sessions/2026-08-29-run-zero --overlays
uv run beanometer results  data/raw/sessions/2026-08-29-run-zero
```

The hand-placed corners are committed; the detector writes its proposals to a
separate file that is not, so the two can be compared rather than confused. On
this session the detector's median reprojection residual was 33 px against
9.3 px for hand placement, and it is the table's reflection that costs it.

Every figure here is reproducible from the committed corner file and the raw
captures. None of it is a literature value.
