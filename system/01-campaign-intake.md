# 01 — Campaign intake

The interview that starts a campaign. **Walk the player through it a few questions at a time,
not all at once.** Three to five concrete example answers for each question, so they can pick
rather than compose. Every question also offers:

- **"surprise me"** — the GM chooses, states what it chose, and moves on.
- **"roll it"** — a real roll on a table in `16-random-tables.md`, with
  `python3 tools/roll.py table system/16-random-tables.md "<table>" --campaign <slug>`.

Run `python3 tools/new_campaign.py "<title>"` **first**, so there is a folder to write answers
into as they arrive. The scaffold's placeholder values are all "not yet decided"; intake
replaces them.

Do not generate a world, an NPC, a map or a stat block during intake. Intake ends with a pitch
and a pause.

---

## Block 1 — shape and length

**How long is this campaign?**

1. A one-shot — one sitting, one problem, a real ending.
2. A short arc — three to six sessions, one escalating problem.
3. A published Adventure Path, run as written with the levers in `03-*` applied for party size.
4. A sandbox — a region, some factions, and no predetermined plot.
5. A long campaign to level 20.

**What level range, and how fast?**

1. Level 1–4 (the fragile, best-remembered part).
2. Level 1–10.
3. Level 5–12 (start competent).
4. Level 1–20, the whole arc.
5. A fixed level with no advancement at all.

Advancement: **XP as written** (1000 XP per level, awarded per encounter) ·
**milestone** (level when the story says so) · **fast** (levels roughly every two sessions).

> Record in `CAMPAIGN.md`: `Shape:`, `Expected level range:`, `Advancement:`.

---

## Block 2 — genre and tone

**Genre** — pick one, or name a pair to cross:

high fantasy · gothic horror · mystery and investigation · political intrigue · war ·
exploration and hexcrawl · dungeon crawl · heist · planar · nautical · weird west ·
post-apocalyptic · comedic

**Tone dial**, from pulpy to grim:

1. **Pulpy** — swashbuckling, the good guys win, death is rare and reversible.
2. **Heroic** — stakes are real but the fiction is on the party's side.
3. **Grounded** — competence matters, consequences stick.
4. **Grim** — the world does not care, and winning costs something.
5. **Bleak** — survival is the victory condition.

**Lethality expectation** — say this out loud now rather than discovering it at dying 3:

1. No character death; defeat is capture, loss, injury, or a narrative cost.
2. Death is possible but telegraphed hard and always avoidable.
3. Death is on the table if the player pushes a bad situation.
4. Death happens; a bad round can end a character.

> Record in `CAMPAIGN.md`: `Genre:`, `Tone:`, `Lethality:`. The lethality answer is the
> single biggest input to the preset chosen in `03-difficulty-and-solo-levers.md`.

---

## Block 3 — setting

**Where?**

1. **Golarion as published** — and where: Absalom · Ustalav · the Mwangi Expanse · Cheliax ·
   the Mana Wastes · Tian Xia · Varisia · the Shackles · somewhere else.
2. **Lightly reskinned Golarion** — the mechanics and gods stay, the names change.
3. **Fully original** — built in intake and in play.
4. **A published Adventure Path's setting**, as that path assumes.

**Which setting assumptions stay?** Ask each, briefly:

| Assumption | The question |
|---|---|
| Gods and religion | The Golarion pantheon, a smaller one, or none that answer? |
| Planes and afterlife | The published cosmology, something else, or unsettled? |
| Ancestries | All published ancestries present, a short list, or humans-plus-a-few? |
| Magic prevalence | Everywhere and regulated · uncommon and feared · nearly gone · returning |
| Technology level | Standard PF2e · pre-industrial · clockwork and guns · scavenged high tech |

> Record in `CAMPAIGN.md` under "Setting assumptions kept". An assumption not asked about
> becomes an argument later.

---

## Block 4 — the shared world (optional)

**Is this campaign standalone, or set in a world that already exists under `worlds/`?**

1. **Standalone** — `World: none`. Nothing about the shared layer becomes mandatory, and
   nothing changes about how the campaign runs.
2. **In an existing world** — name it. Then:
   - **In what era relative to what has already happened there?** Same generation, a
     century later, two centuries earlier, concurrent with another campaign?
   - **What is the start date?** (`4712 AR`, or a date in the world's own calendar.)
   - Confirm: **the date gate will keep the player unspoiled.** When running this campaign the
     GM reads world material dated at or before the campaign's own current in-world date and
     nothing later. `python3 tools/world.py as-of <world> <date>` is what the boot sequence
     loads. A world event from a campaign the player has not reached will not leak in.
3. **A new world, starting here** — `python3 tools/world.py init "<name>"`, then link.

Attach it with:

```
python3 tools/world.py link --campaign <slug> --world <world> --start-date "4712 AR"
```

See `21-shared-worlds.md`.

---

## Block 5 — premise and stakes

Three questions, and the answers want to be specific rather than grand:

1. **What is wrong with the world?** Not "evil rises" — "the river has run wrong for nine
   days and the priests have stopped explaining it".
2. **Who is causing it?** A person, a faction, an institution, or a thing that does not
   know it is doing harm.
3. **What happens if nobody stops it?** Name the concrete loss, and roughly when.

If the player wants the GM to propose these, offer three premises from their earlier answers
and let them pick or mix.

> Record in `CAMPAIGN.md` under "Premise and stakes".

---

## Block 6 — protagonist framing

**Why is this character the one who acts?** Pick one, or two crossed:

1. **Patron** — someone is paying, and has their own reasons.
2. **Obligation** — an oath, a debt, a post, a family name.
3. **Revenge** — something was taken.
4. **Curiosity** — nobody else is asking the question.
5. **Curse** — the problem is attached to them personally.
6. **Accident** — they were in the wrong place and now they know too much.

This is the question that makes a solo campaign work. A protagonist with no reason to be
there has to be dragged from scene to scene.

---

## Block 7 — party structure

The action economy is the thing that breaks solo PF2e, so this is a mechanical question
dressed as a narrative one. Cross-reference `03-difficulty-and-solo-levers.md`.

1. **One character, alone.** Hardest. Needs the safety-net levers.
2. **One character plus a GM-run ally built as a full PC.** Closest to a real party of two.
3. **One character plus a sidekick** — a simplified companion with fewer decisions.
4. **Troupe play** — the player controls two to four characters.
5. **A rotating guest ally per arc** — a full PC who comes and goes with the story.

Then: **are GM-run allies full PCs, sidekicks, or narrative-only** (present in the fiction,
absent from the initiative order)?

> Record in `CAMPAIGN.md` under "Party structure" and in `RULES_DELTAS.md` under party shape.

---

## Block 8 — content boundaries

Ask plainly, once. Do not soften it, do not make a production of it, and do not skip it.

> "Two things before we build anything. **Lines** are things that never appear in this
> campaign at all. **Veils** are things that can happen but stay off-screen and undescribed.
> What are yours? 'None' is a complete answer, and you can add one at any time by saying so."

Offer examples so the question is answerable rather than abstract: harm to children ·
sexual violence · torture described in detail · animal cruelty · self-harm · body horror ·
suicide · religious desecration · slavery · plague and pandemic · spiders and insects ·
drowning · confinement.

Also ask: **is there anything to check in about before it happens**, as distinct from a line
or a veil?

> Record in `PLAYER_PREFS.md`. **Lines and veils outrank everything else in this repository,
> including flags and including the premise.** A flag that conflicts with one gets raised
> with the player rather than quietly dropped.

---

## Block 9 — flags

> "Last one of these, and it is the most useful. **What do you actively want to see happen
> in this campaign?** Not a plot — a target I can aim at on my own terms. Three to five."

Seed the list with examples so the *shape* is clear. Say explicitly that these are examples:

- "I want to be genuinely outmatched at least once and have to run."
- "I want a moral choice where both options cost me something real."
- "I want one fight that's pure spectacle with no moral weight at all."
- "I want to found something that outlasts me."

Then ask, for each flag the player gives: **how hot is it** — `burning`, `warm`, or `someday`?

> Record in `FLAGS.md`, in the player's own words. If they give none, the file stays empty and
> the GM aims at nothing. The examples above are illustrative only and never become elements
> of the campaign. See `20-player-flags.md`.

---

## Block 10 — play preferences

Quick-fire; offer the defaults and let the player correct them.

| Question | Options |
|---|---|
| Narration length | a paragraph · two or three · as long as it needs · short and fast |
| Prose vs. bullets | prose for scenes, bullets for mechanics · mostly bullets · mostly prose |
| Person | second person ("you") · third person ("Kaelen…") |
| Tense | present · past |
| Name the rules being applied | always · when it matters · only if asked |
| Offer tactical suggestions | never · when asked · one option per turn · full advice |
| Remind me of my actions and feats | every turn · when I seem stuck · never |
| Enemy hit points shown as | numbers · a bar · vague descriptors · nothing |
| Transparency mode | `glass` · `standard` · `mystery` (see `04-dice-protocol.md`) |

> Record in `PLAYER_PREFS.md`, and set the transparency mode in state:
> `python3 tools/state.py --campaign <slug> transparency standard`.

---

## Block 11 — session rhythm

| Question | Options |
|---|---|
| How long is a typical sitting? | 30 minutes · an hour · two hours · an evening · open-ended |
| Roughly how many scenes is that? | the GM proposes a number; it gets corrected by experience |
| Open with | a trailer ("previously on…") · a cold open, straight into a scene in motion |
| Aim for a cliffhanger | yes · only when it is earned · no, prefer clean stops |
| Checkpoint aggressiveness | as specified in `05-*` · more often · only when I ask |
| Off-screen turns between sessions | off · on, weekly · on, between sessions |
| `world_pace` if on | glacial · slow · steady · brisk · runaway |
| Relationship graph | off · on (worth it for intrigue, noise in a dungeon) |

> Record in `PLAYER_PREFS.md`. The scene budget is a steering aid and never truncates a
> scene — see `22-session-flow.md`.

---

## Ending intake

Write, in this order:

1. `CAMPAIGN.md` — every answer above, with `World:` and `Era:` / start date.
2. `RULES_DELTAS.md` — the preset and every lever, from `03-difficulty-and-solo-levers.md`.
3. `PLAYER_PREFS.md` — boundaries, transparency, narration, rhythm.
4. `FLAGS.md` — the player's flags in their own words, with heat.
5. `WORLD.md` — only the region and the home base. Not a gazetteer yet.

Then:

```
python3 tools/validate.py --campaign <slug>
python3 tools/state.py --campaign <slug> checkpoint "intake complete"
```

And **offer three one-page pitches from the same answers, and stop.**

Each pitch is: a title, a one-line hook, the opening situation, the antagonist's plan, what
the first session would look like, and one line on what makes it different from the other two.
Say which of the player's flags each pitch aims at.

**Do not build the world until the player approves a pitch.** No NPCs, no maps, no stat
blocks, no gazetteer. If they like parts of two pitches, merge and re-offer rather than
proceeding on a guess.
