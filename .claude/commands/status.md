---
description: HP, conditions, resources, gold, current scene — no narration
---

Print the current state of the active campaign. **From `state.json`, not from memory of the last
few exchanges.**

```
python3 tools/state.py --campaign <slug> render
```

then read out of `CHECKPOINT.md`:

- Each character's HP (current / max, plus temp), AC, saves, Perception.
- **Dying, wounded and doomed first**, if any are non-zero.
- Conditions with their values and remaining durations.
- Hero Points, Focus Points and whether Refocus is available, spell slots by rank.
- Consumables with counts, ammunition, item charges.
- The purse, and Bulk against the limits.
- Location and in-world date and time.
- If a fight is live: round, whose turn, actions remaining, MAP step, reaction availability.

No narration. No fiction. This is the command the player uses when they want the numbers.

If `CHECKPOINT.md` and `state.json` disagree, `state.json` wins — re-render and say you did.
