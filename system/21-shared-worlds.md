# 21 — Shared worlds

**Optional, and off unless a campaign asks for it.** A campaign with `World: none` behaves exactly
as it does otherwise; nothing about this layer becomes mandatory.

> **A world is system-neutral.** Campaigns running either ruleset can be set in the same world, and
> the shared layer records what happened rather than anyone's numbers. Everything in this document
> applies to both. **If a world has campaigns in both games, read
> `23-cross-system-worlds.md` as well** — it covers the one thing this document does not: what
> crosses between the rulesets and what must not. In short: events, people, places, debts and
> reputations cross; levels, DCs, stat blocks and treasure do not.

A shared world lets a second campaign happen in the aftermath of the first: the same continent,
the same factions, and your previous character remembered as a name people invoke. **Campaign
files stay fully separate** — the shared layer is setting material plus a record of what has
already been concluded.

---

## The layout

```
worlds/<world-slug>/
  README.md          # what this world is, which campaigns are set in it, and their date spans
  CHRONICLE.md       # the overarching record: dated significant events, each tagged with its campaign
  characters/
    <name>.md        # one legacy record per character who has played in this world
  GAZETTEER.md       # places, regions, settlements, and their item levels
  FACTIONS.md        # long-lived organisations, their current standing and leadership
  PANTHEON.md        # gods and cosmology (a pointer, for a published setting)
  CALENDAR.md        # calendar, eras, and the current "present day" of the world
  canon.md           # world-level established facts, append-only
  LEGENDS.md         # how past events are now *remembered* in-world, distortions included
  npcs/
    <name>.md        # NPCs who persist beyond one campaign
  gm-private/
    threads.md       # unresolved world-level threads a future campaign could pick up
```

```
python3 tools/world.py init "The Verdant Reach"
```

A campaign declares its world in `CAMPAIGN.md` with a `World:` field naming a `worlds/<slug>`
folder, or `none`:

```
python3 tools/world.py link --campaign ashen-covenant --world verdant-reach --start-date "4712 AR"
```

which writes `World:`, `Era:` and `Start date:` into `CAMPAIGN.md` and adds a row to the world's
README.

---

## The separation rules

This is what keeps the two layers from corrupting each other.

### Writes flow one way, and only at promotion points

**During play you write to the campaign folder and nowhere else.**

The world layer is updated only when:

- an arc concludes,
- a campaign concludes, or
- the player says an event is world-significant.

`tools/world.py promote` does it, and **it asks for confirmation** before appending.

### Nothing live is ever promoted

Current HP, gold, inventory, conditions, positions, checkpoints and roll logs stay in the campaign
folder **permanently**. The world gets **concluded facts**: what happened, when, who did it, and
what it changed.

`world.py promote` refuses text that looks like live state. `tools/validate.py --world <slug>`
fails if a live-state field appears anywhere under `worlds/`.

### Campaign canon wins locally; world canon is the default

Inside a campaign, `CANON.md` takes precedence over `worlds/<slug>/canon.md` for anything the
campaign has touched.

Where a campaign contradicts world canon, record it in the campaign as a **local divergence**
rather than rewriting the world. `templates/CANON.md` has a table for exactly this. **The world
stays the version other campaigns inherit.**

### Date-gated reads

**This is the rule that makes prequels and parallel campaigns possible.**

Each campaign has a start date and an era in `CAMPAIGN.md`. When running that campaign you read
world material dated **at or before its own current in-world date, and nothing later.**

Two reasons, and the second matters more:

1. A campaign set two centuries earlier must not be informed by events that, from its perspective,
   have not happened.
2. **The player must not be spoiled on a world event from another campaign they have not
   reached.**

```
python3 tools/world.py as-of verdant-reach "4712 AR"
```

returns the date-filtered view, **and that view is what the boot sequence loads**
(`15-continuity-and-context-recovery.md`, step 3). It prints how many entries it withheld and why,
so the gate is visible rather than silent.

`secret`-visibility entries are also withheld from a normal read, and appear only with `--gm`.
`validate.py` errors if a campaign file mentions a chronicle entry dated after that campaign's
current date.

### Concurrent campaigns share cautiously

Two campaigns running in the same era can both promote to the chronicle. The chronicle records who
did what, and the reader resolves order by date.

**Flag a collision** — two campaigns claiming the same event differently — rather than silently
merging them. `world.py promote` warns when another campaign already claims the date, and
`world.py timeline` lists every clash.

---

## `CHRONICLE.md`

**Append-only, ordered by in-world date.** Never edit or delete an entry; add a correcting entry
instead. `validate.py` fails a chronicle that is out of date order, or an entry missing its
campaign tag or visibility field.

Each entry carries:

```
## The Ashen Covenant broken

- **Date:** 12 Desnus 4712 AR
- **Campaign:** ashen-covenant
- **Characters:** Kaelen
- **Visibility:** public
- **What happened:** Two or three sentences.
- **What it changed:** What is different about the world now.
```

### Visibility — the field that does the work

| Value | A later campaign can |
|---|---|
| `public` | know it; it is common knowledge |
| `rumor` | have heard a version of it, possibly wrong |
| `secret` | know nothing; it stays in the world's `gm-private/` view |

`as-of` withholds `secret` entries unless `--gm` is passed. A later campaign's NPCs speak from the
`public` and `rumor` entries — and from `LEGENDS.md`, which is where those get distorted.

```
python3 tools/world.py promote --campaign ashen-covenant \
    --date "12 Desnus 4712 AR" \
    --title "The Ashen Covenant broken" \
    --characters "Kaelen" \
    --visibility public \
    --happened "..." --changed "..." \
    --legend "..."
```

`--legend` also appends how the event comes to be told, to `LEGENDS.md`.

---

## Per-character legacy records

One file per character who has played in this world, written at retirement or campaign end and
updated if they return.

```
python3 tools/world.py legacy --campaign ashen-covenant --character kaelen
```

| Field | What goes in it |
|---|---|
| Name, ancestry, class, level reached, campaign | the facts |
| **What they actually did** | a short list of deeds, each tied to a chronicle entry |
| **What they are known for** | **not the same list** — see below |
| Current status and whereabouts | alive · dead · retired · ascended · missing · unknown even to the GM |
| Titles, holdings, organisations founded | what outlasted them |
| Debts owed and held | both directions; either is a hook |
| Surviving relationships | who still cares, and how |
| Notable items they carried, and where those items are now | a resurfacing artefact is one of the better payoffs a shared world offers |
| **Availability in other campaigns** | see below |

### Availability

The player sets this per character and **the GM honours it**:

| Value | Means |
|---|---|
| `playable` | a returning playable character in a later campaign |
| `npc-free` | the GM may use them as an NPC freely |
| `npc-with-permission` | only with the player's say-so, asked each time |
| `off-limits` | they do not appear |

`npc-with-permission` is the default, because using someone's old character without asking is the
fastest way to make a shared world feel like a loss of control rather than a payoff.

---

## Legends and the remembered-versus-real gap

`LEGENDS.md` holds the **in-world telling** of past events: exaggerated, misattributed,
politically edited, or plain wrong.

**When an NPC in a later campaign refers to a past event, they speak from `LEGENDS.md`, not from
`CHRONICLE.md`.**

Keeping the two separate is what makes a legacy campaign land. The player gets to hear their old
character's story told wrong — and to know it is wrong, because they were there.

The legacy record's "what they actually did" and "what they are known for" are the same mechanism
at character scale. **Record both, and note the gap.** Reputation is lossy; that loss is the
material.

Good distortions:

- The deed is real and the **motive** is wrong.
- The deed is real and **someone else** gets the credit.
- Two events have been **merged** into one better story.
- The **scale** has grown — three ghouls become a legion.
- The **outcome** has been cleaned up; the cost has been edited out.
- A faction has an interest in the version told, and it shows.

---

## The tooling

```
python3 tools/world.py init "The Verdant Reach"
python3 tools/world.py link --campaign ashen-covenant --world verdant-reach --start-date "4712 AR"
python3 tools/world.py as-of verdant-reach "4712 AR"          # date-filtered read for play
python3 tools/world.py as-of verdant-reach "4712 AR" --gm     # includes secret entries
python3 tools/world.py promote --campaign ashen-covenant ...  # arc/campaign events → chronicle
python3 tools/world.py legacy --campaign ashen-covenant --character kaelen
python3 tools/world.py timeline verdant-reach                 # all campaigns on one axis
python3 tools/validate.py --world verdant-reach
```

### What `validate.py` checks in this layer

- A `World:` field pointing at a folder that **exists**.
- `CHRONICLE.md` parses, and its entries are **in date order**.
- Every entry has a **campaign tag** and a **visibility field** from the allowed set, and says
  something under "what happened".
- **No live-state fields anywhere under `worlds/`** — hit points, coins, inventory, conditions,
  positions, initiative, checkpoints.
- Every character in a legacy record is **traceable to a campaign**.
- **No campaign has read world material dated after its own current date** — it errors if a
  campaign file mentions a chronicle entry from its own future.
- For a `World: none` campaign, that nothing in the folder references a `worlds/<slug>` path.

---

## A standalone campaign is not second-class

`World: none` is the default and it stays fully supported. The boot sequence skips the `as-of`
step, no `worlds/` folder is read or written, and nothing in `system/` requires the layer to
exist. `validate.py` checks that too.

Add the layer when there is a second campaign to share with. Adding it later costs one
`world.py init` and one `world.py link`, plus promoting whichever events from the first campaign
turn out to matter.
