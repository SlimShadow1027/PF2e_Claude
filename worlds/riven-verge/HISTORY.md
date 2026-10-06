# The history of The Riven Verge

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
`python3 tools/world.py history {slug}`, and the date-gated read in `as-of` includes it.

<!-- HISTORY-CHAPTERS-BELOW -->

## The Reckoning begins, because somebody started counting

- **Span:** 1-4 VR
- **Certainty:** legendary
- **Sources:** the Verge's own telling

Nobody in the Verge claims the world broke in year one. What happened in year one is that a woman on what is now called Low Shoal wrote down that the shards had come close again, and then wrote it down the next time, and the time after that — and her successors kept the count. Everything before that is the deep past, and the Verge does not date it. What the record shows, from its first entries, is that the drift was already regular by then: eight spans, the same order, the same approximate lengths. Whatever broke the world had finished breaking it long enough ago for the pieces to have settled into a rhythm. The woman's name is given three different ways in three different places, which is the earliest thing anybody argues about here.

## The arrivals, and what they would not say

- **Span:** 140-180 VR
- **Certainty:** recorded
- **Sources:** harbour rolls on four shards

Across four decades, people began appearing on the outer shards who had not been born in the Verge and could not say how they had come. The harbour rolls of Low Shoal, Thrennet, the Cant and Bellows Deep all record them, independently and in roughly the same numbers, which is the reason this chapter is recorded rather than disputed. They arrived singly or in small groups, usually injured, usually during Nearing or Touching and almost never during Stillness. They described a world with a sun in it. Several of them described the same place, named differently. What none of them could do, then or since, was go back — and the Verge has had a hundred and fifty years to notice that the traffic runs one way. Their descendants are natives now, and a few of the older families still keep a direction in their house records that points at nothing.
