# Dice audit — test_campaign

Generated 2026-10-05T19:51:29Z from `/home/user/PF2e_Claude/campaigns/test_campaign/logs/rolls.jsonl`.

1 roll(s) in scope.

## Fairness

Does the framework actually roll straight? Every number below carries its sample size and, where it applies, its standard error, so you can tell noise from a pattern yourself.

**All d20 rolls** — 1 d20 face(s)

- Mean **2.0000** against an expected 10.5. Standard error 5.7663, so the gap is -8.5000 — that is 1.47 standard errors.
- Chi-square against a uniform d20: **19.00** on 19 degrees of freedom, p = **0.4568**.
- Natural 20s: 0 against an expected 0.1 (0.00% vs 5.00%, s.e. 21.79%).
- Natural 1s: 0 against an expected 0.1 (0.00% vs 5.00%, s.e. 21.79%).
- Longest run of 11 or more: 0; of 10 or less: 1.

Face distribution:

```
 1       0     -0.1 
 2       1     +0.9 ########################################
 3       0     -0.1 
 4       0     -0.1 
 5       0     -0.1 
 6       0     -0.1 
 7       0     -0.1 
 8       0     -0.1 
 9       0     -0.1 
10       0     -0.1 
11       0     -0.1 
12       0     -0.1 
13       0     -0.1 
14       0     -0.1 
15       0     -0.1 
16       0     -0.1 
17       0     -0.1 
18       0     -0.1 
19       0     -0.1 
20       0     -0.1 
```

### Public versus private

This is the check that matters. A GM that quietly tilts secret checks and enemy saves would show up here and nowhere else, so the two subsets are reported side by side.

**Public rolls (shown to the player)** — no d20 faces in this subset.
**Private and secret rolls (number withheld)** — 1 d20 face(s)

- Mean **2.0000** against an expected 10.5. Standard error 5.7663, so the gap is -8.5000 — that is 1.47 standard errors.
- Chi-square against a uniform d20: **19.00** on 19 degrees of freedom, p = **0.4568**.
- Natural 20s: 0 against an expected 0.1 (0.00% vs 5.00%, s.e. 21.79%).
- Natural 1s: 0 against an expected 0.1 (0.00% vs 5.00%, s.e. 21.79%).
- Longest run of 11 or more: 0; of 10 or less: 1.

Face distribution:

```
 1       0     -0.1 
 2       1     +0.9 ########################################
 3       0     -0.1 
 4       0     -0.1 
 5       0     -0.1 
 6       0     -0.1 
 7       0     -0.1 
 8       0     -0.1 
 9       0     -0.1 
10       0     -0.1 
11       0     -0.1 
12       0     -0.1 
13       0     -0.1 
14       0     -0.1 
15       0     -0.1 
16       0     -0.1 
17       0     -0.1 
18       0     -0.1 
19       0     -0.1 
20       0     -0.1 
```

### What that adds up to

- · Nothing in the fairness numbers looks off. Sample sizes are printed above so you can judge that for yourself rather than take it on faith.

## Play

What the numbers say about the campaign.

### Heroic Inspiration

- No such rerolls in the log yet. Heroic Inspiration *spends* are recorded in `state.json` and the checkpoint commits; only rerolls leave a die behind.
- Note that Heroic Inspiration rerolls **any** die and the new roll stands, so a spend may show as an ordinary reroll rather than as two kept dice.

## Rolls by kind

| Kind | n |
|---|---|
| attack | 1 |

---

Regenerate with `python3 tools/analyze.py --campaign test_campaign`.
