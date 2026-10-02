# 08 — NPCs and the bestiary

## Statblock sourcing

> **Both rulesets.** This document is shared, and the procedure is the same in each: cite the
> source, never freehand, and let the validator fail a file without a `Source:` line. What differs
> is which books you are citing, whether a creature carries a **level** or a **Challenge Rating**,
> and the shape of the stat block. A D&D creature's block and `CR` go in the same file format with
> the same required fields. **Never carry a stat block between the two games** — a CR 5 monster and
> a level 5 Pathfinder creature are not the same creature; see `23-cross-system-worlds.md`.

Per the charter: **creature and NPC statistics come from published Pathfinder 2e Remaster
material.** Monster Core, NPC Core, Player Core, Player Core 2, GM Core, and Adventure Path or
Bestiary entries.

Every `bestiary/<creature>.md` opens with:

```
**Source:** Monster Core p.NNN
**Level:** 1
**Traits:** uncommon, undead, ghoul
```

or

```
**Source:** https://2e.aonprd.com/Monsters.aspx?ID=NNN
```

…followed by the full stats in a consistent block format for the campaign's ruleset. Copy
`templates/bestiary/_CREATURE_TEMPLATE.md`.

`python3 tools/validate.py --campaign <slug>` **fails** a bestiary file with no `Source:` line.
That check exists because "I am fairly sure a ghoul has 28 HP" is exactly the kind of confident
wrongness this framework is built to stop.

Write a bestiary file for a creature **when it is actually used**, not speculatively. The folder
is a record of what this campaign fought, not a copy of a book.

### Homebrew and reskins

Exactly two shapes, and the file says which:

**Reskin** — name, description and flavour change; **the numbers do not.**

```
**Source:** Homebrew — reskin of Ghoul (Monster Core, lvl 1)
```

**Built** — from the GM Core creature-building benchmark tables, with the tables cited row by
row.

```
**Source:** Homebrew — built from the GM Core creature-building benchmarks (level 3:
AC 19 high, HP 45 moderate, Fort +11 high, attack +12 high, damage 2d6+5 moderate)
```

**Changing numbers makes it a new creature, not a reskin.** A "ghoul but tougher" is a level-2
creature built from the benchmarks, or a ghoul with the Elite adjustment — say which.

`validate.py` warns when a file says "homebrew" but names no base creature or benchmark table.

### Adjustments

Elite and Weak are the official dial. Record in the bestiary file whether they are applied, and
say so to the player when it matters — "these are the weaker sort" is information a player can act
on.

```
python3 tools/pf2e.py tables adjustments        # PF2e: Elite and Weak templates
python3 tools/dnd5e.py cr --cr 1/4 2 5          # D&D: XP and proficiency by CR
```

| | Elite | Weak |
|---|---|---|
| Level | +1, or **+2 if the creature is level −1 or 0** | −1, or **−2 if the creature is level 1** |
| AC, attack modifiers, DCs, saves, Perception, skills | +2 | −2 |
| Strike and offensive-ability damage | +2 | −2 |
| …if the ability has a **use limit** (spells, a dragon's breath) | **+4** | **−4** |
| HP | +10 (level **1 or lower**), +15 (**2–4**), +20 (5–19), +30 (20+) | −10 (level **1–2**), −15 (**3–5**), −20 (**6–20**), −30 (**21+**) |
| XP | award for its **new** level | award for its **new** level |

**The two HP columns do not share their level boundaries.** A level-3 creature gains 15 HP elite
but loses 15 weak; a level-5 creature gains 20 but loses only 15; a level-20 creature gains 30 but
loses 20. This framework had them wrong — one shared set of bands — until the table was read from
the source. If you have a bestiary file written before that, recheck its adjusted HP.

**Source:** Monster Core p.6, Adjusting Creatures — <https://2e.aonprd.com/Rules.aspx?ID=3262>.

---

## Significant NPC format

Copy `templates/npcs/_NPC_TEMPLATE.md`. Every significant NPC carries:

- **Name**, and a **concept** — ancestry plus a class-ish idea, not a stat block.
- **Level**, if statted.
- **Role in the story** and **faction**.
- **Disposition toward each PC on a named scale**: `hostile` · `unfriendly` · `wary` ·
  `indifferent` · `friendly` · `helpful` · `devoted`. Per PC, with a reason.
- **Goals, public and private.** What they say they want, and what they actually want.
- **A distinctive voice** — vocabulary, rhythm, verbal tic — so they sound the same three
  sessions later. This is the field that stops every NPC sounding like the same narrator.
- **What they know**, and whether they would share it, and at what price.
- **What they want from the player.**
- **Current status**: alive / dead / missing / hostile / allied / imprisoned / fled.
- **Last seen**: where, and on which in-world date.
- A **`> **GM-ONLY**`** block for secrets.

### Stat blocks only when needed

**A shopkeeper needs a personality, not a stat block.** Build one when combat or a meaningful
contest becomes plausible — and at that point it comes from published material like any other
creature, usually from NPC Core, cited.

An NPC who will only ever be talked to needs: a voice, a disposition, what they know, and what
they want. That is four lines and it is enough.

---

## Recurring-cast discipline

`npcs/ROSTER.md` is the index. **Re-read it before any scene with NPCs.** It exists so the
blacksmith's name and attitude do not drift between sessions, which is the single most common
continuity failure in a long campaign run this way.

The roster holds: name, role, faction, disposition to the party, status, last seen (where and
when), and the file. Plus two side tables worth keeping:

- **Named but not yet met** — people the player has heard of and not seen, and who told them.
- **Voices in use** — one row each, so nobody starts sounding like everybody else.

**Dead NPCs stay in the roster, marked dead.** Deleting them is how a dead NPC walks back into
a scene six sessions later.

Update the roster whenever an NPC's status, location or disposition changes — including from an
off-screen turn.

---

## Structured relationships

Each NPC file carries its ties as **structured fields**, one per line:

```
- ally-of: Mira Vance — shared a cell in Korvosa
- rival-of: Guildmaster Poll — competing for the same contract
- owes: Kaelen — a life, and he knows it
- owed-by: The Ashen Covenant — three months' unpaid work
- serves: House Vhaldrin — nominally
- related-to: Tessa Ferren — half-sister, estranged
- fears: the thing in the aqueduct — saw it, will not say what
```

The seven kinds are `ally-of`, `rival-of`, `owes`, `owed-by`, `serves`, `related-to`, `fears`.
Each names **another NPC, a faction, or a player character**, with a one-phrase reason. The same
fields work on factions in `FACTIONS.md`.

Mark a tie the player has not learned yet with `[unknown]`, and a GM-side one with `[gm-only]`:

```
- serves: The Ashen Covenant — has done since before the siege [gm-only]
- rival-of: Sergeant Aleth — the player has not seen them together yet [unknown]
```

### The graph

```
python3 tools/graph.py --campaign <slug>
```

reads those fields plus `FACTIONS.md` and writes a **Mermaid diagram into `WORLD.md`**,
regenerated whenever the roster changes. Mermaid renders on GitHub and in most Markdown viewers
with nothing to install, so there is no runtime dependency.

Two versions are produced:

- **Player-safe**, into `WORLD.md` — only ties the player has actually learned in play. This is
  the default output.
- **Full**, into `gm-private/relationships.md` — including hidden allegiances. This one is
  **only ever written to `gm-private/`** and is never printed unless `--gm` is passed
  explicitly.

The dashboard shows the same data as a **plain adjacency list** rather than a rendered diagram,
because it must not fetch a diagramming script at runtime.

### It is opt-in

The graph is worth the most in **intrigue and faction play**. In a dungeon crawl with six named
NPCs it is noise. It is off by default; `PLAYER_PREFS.md` records whether it is on, and the
intake interview asks.
