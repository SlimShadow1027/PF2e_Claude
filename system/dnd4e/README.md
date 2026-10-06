# D&D 4th Edition in this framework — read this first

**This ruleset is not shipped on the same footing as its two siblings, and you need to know
why before you run it.**

Pathfinder 2e is published under the ORC Licence, and D&D 2024 has an SRD under CC-BY-4.0.
Both of those licences let this framework carry the actual numbers: `tools/pf2e.py` and
`tools/dnd5e.py` hold DC tables, XP thresholds, encounter budgets and treasure values, each
with a `Source:` line naming where it came from.

**Fourth edition has no equivalent.** The licence Wizards of the Coast offered for 4e — the
Game System License — permitted no Open Game Content at all. It licensed a compatibility
logo and a small index of game terms and templates (what people call "the 4e SRD"), not the
rules. It is also no longer offered. There is therefore no open source from which this
framework can take a single 4e number, and no open text against which it can verify one.

So the split here is:

| | Where it lives | What you get |
|---|---|---|
| **Procedure and structure** | `tools/dnd4e.py` and these documents | Stated in this framework's own words. Mechanics are not copyrightable; the expression of them is, so nothing is quoted. Marked `[D&D 4e mechanic, …]` in `sources`, meaning **believed correct, unverifiable** |
| **Every numeric table** | `tools/dnd4e_tables.json` — **empty until you fill it** | Nothing. The tools **refuse to compute** and name the book and table to read from |

That refusal is deliberate. The alternative is a tool that answers an encounter-budget
question with a number nobody can trace, in a game where the budget maths is the difficulty
dial. A refusal that names the table is more use than a confident guess.

---

## What you have to do before the maths works

```
python3 tools/dnd4e.py tables          # what is filled and what is not
```

Nine tables are listed. **You do not need all nine.** A heroic-tier campaign needs three:

1. **`character_xp`** — the cumulative XP to reach each level, from the Character Advancement
   table in the *Player's Handbook*. Levels 1–10 is enough to start.
2. **`monster_xp_by_level`** — the XP a monster of a given level is worth, from the Experience
   Point Rewards table. Levels 1–12 covers a heroic campaign fighting slightly up.
3. **`encounter_budget_per_character`** — the XP budget for one character of a given level,
   from the *Dungeon Master's Guide*. This is the one that makes `dnd4e.py encounter` work.

Add the rest when you reach them: `dc_by_level` the first time you set a skill DC,
`treasure_parcels` and `magic_item_prices` the first time the party is paid.

Edit `tools/dnd4e_tables.json` by hand. Every entry has a `_source` line saying which book
and table to read. Record which books you used in `_meta.books_used` so the campaign's own
provenance is written down somewhere.

> **One table has a trap in it.** The DC-by-level table was **revised by errata**, and the two
> versions give materially different numbers. `dc_by_level` has a `_printing` field — write in
> which printing yours came from (e.g. `"Rules Compendium, 2010"` or `"DMG, first printing"`),
> because a campaign that mixes the two will drift and nobody will be able to see why.

Nothing else in the framework is blocked. Rolling, state, conditions, the encounter tracker,
rests, healing surges, the living history and every shared tool work immediately.

---

## The documents in this folder

Each **replaces** the root `system/` document of the same number for a campaign with
`System: dnd4e`. Where there is no file here, the root one applies to all three rulesets.

| | |
|---|---|
| `02-character-creation.md` | Building a 4e character, and the solo adjustments |
| `03-difficulty-and-solo-levers.md` | A party of one in a game built hard around a party of five |
| `06-encounter-runner.md` | Running a 4e fight: the turn, the grid, marks and immediate actions |
| `07-encounter-building.md` | The XP budget, roles and ranks — and what it refuses until you fill the tables |
| `09-loot-and-economy.md` | Parcels, item levels, and the coin ratio that is not the other games' |
| `10-downtime-travel-and-rest.md` | Short and extended rests, and the surge pool as the real clock |
| `11-leveling-up.md` | Thirty levels in three tiers, and what each level actually gives |
| `12-rules-quick-reference.md` | The cheat sheet — read this one, not the root one |

---

## The three things most likely to go wrong

1. **Reaching for the wrong game's crit rule.** Pathfinder doubles the whole damage roll. D&D
   2024 doubles the damage dice. **4e rolls nothing and takes the maximum.** Three answers,
   and only `roll.py damage --crit` on a `dnd4e` campaign gives the third.
2. **Saying "advantage".** 4e has no two-dice swing under any name. Combat advantage is a flat
   **+2 to the attack roll**. `roll.py` refuses `--advantage` on a 4e campaign and says so.
3. **Treating hit points as bottoming out at zero.** They do not. A 4e character dies at a
   negative total equal to their bloodied value, so `damage` keeps a `hp_below_zero` figure
   and the death threshold is a real number on the sheet. Look at it.

## Where 4e sits in the shared world

`System: dnd4e` campaigns share the **universe** with the other two but, by design, not the
region. See `system/23-cross-system-worlds.md` and `worlds/UNIVERSE.md`: events, people and
reputations cross between worlds; levels, DCs, defences, monster levels, treasure parcels and
stat blocks never do. A 4e level is drawn from a thirty-level scale that neither sibling has,
which is the clearest case in the framework for why only **scope bands** translate.
