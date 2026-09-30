---
description: Close the session — log, canon, quests, clocks, flags, fairness, checkpoint, teaser
---

Close the session, following `system/22-session-flow.md`, in this order:

1. **Finish or safely suspend the current beat.** If mid-combat, reach the end of the round if that
   is close, then checkpoint — the tracker restores exactly, so stopping mid-fight is fine. Do not
   rush a resolution to make the ending tidy.

2. **Write the prose recap** to `campaigns/<slug>/sessions/NNN-<slug>.md`, from
   `templates/sessions/_SESSION_TEMPLATE.md`. Written for a future session that remembers nothing.
   The single most useful line in it is **what the player said they wanted to do next** — in their
   words.

3. **Append everything newly established to `CANON.md`**, marking anything GM-side as *GM-side
   truth*.

4. **Update quests, clocks and flag statuses.**

```
python3 tools/state.py --campaign <slug> quest set "<quest>" active --lead "<next concrete lead>"
python3 tools/state.py --campaign <slug> clock advance "<clock>" 1
```

5. **Append the one-line dice-fairness summary** to the session log:

```
python3 tools/analyze.py --campaign <slug> --one-line
```

If the numbers look off, say so out loud as well as in the file.

6. **Close the session and checkpoint** (which commits and regenerates the dashboard):

```
python3 tools/state.py --campaign <slug> session end
python3 tools/state.py --campaign <slug> checkpoint "session <N>: <short name>"
```

7. **A "next time on…" teaser** — one or two sentences. A teaser, not a plan, and nothing the
   player's characters do not know.
