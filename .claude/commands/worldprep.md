---
description: Run one off-screen world-prep turn now
---

Run one off-screen turn, following `system/18-between-session-prep.md` in full.

**First, the concurrency guard. Both of these, before anything else:**

```
python3 tools/state.py --campaign <slug> get session_in_progress
git status --porcelain -- campaigns/<slug>
```

If `session_in_progress` is `true`, or `git status` prints anything at all, **stop**. Change
nothing, say why, and end. Do not work around it.

Also check `PLAYER_PREFS.md`: if off-screen turns are switched off there, stop and say so.

Then the pass — clocks, factions, roster, prep file, canon, validate, commit. Honour the
`world_pace` and the per-pass cap in `PLAYER_PREFS.md`.

**The hard limits are absolute:**

- **Never touch player state.** No PC or ally HP, gold, inventory, XP, level, conditions or
  position. **Prove it** with a before-and-after diff of `state.py get pcs` and
  `state.py get party`, and show the (empty) diff.
- **Never resolve anything the player would have had a say in.**
- **Never advance in-world time.** Do not call `advance-time`.
- **Never write anything under `worlds/`.**
- **Never contradict `CANON.md`**, and never edit an entry — append only.
- **Never kill a named NPC the player has met** — leave it as a proposal in the prep file.
- **One bounded pass.** Do not write the next three sessions.

Roll for anything uncertain with the real tool, tagged `offscreen`. Never write a number you did
not roll.

Finish by showing the player the **world pulse** only: one spoiler-free paragraph of what they
could plausibly have heard through rumour. Everything else stays in
`campaigns/<slug>/gm-private/prep/`.
