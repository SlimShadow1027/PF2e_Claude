# {{CREATURE_NAME}}

**Source:** _(Monster Core p.NNN — or `https://2e.aonprd.com/Monsters.aspx?ID=NNN`)_
**Level:** _(N)_
**Traits:** _(rarity, alignment-ish traits, size, type)_

Creature statistics come from published Pathfinder 2e Remaster material. This file is not
written freehand. If this is homebrew, say so on the line above in one of these two shapes:

- `Homebrew — reskin of Ghoul (Monster Core, lvl 1)` — name, description and flavour changed;
  **numbers unchanged**.
- `Homebrew — built from the GM Core creature-building benchmarks`, with the benchmark tables
  cited row by row. Changing numbers makes it a new creature, not a reskin.

`tools/validate.py` fails this file if the `Source:` line is missing.

## Statistics

- **Perception:** _(+N; senses)_
- **Languages:**
- **Skills:**
- **Attributes:** Str _, Dex _, Con _, Int _, Wis _, Cha _
- **Items:**

- **AC:** _ ; **Fort** +_, **Ref** +_, **Will** +_
- **HP:** _ ; **Immunities / Weaknesses / Resistances:**
- **Speed:**

### Defensive abilities

### Offence

| Action | Attack | Damage | Traits |
|---|---|---|---|
| ◆ | +_ | | |

MAP applies normally unless a trait says otherwise: -5 / -10, or -4 / -8 agile.

### Spells / special abilities

## Tactics

Taken from the published entry where one exists; invented here only where it does not, and
said so.

- **What it wants:**
- **What it does first:**
- **Who it targets, and how cleverly:** _(an unintelligent creature does not focus-fire
  optimally; a trained soldier does. Say which this is.)_
- **When it flees:** _(a morale threshold — e.g. "at or below a third of HP, or when its
  leader dies")_
- **Can it be talked down, bribed or intimidated:**

## XP at each party level

`python3 tools/pf2e.py encounter --party-level N --party-size M --add "{{CREATURE_NAME}}:LEVEL"`

## Adjustments in use

| Adjustment | Applied? | Effect |
|---|---|---|
| Weak | no | -2 to most numbers, HP down by level band |
| Elite | no | +2 to most numbers, HP up by level band |

The HP column of the Elite/Weak table is marked `⚠ UNVERIFIED` in `tools/pf2e.py` — check it
before leaning on it.

## Appearances

| Session | Where | Outcome |
|---|---|---|
| | | |
