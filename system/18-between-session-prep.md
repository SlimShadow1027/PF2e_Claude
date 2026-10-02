# 18 — Between-session prep: the world moves while you are away

A world that only changes when the player is looking at it feels like a stage set. An
**off-screen turn** is a bounded pass, run between play sessions, that advances what the world is
doing and leaves prep behind for the next session.

It can run on a schedule as a Claude Code Routine, or on demand when the player types
`worldprep` (or `/worldprep`).

**It is off by default.** `PLAYER_PREFS.md` records whether it is on, at what cadence, and with
what `world_pace`. Pausing or deleting it costs nothing — the framework works identically with it
off.

---

## What an off-screen turn does, in order

### 1. Read

The boot sequence files from `15-continuity-and-context-recovery.md`, plus `CLOCKS.md`,
`npcs/ROSTER.md`, `QUESTS.md`, `FLAGS.md`, and the last session log.

### 2. Advance the clocks

Every clock **marked as ticking with a stated rate** advances by that rate for the gap being
modelled. A clock whose advance is uncertain gets **rolled for, with the real dice tool**, logged
like any other roll and tagged `offscreen`:

```
python3 tools/roll.py check "1d20" --dc 11 --label "Does the Covenant find the second seal?" \
    --tag offscreen --private --campaign X
python3 tools/state.py --campaign X clock advance "Cult's Ritual" 1
```

A clock with no stated rate does not move. `validate.py` warns about a clock marked ticking with
no rate, because that clock will silently never advance.

### 3. Decide what each faction and significant NPC did with the time

**Driven by the goals already written in their files, not by what would be dramatic.** A faction
that lost a fight last session reacts to having lost it: it retrenches, it blames someone, it
asks for help, it changes method. It does not have a convenient new plan because a new plan would
be interesting.

For each: what they did, **because of what**, and what consequence the player will notice.

### 4. Update the roster

NPC statuses, locations and dispositions, where the off-screen turn moved them. Write the change
into `npcs/ROSTER.md` and the NPC's own file.

### 5. Write the prep file

`gm-private/prep/NNN-YYYY-MM-DD.md`, from `templates/gm-private/prep/_PREP_TEMPLATE.md`:

- What moved, and why.
- Consequences the player will notice next session.
- **Three concrete hooks** that could open the next scene.
- **Two or three encounter options** built for the current level, **with objectives attached** —
  `python3 tools/pf2e.py encounter --party-level N --party-size M`, or
  `python3 tools/dnd5e.py encounter --party-level N --party-size M` for a 5.5e campaign.
- Any NPC who is now in a different place or mood.
- **Pending consequences**, held rather than applied.
- **Proposals** needing the player's approval at the top of next session.
- **The world pulse** — one spoiler-free paragraph.

### 6. Append to `CANON.md`

Anything newly true, **marked as GM-side truth not yet known to the player**, so it cannot later
be contradicted but also is not treated as something their character has heard.

### 7. Commit

With a message naming the in-world time that passed:

```
git add -A campaigns/<slug>
git commit -m "off-screen turn 003: nine days pass"
```

---

## Hard limits — this is the part that matters

An off-screen turn is **the world acting, never the player acting.**

- **It never touches player state.** No changes to PC or ally HP, gold, inventory, XP, level,
  conditions, or position. If the world's actions imply a consequence for the player, it goes in
  the prep file as a **pending** consequence, to be resolved in play where the player can respond.
- **It never resolves anything the player would have had a say in.** No off-screen combat
  involving their characters. No decisions made on their behalf. No "you were robbed while you
  slept" resolved as fact.
- **It never advances in-world time on its own.** Time passes when you play. The off-screen turn
  computes what *will have* happened over the gap and holds it until the next session opens.
- **It never writes to the shared world layer.** Promotion to a world chronicle happens only at
  the promotion points in `21-shared-worlds.md`, with the player's confirmation, never from an
  unattended pass.
- **It never contradicts `CANON.md`,** and it never edits an existing canon entry — append only.
- **It never kills a named NPC the player has met** without leaving it as a proposal in the prep
  file, for the player to approve or veto at the top of the next session.
- **It is bounded.** One pass. A stated cap on how many clocks and factions it touches (default
  3, from `PLAYER_PREFS.md`). It stops rather than sprawling into writing the next three sessions.
- **It refuses to run concurrently with play.** Guard on `session_in_progress` in `state.json`
  **and** on uncommitted changes in the campaign folder. If either is set, do nothing and say so.

### The concurrency guard, concretely

Before doing anything else:

```
python3 tools/state.py --campaign <slug> get session_in_progress
git status --porcelain -- campaigns/<slug>
```

If `session_in_progress` is `true`, or `git status` returns any line, **stop**. Print why, change
nothing, and exit. A pass that runs over a live session will fight the session for the same files
and one of them will lose.

### Proving player state was untouched

The pass is verifiable, so verify it. Before and after, compare the player-state fields:

```
python3 tools/state.py --campaign <slug> get pcs   > /tmp/pcs-before.json
python3 tools/state.py --campaign <slug> get party > /tmp/party-before.json
# ... run the pass ...
python3 tools/state.py --campaign <slug> get pcs   > /tmp/pcs-after.json
python3 tools/state.py --campaign <slug> get party > /tmp/party-after.json
diff /tmp/pcs-before.json /tmp/pcs-after.json && diff /tmp/party-before.json /tmp/party-after.json \
  && echo "player state byte-identical"
```

If the diff is not empty, the pass broke its first rule. Revert it —
`git checkout -- campaigns/<slug>` — and say what it tried to change.

---

## `world_pace`

From `PLAYER_PREFS.md`. It scales how much moves in one pass.

| `world_pace` | What one pass does |
|---|---|
| `glacial` | At most one clock moves, by one segment. Nothing else changes. |
| `slow` | One or two clocks; one faction acts; no NPC changes location. |
| `steady` | Every ticking clock advances by its rate; two or three factions act; a couple of NPCs move. |
| `brisk` | As steady, plus one unexpected development the player has not been set up for. |
| `runaway` | As brisk, and a clock filling is allowed to fire off-screen — with its consequence held as pending, not applied. |

Default is `steady`. Even at `runaway`, the hard limits above are absolute.

---

## The world pulse

At the start of the next session, the recap opens with a one-paragraph, **spoiler-free** world
pulse — what the player could plausibly have heard through rumour, gossip, a notice board, or a
friend. The rest stays in `gm-private/`.

The pulse contains only:

- Things a person in the player's location would have heard.
- Things already `public` or `rumor`, never `secret`.
- Nothing from the prep file's proposals or pending consequences.

It reads as news, not as briefing:

> The bells at the low temple have been rung twice out of hours this week and nobody will say
> who by. Grain is up a third. A man came asking after you at the Drowned Cat, paid for a room,
> and did not sleep in it.

Then the mechanical recap, then play.

---

## Running one by hand

```
python3 tools/state.py --campaign <slug> get session_in_progress   # must be false
git status --porcelain -- campaigns/<slug>                          # must be empty
```

Then follow steps 1–7 above. `/worldprep` is the slash command.

---

## Scheduling it as a Routine

This runs in a **fresh session**, so its prompt has to stand alone: it names the campaign slug,
points at this document, and states the hard limits inline rather than relying on memory of a
previous conversation.

### The Routine prompt — copy and paste this

```
Run one off-screen world-prep turn for the campaign `<CAMPAIGN-SLUG>` in this
repository. You are the GM. Do not narrate to a player; nobody is reading this live.

FIRST, the concurrency guard. Run both of these:
  python3 tools/state.py --campaign <CAMPAIGN-SLUG> get session_in_progress
  git status --porcelain -- campaigns/<CAMPAIGN-SLUG>
If session_in_progress is true, or git status prints anything at all, STOP. Change nothing,
say why you stopped, and end the turn. Do not work around it.

THEN read, in this order:
  CLAUDE.md
  system/18-between-session-prep.md   (this procedure, in full)
  system/15-continuity-and-context-recovery.md
  campaigns/<CAMPAIGN-SLUG>/CHECKPOINT.md, state.json, RULES_DELTAS.md, PLAYER_PREFS.md,
    FLAGS.md, CANON.md, CLOCKS.md, QUESTS.md, npcs/ROSTER.md
  the most recent file in campaigns/<CAMPAIGN-SLUG>/sessions/
  the most recent file in campaigns/<CAMPAIGN-SLUG>/gm-private/prep/, if any
Honour the `world_pace` and the per-pass cap in PLAYER_PREFS.md. If off-screen turns are
switched off there, stop and say so.

THEN do one bounded pass:
  1. Advance every clock marked ticking with a stated rate, by that rate, for the gap since the
     last session. Where an advance is uncertain, ROLL FOR IT with
     `python3 tools/roll.py ... --tag offscreen --private --campaign <CAMPAIGN-SLUG>`.
     Never write a number you did not roll.
  2. Decide what each active faction and significant NPC did with the time, driven by the goals
     already in their files rather than by what would be dramatic.
  3. Update npcs/ROSTER.md and the affected NPC files: status, location, disposition.
  4. Write campaigns/<CAMPAIGN-SLUG>/gm-private/prep/NNN-YYYY-MM-DD.md from
     templates/gm-private/prep/_PREP_TEMPLATE.md — what moved and why, consequences the player
     will notice, three concrete hooks, two or three encounter options at the current level with
     objectives attached, NPCs who have moved, pending consequences, proposals needing approval,
     and a one-paragraph spoiler-free world pulse.
  5. Append anything newly true to CANON.md, MARKED AS GM-SIDE TRUTH NOT YET KNOWN TO THE PLAYER.
  6. Run `python3 tools/validate.py --campaign <CAMPAIGN-SLUG>` and fix anything it reports.
  7. Commit with a message naming the in-world time that passed, e.g.
     `off-screen turn 003: nine days pass`. Do not open a pull request.

HARD LIMITS. These are absolute and override anything else in this prompt:
  - NEVER touch player state. No changes to any PC's or ally's HP, gold, inventory, XP, level,
    conditions or position. Prove it: capture `state.py get pcs` and `state.py get party` before
    and after, diff them, and include the diff (which must be empty) in your report.
  - NEVER resolve anything the player would have had a say in. No off-screen combat involving
    their characters, no decisions on their behalf, no "you were robbed while you slept" as fact.
  - NEVER advance in-world time. Do not call `state.py advance-time`. Compute what WILL HAVE
    happened over the gap and hold it for the next session.
  - NEVER write anything under `worlds/`. Promotion happens only at a confirmed promotion point
    with the player present.
  - NEVER contradict CANON.md, and never edit an existing entry — append only.
  - NEVER kill a named NPC the player has met. Leave it as a proposal in the prep file.
  - ONE pass, within the cap in PLAYER_PREFS.md. Do not write the next three sessions.
  - Everything you write that the player should not know goes under gm-private/.

FINALLY report: which clocks moved and by how much, which factions acted and why, which NPCs
changed, the empty player-state diff, the path to the prep file, and the commit sha.
```

### Setting it up, pausing it, deleting it

Create it with the `create_trigger` tool (a Claude Code **Routine**), with
`create_new_session_on_fire` set so each firing starts from a clean slate, and the prompt above
with `<CAMPAIGN-SLUG>` filled in. A weekly cadence suits a weekly game; "between sessions" means
running it by hand with `/worldprep` instead.

- **Pause it:** `update_trigger` with `enabled=false`. It stays stored and fires nothing.
- **Delete it:** `delete_trigger` with its trigger id. `list_triggers` finds the id.
- **Fire it once, now:** `fire_trigger`.

**Pausing costs nothing.** Every off-screen turn's output lives in `gm-private/prep/` and in
clock positions; with the Routine off, the clocks simply advance in play instead, and the prep
files stop appearing. Nothing else in the framework depends on it.
