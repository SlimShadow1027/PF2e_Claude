---
description: Build or run a combat encounter
---

Follow `system/07-encounter-building.md` to build one and `system/06-encounter-runner.md` to run
it.

**Building — objective first, creatures second.** Picking creatures first produces a damage race
with flavour text.

```
python3 tools/pf2e.py encounter --party-level <N> --party-size <M> --threat moderate
python3 tools/pf2e.py encounter --party-level <N> --party-size <M> --add "ghoul:2" --add "ghast:3"
```

Read the solo warning the tool prints. The budget prices creatures by level; it does not price
turns. Four level−2 creatures and one level+2 creature cost similar XP and are completely
different fights for one character.

Give the encounter a win condition from `system/17-encounter-objectives.md` — at least half of a
campaign's fights should have one other than "everything hostile is dead" — and a morale threshold
per creature group.

Every creature needs `bestiary/<name>.md` with a `Source:` line, level, traits, full stats and a
`Tactics:` note. `validate.py` fails a file without the source.

**Running:**

```
python3 tools/state.py --campaign <slug> encounter start "<name>" --objective "<win condition>" --map <scene>
python3 tools/roll.py init --actors "kaelen:+7,ghoul-a:+5,..." --party kaelen --campaign <slug>
python3 tools/state.py --campaign <slug> encounter add ... --side ... --init N
python3 tools/state.py --campaign <slug> encounter telegraph "<how the player learns the objective>"
python3 tools/state.py --campaign <slug> encounter status
```

**Before resolving any trigger, check the party's available reactions and ask.** That is the
obligation in `system/06-encounter-runner.md`, and forgetting it is the most common way an
automated GM quietly shortchanges a player.

At the end: XP, treasure, persisting conditions, the `encounters/history.md` entry with its
`Objective:` field and an honest `Difficulty landed as:` line, `encounter end`, and a checkpoint.
