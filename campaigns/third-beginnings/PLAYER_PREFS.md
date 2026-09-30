# Player preferences — Third Beginnings

What the player asked for. The GM honours this without argument, and the player can change
any line mid-game with one sentence (`meta: ...`).

## Content boundaries

These outrank everything else in this repository, including flags.

- **Lines** (never appears, at all): none stated.
- **Veils** (happens, off-screen, not described): **harm to children.** It may exist in the
  fiction and drive events; it is never depicted, described or played out on screen. The
  player's words: *"Off screen child harm."*
- **Check in before:** nothing named.

### Tone of depiction — asked for, not merely permitted

The player asked, in their own words, for *"an explicit graphically violent/mature adventure
story."* So:

- **Violence is described in detail.** Wounds, their effects and their aftermath land on the
  page. A critical hit reads like one. Death reads like one.
- **Mature subject matter is in scope** — cruelty, desperation, atrocity, moral rot, the
  cost of the things the protagonist does. The campaign does not flinch and does not
  euphemise.
- **This does not override the veil above**, and it is not a request for sexual content or
  sexual violence, neither of which was asked for and neither of which appears.
- **It does not change the lethality setting.** Lethality 2 still stands: death is
  telegraphed hard and always avoidable. Graphic is a matter of *description*, not of
  *how often the player dies*. Those are separate dials and they stay separate.

The player can move this with `dial it back` or `dial it up` at any point, and neither
needs a justification.

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

- **Length:** two or three paragraphs per beat
- **Prose vs. bullets:** prose for scenes, bullets for mechanics
- **Person:** second person
- **Tense:** present
- **Name the rules being applied:** when it matters
- **Offer tactical suggestions:** **one option per turn** — a single thing worth considering,
  never a full solve and never the decision
- **Remind the player of available actions and feats:** folded into the one option per turn;
  a full list on request or when the player is visibly stuck

## Session rhythm

- **Typical sitting:** an evening, open-ended
- **Target scene count:** 5-7 — a steering aid, corrected by experience, never a timer
- **Open with:** trailer (trailer / cold open)
- **Aim for a cliffhanger:** **only when it is earned** — never manufactured
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
