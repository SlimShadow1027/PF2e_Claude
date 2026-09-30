# Third Beginnings

- **Slug:** third-beginnings
- **Created:** 2026-09-30
- **World:** none
- **Era:** present day
- **Start date:** 1 Abadius 4725 AR
- **Shape:** original campaign built to Adventure Path discipline, shaped after a known AP — chapters with level gates, every encounter built to a verified XP budget, treasure paced off GM Core Table 6-1, every creature a cited published stat block. No published adventure text is reproduced; the specifics are this table's, and are flagged as unverifiable against a published adventure.
- **Expected level range:** 1 to roughly 5-8
- **Advancement:** milestone, leaning fast — level when the story says so, roughly every two sessions
- **Genre:** dungeon crawl × exploration/hexcrawl
- **Tone:** heroic — stakes are real, the fiction is on the protagonist's side
- **Lethality:** 2 — death is possible but telegraphed hard and always avoidable. Drives the preset in `system/03-difficulty-and-solo-levers.md`.
- **Setting:** Golarion as published — **Varisia**

> `World:` names a folder under `worlds/`, or `none` for a standalone campaign. A campaign
> with `World: none` behaves exactly as it does today — nothing about the shared layer
> becomes mandatory. See `system/21-shared-worlds.md`.

## The pitch

_Not written yet. Intake ends with three one-page pitches; the player picks one before anything else is generated._

## Premise and stakes

- **What is wrong with the world:** not yet decided
- **Who is causing it:** not yet decided
- **What happens if nobody stops it:** not yet decided

## Protagonist framing

Why is this character the one who acts? **Curiosity crossed with a curse.**

- **Curiosity** — nobody else is asking the question. The protagonist goes because the map is
  blank, not because anyone sent them.
- **Curse** — and then the question turns out to be attached to them personally. The campaign
  cannot be walked away from once it starts answering.

The crossing is the useful part: curiosity gets them through the door of their own free will,
and the curse means the door does not open outward again. Chapter one should be pure
curiosity; the curse should announce itself late enough that the player has already chosen
to be there.

## Party structure

- **Characters the player controls:** 1
- **Characters the GM runs:** 1
- **Ally status:** a **GM-run ally built as a full PC**, in the initiative order, levelling
  alongside the protagonist.

The ally exists to fix the two things that actually break solo PF2e, and both are mechanical:

1. **Flanking becomes possible**, so off-guard is something the protagonist can create rather
   than something they have to buy with Feint, Trip or a spell every single round.
2. **Somebody can Administer First Aid.** Alone, an unconscious character cannot stabilise
   themselves, which turns the dying track from a bad-luck problem into a structural one.

The ally never takes the spotlight, never solves the scene, and never makes the decision. It
carries a build, a voice and a reason to be there, and it is one more body in the initiative
order.

See `system/03-difficulty-and-solo-levers.md` for what each party shape does to the math.

## Setting assumptions kept

| Assumption | Decision |
|---|---|
| Gods and religion | The Golarion pantheon as published. Varisia's own picture is uneven — Desna, Gozreh, Erastil and Pharasma are widely kept; the Sandpoint region keeps a broad Varisian folk faith alongside them. |
| Planes and afterlife | The published cosmology. Pharasma judges; the Boneyard is real and known about. |
| Ancestries present | All published ancestries exist. Varisia in practice is humans (Varisian, Shoanti, Chelish settler stock), with dwarves, elves, halflings, gnomes and goblins common enough to pass unremarked, and anything rarer drawing a look. |
| Magic prevalence | Uncommon but unremarkable. Most villages have someone with a cantrip; a real spellcaster is a person you have heard of by name. Thassilonian magic is a different thing entirely and is feared. |
| Technology level | Standard PF2e. No firearms outside Alkenstar imports, which are a curiosity. |

## Themes to keep returning to

_Not yet decided._

## Intake answers not captured above

Intake run 2026-09-30, in one sitting. Every block answered.

- **Why "original, AP-shaped" rather than a published adventure.** The player owns no
  adventures. `paizo.com` is reachable from this container but `store.paizo.com`,
  `www.paizo.com` and `downloads.paizo.com` are all refused by the egress proxy, so no
  adventure PDF can be fetched. The free PF2e catalogue was read from
  <https://paizo.com/pathfinder/2e/freeresources> and is eight 1-2 hour one-shots built
  around fixed pregenerated characters — none covers level 1 to 5-8 and most do not allow
  the player's own character. Archives of Nethys hosts rules, creatures, hazards and items,
  not adventure text. So a published campaign-length adventure is not reachable, and the
  player chose an original campaign built in an AP's shape instead.
- **What "AP discipline" binds this campaign to.** Chapters with explicit level gates.
  Every encounter built to a budget from `python3 tools/pf2e.py encounter`. Treasure paced
  against GM Core Table 6-1 and tracked in `logs/loot.md`. Every creature a published stat
  block cited by name, source and level, or homebrew naming its base. Milestone advancement
  at chapter boundaries rather than XP totals.
- **The published-adventure honesty note.** Nothing here reproduces published adventure
  text. Where the campaign borrows the *shape* of a known Adventure Path, that shape is this
  table's reconstruction and is not verifiable against a published source. Rules, creatures
  and items are a separate matter and remain cited.
