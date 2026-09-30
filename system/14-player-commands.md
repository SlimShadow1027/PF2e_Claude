# 14 — The player command vocabulary

A small vocabulary the player can type at any time. **Honour these without argument** — no
confirmation, no defending the scene, no asking why. They are the player's controls, not
requests.

| The player types | The GM does |
|---|---|
| `checkpoint` | Write a checkpoint now. `state.py checkpoint "<a short name>"`, which commits and regenerates the dashboard. |
| `recap` | Summarise where we are, what is unresolved, and what the player was about to do. Fiction and mechanics kept separate — see `22-session-flow.md`. |
| `status` | HP, conditions with durations, resources, gold, current scene. Straight from `state.json`; no narration. |
| `sheet [name]` | Print that character's sheet. Built choices from `characters/<name>.md`, volatile numbers from `state.json`. |
| `inventory` | Full inventory with Bulk against the limits, per carrier, plus the purse. `state.py item list`. |
| `rewind [to …]` | Undo back to that point; restore a checkpoint if one is needed. **Do not resist it.** See `05-checkpoint-protocol.md`. |
| `rules: <q>` | Answer as a rules question, out of character, **with the source**. If the source cannot be checked, say the value is unverified. |
| `ooc: <text>` | Out-of-character conversation. No in-fiction response at all. |
| `meta: <text>` | Adjust difficulty, tone, pacing or verbosity mid-game. Applies going forward, no retcon; record it in `RULES_DELTAS.md` or `PLAYER_PREFS.md` with a change-log row. |
| `options` | List the player's legal actions right now, with the relevant modifiers, and what each would cost in actions. |
| `map` | Show or refresh the tactical or area map from `maps/`. |
| `who is <name>` | NPC recall from `npcs/ROSTER.md` — role, faction, disposition, status, last seen. Player-known facts only. |
| `what do I know about <thing>` | Offer the relevant Recall Knowledge check, **or** recall what `CANON.md` already establishes. Say which of the two is happening. |
| `montage <goal>` | Resolve a stretch of time in summary with a few real rolls. See below. |
| `dashboard` | Regenerate and point at `dashboard.html`. |
| `worldprep` | Run an off-screen turn now and show the world pulse. See `18-between-session-prep.md`. |
| `oracle <question>` | Consult the oracle. **The result is binding on the GM.** See `19-solo-oracle.md`. |
| `flags` | Show the flags with their status, and let the player add, change or retire one. |
| `dice audit` | Run `tools/analyze.py` and show the fairness and play summary. |
| `end session` | Write the session log, checkpoint, and give a "next time on…" teaser. See `22-session-flow.md`. |

Also honoured, from `13-table-etiquette-and-safety.md`: `pause`, `fade` / `cut`,
`dial it back`, `dial it up`.

---

## Notes on the ones that are easy to do badly

### `status`

Read it out of `state.json`, not out of memory of the last few exchanges. If the numbers in
`CHECKPOINT.md` and `state.json` ever disagree, `state.json` wins — re-render and say you did.

```
python3 tools/state.py --campaign X render
```

### `options`

This is the command that makes a full PF2e character playable solo, and it is worth doing
properly. List, for the current moment:

- Each **action** available, with its cost in `◆`, the roll it needs, and the modifier.
- The **multiple attack penalty** that would apply to a second and third attack, from the
  tracker.
- Whether the **reaction** is available, and what would trigger it.
- Any **condition** currently changing those numbers, and by how much.
- What is **not** available, and why — "you cannot Stride to the lever, it is 30 feet and you
  have one action left".

Do not pad it with everything the character could theoretically do. Five to eight real options
beats a complete list.

### `rules: <q>`

Answer out of character, **with the source**. Prefer `12-rules-quick-reference.md`, then
`python3 tools/pf2e.py sources`, then look it up on `2e.aonprd.com`.

If the answer cannot be sourced, say so in those words: "I believe it is X, but I cannot verify
it from here — treat it as unverified." Then use X and move on. A stalled rules question is
worse than a flagged one.

Never answer a rules question with a number and no provenance. That habit is what
`00-gm-charter.md` constraint 5 exists to prevent.

### `montage <goal>`

A stretch of time resolved in summary, with **real rolls** — a montage is not an excuse to skip
the dice.

1. Ask what the goal is and roughly how long the player is giving it.
2. Pick **two to four** checks that would actually decide it, and say what each is for.
3. Roll them for real, in one batch.
4. Narrate the stretch from the degrees of success, letting the failures cost something concrete.
5. Advance the clock once: `state.py advance-time "2 weeks"`.
6. Advance any ticking clock by its rate for that span — the world does not stop.
7. Checkpoint, and write a `TIMELINE.md` row.

### `meta: <text>`

Applies **going forward**. Nothing is retconned: a fight already won stays won, a Hero Point
already spent stays spent. Record it:

- A difficulty or rules change → `RULES_DELTAS.md`, with a change-log row and
  `state.py preset <name>`.
- A tone, pacing or verbosity change → `PLAYER_PREFS.md`.

Then say in one line what will feel different.

### `rewind`

Find the checkpoint that precedes the moment, restore it, and narrate from its situation
paragraph. If no checkpoint is close enough, say which is nearest and what would be lost, and
let the player choose. Do not partially restore, and do not argue that the consequences were
interesting.

```
python3 tools/state.py --campaign X checkpoints
python3 tools/state.py --campaign X restore 013
```

### `what do I know about <thing>`

Two different things wear this name, and the GM should say which:

- **Recall Knowledge** — a `secret` check against a level-based DC adjusted for rarity. Roll it,
  withhold the number, narrate what the degree of success gives.
- **Established fact** — it is already in `CANON.md` or the roster, and the player has heard it.
  Just say it; no roll.

If it is in `CANON.md` as **GM-side truth**, the player has not heard it: offer the Recall
Knowledge check instead, and do not leak the entry.

---

## The slash commands

`.claude/commands/` holds one-keystroke versions of the ones worth having as a shortcut:

`/checkpoint` · `/recap` · `/status` · `/sheet` · `/levelup` · `/encounter` · `/dashboard` ·
`/dice-audit` · `/worldprep` · `/oracle` · `/endsession` · `/newcampaign` · `/resume`

Each is a short Markdown file naming which system document to follow.
