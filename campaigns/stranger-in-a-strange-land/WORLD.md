# World — Stranger in a Strange Land

The gazetteer for *this campaign*. If `CAMPAIGN.md` names a world under `worlds/`, the
long-lived setting material lives there and this file holds only what this campaign has
touched, plus anything that diverges locally.

## Where we are

- **Region:** set by the pitch the player picks. The protagonist arrives on a battlefield in a
  border region between two nations.
- **Home base:** none at the start; the protagonist arrives with nothing. The first home base
  comes from the pitch.

## Settlements

| Settlement | Type | Item level | Travel from base | One line |
|---|---|---|---|---|
| | | | | |

Item level is what play actually needs: it caps what can be bought there. The
campaign-agnostic defaults in `tools/pf2e.py` (`ITEM_LEVEL_BY_SETTLEMENT`) are marked
UNVERIFIED — set these explicitly.

## Places

| Place | Region | What it is | Been there? |
|---|---|---|---|
| | | | |

## Travel times

Overland pace comes from `python3 tools/pf2e.py tables travel` (an 8-hour travel day, verified;
the miles-per-day column is marked unverified).

| From | To | Distance | Days at normal pace | Hazards en route |
|---|---|---|---|---|
| | | | | |

## Factions

| Faction | Standing | Wants | Disposition to the party | Player knows? |
|---|---|---|---|---|
| | | | | |

## Weather and season

- **Climate:** not yet decided
- **Current season:** not yet decided
- Roll weather on the table in `system/16-random-tables.md`.

## Local rules of the world

Anything true here that would surprise a visitor: magic that does not work, a law with
teeth, a custom that gets outsiders killed.

- **The gods' peace is fragile.** Each nation reflects its gods' alignments, from lawful good to
  chaotic evil.
- **Magic law varies by nation.** Lawful, advanced states license it through churches and
  academies; some lands distrust or outlaw it. Everyone knows magic exists.
- **Firearms and crossbows are regional.** Some armies field them and others never have.
- **Slavery** is legal and common in the evil nations, and practised in one or two neutral or
  good ones under their own justifications.
- **Native people are measured on a lower scale than the stranger.** Ordinary soldiers and
  champions are built low; native **magic** and great **monsters** are not.
