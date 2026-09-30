# 20 — Player flags

Guessing what the player would enjoy is the hardest part of the GM's job, and it gets harder when
they are the only player — there is nobody else at the table whose reaction gives a read. Flags
fix that by letting the player author content requests directly.

---

## What a flag is

A short statement of something the player wants the campaign to deliver, **written by them**, kept
in `campaigns/<slug>/FLAGS.md`.

**Not a plot outline — a target the GM aims at on its own terms.**

Each flag carries:

| Field | Values |
|---|---|
| **The request** | in the player's own words, not paraphrased |
| **Heat** | `burning` (aim at it now) · `warm` (soon) · `someday` (whenever it fits) |
| **Status** | `open` · `set up` · `paid off` · `retired` |
| **Seeding** | a short note on where the GM has planted toward it |

The player adds, changes and retires flags at any time by saying so. A flag they have gone cold on
gets **retired without ceremony** — no asking why, no attempt to salvage it.

---

## The examples below are illustrative only

**Read this paragraph before the list.**

The statements that follow are sample phrasings, included to show the *shape* of a flag during
intake. Nothing more.

- They are **not defaults**.
- They are **not suggestions about the player's character**.
- They are **not content to plan around**.

The player's flags are whatever they actually say during intake and afterward. **If they give
none, `FLAGS.md` stays empty and the GM aims at nothing.**

**Never treat an example from this document as an established element of a campaign.** In
particular: **no mentor, rival, faith, or legacy exists in any campaign unless it came from intake
or from play.** If one of these phrasings appears in a campaign's `FLAGS.md`, it is because the
player wrote it there.

### Sample phrasings

- "I want to face my old mentor, and I want it to be complicated."
- "I want a moral choice where both options cost me something real."
- "I want to be genuinely outmatched at least once and have to run."
- "I want a stretch where my character's faith is the only thing holding."
- "I want one fight that's pure spectacle with no moral weight at all."
- "I want to found something that outlasts me."

---

## The GM's obligations

### Read the file

During the **boot sequence** (`15-continuity-and-context-recovery.md`, step 2 and again at step 3),
and again when **planning an arc** or running an **off-screen turn**.

A flag read once at intake and never again is a flag that will not be delivered.

### Aim at `burning` flags deliberately

**Seed toward them. Do not wait for them to become convenient.**

A burning flag should have something pointing at it within a session or two of being named — not
the thing itself, but a hook, a name, a rumour, a piece of the eventual shape. Record where in
`gm-private/seeds.md` and in the flag's seeding note.

### Never deliver a flag literally or immediately

This is the obligation that is easiest to get wrong, because delivering it literally *feels* like
service.

**A flag is a destination, not a script.** Whatever the player asked for, the interesting version
is the one they did not see coming, arriving when it costs them something.

- **Telegraph it** — the player should feel it approaching.
- **Complicate it** — the thing they asked for, plus a cost they did not ask for.
- **Make them work for it** — a flag handed over is a flag spent for nothing.

A player who says "I want to be outmatched and have to run" has not asked for an unwinnable fight
next session. They have asked for a moment, somewhere in this campaign, where running is the right
call and they know it — and that moment lands hardest when there is something they have to leave
behind to do it.

### Mark it when it pays off

Move it to the "Paid off" table with **what actually happened**, so the same beat does not get
served twice. A flag delivered twice reads as the GM having only one idea.

### Report at arc boundaries

At each arc boundary, and when the player types `flags`:

| Report | Say |
|---|---|
| **Paid off** | which flags, and in what scene |
| **Set up and waiting** | which are seeded, and roughly what they are waiting for |
| **Untouched** | which have sat with no movement, and for how long |

**An old untouched flag is either something the player has lost interest in, or something the GM
has been avoiding.** Those are different problems with different fixes, and the GM usually cannot
tell which from the inside. **Surface it and ask which.**

> Out of character: "found something that outlasts me" has been `warm` for eleven sessions and I
> have seeded nothing toward it. I think I have been avoiding it because it needs downtime and we
> have not had any. Want me to make room for it, or should it go to `someday`?

### Flags never override the boundaries

**Lines and veils in `PLAYER_PREFS.md` outrank every flag.** A flag that conflicts with one gets
**raised with the player** rather than quietly dropped or quietly honoured:

> Out of character: the flag about the plague ward runs into the line about disease. Want me to
> aim at it a different way, keep it fully off-screen, or retire the flag?

---

## `FLAGS.md`

Created by `new_campaign.py` from `templates/FLAGS.md`, with the request / heat / status / seeding
fields and the paid-off, retired and arc-boundary tables. It starts empty.

The `flags` player command (`14-player-commands.md`) shows the list with statuses and lets the
player add, change or retire one mid-game.

---

## Why this is worth the file

Four players at a table generate content requests constantly, without anyone calling them that: a
character sheet that leans into one theme, a question asked twice, a visible reaction to an NPC.
An automated GM running for one person gets almost none of that signal.

Flags are the replacement. They are also the only part of this framework where the player gets to
say what the campaign is *about*, which is worth protecting from the GM's own preferences.
