# 11 (D&D 2024) — Levelling up

**Replaces `system/11-leveling-up.md` for a campaign with `System: dnd5e`.**

---

## When

XP is **cumulative and never reset**. A character levels when their total reaches the next
threshold:

| Level | XP | Level | XP | Level | XP | Level | XP |
|---|---|---|---|---|---|---|---|
| 2 | 300 | 7 | 23,000 | 12 | 100,000 | 17 | 225,000 |
| 3 | 900 | 8 | 34,000 | 13 | 120,000 | 18 | 265,000 |
| 4 | 2,700 | 9 | 48,000 | 14 | 140,000 | 19 | 305,000 |
| 5 | 6,500 | 10 | 64,000 | 15 | 165,000 | 20 | 355,000 |
| 6 | 14,000 | 11 | 85,000 | 16 | 195,000 | | |

```
python3 tools/dnd5e.py advancement --xp 7000
```

**Do not subtract the threshold.** That is the Pathfinder rule, and applying it here would cost the
character every level after the first. `state.py xp add` accumulates.

Milestone levelling instead of XP is a legitimate choice — record it in `RULES_DELTAS.md` and then
level at arc ends rather than tracking a number nobody is reading.

---

## The checklist

Work through it in order. Say each result out loud as you go, with the arithmetic.

1. **Confirm the XP total reaches the threshold.** `state.py get party.xp`.
2. **Choose the class.** Usually the same one; see "Multiclassing" in the SRD if not.
3. **Hit Points.** Roll the Hit Die and add the Constitution modifier, or take the fixed value —
   **the player's choice, offered, not assumed**. Fixed is Barbarian 7, Fighter/Paladin/Ranger 6,
   Bard/Cleric/Druid/Monk/Rogue/Warlock 5, Sorcerer/Wizard 4, each plus Con.
   ```
   python3 tools/roll.py expr "1d10" --campaign X --label "Level 5 Hit Die"
   ```
   Minimum 1 added. **Also add one Hit Die** to the pool.
4. **New class features.** Read the class table for the new level and note every one. Make the
   choices a new feature offers now, not later.
5. **Subclass**, if this is the level the class chooses or advances one.
6. **Proficiency Bonus**, if it changed: levels 5, 9, 13 and 17. **When it changes, every number
   that includes it changes** — attack bonuses, proficient saves, proficient skills, spell save DC,
   spell attack. This is the step most often missed, and it moves eight or ten numbers at once.
7. **Ability Score Improvement or a feat**, at levels 4, 8, 12, 16 and 19 for most classes. If an
   ability score increases to an even number, its modifier changes — and **if Constitution's
   modifier increases, the HP maximum rises by 1 per level already attained**, not just by 1.
8. **Epic Boon** at level 19, where the class grants one.
9. **Spell slots and prepared spells.** The new row of the class table. Full casters share one
   progression (`python3 tools/dnd5e.py tables`); half casters and Warlocks have their own.
   ```
   python3 tools/state.py --campaign X slots set thorne --rank 3 --max 2
   ```
10. **Weapon mastery**, if the class's count changed.
11. **Re-derive everything** — next section.
12. **Write it to `state.json`**, then **checkpoint**.

---

## Re-derive every number from scratch, then diff

The point of this step is to catch a mistake made three levels ago. **Do not adjust the stored
numbers; rebuild them from the parts and compare.**

For each character, recompute and show:

| Number | From |
|---|---|
| Proficiency Bonus | level |
| HP maximum | level 1 full die + each level's roll or fixed value + (Con modifier × level) |
| Hit Dice | one per level, of the class's die |
| AC | base 10 + Dex, then armour and shield. Only one base calculation |
| Initiative | Dex modifier |
| Each attack bonus | ability modifier + PB where proficient |
| Each damage expression | weapon dice + the same ability modifier |
| All six saving throws | ability modifier + PB where the class is proficient |
| Every skill | ability modifier + PB where proficient, doubled where Expertise |
| Passive Perception | 10 + the Wisdom (Perception) total |
| Spell save DC | 8 + PB + spellcasting ability modifier |
| Spell attack | PB + spellcasting ability modifier |
| Spell slots per level | the class table row |
| Carrying capacity | Strength score × 15 lb (Small/Medium) |
| Attunement | still 3, unless a feature says otherwise |

Then print a diff against what was stored and **report every disagreement**, including the ones in
the character's favour:

```
AC          16 → 16   ok
Fort save   —          (not a D&D save; was this imported from a PF2e sheet?)
Dex save    +4 → +5    PB rose to +3
Spell DC    13 → 14    PB rose to +3
HP max      28 → 38    +1d10+2 for level 4, rolled 8
Stealth     +5 → +6    PB rose to +3
```

A number that disagrees for no reason you can name is a bug from an earlier session. Say so, find
it, and fix it in the open.

---

## Item and wealth expectations at the new level

SRD 5.2 publishes **no treasure-by-level table** — see `09-loot-and-economy.md`. What it does
publish is the starting-equipment-at-higher-levels table, which is the nearest thing to a
statement of what a character of a given level is assumed to have:

| Level band | Money | Magic items |
|---|---|---|
| 2–4 | normal starting equipment | 1 common |
| 5–10 | 500 gp + 1d10 × 25 gp | 1 common, 1 uncommon |
| 11–16 | 5,000 gp + 1d10 × 250 gp | 2 common, 3 uncommon, 1 rare |
| 17–20 | 20,000 gp + 1d10 × 250 gp | 2 common, 4 uncommon, 3 rare, 1 very rare |

```
python3 tools/dnd5e.py treasure --level 7 --party-size 1
```

**Read it as a floor, not a budget.** A character well under it is under-equipped by the game's own
assumption; a character well over it is not broken, because this game has no item-bonus curve the
maths depends on. Bounded accuracy means magic items are a change in options far more than a change
in numbers — which is why being behind matters less here than it does in Pathfinder, and why
catching up should happen in the fiction rather than by handing over a pile.

---

## Then

- **Say what changed and what it opens up**, in play terms rather than mechanics: not "+1
  Proficiency Bonus", but "everything you were trained in just got better, and the ward that beat
  you in Neth is now inside reach."
- **Checkpoint.** `state.py checkpoint "level 5 — <what it cost to get here>"`.
- **Re-read `FLAGS.md`.** A level is a natural place to deliver on something the player asked for.
- **Re-read the difficulty preset.** The encounter budget moved; check the party shape still fits.
