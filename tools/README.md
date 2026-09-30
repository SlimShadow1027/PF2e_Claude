# tools/

All dice and all math live here. Nothing in this framework is done by mental arithmetic, and
no die result is ever written that did not come out of one of these programs.

**Standard library Python only.** No third-party dependencies, no build step, nothing to
install. Every tool runs as `python3 tools/<name>.py`.

## What each one is for

| Tool | Job |
|---|---|
| `roll.py` | The dice engine and the append-only audit log. The only source of random numbers. |
| `state.py` | The only writer of `campaigns/<slug>/state.json`. Also renders `CHECKPOINT.md`, takes checkpoints, makes the git commit, and restores. |
| `pf2e.py` | The rules tables as data, each with a `Source:` line. Encounter budgets, treasure, DCs, the calendar. |
| `new_campaign.py` | Scaffolds `campaigns/<slug>/` from `templates/`. |
| `validate.py` | Catches mechanical drift. Run it when something feels off, and before a long session. |
| `oracle.py` | Yes/no questions on a published likelihood ladder, scene checks, meaning tables, quantities. |
| `world.py` | The optional shared-setting layer under `worlds/`: promotion, date-gated reads, legacy records. |
| `graph.py` | The NPC relationship graph, as Mermaid, into `WORLD.md`. |
| `analyze.py` | Reads the roll log back: fairness (public vs. private) and what the numbers say about play. |
| `dashboard.py` | One offline, self-contained HTML file per campaign, regenerated at every checkpoint. |

Import graph, so a change stays predictable: `roll.py` depends on nothing; `pf2e.py` imports
`roll.py` for its path helpers; everything else imports those two.

## `roll.py` — dice

```
python3 tools/roll.py check  "1d20+13" --dc 21 --label "Strike (longsword)" --actor Kaelen --map 0
python3 tools/roll.py check  "1d20+9"  --dc 24 --secret --label "Recall Knowledge (Religion)"
python3 tools/roll.py damage "1d8+4" --crit --type slashing --label "Longsword crit"
python3 tools/roll.py save   "1d20+11" --dc 22 --actor "Ghoul B" --private --label "Fortitude vs Fireball"
python3 tools/roll.py flat   11 --label "Persistent bleed recovery"
python3 tools/roll.py init   --actors "kaelen:+7,ghoul-a:+5,ghoul-b:+5" --party kaelen
python3 tools/roll.py recovery --dying 2
python3 tools/roll.py table  system/16-random-tables.md "Urban Rumors"
python3 tools/roll.py fortune "1d20+13" --dc 21 --label "Hero Point reroll"
python3 tools/roll.py misfortune "1d20+13" --dc 21 --label "Misfortune effect"
python3 tools/roll.py expr "3d6+2"
```

Add `--campaign <slug>` to any of them and the roll is appended to that campaign's
`logs/rolls.jsonl`. Without it, nothing is logged and the tool says so on stderr — it will
not guess which campaign you meant.

**Notation:** `NdM`, `+N`/`-N` modifiers, several terms (`2d6+1d4-1`), `kh<n>` keep highest
(fortune), `kl<n>` keep lowest (misfortune), `r<N>` reroll a die at or below N once.
Exploding dice are not supported and PF2e does not need them.

**Rolling several things at once.** Combat crawls if each enemy's save is a separate call, so
several expressions go in one invocation:

```
python3 tools/roll.py save "1d20+11" "1d20+11" "1d20+9" --dc 22 \
    --actor "Ghoul A" --actor "Ghoul B" --actor "Ghast" --label "Fortitude vs Fireball" --private
```

For a mixed batch, describe it as JSON:

```
python3 tools/roll.py batch --json-arg '[
  {"kind":"save","expr":"1d20+11","dc":22,"actor":"Ghoul A","label":"Fort vs Fireball","private":true},
  {"kind":"damage","expr":"6d6","type":"fire","label":"Fireball"}
]'
```

**Visibility.** `--secret` is the `secret` trait: the roll happens, the number is withheld,
and the outcome is narrated. `--private` is a GM-side roll shown according to the campaign's
`--transparency` mode. Either way the full detail goes to the log. `--gm` additionally prints
the withheld numbers in a `> **GM-ONLY**` block, for when the GM needs to read its own roll.

**Degrees of success are computed by the tool**, never by the GM, including the one-step shift
on a natural 20 or a natural 1 — which is printed so the shift is visible.

## `state.py` — state

`--campaign <slug>` is required. A few of the commands, all of which refuse impossible states:

```
python3 tools/state.py --campaign X get pcs.kaelen.hp
python3 tools/state.py --campaign X damage kaelen 12 [--from-crit]
python3 tools/state.py --campaign X heal kaelen 8
python3 tools/state.py --campaign X condition add kaelen frightened 2 --duration "2 rounds"
python3 tools/state.py --campaign X condition tick kaelen
python3 tools/state.py --campaign X gold add 42gp 3sp
python3 tools/state.py --campaign X item add "Healing Potion (Lesser)" 2 --owner kaelen --bulk L --kind consumable
python3 tools/state.py --campaign X hero spend kaelen
python3 tools/state.py --campaign X recovery kaelen          # rolls a real recovery check and applies it
python3 tools/state.py --campaign X clock advance "Cult's Ritual" 1
python3 tools/state.py --campaign X advance-time "4 hours"
python3 tools/state.py --campaign X render                   # rewrite CHECKPOINT.md
python3 tools/state.py --campaign X checkpoint "Escaped the flooded crypt"
python3 tools/state.py --campaign X restore 007
python3 tools/state.py --campaign X bulk
python3 tools/state.py --campaign X daily-prep
```

The encounter tracker, which is what a mid-combat checkpoint restores:

```
python3 tools/state.py --campaign X encounter start "Crypt landing" --objective "Reach the lever in 6 rounds" --map crypt-landing
python3 tools/state.py --campaign X encounter add Kaelen --side party --ref kaelen --init 18 --position C4
python3 tools/state.py --campaign X encounter add "Ghoul A" --side adversary --init 19 --hp 28 --position E5
python3 tools/state.py --campaign X encounter next
python3 tools/state.py --campaign X encounter action "Ghoul A" 2
python3 tools/state.py --campaign X encounter map-step "Ghoul A"
python3 tools/state.py --campaign X encounter reaction Kaelen "Reactive Strike"
python3 tools/state.py --campaign X encounter status
python3 tools/state.py --campaign X encounter end
```

Party combatants carry `--ref <character>` and read their HP and conditions out of `pcs`,
rather than holding a second copy. Two copies of the number that decides a death is exactly
the drift this framework exists to prevent.

`checkpoint` writes an immutable snapshot with the full state embedded, re-renders
`CHECKPOINT.md`, regenerates the dashboard, and makes the git commit itself so it cannot be
forgotten. If git is unavailable it says so rather than skipping quietly.

## `pf2e.py` — tables

```
python3 tools/pf2e.py encounter --party-level 3 --party-size 1 --threat moderate
python3 tools/pf2e.py encounter --party-level 3 --party-size 1 --add "ghoul:2" --add "ghast:3"
python3 tools/pf2e.py encounter --party-level 5 --party-size 1 --hazard "rune trap:4 complex"
python3 tools/pf2e.py treasure --level 5 --party-size 1
python3 tools/pf2e.py dc --level 7 --rarity rare
python3 tools/pf2e.py dc --rank expert
python3 tools/pf2e.py tables level-dcs        # also: simple-dcs creature-xp hazard-xp item-bonuses
                                              #       treasure earn-income travel budgets
python3 tools/pf2e.py sources                 # provenance of every table, verified or not
python3 tools/pf2e.py time --advance "3 days 4 hours"
```

`sources` is the important one. It prints where every table came from and which are marked
`⚠ UNVERIFIED`, so a number is never used on trust.

## `oracle.py`

```
python3 tools/oracle.py ask "Is the side gate guarded?" --odds unlikely
python3 tools/oracle.py scene --expectation "the meeting goes ahead quietly"
python3 tools/oracle.py meaning --pair action-theme
python3 tools/oracle.py howmany --range 1-6 --label "guards at the gate"
python3 tools/oracle.py reaction --who "Sergeant Aleth" --mod 2
python3 tools/oracle.py ladder
python3 tools/oracle.py calibrate -n 2000
```

An oracle result is **binding on the GM**. See `system/19-solo-oracle.md`.

## `analyze.py`

```
python3 tools/analyze.py --campaign X
python3 tools/analyze.py --campaign X --since session-7 --actor kaelen
python3 tools/analyze.py --campaign X --fairness
python3 tools/analyze.py --campaign X --one-line       # the line the session log gets
```

## `dashboard.py`, `validate.py`, `graph.py`, `world.py`

```
python3 tools/dashboard.py --campaign X
python3 tools/validate.py --campaign X
python3 tools/validate.py --all --repo -v
python3 tools/graph.py --campaign X
python3 tools/world.py init "The Verdant Reach"
python3 tools/world.py link --campaign X --world verdant-reach --start-date "4712 AR"
python3 tools/world.py as-of verdant-reach "4712 AR"
python3 tools/world.py promote --campaign X --date "12 Desnus 4712 AR" --title "..." \
    --happened "..." --changed "..." --visibility public
python3 tools/world.py legacy --campaign X --character kaelen
python3 tools/world.py timeline verdant-reach
```

## The log format

One JSON object per line in `campaigns/<slug>/logs/rolls.jsonl`, append-only, never rewritten.
The fields that matter when reading it back:

| Field | Means |
|---|---|
| `seq` | position in the log; strictly increasing |
| `ts` | UTC timestamp |
| `kind` | `check`, `save`, `damage`, `flat`, `recovery`, `initiative`, `table`, `oracle`, … |
| `expr` | the expression as asked for |
| `dice[]` | each group: `faces`, every face in `rolls`, which were `kept` and `dropped`, any `rerolled` |
| `natural` | the check die — the kept d20 face |
| `modifier`, `total` | the flat modifier and the final total |
| `dc`, `degree`, `degree_index` | the DC and the computed degree of success |
| `unadjusted_degree`, `degree_shift`, `nat20`, `nat1` | the degree before the natural-20/1 shift, and the shift |
| `shown`, `secret`, `private`, `transparency` | whether the number was shown, and why |
| `tags` | free-form: `oracle`, `offscreen`, `initiative`, `recovery`, … |
| `session`, `checkpoint` | where in the campaign the roll happened |
| `rng` | `random.SystemRandom` |

`dice[].rolls` holds every face the generator produced, including ones a keep-highest threw
away, because the question the fairness report answers is whether the random source is
straight — and a discarded die still came out of it.
