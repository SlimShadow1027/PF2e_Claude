# Acceptance run

Every checkbox in section 26 of `PROMPT.md`, with the real output of the command that verified
it. Nothing here is a claim; it is a transcript, captured on the run that built the framework.

The test campaigns (`test-run`, `standalone-test`, `other-campaign`) and the test world
(`verdant-reach`) were created for these checks and deleted at the end — the last section shows
that. The commits they produced were reset out of the history, so the branch holds only framework
commits.

**Three checks failed on their first run and are recorded as fixed rather than as passes:**

1. `restore` rewound the checkpoint counter, so two different snapshots both took the number
   `002` and `restore 002` became ambiguous. Fixed in `tools/state.py` (`highest_checkpoint`), and
   check 6 below shows the numbering staying unique afterwards.
2. `validate.py` crashed with an unhandled `StateError` on a corrupted state, because
   `encounter_status` could not survive a combatant whose `ref` pointed at a missing character —
   a validator that dies on bad input is not a validator. Fixed in both files; check 12 shows it
   reporting 27 errors instead.
3. `world.py promote` appended to the chronicle at the end of the file, so a promotion dated
   earlier than an existing entry left the chronicle out of date order and failed its own
   validation. Fixed to insert by date; check 23 shows the ordering holding.

Two smaller ones: `state.py advance-time "backwards"` raised a traceback instead of refusing
cleanly (now caught), and `graph.py` turned the character template's unfilled relationship fields
into edges pointing at an empty node (now skipped).

## Contents

| Check | Section |
|---|---|
| 1, 2, 3 — the dice engine, the distribution, the degree shifts | [Dice](#dice) |
| 4, 5 — secret redaction, the campaign scaffold | [Scaffold and secret rolls](#scaffold-and-secret-rolls) |
| 6 — the state round-trip and restore | [State round-trip](#state-round-trip) |
| 7 — impossible-state refusals | [Refusals](#refusals) |
| 8 — the checkpoint commit | [The checkpoint commit](#the-checkpoint-commit) |
| 9, 10 — objectives, the reaction obligation | [Encounter documents](#encounter-documents) |
| 11 — the encounter budget and table sources | [Encounter budget](#encounter-budget) |
| 12 — the validator, clean and corrupted | [Validation](#validation) |
| 13, 14 — fair versus biased logs | [Roll-log analytics](#roll-log-analytics) |
| 15, 16 — the dashboard | [Dashboard](#dashboard) |
| 17, 18 — the off-screen turn and its Routine prompt | [Off-screen turn](#off-screen-turn) |
| 19, 20 — the oracle ladder | [Oracle](#oracle) |
| 21, 22 — flags | [Flags and session flow](#flags-and-session-flow) |
| 23, 24, 25, 26 — the shared world, the date gate, `World: none` | [Shared world](#shared-world) |
| 27 — the mid-combat restore | [Mid-combat restore](#mid-combat-restore) |
| 28 — the relationship graph | [Relationship graph](#relationship-graph) |
| 29, 30, 31 — session flow, structure, table provenance | [Structure and provenance](#structure-and-provenance) |
| 32 — deleting the test campaigns | [Cleanup](#cleanup) |

---

## Dice

```
=== [1] roll.py check produces a real roll with a correct degree ===
🎲 check: 1d20+5 → [8] +5 = 13 vs DC 15 → FAILURE
🎲 check: 1d20+5 → [15] +5 = 20 vs DC 15 → SUCCESS
🎲 check: 1d20+5 → [3] +5 = 8 vs DC 15 → FAILURE
🎲 check: 1d20+5 → [6] +5 = 11 vs DC 15 → FAILURE

=== [2] 10,000 rolls of 1d20+5: mean near 15.5, faces 1-20 covered ===
n            = 10000
mean         = 15.5923   (expected 15.5, standard error 0.0577 -> 1.60 s.e.)
min / max    = 6 / 25   (possible range 6-25)
faces seen   = 20/20   missing: none
chi-square   = 15.98 on 19 df   (95% critical value 30.14)

histogram (face, count, deviation from 500):
   1   472    -28  #######################################
   2   507     +7  ##########################################
   3   493     -7  ########################################
   4   496     -4  #########################################
   5   513    +13  ##########################################
   6   470    -30  #######################################
   7   532    +32  ############################################
   8   470    -30  #######################################
   9   489    -11  ########################################
  10   484    -16  ########################################
  11   478    -22  #######################################
  12   509     +9  ##########################################
  13   489    -11  ########################################
  14   529    +29  ###########################################
  15   511    +11  ##########################################
  16   488    -12  ########################################
  17   521    +21  ###########################################
  18   537    +37  ############################################
  19   501     +1  #########################################
  20   511    +11  ##########################################

=== [3] natural 20 below the DC upgrades; natural 1 above it downgrades ===
Forced cases through the degree function (the same code path roll.py uses):
 natural  total   DC        base degree -> final degree       shift
      20     14   15            failure -> success            +1   # nat 20, total below the DC
      20      5   25   critical failure -> failure            +1   # nat 20, total 20 below the DC
       1     26   15   critical success -> success            -1   # nat 1, total 11 above the DC
       1     16   15            success -> failure            -1   # nat 1, total 1 above the DC
      19     25   15   critical success -> critical success   +0   # no shift: nat 19
      20     25   15   critical success -> critical success   +0   # clamped: already a critical success
       1      4   15   critical failure -> critical failure   +0   # clamped: already a critical failure

--- and the same thing observed in real rolls, printed by the tool ---
upgrade  : 🎲 forced: 1d20+0 → [20] = 20 vs DC 15 → CRITICAL SUCCESS  [natural 20: upgraded from SUCCESS]
downgrade: (not observed in 4000 rolls)
ses use modifiers that force that:

natural 20, total below the DC          : 🎲 forced 1d20+0 vs DC 25: 1d20+0 → [20] = 20 vs DC 25 → SUCCESS  [natural 20: upgraded from FAILURE]
natural 20, total 10+ below the DC      : 🎲 forced 1d20+0 vs DC 35: 1d20+0 → [20] = 20 vs DC 35 → FAILURE  [natural 20: upgraded from CRITICAL FAILURE]
natural 1, total above the DC           : 🎲 forced 1d20+20 vs DC 15: 1d20+20 → [1] +20 = 21 vs DC 15 → FAILURE  [natural 1: downgraded from SUCCESS]
natural 1, total would have been a crit : 🎲 forced 1d20+24 vs DC 15: 1d20+24 → [1] +24 = 25 vs DC 15 → SUCCESS  [natural 1: downgraded from CRITICAL SUCCESS]
```

---

## Scaffold and secret rolls

```
=== [5] new_campaign.py 'Test Run' creates campaigns/test-run/ with no unreplaced placeholder ===
wrote campaigns/test-run/state.json and CHECKPOINT.md
dashboard → campaigns/test-run/dashboard.html (6255 bytes, no network, opens from file://)

campaigns/test-run/ created from templates/ — 19 file(s)
  + CAMPAIGN.md
  + CANON.md
  + CLOCKS.md
  + FLAGS.md
  + PLAYER_PREFS.md
  + QUESTS.md
  + RULES_DELTAS.md
  + TIMELINE.md
  + WORLD.md
  + characters/PARTY.md
  + encounters/active.md
  + encounters/history.md
  + gm-private/README.md
  + gm-private/secrets.md
  + gm-private/seeds.md
  + logs/loot.md
  + npcs/ROSTER.md
  + logs/rolls.jsonl
  + logs/dice-audit.md

No unreplaced {{PLACEHOLDER}} anywhere in the new folder.

Per-character, per-NPC, per-creature, per-map and per-session forms stay in templates/
with their placeholders intact. Copy one when you need it:
  templates/characters/_CHARACTER_TEMPLATE.md
  templates/npcs/_NPC_TEMPLATE.md
  templates/bestiary/_CREATURE_TEMPLATE.md
  templates/maps/_MAP_TEMPLATE.md
  templates/sessions/_SESSION_TEMPLATE.md
  templates/gm-private/prep/_PREP_TEMPLATE.md

Next: run the intake interview — system/01-campaign-intake.md. Nothing in this folder is
decided yet; the defaults exist so the scaffold is valid, not so it is finished.

--- every file in the new folder, and a repo-wide grep for {{PLACEHOLDER}} inside it ---
  campaigns/test-run/CAMPAIGN.md
  campaigns/test-run/CANON.md
  campaigns/test-run/CHECKPOINT.md
  campaigns/test-run/CLOCKS.md
  campaigns/test-run/FLAGS.md
  campaigns/test-run/PLAYER_PREFS.md
  campaigns/test-run/QUESTS.md
  campaigns/test-run/RULES_DELTAS.md
  campaigns/test-run/TIMELINE.md
  campaigns/test-run/WORLD.md
  campaigns/test-run/bestiary/.gitkeep
  campaigns/test-run/characters/PARTY.md
  campaigns/test-run/checkpoints/.gitkeep
  campaigns/test-run/dashboard.html
  campaigns/test-run/encounters/active.md
  campaigns/test-run/encounters/history.md
  campaigns/test-run/gm-private/README.md
  campaigns/test-run/gm-private/prep/.gitkeep
  campaigns/test-run/gm-private/secrets.md
  campaigns/test-run/gm-private/seeds.md
  campaigns/test-run/logs/dice-audit.md
  campaigns/test-run/logs/loot.md
  campaigns/test-run/logs/rolls.jsonl
  campaigns/test-run/maps/.gitkeep
  campaigns/test-run/npcs/ROSTER.md
  campaigns/test-run/sessions/.gitkeep
  campaigns/test-run/state.json

grep -rn '{{[A-Z0-9_]*}}' campaigns/test-run/ :
  (no matches — nothing unreplaced)

=== [4] --secret redacts the chat line but writes full detail to rolls.jsonl ===
--- what the player sees ---
🎲 (secret) Recall Knowledge (Religion) — rolled, result withheld
--- and one public roll for contrast ---
🎲 Kaelen — Strike (longsword): 1d20+13 → [15] +13 = 28 vs DC 21 → SUCCESS

--- what rolls.jsonl actually holds for the secret one ---
{
  "seq": 1,
  "ts": "2026-09-30T03:21:52Z",
  "schema": 1,
  "tool_version": "1.0.0",
  "rng": "random.SystemRandom",
  "campaign": "test-run",
  "session": null,
  "checkpoint": null,
  "kind": "check",
  "actor": null,
  "label": "Recall Knowledge (Religion)",
  "expr": "1d20+9",
  "dice": [
    {
      "expr": "1d20",
      "sign": 1,
      "count": 1,
      "faces": 20,
      "rolls": [
        8
      ],
      "kept": [
        8
      ],
      "dropped": [],
      "rerolled": []
    }
  ],
  "modifier": 9,
  "natural": 8,
  "total": 17,
  "dc": 24,
  "secret": true,
  "private": false,
  "shown": false,
  "transparency": "standard",
  "tags": [],
  "damage_type": null,
  "crit": false,
  "map_step": null,
  "fortune": false,
  "misfortune": false,
  "detail": "\ud83c\udfb2 Recall Knowledge (Religion): 1d20+9 \u2192 [8] +9 = 17 vs DC 24 \u2192 FAILURE",
  "degree": "failure",
  "degree_index": 1,
  "unadjusted_degree": "failure",
  "degree_shift": 0,
  "nat20": false,
  "nat1": false
}

--- confirming the withheld number is recoverable from the log and nothing else ---
secret roll seq 1: natural 8, total 17 vs DC 24 -> failure   shown=False
the chat line was: (the log keeps it)  -> 🎲 Recall Knowledge (Religion): 1d20+9 → [8] +9 = 17 vs DC 24 → FAILURE
cat: /tmp/claude-0/-home-user-PF2e-Claude/614552ad-0188-5da3-936b-ced203e9e078/scratchpad/ac/02-scaffold.txt: input file is output file
```

---

## State round-trip

```
=== [6] state.py round-trip: damage, condition add, gold change, render, checkpoint, restore ===

--- checkpoint the starting state, so there is something to restore to ---
checkpoint 001: before the round-trip
wrote campaigns/test-run/checkpoints/001-before-the-round-trip.md
dashboard regenerated
committed 8be543c — checkpoint 001: before the round-trip

--- BEFORE ---
  HP {"current":22,"max":22,"temp":0} | conds [] | purse {"pp":0,"gp":40,"sp":5,"cp":0} | hero 3 | potions 2 | XP 0 | clock-min 480

--- MUTATE ---
Kaelen HP 10/22
Kaelen: frightened 2 added (2 rounds)
party spends 5 gp → 35 gp, 5 sp
Kaelen spends 1 Hero Point → 2 left
Kaelen: Healing Potion (Lesser) ×1
party XP: 80
4 hours passes: 1 Abadius 4725 AR, 08:00 → 1 Abadius 4725 AR, 12:00

--- re-render CHECKPOINT.md from state, then checkpoint the mutated state ---
rewrote campaigns/test-run/CHECKPOINT.md from state.json
checkpoint 002: after the round-trip mutations
wrote campaigns/test-run/checkpoints/002-after-the-round-trip-mutations.md
dashboard regenerated
committed cf1f79f — checkpoint 002: after the round-trip mutations

--- AFTER MUTATION ---
  HP {"current":10,"max":22,"temp":0} | conds [{"name":"frightened","value":2,"duration":{"kind":"rounds","remaining":2},"source":"Demoralize"}] | purse {"pp":0,"gp":35,"sp":5,"cp":0} | hero 2 | potions 1 | XP 80 | clock-min 720

--- RESTORE checkpoint 001 ---
restored campaigns/test-run/checkpoints/001-before-the-round-trip.md
state.json and CHECKPOINT.md now match checkpoint 001
dashboard regenerated
committed the rewind (f380641)
Narrate from the snapshot's situation paragraph. Rewinding is a legitimate table move.

--- AFTER RESTORE ---
  HP {"current":22,"max":22,"temp":0} | conds [] | purse {"pp":0,"gp":40,"sp":5,"cp":0} | hero 3 | potions 2 | XP 0 | clock-min 480

=== the same round-trip, proved by diffing the whole of state.json ===
top-level fields that changed: clocks, location, party, pcs, quests, time

RESULT: PASS — after restoring checkpoint 001, every field of state.json is identical to
        the pre-change state, except the three bookkeeping fields below.

The three excluded fields, and why:
  updated_at         — a wall-clock timestamp; it moves on every write by design.
  last_checkpoint    — 001 'before the round-trip': correct, that is the
                       checkpoint we are standing on.
  checkpoint_counter — 3, NOT rewound to 1. A restore is history, not an
                       erasure, so the next checkpoint takes a fresh number and
                       `restore NNN` can never be ambiguous between two snapshots.

Snapshots on file — every number distinct, none overwritten:
  001-before-the-round-trip.md
  002-after-the-round-trip-mutations.md
  003-a-second-round-of-mutations.md

A checkpoint taken after the restore:
  001-before-the-round-trip.md
  002-after-the-round-trip-mutations.md
  003-a-second-round-of-mutations.md
  004-one-more-to-show-the-numbering-continues.md
```

---

## Refusals

```
=== [7] state.py refuses an impossible state with a clear error ===

Each block is a refused mutation. "exit 2" is the refusal status; nothing was written.

$ state.py --campaign test-run hp kaelen --current 99
    state.py: refused: current HP 99 is above maximum 22 — refusing rather than clamping
    -> exit 2

$ state.py --campaign test-run hp kaelen --current -1
    state.py: refused: current HP of -1 is impossible; 0 is the floor and dying tracks the rest
    -> exit 2

$ state.py --campaign test-run damage kaelen -5
    state.py: refused: damage of -5 is not damage; use `heal`
    -> exit 2

$ state.py --campaign test-run hero spend kaelen 9
    state.py: refused: Kaelen has 3 Hero Point(s) and cannot spend 9
    -> exit 2

$ state.py --campaign test-run focus spend kaelen 5
    state.py: refused: Kaelen has 2 Focus Point(s) and cannot spend 5
    -> exit 2

$ state.py --campaign test-run slots use kaelen 1 3
    state.py: refused: Kaelen has 2 rank-1 slot(s) and 0 already used
    -> exit 2

$ state.py --campaign test-run gold spend 500gp
    state.py: refused: the party holds 40 gp, 5 sp (worth 4050 cp) and cannot part with 500 gp (worth 50000 cp) — refusing to go negative
    -> exit 2

$ state.py --campaign test-run condition add kaelen frightened
    state.py: refused: frightened always carries a value — say how much
    -> exit 2

$ state.py --campaign test-run condition add kaelen sparkly 2
    state.py: refused: 'sparkly' is not a PF2e condition. Known: blinded, broken, clumsy, concealed, confused, controlled, cursebound, dazzled, deafened, doomed, drained, dying, encumbered, enfeebled, fascinated, fatigued, fleeing, friendly, frightened, grabbed, helpful, hidden, hostile, immobilized, indifferent, invisible, observed, off-guard, paralyzed, persistent-damage, petrified, prone, quickened, restrained, sickened, slowed, stunned, stupefied, unconscious, undetected, unfriendly, unnoticed, wounded
    -> exit 2

$ state.py --campaign test-run condition add kaelen prone 2
    state.py: refused: prone does not take a value
    -> exit 2

$ state.py --campaign test-run condition add kaelen dying 2
    state.py: refused: dying is tracked as its own field, not as a condition entry — use `dying set <who> <value>` so there is only one copy of the number
    -> exit 2

$ state.py --campaign test-run condition remove kaelen blinded
    state.py: refused: Kaelen does not have blinded
    -> exit 2

$ state.py --campaign test-run item remove Healing Potion (Lesser) 9 --owner kaelen
    state.py: refused: Kaelen holds 2 × Healing Potion (Lesser) and cannot give up 9
    -> exit 2

$ state.py --campaign test-run item use Nonexistent Wand --owner kaelen
    state.py: refused: Kaelen has no item called 'Nonexistent Wand'
    -> exit 2

$ state.py --campaign test-run damage nobody 5
    state.py: refused: no character 'nobody' in state.json (known: kaelen)
    -> exit 2

$ state.py --campaign test-run clock advance No such clock 1
    state.py: refused: no clock called 'No such clock' (have: none)
    -> exit 2

$ state.py --campaign test-run advance-time backwards
    state.py: refused: cannot read a span of time out of 'backwards' (try '4 hours', '10 minutes', '1 day')
    -> exit 2

$ state.py --campaign test-run restore 999
    state.py: refused: no checkpoint '999' (have: 001-before-the-round-trip, 002-after-the-round-trip-mutations, 003-a-second-round-of-mutations, 004-one-more-to-show-the-numbering-continues)
    -> exit 2

$ state.py --campaign test-run xp set -50
    state.py: refused: XP cannot be negative
    -> exit 2

--- and two that are legal but worth showing, because they do NOT refuse ---

$ state.py --campaign test-run heal kaelen 500
    healing capped at maximum: 0 of 500 applied
    Kaelen HP 22/22
    -> exit 0

    (healing over the maximum is legal in PF2e — the excess is wasted, and the tool
     says how much it discarded rather than silently absorbing it.)

$ state.py --campaign test-run encounter start 'A fight with no objective'
    usage: state.py encounter start [-h] --objective OBJECTIVE [--map MAP_SLUG]
                                    name
    state.py encounter start: error: the following arguments are required: --objective
    -> exit 2
    (every encounter names its objective — system/17-encounter-objectives.md)
```

---

## The checkpoint commit

```
=== [8] checkpoint produces a git commit containing state.json, CHECKPOINT.md and the
        roll-log lines since the previous checkpoint ===

--- roll-log length before the rolls ---
  rolls.jsonl: 2 line(s)

--- make some rolls, and change some state, since the last checkpoint ---
🎲 Kaelen — Strike (longsword): 1d20+13 → [11] +13 = 24 vs DC 21 → SUCCESS
🎲 Kaelen — Longsword: 1d8+4 → [6] +4 = 10 slashing
🎲 Ghoul A — Fortitude vs Fireball: 1d20+11 → [11] +11 = 22 vs DC 22 → SUCCESS
🎲 Ghoul B — Fortitude vs Fireball: 1d20+11 → [1] +11 = 12 vs DC 22 → CRITICAL FAILURE
Kaelen HP 15/22

  rolls.jsonl: 6 line(s)

--- checkpoint ---
checkpoint 005: four rolls and some damage
wrote campaigns/test-run/checkpoints/005-four-rolls-and-some-damage.md
dashboard regenerated
committed c320610 — checkpoint 005: four rolls and some damage

=== git log --stat for that commit ===
commit c320610
author Claude
date   Wed Sep 30 03:25:17 2026 +0000

    checkpoint 005: four rolls and some damage


 campaigns/test-run/CHECKPOINT.md                   |   8 +-
 .../checkpoints/005-four-rolls-and-some-damage.md  | 142 +++++++++++++++++++++
 campaigns/test-run/dashboard.html                  |   8 +-
 campaigns/test-run/logs/rolls.jsonl                |   4 +
 campaigns/test-run/state.json                      |  16 +--
 5 files changed, 162 insertions(+), 16 deletions(-)

=== the diff to rolls.jsonl in that commit — exactly the lines rolled since the last one ===
  seq   3  check    Kaelen     Strike (longsword)                 natural 11 total  24 shown=True
  seq   4  damage   Kaelen     Longsword                          natural  6 total  10 shown=True
  seq   5  save     Ghoul A    Fortitude vs Fireball              natural 11 total  22 shown=True
  seq   6  save     Ghoul B    Fortitude vs Fireball              natural  1 total  12 shown=True

=== the diff to state.json in that commit ===
  -  "updated_at": "2026-09-30T03:24:26Z",
  +  "updated_at": "2026-09-30T03:25:17Z",
  -  "checkpoint_counter": 4,
  +  "checkpoint_counter": 5,
  -    "id": "004",
  -    "name": "one more, to show the numbering continues",
  -    "at": "2026-09-30T03:24:26Z",
  -    "slug": "one-more-to-show-the-numbering-continues"
  +    "id": "005",
  +    "name": "four rolls and some damage",
  +    "at": "2026-09-30T03:25:17Z",
  +    "slug": "four-rolls-and-some-damage"
  -        "current": 22,
  +        "current": 15,
  -    "situation": "Standing in the doorway of a test, having done nothing yet.",
  +    "situation": "Four rolls and seven points of damage into the test.",
```

---

## Encounter documents

```
=== [9] system/17-encounter-objectives.md has at least six objective categories, and
        encounters/history.md in the templates has an Objective: field ===

--- the numbered categories in system/17-encounter-objectives.md ---
  26:### 1. Timers
  41:### 2. Objectives that are not the enemy
  58:### 3. Morale and surrender
  74:### 4. Terrain that changes
  89:### 5. Retreat as a real option
  103:### 6. Escalation
  -> 6 categories

--- the Objective: field in templates/encounters/history.md ---
  4:without an `Objective:` field. The difficulty note at the end of each entry is what the
  15:- **Objective:** <the win condition other than "everything hostile is dead", or state that it

--- and state.py refuses to start an encounter without one ---
  state.py encounter start: error: the following arguments are required: --objective

=== [10] system/06-encounter-runner.md states the reaction obligation, and the
         per-round tracker format has a reaction-available column ===

--- the obligation ---
  ## The reaction obligation
  
  **Before resolving *any* trigger, check every party member's available reactions and ask the
  player before resolving.**
  
  Triggers that require the check:
  
  - A creature **moving out of reach** or **through a threatened square**.
  - An **incoming attack** (Shield Block, Nimble Dodge, and anything similar).
  - A **spell being cast within sight** (counterspell, and reactions that trigger on casting).
  - A creature **standing up from prone**, or otherwise taking a triggering action within reach.
  - A **readied action's** stated trigger firing.
  - Any class- or feat-specific reaction whose trigger the fiction has just produced.
  
  Reactive Strike, Shield Block, readied actions and class reactions are worth a large share of a
  character's power, and **forgetting to offer them is the most common way an automated GM quietly
  shortchanges the player.** It is a stated duty here, with a tracker column behind it.
  
  Ask in one line, before the trigger resolves, not after:
  
  > The ghoul steps out of your reach toward the porter. **Reactive Strike?** (+13 vs AC 15, your
  > reaction is available.)
  
  Spend it explicitly when the player says yes:
  
  ```
  python3 tools/state.py --campaign X encounter reaction Kaelen "Reactive Strike"
  ```
  
  Because the tracker records it, **"you have no reaction available" is always a statement that
  can be backed with the tracker** — say which trigger spent it and in which round.
  
  Reactions come back at the start of the holder's turn (`encounter next` does it). A reaction
  spent on another creature's turn stays spent until then.
  
  ---

--- the tracker's reaction column, and the tool's output ---
  44:| | Combatant | Init | HP | Actions | MAP | **Reaction** | Position | Conditions (with durations) |
  52:- **Reaction** is a column, not a footnote. See the obligation below.
  97:Reactions come back at the start of the holder's turn (`encounter next` does it). A reaction
```

---

## Encounter budget

> **Superseded, and worth reading as a failure.** The transcript below is the original run. Its
> budget table is **wrong**: it reports a Low budget of 15 XP at a party of one, from a Character
> Adjustment of 10/15/20/30/40. The published adjustment is **10/20/20/30/40** — Low and Moderate
> share the figure of 20 — so the published Low budget at a party of one is **0 XP**, not 15.
> The 15 came from the Foundry implementation's smoothed `partySize × 20` computation, which the
> original source line described accurately and which nobody checked against the book, because the
> table was not marked unverified. See **Verification pass 2** at the end of this file for the corrected output. This check passed; it was checking the wrong
> number.

```
=== [11] pf2e.py encounter reports a budget, and every table it uses has a Source: line ===

Party level 3, party size 1

XP budget by threat level:
  trivial      10 XP
  low          15 XP
  moderate     20 XP  <-- requested
  severe       30 XP
  extreme      40 XP

Source: GM Core, Encounter Budget (https://2e.aonprd.com/Rules.aspx?ID=575): 40/60/80/120/160 XP for a four-character party, adjusted 10/15/20/30/40 XP per character above or below four. Verified against foundryvtt/pf2e v8.5.1 @06b904d6ced9795c4c07af085e6f61a56f845c60 (ORC implementation citing Archives of Nethys inline), src/scripts/macros/xp/index.ts `generateEncounterBudgets`, which computes partySize x 20 and multiplies by 0.5/0.75/1/1.5/2 — identical for a party of four and identical to the per-character adjustment for any other size.

Build to 20 XP for a moderate encounter.

Solo/small-party warning: the budget already scales to 1 character(s), but the action economy does not. Several weak creatures are far deadlier at this party size than the XP says — see system/03-difficulty-and-solo-levers.md before spending the budget on a crowd.

--- and with a creature list, so the creature-XP and hazard tables are exercised too ---

Party level 3, party size 1

XP budget by threat level:
  trivial      10 XP
  low          15 XP
  moderate     20 XP
  severe       30 XP  <-- requested
  extreme      40 XP

Source: GM Core, Encounter Budget (https://2e.aonprd.com/Rules.aspx?ID=575): 40/60/80/120/160 XP for a four-character party, adjusted 10/15/20/30/40 XP per character above or below four. Verified against foundryvtt/pf2e v8.5.1 @06b904d6ced9795c4c07af085e6f61a56f845c60 (ORC implementation citing Archives of Nethys inline), src/scripts/macros/xp/index.ts `generateEncounterBudgets`, which computes partySize x 20 and multiplies by 0.5/0.75/1/1.5/2 — identical for a party of four and identical to the per-character adjustment for any other size.

Spent:
  ghoul (level 2) x2: 30 XP each = 60
  spiked pit (simple hazard, level 1): 4 XP

  total 64 XP → threat rating: EXTREME
  -34 XP against the requested severe budget of 30

Source: GM Core, Creature XP by level relative to the party (https://2e.aonprd.com/Rules.aspx?ID=575), and the Proficiency Without Level column (https://2e.aonprd.com/Rules.aspx?ID=1371). Verified against foundryvtt/pf2e v8.5.1 @06b904d6ced9795c4c07af085e6f61a56f845c60 (ORC implementation citing Archives of Nethys inline), src/scripts/macros/xp/index.ts `xpCreatureDifferences` and `xpVariantCreatureDifferences`.
Source: GM Core, Hazard XP: a simple hazard is worth a fifth of a creature of the same relative level; a complex hazard is worth the same as a creature. Verified against foundryvtt/pf2e v8.5.1 @06b904d6ced9795c4c07af085e6f61a56f845c60 (ORC implementation citing Archives of Nethys inline), src/scripts/macros/xp/index.ts `xpSimpleHazardDifferences` and `getHazardXp`.

Solo/small-party warning: the budget already scales to 1 character(s), but the action economy does not. Several weak creatures are far deadlier at this party size than the XP says — see system/03-difficulty-and-solo-levers.md before spending the budget on a crowd.

=== provenance of every table in tools/pf2e.py ===

Provenance of every table in tools/pf2e.py

[verified] calendar
    Golarion's Absalom Reckoning calendar maps month for month onto the Gregorian calendar (Abadius = January and so on) and keeps its month lengths; the weekdays are Moonday through Sunday. Verified against foundryvtt/pf2e v8.5.1 @06b904d6ced9795c4c07af085e6f61a56f845c60 (ORC implementation citing Archives of Nethys inline), the world clock's AR month and weekday tables in static/lang/en.json (PF2E.WorldClock.AR) and src/module/apps/world-clock/app.ts. Leap years are not modelled; see DESIGN_NOTES.md.

[⚠ UNVERIFIED] creature_adjustments
    GM Core, Elite and Weak adjustments (https://2e.aonprd.com/Rules.aspx?ID=1027 area). UNVERIFIED — the HP steps by level band could not be checked against a source reachable from this machine. The +/-2 to numbers is well established; confirm the HP column before leaning on it.

[verified] creature_xp
    GM Core, Creature XP by level relative to the party (https://2e.aonprd.com/Rules.aspx?ID=575), and the Proficiency Without Level column (https://2e.aonprd.com/Rules.aspx?ID=1371). Verified against foundryvtt/pf2e v8.5.1 @06b904d6ced9795c4c07af085e6f61a56f845c60 (ORC implementation citing Archives of Nethys inline), src/scripts/macros/xp/index.ts `xpCreatureDifferences` and `xpVariantCreatureDifferences`.

[verified] dc_adjustments
    GM Core, Adjusting Difficulty and the rarity adjustments (https://2e.aonprd.com/Rules.aspx?ID=555). Verified against foundryvtt/pf2e v8.5.1 @06b904d6ced9795c4c07af085e6f61a56f845c60 (ORC implementation citing Archives of Nethys inline), src/module/dc.ts `dcAdjustments` and `rarityToDCAdjustment` (uncommon → hard +2, rare → very hard +5, unique → incredibly hard +10).

[verified] degrees
    Player Core / GM Core, Degrees of Success (https://2e.aonprd.com/Rules.aspx?ID=552). Verified against foundryvtt/pf2e v8.5.1 @06b904d6ced9795c4c07af085e6f61a56f845c60 (ORC implementation citing Archives of Nethys inline), src/module/system/degree-of-success.ts.

[verified] dying
    Player Core, the Dying, Wounded and Doomed conditions and the recovery check. Verified against the Foundry VTT PF2e condition compendium (packs/pf2e/conditions/dying.json, wounded.json, doomed.json) and src/module/actor/creature/document.ts, where the maximum dying value is 4 and the recovery DC is 10 + the dying value.

[verified] earn_income
    Player Core, Earn Income — income per day by task level and proficiency, and the failure row. Verified against foundryvtt/pf2e v8.5.1 @06b904d6ced9795c4c07af085e6f61a56f845c60 (ORC implementation citing Archives of Nethys inline), src/scripts/macros/earn-income.ts `REWARDS_BY_LEVEL`.

[verified] encounter_budgets
    GM Core, Encounter Budget (https://2e.aonprd.com/Rules.aspx?ID=575): 40/60/80/120/160 XP for a four-character party, adjusted 10/15/20/30/40 XP per character above or below four. Verified against foundryvtt/pf2e v8.5.1 @06b904d6ced9795c4c07af085e6f61a56f845c60 (ORC implementation citing Archives of Nethys inline), src/scripts/macros/xp/index.ts `generateEncounterBudgets`, which computes partySize x 20 and multiplies by 0.5/0.75/1/1.5/2 — identical for a party of four and identical to the per-character adjustment for any other size.

[verified] hazard_xp
    GM Core, Hazard XP: a simple hazard is worth a fifth of a creature of the same relative level; a complex hazard is worth the same as a creature. Verified against foundryvtt/pf2e v8.5.1 @06b904d6ced9795c4c07af085e6f61a56f845c60 (ORC implementation citing Archives of Nethys inline), src/scripts/macros/xp/index.ts `xpSimpleHazardDifferences` and `getHazardXp`.

[verified] item_bonus_by_level
    GM Core variant rule Automatic Bonus Progression, which states the item-bonus curve the core math assumes: attack potency at levels 2/10/16, striking dice at 4/12/19, defence potency at 5/11/18, perception potency at 7/13/19, save potency at 8/14/20. Verified against foundryvtt/pf2e v8.5.1 @06b904d6ced9795c4c07af085e6f61a56f845c60 (ORC implementation citing Archives of Nethys inline), src/module/actor/character/automatic-bonus-progression.ts (`getAttackPotency`, `getStrikingDice`, `getDefensePotency`, `abpValues`).

[verified] level_dcs
    GM Core, DCs by Level (https://2e.aonprd.com/Rules.aspx?ID=552). Verified against foundryvtt/pf2e v8.5.1 @06b904d6ced9795c4c07af085e6f61a56f845c60 (ORC implementation citing Archives of Nethys inline), src/module/dc.ts `dcByLevel`.

[verified] map
    Player Core, Multiple Attack Penalty: -5/-10, or -4/-8 agile. Verified against foundryvtt/pf2e v8.5.1 @06b904d6ced9795c4c07af085e6f61a56f845c60 (ORC implementation citing Archives of Nethys inline), src/module/actor/helpers.ts `calculateMAPs`.

[⚠ UNVERIFIED] settlement_item_levels
    GM Core, settlement item-level availability. UNVERIFIED — the exact level cap per settlement size could not be checked from this machine. These are usable defaults, not quoted values; set them per campaign in WORLD.md and say so.

[verified] simple_dcs
    GM Core, Simple DCs (https://2e.aonprd.com/Rules.aspx?ID=552); the Proficiency Without Level column from the variant rule (https://2e.aonprd.com/Rules.aspx?ID=1370). Verified against foundryvtt/pf2e v8.5.1 @06b904d6ced9795c4c07af085e6f61a56f845c60 (ORC implementation citing Archives of Nethys inline), src/module/dc.ts `simpleDCs` / `simpleDCsWithoutLevel`.

[⚠ UNVERIFIED] travel_speed
    GM Core, Travel Speed. The 8-hour travel day is verified against foundryvtt/pf2e v8.5.1 @06b904d6ced9795c4c07af085e6f61a56f845c60 (ORC implementation citing Archives of Nethys inline), src/scripts/macros/travel/travel-speed.ts (`hoursPerDay = 8`), and feet per minute is Speed x 10. The miles-per-hour and miles-per-day columns are UNVERIFIED: they are derived from Speed / 10 miles per hour x 8 hours, which reproduces the familiar published rows, but the published table itself could not be checked from this machine.

[⚠ UNVERIFIED] treasure_by_level
    GM Core, Party Treasure by Level — total gp value of everything a FOUR-character party should find over one level. UNVERIFIED: the Foundry VTT system does not implement this table, and 2e.aonprd.com was unreachable, so these values come from the model's reading of GM Core rather than from a checked source. Verify every row before using it to pace a campaign's economy.

[⚠ UNVERIFIED] treasure_mix
    GM Core's guidance that a level's treasure splits roughly half permanent items, a quarter consumables and a quarter currency and valuables. UNVERIFIED — treat the split as a rule of thumb rather than a table.

5 of 17 tables are unverified: creature_adjustments, settlement_item_levels, travel_speed, treasure_by_level, treasure_mix

These are listed in DESIGN_NOTES.md under 'To verify before first play'.
```

---

## Validation

```
=== [12] validate.py passes on a fresh campaign, and catches a deliberately corrupted state ===

--- on the fresh campaign ---
$ python3 tools/validate.py --campaign test-run -v
campaign test-run: 0 error(s), 0 warning(s)
  ok    state.json parses
  ok    CHECKPOINT.md matches state.json
  ok    World: none — nothing references the shared-world layer

PASS — 0 errors, 0 warning(s)
-> exit 0

--- now break it on purpose: sixteen distinct kinds of corruption in state.json,
    plus an encounters/history.md entry with no Objective:, a bestiary file with no
    Source: line, and an unreplaced placeholder ---

$ python3 tools/validate.py --campaign test-run
campaign test-run: 27 error(s), 3 warning(s)
  warn  clock 'Overfull' is marked ticking but states no rate, so an off-screen turn cannot advance it
  warn  the live encounter's objective has not been telegraphed to the player; a timer the player cannot see is a trap, not a tactical problem
  warn  the encounter names map 'nowhere' but campaigns/test-run/maps/nowhere.md does not exist
  ERROR transparency mode 'translucent' is not one of glass/standard/mystery
  ERROR Kaelen: HP 40 is above maximum 22
  ERROR Kaelen: temporary HP -3 is negative
  ERROR Kaelen: wounded is negative (-1)
  ERROR Kaelen: 9 Hero Points, above the cap of 3
  ERROR Kaelen: dying 3 while at 40 HP — dying ends at 1 HP or more
  ERROR Kaelen: 5 Focus Points, above the pool maximum 2
  ERROR Kaelen: rank 1 has 4 of 2 slots used
  ERROR Kaelen: frightened carries no value but always takes one
  ERROR Kaelen: frightened has 0 rounds left but is still listed — expired conditions should be ticked off
  ERROR Kaelen: dying is in the conditions list as well as its own field — two copies of the same number
  ERROR Kaelen: 'sparkly' is not a PF2e condition
  ERROR Ghost is in state.json but has no sheet file at campaigns/test-run/characters/ghost.md
  ERROR the purse holds -5 gp — negative coins
  ERROR party XP is negative
  ERROR clock 'Overfull' is filled 9 of 6
  ERROR the live encounter has no objective — every encounter names one (system/17-encounter-objectives.md)
  ERROR the live encounter has duplicate combatant ids
  ERROR combatant A points at character 'nobody', which is not in pcs
  ERROR combatant A has negative actions remaining
  ERROR combatant A has MAP step 5; it runs 0-2
  ERROR combatant A duplicate id is not a party member and has no HP block
  ERROR the live encounter's turn_index 7 is outside its combatant list
  ERROR CHECKPOINT.md does not match state.json — state.json wins; run `python3 tools/state.py --campaign test-run render`
  ERROR campaigns/test-run/CANON.md still holds unreplaced placeholders: {{UNREPLACED_PLACEHOLDER}}
  ERROR campaigns/test-run/bestiary/unsourced-thing.md has no `Source:` line — creature statistics come from published material, cited by name, source and level
  ERROR encounters/history.md entry '001 — a fight with no objective recorded (1 Abadius 4725 AR)' has no `Objective:` field

FAIL — 27 error(s), 3 warning(s)
-> exit 1

--- put it all back, and it passes again ---
campaign test-run: 0 error(s), 0 warning(s)

PASS — 0 errors, 0 warning(s)
-> exit 0
```

---

## Roll-log analytics

```
=== [13] analyze.py on a synthetic log of 10,000 FAIR rolls, then on a biased one ===

The two logs are built by tools/roll.py itself. In the fair log every d20 comes out of
random.SystemRandom. In the biased log the public half is left fair and the PRIVATE half
has its faces overwritten with draws from 11-20, simulating a GM tilting hidden rolls.

--- FAIR: 10,000 rolls, half public and half private ---
  10000 roll(s) in scope.
  **All d20 rolls** — 10000 d20 face(s)
  - Mean **10.4133** against an expected 10.5. Standard error 0.0577, so the gap is -0.0867 — that is 1.50 standard errors.
  - Chi-square against a uniform d20: **28.32** on 19 degrees of freedom, p = **0.0775**.
  - Natural 20s: 550 against an expected 500.0 (5.50% vs 5.00%, s.e. 0.22%).
  - Natural 1s: 505 against an expected 500.0 (5.05% vs 5.00%, s.e. 0.22%).
  - Longest run of 11 or more: 14; of 10 or less: 15.
  **Public rolls (shown to the player)** — 5000 d20 face(s)
  - Mean **10.4162** against an expected 10.5. Standard error 0.0815, so the gap is -0.0838 — that is 1.03 standard errors.
  - Chi-square against a uniform d20: **24.45** on 19 degrees of freedom, p = **0.1795**.
  - Natural 20s: 272 against an expected 250.0 (5.44% vs 5.00%, s.e. 0.31%).
  - Natural 1s: 238 against an expected 250.0 (4.76% vs 5.00%, s.e. 0.31%).
  - Longest run of 11 or more: 10; of 10 or less: 12.
  **Private and secret rolls (number withheld)** — 5000 d20 face(s)
  - Mean **10.4104** against an expected 10.5. Standard error 0.0815, so the gap is -0.0896 — that is 1.10 standard errors.
  - Chi-square against a uniform d20: **16.45** on 19 degrees of freedom, p = **0.6272**.
  - Natural 20s: 278 against an expected 250.0 (5.56% vs 5.00%, s.e. 0.31%).
  - Natural 1s: 267 against an expected 250.0 (5.34% vs 5.00%, s.e. 0.31%).
  - Longest run of 11 or more: 10; of 10 or less: 9.

  What that adds up to:
  - · Public mean 10.416 (5000 faces) against private mean 10.410 (5000 faces): difference -0.006, 0.05 standard errors. No drift between what is shown and what is withheld.

--- BIASED: the same 10,000 rolls with the private half skewed high ---
  **All d20 rolls** — 10000 d20 face(s)
  - Mean **12.8872** against an expected 10.5. Standard error 0.0577, so the gap is +2.3872 — that is 41.40 standard errors.
  - Chi-square against a uniform d20: **2420.11** on 19 degrees of freedom, p = **0.0000**.
  - Natural 20s: 679 against an expected 500.0 (6.79% vs 5.00%, s.e. 0.22%).
  - Natural 1s: 235 against an expected 500.0 (2.35% vs 5.00%, s.e. 0.22%).
  **Public rolls (shown to the player)** — 5000 d20 face(s)
  - Mean **10.3350** against an expected 10.5. Standard error 0.0815, so the gap is -0.1650 — that is 2.02 standard errors.
  - Chi-square against a uniform d20: **28.66** on 19 degrees of freedom, p = **0.0716**.
  - Natural 20s: 218 against an expected 250.0 (4.36% vs 5.00%, s.e. 0.31%).
  - Natural 1s: 235 against an expected 250.0 (4.70% vs 5.00%, s.e. 0.31%).
  **Private and secret rolls (number withheld)** — 5000 d20 face(s)
  - Mean **15.4394** against an expected 10.5. Standard error 0.0815, so the gap is +4.9394 — that is 60.57 standard errors.
  - Chi-square against a uniform d20: **5011.73** on 19 degrees of freedom, p = **0.0000**.
  - Natural 20s: 461 against an expected 250.0 (9.22% vs 5.00%, s.e. 0.31%).
  - Natural 1s: 0 against an expected 250.0 (0.00% vs 5.00%, s.e. 0.31%).

  What that adds up to:
  - ⚠ all rolls: the face distribution is a poor fit to a uniform d20 (chi-square p = 0.0000 on 10000 faces). That is worth looking at.
  - ⚠ all rolls: mean 12.887 is +41.40 standard errors from 10.5.
  - ⚠ private rolls: the face distribution is a poor fit to a uniform d20 (chi-square p = 0.0000 on 5000 faces). That is worth looking at.
  - ⚠ private rolls: mean 15.439 is +60.57 standard errors from 10.5.
  - ⚠ Public mean 10.335 (5000 faces) against private mean 15.439 (5000 faces): difference +5.104, 44.26 standard errors. The two subsets do not look like the same die.

=== [14] analyze.py reports public and private rolls as separate subsets ===

The section headings it emits, from the fair log:
  ## Fairness
  **All d20 rolls** — 10000 d20 face(s)
  ### Public versus private
  **Public rolls (shown to the player)** — 5000 d20 face(s)
  **Private and secret rolls (number withheld)** — 5000 d20 face(s)
  ### What that adds up to
  ## Play
  ### Per character
  ### Per check
  ### Degrees of success
  ### Attack routines by multiple-attack-penalty step
  ### Hero Points
  ## Rolls by kind
```

```
=== analyze.py on the test campaign's real (small) log, to show it degrades honestly ===

# Dice audit — test-run

Generated 2026-09-30T03:37:04Z from `/home/user/PF2e_Claude/campaigns/test-run/logs/rolls.jsonl`.

13 roll(s) in scope.

## Fairness

Does the framework actually roll straight? Every number below carries its sample size and, where it applies, its standard error, so you can tell noise from a pattern yourself.

**All d20 rolls** — 12 d20 face(s)

- Mean **11.5000** against an expected 10.5. Standard error 1.6646, so the gap is +1.0000 — that is 0.60 standard errors.
- Chi-square against a uniform d20: **18.00** on 19 degrees of freedom, p = **0.5224**.
- Natural 20s: 0 against an expected 0.6 (0.00% vs 5.00%, s.e. 6.29%).
- Natural 1s: 1 against an expected 0.6 (8.33% vs 5.00%, s.e. 6.29%).
- Longest run of 11 or more: 3; of 10 or less: 1.

Face distribution:

```
 1       1     +0.4 ####################
 2       1     +0.4 ####################
 3       0     -0.6 
 4       1     +0.4 ####################
 5       0     -0.6 
 6       0     -0.6 
 7       0     -0.6 
 8       1     +0.4 ####################
 9       0     -0.6 
10       0     -0.6 
11       2     +1.4 ########################################
12       0     -0.6 
13       0     -0.6 
14       0     -0.6 
15       2     +1.4 ########################################
16       0     -0.6 
17       2     +1.4 ########################################
18       1     +0.4 ####################
19       1     +0.4 ####################
20       0     -0.6 
```

### Public versus private

This is the check that matters. A GM that quietly tilts secret checks and enemy saves would show up here and nowhere else, so the two subsets are reported side by side.

**Public rolls (shown to the player)** — 5 d20 face(s)

- Mean **9.8000** against an expected 10.5. Standard error 2.5788, so the gap is -0.7000 — that is 0.27 standard errors.
- Chi-square against a uniform d20: **15.00** on 19 degrees of freedom, p = **0.7226**.
- Natural 20s: 0 against an expected 0.2 (0.00% vs 5.00%, s.e. 9.75%).
- Natural 1s: 0 against an expected 0.2 (0.00% vs 5.00%, s.e. 9.75%).
- Longest run of 11 or more: 2; of 10 or less: 1.

Face distribution:

```
 1       0     -0.2 
 2       1     +0.8 ########################################

--- and the one-line session summary the end-of-session routine appends ---
Dice: 12 d20 face(s), mean 11.50 against 10.5 (s.e. 1.66), chi-square p = 0.522; public mean 9.80 over 5, private 12.71 over 7.
```

---

## Dashboard

```
=== [15] dashboard.py produces a single HTML file that opens from file:// with no
         network, renders at phone width, and respects the transparency mode ===

dashboard → campaigns/test-run/dashboard.html (10056 bytes, no network, opens from file://)

--- it is one file, and it fetches nothing ---
  size                        : 10056 bytes, 201 lines
  external src/href references: none
  <script> tags               : 0
  <link> tags                 : 0
  @import or url() in the CSS : none
  <style> blocks (CSS inlined): 1

--- phone width and theming ---
  viewport meta               : yes
  16px side gutter on body    : yes
  explicit background on body : yes
  single-column default grid  : yes
  min-width breakpoints       : ['620px', '900px']  (mobile-first: the default layout is the narrow one)
  prefers-color-scheme dark   : yes  (guarded by :root:not([data-theme="light"]))
  explicit dark override      : yes
  hard px widths over 400     : none  (only max-width caps: ['1100px'])
  overflow-x on wide content  : pre and table scroll in their own box

--- well-formedness ---
  doctype                     : <!doctype html>
  unclosed tags at EOF        : none
  mismatched close tags       : none
  generated-at line present   : yes
                                -> 2026-09-30T03:28:30Z, checkpoint 007

--- the transparency rule. This campaign is in 'standard' mode, and Ghoul A is at
    11/28 hit points in state.json ---
  transparency = standard
    Ghoul A    init 19   HP cell: 'badly hurt'
    Ghoul B    init 18   HP cell: 'unhurt'
    Kaelen     init 18   HP cell: '15 / 22'
    raw '11 / 28' anywhere in the file: absent  <- correct: the number is withheld

--- the same page in 'glass' mode, where showing the number is what the player asked for ---
    Ghoul A    init 19   HP cell: '11 / 28'
    Ghoul B    init 18   HP cell: '28 / 28'
    Kaelen     init 18   HP cell: '15 / 22'
    raw '11 / 28' anywhere in the file: present <- correct: glass mode shows everything
  (restored to standard)

--- what the page shows, section by section (headings only) ---
  Test Run
    - Party
    - Resources
    - Encounter — live
    - Inventory and money
    - Quests and clocks
    - Scene
    - Tactical map

=== [16] state.py checkpoint regenerates the dashboard as well as committing ===
  deleted dashboard.html — present? no
checkpoint 008: prove the dashboard is regenerated at every checkpoint
wrote campaigns/test-run/checkpoints/008-prove-the-dashboard-is-regenerated-at-every-checkpoint.md
dashboard regenerated
committed cdc3d92 — checkpoint 008: prove the dashboard is regenerated at every checkpoint
  present again? yes   10096 bytes

  and it is inside the commit:
     campaigns/test-run/CHECKPOINT.md                   |   4 +-
     ...dashboard-is-regenerated-at-every-checkpoint.md | 266 +++++++++++++++++++++
     campaigns/test-run/dashboard.html                  |   2 +-
     campaigns/test-run/state.json                      |   8 +-
     4 files changed, 273 insertions(+), 7 deletions(-)
```

---

## Off-screen turn

```
=== [17] a dry-run off-screen turn on test-run: writes a prep file, advances only
         scheduled clocks, leaves every player-state field byte-identical, and refuses
         to run when session_in_progress is set ===

--- first: it refuses while a session is live ---
session 1 started; off-screen turns will refuse to run
  session_in_progress = True

  The guard, as system/18-between-session-prep.md specifies it:
  $ python3 tools/state.py --campaign test-run get session_in_progress
  $ git status --porcelain -- campaigns/test-run
  -> REFUSED. session_in_progress=True; uncommitted files: 1 .
     Nothing was read, nothing was written, no clock moved.
     (the guard exited 3)

--- also refuses on an uncommitted campaign folder, even with no session live ---
  a stray uncommitted change:
     M campaigns/test-run/state.json
    ?? campaigns/test-run/logs/scratch.tmp
  -> REFUSED. session_in_progress=False; uncommitted files present.
     (the guard exited 3)

--- now clean, and the guard lets it through ---
  session_in_progress = False; uncommitted = 0

  clocks before the pass:
    Cult's Ritual: ▰▰▱▱▱▱ 2/6 — ticks 1 per week
    Grain shortage: ▱▱▱▱ 0/4

--- capture player state BEFORE ---
  captured pcs, party and time

--- run the pass: advance only the clock that is marked ticking with a stated rate,
    roll for the uncertain part with the real tool tagged offscreen, write the prep file ---
🎲 Does the Covenant find the second seal this week?: 1d20 → [19] = 19 vs DC 11 → SUCCESS
clock 'Cult's Ritual': ▰▰▰▱▱▱ 3/6

  (Grain shortage is NOT marked ticking and has no rate, so the pass does not touch it.)

  wrote campaigns/test-run/gm-private/prep/001-2026-09-30.md

  clocks after the pass:
    Cult's Ritual: ▰▰▰▱▱▱ 3/6 — ticks 1 per week
    Grain shortage: ▱▱▱▱ 0/4

--- capture player state AFTER, and diff ---

  $ diff pcs-before.json pcs-after.json
    (no output — byte-identical)
  $ diff party-before.json party-after.json
    (no output — byte-identical)
  $ diff time-before.json time-after.json
    (no output — byte-identical: the pass never advances in-world time)

  cmp, for completeness:
    pcs: IDENTICAL
    party: IDENTICAL
    time: IDENTICAL

--- and the git diff for the pass, showing exactly what it did change ---
     .../test-run/gm-private/prep/001-2026-09-30.md     | 75 ++++++++++++++++++++++
     campaigns/test-run/logs/rolls.jsonl                |  1 +
     campaigns/test-run/state.json                      |  2 +-
     3 files changed, 77 insertions(+), 1 deletion(-)

  the state.json diff — only the clock and the checkpoint bookkeeping:
    -      "filled": 2,
    +      "filled": 3,
```

```
=== [18] system/18-between-session-prep.md contains a standalone, copy-pasteable
         Routine prompt ===

  ### The Routine prompt — copy and paste this
  
  ```
  ...

  The prompt block, checked for the properties that make it standalone:
    fenced block found            : yes  (55 lines)
    names the campaign slug placeholder: yes
    points at this document       : yes
    states the concurrency guard inline: yes
    states the hard limits inline : yes
    never touch player state      : yes
    never advance in-world time   : yes
    never write under worlds/     : yes
    never contradict CANON.md     : yes
    never kill a named NPC        : yes
    requires the before/after diff: yes
    requires real rolls, tagged offscreen: yes
    tells it to validate and commit: yes
    tells it not to open a pull request: yes
    assumes no prior conversation : yes

  How to set it up, pause it and delete it:
    Create it with the `create_trigger` tool (a Claude Code **Routine**), with
    `create_new_session_on_fire` set so each firing starts from a clean slate, and the prompt above
    with `<CAMPAIGN-SLUG>` filled in. A weekly cadence suits a weekly game; "between sessions" means
    running it by hand with `/worldprep` instead.
    
    - **Pause it:** `update_trigger` with `enabled=false`. It stays stored and fires nothing.
    - **Delete it:** `delete_trigger` with its trigger id. `list_triggers` finds the id.
    - **Fire it once, now:** `fire_trigger`.
    
    **Pausing costs nothing.** Every off-screen turn's output lives in `gm-private/prep/` and in
    clock positions; with the Routine off, the clocks simply advance in play instead, and the prep
    files stop appearing. Nothing else in the framework depends on it.

=== [21] FLAGS.md in the templates has request / heat / status / seeding fields, and the
         boot sequence in 15-continuity-and-context-recovery.md reads it ===

--- the fields in templates/FLAGS.md ---
  16:| # | The request, in the player's words | Heat | Status | Where it has been seeded |
  20:- **Heat:** `burning` (aim at it now) / `warm` (soon) / `someday` (whenever it fits)
  21:- **Status:** `open` / `set up` / `paid off` / `retired`
  25:| # | The request | When it paid off | What happened |
  33:| # | The request | Retired when | Why |

--- and in the generated campaign, with its placeholder replaced ---
  # Flags — Test Run
  
  What the player has said they want this campaign to deliver, in their own words. Not a plot
  outline — a target the GM aims at on its own terms.
  
  The GM reads this file during the boot sequence and again when planning an arc or an
  off-screen turn. See `system/20-player-flags.md` for the GM's obligations, the most
  important of which is: **never deliver a flag literally or immediately.**
  
  This file starts empty. If the player names no flags, it stays empty and the GM aims at
  nothing. Nothing in `system/20-player-flags.md` is a default — its examples are illustrative
  only and are never treated as established elements of this campaign.

--- the boot sequence reading it, in 15-continuity-and-context-recovery.md ---
  25:- `FLAGS.md` — what the player has said they want to see.
  34:- `FLAGS.md` again, deliberately: read it once as state and once when planning.

--- and in CLAUDE.md's boot sequence ---
  32:2. `campaigns/<slug>/CHECKPOINT.md`, `state.json`, `RULES_DELTAS.md`, `PLAYER_PREFS.md`, `FLAGS.md`.
  33:3. `CANON.md`, `QUESTS.md`, `CLOCKS.md`, `npcs/ROSTER.md`, `FLAGS.md`.

=== [22] system/20-player-flags.md states that its example flags are illustrative only
         and are never to be treated as established campaign elements ===

  ## The examples below are illustrative only
  
  **Read this paragraph before the list.**
  
  The statements that follow are sample phrasings, included to show the *shape* of a flag during
  intake. Nothing more.
  
  - They are **not defaults**.
  - They are **not suggestions about the player's character**.
  - They are **not content to plan around**.
  
  The player's flags are whatever they actually say during intake and afterward. **If they give
  none, `FLAGS.md` stays empty and the GM aims at nothing.**
  
  **Never treat an example from this document as an established element of a campaign.** In
  particular: **no mentor, rival, faith, or legacy exists in any campaign unless it came from intake
  or from play.** If one of these phrasings appears in a campaign's `FLAGS.md`, it is because the
  player wrote it there.
  
  ### Sample phrasings

--- and templates/FLAGS.md repeats it, so a generated campaign carries the warning ---

  11:nothing. Nothing in `system/20-player-flags.md` is a default — its examples are illustrative
  12-only and are never treated as established elements of this campaign.


=== [29] system/22-session-flow.md states that the trailer contains only player-known
         information and that the scene budget never truncates a scene ===

  19:### Two hard rules
  20-
  21-1. **It contains only what the player's characters actually know.** Nothing from `gm-private/`.
  22-   Nothing from an off-screen turn they have not encountered. Nothing marked **GM-side truth** in
  23-   `CANON.md`. Nothing from a world chronicle entry dated after the campaign's current date.
  24-2. **The mechanical recap stays separate.** After the trailer, give the plain-facts version — HP,
  25-   conditions with durations, resources, location, in-world date, what they were about to do — so
  26-   the player gets the fiction and the state **without either contaminating the other.**
  27-

  77-
  78:- **Never truncate a scene to hit the budget.** It is a steering aid, not a timer. A fight that
  79-  runs long runs long. The budget only means you do not start a dungeon level with ten minutes
  80-  left.
  81-- **Stopping mid-combat is fine.** Checkpoint the encounter state per `05-checkpoint-protocol.md`
```

---

## Oracle

```
=== [19] oracle.py ask at each odds level, 2,000 rolls per level, yes-rates matching the
         published ladder within sampling error ===

The ladder as published in system/19-solo-oracle.md:
  Odds                   Yes on  Yes-rate
  Almost certain             2+      95%
  Very likely                4+      85%
  Likely                     6+      75%
  Even                      11+      50%
  Unlikely                  16+      25%
  Very unlikely             18+      15%
  Almost impossible         20+       5%
  
  Clear the threshold by 5+ → 'yes, and'. Land within 2 of it → 'yes, but' or 'no, but'.
  Miss it by 5+ → 'no, and'. A natural 1 or 20 triggers a random event.

$ python3 tools/oracle.py calibrate -n 2000
Oracle ladder calibration — 2000 rolls per rung, real dice through roll.py

odds                  yes on  expected  observed    diff  2 s.e.  verdict
----------------------------------------------------------------------------------
Almost certain            2+   95.00%   94.90%  -0.10%   0.97%  ok
Very likely               4+   85.00%   83.80%  -1.20%   1.60%  ok
Likely                    6+   75.00%   74.75%  -0.25%   1.94%  ok
Even                     11+   50.00%   51.30%  +1.30%   2.24%  ok
Unlikely                 16+   25.00%   24.90%  -0.10%   1.94%  ok
Very unlikely            18+   15.00%   15.15%  +0.15%   1.60%  ok
Almost impossible        20+    5.00%    5.65%  +0.65%   0.97%  ok

Expected yes-rate is (21 - threshold) / 20. 'ok' means the observed rate is within
two standard errors of it, which is the ~95% band for a fair d20.
-> exit 0   (nonzero if any rung falls outside two standard errors)

--- and the same thing through the CLI path the player actually uses (2,000 rolls per rung,
    logged to a scratch file rather than to the campaign's own audit trail) ---
  almost-certain       1909/2000 yes (95.5%); expected 95.0%
  very-likely          1715/2000 yes (85.8%); expected 85.0%
  likely               1486/2000 yes (74.3%); expected 75.0%
  even                 984/2000 yes (49.2%); expected 50.0%
  unlikely             509/2000 yes (25.4%); expected 25.0%
  very-unlikely        319/2000 yes (16.0%); expected 15.0%
  almost-impossible    106/2000 yes (5.3%); expected 5.0%

=== [20] oracle rolls land in rolls.jsonl tagged 'oracle', and 19-solo-oracle.md states
         plainly that a result is binding on the GM ===

🔮 Is the side gate guarded?
   Unlikely — yes on 16+ · rolled [2]
   → **NO, AND** — no, and it is worse than that
   This answer is binding. Build forward from it (system/19-solo-oracle.md).

--- the last oracle record in the log ---
  The campaign's log carries the 'oracle' tag on every oracle roll; the last one:
{
    "seq": 14008,
    "kind": "oracle",
    "label": "Oracle (Unlikely, yes on 16+): Is the side gate guarded?",
    "expr": "1d20",
    "natural": 2,
    "total": 2,
    "tags": [
      "oracle"
    ],
    "shown": true,
    "extra": {
      "oracle": {
        "answer": "no, and",
        "gloss": "no, and it is worse than that",
        "yes": false,
        "margin": -14,
        "flags": [],
        "odds": "unlikely",
        "threshold": 16
      },
      "question": "Is the side gate guarded?"
    }
  }

--- what the document says about binding, verbatim ---
  18:## The rule that makes it work
  19-
  20-**An oracle result is binding on the GM.**
  21-
  22-When the player consults it, the GM takes the answer as established fact and builds forward from
  23-it — **including when it wrecks what the GM had planned.** The GM does not reroll it, does not
  24-reinterpret it toward its prep, and does not quietly route around it.
  25-
  26-There is exactly one legitimate override: **if the answer contradicts something already in
  27-`CANON.md`, say so and re-ask a better question.** Not "that does not fit what I had in mind" —
  28-that is the case the rule exists to prevent.
  29-
  30-Oracle rolls go through the same dice engine and the same audit log as everything else, tagged
```

---

## Shared world

> **Superseded, and worth reading as a failure.** The transcript below shows `world.py as-of`
> printing the **date, title and campaign** of every entry it withheld, under a "do not read"
> header. Reading the title *is* the spoiler, so the gate defeated itself: a GM loading the
> gated view for a prequel learned what happens later just by loading it. Commit `26d52eb`
> fixed it — the player-facing path now prints a count only, and the list stays behind `--gm`,
> matching the secret-visibility path directly below it in the same function.
>
> The evidence is left as captured rather than regenerated, because that is what the run
> produced. This was a sixth defect, found after the acceptance run rather than by it — the
> checks confirmed the gate *filtered* correctly and never asked whether the filtering itself
> leaked.


```
=== [23] world.py init + link produces a world, attaches test-run to it, and promote
         moves a concluded event into CHRONICLE.md with a date, a campaign tag and a
         visibility field ===

world.py: /home/user/PF2e_Claude/worlds/verdant-reach already exists (pass --force to fill in missing files only)
```

```
=== [24] as-of with a date before an event's date omits that event — filtered and
         unfiltered views side by side ===

The chronicle holds four entries, in date order:
  ## The Reach loses its northern watchtowers
  - **Date:** 3 Pharast 4710 AR
  - **Campaign:** test-run
  - **Visibility:** public
  ## The Ashen Covenant broken at the flooded crypt
  - **Date:** 12 Desnus 4712 AR
  - **Campaign:** test-run
  - **Visibility:** public
  ## A different account of the crypt
  - **Date:** 12 Desnus 4712 AR
  - **Campaign:** other-campaign
  - **Visibility:** rumor
  ## The thing under the aqueduct stirs
  - **Date:** 1 Neth 4715 AR
  - **Campaign:** test-run
  - **Visibility:** secret

#### UNFILTERED — as-of a date after everything, with --gm, which is the whole file ####
# verdant-reach — world view as of 1 Kuthona 4730 AR

> **GM view.** Includes `secret` entries. Never paste this into play.

Chronicle: 4 entry/entries at or before this date; 0 dated later are withheld by the date gate.

  visible: ## The Reach loses its northern watchtowers
  visible: ## The Ashen Covenant broken at the flooded crypt
  visible: ## A different account of the crypt
  visible: ## The thing under the aqueduct stirs
  visible: ## Legends current at this date
  visible: ## Undated setting material (read in full)

#### FILTERED — as-of '1 Abadius 4711 AR', before the crypt ####
# verdant-reach — world view as of 1 Abadius 4711 AR

Chronicle: 1 entry/entries at or before this date; 3 dated later are withheld by the date gate.

  visible: ## The Reach loses its northern watchtowers
  visible: ## Legends current at this date
  visible: ## Undated setting material (read in full)
  **Withheld by the date gate** (do not read, do not let them inform this campaign):
  - 12 Desnus 4712 AR — The Ashen Covenant broken at the flooded crypt (test-run)
  - 12 Desnus 4712 AR — A different account of the crypt (other-campaign)
  - 1 Neth 4715 AR — The thing under the aqueduct stirs (test-run)
  

#### FILTERED — as-of '1 Kuthona 4713 AR', after the crypt, before the aqueduct ####
# verdant-reach — world view as of 1 Kuthona 4713 AR

Chronicle: 3 entry/entries at or before this date; 1 dated later are withheld by the date gate.

  visible: ## The Reach loses its northern watchtowers
  visible: ## The Ashen Covenant broken at the flooded crypt
  visible: ## A different account of the crypt
  visible: ## Legends current at this date
  visible: ## Undated setting material (read in full)
  **Withheld by the date gate** (do not read, do not let them inform this campaign):
  - 1 Neth 4715 AR — The thing under the aqueduct stirs (test-run)
  

#### FILTERED — as-of '1 Kuthona 4720 AR', after everything, PLAYER view ####
# verdant-reach — world view as of 1 Kuthona 4720 AR

Chronicle: 3 entry/entries at or before this date; 0 dated later are withheld by the date gate; 1 secret entry/entries withheld.

  visible: ## The Reach loses its northern watchtowers
  visible: ## The Ashen Covenant broken at the flooded crypt
  visible: ## A different account of the crypt
  visible: ## Legends current at this date
  visible: ## Undated setting material (read in full)
  **Withheld as secret:** 1 entry/entries. They are in the world's gm-private view.
  (the aqueduct entry is dated 4715 and so passes the date gate, but it is 'secret')

--- the 4711 view against the 4713 view, as a diff of what the GM may read ---
  1c1
  < # verdant-reach — world view as of 1 Abadius 4711 AR
  ---
  > # verdant-reach — world view as of 1 Kuthona 4713 AR
  3c3
  < Chronicle: 1 entry/entries at or before this date; 3 dated later are withheld by the date gate.
  ---
  > Chronicle: 3 entry/entries at or before this date; 1 dated later are withheld by the date gate.
  13a14,31
  > ## The Ashen Covenant broken at the flooded crypt
  > 
  > - **Date:** 12 Desnus 4712 AR
  > - **Campaign:** test-run
  > - **Characters:** Kaelen
  > - **Visibility:** public
  > - **What happened:** Kaelen reached the crypt lever before the water did and drowned the Covenant's ritual chamber with its officiants inside. The second seal was never lit.
  > - **What it changed:** The Covenant is leaderless in the Reach and its remaining cells cannot coordinate.
  > 
  > ## A different account of the crypt
  > 
  > - **Date:** 12 Desnus 4712 AR
  > - **Campaign:** other-campaign
  > - **Characters:** —
  > - **Visibility:** rumor
  > - **What happened:** Another party claims they were the ones in the crypt.
  > - **What it changed:** Two versions of the same day are now on record.
  > 
  17,18d34
  < - 12 Desnus 4712 AR — The Ashen Covenant broken at the flooded crypt (test-run)
  < - 12 Desnus 4712 AR — A different account of the crypt (other-campaign)
  25,26c41
  < 
  < _1 later legend(s) withheld._
  ---
  > - **How it is told: The Ashen Covenant broken at the flooded crypt** (12 Desnus 4712 AR) — They say one knight held the stair against a hundred and pulled the river down on them, and walked out dry.

=== [25] no live-state field appears anywhere under worlds/, and validate.py fails if
         one is introduced ===

$ python3 tools/validate.py --world verdant-reach -v
world verdant-reach: 0 error(s), 0 warning(s)
  ok    CHRONICLE.md parses (4 entry/entries)
  ok    no live-state fields found under worlds/

PASS — 0 errors, 0 warning(s)
-> exit 0

--- write a legacy record, then append live state to it on purpose ---
  wrote worlds/verdant-reach/characters/kaelen.md
  Fill in the deeds, the reputation, and the gap between them. Set availability deliberately —
  the GM honours it in every other campaign in this world.

$ python3 tools/validate.py --world verdant-reach
world verdant-reach: 5 error(s), 0 warning(s)
  ERROR worlds/verdant-reach/characters/kaelen.md:50 looks like live state in the world layer ('current hp') — hit points, coins, inventory, conditions and positions never leave campaigns/
  ERROR worlds/verdant-reach/characters/kaelen.md:50 looks like live state in the world layer ('hp:') — hit points, coins, inventory, conditions and positions never leave campaigns/
  ERROR worlds/verdant-reach/characters/kaelen.md:52 looks like live state in the world layer ('conditions:') — hit points, coins, inventory, conditions and positions never leave campaigns/
  ERROR worlds/verdant-reach/characters/kaelen.md:51 looks like live state in the world layer ('gold:') — hit points, coins, inventory, conditions and positions never leave campaigns/
  ERROR worlds/verdant-reach/characters/kaelen.md:53 looks like live state in the world layer ('position:') — hit points, coins, inventory, conditions and positions never leave campaigns/

FAIL — 5 error(s), 0 warning(s)
-> exit 1

--- strip it back out; the world validates again ---
world verdant-reach: 0 error(s), 0 warning(s)

PASS — 0 errors, 0 warning(s)
-> exit 0
```

```
=== [26] a campaign created with World: none builds and runs with no reference to worlds/ ===


Next: run the intake interview — system/01-campaign-intake.md. Nothing in this folder is
decided yet; the defaults exist so the scaffold is valid, not so it is finished.

--- its World: field, straight out of the scaffold ---
  5:- **World:** none

--- every reference to a worlds/<slug> path anywhere in the campaign folder ---
  (none — the only mentions of the layer are generic prose about 'worlds/')

--- the generic mentions, for honesty about what IS in there ---
  campaigns/standalone-test/CAMPAIGN.md:16:> `World:` names a folder under `worlds/`, or `none` for a standalone campaign. A campaign
  campaigns/standalone-test/WORLD.md:3:The gazetteer for *this campaign*. If `CAMPAIGN.md` names a world under `worlds/`, the

--- it runs: add a character, take a turn's worth of state changes, checkpoint, validate ---
added Nobody (pc, level 1, 18 HP) as `nobody`
🎲 Nobody — Perception: 1d20+6 → [4] +6 = 10 vs DC 17 → FAILURE
Nobody HP 13/18
1 hour passes: 1 Abadius 4725 AR, 08:00 → 1 Abadius 4725 AR, 09:00
checkpoint 001: standalone works
wrote campaigns/standalone-test/checkpoints/001-standalone-works.md
dashboard regenerated
committed 7504324 — checkpoint 001: standalone works

campaign standalone-test: 0 error(s), 0 warning(s)
  ok    state.json parses
  ok    CHECKPOINT.md matches state.json
  ok    World: none — nothing references the shared-world layer

PASS — 0 errors, 0 warning(s)
-> exit 0

--- and the boot sequence's as-of step is simply skipped, because there is no world:
    world.py refuses to promote from it at all ---
  world.py: standalone-test/CAMPAIGN.md has no `World:` field pointing at a worlds/ folder. A standalone campaign has nothing to promote to.
  -> exit 2
```

---

## Mid-combat restore

```
=== [27] a checkpoint taken in the middle of round 3 of a combat restores the full
         encounter tracker — initiative order, current turn, actions spent, multiple
         attack penalty, reactions used, every combatant's HP and conditions, and map
         positions. Before and after. ===

--- set up the fight and play it to the middle of round 3 ---
encounter 'Flooded crypt landing' started — objective: Reach the lever before the water rises (6 rounds)
🎲 Kaelen — Initiative: 1d20+7 → [15] +7 = 22
🎲 Ghoul A — Initiative: 1d20+5 → [18] +5 = 23
🎲 Ghoul B — Initiative: 1d20+5 → [8] +5 = 13
🎲 Ghast — Initiative: 1d20+8 → [17] +8 = 25

Initiative order:
   1. [-] Ghast                 25  (natural 17)
   2. [-] Ghoul A               23  (natural 18)
   3. [P] Kaelen                22  (natural 15)
   4. [-] Ghoul B               13  (natural 8)
  Cross-side ties: the adversary acts first (Player Core, Roll Initiative).

(The --init values below are fixed rather than taken from the roll above, so that the
before/after comparison has stable numbers to compare. In play you would pass the rolled
totals.)

Kaelen joins the encounter on the party side at initiative 18
Ghoul A joins the encounter on the adversary side at initiative 19
Ghoul B joins the encounter on the adversary side at initiative 18
Ghast joins the encounter on the adversary side at initiative 21
objective telegraphed to the player

--- advance to round 3 ---
Flooded crypt landing — round 3, objective: Reach the lever before the water rises (6 rounds)
map: maps/crypt-landing.md


--- play some of round 3: spend actions, raise the MAP, use a reaction, take damage,
    move, add conditions, wound the enemies ---
Ghast: ◆◇◇ (1 left)
Ghast: MAP step 1 → -5 (agile -4)
Kaelen: reaction spent on Reactive Strike
Ghoul A HP 11/28
Ghast HP 31/45
Kaelen HP 11/22
Kaelen: frightened 2 added (2 rounds)
Kaelen: off-guard added (ends at the end of the turn)
Kaelen is at D5
Ghast is at E5
encounter.combatants.0.persistent = [{"type": "bleed", "expr": "1d6", "dc": 15}]

############################ BEFORE — the tracker mid-round-3 ############################
Flooded crypt landing — round 3, objective: Reach the lever before the water rises (6 rounds)
map: maps/crypt-landing.md

   combatant              init           HP act   MAP rxn  pos   conditions
   Ghast                    21        31/45 ◆◇◇     1 yes  E5    
   Ghoul A                  19        11/28 ◆◆◆     0 yes  E5    
   Ghoul B                  18        28/28 ◆◆◆     0 yes  E6    
→  Kaelen                   18        11/22 ◆◆◆     0 used D5    frightened 2, off-guard

the state.json encounter block, in full:
  {
    "name": "Flooded crypt landing",
    "objective": "Reach the lever before the water rises (6 rounds)",
    "map": "crypt-landing",
    "round": 3,
    "turn_index": 3,
    "started_at": "2026-09-30T03:32:30Z",
    "combatants": [
      {
        "id": "ghast",
        "name": "Ghast",
        "side": "adversary",
        "ref": null,
        "initiative": 21,
        "initiative_natural": null,
        "hp": {
          "current": 31,
          "max": 45,
          "temp": 0
        },
        "conditions": [],
        "dying": 0,
        "actions_remaining": 1,
        "actions_spent": 2,
        "map_step": 1,
        "reaction_available": true,
        "reaction_used_for": null,
        "position": "E5",
        "squad": null,
        "persistent": [
          {
            "type": "bleed",
            "expr": "1d6",
            "dc": 15
          }
        ],
        "sustained": [],
        "level": 2,
        "notes": "",
        "defeated": false
      },
      {
        "id": "ghoul-a",
        "name": "Ghoul A",
        "side": "adversary",
        "ref": null,
        "initiative": 19,
        "initiative_natural": null,
        "hp": {
          "current": 11,
          "max": 28,
          "temp": 0
        },
        "conditions": [],
        "dying": 0,
        "actions_remaining": 3,
        "actions_spent": 0,
        "map_step": 0,
        "reaction_available": true,
        "reaction_used_for": null,
        "position": "E5",
        "squad": null,
        "persistent": [],
        "sustained": [],
        "level": 1,
        "notes": "",
        "defeated": false
      },
      {
        "id": "ghoul-b",
        "name": "Ghoul B",
        "side": "adversary",
        "ref": null,
        "initiative": 18,
        "initiative_natural": null,
        "hp": {
          "current": 28,
          "max": 28,
          "temp": 0
        },
        "conditions": [],
        "dying": 0,
        "actions_remaining": 3,
        "actions_spent": 0,
        "map_step": 0,
        "reaction_available": true,
        "reaction_used_for": null,
        "position": "E6",
        "squad": "ghouls",
        "persistent": [],
        "sustained": [],
        "level": 1,
        "notes": "",
        "defeated": false
      },
      {
        "id": "kaelen",
        "name": "Kaelen",
        "side": "party",
        "ref": "kaelen",
        "initiative": 18,
        "initiative_natural": null,
        "hp": null,
        "conditions": null,
        "dying": null,
        "actions_remaining": 3,
        "actions_spent": 0,
        "map_step": 0,
        "reaction_available": false,
        "reaction_used_for": "Reactive Strike",
        "position": "D5",
        "squad": null,
        "persistent": [],
        "sustained": [],
        "level": null,
        "notes": "",
        "defeated": false
      }
    ],
    "log": [],
    "telegraphed": true,
    "telegraph_text": "the water is already at your ankles and rising a foot a round"
  }

--- checkpoint, in the middle of round 3 ---
checkpoint 010: mid-combat: round 3 of the flooded crypt landing
wrote campaigns/test-run/checkpoints/010-mid-combat-round-3-of-the-flooded-crypt-landing.md
dashboard regenerated
committed fc2faa3 — checkpoint 010: mid-combat: round 3 of the flooded crypt landing

--- now wreck it: end the fight, heal up, clear conditions, walk away ---
  encounter is now: None
  Kaelen HP:        {"current":22,"max":22,"temp":0}
  conditions:       []
  location:         Somewhere else entirely

--- restore the mid-combat checkpoint ---
restored campaigns/test-run/checkpoints/010-mid-combat-round-3-of-the-flooded-crypt-landing.md
state.json and CHECKPOINT.md now match checkpoint 010
dashboard regenerated
committed the rewind (0aedc30)
Narrate from the snapshot's situation paragraph. Rewinding is a legitimate table move.

############################ AFTER — restored from the snapshot ############################
Flooded crypt landing — round 3, objective: Reach the lever before the water rises (6 rounds)
map: maps/crypt-landing.md

   combatant              init           HP act   MAP rxn  pos   conditions
   Ghast                    21        31/45 ◆◇◇     1 yes  E5    
   Ghoul A                  19        11/28 ◆◆◆     0 yes  E5    
   Ghoul B                  18        28/28 ◆◆◆     0 yes  E6    
→  Kaelen                   18        11/22 ◆◆◆     0 used D5    frightened 2, off-guard

the restored encounter block:
  {
    "name": "Flooded crypt landing",
    "objective": "Reach the lever before the water rises (6 rounds)",
    "map": "crypt-landing",
    "round": 3,
    "turn_index": 3,
    "started_at": "2026-09-30T03:32:30Z",
    "combatants": [
      {
        "id": "ghast",
        "name": "Ghast",
        "side": "adversary",
        "ref": null,
        "initiative": 21,
        "initiative_natural": null,
        "hp": {
          "current": 31,
          "max": 45,
          "temp": 0
        },
        "conditions": [],
        "dying": 0,
        "actions_remaining": 1,
        "actions_spent": 2,
        "map_step": 1,
        "reaction_available": true,
        "reaction_used_for": null,
        "position": "E5",
        "squad": null,
        "persistent": [
          {
            "type": "bleed",
            "expr": "1d6",
            "dc": 15
          }
        ],
        "sustained": [],
        "level": 2,
        "notes": "",
        "defeated": false
      },
      {
        "id": "ghoul-a",
        "name": "Ghoul A",
        "side": "adversary",
        "ref": null,
        "initiative": 19,
        "initiative_natural": null,
        "hp": {
          "current": 11,
          "max": 28,
          "temp": 0
        },
        "conditions": [],
        "dying": 0,
        "actions_remaining": 3,
        "actions_spent": 0,
        "map_step": 0,
        "reaction_available": true,
        "reaction_used_for": null,
        "position": "E5",
        "squad": null,
        "persistent": [],
        "sustained": [],
        "level": 1,
        "notes": "",
        "defeated": false
      },
      {
        "id": "ghoul-b",
        "name": "Ghoul B",
        "side": "adversary",
        "ref": null,
        "initiative": 18,
        "initiative_natural": null,
        "hp": {
          "current": 28,
          "max": 28,
          "temp": 0
        },
        "conditions": [],
        "dying": 0,
        "actions_remaining": 3,
        "actions_spent": 0,
        "map_step": 0,
        "reaction_available": true,
        "reaction_used_for": null,
        "position": "E6",
        "squad": "ghouls",
        "persistent": [],
        "sustained": [],
        "level": 1,
        "notes": "",
        "defeated": false
      },
      {
        "id": "kaelen",
        "name": "Kaelen",
        "side": "party",
        "ref": "kaelen",
        "initiative": 18,
        "initiative_natural": null,
        "hp": null,
        "conditions": null,
        "dying": null,
        "actions_remaining": 3,
        "actions_spent": 0,
        "map_step": 0,
        "reaction_available": false,
        "reaction_used_for": "Reactive Strike",
        "position": "D5",
        "squad": null,
        "persistent": [],
        "sustained": [],
        "level": null,
        "notes": "",
        "defeated": false
      }
    ],
    "log": [],
    "telegraphed": true,
    "telegraph_text": "the water is already at your ankles and rising a foot a round"
  }
=== the same restore, checked field by field instead of by eye ===

After nine further mutations mid-fight, the tracker reads:
  round 4, turn_index 1
  Ghast      hp 31/45   act 3 map 0 rxn yes pos E5
  Ghoul A    hp 11/28   act 3 map 0 rxn yes pos E5
  Ghoul B    hp 3/28   act 3 map 0 rxn yes pos E6
  Kaelen     hp 3/22   act 1 map 2 rxn yes pos A1

Restored, compared combatant by combatant and field by field:

  combatant      initiative  actions_remai  actions_spent       map_step  reaction_avai  reaction_used
  Ghast                  21              1              2              1           True           None
  Ghoul A                19              3              0              0           True           None
  Ghoul B                18              3              0              0           True           None
  Kaelen                 18              3              0              0          False  Reactive Stri

  encounter.round        = 3                                                              same
  encounter.turn_index   = 3                                                              same
  encounter.name         = Flooded crypt landing                                          same
  encounter.objective    = Reach the lever before the water rises (6 rounds)              same
  encounter.map          = crypt-landing                                                  same
  encounter.telegraphed  = True                                                           same

  every combatant's initiative           restored identically: yes
  every combatant's actions_remaining    restored identically: yes
  every combatant's actions_spent        restored identically: yes
  every combatant's map_step             restored identically: yes
  every combatant's reaction_available   restored identically: yes
  every combatant's reaction_used_for    restored identically: yes
  every combatant's position             restored identically: yes
  every combatant's squad                restored identically: yes
  every combatant's hp                   restored identically: yes
  every combatant's conditions           restored identically: yes
  every combatant's dying                restored identically: yes
  every combatant's persistent           restored identically: yes
  every combatant's level                restored identically: yes
  every combatant's defeated             restored identically: yes

  the pcs block (party HP and conditions, which the tracker points at rather than
  copying) restored identically: yes

RESULT: PASS — the whole tracker came back exactly.
```

---

## Relationship graph

```
=== [28] graph.py produces a Mermaid diagram in WORLD.md from the NPC relationship
         fields, and the player-safe version omits every tie marked GM-only ===

--- three NPC files with structured relationship fields; two ties marked [gm-only],
    one marked [unknown] because the player has not learned it yet ---
  guildmaster-poll.md:39:- rival-of: Mira Vance — the contract
  guildmaster-poll.md:40:- serves: House Vhaldrin — nominally
  guildmaster-poll.md:41:- related-to: Harrow Kell — half-brother, and neither mentions it [gm-only]
  harrow-kell.md:39:- ally-of: Mira Vance — shared a cell in Korvosa
  harrow-kell.md:40:- owes: Kaelen — a life, and he knows it
  harrow-kell.md:41:- fears: the thing in the aqueduct — saw it, will not say what [unknown]
  harrow-kell.md:42:- serves: The Ashen Covenant — has done since before the siege [gm-only]
  mira-vance.md:39:- ally-of: Harrow Kell — the cell in Korvosa, and since
  mira-vance.md:40:- rival-of: Guildmaster Poll — competing for the same contract
  mira-vance.md:41:- owed-by: Kaelen — two weeks' board

$ python3 tools/graph.py --campaign test-run
7 player-safe tie(s) → campaigns/test-run/WORLD.md
10 total tie(s) → campaigns/test-run/gm-private/relationships.md
3 tie(s) marked gm-only or unknown are in the GM graph only.

--- the player-safe graph, spliced into WORLD.md ---
  <!-- RELATIONSHIP-GRAPH:BEGIN (generated by tools/graph.py — do not hand-edit) -->
  
  ## Relationships
  
  ```mermaid
  graph LR
      Guildmaster_Poll["Guildmaster Poll"]
      Harrow_Kell["Harrow Kell"]
      Mira_Vance["Mira Vance"]
      Kaelen["Kaelen"]
      House_Vhaldrin["House Vhaldrin"]
      Guildmaster_Poll -.->|"rival of: the contract"| Mira_Vance
      Guildmaster_Poll ==>|"serves: nominally"| House_Vhaldrin
      Harrow_Kell -->|"ally of: shared a cell in Korvosa"| Mira_Vance
      Harrow_Kell -->|"owes: a life, and he knows it"| Kaelen
      Mira_Vance -->|"ally of: the cell in Korvosa, and since"| Harrow_Kell
      Mira_Vance -.->|"rival of: competing for the same contract"| Guildmaster_Poll
      Mira_Vance -->|"owed by: two weeks' board"| Kaelen
  ```
  
  What the player has learned in play. Regenerate with `python3 tools/graph.py --campaign test-run` whenever the roster changes.
  
  <!-- RELATIONSHIP-GRAPH:END -->

--- the GM graph, written only to gm-private/relationships.md ---
  <!-- RELATIONSHIP-GRAPH:BEGIN (generated by tools/graph.py — do not hand-edit) -->
  
  ## Relationships (full)
  
  > **GM-ONLY** — includes hidden allegiances and ties the player has not learned.
  
  ```mermaid
  graph LR
      Guildmaster_Poll["Guildmaster Poll"]
      Harrow_Kell["Harrow Kell"]
      Mira_Vance["Mira Vance"]
      Kaelen["Kaelen"]
      House_Vhaldrin["House Vhaldrin"]
      the_thing_in_the_aqueduct["the thing in the aqueduct"]
      The_Ashen_Covenant["The Ashen Covenant"]
      Guildmaster_Poll -.->|"rival of: the contract"| Mira_Vance
      Guildmaster_Poll ==>|"serves: nominally"| House_Vhaldrin
      Guildmaster_Poll ---|"kin: half-brother, and neither mentions it"| Harrow_Kell
      Harrow_Kell -->|"ally of: shared a cell in Korvosa"| Mira_Vance
      Harrow_Kell -->|"owes: a life, and he knows it"| Kaelen
      Harrow_Kell -.->|"fears: saw it, will not say what"| the_thing_in_the_aqueduct
      Harrow_Kell ==>|"serves: has done since before the siege"| The_Ashen_Covenant
      Mira_Vance -->|"ally of: the cell in Korvosa, and since"| Harrow_Kell
      Mira_Vance -.->|"rival of: competing for the same contract"| Guildmaster_Poll
      Mira_Vance -->|"owed by: two weeks' board"| Kaelen
  ```
  
  3 tie(s) here are absent from the player-safe graph in WORLD.md.
  
  <!-- RELATIONSHIP-GRAPH:END -->

--- the check that matters: which ties appear in which file ---
  tie (by its reason text)                       marked    WORLD.md     gm-private
  serves: has done since before the siege        gm-only   absent       present
  kin: half-brother, and neither mentions it     gm-only   absent       present
  fears: saw it, will not say what               unknown   absent       present

  ally of: shared a cell in Korvosa              —         present      present
  rival of: competing for the same contract      —         present      present
  owes: a life, and he knows it                  —         present      present
  serves: nominally                              —         present      present
  owed by: two weeks' board                      —         present      present

  mermaid fence in WORLD.md            : yes
  mermaid fence in gm-private          : yes
  GM-ONLY fence in gm-private          : yes
  gm-private nodes absent from WORLD.md: yes

--- and the plain adjacency list the dashboard uses, since it fetches nothing ---
  3 tie(s) marked gm-only or unknown are in the GM graph only.
  
  - **Guildmaster Poll** — rival of Mira Vance (the contract); serves House Vhaldrin (nominally)
  - **Harrow Kell** — ally of Mira Vance (shared a cell in Korvosa); owes Kaelen (a life, and he knows it)
  - **Mira Vance** — ally of Harrow Kell (the cell in Korvosa, and since); rival of Guildmaster Poll (competing for the same contract); owed by Kaelen (two weeks' board)
```

---

## Structure and provenance

```
=== [30] no campaign-specific content exists outside campaigns/ ===

--- the repository-wide check ---
$ python3 tools/validate.py --repo -v
repository: 0 error(s), 1 warning(s)
  ok    no campaign-specific content found outside campaigns/
  warn  DESIGN_NOTES.md is missing from the repository root

PASS — 0 errors, 1 warning(s)
-> exit 0

--- and by hand: every mention of a live campaign slug outside campaigns/ ---
  campaign 'other-campaign':
    (none)
  campaign 'standalone-test':
    (none)
  campaign 'test-run':
    (none)

  (test-run is excluded above because it is the throwaway test campaign, which is
   deleted at the end of this run. Mentions of it in the acceptance evidence are not
   in the framework.)

--- what DOES live outside campaigns/, for completeness ---
  top-level entries:
    .claude
    .gitignore
    CLAUDE.md
    EXTRAS.md
    LICENSE_NOTES.md
    PROMPT.md
    README.md
    campaigns
    system
    templates
    tools
    worlds

  and nothing under system/, tools/, templates/ or .claude/ holds live state:
    references it: system/18-between-session-prep.md
    references it: system/02-character-creation.md
    references it: system/15-continuity-and-context-recovery.md
    references it: system/05-checkpoint-protocol.md
    references it: system/17-encounter-objectives.md
    references it: system/07-encounter-building.md
    references it: system/14-player-commands.md
    references it: system/04-dice-protocol.md
    (references to the path, not copies of state — no campaigns/<slug>/state.json
     exists outside campaigns/)

=== [31] every rules table is either cited or marked UNVERIFIED, and the unverified ones
         are listed in DESIGN_NOTES.md ===

$ python3 tools/pf2e.py sources   (tail)

5 of 17 tables are unverified: creature_adjustments, settlement_item_levels, travel_speed, treasure_by_level, treasure_mix

These are listed in DESIGN_NOTES.md under 'To verify before first play'.

--- every Source: line in system/, one per table ---
  system/07-encounter-building.md:31  ->   GM Core, Encounter Budget (https://2e.aonprd.com/Rules.aspx?ID=575): 40/60/80/120/160 XP for a four-character
  system/07-encounter-building.md:51  ->   GM Core, Creature XP by level relative to the party (https://2e.aonprd.com/Rules.aspx?ID=575), and the Profic
  system/07-encounter-building.md:95  ->   GM Core, Hazard XP: a simple hazard is worth a fifth of a creature of the same relative level; a complex haza
  system/07-encounter-building.md:104:**⚠ UNVERIFIED —** GM Core, Elite and Weak adjustments (https://2e.aonprd.com/Rules.aspx?ID=1027 area). UNVERI
  system/08-npc-and-bestiary-protocol.md:12  ->   Monster Core p.NNN
  system/08-npc-and-bestiary-protocol.md:20  ->   https://2e.aonprd.com/Monsters.aspx?ID=NNN
  system/08-npc-and-bestiary-protocol.md:40  ->   Homebrew — reskin of Ghoul (Monster Core, lvl 1)
  system/08-npc-and-bestiary-protocol.md:47  ->   Homebrew — built from the GM Core creature-building benchmarks (level 3:
  system/09-loot-and-economy.md:113  ->   Player Core, Bulk. Verified against the Foundry VTT PF2e implementation.
  system/09-loot-and-economy.md:179  ->   Player Core, Earn Income. Verified against the Foundry VTT PF2e implementation.
  system/10-downtime-travel-and-rest.md:173  ->   the healing dice and the bonus-by-rank figures are verified against the Foundry VTT
  system/12-rules-quick-reference.md:32  ->   Player Core / GM Core, Degrees of Success (https://2e.aonprd.com/Rules.aspx?ID=552). Verified against foun
  system/12-rules-quick-reference.md:66  ->   Player Core, Multiple Attack Penalty: -5/-10, or -4/-8 agile. Verified against foundryvtt/pf2e v8.5.1 @06b
  system/12-rules-quick-reference.md:84  ->   GM Core, DCs by Level (https://2e.aonprd.com/Rules.aspx?ID=552). Verified against foundryvtt/pf2e v8.5.1 @
  system/12-rules-quick-reference.md:103  ->   GM Core, Simple DCs (https://2e.aonprd.com/Rules.aspx?ID=552); the Proficiency Without Level column from 
  system/12-rules-quick-reference.md:128  ->   GM Core, Adjusting Difficulty and the rarity adjustments (https://2e.aonprd.com/Rules.aspx?ID=555). Verif
  system/12-rules-quick-reference.md:172  ->   GM Core variant rule Automatic Bonus Progression, which states the item-bonus curve the core math assumes
  system/12-rules-quick-reference.md:200  ->   Player Core, the Dying, Wounded and Doomed conditions and the recovery check. Verified against the Foundr
  system/12-rules-quick-reference.md:542  ->   Player Core, the Dying, Wounded and Doomed conditions and the recovery check. Verified against the Foundr
  system/12-rules-quick-reference.md:569  ->   Player Core, Bulk. Verified against the Foundry VTT PF2e implementation
  system/12-rules-quick-reference.md:578  ->   Player Core, Coins.

--- every UNVERIFIED marker in system/ ---
  system/00-gm-charter.md:59:`Source:` line. Where a value could not be verified it says `⚠ UNVERIFIED` rather than
  system/07-encounter-building.md:104:**⚠ UNVERIFIED —** GM Core, Elite and Weak adjustments (https://2e.aonprd.com/Rules.aspx?I
  system/08-npc-and-bestiary-protocol.md:62:⚠ The HP column of the Elite/Weak table is marked `⚠ UNVERIFIED` in `tools/pf2e.py`.
  system/09-loot-and-economy.md:14:⚠ **The treasure-by-level table in `tools/pf2e.py` is marked `⚠ UNVERIFIED`.** The Foundry VT
  system/09-loot-and-economy.md:58:⚠ `⚠ UNVERIFIED`. `tools/pf2e.py` carries usable defaults —
  system/09-loot-and-economy.md:147:⚠ The rune price table and the transfer cost are `⚠ UNVERIFIED` against a reachable source.
  system/09-loot-and-economy.md:162:⚠ The half-price sale rate is the long-standing convention and is `⚠ UNVERIFIED` here agains
  system/09-loot-and-economy.md:187:⚠ The 4-day setup and the half-price materials figure are `⚠ UNVERIFIED` against a reachable
  system/10-downtime-travel-and-rest.md:27:⚠ The activity list and their speed effects are `⚠ UNVERIFIED` against a source reach
  system/10-downtime-travel-and-rest.md:45:⚠ **PARTLY UNVERIFIED —** GM Core, Travel Speed. The 8-hour travel day is verified ag
  system/10-downtime-travel-and-rest.md:56:⚠ `⚠ UNVERIFIED`.
  system/10-downtime-travel-and-rest.md:137:⚠ The hit-points-per-night formula is `⚠ UNVERIFIED` against a reachable source. The
  system/10-downtime-travel-and-rest.md:178:⚠ The once-per-hour-per-patient limit and the 10-minute duration are `⚠ UNVERIFIED` 
  system/11-leveling-up.md:42:feats and ancestry feats are `⚠ UNVERIFIED` against a source reachable from the machine that
  system/12-rules-quick-reference.md:5:machine that built this framework is marked `⚠ UNVERIFIED`.
  system/12-rules-quick-reference.md:235:⚠ The cover bonuses are `⚠ UNVERIFIED` against a reachable source; the off-guard penalt
  system/12-rules-quick-reference.md:273:⚠ `⚠ UNVERIFIED` against a reachable source. The order matters mostly at the margins, b
  system/12-rules-quick-reference.md:319:⚠ The Grapple/Shove/Trip/Disarm target DCs and the Aid DC are `⚠ UNVERIFIED` against a
```

```
=== [31, continued] the unverified tables are listed in DESIGN_NOTES.md ===

--- the tool's list ---
5 of 17 tables are unverified: creature_adjustments, settlement_item_levels, travel_speed, treasure_by_level, treasure_mix

--- and each of those five in DESIGN_NOTES.md ---
  treasure_by_level        listed
  treasure_mix             listed
  settlement_item_levels   listed
  travel_speed             listed
  creature_adjustments     listed

--- the 'To verify before first play' heading and its inline section ---
  60:## To verify before first play
  table rows in DESIGN_NOTES.md: 47

--- the 'Decisions made without the user' heading ---
  102:## Decisions made without the user
  108:### 1. Verification source: the Foundry VTT PF2e system, not "unverified everything"
  119:### 2. A roll with no `--campaign` is not logged, and says so
  129:### 3. Party combatants reference their `pcs` entry rather than copying HP
  138:### 4. Gaining coins keeps the denominations received; spending breaks them only when it must
  146:### 5. Files beginning with `_` are not copied into a new campaign
  156:### 6. A restore never rewinds the checkpoint counter
  165:### 7. `promote` inserts into the chronicle in date order
  173:### 8. World slugs drop a leading article
  179:### 9. Four documents are generated from the tools, not written beside them
  190:### 10. Conventions this framework invented, and labelled as its own
  205:### 11. Other smaller calls

=== the final repository-wide validation, with DESIGN_NOTES.md now present ===

campaign other-campaign: 0 error(s), 1 warning(s)
  warn  state.json holds no characters yet
campaign standalone-test: 0 error(s), 0 warning(s)
campaign test-run: 0 error(s), 0 warning(s)
world verdant-reach: 0 error(s), 0 warning(s)
repository: 0 error(s), 0 warning(s)

PASS — 0 errors, 1 warning(s)
-> exit 0
```

---

## Cleanup

```
=== [32] delete campaigns/test-run/ and the throwaway test world ===

--- before ---
  campaigns/:
  other-campaign
  standalone-test
  test-run
  
  worlds/:
  verdant-reach

--- after ---
  campaigns/:
  .gitkeep
  
  worlds/:
  .gitkeep

--- git sees them gone ---
   D campaigns/standalone-test/CAMPAIGN.md
   D campaigns/standalone-test/CANON.md
   D campaigns/standalone-test/CHECKPOINT.md
   D campaigns/standalone-test/CLOCKS.md
   D campaigns/standalone-test/FLAGS.md
   D campaigns/standalone-test/PLAYER_PREFS.md
   D campaigns/standalone-test/QUESTS.md
   D campaigns/standalone-test/RULES_DELTAS.md
   D campaigns/standalone-test/TIMELINE.md
   D campaigns/standalone-test/WORLD.md
   D campaigns/standalone-test/bestiary/.gitkeep
   D campaigns/standalone-test/characters/PARTY.md
   D campaigns/standalone-test/characters/nobody.md
   D campaigns/standalone-test/checkpoints/.gitkeep
   D campaigns/standalone-test/checkpoints/001-standalone-works.md
   D campaigns/standalone-test/dashboard.html
   D campaigns/standalone-test/encounters/active.md
   D campaigns/standalone-test/encounters/history.md
   D campaigns/standalone-test/gm-private/README.md
   D campaigns/standalone-test/gm-private/prep/.gitkeep
   D campaigns/standalone-test/gm-private/secrets.md
   D campaigns/standalone-test/gm-private/seeds.md
   D campaigns/standalone-test/logs/dice-audit.md
   D campaigns/standalone-test/logs/loot.md
   D campaigns/standalone-test/logs/rolls.jsonl
   D campaigns/standalone-test/maps/.gitkeep
   D campaigns/standalone-test/npcs/ROSTER.md
   D campaigns/standalone-test/sessions/.gitkeep
   D campaigns/standalone-test/state.json
   D campaigns/test-run/CAMPAIGN.md
   D campaigns/test-run/CANON.md
   D campaigns/test-run/CHECKPOINT.md
   D campaigns/test-run/CLOCKS.md
   D campaigns/test-run/FLAGS.md
   D campaigns/test-run/PLAYER_PREFS.md
   D campaigns/test-run/QUESTS.md
   D campaigns/test-run/RULES_DELTAS.md
   D campaigns/test-run/TIMELINE.md
   D campaigns/test-run/WORLD.md
   D campaigns/test-run/bestiary/.gitkeep
   D campaigns/test-run/characters/PARTY.md
   D campaigns/test-run/characters/kaelen.md
   D campaigns/test-run/checkpoints/.gitkeep
   D campaigns/test-run/checkpoints/001-before-the-round-trip.md
   D campaigns/test-run/checkpoints/002-after-the-round-trip-mutations.md
   D campaigns/test-run/checkpoints/003-a-second-round-of-mutations.md
   D campaigns/test-run/checkpoints/004-one-more-to-show-the-numbering-continues.md
   D campaigns/test-run/checkpoints/005-four-rolls-and-some-damage.md
   D campaigns/test-run/checkpoints/006-mid-fight-round-1-to-prove-the-dashboard-is-regenerated.md
   D campaigns/test-run/checkpoints/007-prove-the-dashboard-is-regenerated-at-every-checkpoint.md
   D campaigns/test-run/checkpoints/008-prove-the-dashboard-is-regenerated-at-every-checkpoint.md
   D campaigns/test-run/checkpoints/009-before-the-off-screen-turn.md
   D campaigns/test-run/checkpoints/010-mid-combat-round-3-of-the-flooded-crypt-landing.md
   D campaigns/test-run/dashboard.html
   D campaigns/test-run/encounters/active.md
   D campaigns/test-run/encounters/history.md
   D campaigns/test-run/gm-private/README.md
   D campaigns/test-run/gm-private/prep/.gitkeep
   D campaigns/test-run/gm-private/prep/001-2026-09-30.md
   D campaigns/test-run/gm-private/secrets.md
   D campaigns/test-run/gm-private/seeds.md
   D campaigns/test-run/logs/dice-audit.md
   D campaigns/test-run/logs/loot.md
   D campaigns/test-run/logs/rolls.jsonl
   D campaigns/test-run/maps/.gitkeep
   D campaigns/test-run/maps/crypt-landing.md
   D campaigns/test-run/npcs/ROSTER.md
   D campaigns/test-run/sessions/.gitkeep
   D campaigns/test-run/state.json
   M tools/graph.py
   M tools/state.py
   M tools/validate.py
   M tools/world.py
  ?? DESIGN_NOTES.md

--- and the framework still validates with nothing in it ---
repository: 0 error(s), 0 warning(s)
  ok    no campaign-specific content found outside campaigns/

PASS — 0 errors, 0 warning(s)
-> exit 0

--- the tools still all run from a clean repository ---
🎲 check: 1d20+5 → [3] +5 = 8 vs DC 15 → FAILURE
Level-based DC, level 3, common: 18
  incredibly easy   8
  very easy         13
🔮 Does the framework still work with no campaign in it?
   Likely — yes on 6+ · rolled [13]
   → **YES, AND** — yes, plus something extra in your favour
   This answer is binding. Build forward from it (system/19-solo-oracle.md).
🎲 Urban Rumors [2] → The river ran red for an hour and the priests have stopped explaining it.: 1d12 → [2] = 2
```

---

## Flags and session flow

Checks 21, 22 and 29 are in the [Off-screen turn](#off-screen-turn) transcript above,
which was captured in one run with them.

---

## Verification pass 2 — Archives of Nethys

The original run was made while `2e.aonprd.com` was unreachable, so the numeric tables were checked
against the Foundry VTT PF2e source and five of seventeen were marked `⚠ UNVERIFIED`. The egress
policy later allowed AoN. Every table was re-read from the published text, and the checks that
depend on a corrected table were re-run. The full list of what was wrong is in `DESIGN_NOTES.md`
under "Pass 2"; this section holds the re-run output.

### Provenance, after the re-read

```
$ python3 tools/pf2e.py sources | tail -6

0 of 23 tables are unverified.

Every table above was read from Archives of Nethys, or is labelled as this
framework's own convention rather than a published rule. Re-verifying against
AoN found eight errors in this file; DESIGN_NOTES.md lists them under 'Pass 2'.
```

### Check 11, re-run — the corrected budget

```
$ python3 tools/pf2e.py encounter --party-level 3 --party-size 1 --threat moderate

Party level 3, party size 1

XP budget by threat level (as published):
  trivial      10 XP
  low           0 XP   (smoothed: 15)
  moderate     20 XP  <-- requested
  severe       30 XP
  extreme      40 XP

  ⚠ At a party of 1 the published rule sends low to 0 XP, because the Character Adjustment for Low and
    Moderate is the same (20). An encounter with nothing in it is not a threat level.
    Pass --smoothed for the 20-XP-per-character reading many tables use instead, or
    build to trivial and accept that it is trivial.

Build to 20 XP for a moderate encounter.
On clearing it, award 80 XP — the four-character figure.
```

The last line is the second correction, and it is the one that matters most to this campaign. XP
**awards** do not scale with party size — GM Core p.76: *"the XP awards for the encounter don't
change—you'll always award the amount of XP listed for a group of four characters."* The original
build scaled them, which would have made a solo character take roughly four times as long to level.

The whole grid, published against smoothed:

```
$ python3 tools/pf2e.py tables budgets

party_size | trivial | low      | moderate | severe | extreme
-----------|---------|----------|----------|--------|--------
1          | 10      | 0 (15)   | 20       | 30     | 40     
2          | 20      | 20 (30)  | 40       | 60     | 80     
3          | 30      | 40 (45)  | 60       | 90     | 120    
4          | 40      | 60       | 80       | 120    | 160    
5          | 50      | 80 (75)  | 100      | 150    | 200    
6          | 60      | 100 (90) | 120      | 180    | 240    

Published figure, with the smoothed alternative in brackets where they differ.
XP awarded is always the four-character figure: trivial 40, low 60, moderate 80, severe 120, extreme 160.
```

### Treasure, re-run — the percentage split was not a rule

```
$ python3 tools/pf2e.py treasure --level 5 --party-size 1

Treasure for one level of play at level 5, party size 1
Published total for four characters: 1350 gp

  As published, for four characters:
    permanent items (4): level 6, level 6, level 5, level 5
    consumables (6):     level 6, level 6, level 5, level 5, level 4, level 4
    currency:                320 gp

  Strict subtraction for the missing characters:
    permanent items (1): level 6
    consumables (0):     none
    currency:                80 gp

  The gentler reading the book invites (half the subtraction):
    permanent items (3): level 6, level 6, level 5
    consumables (4):     level 6, level 6, level 5, level 5
    currency:                240 gp

  Which to use is a judgement call, and the rule says so. Decide, write it in
  RULES_DELTAS.md, and keep logs/loot.md measured against the same choice.
```

The original build reported a single gp figure and a ~50/25/25 split. There is no such split in
GM Core: Table 6-1 names item counts and item levels.

### Settlements — a table that was not a table

```
$ python3 tools/pf2e.py settlement --level 6

A settlement of level 6:
  buys and sells common items up to item level 6
  how many of the top-end items, from the level-5 treasure row:
    permanent:   2x level 6, 2x level 5
    consumables: 2x level 6, 2x level 5, 2x level 4
  above that level: special order or commission; costs time, and the GM sets how much
```

`settlement_item_levels` was marked "unverified published table". It is not a published table at
all — GM Core p.168 gives a settlement a **level**. The size names remain as this framework's own
suggestion for picking one, now labelled as such, and the real rule is implemented beside it.

### The `system/` docs

Six inline values were wrong and are corrected in place, each with the AoN page it was read from:
the persistent-damage assisted flat check (**10**, not 11), the invented "at least 6 hours of
sleep" in a night's rest, the rune transfer cost (**10%** of the rune's Price and 1 day, not half),
the missing full-Price exception when selling coins, gems, art objects and raw materials, the
Treat Wounds toolkit requirement and 1-hour doubling, and the level-up progression presented as
universal when Player Core says the class table is the authority.

```
$ python3 tools/validate.py --all --repo
campaign third-beginnings: 0 error(s), 1 warning(s)
  warn  state.json holds no characters yet
repository: 0 error(s), 0 warning(s)

PASS — 0 errors, 1 warning(s)
```
