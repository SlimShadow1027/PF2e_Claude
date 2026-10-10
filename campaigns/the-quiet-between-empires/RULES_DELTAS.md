# Rules deltas — The Quiet Between Empires

Every variant rule, house rule and difficulty lever in force, with its effect. Nothing here
is assumed; each line was chosen explicitly. Changing a line changes play from that point
forward and is never applied retroactively.

- **Difficulty preset in force:** Standard
- **Encounter threat target:** **severe as standard, extreme at story beats** — raised from the
  `Standard` preset's moderate/severe because the variant stack makes moderate meaningless.
  `extreme` is the top tier `pf2e.py` computes; above it there is no published budget.
- **Lethality agreed at intake:** death is on the table if the player pushes a bad situation
- **Last changed:** 2026-10-06

## Official PF2e variant rules

Each of these is a published GM Core variant. `off` unless the player said yes.

| Lever | Setting | Effect | Difficulty |
|---|---|---|---|
| Free Archetype | **on** | A free archetype feat at every even level | easier / more versatile |
| Ancestry Paragon | **on** | A free ancestry feat at every odd level | easier |
| Dual Class | **on** | Build as two classes at once | much easier — strong for one-PC play |
| Automatic Bonus Progression | **on** | Item bonuses come from level instead of gear | smooths gear dependence |
| Proficiency Without Level | off | Removes level from proficiency; flattens the math | wider level range stays relevant |
| Gradual Attribute Boosts | **on** | Boosts spread across levels instead of in lumps | neutral |
| Stamina | off | A stamina pool with easy between-encounter recovery | much easier attrition |
| Mythic / Mythic Callings | **on from level 2 or 3** — Calling + Rewrite Fate, 3 points/session; mythic monster templates from the same point | Mythic destinies and mythic points | large power spike |
| Elite / Weak adjustments | **on** — Elite on significant enemies | ±2 to most numbers, ±HP by level | direct difficulty dial |

## Solo and small-table levers

See `system/03-difficulty-and-solo-levers.md` for what each one is for.

### Party shape

| Lever | Setting |
|---|---|
| Party shape | 1 PC + 1 GM-run sidekick (simplified companion, in the initiative order) |
| GM-run ally built as a full PC | off |
| Rotating guest ally per arc | off |

### Math

| Lever | Setting |
|---|---|
| Encounter XP budget scaled for party size | on (`tools/pf2e.py encounter --party-size N`) |
| Weak adjustment as the default for mooks | on for groups of three or more |
| Prefer fewer, higher-level enemies over swarms | **biased ~65/35 toward fewer** — not absolute |
| Cap on enemies acting per round | **soft cap: 2.5 × allies initiative entries** (see House rules) |
| Bonus reaction or once-per-encounter extra action for a solo PC | off — replaced by the **Versatile Action** house rule below |

### Safety nets

| Lever | Setting |
|---|---|
| Starting Hero Points | **1** (PF2e as written — below the Standard preset's 2) |
| Hero Point refresh | per session (PF2e as written) |
| Hero Point spend converts a critical failure to a failure | off (as written) |
| No character death without the player's consent | off — consistent with lethality 3 |
| Auto-stabilise at dying 3, first time per session | **on** — **homebrew**; the one net kept, because solo play has nobody to Administer First Aid |
| Free Treat Wounds between encounters | off — Treat Wounds still offered at its published time cost |
| Retreat is always available | **on** — lethality 3 only means something if not pushing is a real option |

### Information

| Lever | Setting |
|---|---|
| Recall Knowledge generosity | as written — one action, generous on a success |
| Enemy HP shown as | wounded descriptors — matches `standard` transparency |
| GM lists the player's legal actions on their turn | **replaced by the tactical-posture offer** — see below |
| GM flags a plan likely to get the character killed | **on** — one out-of-character line before the action is spent |
| Big attacks telegraphed a round ahead | **on** — kept at any lethality; an unannounced save-or-die is a coin flip, not difficulty |

## House rules (not official)

Anything here is this table's invention and is marked as such.

| Rule | What it does | Why | Difficulty effect |
|---|---|---|---|
| **Versatile Action** | A fourth action each round, usable only as defined below | The player's own long-standing house rule, carried in from their other tables | easier — removes the opening-round setup tax and grants free repositioning |
| **Crowd soft cap** | At most 2.5 × (number of allies) enemy initiative entries | Protects the action economy, which the XP budget does not | easier against crowds |

### The Versatile Action

**Homebrew.** One extra action per round. It may be spent on:

- **Any basic action except Strike and Ready** — including **Stride**. Interact, Seek, Take Cover,
  Raise a Shield, Point Out, Sense Motive, Leap, Crawl, Step, Release and Grab an Edge all qualify.
- **Single-action feature actions that deal no damage** — Rage, entering a stance, Sustain a Spell,
  Hunt Prey, Command an Animal and the like.

It may **not** be spent on:

- **Strike** or **Ready**, by definition.
- **Skill actions** — Trip, Grapple, Shove, Disarm, Demoralize, Feint, Recall Knowledge. Settled
  explicitly at intake: the Versatile Action is for movement, setup and utility, not for debuffs.
  (Command an Animal is the one skill-adjacent exception the player named, and it stands.)
- Anything taking **more than one action**, or anything that **deals damage**.

**What it does to play, recorded so it is not a surprise later:** the free Stride is the large part.
It means disengaging and re-engaging every round at no action cost, so a melee-only enemy that has
to spend its whole turn closing will rarely get to act. Encounters are therefore built for a mobile
character rather than against one — and mine-country supplies rubble, shafts, narrow galleries and
vertical space honestly, as the setting rather than as a counter.

### Tactical postures offered each turn

**Homebrew**, replacing the preset's *list legal actions* lever. Each turn I offer a short set of
**postures** rather than an enumeration of legal actions:

- **Aggressive** — press the advantage.
- **Defensive** — protect yourself or hold ground.
- **Task-focused** — support the sidekick, advance a timed objective, or retreat.

Plus **reminders of features you have not been using** — which matters on a dual-class sheet with
free archetype and ancestry paragon, where unused abilities are the likeliest failure mode.

This is a posture menu, not a solve: it never names the optimal line and never makes the decision.

### Crowd handling

1. **Soft cap:** 2.5 × allies initiative entries. At 1 PC + 1 sidekick that is **5**.
2. **Every body counts as 1** toward the cap — mooks and troops included. The published XP table
   (GM Core Table 10-2: level−4 = 10 XP against level+0 = 40) already prices a mook at a quarter,
   so discounting it a second time in the cap would double-count.
3. **Above the cap**, the surplus arrive **Weak** (Monster Core p.6, cited) and **batched into one
   initiative entry** (`system/06-encounter-runner.md`) — a speed change, not a math change.
4. **A troop is one entry** but occupies 16 squares in four contiguous segments, is immune to
   non-damaging single-target effects, and takes area damage per segment. NPC Core p.231.
5. **Bias, not a rule:** roughly **65/35** in favour of fewer, higher-level enemies over crowds.

### Note on the stacked variants — not a house rule, a consequence

Free Archetype + Dual Class + Automatic Bonus Progression are all **on**. Together they put one
character well above the power level the published encounter budget assumes.

- **Encounters are built above the normal budget for the party level as standard.** Building to
  the budget would produce fights that cannot threaten this character, which would quietly cancel
  the lethality 3 the player asked for. `tools/pf2e.py encounter --party-size 2` is the floor, not
  the answer.
- **It does not fix the action economy.** Dual Class grants two classes, not a second turn — three
  actions a round still. So the sidekick, *prefer fewer higher-level enemies*, and the reaction
  discipline all still carry their weight. Durability went up; the action-economy problem did not
  move.
- **ABP decouples the character's math from treasure.** Found gear is now flavour, capability and
  ruin-tech rather than the thing keeping the numbers on curve — which suits a sandbox where
  treasure is not placed on a story schedule, and means a dry stretch cannot break the build.
- **Revisit point:** if fights start feeling flat, the dial to move is the encounter threat target
  or the preset, not these three. Say `dial it up`.

### True minion mode

**on.** **Homebrew.** Creatures three or more levels below the party drop to any solid hit
instead of tracking hit points. Effect: fights against crowds resolve far faster and far
more in the party's favour; area damage and focus fire stop mattering. Batched squads
(`system/06-encounter-runner.md`) are the default instead, because batching is a speed
change and not a math change.

## Change log

| Date (real) | In-world date | What changed | Why |
|---|---|---|---|
| 2026-10-06 | 18 Arodus -1000 AR | Campaign created with the Standard preset | intake |
| 2026-10-08 | 18 Arodus -1000 AR | Party shape set to 1 PC + 1 sidekick | intake, Block 7 |
| 2026-10-08 | 18 Arodus -1000 AR | Six levers corrected to match the `Standard` table in system/03 — Hero Points 1→2, weak-on-mooks off→on for 3+, retreat off→on, list-actions off→when stuck, flag-fatal-plans off→on, telegraph off→on | the scaffold's neutral defaults did not match the preset they were labelled with |
| 2026-10-10 | 18 Arodus -1000 AR | Era moved to -1000 AR, the Mushfens, late summer | player revision after pitch selection |
| 2026-10-10 | 18 Arodus -1000 AR | Official variants set: Free Archetype **on**, Dual Class **on**, Automatic Bonus Progression **on**, Proficiency Without Level off | lever-by-lever walkthrough at the player's request |
| 2026-10-10 | 18 Arodus -1000 AR | Ancestry Paragon **on**, Gradual Attribute Boosts **on**, Stamina off | lever walkthrough |
| 2026-10-10 | 18 Arodus -1000 AR | Mythic requested **on**; held pending — no mythic rules or source exist in this repo | charter rules 4 and 5 |
| 2026-10-10 | 18 Arodus -1000 AR | Mythic deferred to a later level — no mythic rules or `sources` entry in this repo, so every mythic number would be unverified | charter rules 4 and 5 |
| 2026-10-10 | 18 Arodus -1000 AR | Encounter threat target raised to severe standard / extreme at story beats | the variant stack cancels lethality 3 at moderate |
| 2026-10-10 | 18 Arodus -1000 AR | Elite / Weak adjustments **on**; flat ±2 and published HP bands per Monster Core p.6, not a discretionary multiplier | player asked; corrected to the published rule |
| 2026-10-10 | 18 Arodus -1000 AR | Versatile Action adopted (homebrew): one extra action/round, basic actions incl. Stride plus single-action non-damaging feature actions; no Strike, Ready or skill actions | player's house rule, scope settled at intake |
| 2026-10-10 | 18 Arodus -1000 AR | Crowd soft cap 2.5 × allies, every body counting as 1; true minion mode **on**; 65/35 bias toward fewer enemies | player design, with the mook weighting corrected from 0.25 to 1 |
| 2026-10-10 | 18 Arodus -1000 AR | Mythic reinstated for level 2-3 onward, monster templates included — rules verified on Archives of Nethys | the earlier deferral was based on my failure to look it up |
| 2026-10-10 | 18 Arodus -1000 AR | Safety nets: Hero Points **1**, refresh per session, no crit-fail conversion, no death-consent | player chose the published/harsher value on each |
| 2026-10-10 | 18 Arodus -1000 AR | Auto-stabilise at dying 3 **on** (homebrew); free Treat Wounds off; retreat on; telegraph on | player; the only safety net taken is the one solo play cannot cover itself |
| 2026-10-10 | 18 Arodus -1000 AR | Information levers: Recall Knowledge as written (generous on success), enemy HP as wounded descriptors, fatal-plan flagging on | player |
| 2026-10-10 | 18 Arodus -1000 AR | *List legal actions* replaced by a tactical-posture offer each turn (aggressive / defensive / task-focused) plus unused-feature reminders | player design; supersedes the one-option-per-turn preference carried from Third Beginnings |
| 2026-10-10 | 18 Arodus -1000 AR | All 26 levers settled. Preset label set to `Custom` — the configuration matches no single preset | lever-by-lever walkthrough complete |
| 2026-10-10 | 18 Arodus -1000 AR | Setting relocated from the Mushfens to mountains and dwarven mine-country; premise reworked to a Daedalus labyrinth with the entity as its deliberate author | player revision |
| 2026-10-10 | 18 Arodus -1000 AR | `worlds/varisia/GAZETTEER.md` rows tagged by era so the date gate has something to filter | the file was undated and read in full at every date |
