# Party at a glance — The Quiet Between Empires

The numbers here are a convenience copy. **`state.json` is canonical** for everything
volatile — current HP, conditions, resources. When they disagree, `state.json` wins; run
`python3 tools/state.py --campaign the-quiet-between-empires render` and read `CHECKPOINT.md`.

| Character | Level | Role | HP max | AC | Fort | Ref | Will | Perc | Speed | Key skills |
|---|---|---|---|---|---|---|---|---|---|---|
| Shavi Beifong | 1 | Ranger/Kineticist (earth) — guard and guide | 31 | 18 (20 shield raised) | +9 | +6 | +4 | +6 (low-light) | 25 | Athletics +7; Survival, Nature, Stealth, Medicine, Intimidation, Acrobatics +4 |
| Kelda Vornshield | −1 | the Last Witness — knowing | 13 | 13 | +3 | +5 | +9 | +7 (darkvision) | 20 | four Lores +13, Society +9 |

## Resources per character

| Character | Hero Points | Focus | Spell slots | Signature consumables |
|---|---|---|---|---|
| Shavi Beifong | 1 | 1 (Gravity Weapon) | — | caltrops, 5 pints oil |
| Kelda Vornshield | — | — | — | — |

## Who is run by whom

| Character | Controlled by | Status |
|---|---|---|
| Shavi Beifong | player | full PC |
| Kelda Vornshield | GM | sidekick |

## Reactions available

The GM checks this list before resolving any trigger. Forgetting to offer a reaction is the
most common way an automated GM quietly shortchanges a player.

| Character | Reaction | Trigger | Notes |
|---|---|---|---|
| Shavi Beifong | none at level 1 | — | shield can be raised; no Shield Block |
| Kelda Vornshield | none | — | |


## Build notes (character entered into `state.json` 2026-10-12 — full sheet `characters/shavi-beifong.md`)

The player has a level-1 Pathbuilder build in flight. **Not added to state yet** — gear is
undecided and one item needs stripping first. Verified numbers from the export:

| | |
|---|---|
| Class | **Ranger** (Hunter's Edge: Precision) / **Kineticist** (Single Gate, Earth) — dual class |
| Ancestry | Human, Versatile Human heritage |
| Background | Waste Walker |
| Str/Dex/Con/Int/Wis/Cha | 18 / 12 / 18 / 10 / 12 / 12 |
| HP at level 1 | **31** — 8 ancestry + 10 Ranger + 8 Kineticist + 4 Con + 1 Toughness (dual-class HP stacking, homebrew — `RULES_DELTAS.md`). The export's 19 is the published higher-of-two figure and is superseded. |
| AC | **18** — 10 + 3 trained + 1 Dex (capped) + 4 armor |
| Saves | Expert Fort, Expert Reflex, **Trained** Will — correct: both classes are trained in Will at 1st; Kineticist's Will Expertise raises it at level 3 |
| Perception | **+6** — the export's +4 is trained; Ranger grants expert |
| Speed | 25 (Str 18 clears Breastplate's Str 16, so no penalty) |
| Focus | 1 point, Gravity Weapon (via Natural Ambition → Initiate Warden) |
| Languages | Common, Dwarven, Petran |

### Settled 2026-10-11

- **Calling and Rewrite Fate stripped** from the build. They arrive with mythic at level 2–3.
- **HP 31** confirmed by the player.
- **Breastplate** worn if it fits the 15 gp budget. It does: 8 gp, Bulk 2, Str +3 met by Str 18 so the −5 ft Speed penalty does not apply ([Player Core p.271](https://2e.aonprd.com/Armor.aspx?ID=47)).
- **The post:** hired by the Last Witness as guard and guide into the depths of the range where the Labyrinth is rumoured to be.
- **Gear — the suggested loadout, chosen 2026-10-11.** Prices from Player Core / GM Core via AoN.

  | Item | Price | Bulk |
  |---|---|---|
  | Breastplate (worn) | 8 gp | 2 |
  | Adventurer's Pack (backpack, bedroll, 10 chalk, flint and steel, 50 ft rope, 2 weeks' rations, soap, 5 torches, waterskin) | 1 gp 5 sp | 1 |
  | Hooded lantern | 7 sp | L |
  | Oil, 5 pints | 5 cp | — |
  | Climbing kit | 5 sp | 1 |
  | Grappling hook | 1 sp | L |
  | Wooden shield | 1 gp | 1 |
  | Crowbar | 5 sp | L |
  | Signal whistle | 8 cp | — |
  | Caltrops | 3 sp | L |
  | **Spent** | **12 gp 7 sp 3 cp** | ~5 + 5 L |
  | **Purse** | **2 gp 2 sp 7 cp** | |

- **Gravity Weapon:** house-ruled to work with an Elemental Blast shaped by Weapon Infusion — `RULES_DELTAS.md`.
- **Feats confirmed by the player:** the single gate's two impulse feats are **Armor in Earth** and
  **[Stepping Stones](https://2e.aonprd.com/Feats.aspx?ID=4223)** (Rage of Elements p.26), as
  [Single Gate](https://2e.aonprd.com/Classes.aspx?ID=23) requires. The kineticist class feat is
  **Weapon Infusion**. Initiate Warden via Natural Ambition.
- **Perception corrected +4 → +6.** [Ranger](https://2e.aonprd.com/Classes.aspx?ID=36) starts **expert** in Perception
  (Player Core); dual class takes the better rank. Wis +1 + expert (1 + 4) = +6.

### Gravity Weapon needs a weapon

[Gravity Weapon](https://2e.aonprd.com/Spells.aspx?ID=1863) (Player Core p.383) applies to *"your first weapon Strike each round"*. [Elemental Blast](https://2e.aonprd.com/Actions.aspx?ID=2125) is an impulse attack, not a Strike, and [unarmed attacks are not weapons](https://2e.aonprd.com/Rules.aspx?ID=2191) (Player Core p.275). Without a weapon it does nothing. [Precision](https://2e.aonprd.com/HuntersEdge.aspx?ID=5) triggers on *"the first time you hit your hunted prey"*, so it **does** work with Elemental Blast.

### Original two items (both now settled)

1. **Strip the Calling and Rewrite Fate.** Mythic is set to arrive at level 2–3, not 1. Per
   [Mythic Progression](https://2e.aonprd.com/Rules.aspx?ID=3329), a Calling received after 1st
   level normally brings the lower-level mythic feats with it, so nothing is permanently lost.
2. **Armor in Earth vs. a worn breastplate.** [Armor in Earth](https://2e.aonprd.com/Feats.aspx?ID=4221)
   (Rage of Elements p.26) is 1 action for +4 AC / Dex cap +1 / −2 check, and it **suppresses worn
   armor**. A real breastplate is +4 / +1 / −2 — identical at level 1. So wearing one makes the
   impulse AC-neutral and frees that action; the impulse only starts paying for itself at level 3,
   where it becomes heavy, +5, and bulwark.

### Opening-round action load

Channel Elements, Hunt Prey, Gravity Weapon and Armor in Earth are 1 action each — four, against
three actions plus one Versatile Action. Dropping Armor in Earth (see above) leaves **three**, so
round one is 2 normal + 1 Versatile with **one normal action still free** for a Strike or a Stride.
Online on turn one rather than turn two, and the Versatile Action is what buys it.
