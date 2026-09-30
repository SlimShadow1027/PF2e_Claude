---
description: Ask the oracle a question — the answer is binding
argument-hint: [question] [--odds unlikely]
---

Consult the oracle, following `system/19-solo-oracle.md`.

```
python3 tools/oracle.py ask "$ARGUMENTS" --odds even --campaign <slug>
```

Pick the odds from the fiction **before** rolling, and say which rung you picked and why:
`almost-certain` (2+) · `very-likely` (4+) · `likely` (6+) · `even` (11+) · `unlikely` (16+) ·
`very-unlikely` (18+) · `almost-impossible` (20).

**The result is binding on you.** Take it as established fact and build forward from it, including
when it wrecks what you had planned. Do not reroll it, do not reinterpret it toward your prep, and
do not quietly route around it.

The one legitimate override: **if the answer contradicts something already in `CANON.md`, say so
and re-ask a better question.** "That does not fit what I had in mind" is not that case.

Handle the refinements the tool prints:

- **"yes, and" / "no, and"** — the answer plus something further, in that direction.
- **"yes, but" / "no, but"** — the answer with something cutting against it.
- **Random event** on a natural 1 or 20 — roll the intrusion on a table in
  `system/16-random-tables.md` and fold it in.
- **Exceptional result** — narrate the emphasis, and the cost.

Once the answer is established in play, **append it to `CANON.md`.** It is a fact now.

Other moves:

```
python3 tools/oracle.py scene --expectation "..." --campaign <slug>
python3 tools/oracle.py meaning --pair action-theme --campaign <slug>
python3 tools/oracle.py howmany --range 1-6 --label "..." --campaign <slug>
python3 tools/oracle.py reaction --who "..." --mod 0 --campaign <slug>
```

You may consult it yourself when you genuinely do not have a prepared answer — and **say that you
did.** "I rolled for it" is a better answer than an invented certainty.
