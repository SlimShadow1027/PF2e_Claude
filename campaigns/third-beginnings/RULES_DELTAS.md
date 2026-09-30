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
| Ancestry Paragon | off | A free ancestry feat at every odd level | easier |
| Dual Class | off | Build as two classes at once | much easier — strong for one-PC play |
| Automatic Bonus Progression | off | Item bonuses come from level instead of gear | smooths gear dependence |
| Proficiency Without Level | off | Removes level from proficiency; flattens the math | wider level range stays relevant |
| Gradual Attribute Boosts | off | Boosts spread across levels instead of in lumps | neutral |
| Stamina | off | A stamina pool with easy between-encounter recovery | much easier attrition |
| Mythic / Mythic Callings | off | Mythic destinies and mythic points | large power spike |
| Elite / Weak adjustments | off | ±2 to most numbers, ±HP by level | direct difficulty dial |

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
| 2026-09-30 | 1 Abadius 4725 AR | Campaign created with the Standard preset | intake |
