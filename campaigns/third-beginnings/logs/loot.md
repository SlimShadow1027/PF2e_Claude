# Loot and economy — Third Beginnings

The coin total and item list are canonical in `state.json`. This file is the **ledger** —
what arrived, when, and from where — and the **treasure-pacing tracker**.

## Treasure pacing

Compare what has actually been awarded against the expected curve, so the party neither
outpaces nor falls behind the math:

```
python3 tools/pf2e.py treasure --level <party level> --party-size <N>
```

⚠ The treasure-by-level table in `tools/pf2e.py` is marked **UNVERIFIED** — check it against
GM Core before using it to make a pacing decision.

| Level | Expected total (gp) | Awarded so far (gp) | Difference | Verdict |
|---|---|---|---|---|
| 1 | | 0 | | on pace |

## Ledger

| In-world date | What | Value (gp) | Kind | Where it came from |
|---|---|---|---|---|
| | | | permanent / consumable / currency | |

## Spending

| In-world date | What | Cost | Bought where |
|---|---|---|---|
| | | | |

## Item levels available

| Settlement | Item level | Notes |
|---|---|---|
| | | |

## Crafting and Earn Income

`python3 tools/pf2e.py tables earn-income` — verified against the published table.

| In-world date | Who | Activity | Days | Task level | Result | Earned |
|---|---|---|---|---|---|---|
| | | | | | | |
