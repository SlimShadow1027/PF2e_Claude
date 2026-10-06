# 03 (D&D 4e) — Difficulty and the solo levers

**Replaces `system/03-difficulty-and-solo-levers.md` for a campaign with `System: dnd4e`.**

4e is the most tightly tuned of the three rulesets this framework runs, and it is tuned around
**five characters covering four roles**. A party of one is further from its assumptions than a
party of one is from Pathfinder's or D&D 2024's. That is workable, but not by accident.

---

## What actually breaks at a party of one

### 1. The budget scales; the fight does not

The encounter budget is per character, so one character gets one character's worth of monsters.
Arithmetically clean. In play it fails in two ways:

- **Action economy.** A standard monster acts once a round, as you do. One-on-one is an even
  trade. But four minions also act once a round each, so a budget-legal crowd gets four turns
  to your one. In a five-character party that crowd is spread across five people; alone, it all
  lands on you.
- **Focused fire.** Every monster in the room attacks the only target there is. Five
  characters share incoming damage; one does not. The same budget is far deadlier.

`python3 tools/dnd4e.py encounter --party-level N --party-size 1` gives the honest budget
number and says it is a standard encounter. It is the right number and it will still kill you.
4e's budget maths does **not** collapse at a party of one the way Pathfinder's Low threat
does — `degenerate_budgets` returns nothing — so there is no automatic warning. The problem is
in the shape of the fight, not the total.

### 2. No leader means the day is shorter

The surge pool is 4e's attrition clock. A leader's healing lets a party spend surges
efficiently and hands out extra healing on top. Alone, with no leader:

- Second Wind is your only in-combat healing, once per encounter, costing a surge and a
  standard action.
- Nothing refills surges but an extended rest.

So a solo character runs out of **day**, not out of hit points. Expect two or three encounters
between extended rests where a party would manage four or five.

### 3. No defender means nothing is held

Marks are how 4e stops a monster walking past the front line. With one character there is no
line. Monsters that are built to be held in place by a defender behave very differently when
nothing holds them.

---

## The levers, in the order to reach for them

### Lever 1 — build the fight for one, not budget it for one

The most effective change and the one that costs nothing. Within the same XP budget:

- **Fewer, tougher monsters** rather than many weak ones. One standard at the party's level
  beats four minions for a solo fight, because it trades turn-for-turn.
- **Avoid elites and solos.** They are built to survive five characters' worth of damage; alone
  you cannot kill one before it kills you. A solo monster against a solo character is the
  single worst matchup in the game.
- **Minions sparingly, and from one direction.** They are good for pressure and terrible as a
  surround.

### Lever 2 — the companion character

A 4e campaign of one is the strongest case in this framework for a second character under the
GM's hand. An NPC **leader** fixes the surge economy and an NPC **defender** fixes the marks,
and the budget then honestly counts two characters.

```
python3 tools/state.py --campaign X add-character "Sister Halle" --kind ally --level 3 ... 
python3 tools/dnd4e.py encounter --party-level 3 --party-size 2
```

Run the companion plainly and let the player direct them if they want to. Record in
`CAMPAIGN.md` that the party size is two, because the budget maths and the **XP divisor** both
read it.

### Lever 3 — the encounter's level

4e's native difficulty dial. Lower the encounter's level against the party's for an easier
fight and raise it for a harder one, holding the budget roughly level. This is why
`dnd4e.py encounter` has no `--threat` flag: the published budget is one column, and difficulty
is expressed in the monsters you pick, not in the total you spend.

### Lever 4 — objectives other than "kill it"

Shared with both siblings: `system/17-encounter-objectives.md`. 4e rewards this unusually well,
because its monsters are built around positioning and its terrain powers are first class. A
fight the character can **win by leaving** is a fight a solo character can survive.

Aim for at least half of fights to have a win condition other than everything hostile being
dead — and telegraph it, every time.

### Lever 5 — hand out action points

An action point buys an extra action. A solo character's scarcest resource is actions, so this
is the most direct relief available. Milestones give one every second encounter; nothing stops
a GM granting an extra at a dramatic turn and saying so out loud.

```
python3 tools/state.py --campaign X milestone
python3 tools/state.py --campaign X action-point set verrin-ash 2
```

### Lever 6 — say it

Shared with both siblings. If the numbers are drifting — too easy, too lethal, too slow — say
so at the table rather than quietly compensating. `python3 tools/analyze.py --campaign X`
prints the dice and the deaths; `dashboard.py` prints the surge pool and the powers spent.
An undisclosed adjustment is a worse problem than a badly tuned fight.

---

## The XP problem nobody expects

**4e divides an encounter's XP by the party size.** So a solo character banks the whole
encounter's XP, where five characters each bank a fifth. A party of one therefore levels
roughly **five times faster** per encounter than 4e expects.

This is 4e's own rule and `xp_award` implements it as written. It is also the biggest
difference between the three rulesets' advancement, and it is worth deciding what to do about
it **before session one**, because changing it later feels like a punishment:

| Choice | What it does |
|---|---|
| **Leave it** | Levels fly past. Fine for a short campaign that wants to see the Paragon tier |
| **Divide by a notional party size** (4 or 5) | Advancement at the published pace. Record the divisor in `RULES_DELTAS.md` |
| **Award by milestone** | Level at story beats and ignore the counter. Record that too |

Whatever you pick, write it in `campaigns/X/RULES_DELTAS.md` with the reason. A deviation from
the published rule is legitimate; an undocumented one is not.

---

## The difficulty presets

The framework's four presets are the same in all three rulesets — `Story`, `Standard`,
`Gritty`, `Nightmare` — and are set with `python3 tools/state.py --campaign X preset <name>`.
They are this framework's convention, not a published rule, and the tools store the label
rather than applying a multiplier. In 4e they read as:

### `Story` — fiction first, combat rarely lethal
- Encounters a level or two **below** the party's.
- A companion **leader**, so the surge economy works. Action points granted freely.
- Standard monsters and minions only; no elites, no solos.
- Death saving throws public, rolled honestly, with something in the fiction usually able to
  intervene.

### `Standard` — the rules as written, built for one
- Encounters **at** the party's level, within the per-character budget.
- A companion recommended, and the budget counts them.
- Milestones and action points as published.
- No elites or solos against a single character.
- Death saving throws public and rolled honestly; the depth below zero tracked openly.

### `Gritty` — resources matter, retreat is common, death is real
- Encounters at or **one above** the party's level, with a telegraphed way out.
- Companion optional; if there is none, say plainly what that does to the surge pool.
- Surges counted strictly, and extended rests only where the fiction allows one.
- Death saving throws **private** (`transparency: mystery`), rolled honestly, reported as
  "worse" or "holding".

### `Nightmare` — no safety nets, full attrition
- Encounters **above** the party's level; elites on the table.
- No companion unless the player recruits one in the fiction and keeps them alive.
- One extended rest per in-world day, enforced, and the milestone clock runs regardless.
- Death is death, and the negative-bloodied threshold is the floor it sounds like. **Agree
  this one explicitly before the first session.**

Changing preset mid-campaign is legitimate at any time, in either direction, and needs no
reason. Record the change and the session it changed in. `dial it back` / `dial it up` are the
player's handles on this and are honoured without argument.
