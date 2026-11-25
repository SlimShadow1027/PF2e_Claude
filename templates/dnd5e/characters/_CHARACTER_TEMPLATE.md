# {{PC_NAME}}

A D&D 5e (2024 rules) character sheet. The **built character** is canonical here: species,
background, class, subclass, feats, proficiencies, spells. The **volatile numbers** —
current HP, conditions, exhaustion, death saves, Heroic Inspiration, Hit Point Dice, spell
slots used, concentration, coins, item charges — are canonical in `state.json` and appear in
`CHECKPOINT.md`. Nothing volatile is duplicated here.

- **Player:** player / GM
- **Kind:** pc / ally / sidekick / companion / familiar
- **Level:**
- **Species:**
- **Background (and its Origin feat):**
- **Class / subclass:**
- **Languages:**
- **Source of build rules:** SRD 5.2.1, or name the book and page for anything outside it

## Ability scores

| | Str | Dex | Con | Int | Wis | Cha |
|---|---|---|---|---|---|---|
| Score | | | | | | |
| Modifier | | | | | | |
| Save | | | | | | |

Proficiency bonus: `python3 tools/dnd5e.py level` (by level). Saving-throw proficiencies come
from the class.

## Defences

| | Value | Breakdown |
|---|---|---|
| AC | | armour + Dex (capped by armour) + shield + other |
| HP max | | class die max at 1st + (die avg or roll + Con) per level |
| Hit Point Dice | | one per level, size from the class |
| Passive Perception | | 10 + Wisdom (Perception) |
| Initiative | | Dex modifier + other |

## Speed and senses

- **Speed:**
- **Senses:**

## Attacks

| Attack | To hit | Damage | Properties / Mastery |
|---|---|---|---|
| | | | |

Critical hits roll the damage dice twice and add modifiers once:
`python3 tools/roll.py damage "1d8+3" --crit` in a 5e campaign.

## Skills

| Skill | Proficient / Expertise | Mod |
|---|---|---|
| | | |

## Features and feats

- **Species traits:**
- **Origin feat:**
- **Class features:**
- **Subclass features:**
- **Feats (ASI levels):**

## Spellcasting

- **Spellcasting ability:**
- **Spell attack / save DC:** (8 + proficiency + ability modifier)
- **Slots by level:** _(the counts are canonical in `state.json`)_
- **Cantrips:**
- **Spells prepared:**

## Reactions

| Reaction | Trigger | Effect |
|---|---|---|
| Opportunity Attack | a creature you can see leaves your reach | one melee attack |
| | | |

The GM must offer these before resolving any trigger. See `system/06-encounter-runner.md`.

## Gear

The item list is canonical in `state.json`. Record here only what the gear *is*, its weight,
and why this character carries it. Carrying capacity: Strength score × 15 lb.

| Item | Weight | Why |
|---|---|---|
| | | |

## Backstory

{{PC_BACKSTORY}}

## Bonds and ties

- **ally-of:**
- **rival-of:**
- **owes:**
- **owed-by:**
- **serves:**
- **related-to:**
- **fears:**

`tools/graph.py` reads these fields. Mark a tie the player has not learned with `[unknown]`
and a GM-side one with `[gm-only]`; both stay out of the player-safe graph.

## Level-up history

| Level | Date taken | What changed |
|---|---|---|
| 1 | {{CREATED_DATE}} | Character created |
