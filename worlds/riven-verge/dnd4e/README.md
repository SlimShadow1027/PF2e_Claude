# Dungeons & Dragons 4th Edition campaigns in riven-verge

One file per campaign, holding the **thorough narrative history** of what happened in it.

This folder is read by D&D 4e campaigns only, which is what lets it be detailed in a
way the shared `HISTORY.md` cannot be. Here you may name the rules, the class, the spell,
the creature and the roll that turned a scene — a reader of this folder is playing the same
game, so none of it is noise to them.

## How this relates to the rest of the world

| File | Shape | Who reads it |
|---|---|---|
| `../CHRONICLE.md` | dated, structured, terse, one entry per event | every ruleset, date-gated |
| `../HISTORY.md` | prose, spans rather than dates, certainty stated, **no numbers** | every ruleset, date-gated |
| **this folder** | prose, thorough, system-flavoured, as long as it earns | **D&D 4e only** |
| `../LEGENDS.md` | how the above is told wrongly in-world | every ruleset |

So one event can appear in all four: a line in the chronicle, a paragraph in the history,
three pages here, and a distorted song in the legends.

## The rule that still applies

**Nothing live.** Current hit points, coins, inventory, conditions, positions, checkpoints
and roll logs stay in `campaigns/<slug>/` permanently, even here. What belongs here is the
*account* — what happened, what it cost, who changed — written after the fact.

`python3 tools/validate.py --world riven-verge` fails a file here that reads like live state.
