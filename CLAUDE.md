# coffee-beyond-scale

Estimate the mass of coffee beans from a single photo, with calibrated
uncertainty. Python 3.12, uv, `src/` layout.

## Two audiences, two places

- **The repo** (tracked) is for a reader arriving with no context: what the
  project does, how the method works, what was decided and why.
- **`notes/`** (gitignored, its own private git repo) is for me: discussion,
  session logs, plans, progress, dead ends. `/dump` writes to it, and
  `notes/plan.md` holds the schedule and learning plan.

**Invariant: nothing a reader consumes — README, `docs/`, source — ever
mentions `notes/`.** Tooling config is exempt; it is not part of the story
the repo tells. Such a file may cite another tracked file, by concept — never
by section number, which rots on the next edit to that document.

Documentation lives in `docs/`, split by what outlives a single experiment.
The root holds `method.md` (why mass is recoverable from a photo, and the
vocabulary for what a measurement is worth) and `records.md` (what is kept,
what is committed). `docs/knowledge/` holds background on instruments and the
surrounding field.

`docs/experiments/` holds one directory per measurement campaign, each owning
its own protocol, bench, analysis and error budget, indexed in dependency
order. A campaign is named for what it is, never numbered.

When a topic concludes, remind me to run `/dump` before the conversation gets
long enough to be compacted.

## Organise by what a thing is, not by when it was done

Sequence is fine where the sequence belongs to the thing: the steps of a
protocol, the stages of a derivation, anything a reader has to follow in order.
Numbering those is the content, not a schedule leaking in.

The schedule is what stays out. No "week 1", "phase 2", "next sprint", "for
now" in tracked files — not in filenames, headings, docstrings, comments, or
TODOs. A reader in month six does not know what week 1 was and cannot tell
whether it is still week 1. Campaigns and directories are named for what they
are rather than numbered, because their order is a dependency, and dependencies
get reordered.

Dates are narrower still. One that records when something happened is a fact
and keeps: a roast date, a session, a report. One that stands in for
the current state of something rots as soon as the state moves — write the
state instead.

## Decisions live in the document they affect

There is no decision log. A choice and its reason belong in the document that
describes the thing chosen — a campaign's bench, `method.md`, `records.md`,
this file — written as what is true now, not as what was settled when.

Keep a reason only where a reader needs it to understand the arrangement in
front of them, and keep it to a sentence. The alternatives that lost are
deliberation; they belong in the session log.

When something is decided again, edit the document. Do not annotate it with
what it used to say — the history holds that.

## Commits

Conventional Commits. One coherent change per commit — a unit of reasoning, not
a unit of time:

    <type>(<scope>): <subject>

    <why, wrapped at 72 columns. The diff already shows what.>

- Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`.
- Scope: lowercase kebab-case component (`geometry`, `naive`, `records`).
  Omit it rather than invent one.
- Subject: imperative mood — it completes "applying this commit will ___".
  Lowercase, no trailing period, under ~50 characters.
- Never `wip`, `update`, `fixes`, or a bare filename.
- A commit that changes behaviour and a commit that writes down why are two
  commits.
- Source changes land one per commit. Documentation edits may be grouped when
  they land together, so the log is not filled with four-line diffs — the rule
  above still holds across that boundary.

## Writing style in tracked files

Explain the thing, not the process of arriving at it. State a limitation
directly rather than arguing with an imagined critic ("on purpose, this file
contains no…"). Prefer the shortest version that a reader could not have
inferred from the code or the surrounding text.

## Source code

Docstrings are plain prose — no `Parameters` or `Returns` blocks. The
annotation carries the type; the docstring carries what the annotation cannot:
array shape, units, coordinate frame, ordering. `np.ndarray` says nothing on
its own, so `corners_px` needs "(4, 2), (x, y), clockwise from top-left".

Units belong in identifiers: `mass_g`, `area_mm2`, `PX_PER_MM`. A unit error
should read as a name mismatch.

`TODO:` bare — no owner, no date, no parenthetical tag.

## Not settled — ask, do not invent

Nothing is open right now. If work needs a convention this file does not state,
propose one and wait for an answer. Do not establish it by writing code that
assumes it.
