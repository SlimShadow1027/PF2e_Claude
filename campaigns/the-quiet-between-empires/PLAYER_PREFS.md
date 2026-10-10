# Player preferences — The Quiet Between Empires

What the player asked for. The GM honours this without argument, and the player can change
any line mid-game with one sentence (`meta: ...`).

## Content boundaries

These outrank everything else in this repository, including flags.

Asked plainly at intake, and the player's answer was **none**:

- **Lines** (never appears, at all): **none.**
- **Veils** (happens, off-screen, not described): **none.**
- **Check in before:** nothing named.

The player may add a line or a veil at any point with one sentence (`meta: ...`), and it
takes effect immediately and without discussion. "None at intake" is not a waiver.

### Tone of depiction — asked for, not merely permitted

Carried forward from this player's recorded request on *Third Beginnings*: *"an explicit
graphically violent/mature adventure story."* So:

- **Violence is described in detail.** Wounds, their effects and their aftermath land on the
  page. A critical hit reads like one. Death reads like one.
- **Mature subject matter is in scope** — cruelty, desperation, atrocity, moral rot, the cost
  of what the protagonist does. The campaign does not flinch and does not euphemise.
- **This is not a request for sexual content or sexual violence**, neither of which was asked
  for and neither of which appears.
- **It is separate from lethality.** This campaign sits at lethality 3 — death is on the table
  if the player pushes a bad situation. Graphic description and death frequency are different
  dials and they stay different. `dial it back` and `dial it up` move the description without
  touching the preset, and neither needs a justification.

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

Carried over from *Third Beginnings* at the player's agreement.

- **Length:** two or three paragraphs per beat
- **Prose vs. bullets:** prose for scenes, bullets for mechanics
- **Person:** second person
- **Tense:** present
- **Name the rules being applied:** when it matters
- **Offer tactical suggestions:** **a posture menu each turn** — aggressive, defensive, and
  task-focused (support the sidekick, advance a timed objective, retreat). Never the optimal line,
  never the decision. **This supersedes the "one option per turn" preference carried over from
  *Third Beginnings*,** which the player changed during the lever walkthrough.
- **Remind the player of available actions and feats:** **yes, actively** — reminders for features
  that have gone unused. The sheet is dual-class with free archetype and ancestry paragon, so
  forgotten abilities are the likeliest failure mode rather than an edge case.

## Session rhythm

Carried over from *Third Beginnings*.

- **Typical sitting:** an evening, open-ended
- **Target scene count:** 5-7 — a steering aid, corrected by experience, never a timer
- **Open with:** trailer (trailer / cold open)
- **Aim for a cliffhanger:** **only when it is earned** — never manufactured
- **Checkpoint aggressiveness:** as specified in system/05-checkpoint-protocol.md

The scene budget is a steering aid, never a timer. It never truncates a scene. See
`system/22-session-flow.md`.

## Between-session world prep

- **Off-screen turns:** **on**
- **Cadence:** between sessions
- **`world_pace`:** steady (glacial / slow / steady / brisk / runaway)
- **Cap per pass:** 3 clocks and factions

Pausing or deleting the off-screen turn costs nothing — the framework works identically
with it off. See `system/18-between-session-prep.md`.

## Relationship graph

- **Enabled:** **on** (`tools/graph.py`)

Worth the most in intrigue and faction play. This campaign is a faction sandbox, which is the
case it is for — the opposite of the dungeon-crawl reasoning that turned it off on
*Third Beginnings*.

## Difficulty check-ins

- **Offer an adjustment every:** 3 sessions, based on the pattern in
  `encounters/history.md` rather than on one bad night.
