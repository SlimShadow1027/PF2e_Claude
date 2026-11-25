# Licence notes and attribution

## What this repository is

A **framework** for running Pathfinder Second Edition (Remaster) games: tooling, procedures, and
the tables needed to run the procedures. It is not a rulebook and it is not a substitute for one.

## What it does not contain

- **No stat blocks.** `templates/bestiary/_CREATURE_TEMPLATE.md` is an empty form with a required
  `Source:` line. Every creature actually used in a campaign is written into
  `campaigns/<slug>/bestiary/` by the person running it, from material they own, cited by name,
  source and level. `tools/validate.py` fails a bestiary file with no source.
- **No spell, feat, item, class or ancestry text.** Look those up in the books or on Archives of
  Nethys.
- **No adventure or Adventure Path content.**
- **No artwork, maps or trade dress.** Maps in this framework are ASCII grids the GM draws.

## What it does contain, and where those numbers came from

A small number of **game mechanics** — mathematical relationships and short rules statements —
needed for the tooling to compute anything:

| In this repository | What it is |
|---|---|
| Degrees of success, and the natural-20/1 shift | a rule statement, in `tools/roll.py` and `system/12-*` |
| DCs by level; simple DCs by proficiency; DC and rarity adjustments | numeric tables, in `tools/pf2e.py` |
| Encounter XP budgets; creature XP by relative level; hazard XP | numeric tables, in `tools/pf2e.py` |
| Item-bonus expectations by level (from Automatic Bonus Progression) | a numeric table, in `tools/pf2e.py` |
| Earn Income by level and proficiency | a numeric table, in `tools/pf2e.py` |
| Multiple attack penalty; Bulk limits; coin ratios; the dying/recovery loop | rule statements |
| Party treasure by level, with item counts and item levels; treasure per encounter; travel speeds | numeric tables, in `tools/pf2e.py` |
| Fundamental rune upgrade prices and levels | two numeric tables, in `system/09-loot-and-economy.md` |
| The 43 condition entries, quoted in `system/12-rules-quick-reference.md` | **condition text, quoted** |

The condition entries are the only substantial block of **quoted text** in this repository. They
are included because the exact wording is what makes a condition adjudicable, and paraphrasing
them would reintroduce precisely the "recalled from memory" error this framework exists to prevent.

### Provenance

The numeric tables were read from **Archives of Nethys** (`2e.aonprd.com`), which publishes the
ORC-licensed rules text, and each carries the page ID it came from.

Where Archives of Nethys does not present a value as a table — the degrees-of-success thresholds,
the multiple attack penalty, the item-bonus curve, the dying numbers, the Earn Income rates, the
Golarion calendar and the condition text — the value was additionally or solely checked against the
**Foundry VTT Pathfinder 2e system** source, an open-source, ORC-licensed implementation that cites
Archives of Nethys rule IDs inline, at version 8.5.1, commit
`06b904d6ced9795c4c07af085e6f61a56f845c60`:

<https://github.com/foundryvtt/pf2e>

`python3 tools/pf2e.py sources` prints the provenance of every table. `DESIGN_NOTES.md` records
what the re-verification against Archives of Nethys found, including the fourteen values it
corrected.

## ORC

Pathfinder Second Edition's rules are published under the **ORC License**. The mechanics and
condition text reproduced here are Licensed Material under that licence, as is the Foundry VTT PF2e
system they were checked against.

> This product is licensed under the ORC License held in the Library of Congress at TX 9-307-067 and
> available online at various locations including paizo.com/orclicense, azoralaw.com/orclicense,
> and others. All warranties are disclaimed as set forth therein.
>
> **Attribution:** This product is based on the Pathfinder Second Edition Remaster rules published
> by Paizo Inc., and on the Pathfinder Second Edition system for Foundry Virtual Tabletop
> (<https://github.com/foundryvtt/pf2e>), both Licensed Material under the ORC License.
>
> **Reserved Material:** Product Identity and trademarks of Paizo Inc. are Reserved Material and
> are not licensed. This includes, without limitation, the trademarks *Pathfinder*, *Paizo*,
> *Golarion*, *Absalom Reckoning*, *Monster Core*, *Player Core*, *GM Core*, *NPC Core*, and Paizo's
> logos and trade dress.

Anyone redistributing or building on this repository should read the ORC License itself rather than
this summary, and should check that any additional material they add is either their own or
appropriately licensed.

## Paizo Community Use

Setting names used in this repository — Golarion, Absalom, Ustalav, the Mwangi Expanse, Cheliax, the
Mana Wastes, Tian Xia, Varisia, the Shackles, Korvosa, the Absalom Reckoning calendar's month and
weekday names — are Paizo's Product Identity, referenced here as **setting references for the
person running the game**, not reproduced as content.

> Pathfinder and Paizo are trademarks of Paizo Inc. This framework is not published, endorsed, or
> specifically approved by Paizo. For more information about Paizo Inc. and Paizo products, visit
> <https://paizo.com>. Content used under the Paizo Community Use Policy
> (<https://paizo.com/community/communityuse>) where it applies.

## This framework's own contributions

The Python tooling, the procedures in `system/`, the templates, the slash commands, the improv and
oracle tables in `system/16-random-tables.md`, the four difficulty presets, and the solo levers that
are marked as homebrew are this repository's own work, and are offered under whatever licence the
repository owner chooses to apply. Nothing in them is Paizo's.

Where this framework invents a rule rather than quoting one, it says so — in `RULES_DELTAS.md` for a
campaign's house rules, and inline in `system/` for the framework's own conventions (the wounded
descriptors, the scene-check ladder, the "no, and" oracle rung, the four presets).

## D&D 5e — SRD 5.2.1 (CC-BY-4.0)

`tools/dnd5e.py`, `templates/dnd5e/` and `system/dnd5e/` support D&D Fifth Edition campaigns.
They contain game mechanics and short rule statements only — numeric tables and one-line
rules, no stat blocks, spell, class or monster text — in the same spirit as the PF2e material
above.

> This work includes material from the System Reference Document 5.2.1 ("SRD 5.2.1") by
> Wizards of the Coast LLC, available at https://www.dndbeyond.com/srd. The SRD 5.2.1 is
> licensed under the Creative Commons Attribution 4.0 International License, available at
> https://creativecommons.org/licenses/by/4.0/legalcode.

⚠ The wording above follows the attribution statement the SRD 5.2.1 asks for, but it was
written without access to the document (the host was unreachable). Check it against the SRD's
legal page before publishing anything built from this repository.

"Dungeons & Dragons" and "D&D" are trademarks of Wizards of the Coast; they are used here only
to say which game these tools support. This repository is not affiliated with or endorsed by
Wizards of the Coast.

## If you own the books

You should. This framework is designed to be used alongside Player Core, Player Core 2, GM Core and
Monster Core, not instead of them — every `Source:` line in it is an instruction to go and look
something up.
