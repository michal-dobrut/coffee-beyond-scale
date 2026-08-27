# Decisions
Entries are append-only, newest last.

### 2026-08-27 — Reader-facing repo, private deliberation

**Decision:** Four tracked documents drive the project: `README.md` (the premise
and the headline result), `DECISIONS.md` (this log), `CLAUDE.md` (writing and
commit conventions), and method documentation under `docs/` split three ways —
`method.md` (why mass is recoverable from a photo), `uncertainty.md` (the error
budget and interval calibration), `data.md` (capture protocol, ground truth,
evaluation split). Discussion, planning, schedule, and progress live in
`notes/` — a gitignored nested git repository — and nothing a reader consumes
ever references it.

**Why:** The repo is read by someone arriving with no context, while
deliberation is written for me; holding both in one place produced a 314-line
`DECISIONS.md` containing exactly one recorded decision, the rest being a
schedule, a shopping list, and a learning plan.

**Rejected:**
- Deliberation kept inline in the tracked documents — buried the conclusions and
  left a reader unable to separate commitments from thinking-aloud.
- Dated snapshots of each document in a `brainstorming/` directory — snapshotting
  a living document yields near-duplicate files that go stale; dating *sessions*
  instead is naturally append-only and never duplicates.
- `notes/` as plain untracked files — no history and no backup for the material
  that would be most expensive to lose.
- `design.md` as the name — "design" invites forward-looking plan prose that
  rots as the code diverges from it, where "method" invites present-tense
  description that either matches the code or is a bug.
- One combined method document — the uncertainty treatment is this project's
  actual claim to attention and gets undersold buried inside a general design
  document.

**Revisit if:** A reader-facing document needs to cite something that exists only
in `notes/` — that is the signal the split sits in the wrong place, not a licence
to cite it. Or new material keeps landing in whichever of the three `docs/` files
was open at the time, which would mean the seams do not fall where readers'
questions divide.

### 2026-08-27 — Pixel 10 Pro as the primary capture device

**Decision:** Routine sessions are shot on a Pixel 10 Pro, main lens, under the
capture protocol in `docs/data.md`. It is the primary device rather than the
only one — the set-aside evaluation group still requires a second camera body.

**Why:** It is the camera already owned, so standardising on it costs nothing.

**Revisit if:** The device cannot be held to the capture protocol — exposure
merging or per-region tone mapping that cannot be disabled, or white balance and
exposure that cannot be locked — which would break the uniform white reference
that roast estimation depends on. Or its EXIF does not carry a focal length that
the height correction can use.

### 2026-08-27 — Markers set in from the sheet edge

**Decision:** The marker border is printed inside the A4 margin with a rim of
unmarked white paper left between the outer marker row and the sheet edge, so no
marker touches or approaches the paper boundary. Corner detection against the
plain sheet remains the primary route; the markers are read independently.

**Why:** High-contrast ink adjacent to the paper boundary changes the boundary
itself — it shifts a global threshold computed over the frame, and gives
edge-linking a straighter, higher-contrast line to lock onto than paper against
table. The rim keeps the markers from altering the one edge the plain-sheet
detector exists to find, which is what lets the markers measure that detector
rather than flatter it.

**Rejected:**
- A blank sheet with no markers — pose would be assumed rather than measured,
  and the asymmetry is one-way for captured data: markers can be masked out of a
  photograph afterwards, but cannot be added to one without re-shooting.
- Markers flush to the sheet edge, maximising the marker field — puts ink
  against the paper boundary and contaminates the measurement the markers are
  there to make.
- Markers as the primary detector, plain-sheet detection dropped — the whole
  point of this project is to do it with minimal prep.

**Revisit if:** Paired frames of a blank sheet, shot in the same session under
the same lighting, show the plain-sheet detector materially worse without the
markers present — the corner-detection error then describes the marker sheet and
not a blank one. Or the bean field left inside the border is too small for the
bean count where merging begins to dominate.
