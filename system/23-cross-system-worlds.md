# 23 — A world shared across rulesets

Read `21-shared-worlds.md` first: everything in it still applies. This document covers the one
case it does not, which is **a world holding campaigns of more than one of the three rulesets**.

That case is supported, and it is the reason the world layer is shaped the way it is. It is also
the one place where getting it wrong is silent: a level written into a chronicle entry does not
fail validation loudly the way a bad date does — it just misinforms a reader two campaigns later
who has no way to know it was ever meaningless to them.

The layer where each game's campaigns keep their *own* detailed history —
`worlds/<world>/<system>/<campaign>.md` — is in `24-the-living-history.md`. It exists precisely
so that the shared layer can stay imprecise without anyone losing the detail.

```
python3 tools/world.py systems <world>          # which rulesets play here, and the calendar
python3 tools/world.py crossing                 # what crosses, and what does not
python3 tools/world.py convert --level 7 --from pf2e --to dnd5e
python3 tools/world.py convert --level 14 --from dnd4e --to pf2e
python3 tools/rules.py bands                    # the scope bands, and which of them is published
```

---

## The one rule

**The world records what happened. It never records anyone's numbers.**

A world folder is system-neutral. Campaigns of any ruleset link to it, promote into it and
read from it, and nothing in it belongs to one game. That is not tidiness — it is the only
version of a shared world that survives being read by three games with different maths.

---

## What crosses

| Crosses | Why |
|---|---|
| Events, dates, causes, consequences | A tower falling is a tower falling in any ruleset |
| People, factions, places, and their standing | Who holds the harbour does not depend on the dice |
| Debts, titles, oaths, reputations, grudges | All fiction |
| Items **as objects with histories** | "The blade Roderic carried" is a story. "+1 longsword" is not |
| Gods, planes, cosmology | World facts. How they are *served* is each ruleset's own |
| **Scope** — how far an event or a character reached | The one translation this framework makes |

## What does not cross

| Does not cross | Why not |
|---|---|
| Character levels, one for one | A level is a position on one game's power curve. The curves differ in shape, not merely in scale — and 4e's runs to **30**, so a "level 14 character" is mid-campaign there and near the end of one in either sibling. |
| Stat blocks | A CR 5 D&D 2024 monster, a level 5 Pathfinder creature and a level 5 D&D 4e monster are three different creatures, and none of their numbers survive the trip. |
| DCs | Pathfinder's and 4e's DCs rise with level; D&D 2024's do not. "A DC 20 lock" is a different obstacle in each game — and in the two that scale, a different obstacle at level 2 than at level 15. 4e's table was also revised by errata, so two 4e campaigns can disagree. |
| ACs, defences and attack bonuses | Bounded in D&D 2024; climbing in Pathfinder; climbing in 4e with **half the level** added to four different defences at once. |
| Treasure, piece for piece | Pathfinder publishes a per-level allotment; D&D 2024's equivalent is not open content; 4e hands out numbered **parcels** per level, and that table is not open content either. The economies are three different shapes — and the coin ratios themselves differ, since 1 pp is 10 gp in two of them and **100 gp** in 4e. Electrum exists in exactly one. |
| Encounter budgets and XP | Three answers to the same question. Pathfinder's budget is per party with a size adjustment and the counter resets each level; D&D 2024's is per character and accumulates, with the award undivided; 4e's is per character and accumulates, and the award is **divided by party size**. |
| Conditions, by name | All three have *frightened* or *prone*; only Pathfinder counts *frightened* as a value. 4e has *marked* and *dominated*, which neither sibling has, and *bloodied* is a real condition there where in D&D 2024 it is a flag with no effect. |
| "Saving throw" | Not even the same **kind of roll**. In Pathfinder and D&D 2024 it is a defence roll. In 4e it is an **effect-ending** roll against a flat 10, and the defence roll does not exist — the attacker rolls against a static Fortitude, Reflex or Will. This is the most dangerous shared word in the framework. |

---

## Scope: the only translation

Four bands, named for the size of the thing a character can plausibly threaten or protect.

| Band | What it means |
|---|---|
| `local` | a farmstead, a village, a city ward — people who know each other by name |
| `regional` | a city and the land that feeds it; a barony; a stretch of coast |
| `national` | a kingdom, a great city-state, a region; the doorstep of another plane |
| `worldly` | the world itself, or the order of the planes |

**In D&D 2024 these are published.** SRD 5.2's "Tiers of Play" gives levels 1–4 as threats to
"local farmsteads or villages", 5–10 as "dangers that threaten cities and kingdoms", 11–16 as
"threats to whole regions", and 17–20 as "the fate of the world or even the order of the
multiverse". The SRD says in as many words that "these tiers don't have any rules associated with
them" — they describe how big the stakes get, which is exactly and only what this framework uses
them for.

**In Pathfinder the mapping is this framework's own convention.** Pathfinder publishes no tier
table: it has twenty levels and no banding of them. The same 1–4 / 5–10 / 11–16 / 17–20 split is
used so that one world can describe reach without naming a ruleset.

**In 4e the structure is published and the mapping still is not.** 4e does band its **thirty**
levels, into three tiers of ten — Heroic, Paragon, Epic — and the books describe each tier's reach
in those terms. But 4e has no open-content release, so there is no text to quote and the mapping
onto this framework's four bands is this framework's own: the Heroic tier split at 5 into `local`
and `regional`, the Paragon tier read whole as `national`, the Epic tier as `worldly`.

| Band | PF2e | D&D 2024 | D&D 4e |
|---|---|---|---|
| `local` | 1–4 | 1–4 | 1–5 |
| `regional` | 5–10 | 5–10 | 6–10 |
| `national` | 11–16 | 11–16 | 11–20 |
| `worldly` | 17–20 | 17–20 | 21–30 |

`python3 tools/rules.py bands` prints all three statements with that distinction intact. None of
it is a claim that a level 7 in one game and a level 7 in another are equivalent in play. They
are not, and the 4e column is the clearest demonstration: its `national` band is ten levels wide
where the others' is six.

```
$ python3 tools/world.py convert --level 7 --from pf2e --to dnd5e
PF2e level 7 → scope band **regional**
  which is: a city and the land that feeds it; a barony; a stretch of coast
  in D&D 5.5e, that band is levels 5-10
```

A band and a **range**, never a single number. The command then lists what it refuses to do, which
is the useful half of its output.

---

## Writing an entry that survives both readers

A chronicle entry is read by a campaign you have not written yet, possibly in another game.
Write it so that reader can use it.

| Instead of | Write |
|---|---|
| "Rolled a critical success on the ward" | "Opened a ward nobody local could open" |
| "A DC 28 Thievery check" | "A lock that had held for two centuries" |
| "Fought a CR 8 elemental" | "Fought something out of the deep stone that the Cove had no word for" |
| "Found a +2 greatsword" | "Took the blade the last captain carried, and it is still sharp" |
| "A level 12 party cleared it" | "Scope: regional" plus what they actually did |

Four questions to check an entry against:

1. Would this sentence mean the same thing to someone playing either of the other two games?
2. Does any number in it come from a rulebook?
3. Does it say how far the event reached?
4. Could a GM two campaigns later build a scene from it without looking anything up?

`promote` warns when another ruleset reads the world, and `validate.py --world` warns on an entry
mentioning a DC, an AC, a CR, a level or a dice expression. Both are prompts to re-read, not
permission to stop thinking.

---

## The calendar belongs to the world

One world keeps **one** calendar, whoever is playing in it. That is what lets a Pathfinder campaign
in 4725 AR and a D&D campaign in 4728 AR sit on the same timeline and gate each other's entries by
date.

- Pathfinder ships the Golarion (Absalom Reckoning) calendar, and `tools/pf2e.py` cites it.
- **SRD 5.2 publishes no calendar at all** — no months, no era. A D&D 2024 campaign therefore uses
  the framework's placeholder (twelve 30-day months) unless its world says otherwise. The month
  names of published D&D settings are not SRD material and this framework does not reproduce them.
- **4e is the same, and for a stronger reason**: it has no open content at all, so its published
  settings' calendars cannot be reproduced here either. A 4e campaign uses the placeholder or the
  world's own.
- A world may define its own in `CALENDAR.md` as a small JSON block, and then **every** ruleset
  reads its months and its era. `python3 tools/rules.py calendars` lists what is registered,
  including the ones the worlds define. `tools/world.py link` adopts a world's calendar into a
  campaign's `state.json` and seats the clock on the start date, so it does not have to be set
  by hand.

For a cross-system world, declaring the calendar is worth doing explicitly even when it is a
built-in, so there is a single written answer rather than each campaign assuming.

---

## The gazetteer is the one place numbers are allowed

A market is where a world fact and a ruleset's maths unavoidably meet: "what can I buy here" has a
different shape in each game. `GAZETTEER.md` therefore carries **one column per ruleset** per
settlement — Pathfinder's item level, D&D 2024's highest purchasable rarity, 4e's item level
carried — and each campaign reads its own column.

4e's column needs a decision rather than a lookup: it prices items by **level and market price**
rather than by settlement size, and there is no published mapping from a town's population to
what is on its shelf. Decide what item level each market carries, write it in the gazetteer, and
stop deciding it again — see `system/dnd4e/09-loot-and-economy.md`.

**Pick each column from the place as described. Do not derive one from the other.** A converted
number would be a guess wearing a source's clothes, which is worse than a blank cell. Leave the
other column empty until a campaign in that game needs it, then decide it the same way the first
was decided: from what the settlement is.

---

## Characters appearing across the line

A legacy record names its ruleset, its level **in that ruleset**, and its scope band. When a
character from one game appears in a campaign running the other:

- **Rebuild them, do not convert them.** Read the legacy record for who they are, what they did,
  what they are owed and what they carry, then build that person under the target ruleset's own
  character rules and let the numbers land where they land.
- **The scope band is the brief.** A `regional` figure should feel like someone a city has heard of,
  whatever their sheet says.
- **Availability still binds.** `npc-with-permission` means asking, and crossing rulesets is not a
  loophole in that. If anything it is more reason to ask: the player's character is about to be
  rendered in a system they did not choose for them.

---

## What a cross-system world is actually good for

The usual argument for a shared world is continuity. A cross-system one adds something the
single-system version cannot do: **the same place, seen through a different set of rules**.

- A Pathfinder campaign's hard-won regional victory becomes the background a D&D party inherits —
  and the D&D party's maths will not reproduce it, which is the point. They are not the same
  heroes.
- The remembered-versus-real gap that `LEGENDS.md` exists for gets another axis. A deed done under
  one game's rules, retold by people who play by another's, is distorted before anyone embellishes.
- A system the player wants to try does not cost them their world.

What it is not good for is comparing the games. If an entry starts reading like a conversion
exercise, that is the signal to go back to what happened.
