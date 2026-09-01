# Coffee

What the coffee contributes to the error, as against what the instrument
contributes. A figure is here because it moves a mass estimate or carries a
sign; the rest of coffee science is not.

Standing marks are the ones the instrument notes use:

| mark | meaning |
| --- | --- |
| — | consistent across independent sources |
| `[?]` | single source, or derived here; plausible, unconfirmed |
| `[!]` | sources disagree, or published figures are mutually inconsistent |
| `[measure]` | not answerable from the literature; determine on the bench |

## What moves the estimate

Ranked by how much of a dose each one shifts.

| source | size | sign | |
| --- | --- | --- | --- |
| a peaberry read as a small flat bean | 33% per bean | reads low | `[?]` |
| published roasted-bean density, study to study | ±26% | either | `[!]` |
| moisture drift of a stored lot | 3–4 points dry basis, over weeks | set by ambient humidity | `[?]` |
| roast level across its range, through density | 15% | dark reads low on a light fit | `[!]` |
| screen grade, through the area exponent | `β` anywhere in 1.0 to 1.5 | either, per lot | `[measure]` |
| CO2 degassing after roast | 1.1–1.6% of mass, once | reads high | — |
| silverskin shed in handling | a fraction of 2% of bean mass | reads high | `[?]` |
| air buoyancy against a steel-calibrated balance | 0.16% | balance reads low | — |

The last is carried only to be dismissed: it cancels between an analytical
balance and a kitchen scale, because both weigh coffee against steel.

The second prices the position that takes its constant from the literature
rather than from a bag. The spread between studies at one roast level is four
times the spread across the whole roast range within any one study, so that
position is worth tens of per cent and no imaging work recovers it.

## Mass, footprint and density are one fact

A bean of projected area `A`, height `h` and density `ρ` has mass `ρ·φ·A·h`,
where `φ` is how much of the prism `A·h` the bean fills. Under the
size-independent shape the area relation assumes, `h = ψ·√A`, and the constant
is a single product:

```
k = ρ · φ · ψ
```

`φ` and `ψ` are geometry with hard limits. A solid cannot exceed its bounding
prism, and a bean 4–5 mm tall on a 70 mm² footprint pins `ψ` near 0.5. Taking
`φ` in 0.6 to 0.9 and `ψ` in 0.42 to 0.55, a fitted `k` implying a roasted
density outside 0.40–0.80 g/cm³ is reporting a segmentation bias rather than a
bean.

It runs backwards as a check on any stated pair. A mass of 0.145 g on a 50 mm²
footprint implies 1.0–1.2 g/cm³, which is green-coffee density — and roasted
beans float.

| | Rodrigues 2003 | Sivetz 1979 | Clarke 1987 | Dutra 2001 |
| --- | --- | --- | --- | --- |
| particle, green | 1260 | 1200 | 1250 | 1284 |
| particle, light–medium | 550 | 720 | 755 | 607 |
| particle, medium–dark | 470 | 600 | — | 438 |
| bulk, green | 680 | — | 700 | 707 |
| bulk, light–medium | 314 | — | 369 | 304 |
| bulk, medium–dark | 265 | — | 289 | 250 |

kg/m³, four studies tabulated together by the first. `[!]` Within a study,
light to dark moves particle density by about 15%; between studies at one roast
level, by about 60%.

Bulk against particle puts a poured bed of whole roasted beans at a packing
fraction near 0.56, which is random loose packing for moderately elongated
particles. The crease makes a bean non-convex, which lowers packing relative to
a smooth ellipsoid and stabilises loose arrangements by interlocking.

## One bean, measured

| quantity | value | |
| --- | --- | --- |
| roasted arabica mass | 0.10–0.17 g | — |
| within-lot coefficient of variation | 10–13% | `[?]` |
| roasted arabica, length × width × thickness | 11.4 × 8.6 × 5.7 mm | `[?]` |
| the same beans green | 8.6 × 6.9 × 4.4 mm | `[?]` |
| sphericity, green | 0.63–0.70 | `[?]` |
| sphericity, roasted | 0.67–0.75 | `[?]` |
| green moisture, by ISO 6673 | 8–12.5% | — |
| roasted moisture, out of the drum | 1–3% | `[?]` |

Green moisture is capped at 12.5% by ICO Resolution 420, which names ISO 6673 —
drying at 105 °C for 16 h — as the method. Trade guidance sometimes states
9–13%, which the binding resolution does not permit. `[!]`

## Peaberry

A peaberry forms where only one of a cherry's two ovules is fertilised, so the
seed grows round instead of developing a flat face against a twin. Measured
against flat beans from the same lots: length 9.90 mm against 11.19 mm, width
7.19 against 8.56, both differences significant — and mass 0.19 g against
0.20 g, which is not.

Equal mass on 26% less footprint. That footprint predicts 0.641 of the flat
bean's mass where the truth is 0.950, so every peaberry in a frame is read
33% light.

| peaberry fraction, by count | dose reads | where |
| --- | --- | --- |
| 2% | 0.65% low | residue after shape sorting |
| 5% | 1.63% low | natural rate, unsorted |
| 10% | 3.26% low | upper end of natural occurrence |
| 100% | 32.6% low | a bag sold as peaberry |

Natural occurrence is 5–10% of a harvest `[?]` — trade consensus, with no
peer-reviewed field survey behind it. Peaberries are routinely shape-sorted out
and sold separately, so an ordinary bag sits below that rate and a peaberry bag
sits at 100%. What survives sorting is `[measure]`.

The error is therefore bimodal rather than gradual: near zero on a sorted bag,
a third on a peaberry bag, with nothing in between to warn of it. It is also
visible in the same photograph. Peaberry sphericity is 0.8–0.9 against 0.8 and
below for flat beans, and the published geometry splits on that line — flat
beans modelled as hemi-ellipsoids, peaberries as full ellipsoids, which is a
difference in `φ`. Eccentricity separates the two populations, and each takes
its own constant.

## Screen grading sets the exponent

Green coffee is graded over round holes measured in sixty-fourths of an inch:
one screen is 0.397 mm, so screen 16 is 6.35 mm and screen 18 is 7.14 mm. An
elongated bean passes a round hole on its width rather than its length. The
specialty convention is at least 90% retained on screen 16 with at most 5%
through screen 15, against a general contract tolerance of ±5%.

So width arrives truncated, length does not, and thickness is the least
variable dimension of the three. `[?]` Writing `log m = log L + log W + log T`
against `log A = log L + log W`, the regression slope is

```
β = 1 + Cov(log T, log A) / Var(log A)
```

Thickness rising as the square root of footprint puts that covariance term at
exactly 0.5 and returns 3/2. Thickness that does not track footprint at all
returns 1: beans as discs of fixed thickness, mass proportional to area. The
reported ordering of the dimensional variances points at the second.

The exponent is thus a property of how a lot was graded as much as of its
beans, and it moves between bags screened differently. It is decidable at the
precision on offer — an exponent uncertainty near 0.07 separates 1.0 from 1.5
with room — and a result near 1.0 says the remaining mass variance lives in
thickness, the one dimension a nadir photograph cannot see.

## Roast

| roast level | mass loss | single-bean volume | particle density |
| --- | --- | --- | --- |
| green | — | — | 1260 kg/m³ |
| very light, at first crack | 10–13% | +40% | — |
| light–medium, filter | 13–15% | — | 550 kg/m³ |
| medium–dark, espresso | 15–18% | +65% | 470 kg/m³ |
| dark, into second crack | 18–25% | +100% | — |

Mass loss from roaster-trade sources `[?]`; volume and density measured on 100
beans per sample at two-minute intervals. Published expansion figures of
170–300% describe poured bulk volume rather than single beans and do not belong
in this table. `[!]`

The mass-loss curve has two straight regimes with a knee where pyrolysis takes
over from drying — at 7% loss in that study, near 10% in the earlier
literature. About 85% of what leaves is water.

Expansion is not quite isotropic. Sphericity rises through the roast and
thickness gains 22–32%, so a bean rounds as well as swells. `ψ` is invariant
under pure scaling, so only the rounding moves it, upward by a few per cent,
partly offsetting the density fall. Light to dark therefore moves `k` by 12–15%
rather than the 21% that 0.70 and 0.55 g/cm³ as endpoints would imply.

## Colour

| milestone | `L*` | `a*` | `b*` |
| --- | --- | --- | --- |
| green | 59.33 | 2.43 | 21.33 |
| colour change | 62.38 | 9.62 | 30.85 |
| first crack | 29.74 | 12.56 | 18.92 |
| second crack | 19.96 | 6.41 | 6.45 |
| end of roast | 17.19 | 3.24 | 2.84 |

Ground, D65, from 663 samples over 39 roasts and three origins. Across that
dataset both chroma channels follow lightness alone:

```
a* = -14.498 + 1.341·L* - 0.015·L*²    R² = 0.934
b* = -30.221 + 2.244·L* - 0.020·L*²    R² = 0.977
```

Checked against 392 pooled points from twenty other publications at a mean
`ΔE*` of 1.19 ± 0.76, which is below the perceptual threshold. Roast colour is
one degree of freedom and `L*` is the coordinate on it, so appearance has one
number in it rather than three. Distance from the curve is not roast
information: it is a bean that is not arabica, is defective or is
decaffeinated, or a photometry chain that is wrong.

### The scales

The SCA roast tiles run 95 (very light) to 25 (very dark) in steps of ten on
the Agtron Gourmet scale. The cupping reference roast is Gourmet 63.0, and the
same document cross-calibrates it to Commercial 48.0, Colortrack 62.0 and
Probat Colorette 3b 96.0 — one point per instrument at ±1.0, with no conversion
curve beyond it. Agtron reads near-infrared diffuse reflectance rather than
visible colour, so a camera measures something correlated with it and not it.

Every one of these is defined on ground coffee in a flat bed. The colour-curve
study excluded whole-bean work from its meta-analysis, and whole-bean readings
carry about twice the deviation of ground ones because a curved surface
violates the geometry the optics assume. No literature colour value transfers
to whole beans on paper.

| pitfall | magnitude | |
| --- | --- | --- |
| grind size, one roasted material | 22 Agtron points | `[?]` |
| whole bean against ground, one sample | about 2× the deviation | — |
| drift in the first 24 h after roast | up to 3 Agtron points | `[?]` |
| surface oil past second crack | not quantified | `[!]` |

Roast analysers reject the oil-film specular component with crossed
polarisers — the same physics as a highlight thresholding as paper. Copy paper
carries optical brighteners that fluoresce under ultraviolet, so its apparent
blue depends on the illuminant's ultraviolet content: two sources of equal
correlated colour temperature can give the sheet two `b*` values while the
beans hold still. `[measure]`

## Mass is not constant

Two fluxes run in opposite directions after roast, and which one wins is set by
the humidity of the room.

CO2 leaves, and the pool is bounded. Residual CO2 is 6.3–6.7 mg/g at a light
roast, 11.0–11.5 medium and 15.4–15.6 dark, then plateaus — 0.6 to 1.6% of
mass, ever. It tracks roast degree rather than roasting temperature, so beans
brought to one colour fast and slow are indistinguishable. Whole beans release
it on a Weibull curve with a time constant of 190–335 h at 25 °C, which is
about 33 days to 90%. Grinding dumps 26–59% of what remains at once.

Water arrives, and nothing bounds it comparably. Beans leave the drum at 1–3%
moisture, far below equilibrium with room air. Whole bean, dark roast, 25 °C:

| relative humidity | equilibrium moisture |
| --- | --- |
| 33% | 2.6% dry basis |
| 58% | 6.3% dry basis |
| 81% | 16.9% dry basis |

Monolayer moisture sits at a water activity near 0.33, a figure three
independent studies converge on across whole bean and ground, light and dark.
Dark roasts are the more porous and expected to be the more hygroscopic, though
no head-to-head comparison by roast level exists. `[?]`

The two cancel near 33% relative humidity. Below it beans keep losing and
settle about 1% down; above it the moisture term is several times the whole CO2
pool and beans gain low single-digit percent over a month. A stored lot is
therefore a mass reference only to the extent that its water activity is held,
and re-weighing one a campaign later otherwise measures the storage humidity.
Saturated magnesium chloride holds 0.33 at 25 °C, which is the crossover.

Within a session none of this is visible: a bean drifts about 0.03% over two or
three hours, near 0.05 mg, under the repeatability of weighing with the draft
shield open. Beans weighed against an inert dish over one run separate static
and instrument, not coffee, and a null there is not evidence that beans hold
still.

Volatiles are a rounding error beside both. CO2 is over 80% of the gas roasting
produces, so everything aromatic together is several times smaller in mass.
Staling is sensory rather than gravimetric: panels reject coffee once headspace
volatiles fall 60% below their opening value, at 13 to 20 days.

Humidity moves the mass twice. Moisture plasticises the cell walls, so
degassing time constants fall from 294 h at 0% relative humidity to 45 h at
81%. And roasted coffee at 2–3% moisture sits at the dry end where
triboelectric charging is worst, which is where weighing repeatability goes.

## What else is in the bag

**Quakers.** Unripe beans that never brown. Specialty grade permits none,
premium at most three. They are pale, denser and less expanded, which makes
them the lowest-contrast object in a frame against white paper — so the beans
most likely to be dropped by a colour threshold are also the ones whose
appearance carries the most density information. Colour sorters miss them
because the difference only appears after roasting.

**Silverskin.** Four to five per cent of a green bean; about 2% of a roasted
one remains in the crease after the rest leaves as chaff at the roaster. What
sheds under handling is a fraction of that, and a tenth of it is 0.3 mg against
a 145 mg bean — the order of the weighing repeatability it would have to be
distinguished from. Loose chaff on the sheet is coffee-coloured, small enough
to fall under a speck threshold individually, and electrostatically mobile.

**Robusta.** 6.5–8.5 mm long, smaller and rounder than arabica, denser, with a
straighter crease. A blend is a bimodal population, which the self-calibrating
position assumes away.

**Large-bean varieties.** Maragogipe measures 11.69 × 7.25 mm and is the parent
of Pacamara and Maracaturra; Liberica runs 12–15 mm. No mass figure for any of
them is in the accessible literature. `[measure]`

**Decaffeinated.** Roasts faster and colours differently, so the
appearance-to-roast mapping does not transfer. It was excluded from the study
the colour curve comes from.

**Stratification.** Beans sort in a bag under transport and handling, large
ones upward. A scoop off the top is size-biased and its mean bean mass is not
the bag's, so a per-bag constant needs the bag poured out and split.

## In bulk

Poured whole roasted beans sit at 300–410 kg/m³ against a particle density of
470–550. Ground coffee densifies 21–31% from poured to tapped; whole beans,
already near their loosest stable arrangement, densify far less. The angle of
repose is 20–34°, free-flowing and at the low end of the stored grains.

That is what makes reading a heap look tempting, and the published sensitivity
is what rules it out.

| single-image heap volume, error source | sensitivity |
| --- | --- |
| angle-of-repose error | 3.9% of volume per degree |
| contour segmentation error | amplified 1.6× into volume |
| photogrammetric stockpiles, best case | ±5% |
| small piles | 7–23% |

The repose angle of coffee moves with roast level and with moisture, by up to
15° across a full moisture swing, so it would have to be known to a quarter of
a degree on a material that does not hold it. Spreading the beans into one
layer is not a convenience of a protocol; it is the only geometry in which the
target is reachable. The nearest published analogue that works is portion
estimation on rice, at about 5% with a depth camera, which is above the floor a
spread layer already reaches.

## Open on the beans

- `[measure]` Bean height, per bean. It closes `k = ρφψ` and it is where the
  residual scatter lives. A mirror at 45° in the frame yields a top and a side
  view in one exposure, and the rest-pose distribution with them.
- `[measure]` The exponent, per grading regime. Whether `β` lands at 3/2 or
  nearer 1 is a statement about how a lot was screened, and it does not carry
  to a bag graded differently.
- `[measure]` Rest pose from the crease. A flat bean lying flat-face-up shows
  its crease and flat-face-down shows a smooth dome, so the fraction of creases
  visible in a frame is the rest-pose distribution — which sets how far above
  the paper a silhouette forms.
- `[measure]` Whether `k` survives moisture. Beans taking up water gain mass
  and volume together. Photographing the same beans that are re-weighed gives
  the change in mass against the change in `A^(3/2)` directly, and says whether
  humidity moves the constant or only the reference.
- `[measure]` Whole-bean `L*` against roast level. Nothing in the literature is
  on whole beans, so the appearance-to-density relation cannot be imported at
  any strength.
- `[measure]` Optical brightener response of the sheet, under two illuminants
  of equal correlated colour temperature and different ultraviolet content.
- `[measure]` Peaberry residue in an ordinary bag, which is worth between
  nothing and 1.6% of the answer.

## Sources

Rodrigues, Borges, Franca, Oliveira and Corrêa (2003), "Evaluation of Physical
Properties of Coffee during Roasting", CIGR Journal V, FP 03 004, for density
and roast physics; it tabulates its own measurements against Sivetz and
Desrosier (1979), Clarke and Macrae (1987) and Dutra et al. (2001), and the
four-way disagreement above is from that table.

Fu et al. (2023), BMC Genomic Data 24:12, for peaberry dimensions and mass
measured on the same lots. Huamaní-Meléndez et al. (2018), Journal of Food
Process Engineering, for the hemi-ellipsoid and full-ellipsoid split at
sphericity 0.8.

Anokye-Bempah, Styczynski, Ristenpart and Donis-González (2025), "A universal
color curve for roasted arabica coffee", Scientific Reports 15:24192, for the
milestone colours and the chroma regressions. SCAA Standards Committee, "Roast
Level for Cupping" (2015), for the cross-instrument calibration point.

Wang (2014), "Understanding the Formation of CO2 and Its Degassing Behaviours
in Coffee", PhD thesis, University of Guelph, for whole-bean residual CO2,
degassing kinetics and the whole-bean sorption isotherm. Baptestini et al.
(2017), Acta Scientiarum Agronomy 39:273, and Anese, Manzocco and Nicoli
(2006), Journal of Agricultural and Food Chemistry 54:5571, for ground-coffee
sorption parameters and the staling threshold.

Lorbeer et al. (2022), Molecules 27:6839, for silverskin. ICO Resolution 420
(2004) and ISO 6673 for green moisture; FAO Annex 7 for screen-grade
boundaries. Pile-volume sensitivity from single-image angle-of-repose
reconstruction validated on sand and silica, arXiv:2509.13890 and
arXiv:2505.17896; repose angles for whole and ground coffee from the two-part
storage study in Revista Brasileira de Engenharia Agrícola e Ambiental.

Figures without a citation are derived here from these, and carry `[?]` where
that derivation is their only support.
