# Mirren Vale

A full PF2e Remaster character sheet. The **built character** is canonical here: ancestry,
heritage, background, class, feats, proficiencies, spells known. The **volatile numbers** —
current HP, conditions, Hero Points, focus, slots used, coins, item charges — are canonical
in `state.json` and appear in `CHECKPOINT.md`. Nothing volatile is duplicated here.

- **Player:** player / GM
- **Kind:** pc / ally / sidekick / companion / familiar / eidolon
- **Level:**
- **Ancestry / heritage:**
- **Background:**
- **Class:**
- **Key ability:**
- **Deity / philosophy:**
- **Languages:**
- **Source of build rules:** Player Core / Player Core 2 (name the book and page for
  anything uncommon or rare)

## Attributes

| Str | Dex | Con | Int | Wis | Cha |
|---|---|---|---|---|---|
| | | | | | |

Boosts taken at level 1: ancestry, background, class key ability, four free.

## Defences

| | Value | Proficiency | Breakdown |
|---|---|---|---|
| AC | | | 10 + Dex (capped) + prof + item |
| Fortitude | | | |
| Reflex | | | |
| Will | | | |
| Perception | | | |
| HP max | | | ancestry + (class + Con) per level |

## Speed and senses

- **Speed:**
- **Senses:**

## Attacks

| Attack | Bonus | Damage | Traits | MAP (2nd / 3rd) |
|---|---|---|---|---|
| | | | | -5 / -10 (agile -4 / -8) |

Multiple attack penalty: `python3 tools/pf2e.py sources` (`map`).

## Skills

| Skill | Prof | Mod | Notes |
|---|---|---|---|
| | | | |

## Feats and features

- **Ancestry feats:**
- **Class features:**
- **Class feats:**
- **Skill feats:**
- **General feats:**
- **Archetype feats (if Free Archetype is on):**

## Spells / focus spells

- **Tradition:**
- **Spell attack / DC:**
- **Slots by rank:** _(the counts are canonical in `state.json`)_
- **Spells known / prepared:**
- **Focus spells:**

## Reactions

| Reaction | Trigger | Effect |
|---|---|---|
| | | |

The GM must offer these before resolving any trigger. See `system/06-encounter-runner.md`.

## Gear

The item list and Bulk total are canonical in `state.json`. Record here only what the gear
*is* and why this character carries it.

| Item | Why |
|---|---|
| | |

## Backstory

A cartographer who took a commission she should have refused.

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
| 1 | 2026-10-05 | Character created |
