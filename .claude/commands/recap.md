---
description: Summarise where we are, what is unresolved, and what was about to happen
---

Give a recap, following `system/22-session-flow.md`.

**Two parts, kept strictly apart:**

1. **The trailer** — 100 to 150 words, present tense, in the campaign's voice, built from the
   most recent file in `sessions/` rather than from the raw checkpoint, ending on the decision or
   the danger the player was facing.

   **Only what the player's characters actually know.** Nothing from `gm-private/`, nothing from
   an off-screen turn they have not encountered, nothing marked *GM-side truth* in `CANON.md`,
   nothing from a world chronicle entry dated after this campaign's current date.

2. **The plain facts** — HP, conditions with durations, resources, location, in-world date, and
   what they were about to do. Read these out of `state.json`, not out of memory:

```
python3 tools/state.py --campaign <slug> render
python3 tools/state.py --campaign <slug> encounter status
```

Then list what is unresolved, from `QUESTS.md` and `CLOCKS.md`, and **ask whether that is right
before narrating anything new.**
