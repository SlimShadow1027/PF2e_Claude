# Shavi Beifong

A full PF2e Remaster character sheet. The **built character** is canonical here. The **volatile
numbers** (current HP, conditions, Hero Points, focus, coins) are canonical in `state.json` and
appear in `CHECKPOINT.md`.

- **Player:** player
- **Kind:** pc
- **Level:** 1
- **Ancestry / heritage:** Human — [Versatile Human](https://2e.aonprd.com/Heritages.aspx?ID=262) (Player Core p.63)
- **Background:** [Waste Walker](https://2e.aonprd.com/Backgrounds.aspx?ID=279) (Guns & Gears (Remastered) p.123)
- **Class:** **Dual Class** — [Ranger](https://2e.aonprd.com/Classes.aspx?ID=36) (Player Core; Hunter's Edge: Precision) /
  [Kineticist](https://2e.aonprd.com/Classes.aspx?ID=23) (Rage of Elements; Single Gate, Earth)
- **Key ability:** Str (Ranger) / Con (Kineticist)
- **Deity / philosophy:** —
- **Languages:** Common, Dwarven, Petran
- **Source of build rules:** Pathbuilder export, re-derived 2026-10-12. Variants: Dual Class, Free Archetype,
  Ancestry Paragon, Automatic Bonus Progression, Gradual Attribute Boosts; house rules in `RULES_DELTAS.md`.

## Attributes

| Str | Dex | Con | Int | Wis | Cha |
|---|---|---|---|---|---|
| 18 (+4) | 12 (+1) | 18 (+4) | 10 (+0) | 12 (+1) | 12 (+1) |

## Defences

Proficiency at level 1: trained = 3, expert = 5 (level + 2 / + 4).

| | Value | Proficiency | Breakdown |
|---|---|---|---|
| AC | **18** (20 with shield raised) | trained (medium) | 10 + 1 Dex (cap +1) + 3 + 4 breastplate |
| Fortitude | **+9** | expert | 4 Con + 5 |
| Reflex | **+6** | expert | 1 Dex + 5 |
| Will | **+4** | trained | 1 Wis + 3 |
| Perception | **+6** | expert (Ranger) | 1 Wis + 5 |
| HP max | **31** | — | 8 ancestry + 10 Ranger + 8 Kineticist + 4 Con + 1 Toughness — **dual-class HP stacking, homebrew** |
| Class DC | **17** | trained | 10 + 4 (Str or Con) + 3 — same for both classes |

Breastplate: Str +3 requirement met by Str 18, so neither its −2 check penalty nor its −5 ft Speed
penalty applies.

## Speed and senses

- **Speed:** 25 feet
- **Senses:** none beyond normal vision. **No darkvision or low-light vision** — Shavi needs light underground.

## Attacks

| Attack | Bonus | Damage | Traits | MAP (2nd / 3rd) |
|---|---|---|---|---|
| Elemental Blast, melee (earth) | +7 impulse | 1d8+4 bludgeoning or piercing; +4 status if 2-action | attack, impulse, primal; Weapon Infusion may add agile, backswing, forceful, reach or sweep | −5 / −10 (agile −4 / −8) |
| Elemental Blast, ranged (earth) | +7 impulse | 1d8 bludgeoning or piercing; +4 status if 2-action | range 30 ft; Weapon Infusion may change range (see below) | −5 / −10 |
| Fist | +7 | 1d4+4 bludgeoning | agile, finesse, nonlethal, unarmed | −4 / −8 |

- Impulse attack = 4 Con + 3 trained. Melee blast adds Str; a 2-action blast adds Con as a status bonus.
- **Precision** (Hunter's Edge): the first hit on your hunted prey each round deals +1d8 precision. Works on blasts.
- **Gravity Weapon** (house rule): +2 status to damage on the first **Weapon Infusion**-shaped blast each round.
- **Weapon Infusion, ranged options:** 100 ft increment + volley 30 ft; 50 ft + propulsive; or 20 ft + thrown.

## Skills

| Skill | Prof | Mod | Notes |
|---|---|---|---|
| Acrobatics | T | +4 | |
| Arcana | U | +0 | |
| Athletics | T | **+7** | |
| Crafting | T | +3 | |
| Deception | U | +1 | |
| Diplomacy | U | +1 | |
| Intimidation | T | +4 | |
| Medicine | T | +4 | Treat Wounds needs a healer's toolkit — not carried |
| Nature | T | +4 | |
| Occultism | U | +0 | |
| Performance | U | +1 | |
| Religion | U | +1 | |
| Society | U | +0 | |
| Stealth | T | +4 | |
| Survival | T | +4 | |
| Thievery | U | +1 | |
| Wastes Lore | T | +3 | Waste Walker |
| Underground Lore | T | +3 | |
| Warfare Lore | T | +3 | |

## Feats and features

- **Ancestry feats:** [Natural Ambition](https://2e.aonprd.com/Feats.aspx?ID=4478) → Initiate Warden.
  Ancestry Paragon grants one more at level 1 — **not in the export summary; to confirm.**
- **Heritage general feat:** [Toughness](https://2e.aonprd.com/Feats.aspx?ID=5227) (Versatile Human)
- **Class features — Ranger:** Hunt Prey (◆), Hunter's Edge: Precision
- **Class features — Kineticist:** Kinetic Gate (single, earth), Kinetic Aura (10-ft emanation), Channel Elements (◆),
  Elemental Blast (◆ or ◆◆), Base Kinesis
- **Impulse feats (single gate):** [Armor in Earth](https://2e.aonprd.com/Feats.aspx?ID=4221),
  [Stepping Stones](https://2e.aonprd.com/Feats.aspx?ID=4223) (◆◆, Sustain)
- **Class feats:** [Weapon Infusion](https://2e.aonprd.com/Feats.aspx?ID=4186) (Kineticist, free action);
  [Initiate Warden](https://2e.aonprd.com/Feats.aspx?ID=4862) (Ranger, via Natural Ambition).
  Ranger's own level-1 class feat — **to confirm.**
- **Skill feats:** Forager (Waste Walker)
- **General feats:** Toughness
- **Archetype feats:** none yet — Free Archetype begins at level 2
- **Mythic:** none — Calling and Rewrite Fate arrive at level 2–3

## Spells / focus spells

- **Tradition:** primal (Ranger warden)
- **Spell attack / DC:** trained, Wis — +4 / 14 (Gravity Weapon uses neither)
- **Slots by rank:** none
- **Focus spells:** [Gravity Weapon](https://2e.aonprd.com/Spells.aspx?ID=1863) (◆, 1 minute). Focus pool 1.

## Reactions

| Reaction | Trigger | Effect |
|---|---|---|
| — | — | **None at level 1.** The wooden shield can be raised but there is no Shield Block. |

## Opening round

Channel Elements (◆) + Hunt Prey (◆) + Gravity Weapon (◆), with the Versatile Action paying for one of
the single-action non-damaging ones, plus Raise a Shield if the Versatile Action is spare. The
breastplate makes Armor in Earth unnecessary at level 1.

## Gear

| Item | Why |
|---|---|
| Breastplate (worn) | Same AC as Armor in Earth at level 1, without spending the action |
| Wooden shield | +2 AC for the Versatile Action |
| Adventurer's Pack | the basics, rope and torches |
| Hooded lantern + 5 pints oil | no darkvision |
| Climbing kit, grappling hook | shafts and vertical galleries |
| Crowbar | collapsed doors, stuck grates |
| Signal whistle | for when you and Kelda are separated |
| Caltrops | slow pursuers in a narrow gallery |

## Backstory

A waste-walker from somewhere desolate, now a hired guard and guide. Kelda Vornshield has engaged
Shavi to take her into the depths of Maza-Khad, where the Labyrinth is rumoured to be.

## Bonds and ties

- **serves:** Kelda Vornshield (hired guard and guide)

## Level-up history

| Level | Date taken | What changed |
|---|---|---|
| 1 | 2026-10-12 | Character created — Pathbuilder export re-derived; Calling stripped; HP 31 (stacking); Perception +6 (expert) |
