# Player preferences — The Candle Road

What the player asked for. The GM honours this without argument, and the player can change
any line mid-game with one sentence (`meta: ...`).

## Content boundaries

These outrank everything else in this repository, including flags.

- **Lines** (never appears, at all): _Not asked yet. Ask plainly, once, during intake._
- **Veils** (happens, off-screen, not described): _Not asked yet._
- **Check in before:** _Not asked yet._

## Transparency

- **Mode:** standard
  - `glass` — everything shown, including enemy rolls, enemy AC and HP, and DCs.
  - `standard` — the player's rolls and DCs shown; enemy rolls shown as numbers but their
    AC and HP hidden; `secret`-trait checks hidden.
  - `mystery` — only narration for anything on the enemy side; the player's own rolls are
    still always shown.
- In every mode **every roll is logged in full** to `logs/rolls.jsonl`, so the player can
  read it afterward and confirm nothing was invented.

## Narration

- **Length:** not yet decided
- **Prose vs. bullets:** not yet decided
- **Person:** second person
- **Tense:** present
- **Name the rules being applied:** not yet decided
- **Offer tactical suggestions:** not yet decided
- **Remind the player of available actions and feats:** not yet decided

## Session rhythm

- **Typical sitting:** not yet decided
- **Target scene count:** not yet decided
- **Open with:** trailer (trailer / cold open)
- **Aim for a cliffhanger:** not yet decided
- **Checkpoint aggressiveness:** as specified in system/05-checkpoint-protocol.md

The scene budget is a steering aid, never a timer. It never truncates a scene. See
`system/22-session-flow.md`.

## Between-session world prep

- **Off-screen turns:** off (off by default)
- **Cadence:** —
- **`world_pace`:** steady (glacial / slow / steady / brisk / runaway)
- **Cap per pass:** 3 clocks and factions

Pausing or deleting the off-screen turn costs nothing — the framework works identically
with it off. See `system/18-between-session-prep.md`.

## Relationship graph

- **Enabled:** off (`tools/graph.py`)

Worth the most in intrigue and faction play; in a dungeon crawl with six named NPCs it is
noise.

## Difficulty check-ins

- **Offer an adjustment every:** 3 sessions, based on the pattern in
  `encounters/history.md` rather than on one bad night.
