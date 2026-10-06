# 02 (D&D 4e) — Making a character

**Replaces `system/02-character-creation.md` for a campaign with `System: dnd4e`.**

> **What this document cannot give you.** Race and class entries, the powers each class
> knows, feats, backgrounds, themes, the point-buy table and the standard array are all
> non-open 4e content. This framework will not reproduce them. **You build the character from
> your own books**; what follows is the interview, the order of operations, and how the result
> is recorded so the tools can run it. See `system/dnd4e/README.md`.

---

## Before the dice: the interview

Same as the other two rulesets — one human plays at this table, so the character is the
campaign's centre of gravity, not one fifth of it.

1. **What kind of trouble do you want to be in?** Record the answer in `FLAGS.md`.
2. **What are your lines and veils?** `PLAYER_PREFS.md`. These outrank everything.
3. **How much rules weight do you want to carry?** 4e asks more bookkeeping of a player than
   either sibling: powers are cards, conditions are frequent and fiddly, and the grid matters.
   A player who wants a light touch should say so now and let the GM track more of it.
4. **Which role do you want to play?** This is the 4e-specific question, and it matters more
   here than a class choice does elsewhere.

### The four character roles

| Role | What it does |
|---|---|
| **Controller** | Shapes the battlefield; hits several enemies; imposes conditions |
| **Defender** | Holds enemies in place with marks and punishes them for leaving |
| **Leader** | Heals, grants attacks and movement, hands out bonuses |
| **Striker** | Concentrated damage on one target |

**For a solo campaign this choice has teeth.** A five-character party covers all four roles; a
party of one covers at most one. Whatever you do not pick is a hole in the party that the
fiction has to fill. The two that bite hardest alone:

- **No leader** means **nobody but you can spend your healing surges for you**, and no free
  healing between encounters. The surge pool is the attrition clock, so a party with no leader
  burns through the day faster. `03-difficulty-and-solo-levers.md` has the levers.
- **No defender** means nothing stops an enemy walking past you. 4e monsters are built
  expecting someone to be marked.

Say which hole you are leaving open, out loud, and write it in `CAMPAIGN.md`. A solo campaign
that pretends the roles are decoration ends in a surprise.

---

## Building the character

From your books, in this order. Nothing here is a number this framework can supply.

1. **Race**, which gives ability bonuses, a speed, a racial power and skill bonuses.
2. **Class**, which gives a role, hit points at first level and per level, a healing surge
   count, trained skills, class features and the powers you choose from.
3. **Ability scores**, by whichever method your table uses.
4. **Powers**: your at-wills, one encounter power, one daily, as the class says.
5. **Skills**, trained from the class's list.
6. **Feat**, one at first level.
7. **Equipment**, from the starting gold or kit the class gives.
8. **Then do the arithmetic**: the four defences, attack bonuses, initiative, and hit points.

### The arithmetic that is easy to get wrong

- **Half your level, rounded down**, is added to attack rolls, all four defences, all skill
  checks and initiative. At level 1 that is 0, which is why it is so easy to forget — and why
  the character stops working at level 3 if you do.
- **Each defence is 10 + half level + the better of two ability modifiers + armour or class
  bonuses.** Fortitude pairs Strength and Constitution, Reflex pairs Dexterity and
  Intelligence, Will pairs Wisdom and Charisma. **The better of the pair, not both.**
- **Healing surges per day** is the class's own number **plus the Constitution modifier**.
- **Speed is in squares**, from the race, adjusted by armour. Record squares, not feet.

---

## Recording it

```
python3 tools/state.py --campaign X add-character "Verrin Ash" \
    --kind pc --level 1 --hp 29 --ac 16 --fort 13 --ref 14 --will 12 \
    --str 14 --con 16 --dex 18 --int 10 --wis 12 --cha 8 \
    --surges 7 --initiative 4 --speed 6
```

> **`--fort`, `--ref` and `--will` mean something different here.** In a Pathfinder campaign
> those flags take **save modifiers**. In a 4e campaign they take the **defence totals**,
> like AC. Same flags, different quantity, because the games put the number on a different
> side of the table. The tool records what you pass; it cannot tell a 13 that means a defence
> from a 13 that means a modifier, so get it right at entry.

`--surges` takes the **class's** number; the Constitution modifier is added for you. Leave it
out and the character has an empty surge pool, which `add-character` warns about in capitals —
a 4e character with no surges cannot be healed at all.

Then record the powers that have something to spend:

```
python3 tools/state.py --campaign X power add verrin-ash "Twin Strike" encounter
python3 tools/state.py --campaign X power add verrin-ash "Hunter's Bear Trap" daily
```

At-will powers are deliberately **not** recorded — there is nothing to track, and a list of
them in `state.json` would be a second copy of the character sheet waiting to disagree with the
first. They belong in `characters/<key>.md`.

Finally, write the prose sheet at `campaigns/X/characters/<key>.md`: the full power list with
their text, the feats, the gear, and who this person is. `state.json` holds the volatile
numbers; the Markdown holds the built character. `validate.py` errors if the sheet is missing.

---

## What the sheet should show you at a glance

```
python3 tools/state.py --campaign X render
```

The 4e checkpoint table carries **HP · AC · Fort · Ref · Will · Surges · AP · 2nd wind ·
Conditions** — the four defences rather than one AC and three saves, and the surge pool rather
than Hit Dice. Two derived numbers are worth writing on the prose sheet in bold, because they
are what the GM will ask for mid-fight:

- **Bloodied value** — half of maximum hit points. A real condition, with powers keyed to it.
- **Death threshold** — the bloodied value, negative. A 29 HP character dies at −14.
- **Surge value** — a quarter of maximum hit points, rounded down.

`add-character` prints all three when you give `--hp`, and `state.py surge list` recomputes the
surge value whenever you ask.

---

## Levelling

`system/dnd4e/11-leveling-up.md`. In brief: thirty levels, three tiers, and **every level gives
something** — the half-level bonus moves on even levels, and the odd ones carry the feats,
powers and ability bumps.
