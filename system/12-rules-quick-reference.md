# 12 — Rules quick reference

The cheat sheet to consult **instead of recalling from memory**. Every table carries a
`Source:` line, and any value that could not be checked against a source reachable from the
machine that built this framework is marked `⚠ UNVERIFIED`.

Run `python3 tools/pf2e.py sources` for the full provenance list, and see `DESIGN_NOTES.md`
for what still needs verifying before first play.

> **Verification note.** Archives of Nethys (`2e.aonprd.com`) was unreachable when this
> framework was built, so the numeric tables were checked against the Foundry VTT PF2e system
> source — an ORC-licensed implementation that cites AoN rule IDs inline — at version 8.5.1,
> commit `06b904d6ced9795c4c07af085e6f61a56f845c60`. That is a secondary source. Where it does
> not implement a table, the value here says so.

---

## Degrees of success

- Critical success: total >= DC + 10.
- Success: total >= DC.
- Failure: total < DC.
- Critical failure: total <= DC - 10.
- A natural 20 improves the degree by one step; a natural 1 worsens it by one step.

The natural-20 / natural-1 shift is applied **after** the base degree and is clamped, so a
natural 20 on an already-critical success stays a critical success.

**Flat checks have no degrees.** A DC 15 flat check succeeds or fails; a natural 20 does not
make it a critical success.

**Source:** Player Core / GM Core, Degrees of Success (https://2e.aonprd.com/Rules.aspx?ID=552). Verified against foundryvtt/pf2e v8.5.1 @06b904d6ced9795c4c07af085e6f61a56f845c60 (ORC implementation citing Archives of Nethys inline), src/module/system/degree-of-success.ts.

---

## The three-action economy

Each creature gets **3 actions** on its turn, plus **1 reaction** and any number of free
actions (each usable when its trigger occurs).

| | |
|---|---|
| `◆` | one action |
| `◆◆` | two actions (an activity) |
| `◆◆◆` | three actions |
| `↺` | a reaction — one per round, refreshed at the start of your turn |
| `◇` | a free action |

A reaction spent on another creature's turn stays spent until the start of your next turn.
The per-round tracker in `06-encounter-runner.md` has a reaction column, so
"you have no reaction available" is always backable.

---

## Multiple attack penalty

| Attack this turn | Normal | Agile |
|---|---|---|
| first | +0 | +0 |
| second | -5 | -4 |
| third or later | -10 | -8 |

The penalty resets at the start of each of your turns, and applies to attack rolls of any
kind made after the first that turn — weapon Strikes, spell attacks, and unarmed alike.

**Source:** Player Core, Multiple Attack Penalty: -5/-10, or -4/-8 agile. Verified against foundryvtt/pf2e v8.5.1 @06b904d6ced9795c4c07af085e6f61a56f845c60 (ORC implementation citing Archives of Nethys inline), src/module/actor/helpers.ts `calculateMAPs`.

---

## Level-based DCs

| Level | DC | | Level | DC | | Level | DC |
|---|---|---|---|---|---|---|---|
| -1 | 13 | | 8 | 24 | | 17 | 36 |
| 0 | 14 | | 9 | 26 | | 18 | 38 |
| 1 | 15 | | 10 | 27 | | 19 | 39 |
| 2 | 16 | | 11 | 28 | | 20 | 40 |
| 3 | 18 | | 12 | 30 | | 21 | 42 |
| 4 | 19 | | 13 | 31 | | 22 | 44 |
| 5 | 20 | | 14 | 32 | | 23 | 46 |
| 6 | 22 | | 15 | 34 | | 24 | 48 |
| 7 | 23 | | 16 | 35 | | 25 | 50 |

**Source:** GM Core, DCs by Level (https://2e.aonprd.com/Rules.aspx?ID=552). Verified against foundryvtt/pf2e v8.5.1 @06b904d6ced9795c4c07af085e6f61a56f845c60 (ORC implementation citing Archives of Nethys inline), src/module/dc.ts `dcByLevel`.

`python3 tools/pf2e.py dc --level 7 --rarity rare` prints one with its adjustments.

---

## Simple DCs by proficiency

| Proficiency | DC | DC with Proficiency Without Level |
|---|---|---|
| Untrained | 10 | 10 |
| Trained | 15 | 15 |
| Expert | 20 | 20 |
| Master | 30 | 25 |
| Legendary | 40 | 30 |

Use a simple DC when the task has no level of its own — a locked chest in a village, a
rumour anyone in the market could repeat. Use a level-based DC when it does.

**Source:** GM Core, Simple DCs (https://2e.aonprd.com/Rules.aspx?ID=552); the Proficiency Without Level column from the variant rule (https://2e.aonprd.com/Rules.aspx?ID=1370). Verified against foundryvtt/pf2e v8.5.1 @06b904d6ced9795c4c07af085e6f61a56f845c60 (ORC implementation citing Archives of Nethys inline), src/module/dc.ts `simpleDCs` / `simpleDCsWithoutLevel`.

---

## DC adjustments and rarity

| Adjustment | Modifier |
|---|---|
| Incredibly Easy | -10 |
| Very Easy | -5 |
| Easy | -2 |
| Normal | +0 |
| Hard | +2 |
| Very Hard | +5 |
| Incredibly Hard | +10 |

| Rarity | Adjustment | Modifier |
|---|---|---|
| Common | normal | +0 |
| Uncommon | hard | +2 |
| Rare | very hard | +5 |
| Unique | incredibly hard | +10 |

Rarity raises a DC; a relevant Lore skill lowers it by one step on the same scale.

**Source:** GM Core, Adjusting Difficulty and the rarity adjustments (https://2e.aonprd.com/Rules.aspx?ID=555). Verified against foundryvtt/pf2e v8.5.1 @06b904d6ced9795c4c07af085e6f61a56f845c60 (ORC implementation citing Archives of Nethys inline), src/module/dc.ts `dcAdjustments` and `rarityToDCAdjustment` (uncommon → hard +2, rare → very hard +5, unique → incredibly hard +10).

---

## Spell DCs

A spell's level-based DC is taken at **rank × 2 − 1** — a rank-3 spell uses the level-5 DC of 20.

Your own spell DC is **10 + key ability modifier + proficiency bonus (+ item bonus)**, and your
spell attack modifier is the same without the 10.

---

## Item bonus expectations by level

What the core math assumes gear is providing. Taken from Automatic Bonus Progression, which is
the official codification of that curve.

| Level | Attack | Striking dice | AC | Perception | Saves |
|---|---|---|---|---|---|
| 1 | +0 | +0 | +0 | +0 | +0 |
| 2 | +1 | +0 | +0 | +0 | +0 |
| 3 | +1 | +0 | +0 | +0 | +0 |
| 4 | +1 | +1 | +0 | +0 | +0 |
| 5 | +1 | +1 | +1 | +0 | +0 |
| 6 | +1 | +1 | +1 | +0 | +0 |
| 7 | +1 | +1 | +1 | +1 | +0 |
| 8 | +1 | +1 | +1 | +1 | +1 |
| 9 | +1 | +1 | +1 | +1 | +1 |
| 10 | +2 | +1 | +1 | +1 | +1 |
| 11 | +2 | +1 | +2 | +1 | +1 |
| 12 | +2 | +2 | +2 | +1 | +1 |
| 13 | +2 | +2 | +2 | +2 | +1 |
| 14 | +2 | +2 | +2 | +2 | +2 |
| 15 | +2 | +2 | +2 | +2 | +2 |
| 16 | +3 | +2 | +2 | +2 | +2 |
| 17 | +3 | +2 | +2 | +2 | +2 |
| 18 | +3 | +2 | +3 | +2 | +2 |
| 19 | +3 | +3 | +3 | +3 | +2 |
| 20 | +3 | +3 | +3 | +3 | +3 |

A character meaningfully behind this curve will feel it as a flat competence gap rather than
as a bad night. `09-loot-and-economy.md` has the treasure-pacing tracker that catches it.

**Source:** GM Core variant rule Automatic Bonus Progression, which states the item-bonus curve the core math assumes: attack potency at levels 2/10/16, striking dice at 4/12/19, defence potency at 5/11/18, perception potency at 7/13/19, save potency at 8/14/20. Verified against foundryvtt/pf2e v8.5.1 @06b904d6ced9795c4c07af085e6f61a56f845c60 (ORC implementation citing Archives of Nethys inline), src/module/actor/character/automatic-bonus-progression.ts (`getAttackPotency`, `getStrikingDice`, `getDefensePotency`, `abpValues`).

---

## Death, dying, wounded, doomed

- **dying max:** 4
- **recovery dc:** 10 + your current dying value
- **crit success:** dying value reduced by 2
- **success:** dying value reduced by 1
- **failure:** dying value increased by 1
- **crit failure:** dying value increased by 2
- **damage while dying:** +1, or +2 from a critical hit or a critical failure on a save
- **losing dying:** you gain wounded 1, or increase wounded by 1
- **starting dying:** dying 1 when reduced to 0 HP, +1 if the hit was a critical, plus your wounded value
- **doomed:** reduces the dying value at which you die by your doomed value

So the loop is: dropped to 0 HP → unconscious and dying 1 (or 2 from a critical, plus your
wounded value) → a recovery check at the start of each of your turns at DC 10 + dying →
success reduces it, failure raises it, dying 4 is death. Losing the condition leaves you
wounded, which makes the next time worse.

Roll it, and apply it, in one step:

```
python3 tools/state.py --campaign X recovery kaelen
```

**Source:** Player Core, the Dying, Wounded and Doomed conditions and the recovery check. Verified against the Foundry VTT PF2e condition compendium (packs/pf2e/conditions/dying.json, wounded.json, doomed.json) and src/module/actor/creature/document.ts, where the maximum dying value is 4 and the recovery DC is 10 + the dying value.

Wounded is removed by a successful Treat Wounds or by 24 hours of rest. Doomed and drained each
step down by 1 per full night's rest — `python3 tools/state.py --campaign X daily-prep` applies
that. Drained's lost hit points do **not** come back with the step-down.

---

## Flat checks

A flat check has no modifiers and no degrees of success: roll `1d20` against a DC.

| Situation | Flat check DC |
|---|---|
| Ending persistent damage at the end of your turn | 15 (11 if you spend actions to help) |
| Targeting a **concealed** creature | 5 |
| Targeting a **hidden** creature | 11 |
| A **deafened** creature using an auditory action | 5 |

⚠ The "11 if you take steps to help" figure for persistent damage, and the deafened DC, could
not be checked against a source reachable from this machine — see `DESIGN_NOTES.md`. The
concealed (5) and hidden (11) DCs come from the condition text below, which is verified.

---

## Cover, concealment, detection and flanking

| State | Effect |
|---|---|
| **Lesser cover** | +1 circumstance bonus to AC |
| **Standard cover** | +2 circumstance bonus to AC, and to Stealth to Hide/Sneak |
| **Greater cover** | +4 circumstance bonus to AC (needs a specific source, e.g. Take Cover) |
| **Flanking** | the flanked creature is **off-guard** to both flankers |
| **Off-guard** | −2 circumstance penalty to AC |

⚠ The cover bonuses are `⚠ UNVERIFIED` against a reachable source; the off-guard penalty and
the flanking definition are verified from the condition text below.

**Flanking** requires you and an ally to be on opposite sides of the target, both able to act,
both wielding a melee weapon or unarmed attack, and each able to reach it.

### Detection states

From the verified condition text: **observed** → **concealed** (DC 5 flat check to target) →
**hidden** (DC 11, you know roughly where) → **undetected** (you do not know where) →
**unnoticed** (you do not know it exists).

---

## Basic saves

"Basic Fortitude save" and the others resolve as:

| Degree | Effect |
|---|---|
| Critical success | no damage |
| Success | half damage |
| Failure | full damage |
| Critical failure | double damage |

---

## Immunity, weakness and resistance — the order

Apply in this order, and say you did:

1. **Immunity** — the damage does not apply at all.
2. **Doubling and halving** from the effect itself (a critical hit, a basic save).
3. **Resistance** — subtract it.
4. **Weakness** — add it.

Resistance and weakness to the same damage type cancel to the difference, applied once.

⚠ `⚠ UNVERIFIED` against a reachable source. The order matters mostly at the margins, but say
which order was used when it changes an outcome.

---

## Hero Points

| | |
|---|---|
| Starting | 1 at the beginning of each session (this framework's presets often raise it) |
| Spend 1 | **reroll** a check you just made, taking the second result — this is a **fortune** effect |
| Spend all | **avoid death**: you lose the dying condition and are restored to 1 HP |

A reroll is `2d20kh1`: both dice are rolled and both are logged.

```
python3 tools/roll.py fortune "1d20+13" --dc 21 --label "Hero Point reroll" --actor Kaelen --campaign X
python3 tools/state.py --campaign X hero spend kaelen
```

A roll cannot be both fortune and misfortune; if both would apply, neither does, and `roll.py`
refuses the combination rather than picking one.

---

## Common actions worth having to hand

| Action | Cost | Roll | Against |
|---|---|---|---|
| Strike | ◆ | attack roll | AC |
| Stride / Step | ◆ | — | — (Step is 5 feet and does not trigger reactions) |
| Grapple | ◆ | Athletics | target's Fortitude DC |
| Shove / Trip / Disarm | ◆ | Athletics | Fortitude / Reflex / Reflex DC |
| Escape | ◆ | Athletics, Acrobatics, or unarmed attack | the effect's DC |
| Raise a Shield | ◆ | — | grants the shield's circumstance bonus to AC |
| Shield Block | ↺ | — | reduces damage by the shield's Hardness |
| Recall Knowledge | ◆ | the relevant skill, **secret** | level-based DC, adjusted for rarity |
| Demoralize | ◆ | Intimidation | target's Will DC → **frightened 1** (2 on a critical) |
| Feint | ◆ | Deception | target's Perception DC → **off-guard** to your next melee attack |
| Aid | ↺ | the relevant skill, DC 15 by default | prepared with a ◆ on a previous turn |
| Take Cover | ◆ | — | standard → greater cover, or lesser → standard |
| Administer First Aid | ◆◆ | Medicine | stabilise a dying creature, or stop bleeding |

Grapple, Shove, Trip and Disarm are **attack** actions and so raise the multiple attack
penalty.

⚠ The Grapple/Shove/Trip/Disarm target DCs and the Aid DC are `⚠ UNVERIFIED` against a
reachable source. Check them before a fight turns on one.

---

## Every condition, with its exact mechanical effect

Verbatim from the Player Core condition text, verified against the Foundry VTT PF2e condition
compendium (`packs/pf2e/conditions/*.json`, v8.5.1). Conditions marked **valued** always carry
a number.

### Blinded

You can't see. All normal terrain is difficult terrain to you. You can't detect anything using vision. You automatically critically fail Perception checks that require you to be able to see, and if vision is your only precise sense, you take a –4 status penalty to Perception checks. You are immune to visual effects. Blinded overrides Dazzled.

### Broken

Broken is a condition that affects only objects. An object is broken when damage has reduced its Hit Points to equal or less than its Broken Threshold. A broken object can't be used for its normal function, nor does it grant bonuses—with the exception of armor. Broken armor still grants its item bonus to AC, but it also imparts a status penalty to AC depending on its category: –1 for broken light armor, –2 for broken medium armor, or –3 for broken heavy armor.

A broken item still imposes penalties and limitations normally incurred by carrying, holding, or wearing it. For example, broken armor would still impose its Dexterity modifier cap, check penalty, and so forth. If an effect makes an item broken automatically and the item has more HP than its Broken Threshold, that effect also reduces the item's current HP to the Broken Threshold.

### Clumsy  — *valued*

Your movements become clumsy and inexact. Clumsy always includes a value. You take a status penalty equal to the condition value to Dexterity-based rolls and DCs, including AC, Reflex saves, ranged attack rolls, and skill checks using Acrobatics, Stealth, and Thievery.

### Concealed

You are difficult for one or more creatures to see due to thick fog or some other obscuring feature. You can be concealed to some creatures but not others. While concealed, you can still be Observed, but you're tougher to target. A creature that you're concealed from must succeed at a [flat|showDC:all|dc:5] when targeting you with an attack, spell, or other effect. If the check fails, you aren't affected. Area effects aren't subject to this flat check.

### Confused

You don't have your wits about you, and you attack wildly. You are Off-Guard, you don't treat anyone as your ally (though they might still treat you as theirs), and you can't Delay, Ready, or use reactions.

You use all your actions to Strike or cast offensive cantrips, though the GM can have you use other actions to facilitate attack, such as draw a weapon, move so target is in reach, and so forth. Your targets are determined randomly by the GM. If you have no other viable targets, you target yourself, automatically hitting but not scoring a critical hit. If it's impossible for you to attack or cast spells, you babble incoherently, wasting your actions.

Each time you take damage from an attack or spell, you can attempt a [flat|showDC:all|dc:11] to recover from your confusion and end the condition.

### Controlled

You have been commanded, magically dominated, or otherwise had your will subverted. The controller dictates how you act and can make you use any of your actions, including attacks, reactions, or even Delay. The controller usually doesn't have to spend their own actions when controlling you.

### Cursebound  — *valued*

Your oracular curse is constricting around you as you receive divine punishment after drawing too deeply on your mystery's powers. Cursebound is a condition that affects only creatures with an oracular curse, and cursebound always includes a value. Your specific oracular curse imposes unique negative effects depending on your cursebound value. You can remove the cursebound condition only by Refocusing.

### Dazzled

Your eyes are overstimulated or your vision is swimming. If vision is your only precise sense, all creatures and objects are Concealed from you.

### Deafened

You can't hear. You automatically critically fail Perception checks that require you to be able to hear. You take a –2 status penalty to Perception checks for initiative and checks that involve sound but also rely on other senses. If you perform an action that has the auditory trait, you must succeed at a [flat|showDC:all|dc:5] or the action is lost; attempt the check after spending the action but before any effects are applied. You are immune to auditory effects while deafened.

### Doomed  — *valued*

Your soul has been gripped by a powerful force that calls you closer to death. Doomed always includes a value. The Dying value at which you die is reduced by your doomed value. If your maximum dying value is reduced to 0, you instantly die. When you die, you're no longer doomed.

Your doomed value decreases by 1 each time you get a full night's rest.

### Drained  — *valued*

Your health and vitality have been depleted as you've lost blood, life force, or some other essence. Drained always includes a value. You take a status penalty equal to your drained value on Constitution-based rolls and DCs, such as Fortitude saves. You also lose a number of Hit Points equal to your level (minimum 1) times the drained value, and your maximum Hit Points are reduced by the same amount. For example, if you become drained 3 and you're a 3rd-level character, you lose 9 Hit Points and reduce your maximum Hit Points by 9. Losing these Hit Points doesn't count as taking damage.

Each time you get a full night's rest, your drained value decreases by 1. This increases your maximum Hit Points, but you don't immediately recover the lost Hit Points.

### Dying  — *valued*

You are bleeding out or otherwise at death's door. While you have this condition, you are Unconscious. Dying always includes a value, and if it ever reaches dying 4, you die. When you're dying, you must attempt a recovery check at the start of your turn each round to determine whether you get better or worse. Your dying condition increases by 1 if you take damage while dying, or by 2 if you take damage from an enemy's critical hit or a critical failure on your save.

If you lose the dying condition by succeeding at a recovery check and are still at 0 Hit Points, you remain unconscious, but you can wake up as described in that condition. You lose the dying condition automatically and wake up if you ever have 1 Hit Point or more. Any time you lose the dying condition, you gain the Wounded 1 condition, or increase your wounded condition value by 1 if you already have that condition.

### Encumbered

You are carrying more weight than you can manage. While you're encumbered, you're Clumsy 1 and take a 10-foot penalty to all your Speeds. As with all penalties to your Speed, this can't reduce your Speed below 5 feet.

### Enfeebled  — *valued*

You're physically weakened. Enfeebled always includes a value. When you are enfeebled, you take a status penalty equal to the condition value to Strength-based rolls and DCs, including Strength-based melee attack rolls, Strength-based damage rolls, and Athletics checks.

### Fascinated

You're compelled to focus your attention on something, distracting you from whatever else is going on around you. You take a –2 status penalty to Perception and skill checks, and you can't use concentrate actions unless they (or their intended consequences) are related to the subject of your fascination, as determined by the GM. For instance, you might be able to Seek and Recall Knowledge about the subject, but you likely couldn't cast a spell targeting a different creature. This condition ends if a creature uses hostile actions against you or any of your allies.

### Fatigued

You're tired and can't summon much energy. You take a –1 status penalty to AC and saving throws. You can't use exploration activities performed while traveling.

You recover from fatigue after a full night's rest.

### Fleeing

You're forced to run away due to fear or some other compulsion. On your turn, you must spend each of your actions trying to escape the source of the fleeing condition as expediently as possible (such as by using move actions to flee, or opening doors barring your escape). The source is usually the effect or creature that gave you the condition, though some effects might define something else as the source. You can't Delay or Ready while fleeing.

### Friendly

This condition reflects a creature's disposition toward a particular character, and only supernatural effects (like a spell) can impose this condition on a PC. A creature that is friendly to a character likes that character. It is likely to agree to Requests from that character as long as they are simple, safe, and don't cost too much to fulfill. If the character (or one of their allies) uses hostile actions against the creature, the creature gains a worse attitude condition depending on the severity of the hostile action, as determined by the GM.

### Frightened  — *valued*

You're gripped by fear and struggle to control your nerves. The frightened condition always includes a value. You take a status penalty equal to this value to all your checks and DCs. Unless specified otherwise, at the end of each of your turns, the value of your frightened condition decreases by 1.

### Grabbed

You're held in place by another creature, giving you the Off-Guard and Immobilized conditions. If you attempt a manipulate action while grabbed, you must succeed at a [flat|showDC:all|dc:5] or it is lost; roll the check after spending the action, but before any effects are applied.

### Helpful

This condition reflects a creature's disposition toward a particular character, and only supernatural effects (like a spell) can impose this condition on a PC. A creature that is helpful to a character wishes to actively aid that character. It will accept reasonable Requests from that character, as long as such requests aren't at the expense of the helpful creature's goals or quality of life. If the character (or one of their allies) uses a hostile action against the creature, the creature gains a worse attitude condition depending on the severity of the hostile action, as determined by the GM.

### Hidden

While you're hidden from a creature, that creature knows the space you're in but can't tell precisely where you are. You typically become hidden by using Stealth to Hide. When Seeking a creature using only imprecise senses, it remains hidden, rather than Observed. A creature you're hidden from is Off-Guard to you, and it must succeed at a [flat|showDC:all|dc:11] when targeting you with an attack, spell, or other effect or it fails to affect you. Area effects aren't subject to this flat check.

A creature might be able to use the seek action to try to observe you.

### Hostile

This condition reflects a creature's disposition toward a particular character, and only supernatural effects (like a spell) can impose on a PC. A creature hostile to a character actively seeks to harm that character. It doesn't necessarily attack, but it won't accept Requests from the character.

### Immobilized

You are incapable of movement. You can't use any actions that have the move trait. If you're immobilized by something holding you in place and an external force would move you out of your space, the force must succeed at a check against either the DC of the effect holding you in place or the relevant defense (usually Fortitude DC) of the monster holding you in place.

### Indifferent

This condition reflects a creature's disposition toward a particular character, and only supernatural effects (like a spell) can impose this condition on a PC. A creature that is indifferent to a character doesn't really care one way or the other about that character. Assume a creature's attitude to a given character is indifferent unless specified otherwise.

### Invisible

You can't be seen. You're Undetected to everyone. Creatures can Seek to detect you; if a creature succeeds at its Perception check against your Stealth DC, you become Hidden to that creature until you Sneak to become undetected again. If you become invisible while someone can already see you, you start out hidden to them (instead of undetected) until you successfully Sneak. You can't become Observed while invisible except via special abilities or magic.

### Observed

Anything in plain view is observed by you. If a creature takes measures to avoid detection, such as by using Stealth to Hide, it can become Hidden or Undetected instead of observed. If you have another precise sense besides sight, you might be able to observe a creature or object using that sense instead. You can observe a creature with only your precise senses. When Seeking a creature using only imprecise senses, it remains hidden, rather than observed.

### Off-Guard

You're distracted or otherwise unable to focus your full attention on defense. You take a –2 circumstance penalty to AC. Some effects give you the off-guard condition only to certain creatures or against certain attacks. Others—especially conditions—can make you off-guard against everything. If a rule doesn't specify that the condition applies only to certain circumstances, it applies to all of them, such as "The target is off-guard."

### Paralyzed

You're frozen in place. You have the Off-Guard condition and can't act except to Recall Knowledge and use actions that require only your mind (as determined by the GM). Your senses still function, but only in the areas you can perceive without moving, so you can't Seek.

### Persistent Damage

You are taking damage from an ongoing effect, such as from being lit on fire. This appears as "X persistent [type] damage," where "X" is the amount of damage dealt and "[type]" is the damage type. Like normal damage, it can be doubled or halved based on the results of an attack roll or saving throw. Instead of taking persistent damage immediately, you take it at the end of each of your turns as long as you have the condition, rolling any damage dice anew each time. After you take persistent damage, roll a [flat|showDC:all|dc:15] to see if you recover from the persistent damage. If you succeed, the condition ends.

### Petrified

You have been turned to stone. You can't act, nor can you sense anything. You become an object with a Bulk double your normal Bulk (typically 12 for a petrified Medium creature or 6 for a petrified Small creature), AC 9, Hardness 8, and the same current Hit Points you had when alive. You don't have a Broken Threshold. When the petrified condition ends, you have the same number of Hit Points you had as a statue. If the statue is destroyed, you immediately die. While petrified, your mind and body are in stasis, so you don't age or notice the passing of time.

### Prone

You're lying on the ground. You are Off-Guard and take a –2 circumstance penalty to attack rolls. The only move actions you can use while you're prone are Crawl and Stand. Standing up ends the prone condition. You can Take Cover while prone to hunker down and gain greater cover against ranged attacks, even if you don't have an object to get behind, which grants you a +4 circumstance bonus to AC against ranged attacks (but you remain off-guard).

If you would be knocked prone while you're Climbing or Flying, you fall. You can't be knocked prone when Swimming.

### Quickened

You're able to act more quickly. You gain 1 additional action at the start of your turn each round. Many effects that make you quickened require you use this extra action only in certain ways. If you become quickened from multiple sources, you can use the extra action you've been granted for any single action allowed by any of the effects that made you quickened. Because quickened has its effect at the start of your turn, you don't immediately gain actions if you become quickened during your turn.

### Restrained

You're tied up and can barely move, or a creature has you pinned. You have the Off-Guard and Immobilized conditions, and you can't use any attack or manipulate actions except to attempt to Escape or Force Open your bonds. Restrained overrides Grabbed.

### Sickened  — *valued*

@Localize[PF2E.condition.sickened.rules]

### Slowed  — *valued*

You have fewer actions. Slowed always includes a value. When you regain your actions, reduce the number of actions regained by your slowed value. Because you regain actions at the start of your turn, you don't immediately lose actions if you become slowed during your turn.

### Stunned  — *valued*

You've become senseless. You can't act. Stunned usually includes a value, which indicates how many total actions you lose, possibly over multiple turns, from being stunned. Each time you regain actions, reduce the number you regain by your stunned value, then reduce your stunned value by the number of actions you lost. For example, if you were stunned 4, you would lose all 3 of your actions on your turn, reducing you to stunned 1; on your next turn, you would lose 1 more action, and then be able to use your remaining 2 actions normally. Stunned might also have a duration instead, such as "stunned for 1 minute," causing you to lose all your actions for the duration.

Stunned overrides Slowed. If the duration of your stunned condition ends while you are slowed, you count the actions lost to the stunned condition toward those lost to being slowed. So, if you were stunned 1 and slowed 2 at the beginning of your turn, you would lose 1 action from stunned, and then lose only 1 additional action by being slowed, so you would still have 1 action remaining to use that turn.

### Stupefied  — *valued*

Your thoughts and instincts are clouded. Stupefied always includes a value. You take a status penalty equal to this value on Intelligence-, Wisdom-, and Charisma-based rolls and DCs, including Will saving throws, spell attack modifiers, spell DCs, and skill checks that use these attribute modifiers. Any time you attempt to Cast a Spell while stupefied, the spell is disrupted unless you succeed at a [flat|showDC:all|dc:resolve(5+@item.badge.value)] with a DC equal to 5 + your stupefied value.

### Unconscious

You're sleeping or have been knocked out. You can't act. You take a –4 status penalty to AC, Perception, and Reflex saves, and you have the Blinded and Off-Guard conditions. When you gain this condition, you fall Prone and drop items you're holding unless the effect states otherwise or the GM determines you're positioned so you wouldn't.

If you're unconscious because you're Dying, you can't wake up while you have 0 Hit Points. If you are restored to 1 Hit Point or more, you lose the dying and unconscious conditions and can act normally on your next turn.

If you are unconscious and at 0 Hit Points, but not dying, you return to 1 Hit Point and awaken after sufficient time passes. The GM determines how long you remain unconscious, from a minimum of 10 minutes to several hours. If you are healed, you lose the unconscious condition and can act normally on your next turn.

If you're unconscious and have more than 1 Hit Point (typically because you are asleep or unconscious due to an effect), you wake up in one of the following ways.

- You take damage, though if the damage reduces you to 0 Hit Points, you remain unconscious and gain the dying condition as normal.

- You receive healing, other than the natural healing you get from resting.

- Someone shakes you awake with an Interact action.

- Loud noise around you might wake you. At the start of your turn, you automatically attempt a Perception check against the noise's DC (or the lowest DC if there is more than one noise), waking up if you succeed. If creatures are attempting to stay quiet around you, this Perception check uses their Stealth DCs. Some effects make you sleep so deeply that they don't allow you this Perception check.

- If you are simply asleep, the GM decides you wake up either because you have had a restful night's sleep or something disrupted that rest.

### Undetected

When you are undetected by a creature, that creature can't see you at all, has no idea what space you occupy, and can't target you, though you still can be affected by abilities that target an area. When you're undetected by a creature, that creature is Off-Guard to you.

A creature you're undetected by can guess which square you're in to try targeting you. It must pick a square and attempt an attack. This works like targeting a Hidden creature (requiring a [flat|showDC:all|dc:11|traits:secret]), but the flat check and attack roll are rolled in secret by the GM, who doesn't reveal whether the attack missed due to failing the flat check, failing the attack roll, or choosing the wrong square. They can Seek to try to find you.

### Unfriendly

This condition reflects a creature's disposition toward a particular character, and only supernatural effects (like a spell) can impose this condition on a PC. A creature that is unfriendly to a character dislikes and distrusts that character. The unfriendly creature won't accept Requests from the character.

### Unnoticed

If you're unnoticed by a creature, that creature has no idea you're present. When you're unnoticed, you're also Undetected. This matters for abilities that can be used only against targets totally unaware of your presence.

### Wounded  — *valued*

You have been seriously injured. If you lose the Dying condition and do not already have the wounded condition, you become wounded 1. If you already have the wounded condition when you lose the dying condition, your wounded condition value increases by 1. If you gain the dying condition while wounded, increase your dying condition value by your wounded value.

The wounded condition ends if someone successfully restores Hit Points to you using Treat Wounds, or if you are restored to full Hit Points by any means and rest for 10 minutes.

**Source:** Player Core, the Dying, Wounded and Doomed conditions and the recovery check. Verified against the Foundry VTT PF2e condition compendium (packs/pf2e/conditions/dying.json, wounded.json, doomed.json) and src/module/actor/creature/document.ts, where the maximum dying value is 4 and the recovery DC is 10 + the dying value. — the same compendium supplies every condition above.

`tools/state.py` refuses a condition name that is not on this list, refuses a valued
condition with no value, and refuses an unvalued one with a value. Dying, wounded and doomed
are tracked as their own fields rather than as list entries, so there is only ever one copy of
the number that decides a death.

---

## Bulk and encumbrance

| | |
|---|---|
| 10 light items (`L`) | 1 Bulk |
| Negligible items (`—`) | do not count, until a heap of them does |
| **Encumbered** while carrying more than | 5 + Strength modifier Bulk |
| **Maximum** carried | 10 + Strength modifier Bulk |

Encumbered means **clumsy 1** and a 10-foot penalty to all Speeds.

```
python3 tools/state.py --campaign X bulk
```

`validate.py` errors when a carrier is over the maximum and warns when they are encumbered but
the condition has not been recorded.

**Source:** Player Core, Bulk. Verified against the Foundry VTT PF2e implementation
(`src/module/actor/inventory/bulk.ts`).

---

## Coins

1 pp = 10 gp = 100 sp = 1,000 cp.

**Source:** Player Core, Coins.

---

## What is not in this file

Anything that needs a lookup rather than a reminder: the full spell list, every feat, every
item. Look those up rather than recalling them, and cite what you find. A rules answer with no
source is a rules answer that might be wrong.
