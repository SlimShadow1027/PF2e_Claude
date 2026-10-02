# 02 (D&D 2024) — Character creation

**Replaces `system/02-character-creation.md` for a campaign with `System: dnd5e`.** Read
`03-difficulty-and-solo-levers.md` (the D&D one) immediately after, and propose a difficulty preset
and party shape before the first scene.

Three paths, same as the Pathfinder side: **quick build** (playing in five minutes), **guided**
(step by step), or **import** (paste a sheet and it gets parsed and re-derived). Ask which.

> **What this framework does not contain.** No class, species, feat, spell or item text. Those are
> in the books, or in SRD 5.2 at <https://www.dndbeyond.com/srd>, which is free and covers twelve
> classes, their subclasses, the 2024 species, backgrounds, feats, equipment and spells. This
> document is the *procedure*; look the content up.

---

## The build steps, in order

### 1. Class
What they do in a fight and out of it. Pick this first — in the 2024 rules the class decides the
most about how the character plays, and everything numeric below depends on it.

Record: the class, its **Hit Die**, its **two saving throw proficiencies**, its armour and weapon
training, and its skill choices.

### 2. Origin: background and species
**Background** is where the 2024 ability score increases live, which is the big change from 2014.
A background gives:
- **+2 to one ability and +1 to another, or +1 to three** — chosen from the three abilities that
  background names.
- an **origin feat**
- two skill proficiencies, one tool proficiency, and starting equipment or 50 gp

**Species** gives size, Speed, and its own traits — and in the 2024 rules it gives **no ability
score increases at all**. If you find yourself adding a racial +2, that is the 2014 rule.

### 3. Ability scores
Standard array **15, 14, 13, 12, 10, 8**, or point buy, or 4d6-drop-lowest rolled with
`tools/roll.py` if the player wants the dice to decide. Then apply the background's increases.

```
python3 tools/roll.py expr "4d6kh3" "4d6kh3" "4d6kh3" "4d6kh3" "4d6kh3" "4d6kh3" --campaign X
```

A modifier is the score minus 10, halved and rounded down.

### 4. Alignment and the rest of the character
Alignment is in the glossary and carries no mechanics. Name the character, decide what they want,
and write one line about why they are the person who acts — that line matters more to play than
any number on this list.

### 5. Derived statistics

Compute each one and **show the arithmetic**, so the player can check it and so a later level-up
can diff against it.

| Number | How |
|---|---|
| **Proficiency Bonus** | +2 at levels 1–4 (see the table in `12-rules-quick-reference.md`) |
| **Hit Points** | at level 1, the Hit Die's **full** value + Con modifier |
| **Hit Dice** | one of the class's die per level |
| **AC** | 10 + Dex modifier, then armour. Only **one** base AC calculation may be in effect |
| **Initiative** | Dex modifier |
| **Attack bonus** | ability modifier + Proficiency Bonus if proficient with the weapon |
| **Damage** | the weapon's dice + the same ability modifier |
| **Saving throws** | ability modifier, + Proficiency Bonus for the class's two proficient saves |
| **Skills** | ability modifier, + Proficiency Bonus where proficient, doubled where Expertise applies |
| **Passive Perception** | 10 + Wisdom (Perception) total |
| **Spell save DC** | 8 + Proficiency Bonus + spellcasting ability modifier |
| **Spell attack** | Proficiency Bonus + spellcasting ability modifier |
| **Spell slots** | the class table. Full casters share one progression; half casters and Warlocks do not |
| **Carrying capacity** | Strength **score** × 15 lb at Medium or Small |
| **Weapon mastery** | the 2024 property on each weapon, where the class grants it |

Then write them in:

```
python3 tools/state.py --campaign X add-character "Thorne" --level 1 --hp 12 --ac 16 \
    --str 16 --dex 14 --con 14 --int 10 --wis 12 --cha 8 \
    --save str:+5 --save con:+4 --hit-die 10 --initiative +2 --passive-perception 13
```

`add-character` fills in the D&D half of the sheet and **ignores Pathfinder flags with a warning**
rather than storing them, so a sheet never carries a field its game does not have.

Spell slots, if any:

```
python3 tools/state.py --campaign X slots set thorne --rank 1 --max 2
```

---

## The quick-build path

Five minutes to playing. Offer it first — a solo player who wanted to start twenty minutes ago
should not be asked about tool proficiencies.

1. "Which of these do you want to be?" — four one-line pitches tied to the campaign's premise, each
   naming a class and a background without using those words.
2. Standard array, assigned to fit the pitch. Background increases applied.
3. Default equipment package for the class and background.
4. Skills and the origin feat chosen for them, announced rather than asked.
5. Everything derived, shown as arithmetic, and written to `state.json`.
6. **One question only**: "anything about them you want different before we start?"

Write the full sheet to `campaigns/<slug>/characters/<name>.md` as you go, so the choices made for
them are visible and reversible.

---

## The guided path

Steps 1–5 above, one or two questions at a time, with concrete example answers and a "pick for me"
option on every question. Never present more than four options; never ask a question whose answer
the player cannot yet have an opinion about.

Checkpoint after the build, before the first scene.

---

## The import path

The player pastes a sheet — from D&D Beyond, a VTT export, a block of text, a photo transcribed.

1. **Parse what is there** and list it back as a table: class, level, species, background, abilities,
   AC, HP, Hit Dice, saves, skills, proficiency bonus, spells and slots, equipment, feats.
2. **Re-derive every number from the parts** and diff it against what the sheet claims.
3. **Report every disagreement** rather than silently accepting either — "your sheet says AC 17; I
   derive 16 from Chain Mail 16 and no shield listed. Which is right, and what am I missing?"
4. **Ask about anything the sheet implies but does not state**: a feat that changes a derived
   number, an item bonus, a subclass feature altering AC or HP.
5. **Record the variant and house rules** the sheet reveals in `RULES_DELTAS.md`, named as such.
6. Only then write it to `state.json`.

A sheet that imports with four unexplained discrepancies is a sheet that will produce four wrong
rolls in session one.

---

## Party structure

See `03-difficulty-and-solo-levers.md` for what each shape does to the maths. The options:

| Shape | What it costs and buys |
|---|---|
| **One PC alone** | Hardest. One action per round against several; one death ends the campaign. Needs the safety-net levers. |
| **One PC + a GM-run ally** | The common recommendation. Doubles the action economy and gives someone who can stabilise. Keep the ally mechanically simple and narratively subordinate. |
| **Two PCs, both the player's** | Full tactical control, double the bookkeeping. Some players love it; most find it dilutes attachment. |
| **One PC + a sidekick** | A deliberately simple ally: one attack, one useful reaction, no spell list to run. |

This game has no published Summon-equivalent to lean on for action economy at low levels, and no
companion subsystem in the SRD. **An ally is the lever**, which makes the choice more consequential
here than on the Pathfinder side. Say so when recommending.

---

## The rules-variant menu

Offer these explicitly and record the answers in `RULES_DELTAS.md`. Each one is a real decision
about what the campaign feels like.

| Variant | Default | What it changes |
|---|---|---|
| **Rolled vs fixed HP on level-up** | fixed | Fixed is steadier, which matters more with one character |
| **Death saves in public or private** | public | Private is tenser; public lets the player plan. Transparency mode covers this |
| **Flanking / facing** | off | Not in SRD 5.2. Turning it on is houseruling; say so |
| **Feats at every even level** | off | A generosity lever. Off by default because it compounds |
| **Resting cadence** | as published | Gritty realism (short rest = 8 hours, long rest = 7 days) changes the whole resource game, and is not SRD content |
| **Critical hit on 19–20** | off | A generosity lever that also helps the monsters |
| **Massive damage** | **on** | It is published and it is lethal. Turning it off is a legitimate safety-net lever — say which you are doing |
| **Inspiration cadence** | as published | Awarding it freely is the cheapest safety net this game has |

### What to recommend for one PC

- **Fixed HP.** One bad roll at level 2 follows a solo character for twenty levels.
- **Massive damage on, and telegraphed.** Say out loud, once, early: "damage past 0 that meets your
  maximum kills outright, with no save." Then never spring it.
- **Generous Heroic Inspiration.** It is a reroll of any die, it costs the GM nothing, and it is
  the only published resource that can save a bad moment for a character with no party.
- **An ally who can make a Medicine check.** Stabilising is DC 10 Wisdom (Medicine) and there is
  nobody else to make it.
- **No flanking.** Bounded accuracy means a flat +2 or Advantage swings more here than it looks.

---

## Level 1 is not the last time this document gets read

`11-leveling-up.md` re-derives every number from scratch at each level and diffs it against what
was stored, which is how a bad modifier gets caught three levels after it was entered rather than
never. The arithmetic you show now is what that diff compares against, so show it.
