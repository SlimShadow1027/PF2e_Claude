# Checkpoint 017 — the descent begins: into the upper workings

**Immutable.** Never edit a past checkpoint. Restore it with `python3 tools/state.py --campaign the-quiet-between-empires restore 017`.

- Taken: 2026-11-02T17:02:09Z
- In-world: 18 Arodus -1000 AR, 11:15
- Location: the upper workings of The Long Quiet, just inside the adit by the abandoned upper lift-head
- Session: 1
- Mid-combat: no

## Where we are

Session 1, scene 3. Shavi and Kelda have entered the abandoned upper workings through the adit by the upper lift-head, 11:15. Kelda reacted sharply to the crossed-tally chalk detail. Fresh goblin sign ahead. Awaiting the player's exploration activities.

## Immediate situation

- Who is present: Shavi Beifong, Kelda Vornshield
- What is about to happen: none

## Active conditions and effects

- none

## Clocks (what the world is doing off-screen)

- none

## Unresolved threads

- **Kelda's descent** (active) — Talk to Thrain Deepdelve (sister's house, lower terraces) or Dagmar Stonewell (main lift barricade), or go straight up into the abandoned upper workings to Kelda's survey shaft

## Next likely beats

Exploration activities, then the upper workings toward the survey shaft (about 120 ft below the lift-head). A goblin watch post sits on the route. Build it from Monster Core with a cited source, an objective, and severe threat.

## State snapshot

The canonical machine-readable state at this moment. `restore` reads this block.

<!-- STATE-SNAPSHOT-BEGIN -->
```json
{
  "schema_version": 2,
  "campaign": "the-quiet-between-empires",
  "title": "The Quiet Between Empires",
  "created_at": "2026-10-06T20:28:33Z",
  "updated_at": "2026-11-02T17:02:09Z",
  "transparency": "standard",
  "difficulty_preset": "Custom",
  "session_in_progress": true,
  "session_number": 1,
  "scene_count": 3,
  "checkpoint_counter": 17,
  "last_checkpoint": {
    "id": "017",
    "name": "the descent begins: into the upper workings",
    "at": "2026-11-02T17:02:09Z",
    "slug": "the-descent-begins-into-the-upper-workings"
  },
  "time": {
    "calendar": "golarion",
    "year": -1000,
    "month": 8,
    "day": 18,
    "minute_of_day": 675,
    "elapsed_minutes": 195
  },
  "location": "the upper workings of The Long Quiet, just inside the adit by the abandoned upper lift-head",
  "party": {
    "level": 1,
    "xp": 0,
    "gold": {
      "pp": 0,
      "gp": 2,
      "sp": 2,
      "cp": 7
    },
    "stash": []
  },
  "pcs": {
    "kelda-vornshield": {
      "name": "Kelda Vornshield",
      "kind": "sidekick",
      "level": -1,
      "hp": {
        "current": 13,
        "max": 13,
        "temp": 0
      },
      "ac": 13,
      "saves": {
        "fortitude": 3,
        "reflex": 5,
        "will": 9
      },
      "perception": 7,
      "speed": 20,
      "str_mod": 0,
      "hero_points": 0,
      "hero_points_max": 3,
      "focus": {
        "current": 0,
        "max": 0,
        "refocus_available": true
      },
      "spell_slots": {},
      "conditions": [],
      "dying": 0,
      "wounded": 0,
      "doomed": 0,
      "dying_max": 4,
      "persistent": [],
      "items": [],
      "sheet": "npcs/kelda-vornshield.md",
      "notes": ""
    },
    "shavi-beifong": {
      "name": "Shavi Beifong",
      "kind": "pc",
      "level": 1,
      "hp": {
        "current": 31,
        "max": 31,
        "temp": 0
      },
      "ac": 18,
      "saves": {
        "fortitude": 9,
        "reflex": 6,
        "will": 4
      },
      "perception": 6,
      "speed": 25,
      "str_mod": 4,
      "hero_points": 1,
      "hero_points_max": 3,
      "focus": {
        "current": 1,
        "max": 1,
        "refocus_available": true
      },
      "spell_slots": {},
      "conditions": [],
      "dying": 0,
      "wounded": 0,
      "doomed": 0,
      "dying_max": 4,
      "persistent": [],
      "items": [
        {
          "name": "Breastplate (worn)",
          "qty": 1,
          "bulk": "2",
          "kind": "permanent",
          "charges": null,
          "level": null
        },
        {
          "name": "Wooden shield",
          "qty": 1,
          "bulk": "1",
          "kind": "permanent",
          "charges": null,
          "level": null
        },
        {
          "name": "Adventurer's Pack",
          "qty": 1,
          "bulk": "1",
          "kind": "container",
          "charges": null,
          "level": null
        },
        {
          "name": "Hooded lantern",
          "qty": 1,
          "bulk": "L",
          "kind": "gear",
          "charges": null,
          "level": null
        },
        {
          "name": "Oil (pint)",
          "qty": 5,
          "bulk": "-",
          "kind": "consumable",
          "charges": null,
          "level": null
        },
        {
          "name": "Climbing kit",
          "qty": 1,
          "bulk": "1",
          "kind": "gear",
          "charges": null,
          "level": null
        },
        {
          "name": "Grappling hook",
          "qty": 1,
          "bulk": "L",
          "kind": "gear",
          "charges": null,
          "level": null
        },
        {
          "name": "Crowbar",
          "qty": 1,
          "bulk": "L",
          "kind": "gear",
          "charges": null,
          "level": null
        },
        {
          "name": "Signal whistle",
          "qty": 1,
          "bulk": "-",
          "kind": "gear",
          "charges": null,
          "level": null
        },
        {
          "name": "Caltrops",
          "qty": 1,
          "bulk": "L",
          "kind": "consumable",
          "charges": null,
          "level": null
        },
        {
          "name": "Healer's toolkit (bought by Kelda, lent to Shavi)",
          "qty": 1,
          "bulk": "1",
          "kind": "gear",
          "charges": null,
          "level": 0
        }
      ],
      "sheet": "characters/shavi-beifong.md",
      "notes": ""
    }
  },
  "clocks": {},
  "quests": {
    "Kelda's descent": {
      "status": "active",
      "lead": "Talk to Thrain Deepdelve (sister's house, lower terraces) or Dagmar Stonewell (main lift barricade), or go straight up into the abandoned upper workings to Kelda's survey shaft"
    }
  },
  "encounter": null,
  "notes": {
    "situation": "Session 1, scene 3. Shavi and Kelda have entered the abandoned upper workings through the adit by the upper lift-head, 11:15. Kelda reacted sharply to the crossed-tally chalk detail. Fresh goblin sign ahead. Awaiting the player's exploration activities.",
    "next_beats": "Exploration activities, then the upper workings toward the survey shaft (about 120 ft below the lift-head). A goblin watch post sits on the route. Build it from Monster Core with a cited source, an objective, and severe threat.",
    "present": "Shavi Beifong, Kelda Vornshield",
    "pending": "none"
  }
}
```
<!-- STATE-SNAPSHOT-END -->

