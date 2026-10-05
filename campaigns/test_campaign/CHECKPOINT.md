# Test Campaign — current state

> Rendered from `state.json` by `tools/state.py render`. **Do not hand-edit this file.**
> If a number here disagrees with `state.json`, `state.json` wins and this gets re-rendered.

- Checkpoint: **001** mid-fight at the windlass well
- Rendered at: 2026-10-05T19:51:35Z
- Session: 1 (in progress)
- Party level 1, 0 XP
- Transparency mode: `standard` — difficulty preset: **Standard**
- Ruleset: **Dungeons & Dragons 2024 (5.5e)**

## Scene

- **Where:** Roderic's Cove — the salt-stair below the windlass
- **When:** 3 Gozran 4729 AR, 14:00

Mirren is on the salt-stair, counting windlass turns.

## Party

| Character | HP | AC | Init | Pass. Perc | Insp | Hit Dice | Exh | Conditions |
|---|---|---|---|---|---|---|---|---|
| Mirren Vale | 10/19 | 15 | +3 | 11 | — | 2/2d8 | — | grappled |

### Spell slots

- **Mirren Vale** — level 1: 3/3

## Money and carried items

- **Purse:** 12 gp, 4 sp
- **Mirren Vale** 2.3 lb of 150 lb capacity (Str 10, medium)
  - Mirren Vale: Shortbow

## Live encounter

```
Something in the windlass well — round 1, objective: cut the rope before the cage reaches the top

   combatant              init           HP act  bns  move    rxn  pos   conditions
   Mirren Vale              16        10/19 ◆    —    30/30ft yes  -     grappled
→  Grick                    11        27/27 ◆    —    30/30ft yes  -     

One action a turn, plus a Bonus Action only when something grants one, plus one Reaction, plus movement up to your Speed and one free object interaction. There is no multiple attack penalty: extra attacks come from the Attack action itself.
```

This encounter is mid-fight. Restoring this checkpoint restores the tracker exactly:
initiative order, current turn, actions spent, MAP step, reactions, HP, conditions and positions.

---

Deep history lives in `sessions/` and `CANON.md`, not here — this file stays cheap to reload.
