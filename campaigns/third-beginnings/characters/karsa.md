# Karsa

A full PF2e Remaster character sheet. The **built character** is canonical here. The
**volatile numbers** — current HP, conditions, Mythic Points, focus, slots used, coins, item
charges — are canonical in `state.json` and appear in `CHECKPOINT.md`. Nothing volatile is
duplicated here.

- **Player:** player
- **Kind:** pc
- **Level:** 1
- **Ancestry / heritage:** Human (Versatile Heritage) — *Player Core*
- **Ethnicity:** **Nidalese by descent**, several generations removed; the family left Nidal
  and did not go back. Enough of the old tongue survived the move to leave Karsa with a
  **smattering of Shadowtongue** — single words, inscriptions, the shape of a phrase — and
  nothing like conversation.
- **Background:** Martial Disciple (Athletics) — *Player Core* p.87
- **Class:** **Cleric** (Warpriest doctrine) / **Monk** — dual-class
- **Key ability:** Wisdom (cleric) and Strength (monk)
- **Deity:** **Irori**, the Master of Masters — *Divine Mysteries* p.70
- **Sanctification:** holy
- **Languages:** Common, Varisian, Shoanti (the third is a house rule — see
  `RULES_DELTAS.md`). **Shadowtongue is not a known language**; see Ethnicity above.
- **Source of build rules:** *Player Core*, *Player Core 2*, *Rival Academies* (Flood
  Stance), *Character Guide* (Gloomseer), *War of Immortals* (mythic), and the legacy
  *Gamemastery Guide* for the dual-class and ancestry-paragon variants. Every variant and
  house rule in force is in `RULES_DELTAS.md`.

## Attributes

| Str | Dex | Con | Int | Wis | Cha |
|---|---|---|---|---|---|
| 18 (+4) | 12 (+1) | 16 (+3) | 10 (+0) | 16 (+3) | 10 (+0) |

Boosts taken at level 1 — **eleven**, not the standard ten:

| Source | Boosts |
|---|---|
| Ancestry (Versatile Human, two free) | Str, Wis |
| Background (Martial Disciple: Str or Dex, plus one free) | Str, Con |
| Class key — cleric | Wis |
| Class key — monk (**house rule**, see `RULES_DELTAS.md`) | Str |
| Four free | Str, Con, Wis, Dex |

Strength reaches 18 only because of that eleventh boost. Without it the character is Str 16
and every Athletics check, unarmed attack and damage roll drops by 1.

## Defences

| | Value | Proficiency | Breakdown |
|---|---|---|---|
| **HP** | **22** | — | 8 ancestry + (10 class + 3 Con + 1 Toughness) × 1 |
| **AC** | **18** | trained medium (+3) | 10 + 1 Dex (capped by breastplate) + 3 + 4 breastplate |
| **AC, shield raised** | **20** | — | +2 circumstance from the steel shield |
| **Fortitude** | **+8** | expert (+5) | +5 + 3 Con — expert from Warpriest First Doctrine |
| **Reflex** | **+6** | expert (+5) | +5 + 1 Dex — expert from monk |
| **Will** | **+8** | expert (+5) | +5 + 3 Wis — expert from cleric |
| **Perception** | **+6** | trained (+3) | +3 + 3 Wis |
| **Cleric class DC** | **16** | trained (+3) | 10 + 3 + 3 Wis |
| **Monk class DC** | **17** | trained (+3) | 10 + 3 + 4 Str |
| **Cleric spell DC** | **16** | trained (+3) | 10 + 3 + 3 Wis |
| **Cleric spell attack** | **+6** | trained (+3) | +3 + 3 Wis |

Dual-class takes the **highest** proficiency for each statistic (*Gamemastery Guide* p.192),
which is why all three saves are expert — an unusual spread for level 1.

**Dying maximum is effectively doomed-gated, not 4.** As a mythic character, when Karsa's
dying value would reach 4 they instead gain **doomed 1 and stabilise at 0 HP**, and only die
permanently at **doomed 4** (*War of Immortals* p.76).

## Speed and senses

- **Speed 25 feet.** Human base 25. Breastplate has a Strength requirement of 16, which
  Str 18 clears, so no armour speed penalty.
- **Low-light vision**, from **Gloomseer** (*Character Guide* p.12) — and it is the reason
  the Nidalese descent is on the sheet rather than in the backstory only.

## Attacks

| Attack | Bonus | Damage | Traits / notes |
|---|---|---|---|
| **Flooded river** (Flood Stance) | **+7** | **1d10+4 bludgeoning** | brawling group; nonlethal, trip, unarmed, water. **No underwater penalty**, and **gains forceful underwater.** |
| Fist | +7 | 1d6+4 bludgeoning | Powerful Fist makes it d6 and removes the lethal-attack penalty |

- Attack bonus: +1 level +2 trained unarmed +4 Str.
- The **1d10** on flooded river is a **house ruling**, not the text — Deadly Simplicity
  upgrades *Irori's favored weapon (fist)*, and flooded river is a separate unarmed attack.
  By the strict reading it is **1d8**. See `RULES_DELTAS.md`.
- **Multiple attack penalty** −5 / −10 — flooded river is **not** agile.
- **Flurry of Blows** (monk): two unarmed Strikes for one action, sharing a MAP step.

**Source:** Flood Stance — *Rival Academies* p.80,
<https://2e.aonprd.com/Feats.aspx?ID=7492>. Powerful Fist and Flurry of Blows — monk level 1.
Deadly Simplicity — <https://2e.aonprd.com/Feats.aspx?ID=7492> chain; feat text quoted in
`RULES_DELTAS.md`.

## Skills

Trained: **Acrobatics, Arcana, Athletics, Diplomacy, Medicine, Religion, Stealth, Survival**,
plus **Warfare Lore**.

| Skill | Bonus | Note |
|---|---|---|
| **Athletics** | **+7** | Irori's divine skill. The whole build runs through this line. |
| Acrobatics | +4 | |
| Arcana | +3 | Assurance (Arcana) gives a flat **13** instead of rolling |
| Diplomacy | +3 | |
| Medicine | +6 | Treat Wounds DC 15 for 2d8, or 4d8 on a critical success |
| Religion | +6 | |
| Stealth | +4 | |
| Survival | +6 | |
| Warfare Lore | +3 | |

**Athletics at +7 with Titan Wrestler** means Karsa can Grapple, Shove, Trip or Disarm
creatures **two sizes larger** than themselves.

## Feats and features

### Class features

| Feature | From |
|---|---|
| Deity, Anathema, Sanctification (holy), Divine Font (**Heal**), Divine Spellcasting | Cleric |
| **Warpriest** First Doctrine — trained light and medium armour, **expert Fortitude**, **Shield Block**, and **Deadly Simplicity** because Irori's favored weapon is a fist | Cleric doctrine, *Player Core* p.112 |
| **Powerful Fist**, **Flurry of Blows** | Monk level 1 |
| **Mythic Calling: Sage's Calling**, and the **Rewrite Fate** free action | *War of Immortals* p.80 / p.78 |

### Feats

| Feat | Slot | Source |
|---|---|---|
| **Toughness** | General (via Versatile Heritage) | +1 HP per level; recovery DC easier |
| **Gloomseer** | Human ancestry feat | *Character Guide* p.12 — low-light vision. Requires Nidalese ethnicity. |
| **Natural Ambition** | Ancestry feat (ancestry paragon slot) | grants a 1st-level class feat |
| **Qi Spells** → *inner upheaval* | Class feat, via Natural Ambition | *Player Core 2* p.119. **This replaces the legacy "Ki Strike"** on the imported sheet — same ability, current name. Focus pool of 1. |
| **Flood Stance** | Monk class feat 1 | *Rival Academies* p.80 |
| **Assurance (Arcana)** | Skill feat ("Skill Paragon" — not a published variant) | flat 13 instead of a roll |
| **Quick Jump** | Skill feat — **the Martial Disciple background grants this**, so it is not a bonus | High/Long Jump as one action, no run-up |

### The five bonus skill feats

Granted outright, not paid for. Not a published variant — see `RULES_DELTAS.md`. All five are
Athletics feats and four of them are load-bearing in a flooded vertical dungeon.

| Feat | What it does | Source |
|---|---|---|
| **Underwater Marauder** | **Not off-guard while in water**, and no penalty for bludgeoning or slashing melee weapons in water | *Player Core* |
| **Combat Climber** | **Not off-guard while Climbing**, and you can Climb with one hand occupied | *Player Core* |
| **Titan Wrestler** | Disarm, Grapple, Shove or Trip creatures **two sizes larger** | *Player Core* |
| **Hefty Hauler** | **+2 to both Bulk limits** — recorded as `bulk_bonus: 2` in state | *Player Core* |
| **Quick Jump** | (duplicate of the background feat; counts once) | *Player Core* |

## Spells / focus spells

**Divine, prepared, Wisdom.** Spell DC 16, spell attack +6.

- **Cantrips (5, unlimited, auto-heightened):** Light · Shield · Guidance · Divine Lance ·
  Detect Magic
- **Rank 1 prepared slots (2):** **Jump** *(Irori's granted 1st-rank spell)* · **Bless**
- **Divine Font — Heal ×4.** A separate pool from the prepared slots, tracked as
  `divine_font` in state.
- **Focus pool 1 —** *inner upheaval* (the Remaster's ki strike). **Refocus** is 10 minutes
  of the class's activity.

## Reactions

Offer each of these before resolving any trigger. This is the GM's obligation, not the
player's job to remember.

| Reaction | Trigger | Effect |
|---|---|---|
| **Shield Block** | An attack damages you while your shield is raised | Reduce damage by the shield's Hardness; the shield takes the rest |
| **Rewrite Fate** | You roll a skill check or saving throw and dislike the result | **Spend a Mythic Point**, reroll at **mythic proficiency (+11 at level 1)**, take the new result |

Karsa has **no Reactive Strike** — neither cleric nor monk grants it at level 1.

## Gear

Worn: **breastplate** (Bulk 2, worn armour counts in full — no rule reduces it) and a
**steel shield** (Bulk 1).

Carried, in a backpack: healer's toolkit · 100 ft rope · climbing kit · grappling hook ·
hooded lantern and 6 pints of oil · 5 torches · flint and steel · chalk · 10 pitons ·
crowbar · 2 weeks rations · waterskin · bedroll · 2 sacks.

- **Bulk 6.6 carried, 4.6 counted** (the backpack's first 2 Bulk are free — *Player Core*
  p.287). **Encumbered after 11, maximum 16** with Hefty Hauler.
- **5 gp** remaining of the starting 15, after breastplate (8 gp) and steel shield (2 gp).
- The expedition kit itself is a **house-ruled allowance** worth 9 gp 6 cp at *Player Core*
  prices, itemised in `RULES_DELTAS.md`.

## Backstory

Karsa's family came out of Nidal generations ago and never discussed why. What survived the
move was not the faith and not the language — only a handful of Shadowtongue words nobody
could quite place, and a tolerance for the dark that reads as a knack until you learn where
it came from.

Irori found Karsa the way Irori finds most people: through a book. The *Unbinding of Fetters*
argues that a body and a mind are instruments you are obliged to sharpen, and Karsa took that
as permission to be curious about everything.

What Karsa has been curious about lately is **Roderic** — the man the Cove is named for, whose
story does not survive in any form Karsa can make agree with itself. Two accounts of the
founding, three accounts of the man, and no account at all of what he was doing on that
stretch of coast before there was a town on it. Nobody in Roderic's Cove has asked the
question in living memory. They dredge the caves for salvage and sell it, and the story of the
name is a thing you say to visitors.

Karsa came for the true version. The treasures and the knowledge that might still be down
there are the reason it is worth the swim.

## Bonds and ties

- **ally-of:** Vessa Tarn [to be built]
- **serves:** Irori
- **fears:** [unknown]
- **related-to:** a Nidalese family line, several generations back [gm-only]

## Level-up history

| Level | Date taken | What changed |
|---|---|---|
| 1 | 2026-09-30 | Character created — imported from Pathbuilder, re-derived, one attribute-boost discrepancy resolved by house rule, `Ki Strike` translated to the Remaster's `Qi Spells` → *inner upheaval* |
