# Checkpoint 002 — mid-fight, round 1 — the hobgoblin has swung

**Immutable.** Never edit a past checkpoint. Restore it with `python3 tools/state.py --campaign candle-road restore 002`.

- Taken: 2026-10-02T18:19:42Z
- In-world: 1 Month 1 1, 08:00
- Location: unset
- Session: 0
- Mid-combat: yes — The unlit mile, round 1

## Where we are

_(no situation paragraph recorded)_

## Immediate situation

- Who is present: _unrecorded_
- What is about to happen: _unrecorded_

## Encounter tracker at this moment

```
The unlit mile — round 1, objective: get the lantern lit before the escort reaches the bend

   combatant              init           HP act  bns  move    rxn  pos   conditions
   Thorne Ashby             15        28/28 ◆    —    10/30ft yes  -     
→  Hobgoblin Warrior        13        11/11 ◆    —    30/30ft yes  -     
   Goblin Warrior            9          7/7 ◆    —    30/30ft yes  -     

One action a turn, plus a Bonus Action only when something grants one, plus one Reaction, plus movement up to your Speed and one free object interaction. There is no multiple attack penalty: extra attacks come from the Attack action itself.
```

## Active conditions and effects

- none

## Clocks (what the world is doing off-screen)

- none

## Unresolved threads

- see QUESTS.md

## Next likely beats

_(unrecorded)_

## State snapshot

The canonical machine-readable state at this moment. `restore` reads this block.

<!-- STATE-SNAPSHOT-BEGIN -->
```json
{
  "schema_version": 3,
  "system": "dnd5e",
  "campaign": "candle-road",
  "title": "The Candle Road",
  "created_at": "2026-10-02T18:17:37Z",
  "updated_at": "2026-10-02T18:19:42Z",
  "transparency": "standard",
  "difficulty_preset": "Standard",
  "session_in_progress": false,
  "session_number": 0,
  "scene_count": 0,
  "checkpoint_counter": 2,
  "last_checkpoint": {
    "id": "002",
    "name": "mid-fight, round 1 — the hobgoblin has swung",
    "at": "2026-10-02T18:19:42Z",
    "slug": "mid-fight-round-1-the-hobgoblin-has-swung"
  },
  "time": {
    "calendar": "generic",
    "year": 1,
    "month": 1,
    "day": 1,
    "minute_of_day": 480,
    "elapsed_minutes": 0
  },
  "location": "unset",
  "party": {
    "level": 1,
    "xp": 0,
    "gold": {
      "pp": 0,
      "gp": 40,
      "ep": 8,
      "sp": 15,
      "cp": 0
    },
    "stash": []
  },
  "pcs": {
    "thorne-ashby": {
      "name": "Thorne Ashby",
      "kind": "pc",
      "level": 3,
      "hp": {
        "current": 28,
        "max": 28,
        "temp": 0
      },
      "conditions": [],
      "items": [
        {
          "name": "Chain Mail (worn)",
          "qty": 1,
          "weight": "55",
          "kind": "permanent",
          "charges": null,
          "level": null
        },
        {
          "name": "Potion of Healing",
          "qty": 2,
          "weight": "0.5",
          "kind": "consumable",
          "charges": null,
          "level": null
        }
      ],
      "sheet": "characters/thorne-ashby.md",
      "notes": "",
      "ac": 16,
      "abilities": {
        "str": 16,
        "dex": 14,
        "con": 14,
        "int": 10,
        "wis": 13,
        "cha": 8
      },
      "saves": {
        "str": 5,
        "dex": 0,
        "con": 4,
        "int": 0,
        "wis": 0,
        "cha": 0
      },
      "save_proficiencies": [],
      "skills": {},
      "proficiency_bonus": 2,
      "passive_perception": 11,
      "initiative_mod": 2,
      "speed": 30,
      "size": "Medium",
      "strength": 16,
      "hit_dice": {
        "die": 10,
        "max": 3,
        "used": 0
      },
      "death_saves": {
        "successes": 0,
        "failures": 0,
        "stable": false
      },
      "exhaustion": 0,
      "heroic_inspiration": false,
      "concentration": null,
      "spell_slots": {
        "1": {
          "max": 3,
          "used": 0
        }
      },
      "attunement": {
        "max": 3,
        "items": [
          "Cloak of Protection"
        ]
      }
    }
  },
  "clocks": {},
  "quests": {},
  "encounter": {
    "name": "The unlit mile",
    "objective": "get the lantern lit before the escort reaches the bend",
    "map": null,
    "round": 1,
    "turn_index": 1,
    "started_at": "2026-10-02T18:19:32Z",
    "combatants": [
      {
        "id": "thorne-ashby",
        "name": "Thorne Ashby",
        "side": "party",
        "ref": "thorne-ashby",
        "initiative": 15,
        "initiative_natural": null,
        "hp": null,
        "conditions": null,
        "position": null,
        "squad": null,
        "level": null,
        "cr": null,
        "notes": "",
        "defeated": false,
        "actions_remaining": 1,
        "actions_spent": 0,
        "bonus_action_max": 0,
        "bonus_action_remaining": 0,
        "speed": 30,
        "movement_used": 20,
        "object_interaction_used": false,
        "reaction_available": true,
        "reaction_used_for": null,
        "concentrating_on": null,
        "base_speed": 30,
        "death_saves": null
      },
      {
        "id": "hobgoblin-warrior",
        "name": "Hobgoblin Warrior",
        "side": "adversary",
        "ref": null,
        "initiative": 13,
        "initiative_natural": null,
        "hp": {
          "current": 11,
          "max": 11,
          "temp": 0
        },
        "conditions": [],
        "position": null,
        "squad": null,
        "level": null,
        "cr": "1/2",
        "notes": "",
        "defeated": false,
        "actions_remaining": 1,
        "actions_spent": 0,
        "bonus_action_max": 0,
        "bonus_action_remaining": 0,
        "speed": 30,
        "movement_used": 0,
        "object_interaction_used": false,
        "reaction_available": true,
        "reaction_used_for": null,
        "concentrating_on": null,
        "base_speed": 30,
        "death_saves": {
          "successes": 0,
          "failures": 0,
          "stable": false
        }
      },
      {
        "id": "goblin-warrior",
        "name": "Goblin Warrior",
        "side": "adversary",
        "ref": null,
        "initiative": 9,
        "initiative_natural": null,
        "hp": {
          "current": 7,
          "max": 7,
          "temp": 0
        },
        "conditions": [],
        "position": null,
        "squad": null,
        "level": null,
        "cr": "1/4",
        "notes": "",
        "defeated": false,
        "actions_remaining": 1,
        "actions_spent": 0,
        "bonus_action_max": 0,
        "bonus_action_remaining": 0,
        "speed": 30,
        "movement_used": 0,
        "object_interaction_used": false,
        "reaction_available": true,
        "reaction_used_for": null,
        "concentrating_on": null,
        "base_speed": 30,
        "death_saves": {
          "successes": 0,
          "failures": 0,
          "stable": false
        }
      }
    ],
    "log": [],
    "telegraphed": false
  },
  "notes": {
    "situation": "",
    "next_beats": ""
  }
}
```
<!-- STATE-SNAPSHOT-END -->

