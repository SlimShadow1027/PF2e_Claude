# 12 (D&D 4e) — Rules quick reference

**Replaces `system/12-rules-quick-reference.md` for a campaign with `System: dnd4e`.** Read
this one instead of that one; they disagree on purpose.

> ## Provenance warning — read once, then remember it
>
> **This document is weaker than its two siblings, and not by choice.** Everything below is
> stated from the published 4e rules **in this framework's own words**, because D&D 4e has no
> open-content release: the Game System License permitted no Open Game Content, the so-called
> "4e SRD" was an index of terms and templates rather than the rules, and the GSL is no longer
> offered. There is nothing open to quote and nothing open to verify against.
>
> So: treat every mechanic here as **believed correct, unverifiable**. Where a number would
> have to come from a table, this document does not give one — it names the book and sends you
> to `tools/dnd4e_tables.json`. See `system/dnd4e/README.md` and `LICENSE_NOTES.md`.
>
> `python3 tools/dnd4e.py sources` prints every statement with that marking. `python3
> tools/dnd4e.py tables` says which numbers are still missing.

---

## The core resolution

One d20, plus modifiers, against a target number. **Meet it or beat it.**

- **Pass or fail**, with no degrees of success. There is no beat-by-10 critical and no
  miss-by-10 critical failure. If you find yourself computing a margin, you are in
  Pathfinder's head.
- **Natural 20 and natural 1 matter on attack rolls only.** A natural 20 hits automatically
  and is a critical hit; a natural 1 misses automatically. On a skill check, an ability check
  or a saving throw, a 20 is just a 20.
- **Half your level, rounded down, is added** to attack rolls, all four defences, all skill
  checks and initiative. This is why 4e numbers climb steadily and relentlessly with level,
  and the single biggest reason a 4e level number cannot be read across to another ruleset.

```
python3 tools/roll.py attack "1d20+9" --ac 18 --label "Longsword" --actor Verrin --campaign X
python3 tools/roll.py check  "1d20+7" --dc 15 --label "Stealth" --campaign X
```

### Four defences, not one AC and three saves

**AC, Fortitude, Reflex, Will.** All four are static numbers the attacker rolls against — the
defender never rolls. An attack says which defence it targets.

This is the overlap that catches people hardest. In Pathfinder and in D&D 2024 a "save" is a
roll the *defender* makes. In 4e the defender rolls nothing, and the word **saving throw**
means something else entirely (below).

### The saving throw is an effect-ending roll

A 4e saving throw ends a lasting effect. It is a **flat d20 against 10** — no ability
modifier, no level term, though specific bonuses to saves do apply. Made at the end of your
turn against each effect that says "save ends".

```
python3 tools/roll.py save "1d20" --dc 10 --label "save vs ongoing fire" --campaign X
```

`roll.py` forces the DC to 10 on a 4e save whatever you pass, because a 4e save has no other
target number and silently honouring a wrong one would be worse than correcting it.

### Combat advantage: a flat +2

**+2 to the attack roll.** Not a second die. It does not stack with itself. Put it in the
expression so the log shows the arithmetic:

```
python3 tools/roll.py attack "1d20+9+2" --ac 18 --label "Longsword (combat advantage)" --campaign X
```

`roll.py` **refuses** `--advantage` and `--disadvantage` on a 4e campaign. Rolling two d20s
and keeping one is another game's mechanic; applying it under a 4e label would quietly change
every attack's odds.

---

## The turn

| | |
|---|---|
| **Standard action** | One. The attack, the big power, the Second Wind |
| **Move action** | One. Spends your speed in **squares** |
| **Minor action** | One. Draw a weapon, open a door, many sustains |
| **Free actions** | Any number |
| **Immediate action** | One **per round**, not per turn. An interrupt or a reaction, taken on somebody else's turn |
| **Opportunity action** | One per *other creature's* turn |

Usable in any order. **A standard may be traded down** for a move or a minor, and a move for a
minor — never upward. The tracker enforces this and its refusals name the trade you still have:

```
python3 tools/state.py --campaign X encounter action "Verrin" 1 --kind standard
python3 tools/state.py --campaign X encounter action "Verrin" 1 --kind minor
python3 tools/state.py --campaign X encounter action "Verrin" 3 --kind squares
```

**Movement is in squares of five feet**, and the framework stores squares, not feet. A speed of
6 is 30 feet. Do not write 30 in a 4e campaign; `blank_character_fields` defaults to 6 and the
tracker's `mov` column counts down in squares.

### Powers, not slots

At-will, encounter, daily. **At-will powers are not tracked** — there is nothing to spend.

```
python3 tools/state.py --campaign X power add verrin "Twin Strike" encounter
python3 tools/state.py --campaign X power use verrin "Twin Strike"
python3 tools/state.py --campaign X power list verrin
```

`slots` is refused on a 4e campaign. There are no spell slots and no ranks or levels of slot.

### Marked

A 4e creature that marks you imposes a penalty on your attacks against anyone else, and the
mark is tracked on the combatant (`marked_by`). Only one mark at a time — a new one replaces
the old. This condition exists in neither sibling ruleset.

---

## Damage, criticals and healing

### A critical hit deals maximum damage

**Not doubled dice. Not a doubled total. The maximum.** `2d6+5` becomes `17`, every time.
Magic weapons and critical-only powers add their own dice **on top**, and those dice **are**
rolled — roll them as a separate damage roll, because they are not maximised.

```
python3 tools/roll.py damage "2d6+5" --crit --type fire --campaign X
  → 12+5 → +17 = 17 fire (critical) — maximum damage, dice not rolled (2d6+5 maximised to 12+5)
python3 tools/roll.py damage "1d6" --type fire --label "flaming weapon crit die" --campaign X
```

The three rulesets, side by side, because this is where muscle memory hurts most:

| Ruleset | On a critical hit |
|---|---|
| Pathfinder 2e | The **whole roll** doubled, modifiers included |
| D&D 2024 | The damage **dice** doubled, modifier added once |
| **D&D 4e** | The damage dice **maximised**; nothing extra rolled |

### Bloodied

At **half maximum hit points or fewer**. In 4e this is a real condition with rules keyed off
it — powers that trigger on bloodied, monsters that change behaviour. Contrast D&D 2024, where
"Bloodied" is a flag with no effect of its own.

### Healing surges are the real clock

A per-day pool. Spending one restores **a quarter of maximum hit points**, rounded down. Most
healing in 4e *spends a surge* rather than being free, which is why the surge count — not the
hit point total — is what tells you whether the day can continue.

The pool is **the class's own surges-per-day plus the Constitution modifier**. The class number
is in its class entry, which is not open content, so pass it in:

```
python3 tools/state.py --campaign X add-character "Verrin Ash" --level 3 --hp 38 --ac 18 \
    --fort 15 --ref 17 --will 14 --str 14 --con 16 --dex 18 --int 10 --wis 12 --cha 8 --surges 7
python3 tools/state.py --campaign X surge spend verrin-ash
python3 tools/state.py --campaign X surge list
```

A pool of 0 makes a character unhealable, and `add-character` warns loudly when it is left
unset.

### Second Wind

Once per encounter, as a standard action: spend a healing surge and take a bonus to all
defences until the start of your next turn. Restored by a short rest.

```
python3 tools/state.py --campaign X second-wind use verrin-ash
```

### At 0 hit points and below

**Hit points keep going down.** This is the structural difference from both siblings.

- At 0 or below: **dying and unconscious**, making a **death saving throw** at the end of each
  of your turns — a flat d20 against 10. Below 10 is a failure. **10 or more is not a success
  that accumulates**; it is simply not a failure, which is why there is no success counter.
  **Three failures** before an extended rest is death. A **natural 20** lets you spend a
  healing surge and act.
- **Death also comes from the depth**: a character dies when reduced to a negative total equal
  to their **bloodied value**. A 38 HP character dies at −19.

```
python3 tools/state.py --campaign X death-save roll verrin-ash
python3 tools/state.py --campaign X hp-below verrin-ash 12     # correcting the depth by hand
```

`damage` keeps the depth itself (`hp_below_zero`) and reports it against the threshold. Any
healing ends dying and clears both the failures and the depth.

| At 0 HP | Pathfinder 2e | D&D 2024 | **D&D 4e** |
|---|---|---|---|
| Clock | dying, counting up; dying 4 is death, and wounded makes the next one worse | 3 successes / 3 failures, plus Stable | **3 failures only**; no successes, no Stable |
| Floor | HP stop at 0 | HP stop at 0 | **HP keep falling**; death at negative bloodied |
| Instant death | — | damage past 0 ≥ maximum HP | reaching the negative threshold |
| Natural 20 on the roll | upgrades the degree | regain 1 HP | **spend a healing surge and act** |

---

## Rest

| | 4e | D&D 2024 | Pathfinder 2e |
|---|---|---|---|
| Short | **5 minutes** — encounter powers back, Second Wind back; HP only by spending surges | 1 hour | — |
| Long | **Extended rest, 6 hours** — HP full, surge pool full, dailies back, death-save failures cleared, one per 24 hours | Long Rest, 8 hours | daily preparations |

```
python3 tools/state.py --campaign X short-rest
python3 tools/state.py --campaign X extended-rest
```

`long-rest` is refused on a 4e campaign and names `extended-rest` instead.

---

## Action points and milestones

An **action point** buys an **extra action** — not a reroll. One spend per encounter.

A **milestone** is every second encounter completed without an extended rest, and grants an
action point. An extended rest resets the pool to 1 and the milestone count to 0.

```
python3 tools/state.py --campaign X milestone                  # whole party
python3 tools/state.py --campaign X action-point spend verrin-ash
```

The dice audit says so explicitly: there is nothing in the roll log to audit for action points,
because they never produce a die. Contrast Hero Points and Heroic Inspiration, which do.

---

## Levels, tiers and XP

**Thirty levels in three tiers of ten**: Heroic 1–10, Paragon 11–20, Epic 21–30. Both sibling
rulesets stop at 20.

XP is **cumulative** and never resets, as in D&D 2024 and unlike Pathfinder's flat 1,000
per level with a resetting counter. The thresholds are a table this framework does not have:
fill `character_xp` in `tools/dnd4e_tables.json`.

```
python3 tools/dnd4e.py advancement              # all 30 levels; "(not filled)" where the table is empty
python3 tools/state.py --campaign X xp add 1200
```

**XP from an encounter is divided by the party size.** This is 4e's own answer and it differs
from both siblings — Pathfinder awards a flat per-character amount from a level-difference
table, and D&D 2024 awards the monsters' total. For a party of one it means a solo character
banks the **whole** encounter's XP, which levels them roughly five times faster than a party
of five. `system/dnd4e/03-difficulty-and-solo-levers.md` is about what to do with that.

---

## Money and carrying

**Coins: cp, sp, gp, pp.** Ten copper to a silver, ten silver to a gold, and **one hundred gold
to a platinum** — not ten. A purse copied across rulesets is wrong even where the coin names
match.

Astral diamonds (10,000 gp) are deliberately **not** a denomination here; record one as an
item, because adding a 10,000-gp coin to the purse makes every small purchase unreadable.

**Carrying is in pounds**: ten times the Strength score as a normal load, twice that as a heavy
load at the cost of being slowed, five times the normal load as a maximum drag. The framework
reports the normal load as the limit and names the heavy load; it does not apply slowed for you.

```
python3 tools/state.py --campaign X item add "Chainmail" --owner verrin-ash --weight 40
python3 tools/state.py --campaign X carry
```

`--bulk` is refused: Bulk is Pathfinder's unit.

---

## Monsters: roles and ranks

**Roles** describe how a monster fights: artillery, brute, controller, lurker, minion,
skirmisher, soldier. (Characters have their own four: controller, defender, leader, striker.)

**Ranks** describe how much monster it is: standard, elite, solo, minion. **A minion has
exactly 1 hit point** and takes no damage from a missed attack — this is a rule, not a
shorthand, and the tracker warns if a minion is entered with any other hit point total.

```
python3 tools/state.py --campaign X encounter add "Kobold Skirmisher" --side adversary \
    --hp 27 --init 15 --level 1 --role skirmisher
python3 tools/state.py --campaign X encounter add "Kobold Minion" --side adversary \
    --hp 1 --init 12 --level 1 --role minion --rank minion
```

Monster statistics come from your books, named by source and level, exactly as the other two
rulesets require — rule 4 of the GM contract does not relax here. What this framework cannot
do is give you a benchmark to check them against until `monster_benchmarks` is filled.

---

## Conditions

4e's list differs from both siblings in **membership and in effect**. The ones worth naming:

- **marked** and **dominated** exist here and in neither sibling.
- **dazed** is 4e's own; it is not D&D 2024's *stunned*.
- **weakened** halves the damage you deal.
- **bloodied** is a real condition with rules keyed off it.
- **ongoing damage** carries an amount, so it is a valued condition.

```
python3 tools/state.py --campaign X condition add verrin-ash dazed --duration "end-of-turn"
python3 tools/state.py --campaign X condition add verrin-ash ongoing-damage 5 --duration "2 rounds"
```

`condition add` refuses a name from another ruleset and says which ruleset it belongs to.
`python3 tools/dnd4e.py mechanics` prints the full list this framework knows.

---

## Difficulty classes do not come from here

4e has a **DC by level** table, and this framework does not ship it — and that table was
**revised by errata**, so two printings disagree. Fill `dc_by_level`, record which printing in
its `_printing` field, and then:

```
python3 tools/dnd4e.py dc --level 5
```

There is no `--threat` on `dnd4e.py encounter`, and that is not an omission: 4e tunes a fight's
difficulty by setting the encounter's **level** against the party's, not by picking a budget
column. The budget is one number. If your printing does give difficulty columns, fill
`encounter_budget_columns` and they will appear.

Until then it refuses and names the book. Do not substitute D&D 2024's flat DCs (they do not
rise with level) or Pathfinder's DC-by-level table (a different scale entirely).

---

## The commands

```
python3 tools/rules.py which <slug>                  # confirm you are in 4e before anything
python3 tools/dnd4e.py tables                        # what still needs filling
python3 tools/dnd4e.py sources                       # every statement, with its marking
python3 tools/dnd4e.py mechanics                     # the full prose statement of the rules
python3 tools/dnd4e.py encounter --party-level 3 --party-size 1 \
    --monster 1x4:standard 3x3:minion         # LEVEL, LEVEL:ROLE, or Nx LEVEL:ROLE
python3 tools/dnd4e.py advancement                   # the 30-level table and its tiers
python3 tools/dnd4e.py dc --level 5
python3 tools/dnd4e.py treasure --level 4
python3 tools/dnd4e.py resolve --total 24 --dc 18 --kind attack
```

Player-facing commands 4e adds: `short rest` · `extended rest` · `surge` · `second wind` ·
`action point` · `milestone` · `power` · `death save`. See `system/14-player-commands.md`.
