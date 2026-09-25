# Optional Extras

Features that aren't in `PROMPT.md`, with a recommendation on each. Add the ones you want to the prompt
before running it, or ask for them later as add-ons.

## Already folded into `PROMPT.md`

These started life here and are now part of the spec, so you don't need to add them:

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

## Worth considering

**Between-session world prep on a schedule.** A recurring Routine that wakes a session between your play
sessions, advances off-screen clocks, writes what factions did while you were away, and drafts prep for
the next session into `gm-private/`. Makes the world feel like it moves without you. Worth it for a long
campaign, overkill for a one-shot.

**A shared world across campaigns.** A top-level `world/` folder for setting material several campaigns
share, with `campaigns/<slug>/` holding only what that campaign changed. Lets a second campaign happen
in the aftermath of the first — a legacy game where your old character is now a rumor. Slightly
complicates the "nothing outside `campaigns/`" rule, so only add it if you want a persistent setting.

**A solo oracle.** A yes/no-with-complications oracle you can consult directly ("is the gate guarded?"),
plus random-event tables, so you can drive scenes yourself when you want to rather than always asking the
GM. Comes from solo tabletop tradition and fits naturally next to `16-random-tables.md`.

**Player-authored flags.** A short list in `PLAYER_PREFS.md` of what you want to see: "I want to fight my
old mentor", "I want a moral choice with no clean answer", "I want to be genuinely outmatched once".
Gives the GM targets instead of guesses. Pairs well with a per-arc check-in on which flags have paid off.

**Session-start trailer.** A short "previously on" recap in the campaign's voice, generated from the last
session log. Good for a campaign you touch once a week.

**Aggregate mook resolution.** A "fast combat" mode where minions below a level threshold are resolved in
batches rather than individually, to keep a 1-vs-6 fight from taking an hour. Trades tactical precision
for pace.

**NPC relationship graph.** A Mermaid diagram in `WORLD.md` of who owes what to whom, regenerated when
the roster changes. Useful specifically in intrigue campaigns; skip for dungeon crawls.

**Session-length pacing budget.** Target scenes per sitting, with the GM steering toward a cliffhanger as
you approach the end. Helps if your sessions have a natural stopping time.

## Probably skip

**Pre-commit dice hashing.** You could have the tool commit a hash of a pre-generated roll sequence and
reveal it later, cryptographically proving no reroll happened. The append-only log plus git commits
already gives you enough, and this adds real friction.

**Full Pathbuilder JSON round-tripping.** Importing a pasted sheet is worth it (it's in the prompt).
Maintaining a bidirectional export against an undocumented format is not.

**Image generation for maps and portraits.** ASCII grids are more useful at the table than pretty
pictures, because the GM can read positions back out of them.

## Things to watch for once you're playing

- **Context loss mid-encounter.** Combat state in chat is the most fragile thing in the system. If a
  long fight is going badly for continuity, ask for the initiative tracker and HP to be written to
  `encounters/active.md` after every round, not just at the end.
- **Difficulty drift.** A GM that wants you to have a good time will quietly get easier. The
  post-encounter difficulty note and the periodic check-in in `03-difficulty-and-solo-levers.md` exist to
  catch that — actually read them.
- **Rules by memory.** If you ever get a rules answer with no source cited, ask for the source. That one
  habit catches most mechanical errors.
