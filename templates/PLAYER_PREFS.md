# Player preferences — {{CAMPAIGN_TITLE}}

What the player asked for. The GM honours this without argument, and the player can change
any line mid-game with one sentence (`meta: ...`).

## Content boundaries

These outrank everything else in this repository, including flags.

- **Lines** (never appears, at all): {{LINES}}
- **Veils** (happens, off-screen, not described): {{VEILS}}
- **Check in before:** {{CHECK_IN_BEFORE}}

## Transparency

- **Mode:** {{TRANSPARENCY}}
  - `glass` — everything shown, including enemy rolls, enemy AC and HP, and DCs.
  - `standard` — the player's rolls and DCs shown; enemy rolls shown as numbers but their
    AC and HP hidden; `secret`-trait checks hidden.
  - `mystery` — only narration for anything on the enemy side; the player's own rolls are
    still always shown.
- In every mode **every roll is logged in full** to `logs/rolls.jsonl`, so the player can
  read it afterward and confirm nothing was invented.

## Narration

- **Length:** {{NARRATION_LENGTH}}
- **Prose vs. bullets:** {{PROSE_VS_BULLETS}}
- **Person:** {{PERSON}}
- **Tense:** {{TENSE}}
- **Name the rules being applied:** {{NAME_RULES}}
- **Offer tactical suggestions:** {{TACTICAL_HINTS}}
- **Remind the player of available actions and feats:** {{REMIND_ACTIONS}}

## Session rhythm

- **Typical sitting:** {{SITTING_LENGTH}}
- **Target scene count:** {{SCENE_BUDGET}}
- **Open with:** {{SESSION_OPEN}} (trailer / cold open)
- **Aim for a cliffhanger:** {{CLIFFHANGER}}
- **Checkpoint aggressiveness:** {{CHECKPOINT_AGGRESSION}}

The scene budget is a steering aid, never a timer. It never truncates a scene. See
`system/22-session-flow.md`.

## Between-session world prep

- **Off-screen turns:** {{WORLDPREP_ENABLED}} (off by default)
- **Cadence:** {{WORLDPREP_CADENCE}}
- **`world_pace`:** {{WORLD_PACE}} (glacial / slow / steady / brisk / runaway)
- **Cap per pass:** {{WORLDPREP_CAP}} clocks and factions

Pausing or deleting the off-screen turn costs nothing — the framework works identically
with it off. See `system/18-between-session-prep.md`.

## Relationship graph

- **Enabled:** {{GRAPH_ENABLED}} (`tools/graph.py`)

Worth the most in intrigue and faction play; in a dungeon crawl with six named NPCs it is
noise.

## Difficulty check-ins

- **Offer an adjustment every:** {{DIFFICULTY_CHECKIN}} sessions, based on the pattern in
  `encounters/history.md` rather than on one bad night.
