# 11 — Levelling up

A checklist, run in order, ending with a full re-derivation and a diff. The point of the diff is
that an arithmetic error made at level 3 gets caught at level 4 instead of compounding to
level 11.

---

## When

At 1000 XP, or at the milestone if the campaign uses milestone advancement.
`python3 tools/state.py --campaign X xp add N` warns at 1000.

At 1,000 XP, level up and **subtract 1,000 — the remainder carries over.** Player Core: *"If you
have any Experience Points left after this, record them—they count toward your next level."* So a
character who banks 1,080 XP levels and starts the next level on 80.

**Source:** Player Core p.29, Leveling Up — <https://2e.aonprd.com/Rules.aspx?ID=2065>.

---

## The checklist

Work through every row. Say "nothing at this level" out loud for the ones that do not apply,
rather than skipping them silently — a skipped row is how a missing feat happens.

| # | Step | Notes |
|---|---|---|
| 1 | **Level** | `state.py level set N` |
| 2 | **Hit points** | + (class HP + Constitution modifier). Both current and maximum rise. |
| 3 | **Attribute boosts** | At levels **5, 10, 15 and 20**: four boosts, no two to the same attribute. +2 below 18, +1 at 18 or above. |
| 4 | **Class feature** | Whatever the class grants at this level. |
| 5 | **Class feat** | At even levels for most classes. |
| 6 | **Skill increase** | At levels 3, 5, 7, 9, 11, 13, 15, 17, 19. Trained→expert; expert→master from level 7; master→legendary from level 15. |
| 7 | **Skill feat** | At even levels. |
| 8 | **General feat** | At levels 3, 7, 11, 15, 19. |
| 9 | **Ancestry feat** | At levels 5, 9, 13, 17. |
| 10 | **Archetype feat** | Only if Free Archetype is on: at every even level. |
| 11 | **Proficiency changes** | Class-granted increases to attack, defence, spell, Perception and save proficiencies. Check the class table; these are easy to miss and they move several derived numbers at once. |
| 12 | **Spell slots and new ranks** | New slots, and a new spell rank at every odd level for most casters. `state.py slots set <who> <rank> <max>` |
| 13 | **Focus pool** | If a class feature raised it: `state.py focus set <who> <n> --max <n>` |
| 14 | **Spells known / prepared list** | Add what the level grants; retrain if the class allows. |
| 15 | **Item expectations** | Compare against the curve — see below. |

**Sources for the progression rows above**, all read from the published text:

| Row | Levels | Source |
|---|---|---|
| Attribute boosts | 5, 10, 15, 20 | Player Core p.29, Leveling Up — *"all characters gain four attribute boosts at 5th level and every 5 levels thereafter"* (<https://2e.aonprd.com/Rules.aspx?ID=2065>) |
| General feats | 3, 7, 11, 15, 19 | Player Core p.249, Chapter 5: Feats — *"a general feat when you reach 3rd level and every 4 levels thereafter"* (<https://2e.aonprd.com/Rules.aspx?ID=2142>) |
| Skill feats | every even level | Player Core p.249 — *"skill feats at 2nd level and every 2 levels thereafter"* |
| Ancestry feats | 1, 5, 9, 13, 17 | Player Core, Chapter 2: Ancestries — *"an ancestry feat at 1st level, and you gain another at 5th level, 9th level, 13th level, and 17th level"* (<https://2e.aonprd.com/Rules.aspx?ID=2074>) |
| Skill increase ranks | expert any level, master at 7+, legendary at 15+ | Player Core p.225, Improving Skills (<https://2e.aonprd.com/Rules.aspx?ID=2134>) |

One caveat worth being exact about: the **levels at which skill increases and class feats arrive
are per class**, not universal. Player Core says *"Your class lists the levels at which you gain
each of these improvements."* The 3/5/7/9/11/13/15/17/19 pattern for skill increases and the
even-level pattern for class feats hold for the classes in Player Core, but **the class
advancement table is the authority** — read it at the level-up and say you did.

Also from the same page, two knock-on effects that are easy to skip:

- An **Intelligence** boost makes the character trained in an **additional skill and language**.
- A **Constitution** boost means recomputing maximum hit points — typically **+1 HP per level**,
  which at level 10 is 10 HP, not 1.

---

## Item expectations at the new level

```
python3 tools/pf2e.py tables item-bonuses
python3 tools/pf2e.py treasure --level <new level> --party-size <N>
```

The item-bonus table is **verified** (it comes from Automatic Bonus Progression, the official
codification of the curve the core math assumes). Check the character against it:

- Is the attack potency what the level expects?
- Are the striking dice right?
- Is the armour's potency rune keeping up?
- At level 7+, perception; at level 8+, saves?

If the character is behind, that is a treasure-pacing problem, not a character problem — see
`09-loot-and-economy.md`. Fix it in the next hoard rather than by handing over an item at the
level-up, which teaches the player that levelling produces gear.

If Automatic Bonus Progression is **on**, the bonuses simply arrive at those levels and there is
nothing to check.

---

## Re-derive every number from scratch, then diff

This is the step that makes the rest worth doing. **Do not adjust the old numbers; compute the
new ones from the build.**

For each of these, write the formula, compute it, and compare against what was on the sheet:

| Statistic | Formula |
|---|---|
| HP maximum | ancestry HP + (class HP + Con modifier) × level |
| AC | 10 + Dex (capped by armour) + proficiency + item |
| Fortitude / Reflex / Will | attribute + proficiency + item |
| Perception | Wis + proficiency + item |
| Class DC | 10 + key ability + proficiency |
| Spell attack | key ability + proficiency |
| Spell DC | 10 + key ability + proficiency |
| Each attack bonus | attribute + proficiency + item + any circumstance source |
| Each skill | attribute + proficiency + item |
| Bulk limits | encumbered after 5 + Str; maximum 10 + Str |

Proficiency is **level + 2/4/6/8** for trained/expert/master/legendary, unless Proficiency
Without Level is on, in which case it is just 2/4/6/8.

Then present the **diff** as a table, old against new, and say where the change came from:

```
| Statistic | Was | Now | Why |
|---|---|---|---|
| HP max      | 38  | 48  | +8 class +2 Con, level 5 |
| AC          | 19  | 20  | expert in light armour at level 5 |
| Will        | +9  | +12 | +1 level, +2 expert, +0 item — and Wisdom boosted to 16 |
| Athletics   | +11 | +12 | +1 level |
| Reflex      | +11 | +12 | +1 level  ← was recorded as +10 on the old sheet: corrected |
```

**Any row where the recomputed number disagrees with the sheet is a bug that was already
there.** Say so plainly, correct it, and note it in the character file's level-up history. Do
not quietly adopt the new number; the player should know their Reflex has been wrong for two
levels.

Update state with the new values:

```
python3 tools/state.py --campaign X level set 5
python3 tools/state.py --campaign X hp kaelen --current 48 --max 48
python3 tools/state.py --campaign X set pcs.kaelen.ac 20
python3 tools/state.py --campaign X set pcs.kaelen.saves.will 12
```

---

## Then

```
python3 tools/validate.py --campaign X
python3 tools/state.py --campaign X render
python3 tools/state.py --campaign X checkpoint "level 5"
```

The checkpoint means a git commit, so `git diff` across it shows exactly what levelling changed —
which is the record that makes the next level-up's diff trustworthy.

Also worth doing at a level-up, since it is a natural pause:

- Run `python3 tools/analyze.py --campaign X` and look at the per-save success rates. Which save
  is actually the weak one, with what sample size?
- Run the **difficulty check-in** from `03-difficulty-and-solo-levers.md`.
- Run the **flag report** from `20-player-flags.md`, if this is also an arc boundary.
