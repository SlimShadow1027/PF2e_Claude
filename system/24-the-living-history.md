# 24 — The living history, and which layer to write in

Read `21-shared-worlds.md` first, and `23-cross-system-worlds.md` if the world has campaigns in
more than one game.

A world's past lives in **four** files of deliberately different shapes, plus the universe layer
above them. Writing in the wrong one is the commonest way a shared world turns into either a
spreadsheet nobody reads or a novel nobody can query.

```
worlds/UNIVERSE.md              what is true across every world — optional, needs two worlds
worlds/<world>/
  CHRONICLE.md                  the spine:   dated, structured, terse, gated
  HISTORY.md                    the book:    prose, spans, certainty stated, no numbers
  <system>/<campaign>.md        the account: thorough, system-flavoured, one per campaign
  LEGENDS.md                    the telling: how the above is remembered wrongly
```

---

## The four layers

| | `CHRONICLE.md` | `HISTORY.md` | `<system>/<campaign>.md` | `LEGENDS.md` |
|---|---|---|---|---|
| **Shape** | one structured entry per event | prose chapters | prose, long | short retellings |
| **Precision** | an exact date | a **span**, and a stated **certainty** | as exact as it likes | deliberately wrong |
| **Read by** | every ruleset | every ruleset | **that ruleset only** | every ruleset |
| **Date-gated** | yes | yes, on the span's **end** | no — read your own campaign's | yes |
| **Numbers allowed** | no | **no** | yes — name the rules | no |
| **Written** | at a promotion point | when an age closes, or an arc changes the world | at the end of each arc | when a deed starts being told |
| **Tool** | `world.py promote` | `world.py history-add` | `world.py narrative` (scaffold), then by hand | `promote --legend` |

One event can legitimately appear in all four: a line in the chronicle, a paragraph in the
history, three pages in the per-ruleset account, and a song that gets it wrong in the legends.
That is not duplication — each is a different *kind* of record, and the per-ruleset account's
"Promoted to the shared layer" table is where you note which of its contents reached which.

---

## `HISTORY.md` — the living history

**The world's own book about itself.** This is the layer a GM reads to know what kind of place
this is, and the layer a character could plausibly have been *taught*.

It is **less precise than the chronicle on purpose.** A world's memory of itself is uncertain,
and a history that states everything as fact at an exact date is lying about how history works.
So each chapter carries:

- **Span** — the range it covers (`4726-4729 AR`, `before 4700 AR`, a single date). The **end** of
  the span is what the date gate reads, so a chapter still running at a campaign's current date is
  withheld from it.
- **Certainty** — one of five, and this is the field that does the work:

| Certainty | Means |
|---|---|
| `attested` | more than one campaign saw it, or it left physical proof; treat as fact |
| `recorded` | one campaign saw it and wrote it down; treat as fact unless contradicted |
| `disputed` | accounts disagree on what happened, or who did it, or when |
| `legendary` | the world tells it, nobody alive saw it, and the details have drifted |
| `lost` | something happened here and the world no longer knows what |

- **Sources** — which campaigns contributed, each tagged with its ruleset. A chapter with no
  source is the world's own background, written before any campaign ran.

```
python3 tools/world.py history-add --world varisia \
    --title "The water began to fall" \
    --span "4726-4729 AR" --certainty disputed \
    --campaign third-beginnings \
    --body "The waterline in the sump started dropping, and the Cove noticed late. …"

python3 tools/world.py history varisia --date "1 Abadius 4727 AR"
```

### What makes a good chapter

- **An age, not an incident.** If it is one event on one day, it is a chronicle entry. A chapter
  is what changed across a span.
- **Causes and consequences, not deeds.** "The queue at the windlass doubled inside a season" is
  history. "Karsa opened the door" is a chronicle entry.
- **The disagreement, stated.** `disputed` is the most useful certainty and the most underused.
  Two accounts that differ is better material than one that is tidy.
- **The gaps left visible.** `lost` is a legitimate chapter. "Something happened to the second
  stair and nobody knows what" is a hook; silence is not.
- **No numbers.** The tool refuses a chapter mentioning a DC, an AC, a CR, a level, a dice
  expression, a coin value or hit points, because a reader of this file may be playing a different
  game. `--allow-numbers` exists for genuine in-world quantities — a count of ships, a span of
  years — and should be rare.

---

## `<system>/<campaign>.md` — the thorough account

One file per campaign, in a folder named for its ruleset. **This is where detail goes.**

Because only campaigns of that ruleset read this folder, it may name the class, the spell, the
creature, the condition and the roll that turned a scene. To a reader playing the same game none
of that is noise; to a reader playing the other game all of it would be.

```
python3 tools/world.py narrative --campaign third-beginnings   # scaffolds the file
```

The scaffold has sections for what was already true, the arcs in order, the people and what
became of them, **what it cost**, what is still unresolved, and a table of what was promoted to
the shared layer. Write it **at the end of each arc, while the detail is still in reach** — not at
the end of the campaign, by which time the texture is gone.

The one rule that still applies here: **nothing live.** Hit points, coins, inventory, conditions,
positions, checkpoints and roll logs stay in `campaigns/<slug>/` permanently. What belongs here is
the *account*, written after the fact.

### Why this is separate from the campaign's own `sessions/`

`campaigns/<slug>/sessions/` is a log written during play, session by session, for continuity.
This is a history written after play, arc by arc, for a reader. A standalone campaign
(`World: none`) has only the former, and that is fine.

---

## `worlds/UNIVERSE.md` — the layer above worlds

**Optional, and only worth having once a second world exists.**

A world is a place campaigns are set in. A universe is what is true *across* places — so a
campaign on another continent, another plane, or in another age can be the same universe as the
first without sharing its geography, its factions or its history.

Each world declares its own place with fields in its README:

```
- **Universe:** <name>
- **Position:** a continent, a plane, an age — whatever distinguishes it
- **Era:** the present day here
- **Reachable from:** other worlds, and how; "no known route" is a fine answer
```

```
python3 tools/world.py universe --init      # write worlds/UNIVERSE.md
python3 tools/world.py universe             # the register, rebuilt from the world folders
```

### What crosses between worlds

The same discipline as the cross-ruleset rule, one layer up:

| Crosses | Does not cross |
|---|---|
| Cosmology, planar structure, the deep past | Local history, local factions, local geography |
| Powers named in `UNIVERSE.md` | Powers named in a single world's `PANTHEON.md` |
| A character who physically travelled, with their story | Their reputation, unless news travelled too |
| Items, with their histories | Any ruleset's numbers |

**A world's history is its own.** A chapter in one world's `HISTORY.md` is not known in another
unless something carried it there — and saying *what* carried it is more interesting than assuming
it did. "No known route" is the most useful thing a universe register can say, because it makes
the first crossing an event.

The rule that keeps this layer worth having: **write in `UNIVERSE.md` only what is true in every
world listed.** A fact true in one world belongs in that world's files. This is the most commonly
broken rule here and the one that makes the layer worthless when broken.

---

## Where a thing goes — the quick answer

| You want to record | Write it in |
|---|---|
| An event, on a date, that is finished | `CHRONICLE.md` via `promote` |
| How an age changed the world | `HISTORY.md` via `history-add` |
| What actually happened in session 7 | `campaigns/<slug>/sessions/` |
| The full account of an arc, for a reader | `<system>/<campaign>.md` |
| How people get the story wrong | `LEGENDS.md` |
| What your old character is remembered for | `characters/<name>.md` |
| A place, a faction, a god | `GAZETTEER.md`, `FACTIONS.md`, `PANTHEON.md` |
| A fact no campaign may contradict | `canon.md` |
| Something true in every world | `worlds/UNIVERSE.md` |
| Anything with a hit point in it | `campaigns/<slug>/state.json`, and nowhere else |

`python3 tools/validate.py --world <slug>` checks the lot: that the history parses and is in span
order, that no chapter is duplicated or has an unstated certainty or no prose, that no ruleset's
numbers leaked into the shared layer, that each per-ruleset folder holds only its own ruleset's
campaigns, and that a world declaring a universe has one to declare.
