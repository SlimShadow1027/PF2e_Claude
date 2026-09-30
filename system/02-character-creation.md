# 02 — Character creation

Three paths. Offer all three and let the player pick.

- **Quick build** — pick a class, accept sensible defaults, playing in five minutes.
- **Guided** — step by step, each choice explained, with what it costs and what it buys.
- **Import** — the player pastes a sheet from Pathbuilder or anywhere else and the GM parses it.

Everything below is PF2e **Remaster** (Player Core, Player Core 2). Where a choice is uncommon
or rare, name the book and page.

---

## The build steps, in order

PF2e builds in a fixed order and the order matters, because later steps depend on earlier ones.

### 1. Ancestry

Gives HP, Size, Speed, attribute boosts, an attribute flaw in some cases, traits, and access
to ancestry feats. Ask what the character *is* before asking what they *do*.

### 2. Heritage

A variant within the ancestry, chosen at level 1 and never changed.

### 3. Background

Two attribute boosts (one from a short list, one free), a skill, a Lore skill, and a skill
feat. Backgrounds are also the cheapest place to attach the answer to "why is this character
the one who acts" from intake.

### 4. Class

Gives the key ability, HP per level, initial proficiencies, the level-1 class feature, and
the class DC.

### 5. Key ability and the four free boosts

At level 1 a character takes: ancestry boosts, background boosts, the class key ability boost,
and **four free boosts**, no two to the same attribute. A boost is +2 below 18, +1 at 18 or
above.

### 6. Class feature and level-1 feats

The level-1 class feature choice (subclass, doctrine, order, style — whatever the class calls
it), plus the ancestry feat at level 1. Some classes grant a class feat at 1; most do not.

### 7. Skills

Trained in: the class's fixed list + the class's number of free skills + **Intelligence
modifier** more + the background's skill and Lore.

### 8. Starting gold and gear

15 gp (150 sp) at level 1, or the level-appropriate allowance for a higher starting level.
Record the gear with its Bulk — `tools/state.py item add ... --bulk 1` — so the encumbrance
check in `validate.py` has something to check.

### 9. Derived statistics

Compute each of these and show the working, so an error is visible now rather than at level 5:

| Statistic | From |
|---|---|
| HP | ancestry HP + (class HP + Con modifier) × level |
| AC | 10 + Dex (capped by armour) + proficiency + item bonus |
| Fortitude / Reflex / Will | 10-less form: modifier + proficiency + item; the save bonus is attribute + proficiency + item |
| Perception | Wis + proficiency + item |
| Class DC | 10 + key ability + proficiency |
| Spell attack / spell DC | key ability + proficiency (+10 for the DC) |
| Speed | ancestry, less any armour penalty |
| Bulk limits | encumbered after 5 + Str, maximum 10 + Str |

Proficiency adds **level + 2/4/6/8** for trained/expert/master/legendary unless the
Proficiency Without Level variant is on.

> Sources: the build sequence and derived-statistic formulas are Player Core. The Bulk limits
> are verified — `python3 tools/pf2e.py sources` (`map`, and `state.py bulk_report`). The
> item-bonus expectations by level are verified against Automatic Bonus Progression —
> `python3 tools/pf2e.py tables item-bonuses`.

---

## The quick-build path

1. "Pick a class, or say what you want to *do* in a fight and I will pick."
2. The GM proposes: ancestry, heritage, background, key ability, the four boosts, the level-1
   feature and feat, skills, and a kit — all in one message, each with one clause of
   justification.
3. The player changes anything they dislike.
4. The GM writes `characters/<name>.md` from
   `templates/characters/_CHARACTER_TEMPLATE.md` and registers the volatile numbers:

```
python3 tools/state.py --campaign <slug> add-character "Kaelen" \
    --kind pc --level 1 --hp 22 --ac 18 --fort 8 --ref 5 --will 6 \
    --perception 5 --speed 25 --str-mod 4 --hero-points 1
python3 tools/state.py --campaign <slug> slots set kaelen 1 2
python3 tools/state.py --campaign <slug> focus set kaelen 1 --max 1
```

5. `python3 tools/validate.py --campaign <slug>` — it will complain if the sheet file is
   missing or the numbers are impossible.
6. Checkpoint.

## The guided path

Same steps, one at a time, each with: what the choice does mechanically, what it rules out,
and two or three options that suit what the player has said they want. Never present more than
five options for one decision.

## The import path

The player pastes a sheet. The GM:

1. Parses it into the template, keeping the player's own names for things.
2. **Re-derives every derived number from scratch** and reports any disagreement with the
   pasted sheet, rather than trusting either copy silently.
3. Flags anything that is not in the Remaster — legacy alignment, removed feats, renamed
   spells — and asks how to translate it.
4. Registers the volatile numbers in `state.json` as above.

Pathbuilder JSON export is not round-tripped; importing a pasted sheet is supported, keeping a
bidirectional exporter against an undocumented format is not.

---

## Party structure

From intake (`01-campaign-intake.md`, block 7). Whatever the shape, register every character
the GM runs in `state.json` too, with `--kind ally` / `sidekick` / `companion`, so their HP and
conditions are tracked in the same one place.

- **Full PC ally** — built with all the steps above. Two full sheets to run, and the closest
  thing to a real party.
- **Sidekick** — a simplified companion: fewer feats, one job, no spell list. Faster to run,
  and less likely to steal the spotlight.
- **Animal companion / familiar / eidolon** — comes from a class feature; build it as that
  feature specifies.
- **Narrative-only ally** — present in the fiction, absent from the initiative order. Cheap,
  and honest about being scenery.

---

## The rules-variant menu

Present this table, say which are official, and **apply none of them without an explicit yes.**

| Lever | Effect | Difficulty | Official? |
|---|---|---|---|
| Free Archetype | A free archetype feat at every even level | easier / more versatile | **Official** — GM Core variant |
| Ancestry Paragon | A free ancestry feat at every odd level | easier | **Official** — GM Core variant |
| Dual Class | Build as two classes at once | much easier — strong for one-PC play | **Official** — GM Core variant |
| Automatic Bonus Progression | Item bonuses come from level instead of gear | smooths gear dependence | **Official** — GM Core variant |
| Proficiency Without Level | Removes level from proficiency; flattens the math | wider level range stays relevant | **Official** — GM Core variant |
| Gradual Attribute Boosts | Boosts spread across levels instead of in lumps | neutral | **Official** — GM Core variant |
| Stamina | Adds a stamina pool with easy between-encounter recovery | much easier attrition | **Official** — GM Core variant |
| Mythic / Mythic Callings | Mythic destinies, mythic points | large power spike | **Official** — War of Immortals |
| Elite / Weak creature adjustments | ±2 to most numbers, ±HP by level | direct difficulty dial | **Official** — GM Core |

Everything in `03-difficulty-and-solo-levers.md` beyond that table — bonus reactions,
per-scene Hero Point refresh, auto-stabilise, enemy-count caps, "no death without consent" —
is **this framework's suggestion, not a published rule**, and is labelled as such in
`RULES_DELTAS.md`.

### What to recommend for one PC

If the player wants a recommendation rather than a menu:

- **Free Archetype** is the single best fit. A solo character has gaps a party would cover,
  and an archetype is the cheapest way to fill one without changing the math.
- **Dual Class** if they want to feel like two characters rather than one with a hobby. It is
  a large power increase and should come with a matching difficulty preset.
- **Automatic Bonus Progression** if tracking gear upgrades sounds like a chore. It removes
  the "did I miss a +1 weapon" failure mode entirely.
- **Proficiency Without Level** only if the campaign wants low-level threats to stay
  dangerous at high level. It changes almost every DC in play, so decide it at level 1.
- **Weak adjustment on mooks** is not a character-creation choice, but say now that it will be
  the default, because it changes what a "moderate" encounter feels like.

Record every yes in `RULES_DELTAS.md` with its effect **and its difficulty delta**, then:

```
python3 tools/state.py --campaign <slug> preset Standard
python3 tools/state.py --campaign <slug> checkpoint "character created: Kaelen"
```

---

## Level 1 is not the last time this document gets read

`11-leveling-up.md` re-derives every number on the sheet from scratch at each level and diffs
it against the old values, so an error made here is caught at level 2 rather than at level 11.
