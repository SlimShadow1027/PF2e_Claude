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

## The pitch — The Sump Door

Chosen by the player on 2026-09-30 from three offered. The other two are not canon; one is
parked at `campaigns/_parked/the-cartographers-error.md` at the player's request, the third
was discarded.

Roderic's Cove pays a bounty for anything dredged out of the sea caves under the cliff. For
thirty years the haul has been shipwreck junk — rigging, coin, the occasional body. Last
month a diver brought up a door. Freestanding. Upright. Seated in bedrock forty feet down.
Thassilonian, and shut.

The Cove's answer was to build a windlass over it and start charging admission. Yours is to
ask why anyone would build a door underwater.

You are the third person to open it. The first two are still down there. One of them is
still moving.

## Premise and stakes

- **What is wrong with the world:** A Thassilonian door in the sea caves beneath Roderic's
  Cove has been opened. It was not a door *into* anywhere — it was a seal, and it was
  holding. The town has spent a month monetising the hole in it.
- **Who is causing it:** Nobody is causing it on purpose. The Cove's dredging economy opened
  it by accident and now cannot afford to close it. The thing behind it is patient and does
  not need anyone's cooperation. The two previous openers are complications, not villains —
  at least one is still a person.
- **What happens if nobody stops it:** The water table under the Cove keeps dropping. That
  is the visible symptom and the campaign's clock: the deeper levels get drier, and when the
  last of them does, whatever the seal was for walks out on dry stone. Roughly seven
  chapters, and the player can watch it happen on the cliff face.

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

- **Curiosity is not innocent.** The protagonist opens the door because nobody else asked.
  That is admirable and it is also the inciting harm. The campaign never lets them forget
  they did this.
- **A town that cannot afford the right answer.** The Cove is not corrupt or stupid. It is
  poor, and the dredging is the only thing it has. Everyone who obstructs the protagonist
  has a reason that would hold up in front of their own family.
- **Down is drier.** The one physical fact that is wrong, stated early and never explained
  until it has to be. It is the clock, the mystery and the tell, all at once.
- **The other two.** Someone already did what the protagonist is doing. Twice. What they
  became is the campaign's honest forecast.

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
