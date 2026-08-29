# Instruments

Fixed parameters of the balance and the camera, and the geometry that follows
from them. Values here are recorded so they are not looked up twice.

Every figure carries its standing:

| mark | meaning |
| --- | --- |
| — | manufacturer figure, consistent across sources |
| `[?]` | single source, or derived here; plausible, unconfirmed |
| `[!]` | sources disagree, or published figures are mutually inconsistent |
| `[measure]` | not answerable from documentation; determine on the instrument |

A `[?]` or `[!]` figure is safe to compute with and unsafe to defend.

## Balance — Mettler Toledo MS204TS/M00

Analytical balance, NewClassic MS-TS line, touchscreen. The line is
discontinued; documentation remains available from the manufacturer.

| quantity | value | |
| --- | --- | --- |
| `capacity_g` | 220 | |
| `readability_mg` | 0.1 | |
| `repeatability_sd_mg` | 0.1 | `[?]` |
| `linearity_mg` | ±0.2 | `[?]` |
| `settling_time_s` | ~3 | `[?]` |
| `pan_diameter_mm` | 90 | `[?]` |
| internal calibration | yes | `[?]` |

The `/M00` suffix is the OIML-approved, legal-for-trade variant, as against the
plain `/00` laboratory version. Approved firmware can differ in zeroing and tare
behaviour, and an approved balance carries a verification interval `e` coarser
than its readability `d` — plausibly `e = 1 mg` here `[?]`. Whether the
interface returns the full 0.1 mg or a value rounded to `e` is `[measure]`, and
it decides whether the ground truth is quantised at 0.1 mg or at 1 mg.

### Interfaces

RS232C is fitted as standard on every MS-TS. The touchscreen models add USB-B
for a host, USB-A for a memory stick, and LAN. Bluetooth and WLAN are options.

Three routes off the instrument:

- **MT-SICS over RS232 or USB-B.** The manufacturer's command set, common to
  their laboratory balances.
- **EasyDirect.** PC software collecting from up to 10 balances into an SQL
  database.
- **USB stick.** CSV or XML written by the balance itself.

### MT-SICS commands

Level 0 and 1, common to the range `[?]` for this model specifically:

| command | effect |
| --- | --- |
| `S` | send the next stable weight |
| `SI` | send immediately, stable or not |
| `SIR` | send immediately and repeat, a continuous stream |
| `Z` | zero |
| `T` | tare |
| `I2` | query balance model and capacity |

A stable reply takes the form `S S      14.5003 g`; the second field is `S` for
stable, `D` for dynamic. Serial defaults are plausibly 9600 baud, 8 data bits,
no parity, 1 stop bit, Xon/Xoff `[?]` — the balance's own interface menu is
authoritative and reading it is `[measure]`.

The MT-SICS reference manual for Excellence balances documents the full set:
`mt.com/dam/product_organizations/laboratory_weighing/WEIGHING_SOLUTIONS/PRODUCTS/MT-SICS/MANUALS/en/Excellence-SICS-BA-en-11780711D.pdf`

### What this readability means

At 0.1 mg, quantisation of a 14.5 g dose is 0.0007%, and quantisation of a
145 mg bean is 0.07%. Both sit far below every other term in the error budget,
so ground-truth quantisation is negligible and is not carried as a term.

The practical floor is instead repeatability under real handling — dish in,
dish out, draft shield opened — with static on dry roasted coffee as the
suspected dominant contributor. That figure is `[measure]`; the drift-control
design in the capture protocol yields it.

## Camera — Google Pixel 10 Pro

Two of the three rear cameras are usable here. The ultrawide is not: heavy
distortion and its own intrinsics.

| | main (wide) | telephoto (periscope) |
| --- | --- | --- |
| `resolution_mp` | 50 | 48 |
| sensor format | 1/1.31" | 1/2.55" |
| `pixel_pitch_um` | 1.2 | 0.7 `[?]` |
| `aperture_f` | 1.68 | 2.8 |
| `f_equiv_mm` | 24.4 `[?]` | 113 or 128 `[!]` |
| `f_actual_mm` | 6.90 | 16–18 `[?]` |
| stabilisation | OIS | OIS |
| autofocus | dual-pixel PDAF + laser | dual-pixel PDAF |
| `focus_range_mm` | 100–∞ | ~300–∞ `[?]` |
| quad-Bayer binning | yes, to 12.5 MP | yes `[?]` |
| full-resolution capture | yes, Hi-Res setting | yes |

The manufacturer publishes neither actual focal length. The main camera's is
taken from what its own firmware writes into every frame; the telephoto's is
derived from sensor geometry and the equivalent figure and inherits that
figure's uncertainty. The sensor and lens part numbers are not disclosed, and
vendor claims about them are uncorroborated.

### Disagreements to be aware of

**Telephoto equivalent focal length.** GSMArena gives 113 mm, DXOMARK gives
128 mm. Everything geometric downstream scales with this, so it is worth
settling by calibration rather than by citation — the marker board recovers it
directly and that supersedes both.

**Telephoto sensor geometry is internally inconsistent.** 48 MP at 0.7 µm on
4:3 implies 8000 × 6000 px and a 7.00 mm diagonal, but the 1/2.55" designation
implies 6.27 mm. Either the pitch is nearer 0.63 µm or the sensor is larger
than stated. The 12% gap propagates into `f_actual_mm` and therefore into any
height correction that uses it. The main camera has no such problem: 50 MP at
1.2 µm gives a 12.24 mm diagonal against 12.21 mm implied by 1/1.31".

**Main focal length.** The 24 mm and 25 mm figures are two roundings of one
lens rather than a disagreement about it. The camera reports an actual focal
length of 6.90 mm, which against the 12.24 mm sensor diagonal above gives a
crop factor of 3.53 and an equivalent of 24.4 mm; the integer EXIF field renders
that as 24, and a 25 mm citation implies 7.08 mm actual. The geometry below
uses 24.4 mm. Calibration against the board still supersedes it.

**Main aperture** is not in dispute either. The JPEG reports f/1.68 and the
DNG f/1.7 for the same exposure, which is one lens written at two
precisions.

### Capture settings

- Main or telephoto only.
- Exposure merging off. Per-region tone mapping destroys the uniform white
  reference that roast estimation depends on.
- White balance and exposure locked where the camera allows it.
- No cropping, no auto-enhancement.
- Full-resolution mode rather than the binned default.
- Raw alongside JPEG where available.
- Transfer by cable. Messaging apps and some cloud syncs recompress and strip
  EXIF, and the focal length the height correction needs does not come back.

Two behaviours constrain use of the telephoto. Between 1× and 5× the phone
digitally crops the main sensor rather than engaging the periscope module, so
genuine telephoto capture requires 5×. And raw capture has historically been
restricted to the main sensor in third-party applications on this manufacturer's
phones; whether that still holds is `[measure]`, and if it does, the telephoto
cannot serve any role that depends on linear sensor data.

### Raw and JPEG are not the same frame

A raw and JPEG pair shares a capture but not a coordinate system, so a position
measured in one does not carry to the other.

- **Orientation.** The DNG holds the sensor-native landscape plane and records
  the rotation in its orientation tag. The JPEG arrives already rotated and
  tagged upright. The pair therefore disagrees whenever the phone was not held
  in landscape.
- **Dimensions.** The raw plane, the DNG's default crop and the JPEG are three
  different sizes, and the ratio between the last two is not the same on both
  axes, so no single scale factor relates them.
- **Timestamps.** `DateTimeOriginal` is written to whole seconds and the two
  containers round it independently, so a pair can disagree by a second. The
  filename stem is the reliable join.

Exposure merging leaves the raw usable even though the capture settings above
exclude it. The merged DNG is still linear, carrying black and white levels, a
per-shot noise profile, and the brightness push recorded as `BaselineExposure`
rather than applied to the data. Exposure time is identical across the pair and
only the reported sensitivity differs, by that push. What merging damages is
the JPEG, whose per-region tone mapping is the reason for the exclusion.

White balance is recorded as `AsShotWhiteXY`, the chromaticity of the estimated
illuminant, where the specification's more usual choice is `AsShotNeutral`.
A reader expecting the latter finds nothing.

## Geometry that follows

For a board of width `board_mm` filling the frame's long side, working distance
follows from the equivalent focal length alone:

```
distance_mm = board_mm * f_equiv_mm / 36
px_per_mm   = pixels_long_side / board_mm
```

| board | camera | `distance_mm` | `px_per_mm` |
| --- | --- | --- | --- |
| A4, 297 mm | main | 201 | 27.5 |
| A4, 297 mm | tele | 932 | 26.9 |
| 150 mm | main | 102 | 54.4 |
| 150 mm | tele | 471 | 53.3 |

Two of these are impractical. The main camera on a 150 mm board sits at its
minimum focus distance with no margin, and its depth of field there is smaller
than a bean is tall. Small boards belong to the telephoto.

### Corner obliquity

With the board filling the frame, the angle between the optical axis and the
ray to the board's corner depends on nothing but the equivalent focal length —
board size and sensor size both cancel:

```
theta_corner_deg = atan(22.5 / f_equiv_mm)
```

| `f_equiv_mm` | `theta_corner_deg` |
| --- | --- |
| 24.4 | 42.7 |
| 113 | 11.3 |
| 128 | 10.0 |

This is the angular spread across a single frame, distinct from camera tilt,
which is global and recovered from the board. It matters because a bean's
projected area shrinks with viewing angle, so corner beans and centre beans are
not directly comparable without correction — and the larger the correction, the
more a shape-model error is amplified. The magnitude of that effect is a
property of bean shape and is recorded with the bean geometry.

### Depth of field

With circle of confusion `c` set to two pixels, a strict criterion:

```
dof_mm = 2 * N * c * (distance_mm / f_actual_mm)^2
```

| board | camera | `dof_mm` `[?]` |
| --- | --- | --- |
| A4 | main | 6.9 |
| A4 | tele | 22 |
| 150 mm | main | 1.8 |
| 150 mm | tele | 5.6 |

All are derived through `f_actual_mm`, so the telephoto rows carry that
parameter's uncertainty. Beans stand 4–5 mm tall, which the two tightest rows do
not clear. Depth of field also collapses under oblique views of a large board:
an A4 sheet at 45° spans 210 mm in depth, an order of magnitude beyond any row
here, which is why multi-angle work needs a small central patch rather than the
full sheet.

Depth of field does not improve with a larger sensor at equal framing. It scales
as `N * c`, and a larger format needs a proportionally smaller aperture for the
same pixel-level sharpness, which cancels the gain exactly.

### Diffraction

Airy disk diameter at 550 nm:

```
airy_um = 2.44 * 0.55 * N
```

| camera | `airy_um` | in pixels |
| --- | --- | --- |
| main, f/1.68 | 2.25 | 1.9 |
| tele, f/2.8 | 3.76 | 5.4 `[?]` |

The main camera is close to matched: its Airy disk is about two pixels, so the
pixel grid and the optics are of comparable sharpness. The telephoto is
diffraction-limited by a wide margin, and much of its nominal 48 MP is empty
resolution. Symmetric blur widens an edge without displacing it, so this costs
precision rather than accuracy — provided edges are estimated sub-pixel and not
thresholded.

Nominal resolution is not real resolution on either camera, given quad-Bayer
demosaicing on top of diffraction. The slanted-edge method of ISO 12233 measures
it, and the marker board is a suitable target. That measurement is `[measure]`
and it feeds every area estimate.

## Open on the instruments

- `[measure]` Repeatability of a single bean weighing under real handling.
- `[measure]` Whether the approved balance returns 0.1 mg or a value rounded to
  its verification interval.
- `[measure]` The balance's actual serial settings.
- `[measure]` Whether raw capture is available from the telephoto.
- `[measure]` Real resolution of both cameras by slanted edge.
- `[measure]` The telephoto's equivalent focal length, by calibration against
  the board, which settles the 113/128 mm disagreement and its derived actual
  focal length with it. The main camera's is fixed to a rounding by its own
  firmware, and calibration would still supersede that.

## Sources

Manufacturer product pages and the MT-SICS reference manual for the balance;
GSMArena and DXOMARK for the camera, which is where the disagreements noted
above originate. Figures attributed to firmware are read from the EXIF the
phone writes into full-resolution raw and JPEG. The manufacturer does not publish actual focal lengths, sensor
part numbers, or pixel dimensions for either camera.
