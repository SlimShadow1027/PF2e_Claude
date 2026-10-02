# 09 (D&D 2024) — Loot and the economy

**Replaces `system/09-loot-and-economy.md` for a campaign with `System: dnd5e`.**

> **Read this first.** SRD 5.2 contains **no treasure-by-level table and no random treasure
> hoards.** The 2024 treasure tables are Dungeon Master's Guide material and were not released as
> open content. This framework will not reconstruct them from memory, so what follows is built from
> the published figures that *do* exist and is **labelled as this framework's convention** wherever
> it goes beyond them. `python3 tools/dnd5e.py sources` counts those separately from the quoted
> rules. If you own the 2024 DMG, use its tables and record the deviation in `RULES_DELTAS.md`.
>
> This is the largest gap between the two rulesets in this framework. The Pathfinder side has an
> exact per-level allotment with item counts and item levels; here there is a floor and a pacing
> judgement. Say so to the player if treasure pacing comes up.

---

## What is published

### Magic item values and where they sell

| Rarity | Value | Where it can be bought |
|---|---|---|
| Common | 100 gp | often in a town or city |
| Uncommon | 400 gp | usually only in cities |
| Rare | 4,000 gp | usually only in cities |
| Very rare | 40,000 gp | only in wondrous locations, such as a city on another plane |
| Legendary | 200,000 gp | only in wondrous locations |
| Artifact | priceless | not for sale; unique and difficult to acquire |

Halve the value for a consumable other than a Spell Scroll, whose value is double its scribing
cost. Where a magic item incorporates a mundane item, add that item's cost.

**Source:** SRD 5.2, "Magic Items" → "Magic Item Rarity".

### Wealth assumed at a level

The starting-equipment-at-higher-levels table, which is the only published statement of what a
character of a given level should have:

| Starting level | Money | Magic items |
|---|---|---|
| 2–4 | normal starting equipment | 1 common |
| 5–10 | 500 gp + 1d10 × 25 gp | 1 common, 1 uncommon |
| 11–16 | 5,000 gp + 1d10 × 250 gp | 2 common, 3 uncommon, 1 rare |
| 17–20 | 20,000 gp + 1d10 × 250 gp | 2 common, 4 uncommon, 3 rare, 1 very rare |

**Source:** SRD 5.2, "Character Creation" → "Starting at Higher Levels" → "Starting Equipment".

### Coins and attunement

pp 10 gp · gp 1 · **ep ½ gp** · sp 1/10 gp · cp 1/100 gp. **Fifty coins weigh a pound.**

**Attunement: no more than three magic items at a time.** This is the real constraint on magic
items in this game — not their cost. A character with six attunement items has three they cannot
use, which makes the fourth interesting item a *choice* rather than an upgrade. Treat the limit as
a design feature when deciding what to hand out.

```
python3 tools/state.py --campaign X attune add thorne "Cloak of Protection"
python3 tools/state.py --campaign X attune list thorne
```

---

## Treasure pacing — this framework's convention

Since there is no published budget, pace by **tier** and check against the floor.

```
python3 tools/dnd5e.py treasure --level 7 --party-size 1
```

| Tier | Levels | What treasure is for |
|---|---|---|
| 1 | 1–4 | Coins that matter. A single common item is a real event. Equipment is still a decision |
| 2 | 5–10 | The first uncommon items. Consumables are the main currency of survival |
| 3 | 11–16 | Rares appear; attunement starts to bind. Money stops being a constraint on gear |
| 4 | 17–20 | Very rares and legendaries, one at a time, each with a history |

Four pacing rules, all this framework's:

1. **Check the floor at each level-up, not each session.** If the character is well under the band
   above, they are under-equipped by the game's own assumption. If they are over it, nothing is
   broken — see below.
2. **Bounded accuracy means being behind matters less here.** There is no item-bonus curve the
   maths assumes, so a character two items short is not failing checks they should pass. They have
   fewer *options*, which is a pacing problem rather than a correctness problem. Do not panic-grant.
3. **Prefer consumables early and permanents late.** A potion solves a solo character's worst
   problem (nobody to heal them) without permanently raising their numbers.
4. **Make attunement the interesting constraint.** Hand out a fourth attunement item deliberately,
   as a decision, not as a reward.

### Party size

The published figures are per character, so a solo character's floor is one character's worth.

**Do not import the Pathfinder rule here.** That framework's treasure table is a party allotment
that a small party splits fewer ways, and it has a specific published adjustment for party size.
This game's figures are per character already, so multiplying them by one is the whole adjustment.
A solo character does not get four characters' treasure.

---

## The treasure-pacing tracker

Keep it in `campaigns/<slug>/logs/loot.md`, one line per award:

```
| Session | Level | What | Rarity | Value | Running total |
|---|---|---|---|---|---|
| 3 | 2 | Potion of Healing ×2 | common (consumable) | 100 gp | 340 gp |
| 4 | 3 | coin from the sump | — | 180 gp | 520 gp |
| 6 | 4 | Cloak of Protection | uncommon | 400 gp | 920 gp |
```

At each level-up, compare the running total against the floor for the band and **say what it shows**
— including "you are ahead of the curve and I am going to slow down", which is a more useful thing
to tell a player than silence.

---

## What can be bought where

The published guidance is about **place**, not a number:

> *"Common magic items can often be bought in a town or city. Uncommon and Rare magic items are
> usually found only in cities, and rarer magic items might be sold only in wondrous locations,
> such as a city on another plane of existence."*

This framework reads that as a lookup. **The settlement buckets are this framework's; the
rarity-to-place mapping behind them is published.**

| Settlement | Buys up to |
|---|---|
| village | common |
| town | common |
| city | rare |
| metropolis | rare |
| wondrous location | legendary |

```
python3 tools/dnd5e.py settlement city
```

In a shared world, `worlds/<slug>/GAZETTEER.md` records this **alongside** Pathfinder's numeric
item level for each settlement, in its own column. The two were picked independently from the place
as described — see `23-cross-system-worlds.md` for why deriving one from the other would be a guess
wearing a source's clothes.

Mundane equipment is in the SRD's "Equipment" chapter with prices; look it up rather than
estimating.

---

## Buying and selling

- **Selling magic items is not a published market.** The rarity values are what a buyer might pay
  *if you allow buying and selling at all* — the SRD says so explicitly, and notes *"a seller might
  ask for a service rather than coin as payment"*. Deciding there is no open market is a legitimate
  and often better campaign choice. Say which you have decided.
- **Mundane gear** sells for whatever the campaign has established. Half price is a common
  convention and is not published; if you use it, say it is a convention.
- **A service instead of coin** is published guidance and is almost always the better scene.

```
python3 tools/state.py --campaign X gold spend "40gp"
python3 tools/state.py --campaign X item add "Potion of Healing" 2 --weight 0.5 --owner thorne --kind consumable
```

---

## Weight, not Bulk

Carried weight is in **pounds** against a single capacity of Strength **score** × 15 lb at
Small or Medium. `state.py item add --weight`, and `--bulk` is refused on this ruleset by name.

**There is no intermediate "encumbered" band in SRD 5.2.** You carry freely up to the maximum.
Pathfinder has such a band; reporting one here would be inventing a rule. `carry_report` reports
the capacity and whether it is exceeded, and nothing in between.

Fifty coins weigh a pound, and the purse counts.

---

## Crafting, scribing and downtime income

The SRD publishes crafting rules for nonmagical items, brewing Potions of Healing, scribing Spell
Scrolls and crafting magic items, plus lifestyle expenses. **It publishes no Earn Income table** —
that is a Pathfinder mechanism with no 2024 equivalent in open content.

- **Lifestyle expenses** are published: wretched free, squalid 1 sp/day, poor 2 sp/day, modest
  1 gp/day, comfortable 2 gp/day, wealthy 4 gp/day, aristocratic 10 gp/day. They have no inherent
  consequences, *"but the GM might take them into account when determining risks or how others
  perceive your character"* — which is the hook worth using.
- **Downtime work for money** has no published rate here. If the campaign needs one, invent it,
  write it in `RULES_DELTAS.md` as a house rule, and keep it modest — a solo character with a
  reliable income stream has solved the only resource pressure the early game has.

See `10-downtime-travel-and-rest.md` for the downtime procedure itself.
