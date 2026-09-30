# 06 — The encounter runner

The exact combat loop, so combat is consistent and fast.

---

## Before round 1

1. **Name the objective** and telegraph it in the fiction. Every encounter has a win condition;
   see `17-encounter-objectives.md`. A timer the player cannot see is a trap, not a tactical
   problem.
2. **Build the map** if position matters — flanking, cover, reach, area templates, difficult
   terrain. See the map section below.
3. **Start the encounter in state:**

```
python3 tools/state.py --campaign X encounter start "Crypt landing" \
    --objective "Reach the lever before the water rises (6 rounds)" --map crypt-landing
```

4. **Roll initiative for everyone, in one call:**

```
python3 tools/roll.py init --actors "kaelen:+7,ghoul-a:+5,ghoul-b:+5,ghast:+8" \
    --party kaelen --campaign X
```

Higher total first; on a cross-side tie **the adversary acts first**; same-side ties are
settled by a logged roll-off. Add each combatant with its rolled initiative:

```
python3 tools/state.py --campaign X encounter add Kaelen --side party --ref kaelen --init 18 --position C4
python3 tools/state.py --campaign X encounter add "Ghoul A" --side adversary --init 19 --hp 28 --position E5 --level 1
```

5. **Telegraph it on the record:** `encounter telegraph "the water is already at your ankles"`.

---

## The per-round tracker

`python3 tools/state.py --campaign X encounter status` prints it. The shape:

| | Combatant | Init | HP | Actions | MAP | **Reaction** | Position | Conditions (with durations) |
|---|---|---|---|---|---|---|---|---|
| → | Kaelen | 18 | 10/22 | ◆◆◇ | 1 | **available** | D5 | frightened 2 · 2 rounds |
| | Ghoul A | 19 | badly hurt | ◆◆◆ | 0 | **used: Attack of Opportunity** | E5 | — |

- **Round number** and **whose turn** are marked with `→`.
- **Actions** as pips: `◆◆◆` three left, `◆◇◇` one left.
- **MAP** is the multiple-attack-penalty step reached this turn: 0, 1 or 2.
- **Reaction** is a column, not a footnote. See the obligation below.
- **Conditions** carry their remaining durations.
- **Persistent damage** and **temp HP** appear in the conditions column.

Enemy HP is tracked privately unless the transparency mode says otherwise. In `standard` and
`mystery` the player sees a **wounded descriptor** — unhurt, lightly hurt, hurt, badly hurt,
barely standing, down — rather than a number. The dashboard follows the same rule.

Advance a turn with `encounter next`, which resets the next combatant's actions, MAP and
reaction, ticks the outgoing combatant's conditions, and bumps the round when it wraps.

---

## The reaction obligation

**Before resolving *any* trigger, check every party member's available reactions and ask the
player before resolving.**

Triggers that require the check:

- A creature **moving out of reach** or **through a threatened square**.
- An **incoming attack** (Shield Block, Nimble Dodge, and anything similar).
- A **spell being cast within sight** (counterspell, and reactions that trigger on casting).
- A creature **standing up from prone**, or otherwise taking a triggering action within reach.
- A **readied action's** stated trigger firing.
- Any class- or feat-specific reaction whose trigger the fiction has just produced.

Reactive Strike, Shield Block, readied actions and class reactions are worth a large share of a
character's power, and **forgetting to offer them is the most common way an automated GM quietly
shortchanges the player.** It is a stated duty here, with a tracker column behind it.

Ask in one line, before the trigger resolves, not after:

> The ghoul steps out of your reach toward the porter. **Reactive Strike?** (+13 vs AC 15, your
> reaction is available.)

Spend it explicitly when the player says yes:

```
python3 tools/state.py --campaign X encounter reaction Kaelen "Reactive Strike"
```

Because the tracker records it, **"you have no reaction available" is always a statement that
can be backed with the tracker** — say which trigger spent it and in which round.

Reactions come back at the start of the holder's turn (`encounter next` does it). A reaction
spent on another creature's turn stays spent until then.

---

## Enemy tactics: honest, not omniscient

Creatures act on what they can **perceive** and on what their published `Tactics:` note says
they **want**. Each `bestiary/<creature>.md` carries that note, taken from the published entry
where one exists.

- An **unintelligent creature does not focus-fire optimally.** A zombie goes for what is
  closest, or what hurt it last.
- A **trained soldier does.** It flanks, it targets the caster, it retreats behind cover.
- **State which it is when it matters**, in one clause, so the player can read the fight:
  "the ghouls are hungry rather than clever and go for the nearest meat" tells the player
  something they can use.

A creature does not know the player's AC, their HP, or which save is weakest, unless the fiction
says it has seen them fight before. It does not know about a trap it did not set. It does not
act on information the GM has and it does not.

### Morale

Each creature group has a **morale threshold** in its bestiary entry — a wound level, a leader's
death, a number of losses — at which it flees, surrenders, or can be talked down. Apply it.
A fight that ends because the last two goblins run is a better fight than one that ends because
they were killed at 2 HP each.

---

## Batched minions

A one-versus-six fight resolved creature by creature takes an hour and most of it is
bookkeeping.

**Where several identical creatures at least three levels below the party act together, group
them into a squad:**

- **One initiative entry** for the squad.
- **All their attacks rolled in a single tool call** (`roll.py batch`, or several expressions on
  one `check`).
- **One line of narration for the lot** — "three of the six find gaps in your guard".

But **each member still keeps its own hit points and conditions**, because pooling them would
break area damage and single-target focus. Record them as individual combatants sharing a
`--squad` name:

```
python3 tools/state.py --campaign X encounter add "Skeleton 1" --side adversary --init 12 --hp 8 --squad skeletons
python3 tools/state.py --campaign X encounter add "Skeleton 2" --side adversary --init 12 --hp 8 --squad skeletons
```

**The batching is a speed change, not a math change.**

**Promote a creature out of the squad** the moment it becomes individually interesting — it
flanks, it flees, it is the one carrying the key, it is the only one left standing. From then on
it is tracked on its own and gets its own narration.

### True minion mode is separate, optional homebrew

Minions dropping to any solid hit rather than tracking HP. It must be stated as homebrew in
`RULES_DELTAS.md`, with its difficulty effect spelled out, and **never enabled without the
player's say.** Batching is the default because it costs nothing.

---

## The tactical map

Position matters in PF2e, so maintain an **ASCII grid in `maps/<scene>.md`** for any fight where
it does. Copy `templates/maps/_MAP_TEMPLATE.md`.

- **One square is 5 feet.** Distances in feet.
- Columns are letters, rows are numbers, so a square is `C4`.
- A terrain key with the **mechanical effect** of each symbol, not just its name — difficult
  terrain costs 10 feet per square, standard cover is +2 AC.
- **Update token positions each round**, and say what moved.
- Note what **changes during the fight** and on which round: spreading fire, rising water, a
  collapsing bridge.

Move a token in state as well as on the grid:

```
python3 tools/state.py --campaign X encounter position Kaelen D5
```

Positions restore with a mid-combat checkpoint, so the grid and the tracker cannot drift apart.

---

## Resolving a turn

For each combatant, in initiative order:

1. **Start of turn:** any start-of-turn effects. If dying, roll the recovery check —
   `python3 tools/state.py --campaign X recovery <who>` rolls it and applies the result.
2. **Three actions.** Spend them explicitly:
   `encounter action <who> 1`. Reaching 0 refuses a fourth.
3. **Each attack after the first** raises the MAP step: `encounter map-step <who>`.
   −5/−10, or −4/−8 with an agile weapon.
4. **Roll everything**, with the label naming what it is, and batch where you can.
5. **Apply damage through the tool**, so dying is computed rather than remembered:
   `python3 tools/state.py --campaign X damage kaelen 12 --from-crit`
6. **End-of-turn bookkeeping**, in this order:
   - Tick condition durations (`encounter next` does this for the outgoing combatant).
   - **Persistent damage:** roll the damage, then the DC 15 flat check to end it —
     `roll.py damage "1d6" --type bleed` then `roll.py flat 15`.
   - **Sustained spells:** the caster spends an action or the spell ends.
   - Re-render state if anything structural changed.
7. **`encounter next`.**

At the end of a **round**, say the round number out loud and note anything on a timer that
advanced.

---

## At the end of combat

In this order:

1. **XP awarded** — `python3 tools/pf2e.py encounter --party-level N --party-size M --add ...`
   for the real total, then `state.py xp add N`.
2. **Treasure** — record it in `logs/loot.md` and in state.
3. **Conditions that persist** — say which, with their remaining durations. Remove the rest.
4. **`encounters/history.md` entry**, including the `Objective:` field and the honest
   `Difficulty landed as:` line. `validate.py` fails an entry without an objective.
5. **`encounter end`**, which clears the live tracker.
6. **A checkpoint**, which per the charter means a git commit.

```
python3 tools/state.py --campaign X encounter end
python3 tools/state.py --campaign X checkpoint "cleared the crypt landing"
```
