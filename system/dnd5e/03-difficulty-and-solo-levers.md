# 03 (D&D 2024) — Difficulty and the solo levers

**Replaces `system/03-difficulty-and-solo-levers.md` for a campaign with `System: dnd5e`.**

A game designed for four to six characters, run for one. The problems are the same ones the
Pathfinder document names; **the tools for fixing them are almost entirely different**, because
this game's maths is shaped differently. Do not reach for a Pathfinder lever here.

---

## The problems, named

### Action economy
The worst of them, and worse here than on the Pathfinder side. A solo character takes **one
action** per round. Three goblins take three. There is no three-action turn to spend defensively,
and Dodge costs the whole action — so defending means not acting.

This is why **the ally is the primary lever in this game**, not a secondary one.

### No role coverage
Four characters cover melee, ranged, magic, healing and skills. One covers two of those. In this
game the gap that hurts most is **healing**, because there is no out-of-combat self-repair that
does not cost the action economy: Hit Dice only come back on a Long Rest, and a character at 0 HP
cannot stabilise themselves.

### Focused fire
Every attack in the encounter goes at one AC and one HP pool. A budget priced for that damage to be
spread across four bodies lands entirely on one.

### Bounded accuracy cuts both ways
The design that keeps low-level monsters relevant at high level also means **a solo character
cannot out-scale a threat the way a Pathfinder character can**. There is no level-based DC ladder
climbing with them and no item bonus curve to lean on. A CR 2 creature is dangerous at level 5 in a
way its Pathfinder equivalent is not.

### Single point of failure
One character means one failed save, one critical hit, one massive-damage hit. **Massive damage is
the sharpest version of this in any edition**: no save, no dying track, no wounded counter — damage
past 0 that meets the maximum simply kills. A level 3 character on 8 of 24 HP can die to one hit
with no roll to resist it.

### The Death Save is a coin flip with nobody to call it
Three successes or three failures on a flat d20 against DC 10, with no modifier. In a party someone
makes a Medicine check. Alone, the character is 50/50 per round against their own death and there
is no intervention available.

---

## The levers

Four kinds. Reach for party-shape and information first; they cost the least and distort the least.

### Party-shape levers
1. **A GM-run ally.** The strongest lever this game has. Doubles the action economy and provides
   somebody who can make the DC 10 Medicine check. Keep them mechanically simple and narratively
   subordinate — they are not a co-protagonist.
2. **A sidekick.** One attack, one useful reaction, no spell list. Half the lever at a tenth of the
   bookkeeping.
3. **A second PC.** Full control, double the bookkeeping, usually less attachment.
4. **Temporary allies for an arc.** A guide who leaves, a guard who dies, a rival who helps once.

### Maths levers
This game has fewer than Pathfinder, and the ones it has are blunter. Use them deliberately.

1. **Build to the per-character budget and no further.** The budget is linear, so this is simply
   correct rather than a concession. Nothing collapses at a party of one.
2. **Stay under two creatures per character** — the published guidance, and the single most
   effective knob at a solo table. One CR 2 is a very different fight from four CR 1/2s worth the
   same XP.
3. **Prefer fewer, tougher creatures.** It inverts the action-economy problem instead of
   compounding it.
4. **Advantage as a reward, not a tax.** Granting Advantage for good play is worth about +3.3 on
   average and costs nothing to track. Imposing Disadvantage on the player is the same swing
   against them; use it far more sparingly than you grant it.
5. **Lower the creature count mid-fight in the fiction**, not the numbers. Morale, reinforcements
   that do not arrive, a flanker who goes for the horn instead.

**Levers this game does not have, so do not invent them:** there is no Elite/Weak template, no
proficiency-without-level variant, and no published DC-adjustment ladder. If you change a creature,
name it homebrew and record it.

### Safety-net levers
1. **Heroic Inspiration, freely.** A reroll of any die, published, costs nothing, and does not
   scale the monsters. **This is the cheapest and best safety net in this game.** Award it for good
   play, in-character choices, and anything that made the session better.
2. **Massive damage announced, then never sprung.** Say the rule out loud once at level 1.
3. **An ally who can stabilise.** See above. This is a mechanical requirement disguised as a
   narrative choice.
4. **Potions in the loot.** Common, cheap, and the only self-administered healing a character has
   mid-fight.
5. **A visible retreat.** Every dangerous encounter should have a way out that the player can see,
   and Disengage should be worth taking.
6. **Monsters that take prisoners.** Capture is a scene; death is the end of the campaign.

### Information levers
1. **Telegraph.** Name what the thing is, what it did to the last people, and what it is about to
   do. A solo character cannot afford to learn by being hit.
2. **Say the numbers that are not secret.** The AC a player has already hit, the Speed of the thing
   chasing them, how far away it is in feet.
3. **Answer "what do I know about this" generously.** A knowledge check that fails should still
   yield the obvious.
4. **Show the objective and the clock.** `17-encounter-objectives.md`.

---

## The four presets

Four shapes of campaign, not four difficulty numbers. **These presets are this framework's own
convention**, not published rules. Record the choice in `state.json` and in `RULES_DELTAS.md`, and
tell the player which levers it pulls.

### `Story` — fiction first, combat rarely lethal
- Build to **Low**, and read the creature-count guidance strictly.
- A GM-run ally, kept alive.
- Heroic Inspiration awarded most sessions, often twice.
- **Massive damage off** — say so; it is a real change to a published rule.
- Death Saves rolled in public. On the third failure, offer a cost instead of a death (a lasting
  injury, a debt to whoever intervened, a year gone) and let the player choose.
- Retreat always available and always telegraphed.

### `Standard` — the 2024 rules as written, tuned for party size
- Build to **Low** or **Moderate**, which is one step gentler than the label suggests because the
  descriptions are written for a party.
- A GM-run ally recommended and assumed by the maths.
- Heroic Inspiration when earned.
- **Massive damage on, announced at level 1.**
- Death Saves public, rolled honestly, no intervention unless something in the fiction provides it.
- Two creatures per character as a hard ceiling.

### `Gritty` — resources matter, retreat is common, death is real
- Build to **Moderate**, occasionally **High** with a telegraphed way out.
- Ally optional; if there is none, say plainly what that means for Death Saves.
- Heroic Inspiration rarely.
- Massive damage on. Consider the published Extended Travel exhaustion rules, and track lifestyle
  expenses.
- Death Saves **private** (`transparency: mystery`), rolled honestly, displayed only as "worse" or
  "holding".
- Short rests interrupted often enough that Hit Dice are a real decision.

### `Nightmare` — no safety nets, full attrition
- Build to **High**, and let the creature-count guidance be the only mercy.
- No ally unless the player recruits one in the fiction and keeps them alive.
- No Heroic Inspiration except where a rule grants it.
- Massive damage on. Exhaustion tracked from travel, lack of sleep and anything else that earns it.
- Death is death. **Agree this one explicitly before the first session** — a campaign that ends in
  session two because a goblin crit is a legitimate outcome here, and it must be a choice the
  player made knowingly.

### Changing preset mid-campaign
Legitimate, at any time, in either direction, and it does not need a reason. Record the change and
the session it changed in. `meta:` and `dial it back` / `dial it up` are the player's handles on
this and are honoured without argument.

---

## The difficulty check-in

### After every significant encounter
One line, out of character: *"That one ran close — was that the pressure you want, or more than
it?"* Then do what they say.

### Every few sessions
- `python3 tools/analyze.py --campaign X --fairness` — the dice, and whether the public and private
  subsets diverge.
- Count how many fights ended in something other than everything hostile dying. Aim for half.
- Count Death Saves rolled. More than one per two sessions at `Standard` means the encounters are
  running harder than the label.
- Count Heroic Inspiration awarded. Zero over three sessions at `Story` or `Standard` means the
  cheapest safety net is sitting unused.
- **Say what the numbers show, including when they show the campaign is too easy.** Burying drift
  under reassurance is the failure this check-in exists to prevent.
