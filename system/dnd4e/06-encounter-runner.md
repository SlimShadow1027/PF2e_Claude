# 06 (D&D 4e) — The encounter runner

**Replaces `system/06-encounter-runner.md` for a campaign with `System: dnd4e`.**

The procedure has the same shape as the other two. The turn underneath it is a third shape
again, and the habits that carry over from either sibling are wrong here in ways that quietly
favour the monsters. Read this once before the first fight.

---

## Before round 1

1. **Name the objective out loud, in the fiction.** `system/17-encounter-objectives.md`. A
   timer the player cannot see is a trap, not a tactical problem.
2. **Describe the ground in squares.** Elevation, cover, difficult terrain, what can be pushed
   off or knocked over. 4e is the most grid-dependent of the three — forced movement, zones and
   bursts all count squares — so distances have to be concrete or the player cannot plan.
3. **Say who is surprised.** In 4e the surprised creatures **do not act in the surprise round
   at all** and grant combat advantage until they do. This is not a modifier on the initiative
   roll (that is D&D 2024) and not an off-guard condition (that is Pathfinder), so `roll.py
   init --surprised` is **refused** on a 4e campaign and says which. Handle the surprise round
   in the tracker: run it with the unsurprised side only, then start round 1 proper.
4. **Roll initiative** — one roll for a group of identical monsters.
   ```
   python3 tools/roll.py init --campaign X --system dnd4e \
       --actors "Verrin:+6,Kobold Skirmishers:+4,Kobold Dragonshield:+2" --party "Verrin"
   ```
   A 4e tie goes to the higher initiative modifier, then to the DM; this framework rolls the
   remainder off with real dice so the order is auditable rather than an unlogged choice. That
   substitution is the framework's convention — say so at the table.
5. **Start the tracker** and add every combatant with their level, role and rank.
   ```
   python3 tools/state.py --campaign X encounter start "Ambush at the culvert" \
       --objective "get the wounded scout out before the horn sounds"
   python3 tools/state.py --campaign X encounter add "Verrin" --side party --ref verrin --init 22
   python3 tools/state.py --campaign X encounter add "Kobold Dragonshield" --side adversary \
       --hp 36 --init 14 --level 2 --role soldier
   python3 tools/state.py --campaign X encounter add "Kobold Minions" --side adversary \
       --hp 1 --init 12 --level 1 --role minion --rank minion
   ```
   `--cr` is refused: Challenge Rating is D&D 2024's scale. `--bonus-action` is refused: 4e's
   near equivalent is the minor action, which every combatant already has.

---

## The turn, as the tracker shows it

```
   combatant              init           HP std  mov  min  imm  rxn  pos   conditions
→  Verrin                   22        38/38 ◆    ◆6   ◆    ◆    yes  B3
   Kobold Dragonshield      14        36/36 ◆    ◆5   ◆    ◆    yes  C4
```

| Column | What it is |
|---|---|
| `std` | The standard action |
| `mov` | The move action, and the squares of speed still unspent |
| `min` | The minor action |
| `imm` | The immediate action — **one per round**, not per turn |
| `rxn` | The opportunity action |

```
python3 tools/state.py --campaign X encounter action "Verrin" 1 --kind standard
python3 tools/state.py --campaign X encounter action "Verrin" 4 --kind squares
python3 tools/state.py --campaign X encounter action "Verrin" 1 --kind minor
python3 tools/state.py --campaign X encounter next
```

**Trading down.** A standard may be spent as a move or a minor, and a move as a minor — never
upward. The tracker refuses a spent action and names the trade you still have ("You still have
a standard action, which can be traded down to a minor"), so a player is never silently told no.

**`imm` is per round.** `encounter next` resets it on the combatant whose turn begins, which is
the right approximation for a solo table but is worth remembering: a monster that spent its
immediate action on your turn has it back on its own.

---

## Offer the reaction before resolving the trigger — every time

This is the duty most easily skipped, and in 4e there is more of it than in either sibling:

| Trigger | Ask about |
|---|---|
| A creature leaves a square adjacent to an enemy | **Opportunity attack** (one per other creature's turn) |
| A ranged or area attack from an adjacent square | Opportunity attack |
| An attack that would drop a character | Any **immediate interrupt** they hold |
| A monster moving, attacking or being hit | **Immediate reactions**, which are common on 4e powers |
| A marked creature attacking anyone but the marker | The **mark penalty**, which applies to the attack *being made* |

Ask **before** resolving. The tracker has `imm` and `rxn` columns so that "no reaction
available" is always backable against the state rather than asserted from memory.

### Marks

A mark imposes a penalty on the marked creature's attacks against anyone other than the
marker. **Only one mark at a time** — a new one replaces the old, it does not stack. The
combatant carries `marked_by`; set it with a note and clear it when the mark ends. In a solo
campaign the player is usually the only possible marker, so the mark penalty is the one thing
reliably in their favour. Do not forget to apply it to the monster's roll.

---

## Damage and the hit-point floor that is not a floor

```
python3 tools/roll.py attack "1d20+9" --ac 18 --label "Longsword" --actor Verrin --campaign X
python3 tools/roll.py damage "1d8+5" --type slashing --campaign X
python3 tools/state.py --campaign X damage verrin 14
```

A **natural 20 hits automatically and criticals**; a natural 1 misses automatically. A
critical deals **maximum damage** — nothing is rolled:

```
python3 tools/roll.py damage "1d8+5" --crit --type slashing --campaign X
  → 8+5 → +13 = 13 slashing (critical) — maximum damage, dice not rolled (1d8+5 maximised to 8+5)
```

Magic weapon critical dice and critical-only power dice **are** rolled, separately, and added.

**Bloodied** at half maximum hit points or fewer. It is a real condition here, so say it out
loud when it happens — powers on both sides key off it.

**At 0 and below, hit points keep falling.** `damage` tracks the depth as `hp_below_zero` and
reports it against the death threshold. A character dies either at **three death saving throw
failures** or at a **negative total equal to their bloodied value**, whichever comes first.

```
python3 tools/state.py --campaign X damage verrin 40
  Verrin HP 0/38
  reduced to 0 hit points or below — dying and unconscious, making a death saving throw at the end of each turn
  hit points continue below zero; death at -19
python3 tools/state.py --campaign X death-save roll verrin
```

Taking damage while already dying costs a failure as well as depth. There is **no Stable
state** — `death-save stabilise` is refused on a 4e campaign, because nothing in 4e stops the
clock except healing. Any amount of healing ends dying, clears the failures and clears the
depth.

**Minions.** Exactly 1 hit point, and **no damage from a missed attack** — which means a miss
that would normally deal half damage deals none to a minion. This is a rule, not a shorthand,
and the tracker warns if a minion is entered with any other hit point total.

---

## Mid-fight resources

```
python3 tools/state.py --campaign X power use verrin "Twin Strike"        # encounter power
python3 tools/state.py --campaign X second-wind use verrin                # standard action, once
python3 tools/state.py --campaign X surge spend verrin                    # then `heal` the amount
python3 tools/state.py --campaign X action-point spend verrin             # an extra action
```

Second Wind spends a surge **and** a standard action, and grants a bonus to all defences until
the start of the character's next turn — record that as a condition if it will matter.

An action point gives an **extra action**, once per encounter. It is not a reroll; the dice
audit says so, because nothing about a spend reaches the roll log.

**Saving throws end effects.** At the end of their turn, against each "save ends" effect:

```
python3 tools/roll.py save "1d20" --dc 10 --label "save vs ongoing fire (5)" --campaign X
python3 tools/state.py --campaign X condition remove verrin ongoing-damage
```

A flat d20 against 10. `roll.py` forces the target to 10 on a 4e save whatever is passed.

---

## Ending it

```
python3 tools/state.py --campaign X encounter end
```

Then, before anything else:

1. **Award XP** — the monsters' total, **divided by the party size**. `dnd4e.py encounter
   --monster …` prints both figures.
2. **Record treasure** against the parcel plan, not ad hoc. `system/dnd4e/09-loot-and-economy.md`.
3. **Say which conditions persist** past the encounter, and which ended with it. Encounter
   powers and Second Wind come back on a short rest; dailies and surges do not.
4. **Count the milestone.** Every second encounter without an extended rest grants an action
   point: `python3 tools/state.py --campaign X milestone`.
5. **Write `encounters/history.md`** with its `Objective:` line, and take a checkpoint.

```
python3 tools/state.py --campaign X checkpoint "fought clear of the culvert, scout alive"
```
