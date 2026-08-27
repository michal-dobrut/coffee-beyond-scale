---
description: Draft a DECISIONS.md entry, get approval, append it
---

Draft one decision-log entry about: $ARGUMENTS

## Where the content may come from

1. What we actually discussed in this conversation.
2. What I tell you when you ask.

Nothing else. If the conversation does not contain the substance of a field —
**Rejected** above all — do not supply a plausible-sounding one. Fabricated
deliberation is worse than a missing field: this file is worth having only
because it is an honest record, and it is the part of the repo a reader studies
most closely. Ask me, or omit the field and say that you omitted it.

If we have not discussed $ARGUMENTS at all, say so and ask what was decided. Do
not reconstruct an entry from general knowledge of what people usually choose.

## Check for a prior entry

Grep `DECISIONS.md` for an earlier entry on the same subject. If one exists and
this decision changes it, add to the draft:

    **Supersedes:** YYYY-MM-DD — <that entry's title>

Never edit or delete the earlier entry. The file is append-only; a reversal is
recorded, not erased.

## Shape of the entry

    ### <today's date, YYYY-MM-DD> — <short title>
    **Decision:** what was chosen.
    **Why:** the reason, in one or two sentences.
    **Rejected:** the alternatives, each with the reason it lost.
    **Revisit if:** the measurement or event that would reopen this.

State the choice, not the search for it. No hedging — if the decision is
provisional, that belongs in **Revisit if**, phrased as the trigger that would
reopen it, not as vagueness in **Decision**.

## Then

Print the draft in full, then ask with AskUserQuestion:

- **Append** — write it to `DECISIONS.md`, no commit.
- **Append and commit** — write it, then commit `DECISIONS.md` alone as
  `docs(decisions): record <short title>`.
- **Revise** — I will say what to change.

Append at the end of the file, newest last.

Touch no other file.
