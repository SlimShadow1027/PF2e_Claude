# PF2e_Claude

A kit for running campaigns with Claude as Game Master, built for solo and very small tables.

**Three rulesets, one framework:**

| `System:` | Game | Rules module | Ruleset docs | Numbers ship? |
|---|---|---|---|---|
| `pf2e` | Pathfinder Second Edition (Remaster) | `tools/pf2e.py` | the numbered docs in `system/` | yes, under ORC |
| `dnd5e` | fifth edition, 2024 revision ("5.5e") | `tools/dnd5e.py` | `system/dnd5e/` | yes, under CC-BY-4.0 |
| `dnd4e` | fourth edition | `tools/dnd4e.py` | `system/dnd4e/` | **no — you supply them** |

A campaign declares one and the tools dispatch on it. They also **refuse another game's commands
and name the right one**, because the failure mode worth preventing is not a crash — it is a GM
quietly running one game's procedure at another game's table. Asking for Hero Points in a 5.5e
campaign points you at Heroic Inspiration; asking for a recovery check points you at death saving
throws; asking for Advantage in a 4e campaign is refused, because 4e has no such mechanic and its
combat advantage is a flat +2; putting electrum in a Pathfinder purse is refused by name.

```
python3 tools/rules.py list                 # the rulesets and their aliases
python3 tools/rules.py which <campaign>     # which game a campaign runs
```

> **4e is the asymmetric one, and you should know before you pick it.** D&D 4th Edition has **no
> open-content release** — the Game System License permitted no Open Game Content, not even stat
> blocks, and is no longer offered. So this framework ships 4e **procedure, stated in its own
> words**, and **no 4e numbers at all**. The advancement table, the encounter budget, the
> DC-by-level table, the treasure parcels and the item prices live in `tools/dnd4e_tables.json`,
> which ships **empty**; you transcribe what you need from books you own, and until you do the
> tools **refuse to compute and name the book**. A heroic-tier campaign needs three of the nine
> tables. Everything else — rolling, state, conditions, combat, rests, the shared world — works
> immediately. Read `system/dnd4e/README.md` first; `LICENSE_NOTES.md` has the legal statement.

A **shared world can hold campaigns of any of the three**, and a **universe can hold worlds that
share nothing but their cosmology** — which is the other thing this framework is for. See "The
shared world" below.

The framework is built. `PROMPT.md` is the specification the Pathfinder half was built from, kept
for reference.

Two properties this is designed around, because they are the two that make an automated GM
trustworthy:

- **Dice are genuinely rolled by code, and auditable afterward.** Every die face comes out of
  `tools/roll.py` using `random.SystemRandom`, and every roll — public, private or secret — is
  appended to a log you can read and analyse. Secret rolls are *rolled*; only the display is
  withheld. `tools/analyze.py` compares the public and private subsets side by side, so a GM
  quietly tilting hidden rolls would be visible.
- **Campaign state does not drift across sessions.** Every volatile number lives in one
  machine-readable place, mutated only through a tool that refuses impossible states. Checkpoints
  are git commits, restores are real restores, and a checkpoint taken in round 3 of a fight restores
  the whole encounter tracker.

## Layout

```
CLAUDE.md              auto-loaded GM operating contract — the eight rules and the boot sequence
README.md              this file
DESIGN_NOTES.md        assumptions, decisions made without the user, and the "to verify" list
ACCEPTANCE.md          the transcript of the acceptance run, including what failed first
LICENSE_NOTES.md       attribution for all three — ORC, CC-BY-4.0, and one with no open content
PROMPT.md              the original specification
EXTRAS.md              what was deliberately left out, and the failure modes to watch for

system/                rules of engagement — 17 shared documents, plus:
system/dnd5e/            the 8 where fifth edition needs a different answer
system/dnd4e/            the 8 where fourth edition does, plus a README to read first
tools/                 all dice and all math; standard-library Python only
  rules.py               which game a campaign runs; the calendar; cross-system translation
  pf2e.py                Pathfinder tables, each with a Source: line
  dnd5e.py               fifth-edition tables, same discipline
  dnd4e.py               fourth-edition procedure; NO tables, because none are open content
  dnd4e_tables.json      ships empty — the 4e numbers you transcribe from your own books
templates/             copied into a new campaign folder by tools/new_campaign.py
worlds/                OPTIONAL shared settings, one folder each — system-neutral
campaigns/             generated campaigns live here, one folder each
.claude/commands/      slash commands
```

## How to start playing

### 1. Create a campaign

In a fresh Claude Code session in this repository:

```
Read CLAUDE.md and system/01-campaign-intake.md, then walk me through creating a new campaign.
Interview me a few questions at a time. When intake is done, give me three one-page pitches and
wait for my pick before generating anything else.
```

Or type `/newcampaign "The Ashen Covenant"`.

**Intake asks which game first**, because everything after it comes out of a different document
depending on the answer. If you have no preference, two questions usually settle it: do you want
to spend time building the character or start playing in five minutes, and do you want the dice to
tell you *how well* or just *whether*. Then:

```
python3 tools/new_campaign.py "The Ashen Covenant" --system pf2e
python3 tools/new_campaign.py "The Ashen Covenant" --system 5.5e
python3 tools/new_campaign.py "The Ashen Covenant" --system 4e
```

`--system` is required. Nothing defaults, because a campaign scaffolded under the wrong ruleset
carries the wrong calendar, the wrong character sheet and the wrong rules documents from its first
file.

The rest is an interview, a few questions at a time, with concrete example answers and a "roll it"
option on every question. It ends with three pitches and a pause — no world is built until you
approve one.

### 2. Make a character

```
Read CLAUDE.md, system/02-character-creation.md and system/03-difficulty-and-solo-levers.md, plus
campaigns/<slug>/CAMPAIGN.md. Walk me through making my character for this campaign, then propose a
difficulty preset and the party structure you'd recommend for it.
```

Three paths: **quick build** (playing in five minutes), **guided** (step by step), or **import**
(paste a Pathbuilder sheet and it gets parsed and re-derived).

### 3. Play

```
Read CLAUDE.md and campaigns/<slug>/. Begin session 1. Open on a scene that gives me something to
decide in the first three sentences.
```

### 4. Resume, any time later

```
Resume campaign <slug>. Run the boot sequence from system/15-continuity-and-context-recovery.md,
give me a recap, confirm the situation, then pick up where we left off.
```

Or `/resume <slug>`.

## What you can type mid-game

| | |
|---|---|
| `status` `sheet` `inventory` `options` `map` | the numbers, right now |
| `checkpoint` `rewind [to …]` | save, and unwind — rewinding is a legitimate move and the GM will not resist it |
| `recap` `end session` | open and close |
| `rules: <q>` | a rules answer **with its source** |
| `ooc:` `meta:` | out of character, and adjust difficulty or pacing mid-game |
| `oracle <question>` | ask the fiction directly; the answer is binding on the GM |
| `flags` | what you asked the campaign to deliver, and whether it has |
| `dice audit` | the fairness report over every roll ever made |
| `dashboard` `worldprep` | the HTML dashboard, and an off-screen turn |
| `pause` `fade` `cut` `dial it back` `dial it up` | the safety tools |

Plus each game's own resources, which the tools refuse on another game's campaign:

| | |
|---|---|
| **Pathfinder** | `hero point` `refocus` `recovery` |
| **fifth edition** | `inspiration` `short rest` `long rest` `hit dice` `death save` `concentration` `attune` |
| **fourth edition** | `surge` `second wind` `action point` `milestone` `power` `short rest` `extended rest` `death save` |

Slash commands for the ones worth a keystroke: `/checkpoint` `/recap` `/status` `/sheet`
`/levelup` `/encounter` `/dashboard` `/dice-audit` `/worldprep` `/oracle` `/endsession`
`/newcampaign` `/resume`.

Full list: `system/14-player-commands.md`.

## The tools

Standard-library Python only. Nothing to install, no build step.

```
python3 tools/roll.py check "1d20+5" --dc 15          # real dice, with the degree of success
python3 tools/state.py --campaign X damage kaelen 12  # the only writer of state.json
python3 tools/pf2e.py encounter --party-level 3 --party-size 1 --threat moderate
python3 tools/pf2e.py sources                         # provenance of every table
python3 tools/new_campaign.py "The Ashen Covenant"
python3 tools/validate.py --campaign X                # catches mechanical drift
python3 tools/oracle.py ask "Is the gate guarded?" --odds unlikely
python3 tools/analyze.py --campaign X --fairness      # audit the dice
python3 tools/dashboard.py --campaign X               # offline HTML dashboard
python3 tools/world.py as-of verdant-reach "4712 AR"  # date-gated shared-world read
python3 tools/graph.py --campaign X                   # NPC relationship graph

python3 tools/rules.py which third-beginnings         # which game a campaign runs
python3 tools/dnd5e.py encounter --party-level 3 --party-size 1 --threat moderate
python3 tools/dnd5e.py sources                        # provenance, and what is convention
python3 tools/world.py convert --level 7 --from pf2e --to dnd5e

python3 tools/dnd4e.py tables                         # which 4e numbers you still have to supply
python3 tools/dnd4e.py mechanics                      # 4e's shape, stated not quoted
python3 tools/dnd4e.py sources                        # and why its provenance is weaker
python3 tools/world.py universe                       # the worlds, and how they connect
```

## The shared world

`worlds/` is optional, off by default, and **system-neutral**: one world can hold campaigns of all
three rulesets at once, in different eras, with the date gate keeping each from being spoiled by
the other's future.

What makes that work is a single rule — **the world records what happened, never anyone's
numbers.** Events, people, places, debts and reputations cross between the games. Levels, DCs,
ACs, defences, CRs, monster levels, stat blocks and treasure do not, because the games' maths is
different in shape and not merely in scale.

Three layers of history sit under it, deliberately differing in precision:

| Layer | What it is |
|---|---|
| `CHRONICLE.md` | dated, terse, one line of visibility each — gated on the campaign's date |
| `HISTORY.md` | **the world's own book about itself.** Prose, spans rather than dates, the certainty of each account stated (`attested` · `recorded` · `disputed` · `legendary` · `lost`), and **no ruleset's numbers** — refused by the tool, not just discouraged |
| `<system>/<campaign>.md` | the **thorough** per-ruleset narrative. Read only by campaigns of that game, so it may name the rules, the power and the roll that turned a scene |

Above worlds there is a **universe**: `worlds/UNIVERSE.md` holds what is true across places, so a
campaign on another plane or in another age can be the same universe without sharing a single
faction, river or year. The shipped example has a Pathfinder world and a 4e world that share a
cosmology and a deep past and nothing else, connected by a route that runs one way only.

```
python3 tools/world.py history <world>                # the living history, date-gated
python3 tools/world.py history-add --world <w> ...    # append a chapter; refuses numbers
python3 tools/world.py narrative --campaign <slug>    # scaffold this campaign's own account
python3 tools/world.py universe                       # the register, rebuilt from the folders
```

The one translation the framework will make is **scope**: four bands naming the size of the thing
a character can plausibly threaten or protect, from `local` to `worldly`.

```
$ python3 tools/world.py convert --level 7 --from pf2e --to dnd5e
PF2e level 7 → scope band **regional**
  which is: a city and the land that feeds it; a barony; a stretch of coast
  in D&D 5.5e, that band is levels 5-10

A range, not a conversion. This deliberately will not:
  - converting a stat block: a CR 5 monster and a level 5 PF2e creature are not the same creature …
```

Chronicle entries carry a `System:` line and a `Scope:` line; `validate.py` warns when an entry
mentions a DC, an AC, a CR or a level, and `world.py history-add` **refuses outright**, because
the shared layer's reader may be playing a different game. `python3 tools/world.py crossing` is the full statement, and
`system/23-cross-system-worlds.md` is the reasoning — including why a cross-system world is
interesting rather than merely possible: the same place, seen through a different set of rules, and
a party whose numbers cannot reproduce what the last one did.

Full CLI reference: `tools/README.md`.

## Design principles the framework enforces

- **Dice are real.** Every roll comes out of `tools/roll.py` using a system random source, and every
  roll — public or private — is written to an append-only audit log you can read afterward.
- **Private is not the same as fudged.** Secret checks and enemy saves get rolled genuinely; only
  the display is withheld. The log records both, and `analyze.py` compares them.
- **Degrees of success are computed by the tool**, including the natural-20 and natural-1 shift, so
  the GM cannot decide an outcome and then produce a roll that matches it.
- **Creatures come from published stat blocks**, cited by source. Homebrew names its base creature.
  The validator fails a bestiary file with no source.
- **Numbers get verified, not remembered.** Every table carries a `Source:` line naming where it
  was read from, anything that is this framework's own convention rather than a published rule
  says so in place, and anything that could not be checked says `⚠ UNVERIFIED` rather than
  guessing quietly. `pf2e.py sources`, `dnd5e.py sources` and `dnd4e.py sources` print the lot —
  and each reports how many tables are *convention* as a separate count, because the three
  rulesets' open content is in three very different states.
- **Where a ruleset has no open content, the tool refuses instead of guessing.** 4e ships no
  numeric table at all. `dnd4e.py encounter`, `dc`, `treasure` and `advancement` raise and name
  the book and table to read from, rather than producing a figure nobody can trace. A refusal
  that names the page is more use than a confident guess, and in a framework whose first rule is
  "never write a number you did not roll", a guessed table is the same error one layer up.
- **A gap in the published rules is named, not filled from memory.** SRD 5.2 has no
  treasure-by-level table, no Earn Income equivalent, no creature adjustment templates and no
  calendar. The framework says so in each place and offers a convention that is labelled as one.
- **The rulesets never mix**, in a campaign or in a shared world. The tools refuse most crossings
  by name, and the licences require it too: ORC material and CC-BY-4.0 material cannot be
  relicensed into each other, and neither can absorb material from an edition with no open
  content at all.
- **One source of truth per kind of fact.** Volatile numbers live in `state.json`; prose and built
  character choices live in Markdown. `CHECKPOINT.md` is rendered from state, never hand-edited.
- **Impossible states are refused, not clamped.** HP above maximum, negative coins, spending a Hero
  Point you do not have — the tool says what is wrong instead of quietly fixing it.
- **A mid-combat checkpoint restores the whole fight** — initiative order, whose turn, actions
  spent, multiple attack penalty, reactions used, every combatant's HP and conditions, and map
  positions.
- **Every checkpoint is a git commit.** `git log` is the campaign's history; `git diff` between two
  checkpoints says exactly what changed; the roll log is committed alongside the state it produced,
  so the audit trail is tamper-evident.
- **The reaction obligation.** Before resolving any trigger, the GM checks your available reactions
  and asks — with a tracker column behind it, so "you have no reaction" is always backable.
- **Every fight has an objective**, telegraphed in the fiction, because a timer you cannot see is a
  trap rather than a tactical problem.
- **Nothing campaign-specific lives outside `campaigns/`.**

## Things to know before you trust it with a long campaign

- **The Pathfinder half has been played. The fifth-edition and fourth-edition halves have been
  tested but not played.** `ACCEPTANCE.md` holds what was exercised: a 5.5e campaign scaffolded, a
  character built, damage to 0 HP, death saves rolled to a resolution, massive damage, exhaustion
  to 6, the encounter tracker through a round, a checkpoint and a restore, and a cross-system
  world with both games promoting into it. The 4e half was exercised the same way — a character
  with four defences and a surge pool, damage past 0 into the below-zero track, a death saving
  throw rolled through `roll.py`, Second Wind, powers spent and restored, the three-action
  tracker with trade-down, both rests, the Verge calendar adopted by `world.py link`, and the
  living history gated on a world-defined calendar. That is the same bar the Pathfinder half was
  held to before its first session, and it is not the same thing as a session. Run one real fight
  and take a checkpoint in the middle of it before trusting any of them with a long campaign.
- **4e needs you to type in some tables before its maths works at all**, and that is permanent,
  not a to-do. See the box at the top of this file. The practical consequence: do not start a 4e
  session expecting to build an encounter on the fly unless
  `python3 tools/dnd4e.py tables` says the three you need are filled.
- **Fifth edition's open content has real gaps, and the framework names them rather than filling
  them.** SRD 5.2 publishes no treasure-by-level table, no Earn Income equivalent, no
  Elite/Weak-style creature adjustment and no calendar. Where an answer is needed anyway it is
  labelled as this framework's convention and `python3 tools/dnd5e.py sources` counts those
  separately. If you own the 2024 DMG, use its tables and record the deviation — the framework has
  a place for that in `RULES_DELTAS.md`.
- **Every Pathfinder rules table has been read from Archives of Nethys, and that pass found
  fourteen errors.** The framework was first built while AoN was unreachable and the numeric tables were
  checked against the Foundry VTT PF2e source instead, with five marked `⚠ UNVERIFIED`. When AoN
  became reachable, re-reading the published text found **eight wrong values in `tools/pf2e.py` and
  six more stated inline in `system/`** — most of them in tables that had *not* been flagged. They
  are all listed in `DESIGN_NOTES.md` under "Pass 2", corrected in place, and
  `python3 tools/pf2e.py sources` now reports 0 of 26 tables unverified. Two of the eight would
  have been felt immediately at a solo table: XP awards do **not** scale with party size, and the
  published Low encounter budget really does collapse to 0 XP at a party of one.
- **Every fifth-edition table was read from SRD 5.2 and then cross-checked against an independent
  implementation**, because the SRD was read from a Markdown transcription of the official PDF
  rather than the PDF itself. The two sources agreed on all of them — the CR-to-XP table, the
  cumulative advancement thresholds, the XP-budget-per-character table and the coin ratios matched
  value for value. `LICENSE_NOTES.md` names both sources and their commits.
- **The mid-combat restore has been tested but not played.** `ACCEPTANCE.md` holds the transcript:
  a checkpoint taken in the middle of round 3 of a four-combatant fight, and every tracker field
  restored identically. The 5.5e tracker restores the same way, with its own columns.
