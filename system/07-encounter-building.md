# 07 — Encounter building

Every table here is generated from `tools/pf2e.py`, so this document and the tool cannot
disagree. Run `python3 tools/pf2e.py sources` for the provenance of each.

```
python3 tools/pf2e.py encounter --party-level 3 --party-size 1 --threat moderate
python3 tools/pf2e.py encounter --party-level 3 --party-size 1 --add "ghoul:2" --add "ghast:3"
python3 tools/pf2e.py encounter --party-level 5 --party-size 1 --hazard "rune trap:4 complex"
```

---

## XP budget by threat level and party size

The published budget is for a four-character party; each character above or below four adjusts
it by the per-character column. The tool computes `party size × 20 XP` and applies the
multiplier, which reproduces both.

| Party size | Trivial | Low | Moderate | Severe | Extreme |
|---|---|---|---|---|---|
| 1 | 10 | 15 | 20 | 30 | 40 |
| 2 | 20 | 30 | 40 | 60 | 80 |
| 3 | 30 | 45 | 60 | 90 | 120 |
| 4 | 40 | 60 | 80 | 120 | 160 |
| 5 | 50 | 75 | 100 | 150 | 200 |
| 6 | 60 | 90 | 120 | 180 | 240 |

Per-character adjustment: 10 / 15 / 20 / 30 / 40 XP for trivial / low / moderate / severe / extreme.

**Source:** GM Core, Encounter Budget (https://2e.aonprd.com/Rules.aspx?ID=575): 40/60/80/120/160 XP for a four-character party, adjusted 10/15/20/30/40 XP per character above or below four. Verified against foundryvtt/pf2e v8.5.1 @06b904d6ced9795c4c07af085e6f61a56f845c60 (ORC implementation citing Archives of Nethys inline), src/scripts/macros/xp/index.ts `generateEncounterBudgets`, which computes partySize x 20 and multiplies by 0.5/0.75/1/1.5/2 — identical for a party of four and identical to the per-character adjustment for any other size.

---

## Creature XP by level relative to the party

| Creature level − party level | XP |
|---|---|
| -4 | 10 |
| -3 | 15 |
| -2 | 20 |
| -1 | 30 |
| 0 | 40 |
| 1 | 60 |
| 2 | 80 |
| 3 | 120 |
| 4 | 160 |

Levels outside −4…+4 clamp to the ends of the table.

**Source:** GM Core, Creature XP by level relative to the party (https://2e.aonprd.com/Rules.aspx?ID=575), and the Proficiency Without Level column (https://2e.aonprd.com/Rules.aspx?ID=1371). Verified against foundryvtt/pf2e v8.5.1 @06b904d6ced9795c4c07af085e6f61a56f845c60 (ORC implementation citing Archives of Nethys inline), src/scripts/macros/xp/index.ts `xpCreatureDifferences` and `xpVariantCreatureDifferences`.

### With Proficiency Without Level

That variant flattens the math, so a wider band of levels stays relevant and the XP table
changes with it. Pass `--pwol`.

| Creature level − party level | XP |
|---|---|
| -7 | 9 |
| -6 | 12 |
| -5 | 14 |
| -4 | 18 |
| -3 | 21 |
| -2 | 26 |
| -1 | 32 |
| 0 | 40 |
| 1 | 48 |
| 2 | 60 |
| 3 | 72 |
| 4 | 90 |
| 5 | 108 |
| 6 | 135 |
| 7 | 160 |

---

## Hazard XP

A **simple** hazard is worth a fifth of a creature of the same relative level. A **complex**
hazard — one that rolls initiative and acts each round — is worth the same as a creature.

| Hazard level − party level | Simple hazard XP |
|---|---|
| -4 | 2 |
| -3 | 3 |
| -2 | 4 |
| -1 | 6 |
| 0 | 8 |
| 1 | 12 |
| 2 | 16 |
| 3 | 24 |
| 4 | 32 |

**Source:** GM Core, Hazard XP: a simple hazard is worth a fifth of a creature of the same relative level; a complex hazard is worth the same as a creature. Verified against foundryvtt/pf2e v8.5.1 @06b904d6ced9795c4c07af085e6f61a56f845c60 (ORC implementation citing Archives of Nethys inline), src/scripts/macros/xp/index.ts `xpSimpleHazardDifferences` and `getHazardXp`.

---

## Elite and Weak adjustments

- **Weak** — -2 to AC, attack rolls, DCs, saves, Perception, skills and damage; HP down by 10 (level 1-2), 15 (3-4), 20 (5-19) or 30 (level 20+). An adjusted creature's XP value is that of a creature one level lower.
- **Elite** — +2 to AC, attack rolls, DCs, saves, Perception, skills and damage; HP up by 10 (level 1-2), 15 (3-4), 20 (5-19) or 30 (level 20+). An adjusted creature's XP value is that of a creature one level higher.

**⚠ UNVERIFIED —** GM Core, Elite and Weak adjustments (https://2e.aonprd.com/Rules.aspx?ID=1027 area). UNVERIFIED — the HP steps by level band could not be checked against a source reachable from this machine. The +/-2 to numbers is well established; confirm the HP column before leaning on it.

---

## The solo adjustment — read this before spending the budget

`pf2e.py encounter --party-size 1` prints a warning every time, because the number it gives is
correct and still misleading. The XP budget prices creatures by level. It does not price
**turns**.

For one character:

| What the budget says | What it plays like |
|---|---|
| Four level−2 creatures, 40 XP, "moderate" | Four attacks per round against one AC, one turn back. Frequently lethal. |
| One level+2 creature, 80 XP, "extreme" | One attack routine against one AC, one turn back. Hard, and survivable. |

So, for a party of one or two:

1. **Prefer fewer, higher-level enemies.** One level+1 or level+2 creature is a fight. Four
   level−2 creatures is a mugging.
2. **Apply Weak to mooks** in any group of three or more, and say you have.
3. **Cap how many enemies act per round** if a crowd is unavoidable — "three act, the rest
   reposition" — and tell the player the cap exists.
4. **Batch identical low-level creatures** into a squad (`06-encounter-runner.md`) so the fight
   moves at all. Each still keeps its own HP.
5. **Give the objective a reason to end the fight early** (`17-encounter-objectives.md`). A
   solo character cannot win a war of attrition, so do not build one.
6. **Check the action-economy ratio**: enemy turns per round divided by party turns per round.
   At 4:1 a moderate encounter is doing severe damage. At 1:1 it is doing what the budget says.

The lever values for each preset are in `03-difficulty-and-solo-levers.md` and get written into
`RULES_DELTAS.md`.

---

## Working an encounter up

1. **Decide the objective first**, then pick creatures that make it interesting. Building the
   creature list first produces a damage race.
2. **Get the budget:** `pf2e.py encounter --party-level N --party-size M --threat moderate`.
3. **Pick creatures from published material** and write each `bestiary/<name>.md` with its
   `Source:` line, level, traits, full stats and `Tactics:` note.
4. **Price the list:** `--add "ghoul:2" --add "ghoul:2" --add "ghast:3"`. The tool reports the
   spend and the resulting threat rating, which is often not the one that was aimed at.
5. **Add the terrain and the timer.** A fight on a flat floor with no clock is the least
   interesting version of itself.
6. **Write the morale threshold** for each group.
7. **Record the objective in the encounter** so it is in `state.json` and survives a checkpoint,
   and **telegraph it** in round 1.

### XP award

The XP awarded is the encounter's total XP, adjusted for party size — the tool's `xpPerPlayer`
equivalent. For a party of one, an encounter that cost 60 XP against a 20 XP moderate budget is
a severe fight and awards accordingly. 1000 XP is a level.

```
python3 tools/state.py --campaign X xp add 80
```

The tool warns at 1000 and points at `11-leveling-up.md`.

---

## Hazards

A hazard needs a `Source:` line like any creature. Record its stealth DC, its disable DC, its
trigger, its effect and its routine if complex. Price it with `--hazard "name:level"` or
`--hazard "name:level complex"`.

A hazard the player has no way to detect is not a hazard, it is damage. Give it a tell.

