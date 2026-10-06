---
description: Print a character's sheet
argument-hint: [character name]
---

Print the sheet for **$1** (or ask which, if there is more than one and no name was given).

Two sources, and say which each number came from:

- **The built character** — `campaigns/<slug>/characters/<name>.md`: ancestry, heritage,
  background, class, key ability, feats taken, proficiency ranks, spells known, reactions,
  backstory, ties.
- **The volatile numbers** — `state.json`: current HP and temp HP, conditions with durations,
  slots used, items with charges — plus whichever of these the ruleset has:
  **Pathfinder** dying/wounded/doomed, Hero Points, Focus Points;
  **D&D 2024** death saves, Hit Dice, Exhaustion, Heroic Inspiration, Concentration, attunement.
  **D&D 4e** four defences, healing surges, Second Wind, action points, milestones, encounter
  and daily powers, death-save failures, and how far below zero the hit points have fallen.

```
python3 tools/state.py --campaign <slug> get pcs.<key>
```

Include the **reactions** table prominently — those are what the GM has to offer before resolving
a trigger (`system/06-encounter-runner.md`).

If a derived number on the sheet disagrees with the formula, say so and recompute it rather than
reprinting it. `system/11-leveling-up.md` has the formulas.
