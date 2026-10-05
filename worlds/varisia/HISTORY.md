# The history of Varisia

The world's own book about itself. **Prose, shared by every ruleset, and deliberately less
precise than `CHRONICLE.md`.**

This is the layer a GM reads to know what kind of place this is, and the layer a player's
character could plausibly have been taught. It is written as history is written: in spans
rather than dates, with the certainty of each account stated, and with the gaps left visible
rather than filled.

## What goes in here, and what does not

| | |
|---|---|
| **In** | What happened and why it mattered. Causes, consequences, who was changed. Named people, places, factions. The shape of an age. What the world believes about itself |
| **In** | Uncertainty, stated: who disagrees, what was never established, what is only remembered |
| **Out** | **Any ruleset's numbers.** No levels, DCs, ACs, CRs, stat blocks, treasure or dice. A reader of this file may be playing a different game from the one that wrote the chapter |
| **Out** | Live state of any kind. That stays in `campaigns/<slug>/state.json`, permanently |
| **Out** | The blow-by-blow. That is the per-ruleset narrative in `<system>/<campaign>.md` |

## How a chapter is shaped

Each chapter carries three fields and then as much prose as it earns:

- **Span** — the range it covers, in this world's calendar. The *end* of the span is what
  the date gate reads, so a chapter is withheld from a campaign that has not reached it.
- **Certainty** — one of `attested`, `recorded`, `disputed`, `legendary`, `lost`.
- **Sources** — which campaigns contributed, each with its ruleset in brackets. A chapter
  with no source is the world's own background, written before any campaign ran.

Append with `python3 tools/world.py history add`, read with
`python3 tools/world.py history varisia`, and the date-gated read in `as-of` includes it.

<!-- HISTORY-CHAPTERS-BELOW -->

## The sump was dug, and then forgotten

- **Span:** before 4700 AR
- **Certainty:** legendary
- **Sources:** the Cove's own telling

Nobody in Roderic's Cove will tell you who cut the first stair down into the sump, and the three people who claim to know do not agree. The oldest version has it that the stair was not cut at all but found, already going down, by salvagers who were looking for something else and did not like what they found. What is agreed: there was a door at the bottom, it was sealed from the far side, and for a long lifetime the Cove made its living by not opening it. The windlass came later. So did the admission fee.

## The water began to fall

- **Span:** 4726-4729 AR
- **Certainty:** disputed
- **Sources:** third-beginnings (PF2e)

The waterline in the sump started dropping, and the Cove noticed late. Vessa Tarn says she reported it twice before anyone wrote it down; the harbour office says once. Either way the stone below the line came up dry, which it should not have been, and the queue at the windlass doubled inside a season. By the end of the span the Cove had stopped pretending the sump was a sump.

