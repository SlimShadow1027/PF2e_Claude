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

Exploding dice are not supported. PF2e does not use them.

### Degrees of success are computed by the tool, never by the GM

- **Critical success** at total ≥ DC + 10
- **Success** at total ≥ DC
- **Failure** below DC
- **Critical failure** at total ≤ DC − 10
- A **natural 20** improves the degree by one step; a **natural 1** worsens it by one step.

The natural die face is printed separately so the shift is visible:

```
🎲 Kaelen — Strike (longsword): 1d20+13 → [20] +13 = 33 vs AC 40 → SUCCESS  [natural 20: upgraded from FAILURE]
```

The shift applies **after** the base degree, and is clamped: a natural 20 on an already-critical
success stays a critical success, and a natural 1 on an already-critical failure stays one.

> Source: Player Core / GM Core, Degrees of Success. Verified against the Foundry VTT PF2e
> implementation — `python3 tools/pf2e.py sources` (`degrees`).

**Flat checks have no degrees.** A DC 15 flat check to end persistent damage succeeds or fails;
a natural 20 does not make it a critical success. `roll.py flat` reflects this.

---

## Output shape

One compact line per public roll, always the same shape:

```
🎲 Kaelen — Strike (longsword): 1d20+13 → [14] +13 = 27 vs AC 21 → SUCCESS
🎲 Kaelen — Longsword damage: 1d8+4 → [6] +4 = 10 slashing
🎲 Kaelen — Longsword crit: (1d8+4) x2 → [6] +4 = 10 x2 = 20 slashing (critical)
```

A critical damage roll shows the undoubled total and the doubling, because
"`[6] +4 = 20`" looks like an error.

> PF2e criticals double the **whole** damage roll, modifiers included — not just the dice.

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

# a recovery check while dying
python3 tools/roll.py recovery --dying 2 --actor Kaelen --campaign X
# or, to roll it AND apply the result to state in one step:
python3 tools/state.py --campaign X recovery kaelen

# a Hero Point reroll (fortune)
python3 tools/roll.py fortune "1d20+13" --dc 21 --label "Hero Point reroll" --actor Kaelen --campaign X

# a random table
python3 tools/roll.py table system/16-random-tables.md "Urban Rumors" --campaign X
```

### Initiative tie-breaks

Higher total acts first. **On a tie between a party member and an adversary, the adversary acts
first.** `roll.py init` applies that automatically and says so.

Ties within one side are broken by a real d20 roll-off, logged like any other roll, rather than
by sorting on a name.

> Source: Player Core, Roll Initiative. Verified against the Foundry VTT PF2e implementation —
> `python3 tools/pf2e.py sources`.

### Fortune and misfortune

A Hero Point reroll, and any effect with the fortune trait, is `2d20kh1` — both dice are
rolled and both are logged, and the kept one is the natural die for degree purposes.
Misfortune is `2d20kl1`. **A roll cannot be both**; if a fortune and a misfortune effect would
apply, neither does, and `roll.py` refuses the combination rather than silently picking one.

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
