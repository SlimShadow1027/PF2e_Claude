# 05 — The checkpoint protocol

A checkpoint is the campaign's save point. It is a git commit, and it is restorable.

---

## When a checkpoint gets written

### Automatic triggers

- End of any combat encounter.
- Level-up.
- Entering or leaving a settlement.
- Any transaction over a threshold (default: 10% of the party's purse, or any permanent item).
- A major story beat or reveal.
- **Before anything that could kill a character.**
- End of an in-world day.
- End of session.
- Every ~45 minutes of real play.

### Manual

The player types `checkpoint`. That is the whole trigger; no confirmation is needed.

---

## What a checkpoint contains

Written to `campaigns/<slug>/checkpoints/NNN-<slug>.md` by
`python3 tools/state.py --campaign <slug> checkpoint "<message>"`:

1. **The full `state.json` at that moment**, embedded in a fenced JSON block between
   `<!-- STATE-SNAPSHOT-BEGIN -->` and `<!-- STATE-SNAPSHOT-END -->`. This is what `restore`
   reads.
2. A **3–6 sentence "where we are"** paragraph.
3. The **immediate situation** — location, who is present, what is about to happen.
4. **Active conditions and effects** with remaining durations.
5. **Unresolved threads.**
6. **What the world is doing off-screen** — clock positions.
7. A **"next likely beats"** note to pick up from.

Set the prose parts before or during the checkpoint:

```
python3 tools/state.py --campaign X note situation "Water at knee height on the crypt landing..."
python3 tools/state.py --campaign X note present "Kaelen, two ghouls, the corpse of the porter"
python3 tools/state.py --campaign X note pending "Ghoul A acts next; the water rises a foot at the top of round 4"
python3 tools/state.py --campaign X note next_beats "If Kaelen reaches the lever the water drains and..."
python3 tools/state.py --campaign X checkpoint "escaped the flooded crypt"
```

`checkpoint` also accepts `--situation` and `--next-beats` inline.

**Snapshots are immutable.** Never edit a past one. A mistake in a checkpoint is corrected by
taking a new one, not by rewriting an old one.

---

## Every checkpoint commits

`tools/state.py checkpoint` does the following, in order, so none of it can be forgotten:

1. Bumps the counter and records `last_checkpoint` in `state.json`.
2. Re-renders `CHECKPOINT.md`.
3. Writes the immutable snapshot.
4. Regenerates `dashboard.html`.
5. `git add -A campaigns/<slug>` and commits as `checkpoint NNN: <message>`.

The commit therefore includes `state.json`, the rendered `CHECKPOINT.md`, the snapshot, the
dashboard, **and the roll-log lines produced since the last checkpoint** — which is what makes
the audit trail tamper-evident rather than merely append-only.

**Keep the campaign's commits noisy and do not squash them.** The history is the point.

If git is unavailable, or the commit fails, the tool says so in its output. It never skips
silently. If the player is not ready to commit for some reason, say so and continue — but say
it.

---

## Restoring

```
python3 tools/state.py --campaign <slug> restore 007
```

This rewinds `state.json`, re-renders `CHECKPOINT.md`, regenerates the dashboard, and commits
the rewind as `restore: rewind to checkpoint 007`. Then **narrate from the snapshot's situation
paragraph** — not from memory of what happened after it.

Because each checkpoint is a commit, `git diff` between two of them answers "what actually
changed" precisely:

```
git log --oneline -- campaigns/<slug>
git diff <sha-a> <sha-b> -- campaigns/<slug>/state.json
```

If the snapshot files are ever inconsistent — a hand-edit, a partial write — fall back to git:

```
git log --oneline -- campaigns/<slug>/checkpoints/007-*.md
git restore --source <that-sha> -- campaigns/<slug>
```

`restore` says this in its own error message when the snapshot will not parse.

### Rewinding is a legitimate table move

The player can call it at any time. "Rewind to before I opened the door." "Rewind, I misread
the map." "Rewind, I want to try the other thing."

**Do not resist it.** Do not argue that the consequences were interesting, do not ask them to
confirm twice, and do not partially restore. Find the checkpoint that precedes the moment,
restore it, and pick up the narration from there. If no checkpoint is close enough, say which
is the nearest and what would be lost, and let the player choose.

`rewind` is in the player command vocabulary (`14-player-commands.md`) for exactly this reason.

---

## A checkpoint must survive being taken mid-combat

This is the failure mode that loses a session, so it is designed for rather than hoped about.

If a session ends — or a context window runs out — in round 3 of a fight, the following is
serialised into `state.json` under `encounter` and restored exactly:

| Restored | Where it lives |
|---|---|
| Initiative order | `encounter.combatants`, sorted; ties already resolved |
| Whose turn it is | `encounter.turn_index` |
| Round number | `encounter.round` |
| Actions spent and remaining | per combatant: `actions_spent`, `actions_remaining` |
| Multiple attack penalty so far | per combatant: `map_step` |
| Reactions used, and on what | per combatant: `reaction_available`, `reaction_used_for` |
| Every combatant's current HP | party members via `ref` into `pcs`; others in their own `hp` block |
| Conditions with durations | on the character (`pcs`) or on the combatant |
| Persistent damage and sustained spells | `persistent`, `sustained` |
| Positions on the map | per combatant: `position`, plus the grid in `maps/<slug>.md` |
| The objective, and whether it was telegraphed | `encounter.objective`, `encounter.telegraphed` |

Party combatants **point at** their `pcs` entry rather than holding a second copy of their HP.
Two copies of the number that decides a death is precisely the drift this framework exists to
prevent.

To resume: restore, then run `encounter status`, then say out loud whose turn it is, how many
actions they have left, and whether their reaction is available — before narrating anything.

```
python3 tools/state.py --campaign X restore 014
python3 tools/state.py --campaign X encounter status
```

Also rewrite `encounters/active.md` every round when a fight is going badly, so a context loss
mid-round is recoverable from the readable copy as well as the JSON.

---

## `CHECKPOINT.md` stays small

It is **rendered from `state.json`, never hand-edited**. If a number in it disagrees with
`state.json`, `state.json` wins and the file gets re-rendered:

```
python3 tools/state.py --campaign X render
```

`tools/validate.py` fails when the two disagree.

**Aim under ~400 lines.** It gets reloaded at the start of every session, so it needs to be
cheap. Deep history lives in `sessions/` and `CANON.md`, not here. `validate.py` warns when it
grows past that.
