# PF2e_Claude

A kit for running **Pathfinder Second Edition (Remaster)** campaigns with Claude as Game Master,
built for solo and very small tables.

The framework is built. `PROMPT.md` is the specification it was built from, kept for reference.

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
CLAUDE.md              auto-loaded GM operating contract — the seven rules and the boot sequence
README.md              this file
DESIGN_NOTES.md        assumptions, decisions made without the user, and the "to verify" list
LICENSE_NOTES.md       ORC and Paizo Community Use attribution; what this repo does and does not copy
PROMPT.md              the original specification
EXTRAS.md              what was deliberately left out, and the failure modes to watch for

system/                campaign-agnostic rules of engagement — 23 documents
tools/                 all dice and all math; standard-library Python only
templates/             copied into a new campaign folder by tools/new_campaign.py
worlds/                OPTIONAL shared settings, one folder each
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

Intake is an interview, a few questions at a time, with concrete example answers and a "roll it"
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
```

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
- **Numbers get verified, not remembered.** Every table carries a `Source:` line, and anything that
  could not be checked says `⚠ UNVERIFIED` rather than guessing quietly.
  `python3 tools/pf2e.py sources` prints the lot.
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

## Two things to know before you trust it with a long campaign

- **The treasure-by-level table is unverified.** So are travel speeds, settlement item levels, and a
  handful of smaller values. `DESIGN_NOTES.md` lists every one of them under "To verify before first
  play", and each is marked in place. Nothing is silently guessed, but nothing unverified should be
  used to make a pacing decision without a look at the book first.
- **The mid-combat restore has been tested but not played.** `DESIGN_NOTES.md` shows the test. Run
  one real fight and take a checkpoint in the middle of it before trusting it with a long one.
