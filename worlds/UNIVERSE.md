# The universe

The layer above `worlds/`. **Optional, and only worth having once a second world exists.**

A world is a place campaigns are set in. A universe is what is true *across* places — so
that a campaign on another continent, another plane or in another age can be the same
universe as the first without sharing its geography, its factions or its history.

**This universe is called the Strand.** Each world's README declares membership with a
`Universe: the Strand` line.

## The worlds in it

| World | Where it sits | Era | Rulesets | Reachable from |
|---|---|---|---|---|
| `varisia` | a region of the material world | Absalom Reckoning, the 4720s | PF2e, D&D 2024 | the Riven Verge lies below it |
| `riven-verge` | a plane — a shattered world hanging below the material one | the Verge Reckoning, late | D&D 4e (none linked yet) | Varisia, by ways that do not run back |

`python3 tools/world.py universe` rebuilds this table from the world folders themselves, so
it does not drift. Each world declares its own position with a `Position:` field in its
README.

## What is true everywhere

_The things a character from any of these worlds would recognise. Keep this short — the
longer it is, the less room each world has to be itself._

### Cosmology

The Strand is a **stack**, not a sphere. There is a material world, and there are places
below and beside it, and the relationship between them is vertical in a way that everyone in
every world agrees on and nobody can explain. "Below" is not a metaphor and is not a
direction you can walk.

Magic is the same substance everywhere in the Strand and is reached by different habits in
each world — which is the in-world reason three different sets of rules describe it, and
the one place where this file comes close to saying something about mechanics. It stops
there deliberately: **how magic behaves is each ruleset's business, and that is why no
number appears in this file.**

The dead go down. Not to any of the worlds listed above — further — and nobody in any of
them has brought back a reliable account of where.

### The deep past

Something came apart. This is the one event every world in the Strand remembers, and no two
of them remember it the same way.

In Varisia it is read as an ancient collapse: an empire that fell, left ruins that are still
dangerous, and whose survivors became other people. In the Riven Verge it is not history at
all but geography — the shards *are* the event, still visibly in progress. Both accounts are
about the same thing, and neither world knows that.

What is agreed everywhere, in the vague way deep past is agreed: it was not natural, it was
not an accident, and the people responsible are not reliably named anywhere.

### Powers that span worlds

_Nothing is named here yet, and that is the honest state. Add a power to this list only when
a campaign has established it in **more than one** world — until then it belongs in that
world's own `PANTHEON.md` or `FACTIONS.md`. This is the rule most easily broken, because a
god feels universal the moment it is invented._

One candidate is already implied by the deep past above: whoever or whatever took the Strand
apart is feared, under different names, in both worlds listed. Neither world has a name for
it that the other would recognise, so it is not named here either.

## How the worlds connect

_The honest answer is often "they do not, yet", and that is a fine answer. Write it down
anyway, because "no known route" is itself a fact a campaign can work against._

| From | To | Route | Who knows it | Cost |
|---|---|---|---|---|
| Varisia | the Riven Verge | ways down: sinkholes that are not sinkholes, sealed doors, places where the ground is thinner than it should be | nobody deliberately; the people who found one are in the Verge | one-directional, so far as anyone has established |
| the Riven Verge | Varisia | **no known route** | — | — |

That asymmetry is the point, and it is doing work in both directions. A Varisian campaign has
somewhere unreachable it can lose things to. A Verge campaign has a question it cannot answer
and a population descended from people who could not go home.

It is also why a shared NPC or a shared item is interesting here rather than routine: something
that crossed had to cross *once*, in one direction, and saying how is a scene.

## What crosses between worlds

The same discipline as `system/23-cross-system-worlds.md`, one layer up. Across worlds:

| Crosses | Does not cross |
|---|---|
| Cosmology, planar structure, the deep past | Local history, local factions, local geography |
| Powers named in this file | Powers named in a single world's PANTHEON.md |
| A character who physically travelled, with their story | A character's reputation, unless news travelled with them |
| Items, with their histories | Any ruleset's numbers — see `world.py crossing` |

**A world's history is its own.** A chapter in one world's `HISTORY.md` is not known in
another unless something carried it there, and saying what carried it is more interesting
than assuming it did.

## The rules that keep this layer clean

- **Nothing live, ever.** Same as `worlds/`.
- **No ruleset's numbers.** This file may be read by a campaign in any of the games.
- **Write here only what is true in every world listed.** A fact true in one world belongs
  in that world's files. This is the most commonly broken rule and the one that makes the
  layer worthless when broken.
