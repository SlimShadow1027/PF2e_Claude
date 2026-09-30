# 17 — Encounter objectives

A fight whose only victory condition is reducing everything to 0 HP is a damage race, and solo
play turns that repetitive fast. The tactical interest lives in the objective.

**Two requirements, and `tools/validate.py` enforces the first:**

1. **Every encounter entry in `encounters/history.md` names its objective.** The `Objective:`
   field is not optional; `validate.py` fails an entry without one. `state.py encounter start`
   also refuses to begin a fight without `--objective`.
2. **The GM states or telegraphs the objective in the fiction, before or during round 1.** A
   timer the player cannot see is a trap, not a tactical problem. Record it:
   `state.py encounter telegraph "the water is already at your ankles"`.

**Default target: at least half of all combat encounters in a campaign have a win condition
other than "everything hostile is dead."** Check that against `encounters/history.md`
periodically, and say so if it has slipped.

A straight fight is a legitimate objective — occasionally. Write `Objective: a straight fight;
the point was the resource cost` and mean it.

---

## The catalogue

### 1. Timers

Something completes, and it is not the party's hit points.

- **A ritual completing** in N rounds, with a visible tell each round it advances.
- **A fuse burning**, a candle guttering, a charge winding down.
- **Reinforcements arriving** in N rounds — announced by a sound, not a surprise.
- **A building collapsing**, floor by floor, from a stated round.
- **Rising water**, a foot per round, with the squares it takes marked on the map.
- **A ship pulling away** from the dock, five squares per round.
- **Something waking up**, and the round it opens its eyes.

Show the timer. Put the round it fires in `state.json` under the encounter, put the tell in the
fiction every round, and mark the affected squares on the map.

### 2. Objectives that are not the enemy

Winning does not require killing.

- **Reach a lever** (or a door, or an altar) and pull it.
- **Rescue** someone who cannot move themselves, or **escort** someone who moves slowly.
- **Destroy an object** — a totem, a beacon, a cage, a bridge.
- **Hold a position** for N rounds while something else finishes.
- **Recover something and get out** — the fight is the price of the errand, not the point.
- **Stop something leaving** — a messenger, a cart, a boat.
- **Keep something alive** that the enemy is trying to kill.
- **Learn something** — a name, a route, a password — which means keeping one enemy talking or
  alive.

For a solo character these are the best objectives available, because they let a fight end
before attrition does its work.

### 3. Morale and surrender

Enemies who stop fighting. **Specify a morale threshold per creature group**, in the bestiary
entry, and apply it.

- **A wound threshold** — flees at or below a third of its HP.
- **A group threshold** — breaks when half its number is down.
- **The leader's death** — the group scatters, or one takes over and fights harder.
- **Intimidation** — a Demoralize or a display of force ends it.
- **A bribe** — some enemies are working, not crusading.
- **Talked down** — the enemy has a reason, and the reason can be addressed.
- **Surrender offered, and meant** — which creates a prisoner, which creates a decision.

A fight that ends because the last two goblins run is a better fight than one that ends because
they were killed at 2 HP each. It is also faster, which matters in a one-versus-six.

### 4. Terrain that changes

The map is not static.

- **A collapsing bridge** — squares drop out on a stated schedule.
- **Spreading fire** — a square per round, in a direction, doing stated damage.
- **A moving vehicle** — a cart, a barge, a ship's deck that pitches.
- **Shifting darkness** — light sources that fail, or a creature that puts them out.
- **Rising or draining water** — changing which squares are difficult terrain or impassable.
- **Hazards that can be turned on the enemy** — a brazier, a portcullis, a stack of barrels, an
  unstable floor.

The last one is the most valuable in solo play: a hazard the player can use is an extra
action's worth of damage they did not have to buy with a feat.

### 5. Retreat as a real option

Leaving is a legitimate outcome, and it needs rules so it is not a guess.

- **Chase rules:** each round, both sides make a relevant check (Athletics, Acrobatics,
  Stealth). Three successes before three failures and you are away; the reverse and you are
  caught with the ground lost.
- **The cost of fleeing:** what gets dropped, what gets left behind, who sees you go.
- **What the enemy does with the ground you gave up:** reinforces it, loots it, moves the thing
  you came for, or follows.

If the campaign's preset guarantees that retreat is always available
(`03-difficulty-and-solo-levers.md`), say so before the fight, not during it.

### 6. Escalation

The fight changes shape partway through.

- **A second wave**, arriving on a stated round, announced.
- **A creature that transforms at half HP** — a new stat block, cited, or the same one with a
  named ability coming online.
- **An ally who turns**, which should have been seeded (`gm-private/seeds.md`).
- **The objective changing** — the thing being rescued turns out to be the thing to stop.
- **Something bigger noticing** the noise.

Escalation needs a tell. A second wave that arrives unannounced is a difficulty increase; one
announced by a horn two rounds earlier is a tactical problem.

---

## Building one

1. **Pick the objective first**, then the creatures. Picking creatures first produces a damage
   race with flavour text.
2. **Say how the player learns it.** If you cannot answer that, the objective is not in the
   encounter yet.
3. **Give it a number** — a round count, a square count, a hit point total — so it can be
   tracked rather than judged.
4. **Write the morale threshold** for each group.
5. **Record it:**

```
python3 tools/state.py --campaign X encounter start "Crypt landing" \
    --objective "Reach the lever before the water rises (6 rounds); ghouls flee at a third HP" \
    --map crypt-landing
python3 tools/state.py --campaign X encounter telegraph "the water is already at your ankles, and rising"
```

6. **Write the history entry** afterward, with the `Objective:` field and the honest
   `Difficulty landed as:` line.

---

## Objectives and the solo problem

The reason this document exists in a framework built for one player:

A party of four can win a war of attrition, because four HP pools and four action economies can
absorb one. **A single character cannot.** A fight with no objective but "kill everything" is
therefore, solo, a fight the player either wins early or loses slowly — and losing slowly is the
least interesting way to lose.

An objective gives the fight an exit. That is not a difficulty reduction; it is what makes the
difficulty survivable while remaining real.
