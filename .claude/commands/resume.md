---
description: Run the boot sequence for a campaign and pick up where we left off
argument-hint: [campaign slug]
---

Resume a campaign. Run the **boot sequence** from
`system/15-continuity-and-context-recovery.md` in order, before narrating anything.

1. `CLAUDE.md`, and the `system/` docs relevant to what is happening.
2. `campaigns/$1/CHECKPOINT.md`, `state.json` (**canonical** for every volatile number),
   `RULES_DELTAS.md`, `PLAYER_PREFS.md`, `FLAGS.md`.
3. `CANON.md`, `QUESTS.md`, `CLOCKS.md`, `npcs/ROSTER.md`, `FLAGS.md` again.
   If `CAMPAIGN.md` names a world, also load the **date-gated** view and nothing later:

```
python3 tools/world.py as-of <world> "<current in-world date>"
```

4. The last one or two files in `sessions/`.
5. The sheets of characters in play, and the bestiary entries for anything on screen. If a fight is
   live, `encounters/active.md` and:

```
python3 tools/state.py --campaign $1 encounter status
```

6. Run the validator before the first roll, not after the first hour:

```
python3 tools/validate.py --campaign $1
```

7. **Give the recap and confirm the situation before narrating anything new.** Trailer (player-known
   only) and plain facts, kept separate — `system/22-session-flow.md`. Then ask whether that is
   right, and wait.

If the last checkpoint was taken mid-combat, say out loud whose turn it is, how many actions they
have left, and whether their reaction is available, before anything else.
