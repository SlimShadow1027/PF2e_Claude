# 12 (D&D 2024) — Rules quick reference

**Replaces `system/12-rules-quick-reference.md` for a campaign with `System: dnd5e`.** Read this
one instead of that one; they disagree on purpose.

The cheat sheet to consult **instead of recalling from memory**. Every table carries a `Source:`
line. Anything that is this framework's own convention rather than a published value says so in
place. Run `python3 tools/dnd5e.py sources` for the full provenance list.

> **Verification note.** The primary source is the **System Reference Document 5.2** ("SRD 5.2"),
> which Wizards of the Coast publishes free of charge under CC-BY-4.0 and which contains the 2024
> core rules. It was read from a complete Markdown transcription of the official PDF
> (`springbov/dndsrd5.2_markdown` @`6a3547c`). Because that transcription is a conversion rather
> than the publisher's own file, **every numeric table was additionally cross-checked against
> `foundryvtt/dnd5e` v6.0.5 @`7bfb3f1`**, an independent implementation. The two agreed on all of
> them: the CR-to-XP table, the cumulative advancement thresholds, the XP-budget-per-character
> table and the coin ratios matched value for value.
>
> **What the SRD does not contain is as important as what it does.** There is no treasure-by-level
> table, no random treasure hoards and no calendar in SRD 5.2 — those are Dungeon Master's Guide
> material or setting material and are not open content. Where this framework needs an answer
> anyway it says it is this framework's, names what published figures it was built from, and
> appears in `CONVENTION_TABLES` so `sources` counts it separately. It does not reconstruct the
> DMG's tables from memory.

**If you have just come from the Pathfinder documents, read `## Six things that are not true here`
at the bottom first.**

---

## D20 Tests

All three kinds — ability checks, saving throws and attack rolls — work the same way:

1. Roll 1d20. With Advantage or Disadvantage, roll two and use the higher or the lower.
2. Add the relevant ability modifier, your Proficiency Bonus if it applies, and any
   circumstantial bonus or penalty.
3. **Meet or beat the target number and it succeeds. Otherwise it fails.** That is the whole
   ladder — there are no degrees of success.

The target number is a **DC** for a check or a save, and an **AC** for an attack roll.

**Source:** SRD 5.2, "Playing the Game" → "D20 Tests".

### Rolling 20 or 1

> *"If you roll a 20 on the d20 (called a 'natural 20') for an attack roll, the attack hits
> regardless of any modifiers or the target's AC. This is called a Critical Hit."*
> *"If you roll a 1 on the d20 (a 'natural 1') for an attack roll, the attack misses regardless of
> any modifiers or the target's AC."*

**Both statements are scoped to attack rolls.** A natural 20 on an ability check or a saving throw
is a 20 and nothing more: it is not an automatic success and it is not a critical anything. The
Ability Checks and Saving Throws sections state no equivalent rule. `tools/roll.py` implements this
by test kind, which is why `attack` is a separate command from `check` and `save`.

**Source:** SRD 5.2, "Playing the Game" → "D20 Tests" → "Attack Rolls" → "Rolling 20 or 1".

### Advantage and Disadvantage

Roll a second d20 and use the higher (Advantage) or the lower (Disadvantage). They do not stack:
any number of sources granting Advantage still means two dice. **If a roll has both, it has
neither** and you roll one d20 — true even if several things impose Disadvantage and only one
grants Advantage. `roll.py --advantage --disadvantage` therefore cancels rather than erroring.

With Advantage or Disadvantage, a reroll effect replaces **one** of the two dice, your choice.

**Source:** SRD 5.2, "Playing the Game" → "D20 Tests" → "Advantage/Disadvantage".

---

## Typical Difficulty Classes

| Task difficulty | DC |
|---|---|
| Very easy | 5 |
| Easy | 10 |
| Medium | 15 |
| Hard | 20 |
| Very hard | 25 |
| Nearly impossible | 30 |

**There is no DC-by-level table in this game.** A hard task is DC 20 at level 1 and DC 20 at level
20. What changes is the character's bonus, not the lock. Scale the opposition, not the obstacle —
and expect high-level characters to walk through mundane difficulties, because that is the design
working, not a bug to patch with inflated DCs.

**Source:** SRD 5.2, "Playing the Game" → "D20 Tests" → "Ability Checks" → "Difficulty Class", the
Typical Difficulty Classes table.

A spell's save DC is **8 + the caster's Proficiency Bonus + their spellcasting ability modifier**.
A monster's stat block states its own.

**Source:** SRD 5.2, "Spells" → "Casting Spells" → "Saving Throws".

---

## Proficiency Bonus

| Level or CR | Bonus |
|---|---|
| up to 4 | +2 |
| 5–8 | +3 |
| 9–12 | +4 |
| 13–16 | +5 |
| 17–20 | +6 |
| 21–24 | +7 |
| 25–28 | +8 |
| 29–30 | +9 |

One column serves both character level and monster Challenge Rating. The bonus is **never added
twice** to the same number, and where something multiplies or divides it (Expertise doubles it),
that happens once each.

**Source:** SRD 5.2, "Playing the Game" → "Proficiency", the Proficiency Bonus table.
Cross-checked against the Character Advancement table, which matches for levels 1–20, and against
`foundryvtt/dnd5e`.

An ability modifier is the score minus 10, halved and rounded down.

---

## The turn

| | |
|---|---|
| **One action** | the main thing you do |
| **Movement** | up to your Speed, in feet, spent in any order around your action |
| **One Bonus Action** | **only when a feature grants one.** It is not a free second action everybody has |
| **One Reaction** | one per round, refreshed at the start of your turn |
| **One free object interaction** | during your move or your action; a second takes the Utilize action |

> *"On your turn, you can move a distance up to your Speed and take one action."*

Movement is its own allowance and does not cost the action — which is the structural difference
from Pathfinder's three-action turn, and the one most likely to be run wrong out of habit. Dash
spends the action to gain movement equal to your Speed again.

The main actions: **Attack, Dash, Disengage, Dodge, Help, Hide, Influence, Magic, Ready, Search,
Study, Utilize**.

**There is no multiple attack penalty.** Extra attacks come from the Attack action's own text and
the Extra Attack feature, and they are made at no penalty. Do not apply a −5.

**Source:** SRD 5.2, "Playing the Game" → "Combat" → "Your Turn" and → "Actions"; "Rules Glossary"
→ "Bonus Action", "Reaction".

---

## Initiative

Everyone rolls a **Dexterity check**. The GM rolls for monsters, and makes **one roll for a group
of identical creatures** so the whole group shares an Initiative. Highest acts first, and the order
holds from round to round.

**Surprise is Disadvantage on the Initiative roll** — not a lost turn, which is the 2014 rule.
A creature caught unawares by combat starting rolls Initiative with Disadvantage and otherwise acts
normally.

**Ties:** the published rule is that the GM decides among tied monsters, the players among tied
characters, and the GM decides a monster-versus-character tie. **This framework rolls ties off with
real dice instead**, so the ordering lands in the audit log rather than being an unlogged GM
choice. That substitution is this framework's convention; `roll.py init` prints the published rule
alongside it, and you can override the order by hand if the player would rather decide.

**Source:** SRD 5.2, "Playing the Game" → "Combat" → "Initiative", including "Surprise" and "Ties";
"Rules Glossary" → "Initiative" (an Initiative *score*, where the GM prefers not to roll, is
10 + Dexterity modifier).

---

## Critical Hits

> *"Roll the attack's damage dice twice, add them together, and add any relevant modifiers as
> normal. For example, if you score a Critical Hit with a Dagger, roll 2d4 for the damage rather
> than 1d4, and add your relevant ability modifier."*

**The dice double. The modifier is added once.** Extra damage dice from features such as Sneak
Attack double as well. `roll.py damage --crit` on a 5.5e campaign rewrites `1d8+4` to `2d8+4`, so
the extra die is genuinely rolled rather than being a doubled total.

This is **not** Pathfinder's rule, where the whole roll including modifiers is doubled. A crit here
is a smaller swing than a crit there.

**Source:** SRD 5.2, "Playing the Game" → "Damage and Healing" → "Critical Hits".

---

## Damage, resistance and vulnerability

- **Resistance** halves damage of that type (round down). **Vulnerability** doubles it.
- Multiple instances of either count as **one**.
- **Order of application:** bonuses, penalties and multipliers first; then Resistance; then
  Vulnerability.
- A save that deals half damage on a success halves the damage that a failure would have dealt,
  rounding down.
- Damage against several targets at once is rolled **once** for all of them.
- **Immunity** to a damage type means taking none of it; to a condition, not being affected.

The published worked example: Resistance to all damage, Vulnerability to fire, inside an aura
reducing all damage by 5, taking 28 fire → 23 → halved to 11 → doubled to 22.

**Source:** SRD 5.2, "Playing the Game" → "Damage and Healing".

---

## Hit Points, 0 HP, and death

**Bloodied** is half Hit Points or fewer. It has no effect of its own; it exists for other rules
to hang off.

### Dropping to 0

A **monster** dies the instant it hits 0, though the GM may treat an individual monster as a
character instead. A **character** falls Unconscious and starts making Death Saving Throws —
unless one of these kills them outright:

- **Massive damage.** Damage that reduces you to 0 with a remainder **equal to or greater than your
  HP maximum** kills you. The published example: a 12 HP maximum character on 6 HP takes 18; 12
  remains, which equals the maximum, so they die.
- **HP maximum reduced to 0.**

`state.py damage` checks the massive-damage case and records the death.

### Death Saving Throws

> *"Whenever you start your turn with 0 Hit Points, you must make a Death Saving Throw."*

- Roll **1d20**, no ability modifier — *"this one isn't tied to an ability score"*. **10 or higher
  succeeds.**
- **Three successes** → Stable. **Three failures** → dead. They need not be consecutive.
- **Natural 20** → regain 1 Hit Point and stop saving. **Natural 1** → counts as **two failures**.
- **Taking damage at 0 HP** is one failure, or **two from a Critical Hit**. Damage equal to or
  above your HP maximum kills you.
- Both counters **reset to zero** on regaining any Hit Points or becoming Stable.

**Stable** means 0 HP and no more Death Saves, still Unconscious. Taking damage ends it and the
saves resume. An unhealed Stable creature regains 1 HP after **1d4 hours**.

**Stabilising someone** is the Help action and a successful **DC 10 Wisdom (Medicine)** check.

**Knocking out** instead of killing: when a melee attack would reduce a creature to 0, you may
leave it on 1 HP with the Unconscious condition. It then starts a Short Rest, and the condition
ends at the end of it, early on any healing or on first aid (DC 10 Wisdom (Medicine)).

**Source:** SRD 5.2, "Playing the Game" → "Damage and Healing" → "Dropping to 0 Hit Points",
"Death Saving Throws", "Stabilizing a Character", and the "Knocking out a Creature" sidebar;
"Rules Glossary" → "Dead", "Stable".

### Temporary Hit Points

Lost **first** when you take damage. They do **not** stack — receiving more, you choose which set
to keep, you do not add them. They are not Hit Points and not healing: healing cannot restore them,
and receiving them at 0 HP does **not** restore consciousness. They last until spent or until you
finish a Long Rest.

---

## Concentration

Some effects need it. It ends when:

- **You start another Concentration effect.** The moment you begin casting it, not when it lands.
- **You take damage** and fail a **Constitution saving throw**. The DC is **10, or half the damage
  taken (round down), whichever is higher, to a maximum of 30.**
- **You gain the Incapacitated condition, or you die.**

```
python3 tools/state.py --campaign X concentration start thorne "Hunter's Mark"
python3 tools/state.py --campaign X concentration check thorne 23     # prints the DC
```

**Source:** SRD 5.2, "Rules Glossary" → "Concentration".

---

## Cover

| Degree | Benefit |
|---|---|
| Half | +2 to AC and Dexterity saving throws |
| Three-quarters | +5 to AC and Dexterity saving throws |
| Total | cannot be targeted directly |

Behind more than one degree, only the most protective applies.

**Source:** SRD 5.2, "Rules Glossary" → "Cover".

---

## The fifteen conditions

The published list is exactly these. **A condition does not stack with itself** — you either have
it or you do not. **Exhaustion is the single exception**, and the only one that carries a value.

The text below is **quoted**, because the exact wording is what makes a condition adjudicable and
paraphrasing it would reintroduce the recalled-from-memory error this framework exists to prevent.

**Source:** SRD 5.2, "Rules Glossary" → "Condition" and the fifteen `[Condition]` entries.

### Blinded
- **Can't See.** You can't see and automatically fail any ability check that requires sight.
- **Attacks Affected.** Attack rolls against you have Advantage, and your attack rolls have
  Disadvantage.

### Charmed
- **Can't Harm the Charmer.** You can't attack the charmer or target the charmer with damaging
  abilities or magical effects.
- **Social Advantage.** The charmer has Advantage on any ability check to interact with you
  socially.

### Deafened
- **Can't Hear.** You can't hear and automatically fail any ability check that requires hearing.

### Exhaustion
- **Exhaustion Levels.** This condition is cumulative. Each time you receive it, you gain 1
  Exhaustion level. **You die if your Exhaustion level is 6.**
- **D20 Tests Affected.** When you make a D20 Test, the roll is reduced by **2 times** your
  Exhaustion level.
- **Speed Reduced.** Your Speed is reduced by **5 times** your Exhaustion level, in feet.
- **Removing Exhaustion Levels.** Finishing a Long Rest removes 1 level. At 0 the condition ends.

This is the 2024 rewrite: one scaling penalty to every D20 Test, not the 2014 table of six
distinct effects. Levels 1 to 6 are therefore −2/−5 ft, −4/−10 ft, −6/−15 ft, −8/−20 ft,
−10/−25 ft, and death.

### Frightened
- **Ability Checks and Attacks Affected.** You have Disadvantage on ability checks and attack rolls
  while the source of fear is within line of sight.
- **Can't Approach.** You can't willingly move closer to the source of fear.

### Grappled
- **Speed 0.** Your Speed is 0 and can't increase.
- **Attacks Affected.** You have Disadvantage on attack rolls against any target other than the
  grappler.
- **Movable.** The grappler can drag or carry you when it moves, but every foot of movement costs
  it 1 extra foot unless you are Tiny or two or more sizes smaller than it.

### Incapacitated
- **Inactive.** You can't take any action, Bonus Action, or Reaction.
- **No Concentration.** Your Concentration is broken.
- **Speechless.** You can't speak.
- **Surprised.** If you're Incapacitated when you roll Initiative, you have Disadvantage on the
  roll.

### Invisible
- **Surprise.** If you're Invisible when you roll Initiative, you have Advantage on the roll.
- **Concealed.** You aren't affected by any effect that requires its target to be seen unless the
  effect's creator can somehow see you. Any equipment you are wearing or carrying is also
  concealed.
- **Attacks Affected.** Attack rolls against you have Disadvantage, and your attack rolls have
  Advantage. If a creature can somehow see you, you don't gain this benefit against that creature.

### Paralyzed
- **Incapacitated.** You have the Incapacitated condition.
- **Speed 0.** Your Speed is 0 and can't increase.
- **Saving Throws Affected.** You automatically fail Strength and Dexterity saving throws.
- **Attacks Affected.** Attack rolls against you have Advantage.
- **Automatic Critical Hits.** Any attack roll that hits you is a Critical Hit if the attacker is
  within 5 feet of you.

### Petrified
- **Turned to Inanimate Substance.** You are transformed, along with any nonmagical objects you are
  wearing and carrying, into a solid inanimate substance (usually stone). Your weight increases by
  a factor of ten, and you cease aging.
- **Incapacitated.** You have the Incapacitated condition.
- **Speed 0.** Your Speed is 0 and can't increase.
- **Attacks Affected.** Attack rolls against you have Advantage.
- **Saving Throws Affected.** You automatically fail Strength and Dexterity saving throws.
- **Resist Damage.** You have Resistance to all damage.
- **Poison Immunity.** You have Immunity to the Poisoned condition.

### Poisoned
- **Ability Checks and Attacks Affected.** You have Disadvantage on attack rolls and ability checks.

### Prone
- **Restricted Movement.** Your only movement options are to crawl or to spend an amount of
  movement equal to half your Speed (round down) to right yourself and thereby end the condition.
  If your Speed is 0, you can't right yourself.
- **Attacks Affected.** You have Disadvantage on attack rolls. An attack roll against you has
  Advantage if the attacker is within 5 feet of you. Otherwise, that attack roll has Disadvantage.

### Restrained
- **Speed 0.** Your Speed is 0 and can't increase.
- **Attacks Affected.** Attack rolls against you have Advantage, and your attack rolls have
  Disadvantage.
- **Saving Throws Affected.** You have Disadvantage on Dexterity saving throws.

### Stunned
- **Incapacitated.** You have the Incapacitated condition.
- **Saving Throws Affected.** You automatically fail Strength and Dexterity saving throws.
- **Attacks Affected.** Attack rolls against you have Advantage.

### Unconscious
- **Inert.** You have the Incapacitated and Prone conditions, and you drop whatever you're holding.
  When this condition ends, you remain Prone.
- **Speed 0.** Your Speed is 0 and can't increase.
- **Attacks Affected.** Attack rolls against you have Advantage.
- **Saving Throws Affected.** You automatically fail Strength and Dexterity saving throws.
- **Automatic Critical Hits.** Any attack roll that hits you is a Critical Hit if the attacker is
  within 5 feet of you.
- **Unaware.** You're unaware of your surroundings.

---

## Rests

| | Short Rest | Long Rest |
|---|---|---|
| Length | 1 hour | at least 8 hours — at least 6 asleep, no more than 2 of light activity |
| Hit Points | spend Hit Dice | **all** restored |
| Hit Dice | — | **all** spent dice restored |
| Spell slots | **no** — only features whose own text says so | restored |
| Exhaustion | — | **one level removed** |
| Ability scores, HP maximum | — | restored if reduced |
| Interrupted by | rolling Initiative, casting a non-cantrip spell, taking damage | the same, plus an hour of physical exertion |
| If interrupted | **confers no benefits** | resumable, with one extra hour per interruption; and an hour already rested gives the Short Rest benefit |

You must have at least 1 Hit Point to start either. After finishing a Long Rest you must wait at
least **16 hours** before starting another.

**Spending Hit Dice:** roll one, add your Constitution modifier, regain that many HP (minimum 1).
You decide whether to spend another after each roll. The roll is a real roll —
`state.py hit-dice spend` prints the expression and `heal` applies the total.

**Source:** SRD 5.2, "Rules Glossary" → "Short Rest" and "Long Rest".

---

## Heroic Inspiration

> *"If you have Heroic Inspiration, you can expend it to reroll any die immediately after rolling
> it, and you must use the new roll."*

**Binary — you have it or you do not, and it does not stack.** Gaining it while already holding it
means it is lost unless you pass it to a player character who lacks it. The GM awards it for
"something particularly heroic, in character, or entertaining". A Human character starts each day
with it.

Note it rerolls **any die**, not only a d20, and the new roll stands.

**Source:** SRD 5.2, "Playing the Game" → "D20 Tests" → the Heroic Inspiration sidebar;
"Rules Glossary" → "Heroic Inspiration".

---

## Carrying capacity

| Size | Carry | Drag / lift / push |
|---|---|---|
| Tiny | Str × 7.5 lb | Str × 15 lb |
| Small / Medium | Str × 15 lb | Str × 30 lb |
| Large | Str × 30 lb | Str × 60 lb |
| Huge | Str × 60 lb | Str × 120 lb |
| Gargantuan | Str × 120 lb | Str × 240 lb |

The multiplier is on the Strength **score**, not the modifier. Dragging, lifting or pushing above
your carry maximum caps your Speed at 5 feet.

**Fifty coins weigh a pound**, and `state.py` counts the purse against the party's carried weight.

**What is absent matters:** SRD 5.2 defines **no intermediate "encumbered" band**. You carry freely
up to the maximum. Pathfinder has such a band; this game does not, and `carry_report` reports none
rather than inventing one. The optional variant encumbrance rule is not SRD content.

**Source:** SRD 5.2, "Rules Glossary" → "Carrying Capacity".

---

## Coins

| Coin | Value in gp | In copper |
|---|---|---|
| cp | 1/100 | 1 |
| sp | 1/10 | 10 |
| **ep** | 1/2 | 50 |
| gp | 1 | 100 |
| pp | 10 | 1,000 |

**Electrum is the difference from Pathfinder's four coins**, and it is why a purse cannot be
copied across rulesets. `state.py gold` refuses `ep` on a Pathfinder campaign by name.

**Source:** SRD 5.2, "Equipment" → "Coins", the Coin Values table. Cross-checked against
`foundryvtt/dnd5e`.

---

## Magic items

| Rarity | Value | Where it can be bought |
|---|---|---|
| Common | 100 gp | often in a town or city |
| Uncommon | 400 gp | usually only in cities |
| Rare | 4,000 gp | usually only in cities |
| Very rare | 40,000 gp | only in wondrous locations, such as a city on another plane |
| Legendary | 200,000 gp | only in wondrous locations |
| Artifact | priceless | not for sale; unique and difficult to acquire |

Halve the value for a consumable other than a Spell Scroll. Where a magic item incorporates a
mundane item, add that item's cost — *+1 Armor* (Plate) is 4,000 + 1,500 = 5,500 gp.

**Attunement:** a creature can be attuned to **no more than three** magic items at a time. (A
Rogue's level 13 Use Magic Device raises that character's own limit to four; `state.py` stores the
limit per character so a feature like that is recorded rather than hardcoded away.)

**Source:** SRD 5.2, "Magic Items" → "Magic Item Rarity"; "Rules Glossary" → "Attunement".

---

## Travel

| Pace | Per minute | Per hour | Per day | Effect |
|---|---|---|---|---|
| Fast | 400 ft | 4 miles | 30 miles | Disadvantage on Wisdom (Perception or Survival) and Dexterity (Stealth) |
| Normal | 300 ft | 3 miles | 24 miles | Disadvantage on Dexterity (Stealth) |
| Slow | 200 ft | 2 miles | 18 miles | **Advantage** on Wisdom (Perception or Survival) |

An 8-hour travel day. Each hour beyond 8 needs a Constitution save at **DC 10 + 1 per hour past 8**
or costs an Exhaustion level. Mounts double the distance for one hour, then need a rest. A good
road raises the maximum pace one step; the group moves at Slow if any member's Speed is halved.

| Terrain | Max pace | Encounter distance | Forage | Navigate | Search |
|---|---|---|---|---|---|
| Arctic | Fast | 6d6 × 10 ft | 20 | 10 | 10 |
| Coastal | Normal | 2d10 × 10 ft | 10 | 5 | 15 |
| Desert | Normal | 6d6 × 10 ft | 20 | 10 | 10 |
| Forest | Normal | 2d8 × 10 ft | 10 | 15 | 15 |
| Grassland | Fast | 6d6 × 10 ft | 15 | 5 | 15 |
| Hill | Normal | 2d10 × 10 ft | 15 | 10 | 15 |
| Mountain | Slow | 4d10 × 10 ft | 20 | 15 | 20 |
| Swamp | Slow | 2d8 × 10 ft | 10 | 15 | 20 |
| Underdark | Normal | 2d6 × 10 ft | 20 | 10 | 20 |
| Urban | Normal | 2d6 × 10 ft | 20 | 15 | 15 |

**Source:** SRD 5.2, "Playing the Game" → "Exploration" → "Travel Pace", and "Gameplay Toolbox" →
"Travel Pace" (the Travel Terrain table, Extended Travel, Good Roads, Slower Travelers).

`python3 tools/dnd5e.py travel --terrain swamp`

---

## Advancement

| Level | XP (cumulative) | Prof. | Tier |
|---|---|---|---|
| 1 | 0 | +2 | 1 |
| 2 | 300 | +2 | 1 |
| 3 | 900 | +2 | 1 |
| 4 | 2,700 | +2 | 1 |
| 5 | 6,500 | +3 | 2 |
| 6 | 14,000 | +3 | 2 |
| 7 | 23,000 | +3 | 2 |
| 8 | 34,000 | +3 | 2 |
| 9 | 48,000 | +4 | 2 |
| 10 | 64,000 | +4 | 2 |
| 11 | 85,000 | +4 | 3 |
| 12 | 100,000 | +4 | 3 |
| 13 | 120,000 | +5 | 3 |
| 14 | 140,000 | +5 | 3 |
| 15 | 165,000 | +5 | 3 |
| 16 | 195,000 | +5 | 3 |
| 17 | 225,000 | +6 | 4 |
| 18 | 265,000 | +6 | 4 |
| 19 | 305,000 | +6 | 4 |
| 20 | 355,000 | +6 | 4 |

**XP is cumulative and the counter is never reset** — the opposite of Pathfinder's flat 1,000 per
level. A level 5 character has at least 6,500 XP on the sheet, and the gaps between levels grow.

Past level 20, a GM may award one feat per **30,000 XP** above 355,000.

**Source:** SRD 5.2, "Character Creation" → "Level Advancement", the Character Advancement table,
and the "Bonus Feats at Level 20" sidebar. Cross-checked against `foundryvtt/dnd5e`.

### Hit Points per level

| Class | Hit Die | Fixed HP per level |
|---|---|---|
| Barbarian | d12 | 7 + Con |
| Fighter, Paladin, Ranger | d10 | 6 + Con |
| Bard, Cleric, Druid, Monk, Rogue, Warlock | d8 | 5 + Con |
| Sorcerer, Wizard | d6 | 4 + Con |

Roll the die or take the fixed value, your choice each level. At level 1 you take the die's full
value. A Constitution modifier increase raises your maximum by 1 **per level you have attained**.

---

## Monsters

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

**A creature's XP does not vary with the party's level** — unlike Pathfinder, where creature XP is
read off the difference between the two. CR summarises the threat to a party of **four**.

**Source:** SRD 5.2, "Monsters" → "Experience Points", the Experience Points by Challenge Rating
table. Cross-checked against `foundryvtt/dnd5e` (whose array omits the three fractional rows).

`python3 tools/dnd5e.py cr --cr 1/4 5 30`

---

## Lifestyle expenses

Wretched free · Squalid 1 sp/day · Poor 2 sp/day · Modest 1 gp/day · Comfortable 2 gp/day ·
Wealthy 4 gp/day · Aristocratic 10 gp/day.

*"Lifestyles have no inherent consequences, but the GM might take them into account when
determining risks or how others perceive your character."*

**Source:** SRD 5.2, "Equipment" → "Lifestyle Expenses".

---

## Six things that are not true here

If you have been running the Pathfinder side of this framework, these are the habits most likely
to come across with you. Each one is wrong in this game.

1. **There are no degrees of success.** Beating a DC by 12 is a success, the same as beating it by
   1. Do not narrate a "critical success" on a skill check and do not apply a bonus for it.
2. **A natural 20 on a check or a save is just a 20.** The auto-success and critical rules are
   attack rolls only.
3. **DCs do not scale with level.** There is no DC-by-level table to reach for, and raising DCs to
   "keep up" with a high-level party is houseruling, not running the game.
4. **A turn is one action, not three** — and moving does not cost it. A Bonus Action is not a
   standing third action; it exists only where a feature grants it.
5. **There is no multiple attack penalty**, and there is no encounter multiplier for monster count
   either. The 2024 budget is spent at face value.
6. **A critical hit doubles the dice, not the total.** The modifier is added once.

And one that goes the other way: **0 HP is survivable differently.** There is no wounded value
accumulating across the session, but there *is* massive damage, which kills with no saving throw at
all. A character on 6 of 12 HP is one big hit from dead, not from dying 1.
