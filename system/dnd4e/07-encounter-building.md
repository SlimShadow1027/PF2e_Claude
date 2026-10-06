# 07 (D&D 4e) — Building an encounter

**Replaces `system/07-encounter-building.md` for a campaign with `System: dnd4e`.** Read
`system/17-encounter-objectives.md` alongside it — that one is shared by all three rulesets and
is the half of this job that matters more.

> **This document gives no numbers, and that is the licence, not an oversight.** The XP budget
> per character, the XP a monster of a given level is worth, and the elite/solo/minion
> multipliers are all 4e tables with no open-content release. `tools/dnd4e.py encounter`
> **refuses to compute** until you have filled them in `tools/dnd4e_tables.json` from your own
> books, and names the table and the book when it refuses. See `system/dnd4e/README.md`.

---

## The three tables this needs

```
python3 tools/dnd4e.py tables
```

| Table | From | Why |
|---|---|---|
| `encounter_budget_per_character` | *Dungeon Master's Guide*, building an encounter | The budget. Without it nothing here computes |
| `monster_xp_by_level` | Monster Manual / DMG, Experience Point Rewards | What each monster costs |
| `monster_role_multipliers` | DMG, how elites, solos and minions count | How much monster an elite is |

Fill the levels you will actually use. A heroic-tier campaign needs levels 1–12 and nothing
above.

---

## The procedure

### 1. Start from the objective, not the monsters

Shared duty, and it comes first: **what does the player have to do, and what happens if they
take too long?** Aim for at least half of fights to have a win condition other than everything
hostile being dead, and **telegraph it in the fiction before initiative**.

### 2. Get the budget

```
python3 tools/dnd4e.py encounter --party-level 3 --party-size 1
```

The budget is **per character, multiplied by the party size**. It is linear: nothing collapses
at a party of one and there is no multiplier for group size. `degenerate_budgets` returns
nothing for 4e, which is true of the arithmetic and misleading about the fight — see below.

There is **no `--threat` flag**, and that is deliberate. 4e expresses difficulty by setting the
encounter's **level** against the party's, not by picking a budget column. If your printing
does give difficulty columns, fill `encounter_budget_columns` and they will appear here.

### 3. Spend it

```
python3 tools/dnd4e.py encounter --party-level 3 --party-size 1 \
    --monster 1x4:standard 2x3:minion
```

Monster specs are `LEVEL`, `LEVEL:ROLE` or `Nx LEVEL:ROLE`. The command prints each monster's
XP, the total, how that total rates against a standard encounter, and the XP award after the
party divisor.

### 4. Pick roles, not just levels

Roles are what makes a 4e fight interesting, and a mixed set is the whole craft:

| Monster role | What it does to the fight |
|---|---|
| **Artillery** | Attacks at range, weak up close — makes the player cross the room |
| **Brute** | High hit points, heavy damage, low accuracy — a damage clock |
| **Controller** | Conditions and zones — makes the ground the problem |
| **Lurker** | Appears, hits hard, vanishes — punishes a static position |
| **Minion** | 1 hit point, no damage on a miss — pressure and bodies |
| **Skirmisher** | Mobile, hits and moves — punishes a slow turn |
| **Soldier** | Marks and holds — the one that stops you leaving |

A fight of all brutes is a slugging match. One soldier plus two artillery is a problem to
solve. Two or three roles is usually enough.

### 5. Ranks: how much monster each one is

| Rank | What it is |
|---|---|
| **Standard** | One monster's worth. The default |
| **Elite** | Counts as more than one standard; tougher and acts more |
| **Solo** | Counts as several; built to fight a whole party alone |
| **Minion** | Exactly **1 hit point**, and **no damage from a missed attack** |

The multipliers live in your tables file. The minion rule is not a multiplier — it is a rule,
and the encounter tracker warns if a minion is entered with any hit point total but 1.

---

## What the budget does not tell you — the solo problem

The arithmetic is linear and the fight is not. Two things the budget cannot see:

**Action economy.** A budget-legal crowd of minions gets one turn each; a solo character gets
one turn. Four minions against one character is four attacks a round against one. In a party of
five that pressure is shared; alone it is not.

**Focused fire.** Every monster in the room attacks the only target there is.

So for a party of one, within the same budget: **fewer and tougher beats many and weak**, and
**elites and solos are the matchup to avoid entirely** — they are built to survive a whole
party's damage output, and a lone character cannot get through one before it gets through them.
`system/dnd4e/03-difficulty-and-solo-levers.md` is the full treatment.

---

## Terrain is a monster you do not pay for

4e's strongest and cheapest difficulty lever. Difficult terrain, a drop, a zone of fire, a
collapsing floor, something that can be pushed — none of it costs XP and all of it makes the
grid a decision rather than a distance. Forced movement is everywhere in 4e, so terrain that
punishes being moved is worth more than another monster.

Describe it **before initiative**, in squares, and let the player use it.

---

## Checking what you built

```
python3 tools/dnd4e.py encounter --party-level 3 --party-size 1 --monster 1x4:soldier 2x2:artillery
```

The rating it prints (`a standard encounter`, `above a standard encounter`, …) is **this
framework's own convention**, flagged as such in `dnd4e.py sources`: 4e tunes difficulty by
encounter level rather than publishing a budget-to-label mapping, so the five labels are this
framework's reading of how far a build sits from the budget. The budget it compares against is
yours, from your books.

Monster statistics themselves come from published material, cited by name, source and level —
rule 4 of the GM contract applies here exactly as it does to the other two rulesets. What this
framework cannot give you is a benchmark to sanity-check an unfamiliar stat block against,
until `monster_benchmarks` is filled from the DMG's monster-statistics-by-level table.

**Never carry a stat block across rulesets.** A CR 2 D&D 2024 monster, a level 2 Pathfinder
creature and a level 2 4e monster are three different creatures, and none of their numbers
survive the trip — 4e's half-level bonus alone makes its defences a different scale.
`python3 tools/world.py crossing` is the full statement.
