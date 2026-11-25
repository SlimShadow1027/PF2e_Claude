# Rules deltas — {{CAMPAIGN_TITLE}}

**System: D&D Fifth Edition (2024 rules, SRD 5.2.1).** Every optional rule, house rule and
difficulty lever in force, with its effect. Nothing here is assumed; each line was chosen
explicitly. Changing a line changes play from that point forward and is never applied
retroactively.

- **Difficulty preset in force:** {{DIFFICULTY_PRESET}}
- **Last changed:** {{CREATED_DATE}}

## Rules options

`off` unless the player said yes. Name the book for anything outside the SRD.

| Lever | Setting | Effect | Difficulty |
|---|---|---|---|
| Feats at level 1 from background | on (2024 as written) | Origin feat from the background | as written |
| Multiclassing | off | Levels in a second class | more versatile |
| Starting at a higher level | off | Begin above level 1 | easier start |
| Heroic Inspiration on a natural 20 / for play | off | GM awards Heroic Inspiration beyond the class/species sources | easier |
| Rest variant | as written | Long Rest 8 h, Short Rest 1 h (a gritty or heroic variant changes both) | dial |

## Solo and small-table levers

See `system/03-difficulty-and-solo-levers.md` (the levers there are system-neutral) and
`system/dnd5e/README.md` for the 5e mapping.

### Party shape

| Lever | Setting |
|---|---|
| Party shape | {{PARTY_SHAPE}} |
| GM-run ally built as a full PC | {{GM_ALLY}} |
| Rotating guest ally per arc | off |

### Math

| Lever | Setting |
|---|---|
| Encounter XP budget summed per character | on (`tools/dnd5e.py encounter --party-level N --party-size M`) |
| Use the Low budget as the solo default | {{WEAK_MOOKS}} |
| Prefer fewer, higher-CR enemies over swarms | {{FEWER_ENEMIES}} |
| Cap on enemies acting per round | {{ENEMY_CAP}} |
| Extra action economy for a solo PC (e.g. a free bonus action once per fight) | off |

### Safety nets

| Lever | Setting |
|---|---|
| Heroic Inspiration at start | {{HERO_POINTS}} |
| Heroic Inspiration refresh | {{HERO_REFRESH}} |
| No character death without the player's consent | {{DEATH_CONSENT}} |
| Auto-stabilise on the first 0 HP each session | {{AUTO_STABILISE}} |
| Free Short Rest between encounters | {{FREE_TREAT_WOUNDS}} |
| Retreat is always available | {{RETREAT_GUARANTEE}} |

### Information

| Lever | Setting |
|---|---|
| Lore / Intelligence-check generosity | {{RECALL_GENEROSITY}} |
| Enemy HP shown as | {{ENEMY_HP_DISPLAY}} |
| GM lists the player's options on their turn | {{LIST_ACTIONS}} |
| GM flags a plan likely to get the character killed | {{FLAG_LETHAL_PLANS}} |
| Big attacks telegraphed a round ahead | {{TELEGRAPH}} |

## House rules (not official)

Anything here is this table's invention and is marked as such.

| Rule | What it does | Why | Difficulty effect |
|---|---|---|---|
| _(none yet)_ | | | |

## Change log

| Date (real) | In-world date | What changed | Why |
|---|---|---|---|
| {{CREATED_DATE}} | {{START_DATE}} | Campaign created with the {{DIFFICULTY_PRESET}} preset | intake |
