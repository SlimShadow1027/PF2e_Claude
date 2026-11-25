# Rules deltas — Stranger in a Strange Land

Every variant rule, house rule and difficulty lever in force, with its effect. Nothing here
is assumed; each line was chosen explicitly. Changing a line changes play from that point
forward and is never applied retroactively.

- **Difficulty preset in force:** Custom: "Demigod". Between Story and Standard, with risk rising by level.
- **Last changed:** 2026-11-25
- **Status:** **PROPOSED.** Written from the intake answers and awaiting the player's
  confirmation. Lines marked ★ are the GM's recommendations, which the player has not yet
  picked.

## Official PF2e variant rules

Each of these is a published GM Core variant. `off` unless the player said yes.

| Lever | Setting | Effect | Difficulty |
|---|---|---|---|
| Free Archetype | ★ on | A free archetype feat at every even level. The "versatile options" the player asked about. | easier / more versatile |
| Ancestry Paragon | off | A free ancestry feat at every odd level | easier |
| Dual Class | off (offered) | Build as two classes at once. The biggest "demigod" button. | much easier |
| Automatic Bonus Progression | ★ on | Item bonuses come from level, not gear. The stranger arrived with nothing, and this world's magic items are rare and regulated, so the math holds whatever the loot. | smooths gear dependence |
| Proficiency Without Level | off | Would flatten the level gaps that **are** the disparity fantasy | — |
| Gradual Attribute Boosts | off | Boosts spread across levels instead of in lumps | neutral |
| Stamina | off | Free Treat Wounds (below) does the same job more simply | — |
| Mythic / Mythic Callings | off (someday) | A natural late-campaign "demigod" upgrade; revisit around level 11+ | large power spike |
| Elite / Weak adjustments | Weak on native mooks | ±2 to most numbers, ±HP by level | direct difficulty dial |

## Solo and small-table levers

See `system/03-difficulty-and-solo-levers.md` for what each one is for.

### Party shape

| Lever | Setting |
|---|---|
| Party shape | solo at the start; then a sidekick companion; then a full GM-run ally; eventually a small squad the player commands |
| GM-run ally built as a full PC | off at the start; on once the companion grows into one |
| Rotating guest ally per arc | off |

### Math

| Lever | Setting |
|---|---|
| Encounter XP budget scaled for party size | on (`tools/pf2e.py encounter --party-size N`) |
| Weak adjustment as the default for mooks | on, for native rank-and-file |
| Prefer fewer, higher-level enemies over swarms | on, with crowds handled by true minion mode (below) |
| Cap on enemies acting per round | none; minion mode makes crowds fast |
| Bonus reaction for a solo PC | off |
| ★ Once-per-encounter extra action for a solo PC | **on while solo** (**homebrew**). Once per encounter, take a 4th action on your turn. Turns off when a full ally joins. |

### Safety nets

| Lever | Setting |
|---|---|
| Starting Hero Points | 2 |
| Hero Point refresh | per session |
| Hero Point spend converts a critical failure to a failure | off |
| No character death without the player's consent | **on at levels 2–5**; from level 6, off, but every lethal threat is telegraphed hard. Revisit at 11. |
| Auto-stabilise at dying 3, first time per session | on through level 10 |
| Free Treat Wounds between encounters | on, because encounters are frequent |
| Retreat is always available | on |

### Information

| Lever | Setting |
|---|---|
| Recall Knowledge generosity | as written, **except** (★ homebrew) native creatures and lore are unfamiliar: the first Recall Knowledge about a native creature type is **Very Hard (+5 DC)** until the stranger has studied it or fought it once. This serves flag 1. |
| Enemy HP shown as | descriptors |
| GM lists the player's legal actions on their turn | when the player seems stuck |
| GM flags a plan likely to get the character killed | on |
| Big attacks telegraphed a round ahead | on |

## House rules (not official)

Anything here is this table's invention and is marked as such.

| Rule | What it does | Why | Difficulty effect |
|---|---|---|---|
| True minion mode | **on** (below) | The disparity fantasy | much easier against crowds |
| Once-per-encounter extra action | 4th action once per fight, solo only | Solo action economy | easier |
| Unfamiliar native lore | +5 DC on the first Recall Knowledge about a native creature type | The stranger doesn't know this world; serves flag 1 | harder, early only |

### True minion mode

`on`, adopted 2026-11-25 at the player's request. **Homebrew.** Creatures three or more levels
below the party drop to any solid hit instead of tracking hit points. A "solid hit" is any
damaging success: a Strike that hits, or a failed save against a damaging effect. Effect:
fights against crowds resolve far faster and far more in the party's favour, and area damage
and focus fire stop mattering against them. Encounter budgets still count minions at their
listed XP, so budget the real threat with the creatures that are **not** minions.

## Change log

| Date (real) | In-world date | What changed | Why |
|---|---|---|---|
| 2026-11-25 | not yet set | Campaign created with the custom "Demigod" preset; ★ lines proposed, not yet confirmed | intake |
