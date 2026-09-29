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
