---
description: Regenerate the campaign dashboard and point at it
---

```
python3 tools/dashboard.py --campaign <slug>
```

Then give the player the path — `campaigns/<slug>/dashboard.html` — and tell them it opens from
`file://` with no network.

It is **read-only**. Every edit goes through `tools/state.py`; `state.json` stays the single
source of truth.

It **respects the campaign's transparency mode**: outside `glass`, enemy hit points show as
wounded descriptors rather than numbers. If the player wants numbers, change the mode rather than
reading them off somewhere else:

```
python3 tools/state.py --campaign <slug> transparency glass
python3 tools/dashboard.py --campaign <slug>
```

It is regenerated automatically at every checkpoint, and carries the timestamp and checkpoint
number it was generated from, so a stale file is obvious.
