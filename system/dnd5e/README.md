# D&D 5e campaigns — the system overlay

This framework runs **two** game systems. A campaign's `state.json` names its system in the
`system` field: `pf2e` (the default, and what every campaign with no such field is) or `dnd5e`
(D&D Fifth Edition, **2024 rules**, as published in the **SRD 5.2.1**).

This file is the one extra document a 5e campaign reads. Everything in `system/` that is
about running a table — intake, the oracle, flags, canon, clocks, checkpoints, transparency
modes, table etiquette, session flow, shared worlds — applies **as written**. What changes is
the rules engine underneath, and this file says where.

**Read the whole of this file before running a 5e session.** It is short on purpose.

---

## ⚠ Every 5e number is unverified

Every table in `tools/dnd5e.py` carries a `Source:` line naming its SRD 5.2.1 section, and
**every one is marked `⚠ UNVERIFIED`**. They were written from the section names, but the SRD
host could not be reached when the file was written, so not one value has been read back
against the document. `python3 tools/dnd5e.py sources` prints the list.

Rule 5 of `CLAUDE.md` applies without softening: when you quote one of these numbers, say it
is unverified. When you get the chance to read the SRD (`media.dndbeyond.com` hosts the PDF),
verify a table, flip it to `verified=True` with the page cited, and remove its line from
`DESIGN_NOTES.md`.

---

## Creating a 5e campaign

```
python3 tools/new_campaign.py "The Salt Road" --system dnd5e
```

Files under `templates/dnd5e/` replace the matching base templates: `RULES_DELTAS.md`, the
character form, the creature form and the loot ledger. Everything else is shared. Intake
(`system/01-campaign-intake.md`) is the same interview; where it offers PF2e-specific
answers (Golarion, Adventure Paths, Free Archetype), offer the 5e equivalent instead.

The calendar defaults to `generic` (12 months of 30 days, year 1). Name the setting's own
calendar during intake and record it in `CAMPAIGN.md`.

---

## The tools, in a 5e campaign

`roll.py` and `state.py` read the campaign's system from `state.json` whenever `--campaign`
is passed, so the same commands do the right thing. Commands that only make sense in the
other system **refuse** and name the command to use instead.

### Dice

```
python3 tools/roll.py check "1d20+5" --dc 15 --attack --dc-label AC --label "Longsword" --campaign X
python3 tools/roll.py check "1d20+5" --dc 15 --adv --label "Stealth" --campaign X
python3 tools/roll.py save  "1d20+2" --dc 13 --dis --private --actor "Goblin" --label "Dex save vs Burning Hands" --campaign X
python3 tools/roll.py damage "1d8+3" --crit --type slashing --label "Longsword crit" --campaign X
python3 tools/roll.py deathsave --actor Brin --campaign X        # or: state.py deathsave brin
```

| PF2e | 5e |
|---|---|
| four degrees of success; ±10 from the DC moves a step; natural 20/1 shift a step | **pass/fail**: meet or beat the DC. Natural 20/1 mean nothing on checks and saves |
| — | `--attack`: a natural 20 always hits and is a **Critical Hit**; a natural 1 always misses |
| `fortune` / `misfortune` | `--adv` / `--dis` (2d20, keep higher / lower). Both at once cancel to one d20 |
| `--crit` doubles the whole roll, modifiers included | `--crit` **doubles the dice**, modifiers added once |
| `--map 1/2` | refused — 5e has no multiple attack penalty |
| `recovery --dying N` | `deathsave` (DC 10; natural 20 regains 1 HP; natural 1 is two failures) |

The log records `system`, `attack`, `advantage` and `disadvantage` on every line, so
`analyze.py` can still audit the public/private split.

### State

| PF2e | 5e |
|---|---|
| Fort / Ref / Will / Perception | six saving throws (`--str-save` … `--cha-save`), passive Perception |
| Hero Points (`hero`) | Heroic Inspiration (`inspiration gain|spend|clear`) — you have it or you don't |
| Focus Points (`focus`) | none; class resources go on the sheet, or as an item with `--charges` |
| dying / wounded / doomed | death saves (`deathsave <who>`), `stable`, massive-damage instant death |
| drained, fatigued, enfeebled … | the 2024 conditions; **exhaustion** 0–6 is its own field (`exhaustion set`) |
| `daily-prep` | `long-rest` (all HP, all Hit Point Dice, slots, exhaustion −1); `daily-prep` is an alias |
| Treat Wounds, Refocus | `short-rest`, then `hitdice spend <who> <n>` (real dice, logged) |
| Sustain | `concentration <who> <spell>` / `--end`. Damage prints the Con save DC to roll |
| Bulk | weight — Strength × 15 lb., tracked on the sheet; `bulk` refuses |
| pp gp sp cp | pp gp **ep** sp cp |
| XP resets at 1000 per level | XP is cumulative; `xp add` says when a threshold is crossed |

```
python3 tools/state.py --campaign X add-character Brin --hp 12 --ac 16 --str-save 5 --con-save 4 \
    --con-mod 2 --hit-die d10 --passive-perception 13 --inspiration
python3 tools/state.py --campaign X damage brin 9 --from-crit
python3 tools/state.py --campaign X deathsave brin
python3 tools/state.py --campaign X encounter bonus brin "Second Wind"
```

### Rules tables

```
python3 tools/dnd5e.py encounter --party-level 3 --party-size 1 --difficulty moderate \
    --monsters "goblin warrior:1/4x3, hobgoblin:1/2"
python3 tools/dnd5e.py level --xp 1200
python3 tools/dnd5e.py dc hard
python3 tools/dnd5e.py rules death
python3 tools/dnd5e.py sources
```

---

## What changes in each `system/` document

| Document | In a 5e campaign |
|---|---|
| `02-character-creation` | Build from the 2024 rules: class, background (ability increases and an Origin feat), species. Use `templates/dnd5e/characters/_CHARACTER_TEMPLATE.md`. The sheet cites SRD 5.2.1 or the book for anything outside it. |
| `03-difficulty-and-solo-levers` | The levers are system-neutral and apply. Map them: Hero Points → Heroic Inspiration; Elite/Weak → choose a higher/lower CR, or adjust HP; "free Treat Wounds" → a free Short Rest. A solo 5e character is fragile at levels 1–2: prefer **Low** budgets and few enemies, and consider a GM-run ally. |
| `04-dice-protocol` | As written, with the dice table above. Secret checks are as rare in 5e as the GM makes them; passive scores replace many of them. |
| `06-encounter-runner` | A turn is **move + one action + one bonus action**, and one reaction per round (resets at the start of your turn). Offer **Opportunity Attacks** when a creature leaves reach, and **Shield** / **Counterspell** / class reactions before resolving their triggers, exactly as the PF2e reaction duty. A creature at 0 HP rolls its death save at the start of its turn — `encounter next` reminds you. |
| `07-encounter-building` | `tools/dnd5e.py encounter`: sum each character's budget for the difficulty, sum monster XP by CR, compare. The 2024 method has **no group-size multiplier**. `17-encounter-objectives` applies unchanged. |
| `08-npc-and-bestiary-protocol` | Rule 4 holds: every creature comes from published 5e material — SRD 5.2.1 or the 2024 Monster Manual — cited by name, source and CR. Homebrew names its base. Use `templates/dnd5e/bestiary/_CREATURE_TEMPLATE.md`. |
| `09-loot-and-economy` | Electrum exists. The DMG treasure tables are not in this repository; pacing is a judgement, recorded in `logs/loot.md`. Attunement limit: three. |
| `10-downtime-travel-and-rest` | Long Rest 8 h (one per 24 h), Short Rest 1 h. Travel pace from the SRD's Travel Pace table — not reproduced here; quote it with its source. |
| `11-leveling-up` | Level when `xp add` says so (or by milestone). Re-derive: HP (die average or roll — roll it with `roll.py`), proficiency bonus (`dnd5e.py level`), Hit Point Dice max (`hitdice set --max`), slots, features. |
| `12-rules-quick-reference` | PF2e only. For 5e, `python3 tools/dnd5e.py rules`, and the SRD. |
| `16-random-tables` | Names, rumours and weather are system-neutral. Treasure tables are PF2e. |

---

## Licence

SRD 5.2.1 is licensed under CC-BY-4.0. The attribution lives in `LICENSE_NOTES.md`. As with
PF2e, this repository holds mechanics and short rule statements only: no stat blocks, no spell
or class text. Look those up in the SRD or the books.
