# Setup Prompt — PF2e Remaster Solo/Small-Table GM Framework

> **How to use this file:** open a **new Claude Code session** in this repository and paste
> everything from `=== BEGIN PROMPT ===` to `=== END PROMPT ===`. That session's only job is to
> **build the framework** — not to start a campaign. Campaign creation happens afterward with the
> kickoff prompts in the Appendix at the bottom of this file.

---

=== BEGIN PROMPT ===

You are setting up a reusable framework for running **Pathfinder Second Edition (Remaster)** tabletop
campaigns, where you are the Game Master and I am the only human player. Build the framework in this
repository. **Do not start a campaign, do not create a character, and do not roll any dice for play
during this session.** Your deliverable is the scaffolding, tooling, and rule documents that future
sessions will use.

Work through the sections below in order. Ask me clarifying questions **only** where a choice would
change the architecture; use your judgment on everything else and note the assumption in
`DESIGN_NOTES.md`. When you are done, show me the file tree and a short "how to start playing" summary.

---

## 0. Hard constraints (these are non-negotiable and must be restated inside the framework docs)

1. **Every die roll is a real roll produced by code.** You never write a die result that did not come
   out of a tool invocation. No estimating, no "narratively appropriate" numbers, no reconstructing a
   roll you meant to make. If you catch yourself about to state a number you did not roll, stop and
   roll it.
2. **Private rolls are rolled, not fudged.** Secret checks (the `secret` trait), enemy saving throws,
   enemy attack rolls where I've asked for mystery, Stealth/Deception/Perception contests, and
   Recall Knowledge are all genuinely rolled with the tool. What changes is only **what I get shown**
   — the number may be withheld and the outcome narrated instead. The roll itself always happens.
3. **Every roll is logged**, public or private, to an append-only audit log so I can verify the whole
   campaign after the fact. The log records the expression, the individual die faces, the modifiers,
   the DC, the degree of success, whether it was shown to me, and a timestamp.
4. **Creature and NPC statistics come from published Pathfinder 2e Remaster material** (Monster Core,
   NPC Core, Player Core / Player Core 2, GM Core, and Adventure Path/Bestiary entries), cited by
   creature name, source, and level. You do not invent stat blocks freehand. When a custom creature is
   needed, either (a) reskin a published creature of the appropriate level and say which one, or
   (b) build it from the GM Core creature-building benchmark tables — and in either case mark it
   clearly as homebrew with its base listed.
5. **Numbers get verified, not remembered.** Any rules table you write into the framework (DCs by
   level, XP budgets, treasure by level, item bonuses, condition effects) must be checked against a
   source before you commit it, and each table carries a `Source:` line. Where you cannot verify a
   value, write `⚠ UNVERIFIED` next to it rather than guessing silently. Prefer Archives of Nethys
   (`2e.aonprd.com`) as the lookup source; if this session has no network access, mark the table
   `⚠ UNVERIFIED — verify before first play` and list it in `DESIGN_NOTES.md` under "to verify".
6. **Campaign-agnostic core, per-campaign subfolders.** Nothing about a specific campaign, character,
   world, or house rule ever lands outside `campaigns/<campaign-slug>/`. The root-level system files
   must work unchanged for a gothic horror one-shot and a 1–20 high-fantasy epic alike.
7. **Every checkpoint is a git commit.** Git is the campaign's time machine: `git log` is its history,
   `git diff` shows exactly what changed between any two moments, and rewinding is a restore rather than
   a bespoke mechanism. Because the roll log is committed alongside the state it produced, the audit
   trail in constraint 3 becomes tamper-evident rather than merely append-only.

---

## 1. Repository layout to create

```
CLAUDE.md                      # auto-loaded GM operating contract (short, high-signal, points at system/)
README.md                      # what this is, how to start a campaign, how to resume
DESIGN_NOTES.md                # your assumptions, open questions, "to verify" list
LICENSE_NOTES.md              # ORC / Paizo Community Use attribution and what this repo does and doesn't copy

system/                        # campaign-agnostic rules of engagement (never campaign-specific)
  00-gm-charter.md
  01-campaign-intake.md
  02-character-creation.md
  03-difficulty-and-solo-levers.md
  04-dice-protocol.md
  05-checkpoint-protocol.md
  06-encounter-runner.md
  07-encounter-building.md
  08-npc-and-bestiary-protocol.md
  09-loot-and-economy.md
  10-downtime-travel-and-rest.md
  11-leveling-up.md
  12-rules-quick-reference.md
  13-table-etiquette-and-safety.md
  14-player-commands.md
  15-continuity-and-context-recovery.md
  16-random-tables.md
  17-encounter-objectives.md
  18-between-session-prep.md

tools/                         # all dice and math live here; nothing is done by mental arithmetic
  roll.py
  pf2e.py
  state.py
  new_campaign.py
  validate.py
  analyze.py
  dashboard.py
  README.md

templates/                     # copied into a new campaign folder by new_campaign.py
  (mirrors the per-campaign layout in section 2, with {{PLACEHOLDER}} fields)

campaigns/
  .gitkeep                     # generated campaigns live here, one folder each

.claude/
  commands/                    # slash commands (see section 16)
```

---

## 2. Per-campaign folder layout

`tools/new_campaign.py "The Ashen Covenant"` creates `campaigns/ashen-covenant/` containing:

```
CAMPAIGN.md          # premise, tone, genre, setting, themes, pitch, the answers from intake
RULES_DELTAS.md      # every variant rule, house rule and difficulty lever chosen, with its effect
PLAYER_PREFS.md      # pacing, verbosity, combat/RP/exploration mix, tactical-hint level, safety lines
state.json           # CANONICAL machine-readable volatile state (see section 3)
CHECKPOINT.md        # human-readable current-state snapshot, rendered from state.json + narrative notes
CANON.md             # append-only ledger of established facts that must never be contradicted
QUESTS.md            # active / dormant / completed quests, leads, and open threads
CLOCKS.md            # progress clocks: faction plans, looming threats, deadlines
TIMELINE.md          # in-world calendar and what happened when
WORLD.md             # gazetteer, factions, travel times, weather, settlement item levels
characters/
  <pc-name>.md       # full PF2e sheet per player character
  <ally-name>.md     # GM-run allies, companions, sidekicks, animal companions, familiars, eidolons
  PARTY.md           # at-a-glance party table: HP, AC, saves, perception, key skills, resources
npcs/
  <npc-name>.md      # one file per significant NPC
  ROSTER.md          # index: name, role, faction, disposition, last seen, status
bestiary/
  <creature>.md      # one file per creature actually used, with citation + tactics
encounters/
  active.md          # live initiative/round tracker (transient, cleared after combat)
  history.md         # what was fought, where, outcome, XP awarded
maps/
  <scene>.md         # ASCII grid tactical maps with coordinates and terrain key
sessions/
  NNN-<slug>.md      # prose recap per session, written at session end
checkpoints/
  NNN-<slug>.md      # immutable snapshots, restorable
logs/
  rolls.jsonl        # append-only audit log of every die roll
  loot.md            # gold and item ledger with treasure-pacing comparison
  dice-audit.md      # latest analytics report over rolls.jsonl
dashboard.html       # generated single-file campaign dashboard (see section 19)
gm-private/
  README.md          # states the convention: I agree not to read this folder
  secrets.md         # twists, hidden NPC agendas, planned reveals
  seeds.md           # planted foreshadowing and where it's meant to pay off
  prep/
    NNN-YYYY-MM-DD.md  # between-session world prep reports (see section 20)
```

**GM-only information:** anything I shouldn't know goes in `gm-private/`, or inside a clearly fenced
`> **GM-ONLY**` block in a shared file. Never print GM-only content into chat unless I explicitly ask
for a spoiler.

---

## 3. State model — one source of truth per kind of fact

This is the most important architectural decision. Split it:

- **`state.json` is canonical for volatile numbers.** Current/max HP, temp HP, conditions with values
  and durations, Hero Points, Focus Points and refocus status, spell slots used per rank, Dying/Wounded,
  gold by coin type, consumable counts, ammunition, item charges, XP, level, in-world date and time,
  clock segments filled, and current location. These are the things that change constantly and that a
  language model drifts on — so they live in exactly one machine-readable place.
- **Markdown files are canonical for prose and for the built character.** Ancestry/background/class
  choices, feats taken, proficiency ranks, spells known, backstory, NPC personality, lore, recaps.
  These change rarely and read better as text.
- **`CHECKPOINT.md` is rendered, never hand-edited.** `tools/state.py render` regenerates it from
  `state.json` plus a short narrative block. If a number in `CHECKPOINT.md` disagrees with
  `state.json`, `state.json` wins and the file is re-rendered.

Give `tools/state.py` a small CLI so updates are atomic and validated rather than done by rewriting
JSON by hand:

```
python3 tools/state.py --campaign ashen-covenant get pcs.kaelen.hp
python3 tools/state.py --campaign ashen-covenant damage kaelen 12
python3 tools/state.py --campaign ashen-covenant heal kaelen 8
python3 tools/state.py --campaign ashen-covenant condition add kaelen frightened 2
python3 tools/state.py --campaign ashen-covenant condition tick kaelen        # end-of-turn durations
python3 tools/state.py --campaign ashen-covenant gold add 42gp 3sp
python3 tools/state.py --campaign ashen-covenant item add "Healing Potion (Lesser)" 2
python3 tools/state.py --campaign ashen-covenant hero spend kaelen
python3 tools/state.py --campaign ashen-covenant clock advance "Cult's Ritual" 1
python3 tools/state.py --campaign ashen-covenant advance-time "4 hours"
python3 tools/state.py --campaign ashen-covenant render          # rewrite CHECKPOINT.md
python3 tools/state.py --campaign ashen-covenant checkpoint "Escaped the flooded crypt"
python3 tools/state.py --campaign ashen-covenant restore 007     # roll back to a snapshot
```

It must refuse impossible states (HP above max, negative gold, spending a Hero Point you don't have)
and say so rather than silently clamping. Bulk/encumbrance should be computed, and `validate.py`
should flag when the party is over Bulk limits.

---

## 4. `system/04-dice-protocol.md` and `tools/roll.py`

Build a real dice engine using `random.SystemRandom` (or `secrets`). Requirements:

**Notation:** `NdM`, modifiers, `2d20kh1` (keep highest — fortune), `2d20kl1` (keep lowest —
misfortune), reroll flags, exploding not needed. Support damage expressions with critical doubling.

**Suggested CLI:**
```
python3 tools/roll.py check  "1d20+13" --dc 21 --label "Strike (longsword)" --actor Kaelen --map 0
python3 tools/roll.py check  "1d20+9"  --dc 24 --secret --label "Recall Knowledge (Religion)"
python3 tools/roll.py damage "1d8+4" --crit --type slashing --label "Longsword crit"
python3 tools/roll.py save   "1d20+11" --dc 22 --actor "Ghoul B" --private --label "Fortitude vs Fireball"
python3 tools/roll.py flat   11 --label "Persistent bleed recovery"
python3 tools/roll.py init   --actors kaelen,ghoul-a,ghoul-b   # rolls each, returns ordered table
python3 tools/roll.py recovery --dying 2
python3 tools/roll.py table  campaigns/x/../system/16-random-tables.md "Urban Rumors"
python3 tools/roll.py fortune "1d20+13" --dc 21 --label "Hero Point reroll"
```

**Degree of success must be computed by the tool, not by you:** critical success at total ≥ DC+10,
success at ≥ DC, failure below DC, critical failure at ≤ DC−10; a natural 20 improves the degree by
one step and a natural 1 worsens it by one step. Print the natural die face separately so the shift is
visible.

**Output format for public rolls** — one compact line, always the same shape:
```
🎲 Kaelen — Strike (longsword): 1d20+13 → [14] +13 = 27 vs AC 21 → SUCCESS
🎲 Kaelen — Longsword damage: 1d8+4 → [6] +4 = 10 slashing
```

**Private/secret rolls** print the full detail to the log but return a redacted line for chat:
```
🎲 (secret) Recall Knowledge (Religion) — rolled, result withheld
```
…and then you narrate the information I actually get based on the real degree of success.

**Transparency modes** (set per campaign in `PLAYER_PREFS.md`, changeable mid-game):
- `glass` — everything shown, including enemy rolls, enemy AC/HP, and DCs.
- `standard` — my rolls and DCs shown; enemy rolls shown as numbers but their AC/HP hidden; `secret`
  trait checks hidden.
- `mystery` — only narration for anything on the enemy side; my own rolls still always shown.

In every mode the audit log records everything, so I can read `logs/rolls.jsonl` afterward and confirm
nothing was invented.

**Also mandate:** one roll per tool call batch is wasteful — support rolling several expressions in a
single invocation (e.g. all four enemies' saves against one Fireball) so combat doesn't crawl.

### `tools/analyze.py` — the roll-log audit

The audit log is only worth keeping if something reads it. Build `tools/analyze.py` to report over
`logs/rolls.jsonl`, writing to `logs/dice-audit.md` and printing a summary:

```
python3 tools/analyze.py --campaign ashen-covenant
python3 tools/analyze.py --campaign ashen-covenant --since session-7 --actor kaelen
python3 tools/analyze.py --campaign ashen-covenant --fairness
```

**Fairness section** (does the framework actually roll straight?):
- Total d20 count, observed mean against the expected 10.5, and the standard error, so I can see whether
  any gap is noise or not. Give the number rather than a verdict dressed as one.
- Face distribution as a histogram, with a chi-square goodness-of-fit result against a uniform d20.
- The same split by **public vs. private rolls**, which is the check that matters: if secret rolls and
  enemy saves drift favorable or unfavorable relative to public ones, that is visible here and nowhere
  else. Report both subsets side by side.
- Longest streaks, and the count of natural 20s and natural 1s against expectation.

**Play section** (what the numbers say about the campaign):
- Mean d20 and success rate per character, and per skill or save, with the sample size next to each so a
  three-roll "weakness" is not presented as a pattern.
- Degree-of-success breakdown: critical success / success / failure / critical failure rates, overall and
  by check type. Which save is actually the weak one, and by how much.
- Combat load: damage taken per encounter, rounds per encounter, how often a fight ended below a quarter
  HP, how many times I reached Dying and at what value.
- Hero Point usage and what it was spent on.
- Attack routines: hit rate at each multiple-attack-penalty step, which tends to show whether third
  attacks are worth taking with the current build.

Add `/dice-audit` as a slash command, and have the end-of-session routine append a one-line fairness
summary to the session log. If the fairness numbers ever look off, say so unprompted — the point of the
log is that neither of us has to take the dice on faith.

---

## 5. `system/01-campaign-intake.md` — the interview

This is the questionnaire that starts a new campaign. Write it as a script you walk me through, **a
few questions at a time, not all at once**, with 3–5 concrete example answers offered for each so I can
pick rather than compose. Offer a "surprise me / you choose" option on every question, and a "roll it"
option that actually rolls on a table in `16-random-tables.md`. Cover at least:

- **Campaign shape:** one-shot, short arc (3–6 sessions), published Adventure Path, sandbox, or long
  campaign to level 20. Expected level range and advancement speed.
- **Genre and tone:** high fantasy, gothic horror, mystery/investigation, political intrigue, war,
  exploration/hexcrawl, dungeon crawl, heist, planar, nautical, weird west, post-apocalyptic, comedic.
  Tone dial from pulpy to grim. Lethality expectation.
- **Setting:** Golarion (and where — Absalom, Ustalav, the Mwangi Expanse, Cheliax, the Mana Wastes,
  Tian Xia…), a lightly-reskinned Golarion, or fully original. Ask which setting assumptions I want
  kept: gods, planes, ancestries, magic prevalence, technology level.
- **Premise and stakes:** what's wrong with the world, who's causing it, what happens if nobody stops it.
- **Protagonist framing:** why is this character (or these characters) the one who acts? Patron,
  obligation, revenge, curiosity, curse, accident.
- **Party structure:** how many characters I control, how many you run, whether allies are full PCs,
  sidekicks, or narrative-only. (Cross-reference section 6.)
- **Content boundaries:** lines (never appears) and veils (happens off-screen). Ask plainly, once, and
  record it in `PLAYER_PREFS.md`.
- **Play preferences:** narration length, whether you offer tactical suggestions, whether you remind me
  of my available actions and feats, whether you name the rules being applied, how much prose vs.
  bullet summary, second person vs. third person, present vs. past tense.
- **Session rhythm:** how long a typical sitting is, whether to aim for a cliffhanger, how aggressively
  to checkpoint.

The intake ends with you writing `CAMPAIGN.md`, `RULES_DELTAS.md`, `PLAYER_PREFS.md`, `WORLD.md`, and a
**one-page pitch for my approval before anything else is generated.** Do not build the world until I
approve the pitch. Offer me 2–3 alternative pitches from the same answers.

---

## 6. `system/02-character-creation.md`

Present character creation as a guided menu, in PF2e Remaster terms, with a "quick build" path
(pick a class, accept sensible defaults, play in 5 minutes), a "guided" path (step-by-step with
explanations), and an "import" path (I paste a sheet from Pathbuilder and you parse it).

Cover the actual build steps: ancestry → heritage → background → class → key ability and four free
attribute boosts → class feature and level-1 feats → skills (class-granted + Intelligence + background)
→ starting gold and gear → derived statistics.

**Then present the rules-variant menu, each with a one-line effect and a difficulty delta:**

| Lever | Effect | Difficulty |
|---|---|---|
| Free Archetype | A free archetype feat at every even level | easier / more versatile |
| Ancestry Paragon | A free ancestry feat at every odd level | easier |
| Dual Class | Build as two classes at once | much easier — strong for one-PC play |
| Automatic Bonus Progression | Item bonuses come from level instead of gear | smooths gear dependence |
| Proficiency Without Level | Removes level from proficiency; flattens the math | wider level range stays relevant |
| Gradual Attribute Boosts | Boosts spread across levels instead of in lumps | neutral |
| Stamina | Adds a stamina pool with easy between-encounter recovery | much easier attrition |
| Mythic / Mythic Callings | Mythic destinies, mythic points | large power spike |
| Elite / Weak creature adjustments | ±2 to most numbers, ±HP by level | direct difficulty dial |

Always state which of these are official PF2e variant rules from GM Core versus your own suggestion,
and don't apply any of them without my explicit yes.

---

## 7. `system/03-difficulty-and-solo-levers.md`

Solo PF2e breaks in specific, predictable ways. Document the failure modes and the fixes.

**The problems to name explicitly:**
- **Action economy.** One PC against four creatures takes four times the incoming attacks and gets one
  turn. Many-weak-enemies encounters are far deadlier solo than the XP budget implies.
- **No role coverage.** No healer means Dying spirals; no one with Thievery means locked doors are walls;
  no one Recalling Knowledge means fighting blind.
- **Focused fire.** Enemies with any tactical sense all target the only target.
- **Death spiral.** Dying/Wounded has no ally to Administer First Aid.
- **Single point of failure.** One failed save can end the campaign, which is a bad story, not a
  challenge.

**The levers to offer, grouped into presets:**

Party-shape levers: solo PC; solo PC plus a GM-run ally built as a full PC; solo PC plus a sidekick
(simplified companion); troupe play where I control 2–4 characters; a rotating "guest" ally per arc.

Math levers: encounter XP budget scaling for party size; Weak adjustment as the default for mooks;
prefer fewer, higher-level enemies over swarms; cap the number of enemies acting per round; give the
solo PC a bonus reaction or a once-per-encounter extra action.

Safety-net levers: starting Hero Points (2–3) with per-scene refresh instead of per-session; Hero Point
spend to convert a critical failure to a failure; "no character death without my consent" — defeat
becomes capture, loss, injury, or a narrative cost instead; auto-stabilize at Dying 3 the first time per
session; a free Treat Wounds between encounters; a "retreat is always available" guarantee.

Information levers: free or generous Recall Knowledge; enemy HP shown as a bar or as vague descriptors
("badly hurt"); you list my legal actions on my turn; you flag when a plan is likely to get me killed
before I commit to it; telegraph big attacks a round ahead.

**Wrap these into four named presets** so I can pick one word instead of twelve toggles:
`Story` (fiction first, combat rarely lethal), `Standard` (PF2e as written, tuned for party size),
`Gritty` (resources matter, retreat is common, death is real), `Nightmare` (no safety nets, Elite
adjustments, full attrition). Each preset is a concrete list of toggle values written into
`RULES_DELTAS.md`. **I can change the preset mid-campaign with one sentence, and you apply it going
forward without retconning.**

Also: a **difficulty check-in** — after each significant encounter, note in `encounters/history.md`
whether it landed as trivial/appropriate/brutal, and every few sessions offer to adjust based on the
pattern rather than on one bad night.

---

## 8. `system/05-checkpoint-protocol.md`

Define precisely when a checkpoint gets written, what it contains, and how to restore one.

**Automatic checkpoint triggers:** end of any combat encounter; level-up; entering or leaving a
settlement; any transaction over a threshold; a major story beat or reveal; before anything that could
kill a character; end of an in-world day; end of session; and every ~45 minutes of real play.
**Manual:** I type `checkpoint`.

**A checkpoint snapshot contains:** the full `state.json` at that moment; a 3–6 sentence "where we are"
paragraph; the immediate situation (location, who's present, what's about to happen); active conditions
and effects with remaining durations; unresolved threads; what the world is doing off-screen (clock
positions); and a "next likely beats" note for you to pick up from.

**Every checkpoint commits.** After writing a snapshot, `git add -A` the campaign folder and commit with
the checkpoint name as the message, e.g. `checkpoint 014: escaped the flooded crypt`. `tools/state.py
checkpoint` should do this itself so it can't be forgotten. The commit includes `state.json`, the
rendered `CHECKPOINT.md`, and the roll-log lines produced since the last checkpoint, which is what makes
the audit trail tamper-evident. Keep the campaign's commits noisy and don't squash them — the history is
the point. If I'm not ready to commit for some reason, say so and continue; never silently skip it.

**Restoring:** `tools/state.py restore NNN` rewinds `state.json` and re-renders `CHECKPOINT.md`, and you
then narrate from the snapshot's situation paragraph. Because each checkpoint is a commit, `git diff`
between two checkpoints answers "what actually changed" precisely, and a restore can fall back to
`git restore` against the checkpoint's commit if the snapshot files are ever inconsistent. Snapshots are immutable — never edit a past one.
Document that rewinding is a legitimate table move I can call at any time ("rewind to before I opened
the door"), and that you should not resist it.

**`CHECKPOINT.md` must be small enough to be cheap to reload** — aim under ~400 lines. Deep history
lives in `sessions/` and `CANON.md`, not in the checkpoint.

---

## 9. `system/06-encounter-runner.md`

Specify the exact combat loop so combat is consistent and fast:

- Initiative table with the roll, the total, and tie-breaks resolved by the rules.
- A per-round tracker: round number, whose turn, actions spent (◆◆◆), multiple attack penalty so far,
  reaction available or used, conditions with durations, persistent damage, temp HP.
- Enemy HP tracked privately unless transparency mode says otherwise; wounded descriptors instead of
  numbers in `standard` and `mystery` modes.
- Per-creature `Tactics:` notes (what this creature wants, what it does first, when it flees) taken from
  the published entry where one exists.
- Positioning matters in PF2e — flanking, cover, reach, area templates, difficult terrain — so maintain
  an **ASCII grid map in `maps/`** for any fight where position matters, with a coordinate system, a
  terrain key, and updated token positions each round. Distances in feet, 5 ft per square.
- **The reaction obligation.** Before resolving *any* trigger — a creature moving out of reach or
  through a threatened square, an incoming attack, a spell being cast within sight, a creature standing
  up from prone — check every party member's available reactions and **ask me before resolving**.
  Reactive Strike, Shield Block, readied actions, and class-specific reactions are worth a large share
  of a character's power, and forgetting to offer them is the most common way an automated GM quietly
  shortchanges the player. A reaction that was spent this round is tracked in the per-round tracker, so
  "you have no reaction available" is a statement you can always back with the tracker.
- **Enemy tactics are played honestly but not omnisciently.** Creatures act on what they can perceive
  and what their published `Tactics:` note says they want. An unintelligent creature does not focus-fire
  optimally; a trained soldier does. State which it is when it matters.
- End-of-turn bookkeeping: tick durations, persistent damage flat checks, sustained spells, recovery
  checks, then re-render state.
- At the end of combat: XP awarded, treasure, conditions that persist, `encounters/history.md` entry,
  and an automatic checkpoint — which per constraint 7 means a git commit.

## 10. `system/07-encounter-building.md`

XP budgets by threat level, per-character adjustment, creature XP by level relative to the party, hazard
XP, and **the solo adjustment guidance from section 7**. Include a `tools/pf2e.py encounter` helper:

```
python3 tools/pf2e.py encounter --party-level 3 --party-size 1 --threat moderate
python3 tools/pf2e.py encounter --party-level 3 --party-size 1 --add "ghoul:2" --add "ghast:3"
```
…which reports the budget, what's been spent, and the resulting threat rating. Verify every table value
against a source and cite it.

**Also add `system/17-encounter-objectives.md`.** A fight whose only victory condition is reducing
everything to 0 HP is a damage race, and solo play turns that repetitive fast — the tactical interest
lives in the objective. Write a catalogue the GM draws from when building any encounter, with at least:

- **Timers** — a ritual completing, a fuse burning, reinforcements arriving in N rounds, a building
  collapsing, rising water.
- **Objectives that aren't the enemy** — reach a lever, rescue or escort someone, destroy an object,
  hold a position for N rounds, recover something and get out.
- **Morale and surrender** — enemies who flee at a wound threshold, who can be intimidated, bribed, or
  talked down, whose leader's death breaks the group. Specify a morale threshold per creature group.
- **Terrain that changes** — a fight on a collapsing bridge, in spreading fire, on a moving vehicle, in
  darkness that shifts, with hazards that can be turned on the enemy.
- **Retreat as a real option** — chase rules, the cost of fleeing, what the enemy does with the ground
  you gave up.
- **Escalation** — a second wave, a creature that transforms at half HP, an ally who turns.

Require that **every encounter entry in `encounters/history.md` names its objective**, and that the GM
states or telegraphs the objective to me in the fiction before or during round 1 — a timer I can't see
is a trap, not a tactical problem. Default guidance: at least half of all combat encounters in a
campaign should have a win condition other than "everything hostile is dead".

## 11. `system/08-npc-and-bestiary-protocol.md`

- **Statblock sourcing rules** per constraint 4 above. Each `bestiary/<creature>.md` opens with
  `Source: Monster Core p.NNN` or `Source: 2e.aonprd.com/Monsters.aspx?ID=NNN`, plus level, traits, and
  full stats in a consistent PF2e block format.
- **Homebrew and reskins** must name the base creature: `Homebrew — reskin of Ghoul (Monster Core, lvl 1)`.
  A reskin changes name, description, and flavor; changing numbers makes it a new creature that must be
  rebuilt from the GM Core benchmark tables, with the tables cited.
- **Significant NPC format:** name, ancestry/class-ish concept, level, role in the story, faction,
  disposition toward each PC on a named scale, goals (public and private), a distinctive voice —
  vocabulary, rhythm, verbal tic — so they sound consistent across sessions, what they know, what they
  want from me, current status (alive/dead/missing/hostile/allied), last seen where and when, and a
  `> **GM-ONLY**` block for secrets.
- **Recurring-cast discipline:** `npcs/ROSTER.md` is the index you re-read before any scene with NPCs,
  so the blacksmith's name and attitude don't drift. Dead NPCs stay in the roster marked dead.
- **Stat blocks for NPCs only when needed** — a shopkeeper needs a personality, not a stat block. Build
  one when combat or a meaningful contest becomes plausible.

## 12. `system/09-loot-and-economy.md`

Treasure by level for the party size in play, item level availability by settlement, the full coin
ledger (pp/gp/sp/cp), Bulk and encumbrance, consumable tracking, item runes and their costs, crafting
and Earn Income, buying and selling rates, and a **treasure-pacing tracker**: `logs/loot.md` compares
awarded value against the expected curve for my level so I neither outpace nor fall behind the math.
Add `python3 tools/pf2e.py treasure --level 5 --party-size 1` to generate a level-appropriate hoard with
a permanent-item/consumable/currency mix.

## 13. `system/10-downtime-travel-and-rest.md`

Exploration activities, travel speeds and overland pace, encounter-check cadence, weather, making camp,
watches, resting and its requirements, Treat Wounds and other healing, Refocus, daily preparations, and
downtime activities with their DCs and earnings. Include a per-day and per-week downtime resolution
procedure so weeks of in-world time can pass in a few exchanges.

## 14. `system/11-leveling-up.md`

A checklist procedure for level-up: HP, attribute boosts at 5/10/15/20, class feats, skill increases,
skill feats, general feats, ancestry feats, proficiency changes, spell slots and new spell ranks, and
the automatic bonus/item expectations for the new level. End by re-deriving every derived number on the
sheet from scratch and diffing against the old values, so errors get caught at level-up rather than
compounding. Then checkpoint.

## 15. `system/12-rules-quick-reference.md`

The cheat sheet you consult instead of recalling from memory. Degrees of success. The three-action
economy, reactions, free actions. Multiple attack penalty (and the agile variant). Level-based DCs.
Simple DCs by proficiency. Rarity DC adjustments. Every condition with its exact mechanical effect.
Death, Dying, Wounded, Doomed, and recovery checks. Flat checks. Cover, concealment, invisibility,
flanking, and off-guard. Basic saves. Persistent damage. Immunity/weakness/resistance ordering. Hero
Points. Item bonus expectations by level. Attack and spell DC math. Grapple and other common actions.
Every table carries a `Source:` line and any unverified value is marked.

## 16. `system/14-player-commands.md`

Define a small vocabulary I can type at any time, and make you honor it without argument:

| I type | You do |
|---|---|
| `checkpoint` | write a checkpoint now |
| `recap` | summarize where we are, what's unresolved, what I was about to do |
| `status` | HP, conditions, resources, gold, current scene |
| `sheet [name]` | print that character's sheet |
| `inventory` | full inventory with Bulk |
| `rewind [to ...]` | undo back to a point; restore a checkpoint if needed |
| `rules: <q>` | answer as a rules question out of character, with the source |
| `ooc: <text>` | out-of-character conversation, no in-fiction response |
| `meta: <text>` | adjust difficulty, tone, pacing, verbosity mid-game |
| `options` | list my legal actions right now, with the relevant modifiers |
| `map` | show or refresh the tactical/area map |
| `who is <name>` | NPC recall from the roster |
| `what do I know about <thing>` | offer the relevant Recall Knowledge check, or recall established facts |
| `montage <goal>` | resolve a stretch of time in summary with a few rolls |
| `dashboard` | regenerate and open the campaign dashboard |
| `worldprep` | run an off-screen turn now and show me the world pulse |
| `dice audit` | run the roll-log analytics and show the fairness and play summary |
| `end session` | write the session log, checkpoint, and give a "next time on…" teaser |

Also make **`.claude/commands/`** slash commands for the ones worth having as one keystroke:
`/checkpoint`, `/recap`, `/status`, `/sheet`, `/levelup`, `/encounter`, `/dashboard`, `/dice-audit`,
`/worldprep`, `/endsession`, `/newcampaign`, `/resume`. Each is a short Markdown file telling you which system doc to follow.

## 17. `system/15-continuity-and-context-recovery.md`

Assume a future session starts with no memory of this one. Define the **boot sequence**:

1. Read `CLAUDE.md`, then the `system/` docs relevant to what's happening.
2. Read `campaigns/<slug>/CHECKPOINT.md`, `state.json`, `RULES_DELTAS.md`, `PLAYER_PREFS.md`.
3. Read `CANON.md`, `QUESTS.md`, `CLOCKS.md`, `npcs/ROSTER.md`.
4. Read the last one or two files in `sessions/`.
5. Read the sheets of characters currently in play, and the bestiary entries for anything on screen.
6. Give me a recap and confirm the current situation **before** narrating anything new.

Also define **anti-drift practice:** append to `CANON.md` whenever a fact is established out loud
(a name, a date, a relationship, a geographic claim); re-read the roster before NPC scenes; never
contradict `CANON.md` — if you need to, ask me for a retcon instead; and when you notice a past
inconsistency, surface it and propose a fix rather than papering over it. `tools/validate.py` should
check for the mechanical classes of drift: HP above max, negative resources, conditions with expired
durations still listed, `CHECKPOINT.md` out of sync with `state.json`, characters referenced in
`state.json` with no sheet file, bestiary entries missing a `Source:` line.

## 18. `system/16-random-tables.md`

Improv tables that `roll.py table` can roll on: NPC names by ancestry and region, NPC quirks and wants,
tavern and settlement details, rumors, weather by climate and season, random urban/wilderness/dungeon
encounters by level, complications for skill-check failures, treasure flavor, dungeon dressing, and a
"what goes wrong" table. Machine-readable enough to roll on — numbered entries under a heading.

## 19. `tools/dashboard.py` — the campaign dashboard

Scrolling terminal history to find current HP mid-combat is the worst part of playing this way. Generate
a **single self-contained HTML file** at `campaigns/<slug>/dashboard.html` from `state.json` plus a few
of the Markdown files, regenerated at every checkpoint (so `tools/state.py checkpoint` calls it, the same
way it makes the git commit).

**What it shows,** in rough priority order:
- **Party panel** — one card per character: HP as a bar with current/max and temp HP, AC, saves,
  Perception, speed, and the conditions currently on them with their values and remaining durations.
  Dying and Wounded get their own prominent treatment, because that is the number needed fastest.
- **Resources** — Hero Points, Focus Points and whether Refocus is available, spell slots used and
  remaining by rank, consumables with counts, ammunition, item charges.
- **Encounter strip** — when a fight is live, the initiative order with the current turn marked, each
  combatant's status, and the round number. Enemy HP shows as the descriptor or the number depending on
  the campaign's transparency mode — the dashboard has to respect that setting, or it leaks.
- **Inventory and money** — carried items with Bulk, the running Bulk total against the limit, and coins
  by denomination.
- **Quests and clocks** — active quests with their next lead, and progress clocks drawn as filled
  segments so a deadline reads at a glance.
- **Scene** — current location, in-world date and time, who is present, and the last checkpoint's
  situation paragraph.
- **Tactical map** — the current ASCII grid from `maps/`, in a monospace block.

**Build requirements:**
- Standard library only, no build step, no network fetches at runtime. Inline the CSS and any JavaScript;
  the file must open correctly from `file://` with no internet connection.
- Read-only. The dashboard reflects state and never writes it — `state.json` stays the single source of
  truth, and every edit goes through `tools/state.py`.
- Works at phone width as well as desktop, since this is the thing I will glance at on a second screen.
- Light and dark themes following the system preference, with an explicit background on `body`.
- A visible "generated at <timestamp> from checkpoint NNN" line, so a stale file is obvious rather than
  quietly misleading.
- Degrade gracefully: a campaign with no live encounter, no map, or no clocks renders the rest without
  empty scaffolding.

**Optional, once the local file works:** publish it as an Artifact so it has a URL openable on any
device, republished to the same URL at each checkpoint. The local file stays the primary output —
publishing is a convenience on top, not the mechanism.

Add `/dashboard` as a slash command that regenerates and opens it.

## 20. `system/18-between-session-prep.md` — the world moves while I'm away

A world that only changes when I'm looking at it feels like a stage set. Define an **off-screen turn**:
a bounded pass, run between play sessions, that advances what the world is doing and leaves prep behind
for the next session. It can be run on a schedule, or on demand when I type `worldprep`.

**What an off-screen turn does, in order:**
1. Read the boot sequence files, plus `CLOCKS.md`, `npcs/ROSTER.md`, `QUESTS.md`, and the last session log.
2. Advance every clock marked as ticking on a schedule by its stated rate, and roll for any whose
   advance is uncertain — with the real dice tool, logged like any other roll, tagged `offscreen`.
3. Decide what each active faction and significant NPC did with that time, driven by the goals already
   written in their files rather than by what would be dramatic. A faction that lost a fight last session
   reacts to having lost it.
4. Update NPC statuses, locations, and dispositions in the roster where the off-screen turn moved them.
5. Write `gm-private/prep/NNN-YYYY-MM-DD.md`: what moved and why, consequences I'll notice next session,
   three concrete hooks that could open the next scene, two or three encounter options built for my
   current level with objectives attached, and any NPC who is now in a different place or mood.
6. Append anything newly true to `CANON.md` **marked as GM-side truth not yet known to me**, so it can't
   later be contradicted but also isn't treated as something my character has heard.
7. Commit, with a message naming the in-world time that passed.

**Hard limits — this is the part that matters.** An off-screen turn is the world acting, never me acting:
- **It never touches player state.** No changes to PC or ally HP, gold, inventory, XP, level, conditions,
  or position. If the world's actions imply a consequence for me, it goes in the prep file as a *pending*
  consequence to be resolved in play, where I get to respond to it.
- **It never resolves anything I would have had a say in.** No off-screen combat involving my characters,
  no decisions made on my behalf, no "you were robbed while you slept" resolved as fact.
- **It never advances in-world time on its own.** Time passes when we play. The off-screen turn
  computes what *will have* happened over the gap and holds it until the next session opens.
- **It never contradicts `CANON.md`,** and it never edits an existing canon entry — append only.
- **It never kills a named NPC I have met** without leaving it as a proposal in the prep file for me to
  approve or veto at the top of the next session.
- **It is bounded.** One pass, a stated cap on how many clocks and factions it touches, and it stops
  rather than sprawling into writing the next three sessions.
- **It refuses to run concurrently with play.** Guard on a `session_in_progress` flag in `state.json`
  and on uncommitted changes in the campaign folder; if either is set, do nothing and say so.

**Opt-in and cadence** live in `PLAYER_PREFS.md`: off by default, with a chosen cadence (weekly, or
between sessions), and a `world_pace` setting from `glacial` to `runaway` that scales how much moves.
At the start of the next session, the recap opens with a one-paragraph, spoiler-free **world pulse** —
what I could plausibly have heard about through rumor — with the rest staying in `gm-private/`.

**Scheduling it.** This runs as a Claude Code Routine firing into a fresh session, so its prompt has to
stand alone: name the campaign slug, point at this document, and state the hard limits inline rather
than relying on memory of a previous conversation. Write the exact Routine prompt into this file as a
copy-paste block, and include the `/worldprep` slash command for running a turn by hand. Tell me how to
set up, pause, and delete the Routine, and make clear that pausing it costs nothing — the framework
works identically with it off.

## 21. `CLAUDE.md` at the repository root

Short and dense — this gets auto-loaded into every session, so it is not the place for full rules. It
should contain: the hard constraints from section 0 restated as blunt rules; the boot sequence; the file
map; and pointers into `system/` by situation ("running combat → `06-encounter-runner.md`"). Keep it
under about 150 lines.

---

## 22. Build order and acceptance criteria

Build in this order so the tools exist before the docs that reference them:
`tools/roll.py` and `tools/state.py` → the rest of `tools/` → `system/` → `templates/` →
`tools/analyze.py` → `tools/dashboard.py` → `.claude/commands/` → `CLAUDE.md` → `README.md` →
`DESIGN_NOTES.md`. Build `analyze.py` and `dashboard.py` last of the tools, once `rolls.jsonl` and
`state.json` have settled into their final shapes — both read those formats, and reworking them twice is
wasted effort.

Before you report done, verify all of the following and show me the evidence:

- [ ] `python3 tools/roll.py check "1d20+5" --dc 15` produces a real roll with a correct degree of success.
- [ ] Rolling `1d20+5` 10,000 times gives a mean near 15.5 and covers faces 1–20 — show the histogram summary.
- [ ] A natural 20 below the DC prints as a one-step upgrade; a natural 1 above it prints as a downgrade.
- [ ] `--secret` redacts the chat line but writes the full detail to `rolls.jsonl`.
- [ ] `python3 tools/new_campaign.py "Test Run"` creates `campaigns/test-run/` with every file populated
      from templates and no unreplaced `{{PLACEHOLDER}}`.
- [ ] `tools/state.py` round-trips: damage, condition add, gold change, render, checkpoint, restore —
      and the restored state matches the pre-change state exactly.
- [ ] `tools/state.py` refuses an impossible state with a clear error.
- [ ] `tools/state.py checkpoint "..."` produces a git commit containing `state.json`, `CHECKPOINT.md`,
      and the roll-log lines since the previous checkpoint — show `git log --stat` for it.
- [ ] `system/17-encounter-objectives.md` exists with at least six objective categories, and
      `encounters/history.md` in the templates has an `Objective:` field.
- [ ] `system/06-encounter-runner.md` states the reaction obligation, and the per-round tracker format
      has a reaction-available column.
- [ ] `python3 tools/pf2e.py encounter --party-level 3 --party-size 1 --threat moderate` reports a budget,
      and every table it uses has a `Source:` line.
- [ ] `python3 tools/validate.py --campaign test-run` passes on a fresh campaign and catches a deliberately
      corrupted state.
- [ ] Feed `analyze.py` a synthetic log of 10,000 fair rolls: it reports a mean near 10.5 and a chi-square
      consistent with uniform. Feed it a deliberately biased log: it flags the bias. Show both runs.
- [ ] `analyze.py` reports public and private rolls as separate subsets.
- [ ] `tools/dashboard.py --campaign test-run` produces a single HTML file that opens from `file://` with
      no network, renders at phone width, and respects the transparency mode for enemy HP.
- [ ] `tools/state.py checkpoint` regenerates the dashboard as well as committing.
- [ ] A dry-run off-screen turn on `test-run` writes a prep file, advances only scheduled clocks, leaves
      every player-state field byte-identical, and refuses to run when `session_in_progress` is set —
      show the diff proving player state is untouched.
- [ ] `system/18-between-session-prep.md` contains a standalone, copy-pasteable Routine prompt.
- [ ] No campaign-specific content exists outside `campaigns/`.
- [ ] Every rules table is either cited or marked `⚠ UNVERIFIED`, and the unverified ones are listed in
      `DESIGN_NOTES.md`.
- [ ] Delete `campaigns/test-run/` when the checks pass, commit everything, and push.

Tools should use only the Python standard library.

Finally, write `DESIGN_NOTES.md` with: your assumptions, the tables still needing verification, anything
you deliberately left simple, and **your own suggestions for what would make this framework better to
run** — you are the one who will have to GM with it.

=== END PROMPT ===

---

## Appendix A — Kickoff prompt for creating a campaign

Paste this in a fresh session once the framework exists:

```
Read CLAUDE.md and system/01-campaign-intake.md, then walk me through creating a new campaign.
Interview me a few questions at a time. When intake is done, give me three one-page pitches and
wait for my pick before generating anything else.
```

## Appendix B — Kickoff prompt for character creation

```
Read CLAUDE.md, system/02-character-creation.md and system/03-difficulty-and-solo-levers.md, plus
campaigns/<slug>/CAMPAIGN.md. Walk me through making my character for this campaign, then propose a
difficulty preset and the party structure you'd recommend for it.
```

## Appendix C — Prompt to resume play

```
Resume campaign <slug>. Run the boot sequence from system/15-continuity-and-context-recovery.md,
give me a recap, confirm the situation, then pick up where we left off.
```

## Appendix D — Prompt to start the first session

```
Read CLAUDE.md and campaigns/<slug>/. Begin session 1. Open on a scene that gives me something to
decide in the first three sentences.
```
