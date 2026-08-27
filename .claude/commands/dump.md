---
description: Append a settled topic to today's notes log
---

Append a record of the topic we just finished to `notes/log/`.

Topic slug: $ARGUMENTS — if empty, derive a short kebab-case slug from what we
actually discussed.

File: `notes/log/<YYYY-MM-DD>-<slug>.md`, today's date. Create it if absent,
append if it exists. Never rewrite or reflow content already in the file.

Append one section:

    ## <topic>
    **Asked:** what I wanted to know.
    **Landed on:** the conclusion.
    **Rejected:** the alternatives, each with the reason it lost.
    **Open:** what is still unresolved.

Write it from what was actually said in this conversation. Keep my reasoning
and my objections, not only the conclusions — this file exists to hold the
discussion that the repo deliberately omits, so a bare summary defeats it.
Quote me where the wording carried the point.

Then commit in the notes repo: `git -C notes add -A && git -C notes commit -m "<slug>"`.
