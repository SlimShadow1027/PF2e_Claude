# 14 — The player command vocabulary

A small vocabulary the player can type at any time. **Honour these without argument** — no
confirmation, no defending the scene, no asking why. They are the player's controls, not
requests.

Most of them are shared between the two rulesets. The resource commands are not, because the
resources are not — `## Per-ruleset commands` at the bottom lists each game's own, and the tools
refuse the other game's and name the right one.

| The player types | The GM does |
|---|---|
| `checkpoint` | Write a checkpoint now. `state.py checkpoint "<a short name>"`, which commits and regenerates the dashboard. |
| `recap` | Summarise where we are, what is unresolved, and what the player was about to do. Fiction and mechanics kept separate — see `22-session-flow.md`. |
| `status` | HP, conditions with durations, resources, gold, current scene. Straight from `state.json`; no narration. |
| `sheet [name]` | Print that character's sheet. Built choices from `characters/<name>.md`, volatile numbers from `state.json`. |
| `inventory` | Full inventory with what each carrier is carrying against their limits — **Bulk** in Pathfinder, **pounds** in D&D — plus the purse. `state.py item list`. |
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

This is the command that makes a full character playable solo, and it is worth doing properly.
List, for the current moment:

- Each **action** available, with the roll it needs and the modifier.
- Whether the **reaction** is available, and what would trigger it.
- Any **condition** currently changing those numbers, and by how much.
- What is **not** available, and why.

What the costs are measured in depends on the ruleset, and getting this wrong is the fastest way
to make the command useless:

| | Pathfinder | D&D 2024 |
|---|---|---|
| Cost per option | in `◆` — one, two or three actions | the **action**, a **Bonus Action** only if a feature grants one, or free |
| Movement | costs an action (Stride) | its own allowance, in **feet**, quoted as feet remaining |
| Repeat attacks | name the **multiple attack penalty** on the second and third | **no penalty** — say how many attacks the Attack action gives |
| "Not available" reads like | "you cannot Stride to the lever, it is 30 feet and you have one action left" | "the lever is 40 feet and you have 30 left — Dash would cost your action" |

Do not pad it with everything the character could theoretically do. Five to eight real options
beats a complete list.

### `rules: <q>`

Answer out of character, **with the source** — and from **the campaign's ruleset**. The two games
share vocabulary and disagree underneath it, so check which one you are in before answering
(`python3 tools/rules.py which <slug>`). "Advantage", "critical hit", "a DC 20 check" and "level 5"
all mean different things.

| | Look in | Then in | Then |
|---|---|---|---|
| Pathfinder | `12-rules-quick-reference.md` | `python3 tools/pf2e.py sources` | `2e.aonprd.com` |
| D&D 2024 | `dnd5e/12-rules-quick-reference.md` | `python3 tools/dnd5e.py sources` | SRD 5.2 at `dndbeyond.com/srd` |

Where SRD 5.2 simply does not publish the answer — treasure by level, Earn Income, a calendar,
creature adjustment templates — **say that**, rather than reaching for the Pathfinder answer or
the 2014 one. "That is DMG material and not in the open content I have; here is what the SRD does
say, and here is a convention we could use" is the honest reply.

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
4. Narrate the stretch from the outcomes, letting the failures cost something concrete. In
   Pathfinder the degrees give you four shades to narrate from; in D&D there are two, so the
   *margin* and the fiction have to do that work instead.
5. Advance the clock once: `state.py advance-time "2 weeks"`.
6. Advance any ticking clock by its rate for that span — the world does not stop.
7. Checkpoint, and write a `TIMELINE.md` row.

### `meta: <text>`

Applies **going forward**. Nothing is retconned: a fight already won stays won, and a Hero Point
or a Heroic Inspiration already spent stays spent. Record it:

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

---

## Per-ruleset commands

Each game's own resources. The tools refuse the other game's command and name the right one, so a
mistyped command is a one-line correction rather than a wrong number written to state.

### Pathfinder

| The player types | The GM does |
|---|---|
| `hero point` | Spend one for a reroll (`roll.py fortune`, which keeps the higher of two real d20s) or to stabilise at dying. `state.py hero spend`. |
| `refocus` | Recover a Focus Point, once per spent focus spell. `state.py focus refocus`. |
| `recovery` | Roll the recovery check at dying N against DC 10 + N and apply it. `state.py recovery <who>`. |

### D&D 2024

| The player types | The GM does |
|---|---|
| `inspiration` | Spend Heroic Inspiration to reroll **any** die just rolled, and the new roll stands. `state.py inspiration spend`. Note it is not limited to a d20. |
| `short rest` | One hour. Offer Hit Dice, say plainly that **spell slots do not come back**, drop Concentration. `state.py short-rest`. |
| `long rest` | Eight hours. HP, Hit Dice and slots restored, one Exhaustion level removed, temporary HP ended. `state.py long-rest`. |
| `hit dice` | Spend Hit Dice on a Short Rest: a real roll plus the Constitution modifier per die, applied with `heal`. `state.py hit-dice spend`. |
| `death save` | Roll the Death Saving Throw and record it. `state.py death-save roll <who>`. |
| `concentration` | Start, drop, or check it after damage — `state.py concentration check <who> <damage>` prints the DC. |
| `attune` | Attune to or release a magic item, against the limit of three. `state.py attune add`. |

**Say the limit when it bites.** A player asking to attune a fourth item wants to know which of the
three they would have to give up, not that the command failed.
