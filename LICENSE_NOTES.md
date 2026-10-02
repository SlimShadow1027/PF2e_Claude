# Licence notes and attribution

## What this repository is

A **framework** for running tabletop games: tooling, procedures, and the tables needed to run the
procedures. It is not a rulebook and it is not a substitute for one.

It supports **two rulesets, published under two different licences**, and that distinction runs
through everything below:

| Ruleset | Rules published under | This repository's material from it |
|---|---|---|
| Pathfinder Second Edition (Remaster) | the **ORC License** | `tools/pf2e.py`, the numbered `system/` docs |
| Fifth edition, 2024 revision | **CC-BY-4.0**, as SRD 5.2 | `tools/dnd5e.py`, `system/dnd5e/` |

**The two licences are not interchangeable and this repository does not mix them.** ORC-licensed
material cannot be relicensed as CC-BY-4.0, nor the reverse. Every table, quotation and rule
statement in this repository sits in exactly one of the two sections below, and nothing has been
merged, blended or derived across them. That is a legal constraint as well as a design one, and it
is part of why `system/23-cross-system-worlds.md` is strict about what crosses between the games:
the shared `worlds/` layer holds events and people, which belong to neither publisher, and holds
no rules text from either.

## What it never contains, for either game

- **No stat blocks.** `templates/bestiary/_CREATURE_TEMPLATE.md` is an empty form with a required
  `Source:` line. Every creature actually used in a campaign is written into
  `campaigns/<slug>/bestiary/` by the person running it, from material they own, cited by name and
  by level or Challenge Rating. `tools/validate.py` fails a bestiary file with no source.
- **No spell, feat, item, class, ancestry or species text.** Look those up in the books, on
  Archives of Nethys, or in SRD 5.2.
- **No adventure, Adventure Path or published-setting content.**
- **No artwork, maps or trade dress.** Maps in this framework are ASCII grids the GM draws.

What it *does* contain is a small number of **game mechanics** — mathematical relationships and
short rule statements — needed for the tooling to compute anything, plus one block of quoted
condition text per ruleset. Each game's is itemised in its own section below.

---

# Pathfinder Second Edition — ORC

## What this repository does not contain from Pathfinder

- **No stat blocks.** `templates/bestiary/_CREATURE_TEMPLATE.md` is an empty form with a required
  `Source:` line. Every creature actually used in a campaign is written into
  `campaigns/<slug>/bestiary/` by the person running it, from material they own, cited by name,
  source and level. `tools/validate.py` fails a bestiary file with no source.
- **No spell, feat, item, class or ancestry text.** Look those up in the books or on Archives of
  Nethys.
- **No adventure or Adventure Path content.**
- **No artwork, maps or trade dress.** Maps in this framework are ASCII grids the GM draws.

## What this repository contains from Pathfinder, and where those numbers came from

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

---

# Fifth edition, 2024 revision — CC-BY-4.0

## The required attribution

SRD 5.2 is provided free of charge by Wizards of the Coast LLC under the Creative Commons
Attribution 4.0 International License, which requires a specific attribution statement. It is
reproduced here verbatim, as the licence requires:

> This work includes material from the System Reference Document 5.2 ("SRD 5.2") by Wizards of
> the Coast LLC, available at <https://www.dndbeyond.com/srd>. The SRD 5.2 is licensed under the
> Creative Commons Attribution 4.0 International License, available at
> <https://creativecommons.org/licenses/by/4.0/legalcode>.

The licence asks that **no other attribution to Wizards of the Coast or its affiliates** be
included beyond that statement, and this repository includes none. It permits a statement of
compatibility, so: **this framework is compatible with fifth edition.** It is not published,
endorsed or approved by Wizards of the Coast, and trademarks are not licensed to it — the game's
name is used only to say which rules a campaign is running, which is the one thing a GM has to
know before rolling anything.

Section 5 of CC-BY-4.0 contains a Disclaimer of Warranties and Limitation of Liability.

## What this repository contains from SRD 5.2, and where it came from

| In this repository | What it is |
|---|---|
| The D20 Test procedure, and the natural-20/natural-1 attack rules | rule statements, quoted in part, in `tools/dnd5e.py` and `system/dnd5e/12-*` |
| Typical Difficulty Classes; the Proficiency Bonus table | numeric tables, in `tools/dnd5e.py` |
| Character Advancement (cumulative XP); fixed Hit Points by class | numeric tables |
| Experience Points by Challenge Rating | a numeric table |
| XP Budget per Character, and the three difficulty descriptions | a numeric table and close paraphrase |
| Magic Item Rarities and Values; Starting Equipment at Higher Levels | numeric tables |
| Carrying Capacity; Coin Values; Lifestyle Expenses | numeric tables |
| Travel Pace and Travel Terrain | numeric tables |
| Full-caster spell slots by level | a numeric table |
| Critical hits, damage order of application, 0 HP, Death Saving Throws, instant death | rule statements, quoted in part |
| Concentration, Cover, Attunement, Short Rest, Long Rest, Heroic Inspiration | rule statements, quoted in part |
| Tiers of Play | quoted, for the scope bands in `tools/rules.py` |
| **The fifteen condition entries, quoted in `system/dnd5e/12-rules-quick-reference.md`** | **condition text, quoted** |

The condition entries are the only substantial block of **quoted text** from SRD 5.2 in this
repository, and they are here for the same reason the Pathfinder condition entries are: the exact
wording is what makes a condition adjudicable, and paraphrasing would reintroduce the
"recalled from memory" error this framework exists to prevent.

### Provenance

SRD 5.2 was read from a complete Markdown transcription of the official PDF:

<https://github.com/springbov/dndsrd5.2_markdown> at commit
`6a3547c1d625fb125fbbcb8ded563f5beff197a8`, file `DND-SRD-5.2-CC.md` — itself CC-BY-4.0 and
carrying the same attribution statement.

Because that transcription is a conversion rather than the publisher's own file, **every numeric
table was additionally cross-checked against an independent implementation**:

<https://github.com/foundryvtt/dnd5e> v6.0.5 at commit
`7bfb3f1c03e107bf65942151ef08d50ddb01ba8a`, `module/config.mjs`. Its software is MIT-licensed
(copyright 2021 Andrew Clayton and contributors) and its SRD content is CC-BY-4.0. **No code from
it is reproduced here** — it was read to confirm numbers. The two sources agreed on all of them.

`python3 tools/dnd5e.py sources` prints the provenance of every table, and reports separately how
many are this framework's own convention rather than a published rule.

## What this repository does NOT contain from fifth edition

- **No class, species, background, feat, spell or magic item text.** Look those up in SRD 5.2,
  which is free, or in the books.
- **No stat blocks.** `templates/bestiary/_CREATURE_TEMPLATE.md` is an empty form with a required
  `Source:` line.
- **No adventure content, artwork, maps or trade dress.**
- **No Dungeon Master's Guide material.** This matters more than it sounds: the 2024 treasure
  tables, the random treasure hoards and the published settings are **not** SRD content, and this
  framework does not reproduce or reconstruct them. Where it needs an answer anyway — treasure
  pacing, settlement availability, downtime income — it says the answer is its own and names the
  published figures it was built from. See `system/dnd5e/09-loot-and-economy.md`.
- **No calendar, and no setting material of any kind.** SRD 5.2 publishes none. The month names of
  published settings are deliberately not reproduced; a campaign supplies its own, or its world
  defines one in `CALENDAR.md`.

---

# Both

## This framework's own contributions

The Python tooling, the procedures in `system/`, the templates, the slash commands, the improv and
oracle tables in `system/16-random-tables.md`, the difficulty presets, the solo levers that are
marked as homebrew, the cross-system scope bands and the shared-world layer are this repository's
own work, and are offered under whatever licence the repository owner chooses to apply. Nothing in
them is Paizo's or Wizards'.

Specifically **this framework's, not anyone's published rule**, and labelled as such in place:

| This framework's | Where it says so |
|---|---|
| The four difficulty presets, for both rulesets | `system/03-*` and `system/dnd5e/03-*` |
| The oracle ladder and the "no, and" rung | `system/19-solo-oracle.md` |
| The four scope bands as applied to **Pathfinder** levels (the D&D tiers behind them are published) | `python3 tools/rules.py bands` |
| D&D treasure pacing by tier, and the settlement-size buckets | `python3 tools/dnd5e.py sources` |
| Rolling initiative ties off with dice in D&D, where the published rule is that the GM decides | `roll.py init` prints both |
| The random-encounter cadence and the morale rule | `system/dnd5e/06-*`, `system/dnd5e/10-*` |
| The `generic` placeholder calendar | `python3 tools/rules.py calendars` |

`python3 tools/pf2e.py sources` and `python3 tools/dnd5e.py sources` each count these separately
from the published tables, so the line between what is quoted and what is invented stays visible
rather than being a matter of trust.

Where this framework invents a rule rather than quoting one, it says so — in `RULES_DELTAS.md` for a
campaign's house rules, and inline in `system/` for the framework's own conventions (the wounded
descriptors, the scene-check ladder, the "no, and" oracle rung, the four presets).

## If you own the books

You should. This framework is designed to be used **alongside** the rulebooks for whichever game a
campaign is running, not instead of them — every `Source:` line in it is an instruction to go and
look something up.

- For Pathfinder: Player Core, Player Core 2, GM Core and Monster Core.
- For fifth edition: the 2024 Player's Handbook, Dungeon Master's Guide and Monster Manual. The
  DMG in particular fills a real gap here, since its treasure tables are not open content and this
  framework paces treasure by convention in their absence.

SRD 5.2 is free, covers the player-facing core rules in full, and is enough to run a campaign in
this framework without buying anything: <https://www.dndbeyond.com/srd>. Archives of Nethys
(<https://2e.aonprd.com>) is the equivalent for Pathfinder.
