---
description: Write a checkpoint now — commits and regenerates the dashboard
---

Take a checkpoint of the active campaign, following `system/05-checkpoint-protocol.md`.

1. If you do not know which campaign is active, ask — or infer it from the only folder in
   `campaigns/`.
2. Set the prose notes first, so the snapshot is usable by a session that remembers nothing:

```
python3 tools/state.py --campaign <slug> note situation "<3–6 sentences: where we are>"
python3 tools/state.py --campaign <slug> note present "<who is here>"
python3 tools/state.py --campaign <slug> note pending "<what is about to happen>"
python3 tools/state.py --campaign <slug> note next_beats "<what you would pick up from>"
```

3. Then:

```
python3 tools/state.py --campaign <slug> checkpoint "<a short name for this moment>"
```

That renders `CHECKPOINT.md`, writes the immutable snapshot, regenerates `dashboard.html`, and
makes the git commit. Report the checkpoint number and the commit sha. **If the commit fails, say
so — never skip it silently.**

If a fight is live, confirm the tracker is complete first (`encounter status`): initiative order,
whose turn, actions spent, MAP step, reactions, HP, conditions, positions.
