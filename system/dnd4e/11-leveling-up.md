# 11 (D&D 4e) — Levelling up

**Replaces `system/11-leveling-up.md` for a campaign with `System: dnd4e`.**

> **The advancement table is yours to supply.** 4e's Character Advancement table — the
> cumulative XP to reach each level — is non-open content. Fill `character_xp` in
> `tools/dnd4e_tables.json` from the *Player's Handbook*, as far as your campaign will reach.
> Until then `dnd4e.py advancement` prints the structure with `(not filled)` in the XP column,
> and `state.py xp add` says plainly that it cannot tell you whether a total is a level-up
> rather than borrowing a threshold from another ruleset.

---

## Thirty levels, three tiers

| Tier | Levels | What the game is about |
|---|---|---|
| **Heroic** | 1–10 | Local. A town, a ruin, a warband. Mortal threats |
| **Paragon** | 11–20 | Regional and planar. A paragon path opens at 11 |
| **Epic** | 21–30 | The world and the planes. An epic destiny opens at 21 |

Both sibling rulesets stop at 20. A 4e level number is therefore drawn from a different scale
and **does not read across** — see the scope bands below.

```
python3 tools/dnd4e.py advancement
```

---

## XP is cumulative, and divided by the party

**Cumulative**: the total climbs and is never reset, as in D&D 2024 and unlike Pathfinder's
flat 1,000 with a resetting counter.

**Divided**: an encounter's XP is split among the characters who took part. This is 4e's own
rule, and it is the third distinct answer the three rulesets give to the same question:

| | Budget for a small party | Award |
|---|---|---|
| Pathfinder 2e | Shrinks with the party | The four-character figure, **undivided** |
| D&D 2024 | Per character × party size | The monsters' XP, **undivided** |
| **D&D 4e** | Per character × party size | The monsters' XP, **divided by party size** |

So a solo 4e character banks the **whole** encounter's XP and levels roughly five times faster
per encounter than 4e expects. Decide what to do about that before session one, record the
decision in `RULES_DELTAS.md`, and do not change it quietly later —
`system/dnd4e/03-difficulty-and-solo-levers.md` lays out the three choices.

```
python3 tools/state.py --campaign X xp add 1200
python3 tools/state.py --campaign X level 4
```

`level` without `--who` sets the party level and every character's level together, which is
what a solo campaign wants.

---

## What each level gives

4e is unusually regular about this, and the regularity is what makes it easy to get wrong —
there is no level that gives nothing, so a skipped level is invisible until the numbers stop
working.

| | |
|---|---|
| **Every level** | Hit points, by the class's per-level figure |
| **Every even level** | **Half level, rounded down, goes up** — which moves attack rolls, all four defences, all skill checks and initiative at once |
| **Odd levels** | Where the powers, feats and most features land |
| **Every 4th level** | Two ability score increases |
| **Levels 11 and 21** | A paragon path and an epic destiny, each of which is a second progression on top of the class |

The exact list of what a given class gains at a given level is in its class entry — non-open
content, from your books.

### The half-level bonus is the one that bites

At level 1 it is 0, so nothing looks wrong. At level 3 it is 1. At level 11 it is 5, applied to
**attack rolls, AC, Fortitude, Reflex, Will, every skill check and initiative**. A character
whose half-level bonus was not updated at level 2 is quietly 1 behind on nine numbers, and by
level 10 is 4 behind — which in 4e's tight maths means the monsters hit and they do not.

**Recompute, do not increment.** Rebuild each defence from its formula at every level rather
than adding to last level's figure. The same applies to attack bonuses.

---

## The level-up procedure

1. **Check the threshold.** `python3 tools/state.py --campaign X xp add <n>` says whether the
   cumulative total has reached the next level, or says it cannot tell you because
   `character_xp` is unfilled.
2. **Read the class entry** for what this level gives.
3. **Hit points up**, by the class's per-level figure. Then **recompute the derived numbers**:
   the bloodied value is half the new maximum, the death threshold is that negated, and the
   surge value is a quarter of the new maximum.
4. **Half level**, if this is an even level. Then **rebuild** the four defences, the attack
   bonuses, the skill modifiers and initiative from their formulas.
5. **Powers.** New ones where the level gives them; **swap out** an old one where the class
   says to, and narrate the retraining rather than just ticking it.
6. **Feat**, where the level gives one. **Ability increases**, every fourth level.
7. **Surge pool** does not change with level by itself — it is the class's number plus the
   Constitution modifier, so it moves when Constitution does.
8. **Write it down.**

```
python3 tools/state.py --campaign X level 4
python3 tools/state.py --campaign X hp verrin-ash --max 46 --current 46
python3 tools/state.py --campaign X set pcs.verrin-ash.half_level 2
python3 tools/state.py --campaign X set pcs.verrin-ash.defences.ac 19
python3 tools/state.py --campaign X power add verrin-ash "Disruptive Strike" encounter
python3 tools/state.py --campaign X surge set verrin-ash --max 11
python3 tools/state.py --campaign X render
python3 tools/state.py --campaign X checkpoint "Verrin reaches level 4"
```

Then update the prose sheet at `campaigns/X/characters/<key>.md` — the powers with their text,
the feats, the gear. `state.json` holds the volatile numbers; the Markdown holds the built
character, and `validate.py` compares them.

---

## Tiers, scope bands and the shared world

The framework translates **scope**, never levels. 4e's thirty levels map onto the four shared
bands like this:

| Band | 4e | PF2e and D&D 2024 |
|---|---|---|
| `local` | 1–5 | 1–4 |
| `regional` | 6–10 | 5–10 |
| `national` | 11–20 | 11–16 |
| `worldly` | 21–30 | 17–20 |

```
python3 tools/world.py convert --level 14 --from dnd4e --to pf2e
python3 tools/rules.py bands --system dnd4e
```

That mapping is **this framework's own convention**, and `rules.py bands` says so in full: 4e
does band its levels into three published tiers, and the books describe each tier's reach, but
there is no open text to quote — so the four bands are this framework's reading, with the
Heroic tier split at 5 and the Paragon tier read whole as `national`.

What this means in play: a 4e Paragon-tier character and a Pathfinder level 13 character
threaten things of a comparable **size**. Their numbers have nothing to do with each other, and
neither does their treasure.

---

## Milestones are not levels

Easy to conflate, because both are counters. A **milestone** is every second encounter
completed without an extended rest, and it grants an **action point**. It has nothing to do
with levelling and resets on every extended rest.

```
python3 tools/state.py --campaign X milestone
```
