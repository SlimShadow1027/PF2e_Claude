---
description: Create a new campaign and run the intake interview
argument-hint: [campaign title]
---

Create a new campaign. Two steps, and the second is the long one.

**1. Scaffold the folder** so there is somewhere to write answers as they arrive:

```
python3 tools/new_campaign.py "$ARGUMENTS"
```

Every `{{PLACEHOLDER}}` is filled with a neutral "not yet decided" default and the tool proves it
by scanning the result. Those defaults exist so the scaffold is valid, not so it is finished.

**2. Run the intake interview** from `system/01-campaign-intake.md`.

**A few questions at a time, not all at once.** Three to five concrete example answers for each, so
the player can pick rather than compose. Offer "surprise me" and "roll it" on every question — and
"roll it" means a real roll:

```
python3 tools/roll.py table system/16-random-tables.md "<table>" --campaign <slug>
```

Eleven blocks: shape and length · genre and tone · setting · the shared world · premise and stakes ·
protagonist framing · party structure · **content boundaries** · **flags** · play preferences ·
session rhythm.

Ask the boundaries question plainly, once, and do not skip it. Lines and veils outrank everything
else in this repository, including the premise.

**Do not generate a world, an NPC, a map or a stat block during intake.**

Intake ends by writing `CAMPAIGN.md`, `RULES_DELTAS.md`, `PLAYER_PREFS.md`, `FLAGS.md` and the
region-and-base part of `WORLD.md`, then:

```
python3 tools/validate.py --campaign <slug>
python3 tools/state.py --campaign <slug> checkpoint "intake complete"
```

…and then **three one-page pitches, and a stop.** Say which of the player's flags each pitch aims
at. **Do not build the world until they approve one.** If they like parts of two, merge and
re-offer rather than proceeding on a guess.
