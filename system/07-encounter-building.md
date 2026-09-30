# 07 — Encounter building

Every table here is generated from `tools/pf2e.py`, so this document and the tool cannot
disagree. Run `python3 tools/pf2e.py sources` for the provenance of each.

```
python3 tools/pf2e.py encounter --party-level 3 --party-size 1 --threat moderate
python3 tools/pf2e.py encounter --party-level 3 --party-size 1 --add "ghoul:2" --add "ghast:3"
python3 tools/pf2e.py encounter --party-level 5 --party-size 1 --hazard "rune trap:4 complex"
python3 tools/pf2e.py encounter --party-level 3 --party-size 1 --threat low --smoothed
```

---

## The two rules that matter most at a small table

**1. The XP budget scales with party size. The XP award does not.**

> *"Note that if you adjust your XP budget to account for party size, the XP awards for the
> encounter don't change—you'll always award the amount of XP listed for a group of four
> characters."* — GM Core p.76

So a solo character who clears a moderate-threat encounter — one built to a 20 XP budget, not 80 —
is awarded **80 XP**, the four-character figure. At 1,000 XP per level that is 12.5 moderate
encounters per level, the same as for a full party. This is the mechanism that lets a small party
keep pace with the level curve while fighting a fraction as much. Getting it wrong in either
direction wrecks advancement: award the adjusted budget and a solo character never levels.

**2. The published per-character adjustment sends Low to 0 XP for a solo party.**

Table 10-1 gives Low and Moderate the same Character Adjustment of 20. Subtract three characters'
worth from Low's 60 and you get nothing at all. The tool reports that rather than hiding it, and
offers `--smoothed` — 20 XP per character scaled by threat — which is what many tables use and what
the Foundry VTT implementation computes. The two agree exactly at a party of four.

---

## XP budget by threat level and party size

The published figure, with the smoothed alternative in brackets where they differ.

| Party size | Trivial | Low | Moderate | Severe | Extreme |
|---|---|---|---|---|---|
| 1 | 10 | **0** (15) | 20 | 30 | 40 |
| 2 | 20 | **20** (30) | 40 | 60 | 80 |
| 3 | 30 | **40** (45) | 60 | 90 | 120 |
| 4 | 40 | 60 | 80 | 120 | 160 |
| 5 | 50 | **80** (75) | 100 | 150 | 200 |
| 6 | 60 | **100** (90) | 120 | 180 | 240 |

Four-character budget: trivial 40, low 60, moderate 80, severe 120, extreme 160. Per-character adjustment: trivial 10, low 20, moderate 20, severe 30, extreme 40.

**XP awarded, whatever the party size:** trivial 40, low 60, moderate 80, severe 120, extreme 160.

**Source:** GM Core p.75, Table 10-1: Encounter Budget, and 'Different Party Sizes' (GM Core p.76) — read from https://2e.aonprd.com/Rules.aspx?ID=2715 and ?ID=2719. Budget for four characters is 40 (or less) / 60 / 80 / 120 / 160 XP; the per-character adjustment is 10 (or less) / 20 / 20 / 30 / 40. Quoting the rule: 'For each additional character in the party beyond the fourth, increase your XP budget by the amount shown in the Character Adjustment value... If you have fewer than four characters, use the same process in reverse: for each missing character, remove that amount of XP from your XP budget.' NOTE the published Low and Moderate adjustments are both 20, so the published rule sends Low to 0 XP at a party of one; `encounter_budgets` reports that honestly and offers a smoothed alternative.

**Source:** GM Core p.76, 'Different Party Sizes' (https://2e.aonprd.com/Rules.aspx?ID=2719), quoting: 'Note that if you adjust your XP budget to account for party size, the XP awards for the encounter don't change—you'll always award the amount of XP listed for a group of four characters.' So a solo character who clears a moderate encounter built to a 20 XP budget is awarded the four-character moderate figure of 80 XP, not 20. This is how a small party keeps pace with the 1,000-XP-per-level curve while fighting fewer creatures.

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

Levels outside −4…+4 clamp to the ends of the table. The encounter-design table and the
Rewards award table agree on every row.

**Source:** GM Core, Table 10-2: Creature XP (encounter design) and the matching Adversary XP award table in Rewards — read from https://2e.aonprd.com/Rules.aspx?ID=2715 and ?ID=2647, which agree: -4 -> 10, -3 -> 15, -2 -> 20, -1 -> 30, party level -> 40, +1 -> 60, +2 -> 80, +3 -> 120, +4 -> 160. The Proficiency Without Level column (https://2e.aonprd.com/Rules.aspx?ID=1371) is still only verified against foundryvtt/pf2e v8.5.1 @06b904d6ced9795c4c07af085e6f61a56f845c60 (ORC implementation citing Archives of Nethys inline), src/scripts/macros/xp/index.ts `xpVariantCreatureDifferences`.

### With Proficiency Without Level

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

| Hazard level − party level | Simple hazard XP | Complex hazard XP |
|---|---|---|
| -4 | 2 | 10 |
| -3 | 3 | 15 |
| -2 | 4 | 20 |
| -1 | 6 | 30 |
| 0 | 8 | 40 |
| 1 | 12 | 60 |
| 2 | 16 | 80 |
| 3 | 24 | 120 |
| 4 | 32 | 160 |

**Source:** GM Core, Rewards — Hazard XP award table, read from https://2e.aonprd.com/Rules.aspx?ID=2647. Simple hazards: -4 -> 2, -3 -> 3, -2 -> 4, -1 -> 6, party level -> 8, +1 -> 12, +2 -> 16, +3 -> 24, +4 -> 32. Complex hazards award the same as a creature of that relative level. Both columns checked.

---

## Accomplishment XP

For advancement that is not encounter-driven — which is what milestone pacing means in practice.

| Accomplishment | XP |
|---|---|
| Minor | 10 |
| Moderate | 30 |
| Major | 80 |

**Source:** GM Core, Rewards — Accomplishment XP (https://2e.aonprd.com/Rules.aspx?ID=2647): minor 10 XP, moderate 30 XP, major 80 XP. Useful when advancement is by milestone rather than by encounter.

---

## Elite and Weak adjustments

| Adjustment | Effect |
|---|---|
| Elite | Level +1 (or +2 if the creature is level -1 or 0). +2 to AC, attack modifiers, DCs, saving throws, Perception and skill modifiers. +2 damage to Strikes and other offensive abilities, or +4 if the ability has a limit on how often it can be used (a spellcaster's spells, a dragon's breath). HP up by 10 (level 1 or lower), 15 (2-4), 20 (5-19) or 30 (20+). Award XP for its new level. |
| Weak | Level -1 (or -2 if the creature is level 1). -2 to AC, attack modifiers, DCs, saving throws, Perception and skill modifiers. -2 damage to Strikes and other offensive abilities, or -4 if the ability has a use limit. HP down by 10 (level 1-2), 15 (3-5), 20 (6-20) or 30 (21+). Award XP for its new level. |

The elite and weak HP tables use **different** level bands — see
`system/08-npc-and-bestiary-protocol.md` for the grid, or `pf2e.py tables adjustments`.

**Source:** Monster Core p.6, Adjusting Creatures — read from https://2e.aonprd.com/Rules.aspx?ID=3262. Elite and weak each shift the level by 1 (by 2 at the bottom of the range: elite on a level -1 or 0 creature, weak on a level 1 creature), change AC, attack modifiers, DCs, saves, Perception and skills by 2, change Strike and offensive-ability damage by 2 (by 4 for limited-use abilities), and change HP on the bands above. The two HP tables have DIFFERENT band boundaries, which is easy to get wrong.

---

## The solo adjustment — read this before spending the budget

`pf2e.py encounter --party-size 1` prints a warning every time, because the number it gives is
correct and still misleading. The XP budget prices creatures by level. It does not price **turns**.

For one character:

| What the budget says | What it plays like |
|---|---|
| Four level−2 creatures, 40 XP, "moderate" for a full party | Four attacks per round against one AC, one turn back. Frequently lethal. |
| One level+2 creature, 80 XP | One attack routine against one AC, one turn back. Hard, and survivable. |

So, for a party of one or two:

1. **Prefer fewer, higher-level enemies.** One level+1 or level+2 creature is a fight. Four
   level−2 creatures is a mugging.
2. **Apply Weak to mooks** in any group of three or more, and say you have. Remember weak shifts a
   level-1 creature to level −1, not level 0.
3. **Cap how many enemies act per round** if a crowd is unavoidable — "three act, the rest
   reposition" — and tell the player the cap exists.
4. **Batch identical low-level creatures** into a squad (`06-encounter-runner.md`) so the fight
   moves at all. Each still keeps its own HP.
5. **Give the objective a reason to end the fight early** (`17-encounter-objectives.md`). A solo
   character cannot win a war of attrition, so do not build one.
6. **Check the action-economy ratio**: enemy turns per round divided by party turns per round. At
   4:1 a moderate encounter is doing severe damage. At 1:1 it is doing what the budget says.

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
   spend, the resulting threat rating — often not the one aimed at — and the XP to award.
5. **Add the terrain and the timer.** A fight on a flat floor with no clock is the least
   interesting version of itself.
6. **Write the morale threshold** for each group.
7. **Record the objective in the encounter** so it is in `state.json` and survives a checkpoint,
   and **telegraph it** in round 1.

### XP award

Award the four-character figure for whatever threat the encounter turned out to be — the tool
prints it. 1,000 XP is a level, **and the remainder carries over**.

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

