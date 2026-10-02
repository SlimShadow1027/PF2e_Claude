# {{CREATURE_NAME}}

**Source:** _(see below — required)_
**System:** _(pf2e or dnd5e — must match the campaign's)_
**Level / CR:** _(a **level** in Pathfinder, a **Challenge Rating** in D&D 2024)_
**Traits:** _(PF2e: rarity, traits, size, type — D&D: size, creature type, alignment)_

Creature statistics come from published material **for this campaign's ruleset**. This file is
not written freehand.

| System | A published `Source:` reads | Homebrew reads |
|---|---|---|
| `pf2e` | `Monster Core p.NNN` or `https://2e.aonprd.com/Monsters.aspx?ID=NNN` | `Homebrew — reskin of Ghoul (Monster Core, lvl 1)`, numbers unchanged; or `Homebrew — built from the GM Core creature-building benchmarks`, tables cited row by row |
| `dnd5e` | `SRD 5.2, Monsters A–Z — <name> (CR N)`, or the book and page | `Homebrew — reskin of Bugbear Warrior (SRD 5.2, CR 1)`, numbers unchanged; or `Homebrew — <base creature> with <the change>`, which makes it a new creature and should say so |

**D&D 2024 publishes no Elite/Weak adjustment templates.** There is no open-content equivalent
of Pathfinder's, so adjusting a creature there is homebrew and the file must say so, including
what XP you are counting it as.

**Never carry a stat block between the rulesets.** A CR 5 monster and a level 5 Pathfinder
creature are not the same creature, and neither set of numbers survives the trip — see
`system/23-cross-system-worlds.md`.

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
