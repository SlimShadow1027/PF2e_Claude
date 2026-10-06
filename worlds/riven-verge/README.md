# The Riven Verge

A shared setting. Several campaigns can be set here, in different eras.

A world here is **system-neutral**: campaigns running any supported ruleset can be set in
it, and the shared layer records what happened rather than anyone's numbers.

## Where this world sits

- **Universe:** the Strand
- **Position:** a plane, not a continent — a shattered world hanging below the material one
- **Era:** the Verge Reckoning, and it is late in it
- **Reachable from:** Varisia, by ways that are lost, sealed or one-directional — and no known route runs back

> `Universe:` links this world to others in `worlds/UNIVERSE.md`, so a campaign somewhere
> else entirely can be the same universe without sharing this world's history or geography.
> `none` keeps it standalone. `python3 tools/world.py universe` lists the register.

## Campaigns set in this world

| Campaign | System | Era / start date | Status |
|---|---|---|---|
| _(none yet — `tools/world.py link` adds a row)_ | | | |

## What this world is

The Riven Verge is what is left of a world that came apart and did not finish falling. It
hangs in pieces — shards of continent the size of counties, each with its own weather and its
own horizon, drifting slowly against one another in a sky that has no sun in it and is not
dark. Crossing between shards is the central fact of life here, and every settlement of any
size is built around whatever means of crossing it controls.

Nobody here agrees on what broke it. The oldest account says the Verge was never whole and
the shards were always shards; the commonest says something was done, deliberately, by people
whose names did not survive the doing. Both agree that it happened long enough ago that the
survivors' descendants have had time to become natives, and that something is still coming
apart somewhere, because new shards are still appearing at the edges.

**The one thing a newcomer needs to know:** the Verge is reachable from the material world
and does not reach back. People arrive here. Some of them arrive by accident. None of them
have gone home, and the question of whether anyone could is the oldest live argument in the
place.

> **This is deliberately far from Varisia.** Different plane, different era, different
> cosmology at ground level, a calendar of its own and no shared geography or factions. What
> it shares with Varisia is the **universe** — see `worlds/UNIVERSE.md` — which is to say the
> deep past and the shape of the planes, and nothing local at all. A character from Varisia
> could be here; their reputation could not have preceded them.

## What lives where

- `CHRONICLE.md` — dated record of concluded events, append-only, one line of visibility each.
- `HISTORY.md` — the living history: prose, shared by every ruleset, spans rather than dates,
  the certainty of each account stated, and **no ruleset's numbers**.
- `<system>/<campaign>.md` — the thorough narrative history of one campaign, read only by
  campaigns of that ruleset, so it may name the rules.
- `LEGENDS.md` — how those events are *remembered* in-world, distortions included.
- `GAZETTEER.md` — places, regions, settlements and what can be bought in each.
- `FACTIONS.md` — long-lived organisations, their standing and leadership.
- `PANTHEON.md` — gods and cosmology.
- `CALENDAR.md` — the calendar, eras, and the current present day. The calendar belongs to
  the world, not to a ruleset, so every game reads the same dates.
- `canon.md` — world-level established facts, append-only.
- `characters/` — one legacy record per character who has played here.
- `npcs/` — NPCs who persist beyond one campaign.
- `gm-private/threads.md` — unresolved world-level threads a future campaign could pick up.

## The rules that keep this layer clean

- **Nothing live is ever written here.** No hit points, coins, inventory, conditions,
  positions, checkpoints or roll logs. Those stay in `campaigns/<slug>/` permanently.
- **Writes happen only at promotion points** — an arc concludes, a campaign concludes, or
  the player says an event is world-significant — through `tools/world.py promote`.
- **Campaign canon wins locally.** Where a campaign contradicts world canon, the campaign
  records a local divergence; the world keeps the version other campaigns inherit.
- **Reads are date-gated.** A campaign reads world material dated at or before its own
  current in-world date and nothing later.
- **No ruleset's numbers go in here.** Events, people, places, debts and reputations
  cross between the games; levels, DCs, stat blocks and treasure do not. Chronicle
  entries carry a `System:` line saying which game wrote them and a `Scope:` line saying
  how far the event reached — scope is the only translation this framework will make.
  `python3 tools/world.py crossing` is the full statement.
