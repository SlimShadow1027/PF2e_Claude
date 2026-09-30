# 22 — Session flow: opening, pacing, closing

How a session starts and ends does more for the feel of a campaign than any single rule, and both
are easy to get wrong when there is no table full of people to set the rhythm.

---

## Opening: the trailer

Start each session after the first with a short **"previously on"**, written **in the campaign's
voice** rather than as a status report.

- **100 to 150 words.**
- **Present tense.**
- **Ends on the decision or the danger** the player was facing when you stopped.
- Built from the **last session log**, not from the raw checkpoint. The log is prose about what
  mattered; the checkpoint is a state dump.

### Two hard rules

1. **It contains only what the player's characters actually know.** Nothing from `gm-private/`.
   Nothing from an off-screen turn they have not encountered. Nothing marked **GM-side truth** in
   `CANON.md`. Nothing from a world chronicle entry dated after the campaign's current date.
2. **The mechanical recap stays separate.** After the trailer, give the plain-facts version — HP,
   conditions with durations, resources, location, in-world date, what they were about to do — so
   the player gets the fiction and the state **without either contaminating the other.**

A trailer with HP totals in it is a status report with adjectives. A status report with a mood in
it is a trailer that cannot be trusted for numbers. Keep them apart.

### Example shape

> **Previously.** The water in the crypt is at your knees and still rising. The lever is three
> squares off, past the second ghoul, and the porter you came down here to find has stopped
> answering. Somewhere above, the bell you were told not to ring has rung twice. You have one
> action left and a choice about what to spend it on.
>
> ---
>
> **Where we actually are.** Kaelen: 4 / 22 HP, frightened 2 (2 rounds), 0 Hero Points, one
> lesser healing potion. Round 3 of the crypt landing fight, your turn, one action remaining,
> reaction available. 1 Abadius 4725 AR, 16:00. You were about to decide between the lever and
> the potion.

### The cold open

Offer it as an alternative: **skip the recap and drop straight into a scene already in motion**,
with the recap available on `recap` if the player wants it.

A cold open works best when the last session ended cleanly and the next thing is a new place or a
new person. It works badly mid-combat, where the player needs the numbers before they need the
mood.

Which one is the default goes in `PLAYER_PREFS.md`.

---

## Pacing: the scene budget

Intake asks roughly how long a sitting runs, and records a **target scene count** in
`PLAYER_PREFS.md`. Track scenes as they pass:

```
python3 tools/state.py --campaign X session scene
python3 tools/state.py --campaign X get scene_count
```

Then steer with the budget in mind:

- **Aim to reach a natural stopping point** — a resolution, a reveal, or a cliffhanger — near the
  end of the budget, rather than trailing off mid-corridor.
- **At roughly three quarters of the budget, say so out of character, in one line**, and offer the
  choice:

  > Out of character: that is scene five of about seven. Push toward a stopping point, or open
  > something new knowing we will stop mid-thread?

- **Never truncate a scene to hit the budget.** It is a steering aid, not a timer. A fight that
  runs long runs long. The budget only means you do not start a dungeon level with ten minutes
  left.
- **Stopping mid-combat is fine.** Checkpoint the encounter state per `05-checkpoint-protocol.md`
  and resume from it; the tracker restores exactly.
- **Track how the estimate performs and adjust.** If every session runs two scenes over, **the
  budget is wrong, not the session.** Change the number in `PLAYER_PREFS.md` and say you did.

---

## Closing: the session log

On `end session`, in this order:

### 1. Finish or safely suspend the current beat

If mid-combat, get to the end of the current round if that is close, then checkpoint. Do not rush
a resolution to make the ending tidy.

### 2. Write the prose recap

`sessions/NNN-<slug>.md`, from `templates/sessions/_SESSION_TEMPLATE.md`.

**Written for a future session that remembers nothing.** It records:

- **What happened** — prose, past tense, complete enough to reconstruct from.
- **What changed** — mechanically, in the world, and what was added to canon.
- **What is unresolved.**
- **What the player said they wanted to do next.** ← **The single most useful line in the file.**
  Write it in their words.

### 3. Append to `CANON.md`

Everything newly established out loud. Names, dates, relationships, geography, prices. Mark
anything GM-side as **GM-side truth**.

### 4. Update quests, clocks and flag statuses

```
python3 tools/state.py --campaign X quest set "Find the tax collector" active --lead "The Drowned Cat, ask for Harrow"
python3 tools/state.py --campaign X clock advance "Cult's Ritual" 1
```

And move any flag that got set up or paid off in `FLAGS.md`, with a note on what happened.

### 5. Append the one-line dice-fairness summary

```
python3 tools/analyze.py --campaign X --one-line
```

into the session log's fairness section. If the numbers look off, **say so in the session log and
out loud**, not just in the file.

### 6. Take a checkpoint

Which commits and regenerates the dashboard:

```
python3 tools/state.py --campaign X session end
python3 tools/state.py --campaign X checkpoint "session 7: the flooded crypt"
```

### 7. Close with a "next time on…" teaser

One or two sentences. A **teaser, not a plan** — it should not commit the next session to anything,
and it should not contain information the player's characters do not have.

> Next time: the bell rings a third time, and this time somebody is standing under it.

---

## A one-line checklist

Opening: trailer (player-known only, 100–150 words) → plain facts → confirm → play.

Closing: finish the beat → session log → canon → quests, clocks, flags → fairness line →
checkpoint → teaser.
