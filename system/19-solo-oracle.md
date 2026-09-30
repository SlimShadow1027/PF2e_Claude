# 19 — The solo oracle

In solo play you sometimes want to interrogate the fiction directly rather than wait to be told:
*is the gate guarded? does she believe me? is there another way out?* An oracle answers those
with dice instead of with the GM's judgment, which keeps the world from bending toward whatever
either of you expected.

```
python3 tools/oracle.py ask "Is the side gate guarded?" --odds unlikely --campaign X
python3 tools/oracle.py scene --expectation "the meeting goes ahead quietly" --campaign X
python3 tools/oracle.py meaning --pair action-theme --campaign X
python3 tools/oracle.py howmany --range 1-6 --label "guards at the gate" --campaign X
python3 tools/oracle.py reaction --who "Sergeant Aleth" --mod 2 --campaign X
```

---

## The rule that makes it work

**An oracle result is binding on the GM.**

When the player consults it, the GM takes the answer as established fact and builds forward from
it — **including when it wrecks what the GM had planned.** The GM does not reroll it, does not
reinterpret it toward its prep, and does not quietly route around it.

There is exactly one legitimate override: **if the answer contradicts something already in
`CANON.md`, say so and re-ask a better question.** Not "that does not fit what I had in mind" —
that is the case the rule exists to prevent.

Oracle rolls go through the same dice engine and the same audit log as everything else, tagged
`oracle`, so an ignored oracle result leaves evidence.

Once an oracle answer is established in play, **append it to `CANON.md`**. It is a fact now.

### The GM may consult it too

When the GM genuinely does not have a prepared answer, it should roll rather than invent — and
**say that it did**. "I rolled for it" is a better answer than an invented certainty, and it is
honest about where the fiction came from.

---

## The core move: a yes/no question with odds

The player states the question and how likely it feels. The tool rolls a d20. The answer is what
came up.

| Odds | Yes on | Yes-rate |
|---|---|---|
| Almost certain | 2+ | 95% |
| Very likely | 4+ | 85% |
| Likely | 6+ | 75% |
| Even | 11+ | 50% |
| Unlikely | 16+ | 25% |
| Very unlikely | 18+ | 15% |
| Almost impossible | 20+ | 5% |

The yes-rate is exactly `(21 − threshold) / 20`. Verify it against the dice at any time:

```
python3 tools/oracle.py calibrate -n 2000
```

which rolls each rung 2,000 times and reports whether the observed rate sits inside two standard
errors of the published one.

## The three refinements

### "And" / "but" results

| The roll | Result |
|---|---|
| Clears the threshold by **5 or more** | **yes, and** — the answer plus something in the player's favour |
| Clears it by **1 to 2** | **yes, but** — yes, with a complication attached |
| Clears it by 3 to 4 | a plain **yes** |
| Misses it by **1 to 2** | **no, but** — no, but something softens it |
| Misses it by 3 to 4 | a plain **no** |
| Misses it by **5 or more** | **no, and** — no, and it is worse than that |

The "no, and" rung is this framework's own symmetric completion of the published "yes, and"; the
rest is the standard shape.

### Random event trigger

**On a natural 1 or a natural 20**, something unrelated intrudes. Roll it on a table in
`16-random-tables.md` — `What Goes Wrong`, an encounter table for the terrain, or a meaning pair —
and fold it into the answer.

This is deliberately a flat 10% of all questions. Often enough to keep the fiction from
converging on what either of you expected; rare enough not to make every question a digression.

### Exceptional results

- A **natural 20 on a question that was already likely** (threshold 6 or
  lower) is an emphatic yes **with consequences** — it goes further than asked, and that costs
  something.
- A **natural 1 on an unlikely question** (threshold 16 or higher) is an
  emphatic no — the door is shut hard, and shut in a way that is worth narrating.

The tool prints both flags; it does not decide what they mean.

---

## Scene check

Before a scene opens, roll whether it plays out as expected.

```
python3 tools/oracle.py scene --expectation "the meeting goes ahead quietly" --campaign X
```

| d20 | Result |
|---|---|
| 1–2 | **Interrupted** — something else arrives first and the expected scene does not get to start |
| 3–7 | **Altered** — the scene happens, but one of its assumptions is wrong. Change a detail that matters |
| 8–20 | **As expected** — it opens the way you thought |

This ladder is **this framework's own design**, not a published PF2e or Mythic table, and is
stated here so it can be argued with. On an interruption, roll the intrusion on a table.

Use it when the GM has a scene planned and wants the world to get a vote. Do not use it on every
scene; a campaign where two scenes in ten are interrupted feels alive, and one where six are
feels random.

---

## Meaning tables

When a result needs interpretation and neither of you has a read on it, roll a pair and read it
together.

```
python3 tools/oracle.py meaning --pair action-theme
python3 tools/oracle.py meaning --pair descriptor-focus
```

- **action + theme** — for *what is happening*. `Dispute` + `Obligation`. Someone is contesting a
  duty.
- **descriptor + focus** — for *what a thing is like*. `Growing` + `A ledger`. A debt that is
  getting worse, written down somewhere.

The tables are `Oracle Actions`, `Oracle Themes`, `Oracle Descriptors` and `Oracle Focuses` in
`16-random-tables.md`, 100 entries each. They live in that file rather than in the tool so there
is one place to edit them.

**If a pair says nothing**, re-roll once and say you did. Two rolls that both say nothing means
the question was wrong, not the table.

---

## How many, how bad, how long

Bounded quantity rolls, so "a few guards" becomes a number.

```
python3 tools/oracle.py howmany --range 1-6 --label "guards at the gate"
python3 tools/oracle.py howmany --range 1-4 --label "rounds until the ritual completes"
python3 tools/oracle.py howmany --range 2-12 --label "days before the caravan returns"
```

Pick the range from the fiction before rolling, not after seeing the number. "A handful" is 1–6;
"a patrol" is 2–8; "a garrison" is 20–60. Writing the range down first is what makes this a roll
rather than a decision with dice on top.

---

## NPC reaction and attitude shifts

Only **where the rules do not already cover it.** A real Diplomacy check against a real Will DC
beats an oracle roll every time; this is for the moments where there is no check to make and the
GM has no prepared answer.

| d20 total | Reaction |
|---|---|
| 1–2 | hostile — they act against you now |
| 3–5 | unfriendly — they refuse and remember it |
| 6–9 | wary — they hedge, and want something first |
| 10–14 | indifferent — they will deal, on ordinary terms |
| 15–18 | friendly — they help, within reason |
| 19+ | helpful — they go out of their way, and say why |

`--mod` carries whatever the fiction justifies: a prior favour, a shared enemy, a visible weapon.
The result shifts the NPC's **disposition** in their roster entry, so it sticks.

---

## When not to use the oracle

- **When a rule already covers it.** Recall Knowledge, Perception, Diplomacy, Seek — roll the
  check. The oracle is for questions the rules have no check for.
- **When `CANON.md` already answers it.** Read the file.
- **When the player is really asking the GM to decide.** "Is there another way out?" asked as a
  genuine question deserves an oracle roll; asked as "please give me an out" deserves a
  conversation.
- **To relitigate an answer either of you disliked.** That is the thing the binding rule forbids.

---

## In the audit log

Every oracle roll lands in `logs/rolls.jsonl` tagged `oracle`, with the question, the odds, the
threshold, the natural die and the interpreted answer in its `extra` block. `analyze.py` reports
how many oracle questions were asked and how many came back yes.

That record is the enforcement mechanism for the binding rule: an oracle result the GM quietly
ignored is a line in the log that does not match what happened next.
