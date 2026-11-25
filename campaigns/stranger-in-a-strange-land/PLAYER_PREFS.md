# Player preferences — Stranger in a Strange Land

What the player asked for. The GM honours this without argument, and the player can change
any line mid-game with one sentence (`meta: ...`).

## Content boundaries

These outrank everything else in this repository, including flags.

Asked 2026-11-25.

- **Lines** (never appears, at all):
  - **Graphic sexual violence.** It is never described.
- **Veils** (happens, off-screen, not described):
  - **Sexual violence** may be used as a narrative fact; it is never described.
  - **Violence towards children** is kept minimal and never shown in detail.
- **Explicitly in bounds:**
  - **Sex and intimacy** are fine.
  - **Slavery** should be fairly prominent in the more evil nations, with one or two neutral
    or good places practising it under their own cultural justifications.
- **Check in before:** nothing named.

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

- **Length:** short. "Lightweight and quick story beats." About a paragraph per beat; short and
  fast in combat.
- **Prose vs. bullets:** prose for scenes, bullets for mechanics
- **Person:** second person
- **Tense:** present
- **Name the rules being applied:** when it matters
- **Offer tactical suggestions:** when asked
- **Remind the player of available actions and feats:** when they seem stuck
- **Enemy HP shown as:** descriptors
- **Play focus:** mostly combat, with roleplay secondary. Encounters come frequently, at
  least half of each session's scenes.

## Session rhythm

- **Typical sitting:** about two hours
- **Target scene count:** 3–4, at least half of them fights
- **Open with:** trailer (trailer / cold open)
- **Aim for a cliffhanger:** only when it is earned
- **Checkpoint aggressiveness:** as specified in system/05-checkpoint-protocol.md

The scene budget is a steering aid, never a timer. It never truncates a scene. See
`system/22-session-flow.md`.

## Between-session world prep

- **Off-screen turns:** on, so rivals and factions act while the player is away
- **Cadence:** between sessions
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
