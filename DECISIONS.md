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