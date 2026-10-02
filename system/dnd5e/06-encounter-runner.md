# 06 (D&D 2024) — The encounter runner

**Replaces `system/06-encounter-runner.md` for a campaign with `System: dnd5e`.**

The procedure is the same shape as the Pathfinder one; the turn underneath it is not. Read the
whole of this document once before the first fight, because the habits that carry over from a
three-action game are wrong here in ways that quietly favour the monsters.

---

## Before round 1

1. **Name the objective out loud, in the fiction.** `17-encounter-objectives.md`. A timer the
   player cannot see is a trap, not a tactical problem.
2. **Describe the ground**: elevation, cover, what can be moved, knocked over or climbed. Distances
   in **feet**, because movement is measured in feet here and a player cannot plan without them.
3. **Say who is surprised, and why.** Surprise in this game is **Disadvantage on the Initiative
   roll** — not a lost turn. An ambusher does not get a free round; they get a better position in
   the order.
4. **Roll initiative** — a Dexterity check, one roll for a group of identical creatures.
   ```
   python3 tools/roll.py init --campaign X --system dnd5e \
       --actors "Thorne:+3,Goblin Boss:+2,Goblins:+2" --party "Thorne" --surprised "Goblin Boss"
   ```
5. **Start the tracker**, and add every combatant with their Speed and whether they have a Bonus
   Action.
   ```
   python3 tools/state.py --campaign X encounter start "Ambush at the ford" \
       --objective "reach the far bank before the horn sounds"
   python3 tools/state.py --campaign X encounter add "Thorne" --side party --ref thorne \
       --init 17 --speed 30 --bonus-action
   python3 tools/state.py --campaign X encounter add "Goblin Boss" --side adversary \
       --hp 21 --init 12 --cr 1 --speed 30
   ```
6. **Have the stat blocks in `bestiary/` already**, each with a `Source:` line.

---

## The per-round tracker

```
   combatant              init           HP act  bns  move    rxn  pos   conditions
   Thorne                   17        28/28 ◆    ◆    30/30ft yes  B3    
→  Goblin Boss              12        21/21 ◆    —    30/30ft yes  D5    
```

| Column | What it holds |
|---|---|
| `act` | the one action: `◆` available, `◇` spent |
| `bns` | the Bonus Action: `◆`/`◇` if a feature grants one, `—` if not |
| `move` | movement left of the Speed, in feet |
| `rxn` | the reaction, one per round |

**`—` in the `bns` column is information, not an omission.** A Bonus Action exists only where a
feature grants one. Adding every combatant with `--bonus-action` because it looks tidier gives the
monsters a resource the rules do not.

The tracker has no MAP column, because there is no multiple attack penalty. `encounter map-step`
refuses to run on this ruleset and says why.

Spending things:

```
python3 tools/state.py --campaign X encounter action thorne --kind action
python3 tools/state.py --campaign X encounter action thorne --kind bonus
python3 tools/state.py --campaign X encounter action thorne 25 --kind move    # feet
python3 tools/state.py --campaign X encounter action thorne --kind dash
python3 tools/state.py --campaign X encounter next
```

`next` resets the incoming combatant's action, Bonus Action, movement and reaction, puts a Dash's
borrowed Speed back, and **prompts for a Death Saving Throw if they start their turn on 0 HP**.

---

## The reaction obligation

**Before resolving any trigger, check the reaction column and ask.** This is the duty most easily
skipped and the one a player most reasonably resents losing.

Triggers to ask about, every time:

| Trigger | Ask about |
|---|---|
| A creature leaves your reach using its movement | **Opportunity Attack** |
| An attack is about to hit you | Shield, Deflect Attack, Uncanny Dodge, Interception |
| A creature you can see casts a spell | Counterspell, Silvery Barbs |
| You or an ally fails a save | Absorb Elements, a Paladin's aura abilities |
| An ally is hit | Protection, Interception |
| A creature moves into your reach | a readied action |
| You take damage that could drop you | anything that reduces damage, before you apply it |

Two things that catch an automated GM out:

- **Opportunity Attack triggers on movement out of reach, not on movement near you**, and the
  Disengage action turns it off for the turn. Check which the creature did.
- **A readied action spends the reaction**, and the trigger has to be stated when it is readied.
  Write the trigger in the `rxn` column's note so "that is not what you readied" is backable.

Ask *before* resolving. A reaction offered after the damage is applied is not an offer.

---

## Enemy tactics: honest, not omniscient

Unchanged from the Pathfinder document, because it is not a rules question:

- Monsters know what they could plausibly know. They do not know the player's AC, their remaining
  HP, which save is weakest, or what is in their hand.
- They learn in play. Something that watched a spell land twice will act on it.
- They use their own stat block's options rather than optimal play invented for them.
- **Roll their saves and attacks for real**, `--private`. A monster's save is not a narrative
  decision.

### Morale

Not a published rule in this game, so it is this framework's convention and it says so. A sensible
creature reduced below about a third of its HP, or watching half its side fall, gets a decision:
flee, surrender, negotiate, or fight because it cannot do otherwise. Use the oracle if it is
genuinely uncertain (`19-solo-oracle.md`). Record it in `RULES_DELTAS.md` as a house rule.

A fight that ends because the other side broke is often a better scene than one that ends because
the last hit point went, and at a solo table it is also a mercy.

---

## Groups of identical creatures

One Initiative roll for the group is **published** here, which makes a group easy to run: they all
act together.

- Give them one line in the tracker with a count, or one line each if their HP will diverge — HP
  will diverge the moment anything deals damage to one of them, so separate lines are usually
  right.
- **Roll their attacks separately.** One roll applied to several attacks is not the same
  distribution and it will show up in `analyze.py`.
- Batching is a presentation shortcut, never a dice shortcut.

---

## The tactical map

An ASCII grid the GM draws, in `campaigns/<slug>/maps/`. **Each square is 5 feet** — that is
published, and it is what makes movement legible.

```
    A   B   C   D   E
1   .   .   #   #   #
2   .   T   .   .   #
3   #   .   .   G   #
4   #   #   .   .   .
```

Positions go in the tracker's `pos` column. When the player asks how far something is, answer in
feet and in squares, because they will plan in whichever they think in.

---

## Resolving a turn

1. **Say what the creature does, in the fiction, before any dice.**
2. **Check reactions** — see above. Ask, do not assume.
3. **Roll the attack with `attack`, not `check`.** This matters: `attack` applies the natural-20
   and natural-1 rules and `check` does not, and that is the correct behaviour for each.
   ```
   python3 tools/roll.py attack "1d20+7" --ac 15 --actor Thorne --campaign X --label "Longsword"
   ```
4. **Roll damage separately**, and pass `--crit` on a critical hit so the **dice** double.
   ```
   python3 tools/roll.py damage "1d8+4" --crit --type slashing --campaign X
   ```
5. **Apply it through `state.py damage`**, which handles temp HP, 0 HP, Death Saves and massive
   damage. Do not edit HP by hand.
6. **Check Concentration** if the target was concentrating:
   `state.py concentration check <who> <damage>` prints the DC, then roll the save for real.
7. **Spend what was spent** in the tracker, then `encounter next`.

---

## At the end of combat

1. **Award XP**: the creatures' own XP, undivided. `state.py xp add`.
2. **Record treasure** found, if any — and see `09-loot-and-economy.md` on why this game's
   treasure pacing is a convention rather than a table.
3. **Note which conditions persist** past the fight, and which ended with it.
4. **Temporary HP** survives the fight and ends with the next Long Rest.
5. **Death Save counters** reset the moment anyone regains a Hit Point. A character left Stable at
   0 HP regains 1 HP after 1d4 hours if nobody heals them — set a reminder or they will be
   forgotten unconscious.
6. **Write `encounters/history.md`** with its `Objective:` field and whether the objective was met.
7. **Checkpoint.** `state.py checkpoint "<what just happened>"`.

---

## The five mistakes this ruleset invites

1. **Giving everyone a Bonus Action.** It is not a third action everyone has.
2. **Charging an action for movement.** Movement is its own allowance.
3. **Applying a multiple attack penalty.** There is none. Extra attacks come from Extra Attack and
   the Attack action, at full bonus.
4. **Doubling the modifier on a crit.** Only the dice double.
5. **Treating surprise as a lost turn.** It is Disadvantage on Initiative.

All five make the game harder than written, and four of the five make it harder for the player
rather than the monsters.
