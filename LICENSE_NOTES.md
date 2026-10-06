# Licence notes and attribution

## What this repository is

A **framework** for running tabletop games: tooling, procedures, and the tables needed to run the
procedures. It is not a rulebook and it is not a substitute for one.

It supports **three rulesets under three completely different licensing situations**, and that
distinction runs through everything below:

| Ruleset | Rules published under | This repository's material from it |
|---|---|---|
| Pathfinder Second Edition (Remaster) | the **ORC License** | `tools/pf2e.py`, the numbered `system/` docs |
| Fifth edition, 2024 revision | **CC-BY-4.0**, as SRD 5.2 | `tools/dnd5e.py`, `system/dnd5e/` |
| Fourth edition | **nothing. There is no open-content release** | `tools/dnd4e.py`, `system/dnd4e/` — **procedure only; every number is owner-supplied** |

**The licences are not interchangeable and this repository does not mix them.** ORC-licensed
material cannot be relicensed as CC-BY-4.0, nor the reverse, and neither can absorb material from
the third. Every table, quotation and rule statement in this repository sits in exactly one of the
sections below, and nothing has been merged, blended or derived across them. That is a legal
constraint as well as a design one, and it is part of why `system/23-cross-system-worlds.md` is
strict about what crosses between the games: the shared `worlds/` layer holds events and people,
which belong to no publisher, and holds no rules text from any of them.

**Fourth edition is the asymmetric case, and it is the one to understand before using it.** The
licence Wizards of the Coast offered for 4e — the Game System License — permitted no Open Game
Content at all; it licensed a compatibility logo and an index of game terms and templates (the
so-called "4e SRD"), not the rules. It is also no longer offered. So for 4e this repository ships
**no numeric table of any kind**, and the tools refuse to compute rather than guessing. The
"Fourth edition" section below is the full statement.

## What it never contains, for any of the three

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
condition text for each of the two rulesets that have an open source to quote. Each game's is
itemised in its own section below. **For 4e there is no quoted text at all.**

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

# Fourth edition — no open content, and what this framework does about it

## The situation

**There is no open-content release of D&D 4th Edition, and there never was.**

The licence Wizards of the Coast offered for 4e was the **Game System License**. It was not an
open-content licence in the sense the OGL and the ORC License are. It licensed the use of a
compatibility logo and a small index of game terms and templates — what people loosely call "the
4e SRD" — on terms that **permitted no Open Game Content**: not spells, not classes, not feats,
and **not monster stat blocks**. The GSL is also no longer offered.

Fourth edition therefore has:

- **no open text to quote**, and
- **no open text to verify against.**

That second one matters as much as the first. The other two rulesets in this repository were built
by reading an open source and then cross-checking every number against a second, independent
open implementation (Archives of Nethys against Foundry VTT's PF2e system; SRD 5.2 against
Foundry VTT's dnd5e system). Neither step is available for 4e.

## What this framework does instead

It splits procedure from numbers, and treats them completely differently.

| | Where it lives | Status |
|---|---|---|
| **Procedure and structure** | `tools/dnd4e.py`, `system/dnd4e/` | Stated in this framework's **own words**. Nothing quoted. Marked in `sources` as a mechanic with no open source, meaning **believed correct, unverifiable** |
| **Every numeric table** | `tools/dnd4e_tables.json` — **ships empty** | Nothing at all. The tools **refuse to compute** and name the book and table to read from |

Game mechanics — the mathematical relationships and procedures of a game — are not themselves
copyrightable; the **expression** of them is. So this framework states how 4e works in sentences
it wrote itself, and quotes nothing. That is a narrower and more cautious position than the one
it takes with the other two rulesets, where an open licence explicitly permits reproduction.

The nine tables it will not ship are:

| Table | Read it from |
|---|---|
| `character_xp` | *Player's Handbook*, Character Advancement |
| `monster_xp_by_level` | Monster Manual / *Dungeon Master's Guide*, Experience Point Rewards |
| `monster_role_multipliers` | *Dungeon Master's Guide*, how elites, solos and minions count |
| `encounter_budget_per_character` | *Dungeon Master's Guide*, building an encounter |
| `encounter_budget_columns` | *Dungeon Master's Guide*, if your printing gives difficulty columns |
| `dc_by_level` | Rules Compendium or DMG — **revised by errata; record the printing** |
| `treasure_parcels` | *Dungeon Master's Guide*, the parcels for a level |
| `magic_item_prices` | *Player's Handbook* / *Adventurer's Vault*, Magic Item Prices by Level |
| `monster_benchmarks` | *Dungeon Master's Guide*, monster statistics by level |

```
python3 tools/dnd4e.py tables     # what is filled and what is not
python3 tools/dnd4e.py sources    # every statement, with its marking
```

A heroic-tier campaign needs three of the nine. Everything else in the framework — rolling, state,
conditions, the encounter tracker, rests, surges, the living history — works without any of them.

## What this means for you

**`tools/dnd4e_tables.json` is yours.** When you fill it in, you are transcribing, for your own
use, tables out of books you own. That is a private copy for personal use, which is a very
different act from this repository redistributing them — and it is why the file ships empty rather
than ships filled and asks you to delete it.

If you **redistribute** a filled copy of that file, you are redistributing 4e content, and that is
your decision and your exposure, not this framework's. The file's `_meta.books_used` field exists
so your own campaign can record its provenance; it is not a licence.

Nothing in `tools/dnd4e.py` or `system/dnd4e/` is Wizards of the Coast's text. This framework is
not published, endorsed or approved by Wizards of the Coast, and no trademark is licensed to it.
The edition's name is used only to say which rules a campaign is running, which is the one thing a
GM has to know before rolling anything.

## What this repository does NOT contain from fourth edition

Everything. More precisely:

- **No numeric table of any kind.** This is the difference from the other two sections, and it is
  absolute.
- **No class, race, power, feat, ritual, magic item, paragon path or epic destiny text.**
- **No stat blocks**, and no monster benchmark numbers to check one against.
- **No calendar and no setting material.** 4e's published settings are not open content; the
  month names of any of them are deliberately not reproduced. A 4e campaign uses the `generic`
  placeholder calendar or defines one in its world's `CALENDAR.md`.
- **No adventure content, artwork, maps or trade dress.**
- **No quoted rule text**, not even the conditions — which the other two sections both include,
  and which is the clearest single illustration of the asymmetry.

---

# All three

## This framework's own contributions

The Python tooling, the procedures in `system/`, the templates, the slash commands, the improv and
oracle tables in `system/16-random-tables.md`, the difficulty presets, the solo levers that are
marked as homebrew, the cross-system scope bands, the shared-world layer and the living-history
layer are this repository's own work, and are offered under whatever licence the repository owner
chooses to apply. Nothing in them is Paizo's or Wizards'. **Everything in `tools/dnd4e.py` and
`system/dnd4e/` is also this framework's own prose**, for the reason the Fourth edition section
gives.

Specifically **this framework's, not anyone's published rule**, and labelled as such in place:

| This framework's | Where it says so |
|---|---|
| The four difficulty presets, for all three rulesets | `system/03-*`, `system/dnd5e/03-*`, `system/dnd4e/03-*` |
| The oracle ladder and the "no, and" rung | `system/19-solo-oracle.md` |
| The four scope bands as applied to **Pathfinder** levels (D&D 2024's tiers behind them are published) | `python3 tools/rules.py bands` |
| The four scope bands as applied to **4e's thirty** levels (its three tiers are published but not open, so the mapping is this framework's) | `python3 tools/rules.py bands --system dnd4e` |
| **Every statement about 4e**, since there is no open source to quote or verify against | `python3 tools/dnd4e.py sources` — 18 of 20 entries |
| 4e's five encounter-rating labels, since 4e publishes no budget-to-difficulty mapping | `python3 tools/dnd4e.py sources` (`encounter_rating`) |
| D&D treasure pacing by tier, and the settlement-size buckets | `python3 tools/dnd5e.py sources` |
| Rolling initiative ties off with dice in both D&D editions, where the published rule leaves them to the GM | `roll.py init` prints both |
| The random-encounter cadence and the morale rule | `system/dnd5e/06-*`, `system/dnd5e/10-*` |
| The `generic` placeholder calendar | `python3 tools/rules.py calendars` |

`python3 tools/pf2e.py sources`, `python3 tools/dnd5e.py sources` and
`python3 tools/dnd4e.py sources` each count these separately from the published tables, so the
line between what is quoted, what is stated and what is invented stays visible rather than being a
matter of trust. The 4e one is worth running once for its own sake: it says, at the top, that this
ruleset's provenance is weaker than its siblings' and why.

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
- **For fourth edition this is not advice, it is a requirement.** The Player's Handbook and
  Dungeon Master's Guide are the only places the numbers exist; without them the encounter,
  advancement, DC and treasure maths will not compute at all, and the tools will keep saying so.
  The Rules Compendium is worth having for the revised DC table.

SRD 5.2 is free, covers the player-facing core rules in full, and is enough to run a campaign in
this framework without buying anything: <https://www.dndbeyond.com/srd>. Archives of Nethys
(<https://2e.aonprd.com>) is the equivalent for Pathfinder.
