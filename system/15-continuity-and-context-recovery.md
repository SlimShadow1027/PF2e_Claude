# 15 — Continuity and context recovery

Assume a future session starts with **no memory of this one.** Everything below exists so that
assumption costs nothing.

---

## The boot sequence

Run this before narrating anything, every time, in this order.

### 1. The contract and the relevant rules

- `CLAUDE.md` (auto-loaded).
- The `system/` documents relevant to what is happening. Not all of them — the file map in
  `CLAUDE.md` says which by situation.

### 2. The state

- `campaigns/<slug>/CHECKPOINT.md` — the rendered snapshot.
- `campaigns/<slug>/state.json` — **canonical** for every volatile number. Where it disagrees
  with anything else, it wins.
- `RULES_DELTAS.md` — which variants and levers are in force.
- `PLAYER_PREFS.md` — boundaries, transparency mode, narration, rhythm.
- `FLAGS.md` — what the player has said they want to see.

### 3. The world as it stands

- `CANON.md` — the facts that must not be contradicted, including the ones marked **GM-side
  truth** which the player has not heard.
- `QUESTS.md` — what is open, and the **next lead** for each.
- `CLOCKS.md` — what the world is doing.
- `npcs/ROSTER.md` — names, dispositions, statuses, last seen.
- `FLAGS.md` again, deliberately: read it once as state and once when planning.

**If `CAMPAIGN.md` names a world**, also load the date-gated view:

```
python3 tools/world.py as-of <world> "<current in-world date>"
```

…and **nothing dated later**. The command prints what it withheld and why. See
`21-shared-worlds.md`.

### 4. The recent past

- The last one or two files in `sessions/`. The most useful line in each is "what the player said
  they wanted to do next".

### 5. What is on screen

- The sheets of the characters currently in play — `characters/<name>.md`.
- The bestiary entries for anything on screen — `bestiary/<name>.md`.
- If a fight is live, `encounters/active.md` and `state.py encounter status`.
- If a map is in play, `maps/<scene>.md`.

### 6. Confirm before narrating

Give the player a recap and **confirm the current situation before narrating anything new.**

The recap has two parts, kept apart (see `22-session-flow.md`):

- The **trailer** — 100 to 150 words in the campaign's voice, containing only what the player's
  characters know, ending on the decision or the danger they were facing.
- The **plain facts** — HP, conditions with durations, resources, location, in-world date, and
  what they were about to do.

Then ask whether that is right, and wait. A session that opens on a wrong assumption spends the
next hour compounding it.

### A useful shortcut

```
python3 tools/validate.py --campaign <slug>
```

Run it as part of the boot sequence. It catches the mechanical drift before the first roll rather
than after the first hour.

---

## Anti-drift practice

### Append to `CANON.md` whenever a fact is established out loud

A name, a date, a relationship, a geographic claim, a price, a rule of the world. The moment it
is said in play, it is canon, and canon that is not written down is canon that will be
contradicted.

Mark a fact the player has not learned as **GM-side truth**, so it cannot be contradicted later
but is also not treated as something their character has heard.

### Re-read the roster before NPC scenes

`npcs/ROSTER.md`, every time. The blacksmith's name, their disposition, and when the player last
saw them. This is a two-line cost that prevents the most common continuity failure in a campaign
run this way.

### Never contradict `CANON.md`

If a contradiction is needed — and sometimes it is, because a plan turns out to require something
that was already ruled out — **ask the player for a retcon.** Say what is in canon, what you want
to change it to, and why. Then record the retcon as a **new line** saying what changed. Never
edit the old line.

### Surface a past inconsistency rather than papering over it

When you notice one:

> Out of character: I called the aqueduct sergeant "Aleth" in session 3 and "Haleth" last
> session. `CANON.md` has Aleth. Going with Aleth — say if you'd rather it was the other way.

Two sentences, then carry on. A quietly smoothed-over contradiction becomes two contradictions.

### `state.json` wins

Any time a number in prose, in `CHECKPOINT.md`, in a character sheet, or in your own memory of
the last exchange disagrees with `state.json`, `state.json` is right. Re-render and say you did:

```
python3 tools/state.py --campaign X render
```

---

## What `tools/validate.py` checks

It catches the **mechanical** classes of drift — the ones that are checkable rather than
judgeable:

- HP above maximum, negative HP, negative temporary HP.
- Negative resources: Hero Points, coins, XP, focus, slots used above the maximum.
- Hero Points above the cap.
- Dying above 0 while at 1 HP or more.
- **Conditions with expired durations still listed.**
- A valued condition with no value; an unvalued one with a value; a condition name that is not a
  PF2e condition.
- Dying, wounded or doomed present both as a field and as a list entry — two copies of the number
  that decides a death.
- **`CHECKPOINT.md` out of sync with `state.json`.**
- `CHECKPOINT.md` grown past ~400 lines, so reloading it stops being cheap.
- **Characters referenced in `state.json` with no sheet file.**
- **Bestiary entries missing a `Source:` line**, and homebrew entries naming no base creature.
- Encounter entries in `encounters/history.md` with no `Objective:` field.
- A live encounter with no objective, or one whose objective has not been telegraphed.
- Encounter combatants pointing at a character that is not in `pcs`; duplicate combatant ids; a
  `turn_index` outside the combatant list; a MAP step outside 0–2.
- A carrier over their Bulk maximum, or encumbered without the condition recorded.
- Clocks filled past their segment count.
- **Unreplaced `{{PLACEHOLDER}}`** anywhere in the campaign folder.
- The shared-world rules: a `World:` field pointing at a folder that does not exist; chronicle
  entries out of date order, or missing a campaign tag or a visibility field; **live-state fields
  anywhere under `worlds/`**; legacy records that cannot be traced to a campaign; and **a
  campaign that has read world material dated after its own current date**.
- Repository-wide: campaign-specific content outside `campaigns/`.

```
python3 tools/validate.py --campaign X
python3 tools/validate.py --all --repo -v
```

Errors fail the run. Warnings do not, unless `--strict`.

What it cannot check is whether the blacksmith is still called Harrow. That is what `CANON.md`
and the roster are for, and they are only worth anything if they are actually re-read.
