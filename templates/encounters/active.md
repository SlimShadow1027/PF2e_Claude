# Live encounter — {{CAMPAIGN_TITLE}}

**Transient.** Cleared after combat. The canonical tracker is in `state.json` under
`encounter`, which is what a mid-combat checkpoint restores; this file is the readable copy,
rewritten each round.

```
python3 tools/state.py --campaign {{CAMPAIGN_SLUG}} encounter status
```

- **Encounter:** —
- **Objective:** — _(every encounter has one, and it is telegraphed to the player in the
  fiction before or during round 1)_
- **Round:** —
- **Map:** —

| | Combatant | Init | HP | Actions | MAP | Reaction | Position | Conditions (with durations) |
|---|---|---|---|---|---|---|---|---|
| → | | | | ◆◆◆ | 0 | available | | |

Enemy HP shows as a number or as a wounded descriptor depending on the campaign's
transparency mode. In `standard` and `mystery` it is a descriptor.

## Reaction check

Before resolving **any** trigger — a creature moving out of reach or through a threatened
square, an incoming attack, a spell being cast within sight, a creature standing from prone —
check every party member's available reactions and **ask the player before resolving**.

| Character | Reaction | Available? |
|---|---|---|
| | | |

## This round's log

- _(one line per resolved action, so a context loss mid-round is recoverable)_
