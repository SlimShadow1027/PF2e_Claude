---
description: Create a new campaign and run the intake interview
argument-hint: [campaign title]
---

Create a new campaign. Three steps, and the last is the long one.

**1. Ask which game**, before anything else — this is Block 0 of intake and everything after it
depends on the answer:

> Pathfinder Second Edition (Remaster), or Dungeons & Dragons 2024 ("5.5e")?

If they have no preference, two questions usually settle it: *"spend time building the character,
or start playing in five minutes?"* and *"do you want the dice to tell you how well, or just
whether?"* `system/01-campaign-intake.md` Block 0 has the longer version, including the one
mechanical difference worth mentioning up front at a table of one character.

**2. Scaffold the folder** so there is somewhere to write answers as they arrive:

```
python3 tools/new_campaign.py "$ARGUMENTS" --system <pf2e|dnd5e>
```

`--system` is **required**. Nothing defaults, because a campaign scaffolded under the wrong
ruleset carries the wrong calendar, the wrong character sheet and the wrong rules documents from
its first file.

Every `{{PLACEHOLDER}}` is filled with a neutral "not yet decided" default and the tool proves it
by scanning the result. Those defaults exist so the scaffold is valid, not so it is finished.

**3. Run the intake interview** from `system/01-campaign-intake.md`.

**A few questions at a time, not all at once.** Three to five concrete example answers for each, so
the player can pick rather than compose. Offer "surprise me" and "roll it" on every question — and
"roll it" means a real roll:

```
python3 tools/roll.py table system/16-random-tables.md "<table>" --campaign <slug>
```

Twelve blocks: **which game** · shape and length · genre and tone · setting · the shared world ·
premise and stakes · protagonist framing · party structure · **content boundaries** · **flags** ·
play preferences · session rhythm.

For a D&D campaign, the setting block also has to settle the **calendar**: SRD 5.2 publishes none,
so either name the setting's, define one in the world's `CALENDAR.md`, or keep the placeholder
knowingly.

Ask the boundaries question plainly, once, and do not skip it. Lines and veils outrank everything
else in this repository, including the premise.

**Do not generate a world, an NPC, a map or a stat block during intake.**

Intake ends by writing `CAMPAIGN.md` (including `System:`), `RULES_DELTAS.md` (**delete the
other ruleset's variant menu**), `PLAYER_PREFS.md`, `FLAGS.md` and the region-and-base part of
`WORLD.md`, then:

```
python3 tools/validate.py --campaign <slug>
python3 tools/state.py --campaign <slug> checkpoint "intake complete"
```

…and then **three one-page pitches, and a stop.** Say which of the player's flags each pitch aims
at. **Do not build the world until they approve one.** If they like parts of two, merge and
re-offer rather than proceeding on a guess.
