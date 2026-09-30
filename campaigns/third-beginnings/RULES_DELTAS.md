# Rules deltas — Third Beginnings

Every variant rule, house rule and difficulty lever in force, with its effect. Nothing here
is assumed; each line was chosen explicitly. Changing a line changes play from that point
forward and is never applied retroactively.

- **Difficulty preset in force:** Standard
- **Last changed:** 2026-09-30

## Official PF2e variant rules

Each of these is a published GM Core variant. `off` unless the player said yes.

| Lever | Setting | Effect | Difficulty |
|---|---|---|---|
| Free Archetype | off | A free archetype feat at every even level | easier / more versatile |
| Ancestry Paragon | **ON** | Two ancestry feats at 1st, then one at every odd level (11 total). Legacy *Gamemastery Guide* p.194 — **not carried into GM Core**. | easier |
| Dual Class | **ON** | Everything from both classes except Hit Points and starting skills; highest proficiency wins. Legacy *Gamemastery Guide* p.192 — **not carried into GM Core**. | much easier — strong for one-PC play |
| Automatic Bonus Progression | off | Item bonuses come from level instead of gear | smooths gear dependence |
| Proficiency Without Level | off | Removes level from proficiency; flattens the math | wider level range stays relevant |
| Gradual Attribute Boosts | off | Boosts spread across levels instead of in lumps | neutral |
| Stamina | off | A stamina pool with easy between-encounter recovery | much easier attrition |
| Mythic / Mythic Callings | **ON from level 1** | *War of Immortals* p.76. Calling + Rewrite Fate at 1st, a mythic feat at every even level, a destiny at 12th. See the dedicated section below — this one changes more than its row suggests. | large power spike |
| Elite / Weak adjustments | off | ±2 to most numbers, ±HP by level | direct difficulty dial |

## Solo and small-table levers

See `system/03-difficulty-and-solo-levers.md` for what each one is for.

### Party shape

| Lever | Setting |
|---|---|
| Party shape | 1 PC + 1 GM-run ally |
| GM-run ally built as a full PC | **on** — Vessa Tarn, in the initiative order, levelling alongside the PC |
| Rotating guest ally per arc | off |

### Math

| Lever | Setting |
|---|---|
| Encounter XP budget scaled for party size | on (`tools/pf2e.py encounter --party-size N`) |
| Weak adjustment as the default for mooks | off |
| Prefer fewer, higher-level enemies over swarms | on |
| Cap on enemies acting per round | none |
| Bonus reaction or once-per-encounter extra action for a solo PC | off |

### Safety nets

| Lever | Setting |
|---|---|
| Starting Hero Points | 1 (PF2e as written) |
| Hero Point refresh | per session (PF2e as written) |
| Hero Point spend converts a critical failure to a failure | off |
| No character death without the player's consent | off |
| Auto-stabilise at dying 3, first time per session | off |
| Free Treat Wounds between encounters | off |
| Retreat is always available | off |

### Information

| Lever | Setting |
|---|---|
| Recall Knowledge generosity | as written |
| Enemy HP shown as | wounded descriptors |
| GM lists the player's legal actions on their turn | off |
| GM flags a plan likely to get the character killed | off |
| Big attacks telegraphed a round ahead | off |

## House rules (not official)

Anything here is this table's invention and is marked as such.

| Rule | What it does | Why | Difficulty effect |
|---|---|---|---|
| **Dual-class grants an extra attribute boost** | A dual-class character gets the key-attribute boost from **both** classes, on top of the normal ten at level 1 — here Wisdom (cleric) **and** Strength (monk), for eleven boosts total. | The player's call, made explicitly: *"Added a boost for monk from the dual class. Leave it."* **This is not in the published text.** GMG p.192 lists what dual-class grants and attribute boosts are not on it; GMG p.193 says a dual-class character gets ability boosts *"only once per level, since both classes would provide the same benefit."* Recorded here so it is a known house rule rather than an unnoticed error. | Str 18 instead of 16 at level 1: +1 to Athletics, every unarmed attack, damage, Monk class DC and both Bulk limits |
| **Five bonus skill feats at level 1** | Hefty Hauler, Titan Wrestler, Combat Climber, Underwater Marauder, Quick Jump — granted outright, not paid for. | Pathbuilder records them as "Awarded Feats"; there is no published variant that grants them. Kept because they are the character's concept, and because four of the five are load-bearing in a flooded dungeon. *(Quick Jump is also the Martial Disciple background feat, so it is duplicated on the sheet; it counts once.)* | noticeably easier in exploration and Athletics-based combat manoeuvres |
| **"Skill Paragon"** | Pathbuilder option granting an extra skill feat (here: Assurance). | Not a published variant under any name found on Archives of Nethys. Pathbuilder's own. | minor |
| **Starting expedition kit granted on top of the 15 gp** | A healer's toolkit, 100 ft of rope, climbing kit, grappling hook, hooded lantern and six pints of oil, five torches, flint and steel, chalk, ten pitons, a crowbar, two weeks of rations, waterskin, bedroll, two sacks and a backpack. **9 gp 6 cp** of gear at Player Core prices, itemised in the character sheet. | Player Core gives 15 gp at level 1. Breastplate (8 gp) and a steel shield (2 gp) eat 10 of it, leaving 5 gp — and a healer's toolkit alone is 5 gp. By the book the character descends into a lightless flooded cave with no rope, no light and no food, *or* with no ability to Treat Wounds. Anyone hired to go down a hole would be outfitted, so they are. | easier attrition (Treat Wounds becomes available from session 1) and removes a class of pointless failure |
| **A third language** | Common, Varisian **and** Shoanti. | Human grants Common + one language + Intelligence modifier, and Int 10 means **two** languages, not three. The third is granted because the player asked for it and the power difference is negligible — but it wants a reason in the fiction, and a Nidalese newcomer who speaks Shoanti is a question an NPC will eventually ask. | none mechanically |
| **Deadly Simplicity applies to *flooded river*** | The flooded river unarmed attack from Flood Stance is treated as Irori's favored weapon for Deadly Simplicity, so it deals **1d10** instead of 1d8. | Deadly Simplicity reads *"when you are wielding your deity's favored weapon, increase the damage die size of **that weapon**."* Irori's favored weapon is **fist**; flooded river is a different unarmed attack, so by the strict text it would **not** be upgraded. The player chose the generous reading knowingly. | +1 damage die step on the character's only Strike while in stance |

### True minion mode

`off`. **Homebrew.** Creatures three or more levels below the party drop to any solid hit
instead of tracking hit points. Effect: fights against crowds resolve far faster and far
more in the party's favour; area damage and focus fire stop mattering. Batched squads
(`system/06-encounter-runner.md`) are the default instead, because batching is a speed
change and not a math change.

## Change log

| Date (real) | In-world date | What changed | Why |
|---|---|---|---|
| 2026-09-30 | 1 Abadius 4725 AR | Campaign created with the Standard preset | intake |
| 2026-09-30 | 1 Abadius 4725 AR | Party shape set to 1 PC + 1 GM-run ally | intake block 7 |
| 2026-09-30 | 1 Abadius 4725 AR | Dual Class, Ancestry Paragon and Mythic turned on; five bonus skill feats and "Skill Paragon" accepted | character import — the player kept all four on being shown what each one is and where it comes from |
| 2026-09-30 | 1 Abadius 4725 AR | House rule: dual-class grants an extra key-attribute boost | the player's explicit ruling on the one arithmetic discrepancy in the imported sheet |
| 2026-09-30 | 1 Abadius 4725 AR | House rule: Deadly Simplicity upgrades flooded river to 1d10 | the player chose the generous reading over the strict text |
| 2026-09-30 | 1 Abadius 4725 AR | House rule: starting expedition kit (9 gp 6 cp) granted on top of the 15 gp | the by-the-book alternative was a healer with no toolkit or an expedition with no light |
| 2026-09-30 | 1 Abadius 4725 AR | House rule: a third language (Shoanti) | requested; no mechanical effect |


---

## Mythic, and what it changes about this framework

*War of Immortals* p.76-84, read from <https://2e.aonprd.com/Rules.aspx?ID=3320>. Mythic is on
from level 1, which is earlier than the book expects — it describes mythic power as *granted by a
deity, gained by slaying a mythic monster or completing a mythic deed*. Three of its rules
override things this framework otherwise assumes, so they are written out here rather than left
to be discovered mid-fight.

### 1. Mythic Points replace Hero Points entirely

> *"Each mythic character starts the session with 3 Mythic Points and can have a maximum of 3
> Mythic Points at any time. **If you have Mythic Points, you do not gain Hero Points.**"*

So `hero_points` stays at **0** for this character for as long as they hold a Mythic Point, and
the solo levers in `system/03-difficulty-and-solo-levers.md` that hand out extra Hero Points are
**inert**. Three Mythic Points a session is a larger and more flexible budget than one Hero
Point, and it refreshes per session the same way.

**Recovering them mid-session:** slaying a mythic opponent (2 to the killer, 1 to everyone else),
completing a mythic deed (3 to each), or **acting in line with the Calling's edicts (1)** — which,
for Sage's Calling, means *"seek out lost knowledge in dangerous or forgotten places."*

### 2. Mythic proficiency is enormous, and it is opt-in

> *"Your proficiency bonus when using mythic proficiency is 10 plus your level."*

At level 1 that is **+11** where trained is +3. It is a step above legendary and ignores
proficiency prerequisites outright. It applies **only when an ability says so** and almost always
costs a Mythic Point. In practice this character can, three times a session, simply succeed at
something a level-1 character cannot attempt.

### 3. Mythic characters do not die at dying 4

> *"When a mythic character's dying value would reach an amount sufficient to kill them (usually
> 4), they instead increase their doomed value by 1 and stabilize at 0 Hit Points. A mythic
> character doesn't permanently die until their doomed value reaches 4."*

**This largely solves the solo death spiral on its own**, which is the problem
`system/03-difficulty-and-solo-levers.md` exists to manage. Combined with lethality 2
(telegraphed and avoidable) and a GM-run ally who can Administer First Aid, the character is very
hard to kill by accident. The safety-net levers below are therefore left **off** — they would be
stacking a third layer on two that already hold.

`tools/state.py` tracks dying and doomed natively; the substitution at dying 4 is applied by the
GM and noted in the log when it happens.

### 4. What this does to encounter building

> *"Mythic power doesn't change a creature or character's effective level, but it does make them
> more powerful than a creature of the same level."* — War of Immortals p.84

The published XP budget has no mythic column. Combined with dual-class, ancestry paragon and five
bonus feats, **the party of two fights meaningfully above its level**. The working assumption for
this campaign, to be corrected by `encounters/history.md` rather than by guesswork:

- Build to the **severe** budget where the book would say moderate.
- Check the pattern every three sessions per the difficulty check-in, not after one bad night.
- If the numbers say it is still too easy, the honest next step is the **Elite adjustment**
  (+2 to most numbers, +HP by level — `python3 tools/pf2e.py tables adjustments`), applied and
  recorded here, rather than quietly adding enemies.
