# 04 — The dice protocol

## The rule

**Every die roll is a real roll produced by `tools/roll.py`.** No die result is ever written
that did not come out of a tool invocation. Not an estimate, not a "narratively appropriate"
number, not a reconstruction of a roll that was meant to be made.

If you notice yourself about to state a number you did not roll — stop and roll it.

If a tool call fails, say it failed and roll again. A failed call is not licence to improvise.

## Private is not the same as fudged

Secret checks (the `secret` trait), enemy saves, enemy attacks in a mystery-mode campaign,
Stealth/Deception/Perception contests and Recall Knowledge are **all genuinely rolled**. What
changes is only what the player is shown: the number may be withheld and the outcome narrated.

The roll always happens. It always lands in the log. `tools/analyze.py` reports the public and
private subsets side by side so that this is a checkable claim and not a promise.

---

## The engine

`random.SystemRandom` — the operating system's cryptographic random source, not a seeded PRNG.
Nothing in this framework can reproduce a past roll, which is the point.

### Notation

| Form | Means |
|---|---|
| `NdM` | roll N dice of M faces |
| `+N` / `-N` | flat modifier; several terms are fine (`2d6+1d4-1`) |
| `2d20kh1` | keep highest — **fortune** |
| `2d20kl1` | keep lowest — **misfortune** |
| `4d6kh3` | keep the best three |
| `1d20r1` | reroll a 1 once, keep the second result |

Exploding dice are not supported. No supported ruleset uses them.

---

## The outcome is computed by the tool, never by the GM

**This section is the one place in this document where the rulesets differ, and they differ
a lot.** `roll.py` reads the campaign's `System:` and applies that game's rule; pass `--system`
to override it for one roll. The arithmetic lives in `pf2e.resolve`, `dnd5e.resolve` and
`dnd4e.resolve`, each with its own `Source:` note, so no game's answer is recalled from memory.

### Pathfinder: four degrees, and the natural-20 shift on everything

- **Critical success** at total ≥ DC + 10
- **Success** at total ≥ DC
- **Failure** below DC
- **Critical failure** at total ≤ DC − 10
- A **natural 20** improves the degree by one step; a **natural 1** worsens it by one step — on
  **every** check and save, not only attacks.

The natural die face is printed separately so the shift is visible:

```
🎲 Kaelen — Strike (longsword): 1d20+13 → [20] +13 = 33 vs AC 40 → SUCCESS  [natural 20: upgraded from FAILURE]
```

The shift applies **after** the base degree, and is clamped: a natural 20 on an already-critical
success stays a critical success, and a natural 1 on an already-critical failure stays one.

> Source: Player Core / GM Core, Degrees of Success. Verified against the Foundry VTT PF2e
> implementation — `python3 tools/pf2e.py sources` (`degrees_of_success`).

**Flat checks have no degrees.** A DC 15 flat check to end persistent damage succeeds or fails;
a natural 20 does not make it a critical success. `roll.py flat` reflects this.

### D&D 2024: pass or fail, and the natural-20 rules on attacks only

- **Meet or beat the target number** and it succeeds. Otherwise it fails. There is no ladder.
- A **natural 20 on an attack roll** hits regardless of AC and is a Critical Hit. A **natural 1**
  misses regardless of AC.
- **On an ability check or a saving throw, a 20 is just a 20.** No automatic success, no critical
  anything. The published rule is scoped to attack rolls and this framework scopes it the same way.

```
🎲 Thorne — Longsword: 1d20+7 → [20] +7 = 27 vs AC 15 → CRITICAL HIT  [natural 20: hits regardless of AC, and is a Critical Hit]
🎲 Thorne — Wisdom save: 1d20+4 → [20] +4 = 24 vs DC 14 → SUCCESS
```

Note the second line: a natural 20, a margin of ten, and still just `SUCCESS`.

**This is why `attack` is a separate command from `check` and `save`.** Rolling an attack with
`check` on a D&D campaign suppresses the crit; rolling a save with `attack` invents one. The
command names the kind of test, and the kind of test decides the rule.

> Source: SRD 5.2, "D20 Tests" → "Attack Rolls" → "Rolling 20 or 1" —
> `python3 tools/dnd5e.py sources` (`crit_rule`).

### D&D 4e: pass or fail, attacks crit, and "saving throw" means something else

- **Meet or beat the target number** and it succeeds. No ladder, as in D&D 2024.
- A **natural 20 on an attack roll** hits automatically and is a critical hit; a **natural 1**
  misses automatically. Checks and saves are unaffected.
- **The attacker rolls against a static defence** — AC, Fortitude, Reflex or Will. The defender
  never rolls. So what the other two games call a save is, here, the attacker's roll against
  Fortitude, Reflex or Will.
- **A 4e "saving throw" is an effect-ending roll**: a flat d20 against **10**, made at the end
  of your turn against each "save ends" effect. No ability modifier, no level term.
  `roll.py save` on a 4e campaign forces the target to 10 whatever DC is passed, because a 4e
  save has no other target number and honouring a wrong one silently would be worse than
  correcting it.
- **Half the character's level** is added to attack rolls, all four defences, all skill checks
  and initiative. Put it in the expression; the tool does not know the character's level.

```
🎲 Verrin — Longsword: 1d20+9 → [18] +9 = 27 vs AC 18 → HIT
🎲 Verrin — save vs ongoing fire: 1d20 → [8] = 8 vs flat DC 10 → FAILURE
🎲 Verrin — Death saving throw → 1/3 failures: 1d20 → [8] = 8 vs flat DC 10 → FAILURE
```

**4e has no two-dice swing under any name.** `--advantage` and `--disadvantage` are **refused**
on a 4e campaign: combat advantage is a flat **+2 to the attack roll**, so it goes in the
expression (`1d20+9+2`) where the log can show the real arithmetic.

> Source: there is none to cite. D&D 4e has no open-content release, so everything in this
> section is stated in this framework's own words and is marked "believed correct,
> unverifiable" — `python3 tools/dnd4e.py sources`. `system/dnd4e/README.md` explains why, and
> `LICENSE_NOTES.md` has the full statement.

---

## Output shape

One compact line per public roll, always the same shape:

```
🎲 Kaelen — Strike (longsword): 1d20+13 → [14] +13 = 27 vs AC 21 → SUCCESS
🎲 Kaelen — Longsword damage: 1d8+4 → [6] +4 = 10 slashing
🎲 Kaelen — Longsword crit: (1d8+4) x2 → [6] +4 = 10 x2 = 20 slashing (critical)
```

A critical damage roll shows its working, because `[6] +4 = 20` looks like an error. **How it
works differs by ruleset, and the line says which was applied:**

| | |
|---|---|
| **Pathfinder** | the **whole roll** doubles, modifiers included. `(1d8+4) x2 → [6] +4 = 10 x2 = 20` |
| **D&D 2024** | the **dice** double and the modifier is added once. `2d8+4 → [6,3] +4 = 13 (critical) — dice doubled from 1d8+4` |
| **D&D 4e** | the dice are **maximised** and nothing is rolled. `12+5 → +17 = 17 (critical) — maximum damage, dice not rolled (2d6+5 maximised to 12+5)` |

Three rulesets, three different answers to the same question, which is why the rule lives with
the ruleset and not with the dice.

The D&D 2024 case rewrites the expression and **rolls the extra die for real** rather than
multiplying a number that was already rolled — *"roll the attack's damage dice twice"* is an
instruction to roll, and the audit log shows both faces.

The 4e case is the opposite and the line says so explicitly: a 4e critical deals maximum damage,
so **no die is thrown at all** and the output does not pretend one was. Extra dice from a
high-crit weapon or a critical-only power **are** rolled — roll them as a separate damage roll,
because they are not maximised.

In all three, a term that keeps highest or lowest dice is refused rather than guessed at.

Private and secret rolls print the full detail to the log and a redacted line to chat:

```
🎲 (secret) Recall Knowledge (Religion) — rolled, result withheld
```

…and then the GM narrates the information the player actually gets, based on the real degree of
success. Pass `--gm` to also print a `> **GM-ONLY**` block with the withheld numbers, for when
the GM needs to read its own roll.

---

## Transparency modes

Set per campaign in `PLAYER_PREFS.md` and in `state.json`; changeable mid-game with one
sentence.

| Mode | The player sees |
|---|---|
| `glass` | Everything: enemy rolls, enemy AC and HP, and every DC. |
| `standard` | Their own rolls and DCs; enemy rolls as numbers but their AC and HP hidden; `secret`-trait checks hidden. |
| `mystery` | Only narration for anything on the enemy side. Their own rolls are still always shown. |

**In every mode the audit log records everything.** The player can read
`logs/rolls.jsonl` afterward and confirm nothing was invented. The dashboard respects the mode
too, or it would leak enemy HP.

To change it:

```
python3 tools/state.py --campaign <slug> transparency mystery
```

and pass `--transparency mystery` on rolls, so the redaction matches.

---

## Roll several things at once

Combat crawls if each of six enemies' saves is a separate call. Several expressions go in one
invocation:

```
python3 tools/roll.py save "1d20+11" "1d20+11" "1d20+9" --dc 22 \
    --actor "Ghoul A" --actor "Ghoul B" --actor "Ghast" \
    --label "Fortitude vs Fireball" --private --campaign <slug>
```

For a mixed batch — three attacks and the damage, or a squad's whole round:

```
python3 tools/roll.py batch --campaign <slug> --json-arg '[
  {"kind":"check","expr":"1d20+13","dc":21,"actor":"Ghoul A","label":"Jaws","private":true},
  {"kind":"check","expr":"1d20+8","dc":21,"actor":"Ghoul A","label":"Claw","map":1,"private":true},
  {"kind":"damage","expr":"1d8+4","type":"piercing","label":"Jaws damage","private":true}
]'
```

Batching is a speed change, not a math change. Each roll is still independent, still logged
separately, and still interpreted by the tool.

---

## The common calls

```
# a skill check or an attack
python3 tools/roll.py check "1d20+13" --dc 21 --label "Strike (longsword)" --actor Kaelen --map 0 --dc-label AC --campaign X

# a secret check
python3 tools/roll.py check "1d20+9" --dc 24 --secret --label "Recall Knowledge (Religion)" --campaign X

# a save
python3 tools/roll.py save "1d20+11" --dc 22 --actor "Ghoul B" --private --label "Fortitude vs Fireball" --campaign X

# damage, and a critical
python3 tools/roll.py damage "1d8+4" --type slashing --label "Longsword" --campaign X
python3 tools/roll.py damage "1d8+4" --crit --type slashing --label "Longsword crit" --campaign X

# a flat check
python3 tools/roll.py flat 11 --label "Persistent bleed recovery" --campaign X

# initiative for the whole room
python3 tools/roll.py init --actors "kaelen:+7,ghoul-a:+5,ghoul-b:+5" --party kaelen --campaign X

# PF2e: a recovery check while dying
python3 tools/roll.py recovery --dying 2 --actor Kaelen --campaign X
# or, to roll it AND apply the result to state in one step:
python3 tools/state.py --campaign X recovery kaelen

# PF2e: a Hero Point reroll (fortune)
python3 tools/roll.py fortune "1d20+13" --dc 21 --label "Hero Point reroll" --actor Kaelen --campaign X

# Both D&D editions: an attack roll, which is the only kind that can crit
python3 tools/roll.py attack "1d20+7" --ac 15 --actor Thorne --campaign X --label "Longsword"

# D&D 2024: a check with Advantage (refused on a 4e campaign — 4e has no two-dice swing)
python3 tools/roll.py check "1d20+5" --dc 15 --advantage --label "Stealth" --campaign X

# D&D 4e: combat advantage is a flat +2, so it goes in the expression
python3 tools/roll.py attack "1d20+9+2" --ac 18 --label "Longsword (combat advantage)" --campaign X

# D&D 4e: a saving throw ENDS an effect, and is always a flat d20 vs 10
python3 tools/roll.py save "1d20" --dc 10 --label "save vs ongoing fire (5)" --campaign X

# Either D&D edition: a death saving throw at 0 HP. The semantics differ — 2024 counts
# successes as well as failures; 4e counts failures only — and roll.py applies the right one.
python3 tools/roll.py death-save --failures 1 --actor Thorne --campaign X
# or, to roll it AND apply the result to state in one step:
python3 tools/state.py --campaign X death-save roll thorne

# D&D 4e: a critical, which MAXIMISES the dice rather than doubling anything
python3 tools/roll.py damage "2d6+5" --crit --type fire --label "Flaming burst crit" --campaign X

# a random table
python3 tools/roll.py table system/16-random-tables.md "Urban Rumors" --campaign X
```

`recovery` and `death-save` each refuse to run on the other game's campaign, and name the command
that was wanted.

### Initiative tie-breaks

Higher total acts first. What happens on a tie differs, and `roll.py init` prints the rule it
applied:

- **Pathfinder:** on a tie between a party member and an adversary, **the adversary acts first**.
  Ties within one side are broken by a real d20 roll-off, logged like any other roll, rather than
  by sorting on a name.
  > Source: Player Core, Roll Initiative. Verified against the Foundry VTT PF2e implementation —
  > `python3 tools/pf2e.py sources`.
- **D&D 2024:** the published rule is that **the GM decides** — among tied monsters, and in a
  monster-versus-character tie; the players decide among tied characters. An automated GM deciding
  that silently is exactly the unlogged choice this document exists to prevent, so **this framework
  rolls every tie off with real dice instead** and prints the published rule beside the result.
  That substitution is this framework's convention, not the published rule, and the player may
  override the order.
  > Source: SRD 5.2, "Combat" → "Initiative" → "Ties".

### The two dice, under two names

`2d20kh1` and `2d20kl1` are the same operation in the two rulesets that have it:

| Pathfinder | D&D 2024 |
|---|---|
| a **fortune** effect — a Hero Point reroll, and anything with the fortune trait | **Advantage** |
| a **misfortune** effect | **Disadvantage** |

Both dice are rolled and both are logged, and the kept one is the natural die for outcome purposes.
The chat line prints whichever word the campaign's ruleset uses, so a D&D roll never reports
`[fortune]`.

**What happens when both apply differs, and this is a real rules difference rather than a
presentation one:**

- **Pathfinder:** a roll cannot be both. `roll.py fortune` / `misfortune` refuse the combination
  rather than silently picking one.
- **D&D 2024:** *"If circumstances cause a roll to have both Advantage and Disadvantage, the roll
  has neither of them, and you roll one d20"* — true even if several things impose Disadvantage and
  only one grants Advantage. `--advantage --disadvantage` therefore **cancels** to a single d20,
  which is the published rule, and the log records that it cancelled.

---

## The audit log

`campaigns/<slug>/logs/rolls.jsonl`, one JSON object per line, append-only. Never edited,
never pruned, never rewritten. It is committed alongside the state it produced at each
checkpoint, which makes the trail tamper-evident and not merely append-only: an altered past
line changes a commit that is already in the history.

The full field list is in `tools/README.md`. The fields that make it auditable:

- `dice[].rolls` — every face the generator produced, **including any a keep-highest
  discarded**, because the question is whether the source is straight and a discarded die
  still came out of it.
- `natural`, `unadjusted_degree`, `degree_shift` — so the natural-20 shift can be checked.
- `shown`, `secret`, `private`, `transparency` — so the public and private subsets can be
  compared.

### Reading it back

```
python3 tools/analyze.py --campaign <slug>
python3 tools/analyze.py --campaign <slug> --fairness
python3 tools/analyze.py --campaign <slug> --one-line
```

The end-of-session routine appends the one-line fairness summary to the session log. `/dice-audit`
runs the full report.

**If the fairness numbers ever look off, say so unprompted.** The whole point of the log is
that neither the GM nor the player has to take the dice on faith. `analyze.py` will flag a
chi-square that does not fit and a drift between the public and private subsets; do not bury
that behind a reassuring sentence.
