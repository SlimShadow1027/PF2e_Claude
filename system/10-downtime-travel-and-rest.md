# 10 — Downtime, travel and rest

---

## Exploration activities

Out of combat, moving through the world, each character has **one exploration activity** at a
time. Changing it takes no action; it is simply what they are doing.

| Activity | Speed | What it does |
|---|---|---|
| Avoid Notice | half | Stealth while travelling; at the start of an encounter you roll Stealth for initiative *and* to see whether the enemies notice you |
| Defend | half | you have your shield raised before your first turn begins |
| Detect Magic | half or slower | no chance of overlooking an aura up to 300 ft/min; **150 ft/min or slower** to detect auras *before* you walk into them |
| Follow the Expert | matches the ally | add your level as a proficiency bonus even if untrained, plus +2 / +3 / +4 for an expert / master / legendary ally |
| Hustle | **double** | for a number of minutes equal to your Constitution modifier × 10, minimum 10 |
| Investigate | half | Recall Knowledge as a **secret** check for clues as you go |
| Repeat a Spell | half | keep a 2-action-or-less spell going; the GM may make you fatigued |
| Scout | half | +1 circumstance bonus to **everyone's** initiative in the next encounter |
| Search | half | Seek meticulously; **300 ft/min** to guarantee you checked everything, **150 ft/min** to check it before walking into it. The GM rolls a free **secret** Seek |

Skill exploration activities also exist and run at whatever the skill says: Borrow an Arcane Spell,
Coerce, Cover Tracks, Decipher Writing, Gather Information, Identify Alchemy, Identify Magic,
Impersonate, Learn a Spell, Make an Impression, Repair, Sense Direction, Squeeze, Track, Treat
Wounds.

**The important one for solo play:** a single character can only do one of these. Choosing Search
means not Avoiding Notice, which means being seen. That is a real decision and it should be
presented as one, not defaulted. It is also why Scout's "+1 to everyone's initiative" is worth
less at this table than its reputation suggests, and why Follow the Expert is worth nothing at
all with no ally to follow.

**Source:** Player Core p.438-439, Exploration Activities —
<https://2e.aonprd.com/Rules.aspx?ID=2442>. Every activity and its speed effect read from the
published text.

---

## Travel speed

| Speed | Feet per minute | Miles per hour | Miles per day (8 hours) |
|---|---|---|---|
| 10 ft | 100 | 1 | 8 |
| 15 ft | 150 | 1.5 | 12 |
| 20 ft | 200 | 2 | 16 |
| 25 ft | 250 | 2.5 | 20 |
| 30 ft | 300 | 3 | 24 |
| 35 ft | 350 | 3.5 | 28 |
| 40 ft | 400 | 4 | 32 |
| 50 ft | 500 | 5 | 40 |
| 60 ft | 600 | 6 | 48 |

**Source:** Player Core p.438, Travel Speed — <https://2e.aonprd.com/Rules.aspx?ID=2441>. All nine
rows read from the published table. `python3 tools/pf2e.py tables travel` prints the same rows with
the terrain multipliers.

Terrain multipliers, applied to the day's distance:

| Terrain | Effect |
|---|---|
| Road, open plain | full speed |
| Difficult terrain (forest, rubble, deep snow) | half speed |
| Greater difficult terrain (swamp, thick ice, a cliff face) | one third speed |
| Hot or cold climate without protection | fewer travel hours per day |

The published table *"assume[s] traveling over flat and clear terrain at a determined pace, but one
that's not exhausting."* **Difficult terrain halves** the rate; **greater difficult terrain reduces
it to one third.** Where travel needs a skill check — climbing, swimming — the GM may call for one
**once per hour** and read progress off the table.

⚠ The hot/cold-climate row is this framework's own note, not a published figure.

**Source:** Player Core p.438, Travel Speed — <https://2e.aonprd.com/Rules.aspx?ID=2441>.

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

**Once every 24 hours you can take a period of rest, typically 8 hours.** The published rule is
exactly that — there is no separate "hours of sleep" requirement, and this framework previously
invented one. It restores:

- **Hit points** equal to **Constitution modifier (minimum 1) × level**.
- **All spell slots** and **all Focus Points** — though those come from the daily preparations
  afterwards, not the sleep itself.
- **Reduces drained and doomed by 1** each (from the condition text).
- **Removes fatigued**, given a full night.

Two penalties are published and both matter on the road:

- **Sleeping in armour** gives poor rest and leaves you **fatigued**.
- **More than 16 hours without resting** makes you **fatigued**, and you cannot recover from that
  fatigue until you rest **at least 8 continuous hours**.

```
python3 tools/state.py --campaign X daily-prep
```

restores slots and focus, steps drained and doomed down by 1, and reports what changed. It does
**not** restore the hit points drained took away — that is correct, and the tool says so.

**Source:** Player Core p.439, Rest and Daily Preparations —
<https://2e.aonprd.com/Rules.aspx?ID=2443>, quoting: *"Once every 24 hours, you can take a period
of rest (typically 8 hours), during which you heal naturally, regaining Hit Points equal to your
Constitution modifier (minimum 1) times your level."*

### Long-term rest, in downtime

Spending **an entire day and night resting** during downtime recovers **Constitution modifier
(minimum 1) × double your level** in hit points. That is the lever for a character who is a long
way down and has no Medicine: two days of doing nothing beats one long night.

**Source:** Player Core p.440, Downtime Mode — <https://2e.aonprd.com/Rules.aspx?ID=2444>.

### Daily preparations

**Around 1 hour** after resting, and only once per day, and only if you rested. During it:
spellcasters regain slots and prepared casters choose the day's spells; Focus Points and
per-day item uses reset; you don armour and equip gear; you **invest up to 10 worn magic
items**.

This is the moment to ask the player what they are preparing *for*, which is a better question
than what they are preparing.

**Source:** Player Core p.439 — <https://2e.aonprd.com/Rules.aspx?ID=2443>.

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

**Requires a healer's toolkit**, worn or held.

**Two things the framework originally missed, and both matter solo:**

- **An hour of treatment doubles the healing.** *"If you succeed at your check, you can continue
  treating the target to grant additional healing. If you treat it for a total of 1 hour, double
  the Hit Points it regains from Treat Wounds."* For a character with no healer in the party this
  is the single largest attrition lever available, and it costs only in-world time.
- **A critical success removes the wounded condition too**, not just a success.

The immunity window is precise: the target is immune to Treat Wounds for **1 hour**, and that hour
*overlaps the ten minutes spent treating* — so a patient can be treated **once per hour, not once
per seventy minutes**.

Attempting a higher DC than your rank allows is optional and the critical-failure damage stays
1d8 either way.

**Source:** Treat Wounds — <https://2e.aonprd.com/Actions.aspx?ID=57>. Every figure in the table
above, the DCs, the healing, the 1d8 on a critical failure, the healer's-tools requirement, the
1-hour immunity window and the 1-hour doubling are quoted from it, including the parenthesis
*"so a patient can be treated once per hour, not once per 70 minutes"*. Both success and critical
success remove **wounded**. AoN still serves this action from the pre-Remaster Core Rulebook
p.249; the Remaster text renames the tools and is otherwise unchanged.

For a solo character this is the main attrition lever. The `Story` and some `Standard` presets
in `03-difficulty-and-solo-levers.md` grant a free one between encounters precisely because
there is nobody else to cast a heal.

### Administer First Aid

Two actions, Medicine, untrained, on an **adjacent** creature that is dying or bleeding. You are
holding healer's tools, or wearing them with a hand free. If the creature is both, choose which
before you roll.

| Use | DC | Success | Critical failure |
|---|---|---|---|
| **Stabilise** | **5 + the creature's recovery DC** — typically **15 + its dying value** | it loses dying, but stays unconscious | its dying value **increases by 1** |
| **Stop bleeding** | usually the DC of the effect that caused the bleed | it attempts a flat check to end the persistent damage | it immediately takes damage equal to its persistent bleed |

The stabilise DC is the one worth having right: against a creature at dying 2 that is **DC 17**,
not 15, and the critical failure pushes it to dying 3.

**Source:** Administer First Aid — <https://2e.aonprd.com/Actions.aspx?ID=54>.

For one character this is the action they cannot use on themselves while unconscious, which is
what makes the death spiral in `03-difficulty-and-solo-levers.md` a structural problem rather than
a bad-luck problem.

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

