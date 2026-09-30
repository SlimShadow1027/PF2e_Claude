---
description: Audit the roll log — fairness, and what the numbers say about play
---

```
python3 tools/analyze.py --campaign <slug>
```

Show the player the **fairness** section, and specifically the **public versus private** split —
that is the check that matters. If secret checks and enemy saves have drifted favourable or
unfavourable relative to public rolls, it shows up there and nowhere else.

Read the numbers with their sample sizes. A chi-square p-value of 0.03 on 400 faces is the sort of
thing a fair die produces about one time in twenty; the same p-value on 40,000 faces is not.

**If the numbers look off, say so plainly.** `analyze.py` flags it already; do not bury the flag
under a reassuring sentence. The whole point of the log is that neither of you has to take the
dice on faith.

Then the **play** section: success rates per character and per check with sample sizes, the
degree-of-success breakdown, which save is actually the weak one and by how much, damage rolled,
dying and recovery counts, Hero Point rerolls, and hit rate at each multiple-attack-penalty step —
the table that tends to show whether a third attack is worth taking.

Filtered views:

```
python3 tools/analyze.py --campaign <slug> --since session-7 --actor kaelen
python3 tools/analyze.py --campaign <slug> --fairness
python3 tools/analyze.py --campaign <slug> --one-line
```

The report is written to `campaigns/<slug>/logs/dice-audit.md`.
