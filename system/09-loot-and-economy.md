# 09 — Loot and the economy

```
python3 tools/pf2e.py treasure --level 5 --party-size 1
python3 tools/pf2e.py tables treasure
python3 tools/pf2e.py tables earn-income
python3 tools/pf2e.py tables item-bonuses
```

---

## Treasure by level

**Verified.** `python3 tools/pf2e.py tables treasure` prints all twenty rows of GM Core's Table
6-1: Party Treasure by Level, and `treasure --level N --party-size M` reads one row three ways.

The published guidance is **not a percentage split** — that was this framework's earlier guess and
it was wrong. Each level names how many permanent items and consumables to hand out **and at which
item levels**, plus a currency figure and a per-additional-PC currency column. Level 5, for
example, is four permanent items (two at level 6, two at level 5), six consumables (two each at
levels 6, 5 and 4) and 320 gp, totalling 1,350 gp for four characters.

The item levels are the part that matters more than the total: a hoard of the right gp value made
entirely of level-1 items leaves the character behind the curve anyway.

**Source:** GM Core p.59, Table 6-1 — <https://2e.aonprd.com/Rules.aspx?ID=2656>. The
per-encounter and extra-treasure columns are GM Core p.77, Table 10-3 —
<https://2e.aonprd.com/Rules.aspx?ID=2715>.

### Party size, and why a small party gets more than its share

The book addresses this directly, and it does **not** say to scale linearly:

> GM Core p.61: for each character ABOVE four, add one permanent item of the party's level or one higher, two consumables (usually one at level and one at +1), and the Currency per Additional PC figure. For each character BELOW four you may subtract the same amount — but the book says outright: 'since the game is inherently more challenging with a smaller group that can't cover all roles as efficiently, you might consider subtracting less treasure and allowing the extra gear help compensate for the smaller group size.'

**Source:** GM Core p.61, Different Party Sizes — <https://2e.aonprd.com/Rules.aspx?ID=2661>.

So `pf2e.py treasure` offers three readings of every row and refuses to pick for you: the
published four-character figure, the strict subtraction, and half the subtraction — the gentler
reading the rule invites. Decide once, write it in `RULES_DELTAS.md`, and keep `logs/loot.md`
measured against the same choice. At a party of one the strict reading is brutal: level 5 becomes
one permanent item, no consumables and 80 gp.

---

## The treasure-pacing tracker

`logs/loot.md` compares what has actually been awarded against the expected curve, so the party
neither outpaces nor falls behind the math.

| Level | Expected total (gp) | Awarded so far (gp) | Difference | Verdict |
|---|---|---|---|---|

Check it at every level-up, and act on it:

- **Behind by more than about 25%** — the character will feel a flat competence gap, not a hard
  night. Put a permanent item in the next hoard, at an item level of the party level or one
  above.
- **Ahead by more than about 25%** — the next few encounters will read as easy for reasons that
  have nothing to do with how they were built. Shift toward consumables and currency.

The item-bonus curve in `12-rules-quick-reference.md` is what this is really tracking: a
character who is two levels behind on attack potency misses about 10% more often at every
attack, forever, and will read that as bad luck.

---

## What can be bought where

This is the one place the earlier version of this file was not merely unverified but wrong in
kind: there is **no published table of item levels by settlement size**. The published rule is
that a settlement has a **level**, and:

> a character can usually purchase any common item ... that's of the same or lower level than the
> settlement's

with **fewer of the highest-level items** available — use the Permanent Items and Consumables
columns of Table 6-1 for a level **one lower** than the settlement's as a guide to how many.
Selling works the same way. A character of higher level than the settlement can leverage
influence for a **special order**, which costs time the GM sets.

```
python3 tools/pf2e.py settlement --level 6
```

**Source:** GM Core p.168, Marketplaces — <https://2e.aonprd.com/Rules.aspx?ID=3003>.

The size names below are **this framework's own suggestion** for picking that level, not a quoted
table:

| Settlement | Suggested level |
|---|---|
| Village | 2 |
| Town | 6 |
| City | 10 |
| Metropolis | 14 |
| Capital / planar market | 20 |

**Set the level explicitly per settlement in `WORLD.md`** and say that is where it came from. What
can be bought where is one of the few economic facts a player will plan around, so it should be
decided rather than improvised.

---

## Runes and their costs

A weapon or armour's item bonus comes from its **potency** rune; its extra damage dice from
**striking** (weapons) or its save bonus from **resilient** (armour); a shield's from
**reinforcing**. Property runes add everything else, and the number a weapon or armour can hold
equals the value of its potency rune — striking and resilient are fundamental and do not count
against that limit.

An item's level is the **highest** level among the base item and every rune on it.

### Etching

Etching follows the **Craft** activity: you must be able to Craft magic items, hold the item
throughout, and you can etch only one rune at a time. The rune does nothing until the Craft
completes.

The published upgrade paths, with their prices and the level at which each becomes legal:

| Starting weapon | Improved to | Price and process |
|---|---|---|
| +1 weapon | +1 striking weapon | 65 gp to etch striking (4th level) |
| +1 striking weapon | +2 striking weapon | 900 gp to etch +2 weapon potency (10th level) |
| +2 striking weapon | +2 greater striking weapon | 1,000 gp to etch greater striking (12th level) |
| +2 greater striking weapon | +3 greater striking weapon | 8,000 gp to etch +3 weapon potency (16th level) |
| +3 greater striking weapon | +3 major striking weapon | 30,000 gp to etch major striking (19th level) |

| Starting armour | Improved to | Price and process |
|---|---|---|
| +1 armor | +1 resilient armor | 340 gp to etch resilient (8th level) |
| +1 resilient armor | +2 resilient armor | 900 gp to etch +2 armor potency (11th level) |
| +2 resilient armor | +2 greater resilient armor | 3,100 gp to etch greater resilient (14th level) |
| +2 greater resilient armor | +3 greater resilient armor | 19,500 gp to etch +3 armor potency (18th level) |
| +3 greater resilient armor | +3 major resilient armor | 46,000 gp to etch major resilient (20th level) |

### Transferring

**Transferring a rune costs 10% of the rune's Price, not half**, and takes **1 day instead of the
4 days a Craft normally needs**. The Crafting DC comes from the item level of the rune being
moved. Transferring **from a runestone is free**. Swapping a pair uses the higher level and the
higher Price of the two, and the two runes must both be fundamental or both be property runes.

Move a potency rune off an item and its property runes go **dormant** until the item has a potency
rune again — they are not lost.

**Source:** GM Core p.225, The Etching Process and Transferring Runes —
<https://2e.aonprd.com/Rules.aspx?ID=3165> and <https://2e.aonprd.com/Rules.aspx?ID=3166>. The two
upgrade tables are GM Core p.225, Armor & Armaments —
<https://2e.aonprd.com/Rules.aspx?ID=3161>.

The **curve** the runes are there to keep up with is verified too:
`python3 tools/pf2e.py tables item-bonuses`. The etching levels above line up with it — weapon
potency at 2/10/16, striking at 4/12/19, armour potency at 5/11/18, resilient at 8/14/20.

---

## Buying and selling

- **Buying** at full Price, where the settlement's level allows it —
  `python3 tools/pf2e.py settlement --level N`.
- **Selling** at **half** the item's Price. A specialist buyer, a Diplomacy or Society check, or
  an interested collector can improve it — that is a scene, not a table.
- **Coins, gems, art objects and raw materials are the exception: they exchange at their full
  Price.** This is the reason a hoard of art objects is worth twice a hoard of swords, and it is
  worth saying out loud when the player is deciding what to carry out.
- Selling a **consumable** or a common item is usually not worth the scene; just take the half.

**Source:** Player Core p.267, Price — <https://2e.aonprd.com/Rules.aspx?ID=2146>, quoting:
*"Most items can be sold for half their Price, but coins, gems, art objects, and raw materials
(such as components for the Craft activity) can be exchanged for their full Price."*

---

## Crafting and Earn Income

### Earn Income

Verified. `python3 tools/pf2e.py tables earn-income` prints the full table: income per day by
task level and proficiency, plus the failure row.

The procedure: find a task at a level you can attempt, roll the relevant skill against that
level's DC, and earn the per-day figure for your proficiency rank for the number of days
committed. A critical success earns at the next proficiency rank's rate. A failure earns the
failure row. A critical failure earns nothing and may cost the job.

**Source:** Player Core, Earn Income. Verified against the Foundry VTT PF2e implementation.

### Crafting

Crafting an item takes **4 days** of work, and the crafter must supply **raw materials worth at
least half the item's Price**. Each additional day of work after that reduces the remaining cost
by the Earn Income rate for your level and proficiency. The other published requirements:

- Your level must be **at least the item's level**.
- **9th level or higher** items need **master** in Crafting; **16th or higher** need **legendary**.
- You need the **formula** for anything uncommon or rarer.
- You need appropriate **tools**, and often a **workshop**.
- Alchemical items need **Alchemical Crafting**; magic items need **Magical Crafting**.

**Source:** GM Core p.223, Crafting Items — <https://2e.aonprd.com/Rules.aspx?ID=3157>, for the
requirements and the half-Price materials; the 4-day figure is quoted in GM Core p.225 under
Transferring Runes (*"1 day (instead of the 4 days usually needed to Craft)"*).

For long stretches, use the downtime procedure in `10-downtime-travel-and-rest.md` so weeks
resolve in a few exchanges.
