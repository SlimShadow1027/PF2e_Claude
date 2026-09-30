---
description: Run the level-up checklist and re-derive every number
---

Level a character, following `system/11-leveling-up.md` in full.

Work every row of the checklist, and **say "nothing at this level" out loud** for the ones that do
not apply — a skipped row is how a missing feat happens.

Then the step that makes the rest worth doing: **re-derive every derived number from scratch from
the build, do not adjust the old ones**, and present the diff as a table with old, new, and where
the change came from.

**Any row where the recomputed number disagrees with the sheet is a bug that was already there.**
Say so plainly, correct it, and record it in the character file's level-up history. Do not quietly
adopt the new number.

Also check the item-bonus curve for the new level:

```
python3 tools/pf2e.py tables item-bonuses
python3 tools/pf2e.py treasure --level <new level> --party-size <N>
```

A character behind that curve is a treasure-pacing problem (`system/09-loot-and-economy.md`), not
a character problem — fix it in the next hoard, not at the level-up.

Finish with:

```
python3 tools/validate.py --campaign <slug>
python3 tools/state.py --campaign <slug> level set <N>
python3 tools/state.py --campaign <slug> checkpoint "level <N>"
```

This is a natural pause, so also offer the difficulty check-in from
`system/03-difficulty-and-solo-levers.md` and, at an arc boundary, the flag report from
`system/20-player-flags.md`.
