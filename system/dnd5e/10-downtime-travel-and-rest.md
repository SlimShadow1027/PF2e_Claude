# 10 (D&D 2024) — Downtime, travel and rest

**Replaces `system/10-downtime-travel-and-rest.md` for a campaign with `System: dnd5e`.**

The rest rules are where this game and Pathfinder diverge most in how a session *feels*. Pathfinder
recovers HP with a skill check and a day; this game recovers everything on an 8-hour sleep and
rations the middle of the day with Hit Dice. Running one cadence with the other's rules changes the
whole resource game.

---

## Travel

| Pace | Per minute | Per hour | Per day | Effect |
|---|---|---|---|---|
| Fast | 400 ft | 4 miles | 30 miles | Disadvantage on Wisdom (Perception or Survival) and Dexterity (Stealth) |
| Normal | 300 ft | 3 miles | 24 miles | Disadvantage on Dexterity (Stealth) |
| Slow | 200 ft | 2 miles | 18 miles | **Advantage** on Wisdom (Perception or Survival) |

An **8-hour travel day**. Beyond it, each extra hour needs a Constitution save at **DC 10 + 1 per
hour past 8** or costs an **Exhaustion level** — and Exhaustion is −2 to every D20 Test per level
in this game, so one pushed day is felt immediately.

Mounts double the distance for one hour, then need a Short or Long Rest. A good road raises the
maximum pace one step. The group moves at **Slow** if any member's Speed is halved or worse.

| Terrain | Max pace | Encounter distance | Forage | Navigate | Search |
|---|---|---|---|---|---|
| Arctic | Fast | 6d6 × 10 ft | 20 | 10 | 10 |
| Coastal | Normal | 2d10 × 10 ft | 10 | 5 | 15 |
| Desert | Normal | 6d6 × 10 ft | 20 | 10 | 10 |
| Forest | Normal | 2d8 × 10 ft | 10 | 15 | 15 |
| Grassland | Fast | 6d6 × 10 ft | 15 | 5 | 15 |
| Hill | Normal | 2d10 × 10 ft | 15 | 10 | 15 |
| Mountain | Slow | 4d10 × 10 ft | 20 | 15 | 20 |
| Swamp | Slow | 2d8 × 10 ft | 10 | 15 | 20 |
| Underdark | Normal | 2d6 × 10 ft | 20 | 10 | 20 |
| Urban | Normal | 2d6 × 10 ft | 20 | 15 | 15 |

The three DCs are the ones to actually call for: **Foraging** for food and water, **Navigation**
against getting lost, **Search** for finding something hidden along the way. Each is a Wisdom
(Survival) check in most terrains; the Search DC is Wisdom (Perception).

```
python3 tools/dnd5e.py travel --terrain swamp
python3 tools/state.py --campaign X advance-time "8 hours"
```

**Source:** SRD 5.2, "Playing the Game" → "Exploration" → "Travel Pace"; "Gameplay Toolbox" →
"Travel Pace".

### Who is doing what while travelling

Ask once per travel day and let the answer set the checks: who is navigating, who is watching, who
is foraging. A solo character cannot do all three, and **choosing which to drop is the interesting
part of travel.** Fast pace costs Perception and Stealth; Slow pace buys Perception. Say the
trade-off out loud so the choice is real.

---

## The encounter-check cadence

No published random-encounter frequency, so this is this framework's convention: **one check per
travel day and one per night watch**, with the chance set by how settled the land is. Roll it for
real.

```
python3 tools/roll.py flat 18 --campaign X --private --label "Day's travel — encounter check"
```

A result is not automatically a fight. Roll the terrain's **encounter distance** and ask what the
thing is doing before deciding whether it has noticed the party — most encounters at 180 feet in
grassland are an opportunity to avoid an encounter.

---

## Weather

Not published in SRD 5.2 as a table. `16-random-tables.md` has this framework's own, and says so.
Weather that changes the **maximum pace** or the Search DC is worth rolling; weather that is
scenery can be narrated.

---

## Making camp, watches, and the night

### Making camp
Where, how concealed, what fire, who sleeps when. A Wisdom (Survival) check for a good site if the
terrain makes it uncertain.

### Watches
A **Long Rest** is at least 8 hours with at least 6 asleep and **no more than 2 hours of light
activity, such as reading, talking, eating, or standing watch**. So a character *can* take a watch
inside their own Long Rest — up to two hours of it. A solo character taking the whole night's watch
does **not** finish a Long Rest.

This is the cleanest pressure point in a solo campaign: somebody has to watch, and the only person
there is the one who needs the sleep. An ally is the answer, and that is worth saying plainly when
the player is deciding whether to recruit one.

### Resting

| | Short Rest | Long Rest |
|---|---|---|
| Length | **1 hour** | **at least 8 hours**; 6+ asleep, ≤2 light activity |
| Hit Points | spend Hit Dice | **all** restored |
| Hit Dice | — | **all** spent dice restored |
| Spell slots | **no** | restored |
| Exhaustion | — | **one level removed** |
| Reduced ability scores / HP maximum | — | restored |
| Interrupted by | rolling Initiative, casting a non-cantrip spell, taking damage | the same, **plus an hour of physical exertion** |
| If interrupted | **confers no benefits at all** | resumable with +1 hour per interruption; an hour already rested gives a Short Rest's benefit |

At least 1 HP is needed to start either. **After a Long Rest, 16 hours must pass before another.**

**Spending Hit Dice is the whole mid-day economy.** Roll one, add the Constitution modifier, regain
that much (minimum 1), and decide after each roll whether to spend another. They are the only HP a
character recovers without magic between Long Rests, and they do not come back until a Long Rest.

```
python3 tools/state.py --campaign X hit-dice spend thorne 2
python3 tools/roll.py expr "2d10+4" --campaign X --label "Hit Dice on a Short Rest"
python3 tools/state.py --campaign X heal thorne 15
python3 tools/state.py --campaign X short-rest
python3 tools/state.py --campaign X long-rest
```

`short-rest` says what a Short Rest does **not** restore, because the thing most often got wrong is
assuming spell slots come back.

**Source:** SRD 5.2, "Rules Glossary" → "Short Rest", "Long Rest".

### What a Long Rest means for a solo campaign

A full Long Rest wipes the attrition clock: full HP, all Hit Dice, all slots, one Exhaustion level
gone. That is generous, and it means **the pressure in this game lives inside the day, not across
days**. If a campaign feels toothless, the lever is not harsher encounters — it is denying the Long
Rest: a dungeon that cannot be safely slept in, a pursuit, a deadline, a place where 8 hours is not
available.

The published "gritty realism" variant (short rest 8 hours, long rest 7 days) is **not SRD
content**. If you want it, write it in `RULES_DELTAS.md` as a house rule and name it as one.

---

## Healing without magic

This game has far less of it than Pathfinder, and the difference matters most at a solo table.

| | |
|---|---|
| **Hit Dice on a Short Rest** | the main one. Finite, and refilled only by a Long Rest |
| **A Long Rest** | everything back |
| **Stabilising someone at 0 HP** | the Help action, **DC 10 Wisdom (Medicine)** |
| **An unhealed Stable creature** | regains 1 HP after **1d4 hours** |
| **Potions** | the only self-administered mid-fight healing most characters have |

**There is no Treat Wounds here.** No skill check that restores hit points out of combat, no
repeatable hour-by-hour healing. A character who has spent their Hit Dice has one option, and it is
to sleep. Say that early, because a player coming from Pathfinder will plan as though Medicine
heals.

A character at 0 HP alone cannot stabilise themselves, and the DC 10 Medicine check needs somebody
else's hands. This is the mechanical reason `03-difficulty-and-solo-levers.md` treats an ally as
the primary lever rather than a nicety.

---

## Downtime

### Per day
Lifestyle cost (wretched free to aristocratic 10 gp/day), and one activity: training, crafting,
scribing a scroll, brewing a potion, research, working a job, maintaining a relationship. One
meaningful check, one outcome, one line of fiction.

### Per week — so weeks pass in a few exchanges
1. **Name the span and the lifestyle**, and deduct the cost.
2. **One activity per week**, with one check.
3. **One complication or one piece of news** per week — roll on the rumour table in
   `16-random-tables.md` or ask the oracle.
4. **Advance clocks** that tick on time rather than on events (`CLOCKS.md`).
5. **One scene** out of the whole span: the moment that mattered. Narrate that; summarise the rest.

```
python3 tools/state.py --campaign X advance-time "3 weeks"
python3 tools/state.py --campaign X gold spend "21gp"
python3 tools/state.py --campaign X clock advance "the tide in the sump" 2
```

**Crafting** nonmagical items, **brewing Potions of Healing**, **scribing Spell Scrolls** and
**crafting magic items** all have published procedures in the SRD's "Equipment" and "Magic Items"
chapters — look them up rather than estimating, and cite them when you quote a cost or a time.

**Earn Income has no 2024 equivalent in open content.** If the campaign needs a downtime wage,
invent one, record it in `RULES_DELTAS.md`, and keep it modest: a reliable income removes the only
resource pressure the early game has.
