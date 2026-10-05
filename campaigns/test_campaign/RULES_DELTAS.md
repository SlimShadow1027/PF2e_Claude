# Rules deltas — Test Campaign

Every variant rule, house rule and difficulty lever in force, with its effect. Nothing here
is assumed; each line was chosen explicitly. Changing a line changes play from that point
forward and is never applied retroactively.

- **System:** Dungeons & Dragons 2024 (5.5e)
- **Difficulty preset in force:** Standard
- **Last changed:** 2026-10-05

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
| Elite / Weak adjustments | off | ±2 to most numbers, ±HP by level | direct difficulty dial |

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
| Calendar | generic — SRD 5.2 publishes no calendar; name the setting's in intake, or define one in the world's CALENDAR.md |
| Random encounter frequency | _(this framework's convention: one check per travel day and per watch)_ |
| Morale | _(this framework's convention; see `system/dnd5e/06-encounter-runner.md`)_ |


## Solo and small-table levers

See `system/03-difficulty-and-solo-levers.md` for what each one is for.

### Party shape

| Lever | Setting |
|---|---|
| Party shape | solo PC |
| GM-run ally built as a full PC | off |
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
| 2026-10-05 | 1 Month 1 1 | Campaign created with the Standard preset | intake |
