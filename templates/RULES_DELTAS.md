# Rules deltas — {{CAMPAIGN_TITLE}}

Every variant rule, house rule and difficulty lever in force, with its effect. Nothing here
is assumed; each line was chosen explicitly. Changing a line changes play from that point
forward and is never applied retroactively.

- **System:** {{SYSTEM_NAME}}
- **Difficulty preset in force:** {{DIFFICULTY_PRESET}}
- **Last changed:** {{CREATED_DATE}}

> **Delete the section below that does not apply to this campaign's ruleset.** Leaving the other
> game's variant menu in place is how a houserule from the wrong game ends up in force.

## Official PF2e variant rules — *for a `System: pf2e` campaign*

Each of these is a published GM Core variant. `off` unless the player said yes.

| Lever | Setting | Effect | Difficulty |
|---|---|---|---|
| Free Archetype | off | A free archetype feat at every even level | easier / more versatile |
| Ancestry Paragon | off | A free ancestry feat at every odd level | easier |
| Dual Class | off | Build as two classes at once | much easier — strong for one-PC play |
| Automatic Bonus Progression | off | Item bonuses come from level instead of gear | smooths gear dependence |
| Proficiency Without Level | off | Removes level from proficiency; flattens the math | wider level range stays relevant |
| Gradual Attribute Boosts | off | Boosts spread across levels instead of in lumps | neutral |
| Stamina | off | A stamina pool with easy between-encounter recovery | much easier attrition |
| Mythic / Mythic Callings | off | Mythic destinies and mythic points | large power spike |
| Elite / Weak adjustments | {{ADJUSTMENT_DEFAULT}} | ±2 to most numbers, ±HP by level | direct difficulty dial |

## Official D&D 2024 variant rules — *for a `System: dnd5e` campaign*

SRD 5.2 publishes far fewer dials than Pathfinder does, and several things a 2014 table will
reach for are **not open content**. Each row says which it is.

| Lever | Setting | Effect | Published? |
|---|---|---|---|
| Fixed HP on level-up | **on** | Take the class's fixed value instead of rolling | **published** — the player's choice each level |
| Rolled HP on level-up | off | Roll the Hit Die instead | **published** |
| Massive damage | **on** | Damage past 0 meeting the HP maximum kills outright, no save | **published** — turning it *off* is the houserule |
| Death saves in public | **on** | The player sees the counters climb | a transparency choice, not a rule |
| Feats at every even level | off | More feats than the class table gives | **houserule** |
| Critical hit on 19–20 | off | Widens the crit range | **houserule** |
| Flanking / facing | off | Not in SRD 5.2 at all | **houserule** |
| Gritty realism rests | off | Short rest 8 hours, long rest 7 days | **not SRD content** — houserule |
| Milestone levelling | off | Level at arc ends instead of tracking XP | a pacing choice |
| Generous Heroic Inspiration | — | How freely it is awarded | **published** resource, GM-set cadence |

### What this ruleset has no published answer for

Write the campaign's answer here when one is needed, and name it as this campaign's own:

| Gap | This campaign's answer |
|---|---|
| Treasure by level | _(see `system/dnd5e/09-loot-and-economy.md` — pace by tier)_ |
| Downtime income | _(no published rate; invent one and keep it modest)_ |
| Creature adjustment templates | _(no Elite/Weak equivalent; use a different creature or name homebrew)_ |
| Calendar | {{CALENDAR}} |
| Random encounter frequency | _(this framework's convention: one check per travel day and per watch)_ |
| Morale | _(this framework's convention; see `system/dnd5e/06-encounter-runner.md`)_ |


## Solo and small-table levers

See `system/03-difficulty-and-solo-levers.md` for what each one is for.

### Party shape

| Lever | Setting |
|---|---|
| Party shape | {{PARTY_SHAPE}} |
| GM-run ally built as a full PC | {{GM_ALLY}} |
| Rotating guest ally per arc | off |

### Math

| Lever | Setting |
|---|---|
| Encounter XP budget scaled for party size | on (`tools/pf2e.py encounter --party-size N`) |
| Weak adjustment as the default for mooks | {{WEAK_MOOKS}} |
| Prefer fewer, higher-level enemies over swarms | {{FEWER_ENEMIES}} |
| Cap on enemies acting per round | {{ENEMY_CAP}} |
| Bonus reaction or once-per-encounter extra action for a solo PC | off |

### Safety nets

| Lever | Setting |
|---|---|
| Starting Hero Points | {{HERO_POINTS}} |
| Hero Point refresh | {{HERO_REFRESH}} |
| Hero Point spend converts a critical failure to a failure | {{HP_CRIT_FIX}} |
| No character death without the player's consent | {{DEATH_CONSENT}} |
| Auto-stabilise at dying 3, first time per session | {{AUTO_STABILISE}} |
| Free Treat Wounds between encounters | {{FREE_TREAT_WOUNDS}} |
| Retreat is always available | {{RETREAT_GUARANTEE}} |

### Information

| Lever | Setting |
|---|---|
| Recall Knowledge generosity | {{RECALL_GENEROSITY}} |
| Enemy HP shown as | {{ENEMY_HP_DISPLAY}} |
| GM lists the player's legal actions on their turn | {{LIST_ACTIONS}} |
| GM flags a plan likely to get the character killed | {{FLAG_LETHAL_PLANS}} |
| Big attacks telegraphed a round ahead | {{TELEGRAPH}} |

## House rules (not official)

Anything here is this table's invention and is marked as such.

| Rule | What it does | Why | Difficulty effect |
|---|---|---|---|
| _(none yet)_ | | | |

### True minion mode

`off`. **Homebrew.** Creatures three or more levels below the party drop to any solid hit
instead of tracking hit points. Effect: fights against crowds resolve far faster and far
more in the party's favour; area damage and focus fire stop mattering. Batched squads
(`system/06-encounter-runner.md`) are the default instead, because batching is a speed
change and not a math change.

## Change log

| Date (real) | In-world date | What changed | Why |
|---|---|---|---|
| {{CREATED_DATE}} | {{START_DATE}} | Campaign created with the {{DIFFICULTY_PRESET}} preset | intake |
