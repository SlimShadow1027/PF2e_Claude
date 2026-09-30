# 10 — Downtime, travel and rest

---

## Exploration activities

Out of combat, moving through the world, each character has **one exploration activity** at a
time. Changing it takes no action; it is simply what they are doing.

| Activity | Speed | What it does |
|---|---|---|
| Search | half | you get a Perception check against anything you pass; without it, hidden things stay hidden |
| Detect Magic | maximum ~300 ft/min | repeatedly cast detect magic as you go |
| Avoid Notice | half | Stealth instead of a normal approach; sets up an ambush or avoids one |
| Scout | half | +1 circumstance bonus to the party's initiative |
| Defend | half | you have your shield raised when combat starts |
| Track | half | follow a trail with Survival |
| Cover Tracks | half | hide the party's own trail |
| Investigate | half | Recall Knowledge as you go |
| Repeat a Spell | half | keep a spell active as you travel |
| Hustle | full ×2 | double speed, for a number of minutes equal to your Constitution modifier × 10 |

**The important one for solo play:** a single character can only do one of these. Choosing
Search means not Avoiding Notice, which means being seen. That is a real decision and it should
be presented as one, not defaulted.

⚠ The activity list and their speed effects are `⚠ UNVERIFIED` against a source reachable from
this machine, except the half-speed rule and the 8-hour travel day, which are verified — see
`python3 tools/pf2e.py sources` (`travel_speed`).

---

## Travel speed

| Speed | Feet per minute | Miles per hour | Miles per day (8 hours) |
|---|---|---|---|
| 10 ft | 100 | 1.0 | 8 |
| 15 ft | 150 | 1.5 | 12 |
| 20 ft | 200 | 2.0 | 16 |
| 25 ft | 250 | 2.5 | 20 |
| 30 ft | 300 | 3.0 | 24 |
| 35 ft | 350 | 3.5 | 28 |
| 40 ft | 400 | 4.0 | 32 |

⚠ **PARTLY UNVERIFIED —** GM Core, Travel Speed. The 8-hour travel day is verified against foundryvtt/pf2e v8.5.1 @06b904d6ced9795c4c07af085e6f61a56f845c60 (ORC implementation citing Archives of Nethys inline), src/scripts/macros/travel/travel-speed.ts (`hoursPerDay = 8`), and feet per minute is Speed x 10. The miles-per-hour and miles-per-day columns are UNVERIFIED: they are derived from Speed / 10 miles per hour x 8 hours, which reproduces the familiar published rows, but the published table itself could not be checked from this machine.

Terrain multipliers, applied to the day's distance:

| Terrain | Effect |
|---|---|
| Road, open plain | full speed |
| Difficult terrain (forest, rubble, deep snow) | half speed |
| Greater difficult terrain (swamp, thick ice, a cliff face) | one third speed |
| Hot or cold climate without protection | fewer travel hours per day |

⚠ `⚠ UNVERIFIED`.

Advance the clock through the tool, so the in-world date cannot drift from the narration:

```
python3 tools/state.py --campaign X advance-time "3 days"
python3 tools/pf2e.py time --advance "3 days 4 hours"
```

`advance-time` also expires minute-, hour- and day-length condition durations as the time
passes, and reports which ones ended.

---

## The encounter-check cadence

Rolling for a random encounter every hour of a ten-day journey is a hundred rolls and no story.
Use a cadence that produces a handful of decisions:

- **Once per travel day**, plus once per night watch, in ordinary territory.
- **Twice per day** in hostile territory or during a pursuit.
- **Once per leg** for a long, uneventful journey the player has said they want to skip —
  and say that is what you are doing.

Roll it for real, on a table in `16-random-tables.md`:

```
python3 tools/roll.py table system/16-random-tables.md "Wilderness Encounters (by tier)" --campaign X
```

A rolled encounter does not have to be a fight. About half should be a complication, a sign, or
a person.

---

## Weather

Roll it, by climate and season, on the tables in `16-random-tables.md`. Weather earns its place
when it changes a decision — a storm that closes a pass, a heat that halves the travel day, a
fog that makes the ambush possible. Weather that is only scenery can be narrated without a roll.

---

## Making camp, watches, and the night

### Making camp

One hour, and it wants a decision or two: where, how hidden, and who is awake.

- **Concealment** — a Stealth check to make the camp hard to find, or a good site chosen with
  Survival.
- **A fire** — warmth and cooked food against being visible for miles.
- **Subsistence** — a Survival check to feed the party off the land instead of off rations.

### Watches

A full night is 8 hours. Anyone on watch is not resting, and a character who spends the whole
night on watch does not get the benefits of a night's rest.

For one character alone, this is a genuine problem with no clean answer, and it should be named
rather than glossed: sleeping unwatched in hostile territory is a risk, and staying awake costs
the rest. An animal companion, a familiar, an alarm spell, or a hired watch are the usual
answers.

### Resting

A full night's rest requires **8 hours** of rest, of which at least 6 must be sleep, without
being interrupted by combat. It restores:

- **Hit points** equal to Constitution modifier × level (minimum 1 × level).
- **All spell slots** and **all Focus Points**.
- **Reduces drained and doomed by 1** each.
- **Removes fatigued**, given a full and uninterrupted night.

```
python3 tools/state.py --campaign X daily-prep
```

restores slots and focus, steps drained and doomed down by 1, and reports what changed. It does
**not** restore the hit points drained took away — that is correct, and the tool says so.

⚠ The hit-points-per-night formula is `⚠ UNVERIFIED` against a reachable source. The
drained/doomed/wounded step-downs are verified from the condition text in
`12-rules-quick-reference.md`.

### Daily preparations

Half an hour after waking: prepare spells, invest worn items (up to 10), ready the kit. This is
the moment to ask the player what they are preparing *for*, which is a better question than
what they are preparing.

---

## Healing

### Treat Wounds

The workhorse. Medicine, once per hour per patient, out of combat, 10 minutes.

| DC | Healing on a success | Critical success |
|---|---|---|
| 15 (trained) | 2d8 | 4d8 |
| 20 (expert) | 2d8 + 10 | 4d8 + 10 |
| 30 (master) | 2d8 + 30 | 4d8 + 30 |
| 40 (legendary) | 2d8 + 50 | 4d8 + 50 |

A **critical failure** deals 1d8 damage. A success also **removes the wounded condition**.

You may attempt a DC higher than your proficiency allows for the larger healing, at the risk of
the critical failure.

```
python3 tools/roll.py check "1d20+9" --dc 15 --label "Treat Wounds (DC 15)" --actor Kaelen --campaign X
python3 tools/roll.py damage "2d8" --label "Treat Wounds healing" --campaign X
python3 tools/state.py --campaign X heal kaelen 11
```

**Source:** the healing dice and the bonus-by-rank figures are verified against the Foundry VTT
PF2e implementation (`src/module/system/action-macros/medicine/`), which gives 2d8 on a success,
4d8 on a critical, and +0 / +0 / +10 / +30 / +50 by proficiency rank. The DCs come from the
verified simple-DC table, with master at 30 and legendary at 40.

⚠ The once-per-hour-per-patient limit and the 10-minute duration are `⚠ UNVERIFIED` here.

For a solo character this is the main attrition lever. The `Story` and some `Standard` presets
in `03-difficulty-and-solo-levers.md` grant a free one between encounters precisely because
there is nobody else to cast a heal.

### Administer First Aid

Two actions, Medicine, in combat. **Stabilise** a dying creature (DC 15 + their dying value) or
**stop bleeding** (DC 15, or the persistent damage's DC).

For one character this is the one they cannot use on themselves while unconscious, which is what
makes the death spiral in `03-difficulty-and-solo-levers.md` a structural problem rather than a
bad-luck problem.

### Refocus

Ten minutes of the activity your class specifies, recovering **1 Focus Point**. Once between
uses of a focus spell unless a specific ability says otherwise.

```
python3 tools/state.py --campaign X focus refocus kaelen
```

The tool refuses a second Refocus before a focus spell has been spent, and refuses to overfill
the pool.

---

## Downtime

### Per day

Each downtime day, each character does one thing. Resolve it with one roll and one sentence:

| Activity | Roll | Result |
|---|---|---|
| Earn Income | the relevant skill vs. the task's level DC | the day's income (verified table) |
| Craft | Crafting vs. the item's level DC | progress toward the item |
| Retrain | — | one feat, skill or class choice per week or so |
| Treat Wounds | Medicine | healing between days |
| Long-term rest | — | full recovery, faster than adventuring rest |
| Subsist | Survival | keeps you fed, or does not |
| Gather information | Diplomacy or Society | what the town knows |
| Practice a skill | — | narrative competence, not a mechanical bonus |

### Per week — so weeks pass in a few exchanges

For a stretch of downtime longer than a few days, do not roll per day. Instead:

1. **Ask what each character is doing with the stretch**, in one sentence each.
2. **Roll once per week per character**, against the relevant DC, and read the degree of success
   as the week's outcome:
   - **Critical success** — the goal is met early, plus one useful extra (a contact, a discount,
     a rumour worth acting on).
   - **Success** — the goal is met.
   - **Failure** — partial progress, and a cost: time, money, or a complication.
   - **Critical failure** — no progress, and the complication arrives with a name attached.
3. **Advance the clock once**, for the whole stretch:
   `python3 tools/state.py --campaign X advance-time "3 weeks"`
4. **Advance any ticking clock** by its stated rate for that many weeks — the world does not
   stop because the player is crafting.
5. **Roll for one interruption** across the whole stretch. A month of downtime with nothing
   happening is a month the player should have skipped; a month with one real interruption is a
   scene.
6. **Checkpoint**, and write a short `TIMELINE.md` row for the stretch.

A month of downtime should cost three or four exchanges and produce one scene, one number, and
one complication.

