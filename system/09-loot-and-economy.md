# 09 — Loot and the economy

```
python3 tools/pf2e.py treasure --level 5 --party-size 1
python3 tools/pf2e.py tables treasure
python3 tools/pf2e.py tables earn-income
python3 tools/pf2e.py tables item-bonuses
```

---

## Treasure by level

⚠ **The treasure-by-level table in `tools/pf2e.py` is marked `⚠ UNVERIFIED`.** The Foundry VTT
system does not implement it and `2e.aonprd.com` was unreachable when this framework was built,
so those values come from the model's reading of GM Core rather than from a checked source.
**Verify every row against GM Core before using it to pace a campaign's economy.** It is listed
in `DESIGN_NOTES.md` under "To verify before first play".

The published row is the total gp value of everything a **four-character party** should find over
one level. For a smaller party the tool divides by four and multiplies by the party size, which
is a derivation rather than a published column — say so when it is used.

The mix, also unverified and treated as a rule of thumb:

| Kind | Share |
|---|---|
| Permanent items | ~50% |
| Consumables | ~25% |
| Currency and valuables | ~25% |

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

## Item level availability by settlement

⚠ `⚠ UNVERIFIED`. `tools/pf2e.py` carries usable defaults —

| Settlement | Item level |
|---|---|
| Village | 2 |
| Town | 6 |
| City | 10 |
| Metropolis | 14 |
| Capital / planar market | 20 |

— but these are defaults, not quoted values. **Set them explicitly per campaign in `WORLD.md`**
and say that is where they came from. What can be bought where is one of the few economic facts
a player will plan around, so it should be decided rather than improvised.

---

## The coin ledger

1 pp = 10 gp = 100 sp = 1,000 cp. **Source:** Player Core, Coins.

```
python3 tools/state.py --campaign X gold add 42gp 3sp
python3 tools/state.py --campaign X gold spend 5gp
```

Gaining coins **keeps the denominations as received**, so the purse reads back as what the party
actually picked up rather than as the tidiest equivalent. Spending pays from matching
denominations first and only breaks larger coins when it has to, and says when it did.

The tool **refuses** to go negative and says what the purse holds. It does not clamp.

Record every arrival and every departure in `logs/loot.md` with the in-world date and where it
came from. That ledger is what makes the pacing tracker above possible.

---

## Bulk and encumbrance

| | |
|---|---|
| 10 light items (`L`) | 1 Bulk |
| Negligible (`—`) | does not count until a heap of it does |
| **Encumbered** above | 5 + Strength modifier |
| **Maximum** | 10 + Strength modifier |

Encumbered is **clumsy 1 and a 10-foot penalty to all Speeds**.

```
python3 tools/state.py --campaign X item add "Healing Potion (Lesser)" 2 --owner kaelen --bulk L --kind consumable
python3 tools/state.py --campaign X bulk
```

`validate.py` errors when a carrier is over the maximum, and warns when they are encumbered but
the condition has not been recorded on them.

**Source:** Player Core, Bulk. Verified against the Foundry VTT PF2e implementation.

---

## Consumables, ammunition and charges

Track each as an item with a `kind`:

- `consumable` — potions, scrolls, talismans. `item use` decrements the count.
- `ammunition` — arrows, bolts, sling bullets. Decrement on the shot, not at the end of the
  fight, or it will not get decremented.
- Anything with `--charges N` — a wand, a staff, a charged item. `item use` spends a charge and
  refuses to go below zero.

```
python3 tools/state.py --campaign X item use "Healing Potion (Lesser)" --owner kaelen
python3 tools/state.py --campaign X item add "Wand of Heal" 1 --owner kaelen --charges 1 --kind permanent
```

A consumable the player forgot they had is a consumable that was never worth buying, so the
dashboard lists them with their counts on the resources row.

---

## Runes and their costs

A weapon or armour's item bonus comes from its **potency** rune; its extra damage dice from
**striking** (weapons) or its save bonus from **resilient** (armour); property runes add
everything else.

Etching a rune costs the rune's price and requires Crafting at the rune's level. Transferring a
rune to another item costs half the rune's price. A rune can be moved; an item's own base
quality cannot.

⚠ The rune price table and the transfer cost are `⚠ UNVERIFIED` against a reachable source.
Look them up in Player Core before a purchase, and cite what you find.

The **curve** the runes are there to keep up with is verified:
`python3 tools/pf2e.py tables item-bonuses`.

---

## Buying and selling

- **Buying** at full price, where the settlement's item level allows it.
- **Selling** at **half** the item's price, as the default. A specialist buyer, a Diplomacy or
  Society check, or an interested collector can improve it — that is a scene, not a table.
- Selling a **consumable** or a common item is usually not worth the scene; just take the half.

⚠ The half-price sale rate is the long-standing convention and is `⚠ UNVERIFIED` here against a
reachable source.

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

Crafting an item takes 4 days of setup plus the material cost (half the item's price), then each
additional day of work reduces the remaining cost by the Earn Income rate for your level and
proficiency. You must have the formula, and be at least the item's level.

⚠ The 4-day setup and the half-price materials figure are `⚠ UNVERIFIED` against a reachable
source.

For long stretches, use the downtime procedure in `10-downtime-travel-and-rest.md` so weeks
resolve in a few exchanges.
