# Optional Extras

Where the optional features ended up. Everything that was worth adding has been folded into `PROMPT.md`;
what's left below is the short list of things deliberately left out, and the failure modes to watch for
once you're actually playing.

## Folded into `PROMPT.md`

These started life here as optional extras and are now part of the spec:

- **Git as the time machine** — every checkpoint is a commit, so `git log` is the campaign history,
  `git diff` shows what changed between any two moments, and the roll log is committed alongside the
  state it produced, which makes the audit trail tamper-evident rather than merely append-only.
- **Encounter objectives beyond "reduce to 0 HP"** — `system/17-encounter-objectives.md`, a catalogue of
  timers, non-combat win conditions, morale and surrender, shifting terrain, retreat, and escalation.
  Every encounter records its objective, the objective gets telegraphed in the fiction, and the default
  target is that at least half of all fights have a win condition other than killing everything.
- **The reaction obligation** — before resolving any trigger, the GM checks the party's available
  reactions and asks. Forgetting Reactive Strike and Shield Block is the most common way an automated
  GM quietly shortchanges a player, so it's a stated duty with a tracker column behind it.
- **Roll-log analytics** — `tools/analyze.py` and `/dice-audit`, reporting a fairness section (d20 mean,
  chi-square against uniform, and public vs. private rolls as separate subsets) and a play section
  (success rates by skill and save, damage taken per encounter, Dying counts, hit rate by
  multiple-attack-penalty step).
- **The campaign dashboard** — `tools/dashboard.py` and `/dashboard`, a self-contained HTML file
  regenerated at every checkpoint with HP bars, conditions, resources, the live initiative strip,
  inventory with Bulk, quests, clocks, and the tactical map. Read-only, offline, phone-friendly, and it
  respects the transparency mode so it can't leak enemy HP.
- **Between-session world prep** — `system/18-between-session-prep.md` and `/worldprep`, a bounded
  off-screen turn that advances scheduled clocks, decides what factions did with the gap, and leaves a
  prep file in `gm-private/`. Opt-in, schedulable as a Routine, and fenced by hard limits: it never
  touches player state, never resolves anything you'd have had a say in, never advances in-world time on
  its own, and refuses to run while a session is live.
- **The solo oracle** — `system/19-solo-oracle.md`, `tools/oracle.py` and `/oracle`: yes/no questions on
  a published likelihood ladder with "and/but" results, scene checks, meaning tables, and bounded
  quantity rolls. The rule that makes it worth having is that an oracle result is binding on the GM.
- **Player-authored flags** — `system/20-player-flags.md` and a per-campaign `FLAGS.md`: what you want
  the campaign to deliver, with heat and status, read during the boot sequence, aimed at deliberately,
  never delivered literally, and reported on at arc boundaries.
- **A shared world across campaigns** — `system/21-shared-worlds.md` and an optional `worlds/<slug>/`
  layer holding setting material, a dated `CHRONICLE.md`, per-character legacy records, and a `LEGENDS.md`
  for how events are misremembered in-world. Campaign files stay fully separate: writes flow to the world
  only at confirmed promotion points, never during play, nothing live is ever promoted, campaign canon
  wins locally, and reads are date-gated so a prequel or parallel campaign can't be informed — or you
  spoiled — by events later than its own in-world date.
- **Session trailers and the scene budget** — `system/22-session-flow.md`: a 100–150 word "previously on"
  in the campaign's voice containing only what your characters know, with the mechanical recap kept
  separate and a cold open available instead; a target scene count that steers toward a stopping point
  without ever truncating a scene; and a closing routine that writes the log, updates canon, quests,
  clocks and flags, checkpoints, and ends on a teaser.
- **Batched minions** — in the encounter runner: identical creatures three or more levels below the party
  act as a squad with one initiative entry and their attacks rolled in a single call, while each keeps its
  own HP and conditions so area damage and focus fire still work. A speed change, not a math change.
  True minion rules stay optional homebrew.
- **The NPC relationship graph** — `tools/graph.py` builds a Mermaid diagram in `WORLD.md` from structured
  relationship fields on each NPC file, in a player-safe version and a GM version with hidden allegiances.
  Opt-in per campaign, since it earns its place in intrigue play and is noise in a dungeon crawl.

## Probably skip

**Pre-commit dice hashing.** You could have the tool commit a hash of a pre-generated roll sequence and
reveal it later, cryptographically proving no reroll happened. The append-only log plus git commits
already gives you enough, and this adds real friction.

**Full Pathbuilder JSON round-tripping.** Importing a pasted sheet is worth it (it's in the prompt).
Maintaining a bidirectional export against an undocumented format is not.

**Image generation for maps and portraits.** ASCII grids are more useful at the table than pretty
pictures, because the GM can read positions back out of them.

## Things to watch for once you're playing

- **Context loss mid-encounter.** Combat state in chat is the most fragile thing in the system. The
  prompt requires the encounter tracker to serialize into `state.json` so a mid-combat checkpoint
  restores exactly — confirm that actually works before you trust it with a long fight, and ask for
  `encounters/active.md` to be rewritten every round if a fight is going badly for continuity.
- **Difficulty drift.** A GM that wants you to have a good time will quietly get easier. The
  post-encounter difficulty note and the periodic check-in in `03-difficulty-and-solo-levers.md` exist to
  catch that — actually read them.
- **Rules by memory.** If you ever get a rules answer with no source cited, ask for the source. That one
  habit catches most mechanical errors.

---

# Added later: the second ruleset

## What was left out of the D&D side on purpose

- **Half-caster and Warlock spell slot tables.** `dnd5e.py` holds the full-caster progression,
  which covers Bard, Cleric, Druid, Sorcerer and Wizard exactly. Paladin, Ranger and Pact Magic
  are read off their own class tables by the GM. One table that is exactly right for five classes
  is useful; a table that is approximately right for two more is a trap.
- **Multiclass validation.** The tooling stores what it is told. Prerequisites and the
  multiclass-spellcaster slot table are the GM's to look up.
- **The 2014 rules.** Where the two editions differ — exhaustion, surprise, the encounter
  multiplier, where ability score increases live — only the 2024 answer is implemented.
  `system/dnd5e/12-rules-quick-reference.md` ends with the habits most likely to arrive from
  elsewhere, and six that are specifically false in this game.
- **The Bastion system.** Optional 2024 downtime content, and not in SRD 5.2.
- **Any DMG content.** Treasure tables, random hoards and published settings are not open content.
  The framework names each gap rather than reconstructing it — see `DESIGN_NOTES.md`.

## What a cross-system world deliberately will not do

- **Convert a stat block, a sheet or a purse.** `world.py convert` translates *scope* and prints
  what it refuses. Rebuilding a character in the target ruleset from their legacy record is the
  supported path, and the record carries a section saying so.
- **Derive one game's market numbers from the other's.** The gazetteer holds both columns, picked
  independently. A derived number would be a guess wearing a source's clothes.
- **Merge rules text across the licence boundary.** ORC and CC-BY-4.0 material cannot be
  relicensed into each other, so the shared layer holds events and people and no rules text from
  either publisher.

## Things to watch for once you are playing the D&D side

- **The habits that come across from Pathfinder.** In rough order of likelihood: narrating a
  "critical success" on a skill check, treating a natural 20 on a save as special, raising DCs to
  keep up with a levelling party, charging an action for movement, giving everyone a Bonus Action,
  and applying a multiple attack penalty. Five of those six make the game harder than written, and
  four of them make it harder for the player rather than the monsters. The tools catch the ones
  that touch state; nothing catches narration.
- **Massive damage.** It kills with no save and no dying track, which is a sharper edge than
  anything on the Pathfinder side. Announce the rule once at level 1 and then never spring it.
- **The Long Rest wipes the attrition clock.** Full HP, all Hit Dice, all slots, one Exhaustion
  level. If a campaign feels toothless, the lever is denying the rest — a place that cannot be
  safely slept in, a deadline, a pursuit — not harsher encounters.
- **A solo character at 0 HP cannot stabilise themselves.** The DC 10 Wisdom (Medicine) check needs
  someone else's hands. That is the mechanical reason the solo-levers document treats an ally as
  the primary lever in this game rather than a nicety, and it is worth saying out loud before the
  player decides to go alone.
- **Treasure pacing is a convention here, not a table.** If it drifts, say so and fix it in the
  open; there is no published budget to appeal to.
