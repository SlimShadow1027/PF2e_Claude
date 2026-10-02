# Varisia

A shared setting. Several campaigns can be set here, in different eras.

A world here is **system-neutral**: campaigns running either ruleset can be set in it, and
the shared layer records what happened rather than anyone's numbers.

## Campaigns set in this world

| Campaign | System | Era / start date | Status |
|---|---|---|---|
| third-beginnings | PF2e | 1 Abadius 4725 AR | active |

## What this world is

_Two or three paragraphs: the shape of the place, what makes it itself, and the one thing
a newcomer needs to know._

## What lives where

- `CHRONICLE.md` — dated record of concluded events, append-only, one line of visibility each.
- `LEGENDS.md` — how those events are *remembered* in-world, distortions included.
- `GAZETTEER.md` — places, regions, settlements and what can be bought in each.
- `FACTIONS.md` — long-lived organisations, their standing and leadership.
- `PANTHEON.md` — gods and cosmology.
- `CALENDAR.md` — the calendar, eras, and the current present day. The calendar belongs
  to the world, not to a ruleset, so both games read the same dates.
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
- **No ruleset's numbers go in here.** Events, people, places, debts and reputations cross
  between the two games; levels, DCs, stat blocks and treasure do not. Chronicle entries
  carry a `System:` line saying which game wrote them and a `Scope:` line saying how far
  the event reached — scope is the only translation this framework will make.
  `python3 tools/world.py crossing` is the full statement.
