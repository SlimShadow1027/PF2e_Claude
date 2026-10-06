# Gazetteer

Places, regions, settlements, and what can be bought in each. **No ruleset's numbers.**
Prices and item availability go in the per-ruleset columns at the bottom of each entry,
because a market is the one place a world's description and a ruleset's numbers meet.

## The shape of the place

The Verge is not a map. It is a **set of maps that move**, and a journey here is described
by which shards you cross and in which span of the drift cycle (`CALENDAR.md`) you cross
them. A route that exists in Touching does not exist in Falling.

Every shard has a **shore** — the edge where it ends and the sky begins — and the shore is
where everything of consequence is built. Inland is farmland, ruin or nothing.

## The shards that matter so far

### Low Shoal

The oldest continuously inhabited shard, and the one that keeps the Reckoning. A long, low
shard with three harbours on its windward shore, none of which is a harbour for water. The
count of years has been kept here without a break since year one, by an office that has
outlasted every government that tried to own it.

Low Shoal is where an outsider arrives, because it is where the crossing-keepers are. It is
also the only shard with a written claim to being the centre of anything, which the others
find funny.

### Thrennet

Closest to Low Shoal through most of the cycle, and therefore its rival rather than its
neighbour. Thrennet controls more crossings than anyone and sells them. If something has to
move between shards, a Thrennet house took a cut of it.

### The Cant

A cluster of small shards rather than one — close enough together that ropes and bridges
hold between them for most of the cycle, and the only place in the Verge where "walking to
the next shard" is a thing anybody says. Lawless by reputation, intricately governed in
fact, by about forty families who do not write anything down.

### Bellows Deep

A mining shard, and the one visibly still coming apart. Pieces calve off its underside on a
schedule the miners can predict and have learned to work around. Everything here is built
to be moved, including the buildings.

### The outer shards

Unnamed in any list because the list changes. New shards appear at the edges, old ones drift
beyond reach, and the people who live on them are either prospecting, hiding, or were born
there and have never seen another.

## Markets

| Settlement | Size | What it has | What it does not |
|---|---|---|---|
| Low Shoal | a city | records, passage, law, anything imported | nothing it makes itself |
| Thrennet | a city | crossings, contracts, muscle | anything it cannot sell again |
| The Cant | many small places | everything, unreliably | a receipt |
| Bellows Deep | a town | ore, stone, salvage, engineers | anything grown |

### What can be bought, per ruleset

**D&D 4e.** 4e prices magic items by **level and market price**, not by settlement size, so
there is no published mapping to use. Record per settlement **what item level its market
carries**, and nothing above it is on a shelf — above that is a commission with a wait.
The price table is `magic_item_prices` in `tools/dnd4e_tables.json` and is **yours to
supply**; see `system/dnd4e/09-loot-and-economy.md`.

| Settlement | Item level carried | Above that |
|---|---|---|
| Low Shoal | the party's level | commission, one span's wait |
| Thrennet | the party's level, plus two for a price | commission, and a favour owed |
| The Cant | two below the party's level, at random | not available; something else is, though |
| Bellows Deep | one below, and consumables only | not available |

_(If a campaign in another ruleset is ever set here, add its own column rather than
converting this one. `python3 tools/world.py crossing`.)_
