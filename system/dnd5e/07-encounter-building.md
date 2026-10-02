# 07 (D&D 2024) — Encounter building

**Replaces `system/07-encounter-building.md` for a campaign with `System: dnd5e`.** Read
`17-encounter-objectives.md` alongside it — that document is shared and still applies in full.

Every table here is generated from `tools/dnd5e.py`, so this document and the tool cannot
disagree. Run `python3 tools/dnd5e.py sources` for the provenance of each.

```
python3 tools/dnd5e.py encounter --party-level 3 --party-size 1 --threat moderate
python3 tools/dnd5e.py encounter --party-level 3 --party-size 1 --threat high --cr 2 1/4 1/4
python3 tools/dnd5e.py cr --cr 1/4 2 5
```

---

## The three things to know before building anything

**1. The budget is per character, multiplied by party size.**

> *"Using the XP Budget per Character table, cross-reference the party's level with the desired
> encounter difficulty. Multiply the number in the table by the number of characters in the party
> to get your XP budget for the encounter."*

It is strictly linear, which is the good news at a small table: **a solo character simply gets one
character's budget and nothing degenerates.** Compare the Pathfinder side of this framework, where
the published Low budget collapses to 0 XP at a party of one and the tool has to offer a smoothed
alternative. Here there is nothing to work around.

**2. There is no encounter multiplier.**

The 2014 rules multiplied a monster group's XP by a factor based on how many monsters there were.
**That is gone.** Spend the budget at face value: add creatures, deduct their stat-block XP, stop
when you cannot afford another. *"Spend as much of your XP budget as you can without going over.
It's OK if you have a few unspent XP left over."*

What replaces it is a prose caution about action economy, quoted in full:

> *"If your encounter includes more than two creatures per character, include fragile creatures
> that can be defeated quickly. This guideline is especially important for characters of level 1 or
> 2."*

`encounter` prints the ratio and warns when you cross it. **Take that seriously at a solo table**,
where it is the single most dangerous thing you can get wrong: three creatures against one
character is three turns of attacks against one, and the budget does not price that.

**3. The XP award is the creatures' own XP, undivided.**

The SRD states no party-size adjustment to the award and no division among the party. So a solo
character fighting one character's worth of monsters earns one character's worth of XP and advances
along the published curve at the published rate. The budget scales with party size and the award
does not need to, because the award *is* what was spent.

This is the mirror image of how Pathfinder solves the same problem — there, the budget shrinks and
the award stays at the four-character figure. Both get a small party to the next level on schedule.
Do not import either solution into the other game.

---

## XP budget per character

| Party's level | Low | Moderate | High |
|---|---|---|---|
| 1 | 50 | 75 | 100 |
| 2 | 100 | 150 | 200 |
| 3 | 150 | 225 | 400 |
| 4 | 250 | 375 | 500 |
| 5 | 500 | 750 | 1,100 |
| 6 | 600 | 1,000 | 1,400 |
| 7 | 750 | 1,300 | 1,700 |
| 8 | 1,000 | 1,700 | 2,100 |
| 9 | 1,300 | 2,000 | 2,600 |
| 10 | 1,600 | 2,300 | 3,100 |
| 11 | 1,900 | 2,900 | 4,100 |
| 12 | 2,200 | 3,700 | 4,700 |
| 13 | 2,600 | 4,200 | 5,400 |
| 14 | 2,900 | 4,900 | 6,200 |
| 15 | 3,300 | 5,400 | 7,800 |
| 16 | 3,800 | 6,100 | 9,800 |
| 17 | 4,500 | 7,200 | 11,700 |
| 18 | 5,000 | 8,700 | 14,200 |
| 19 | 5,500 | 10,700 | 17,200 |
| 20 | 6,400 | 13,200 | 22,000 |

**Multiply by the number of characters.** A solo level 3 character's moderate budget is 225 XP; a
party of five at the same level has 1,125.

**Source:** SRD 5.2, "Gameplay Toolbox" → "Combat Encounters" → "Combat Encounter Difficulty",
step 2. Read row by row for all twenty levels and cross-checked value for value against
`foundryvtt/dnd5e` v6.0.5 (`DND5E.ENCOUNTER_DIFFICULTY`), which matches exactly.

### What the three difficulties mean

| | |
|---|---|
| **Low** | *"likely to have one or two scary moments for the players, but their characters should emerge victorious with no casualties. One or more of them might need to use healing resources, however."* |
| **Moderate** | *"Absent healing and other resources, an encounter of moderate difficulty could go badly for the adventurers. Weaker characters might get taken out of the fight, and there's a slim chance that one or more characters might die."* |
| **High** | *"A high-difficulty encounter could be lethal for one or more characters. To survive it, the characters will need smart tactics, quick thinking, and maybe even a little luck."* |

The published Low guideline also notes that *"a single monster generally presents a low-difficulty
challenge for a party of four characters whose level equals the monster's Challenge Rating"* —
useful as a sanity check on a build.

**At a solo table, read one line to the left of where you would for a party.** "A slim chance one
or more characters might die" means a slim chance *the* character dies, and there is nobody to
stabilise them. `03-difficulty-and-solo-levers.md` has the levers.

---

## XP by Challenge Rating

| CR | XP | | CR | XP | | CR | XP |
|---|---|---|---|---|---|---|---|
| 0 | 0 or 10 | | 10 | 5,900 | | 21 | 33,000 |
| 1/8 | 25 | | 11 | 7,200 | | 22 | 41,000 |
| 1/4 | 50 | | 12 | 8,400 | | 23 | 50,000 |
| 1/2 | 100 | | 13 | 10,000 | | 24 | 62,000 |
| 1 | 200 | | 14 | 11,500 | | 25 | 75,000 |
| 2 | 450 | | 15 | 13,000 | | 26 | 90,000 |
| 3 | 700 | | 16 | 15,000 | | 27 | 105,000 |
| 4 | 1,100 | | 17 | 18,000 | | 28 | 120,000 |
| 5 | 1,800 | | 18 | 20,000 | | 29 | 135,000 |
| 6 | 2,300 | | 19 | 22,000 | | 30 | 155,000 |
| 7 | 2,900 | | 20 | 25,000 | | | |
| 8 | 3,900 | | | | | | |
| 9 | 5,000 | | | | | | |

**The XP does not depend on the party's level.** A CR 2 creature is 450 XP whether the party is
level 1 or level 11 — what changes is how much of the budget that consumes.

A stat block's own XP figure is authoritative where it differs; CR 0 is published as "0 or 10", so
read the block.

**Source:** SRD 5.2, "Monsters" → "Experience Points". Cross-checked against `foundryvtt/dnd5e`
(`DND5E.CR_EXP_LEVELS`); the three fractional rows are from the SRD table alone.

---

## The published troubleshooting notes

All five are worth reading before a build, and the first two are the ones that bite at a small
table.

- **Many creatures.** More creatures means more chance a lucky streak on their side does more
  damage than you expected. Past two per character, include fragile ones that die fast.
- **Powerful creatures.** A creature whose CR exceeds the party's level *"might deal enough damage
  with a single action to take out one or more characters"* — the published example is an Ogre
  (CR 2) killing a level 1 Wizard in one blow. At a solo table that is the end of the session, so
  telegraph it or lower it.
- **CR 0 creatures.** Use sparingly, especially the 0-XP ones; use a swarm instead of a crowd.
- **Number of stat blocks.** More than two or three in one fight is daunting to run.
- **Unusual features.** A monster with something low-level characters cannot answer at all is
  usually the wrong monster rather than a hard one.
- **Adjustments.** Die rolls will make an encounter easier or harder than built. Have creatures
  flee or reinforcements arrive — adjust in the fiction, not by changing numbers mid-fight.

**Source:** SRD 5.2, "Gameplay Toolbox" → "Combat Encounters" → "Troubleshooting".

---

## Building one, in order

1. **Pick the objective first.** `17-encounter-objectives.md`. At least half of fights should have
   a win condition other than "everything hostile is dead", and the player has to be able to see it.
2. **Pick a difficulty**, reading one line harder than you mean it if the party is one character.
3. **Multiply the per-character budget by the party size.**
4. **Spend it**, deducting each creature's stat-block XP. Stop before going over.
5. **Check the creature count** against two per character.
6. **Check the CR ceiling** against the party's level.
7. **Name what makes the ground interesting** — elevation, cover, something to move toward or
   knock over. The SRD lists changes in elevation, defensive positions, mixed monster groups and
   reasons to move; a flat empty room is a worse fight than a cheap one.
8. **Write the stat blocks into `campaigns/<slug>/bestiary/`** with a `Source:` line, before the
   fight. `validate.py` fails a bestiary file without one.

```
$ python3 tools/dnd5e.py encounter --party-level 1 --party-size 1 --threat moderate --cr 1/4 1/8
Built encounter: 1 x CR 1/4 (50 XP each), 1 x CR 1/8 (25 XP each)
  total 75 XP → rated **moderate** for 1 character(s) at level 1
  XP awarded on clearing it: 75
```

---

## Adjusting a creature

The SRD publishes no Elite/Weak adjustment templates — those are a Pathfinder tool, and there is no
2024 equivalent in open content. **Do not invent one and present it as a rule.** What you can do,
and should say you are doing:

- **Use a different creature.** The CR ladder is dense enough that there is usually one at the
  right weight.
- **Change the numbers and name it as homebrew.** `Homebrew — Bugbear Warrior (SRD 5.2, CR 1) with
  HP 27→20`, recorded in the bestiary file and in `RULES_DELTAS.md`. The XP you count it as is then
  your judgement, and the file should say so.
- **Change the situation rather than the statistics.** Fewer of them, worse ground, a shorter
  timer, an objective that lets the player win without killing anything. This is almost always the
  better answer and it needs no houseruling at all.

Either way: **cite the base creature, and never freehand a stat block.** Rule 4 of the contract.
