# 09 (D&D 4e) — Treasure, money and carrying

**Replaces `system/09-loot-and-economy.md` for a campaign with `System: dnd4e`.**

> **Two of the three numeric tables here are yours to supply.** 4e's treasure parcels and its
> magic-item prices by level are both non-open content. `dnd4e.py treasure` and
> `settlement_availability` **refuse to compute** until `treasure_parcels` and
> `magic_item_prices` are filled in `tools/dnd4e_tables.json`, and name the book when they
> refuse. The coin ratios and carrying capacity below are mechanics, stated in this framework's
> own words. See `system/dnd4e/README.md`.

---

## Coins: the ratio that is not the other games'

| | |
|---|---|
| 10 cp | = 1 sp |
| 10 sp | = 1 gp |
| **100 gp** | **= 1 pp** |

**One hundred gold to a platinum, not ten.** Both sibling rulesets use ten. A purse carried
across rulesets is therefore wrong even where the coin names match, which is one of the
clearest small illustrations of why rule 8 exists.

4e also has **astral diamonds**, worth 10,000 gp each. This framework deliberately leaves them
out of the coin set: adding a 10,000-gp denomination to the purse makes every small purchase
unreadable in the ledger. **Record one as an item**, with its value in the note.

D&D 2024, for contrast, has an **electrum** piece that neither 4e nor Pathfinder uses. Three
rulesets, three coin sets.

```
python3 tools/state.py --campaign X gold add 240gp 15sp
python3 tools/state.py --campaign X gold spend 2pp         # = 200 gp here, 20 gp in the siblings
python3 tools/state.py --campaign X item add "Astral diamond (10,000 gp)" \
    --owner verrin-ash --kind permanent --weight 0
```

---

## Treasure comes in parcels

4e does not hand out a lump sum per level. It hands out a **numbered set of parcels** for each
level — this many magic items of this level, this much coin, this many consumables — meant to
be distributed across the level's adventures rather than dropped at once.

```
python3 tools/dnd4e.py treasure --level 4
```

Until `treasure_parcels` is filled, that refuses and names the table. When it is filled, it
prints the list you transcribed — **your list, not a budget**, which is why the output says so.

### Running parcels for a party of one

The published parcels assume five characters sharing. For a solo campaign:

- **Keep the parcel structure, not the count.** The shape — items at and around the party's
  level, interleaved with coin and consumables — is the part that makes 4e's maths work. The
  number of items in a level's set is sized for five people.
- **Scale by the characters you actually have**, and write the divisor in `RULES_DELTAS.md`
  with the reason. A solo character given five characters' parcels will be several item levels
  ahead of their own by the end of the tier, and 4e's defences are tight enough that this shows
  up as the monsters stopping being able to hit them.
- **The companion counts.** If a GM-run ally is in the party, they are one of the shares.

### Item levels

Magic items in 4e have **levels**, and an item's level sets both its bonus and its price. An
item of the party's level is the baseline; a few levels up is a genuine prize. Record the level
on the item so nothing has to be reconstructed later:

```
python3 tools/state.py --campaign X item add "Magic Longsword +1" --owner verrin-ash \
    --kind permanent --level 2 --weight 4
```

`magic_item_prices` is the table that turns a level into a price. It is in the *Player's
Handbook* and *Adventurer's Vault*; fill the levels your campaign will see.

### No attunement, and no slot limit this framework enforces

4e has **no attunement** — the limit on magic items is the body slot an item occupies and its
level, not a count of attuned items. `state.py attune` is refused on a 4e campaign and says so.
The framework does not model slots; keep them on the prose sheet.

---

## Buying and selling

`settlement_availability` **refuses on 4e by design**, and the refusal is the honest answer: 4e
prices items by **level and market price** rather than by settlement size, so there is no
published mapping from "a town of 2,000 people" to "what is on the shelf".

What to do instead: fill `magic_item_prices`, then decide per settlement **what item level its
market carries**, and record that in the world's `GAZETTEER.md` beside the other rulesets'
columns. A frontier village carries level 1–2 consumables; a tiered city carries up to the
party's level; anything above that is a commission with a wait.

Record the decision in the world file rather than deciding again each time the player goes
shopping — two different answers to the same question is the continuity failure this layer
exists to prevent.

---

## Carrying

**Pounds**, as in D&D 2024 and unlike Pathfinder's Bulk.

| | |
|---|---|
| **Normal load** | Ten times the Strength score, in pounds |
| **Heavy load** | Twice the normal load, at the cost of being **slowed** |
| **Maximum drag** | Five times the normal load |

```
python3 tools/state.py --campaign X item add "Chainmail" --owner verrin-ash --weight 40
python3 tools/state.py --campaign X carry
  Verrin Ash: 40.0 lb of 140 lb normal load (heavy 280 lb; Str 14)
```

The framework reports the **normal load as the limit** and names the heavy load. It does not
apply the slowed condition for you — if a character is over the normal load, say so and add the
condition by hand:

```
python3 tools/state.py --campaign X condition add verrin-ash slowed
```

`--bulk` is refused on a 4e campaign: Bulk is Pathfinder's unit, and a Bulk figure stored in a
pounds field would produce a carried total that silently means nothing.

---

## What crosses, and what does not

Treasure is firmly on the **does not cross** side of rule 8. A world shared between a 4e
campaign and a D&D 2024 one may share the *fact* that a sword was taken from the barrow and who
wants it back; it does not share the sword's level, its bonus, its price or its slot. The three
economies are not the same shape and a +1 is not a +1.

```
python3 tools/world.py crossing
```

Write the sword into the world's living history as **a sword with a history**, not as a stat
block — `system/24-the-living-history.md` says why, and `_ruleset_numbers()` in `world.py`
refuses a chapter that smuggles the numbers in.
