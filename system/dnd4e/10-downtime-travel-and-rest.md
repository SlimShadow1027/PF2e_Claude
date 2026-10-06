# 10 (D&D 4e) — Travel, camp, rest and downtime

**Replaces `system/10-downtime-travel-and-rest.md` for a campaign with `System: dnd4e`.**

The one thing to take from this document if you take nothing else: **in 4e the resource that
runs out is the healing surge pool, not hit points.** Everything below is about that.

---

## The two rests

| | **Short rest** | **Extended rest** |
|---|---|---|
| Takes | About **5 minutes** | About **6 hours** |
| Encounter powers | Back | Back |
| Second Wind | Available again | Available again |
| Hit points | **Not restored** — spend surges | Full |
| Healing surges | **Not restored** | Full pool |
| Daily powers | **Not** restored | Back |
| Death save failures | Not cleared | Cleared |
| Action points | Not restored — they come from milestones | Reset to 1, milestone count to 0 |
| Limit | As many as you like | **One per 24 hours** |

```
python3 tools/state.py --campaign X short-rest
python3 tools/state.py --campaign X extended-rest
```

`long-rest` is refused on a 4e campaign and names `extended-rest`. Compare: D&D 2024's short
rest is an hour and its long rest eight; Pathfinder has daily preparations and no short rest at
all. Three rulesets, three rest economies, and reaching for the wrong one quietly changes how
long an adventuring day lasts.

### A short rest is cheap, and that is the point

Five minutes. In practice a party takes one after almost every fight, which means **encounter
powers and Second Wind are effectively per-fight resources** and should be spent freely. A
player holding an encounter power back "for later" is usually making a mistake, and it is worth
saying so once.

What a short rest does **not** do is give hit points back. That costs surges.

### The surge pool is the adventuring day

Spending a surge restores a quarter of maximum hit points. The pool refills only on an extended
rest. So the question "can we keep going?" is answered by the surge count, not by the hit point
total — a character on full hit points with one surge left is nearly done for the day.

```
python3 tools/state.py --campaign X surge list
python3 tools/state.py --campaign X surge spend verrin-ash
python3 tools/state.py --campaign X heal verrin-ash 9
```

`surge spend` tells you what the surge is worth and leaves the hit points to `heal`, so the
number applied is always visible rather than implied.

**Say the surge count out loud after each fight.** It is the single most useful piece of
information for deciding whether to press on, and in a solo campaign with no leader it is the
whole attrition story.

---

## Camping, and when an extended rest is available

An extended rest needs six hours and somewhere to take them. Deciding whether the party gets
one is a GM call with real teeth, because it is the only thing that refills the pool.

Things that legitimately deny one:

- **Interruption.** An extended rest that is broken does not count; the six hours start again.
- **No safe place.** Resting in a hostile dungeon is a decision with consequences, not a free
  reset.
- **The 24-hour limit.** Two extended rests in a day is not available, however much the party
  would like one.

Things that should not deny one: an arbitrary GM refusal to make a fight harder. If the day
needs to be harder, make the fights harder; do not withhold the mechanic that makes the next
day possible.

Record the clock honestly:

```
python3 tools/state.py --campaign X advance-time "6 hours"
python3 tools/state.py --campaign X extended-rest
python3 tools/state.py --campaign X checkpoint "camped in the drover's hut, pool full"
```

`advance-time` expires minute-, hour- and day-length conditions as it goes, and it advances the
**world's** calendar — which in a shared world is the same calendar the other rulesets' campaigns
read. The in-world date is how the living history stays gated correctly, so do not skip it.

---

## Travel

4e's travel rules are thinner than either sibling's, and this framework ships no 4e travel
table. Use the shared procedure in `system/10-downtime-travel-and-rest.md` for the *shape* of a
journey — legs, a check per leg, a complication budget — and resolve the checks with 4e's own
machinery:

- Skill checks against a **DC by level** (fill `dc_by_level`; and note the errata, below).
- Failure costs time, or a surge, or an encounter — **surges are the best currency for travel
  attrition in 4e**, because spending them shortens the day in exactly the way a hard road
  should.
- No ration or exhaustion track. 4e has no Exhaustion condition; `state.py exhaustion` is
  refused on a 4e campaign. If you want an attrition clock for a long march, use a framework
  clock and say so:

```
python3 tools/state.py --campaign X clock add "the road wears us down" 6
python3 tools/state.py --campaign X clock advance "the road wears us down"
```

> **The DC table has an errata trap.** 4e's Difficulty Class by Level table was **revised**
> partway through the edition's life, and the two printings give different numbers for the same
> level. Record which printing you transcribed in `dc_by_level._printing`, because a campaign
> that mixes them drifts in a way nobody can see. `dnd4e.py dc --level N` prints the recorded
> printing with every answer for exactly this reason.

---

## Downtime

Shared procedure: the montage. `system/10-downtime-travel-and-rest.md` and the `montage <goal>`
player command. Nothing in 4e changes its shape.

Two 4e-specific things worth doing in downtime:

1. **Retraining.** 4e lets a character swap out a feat, a power or a trained skill as they
   level. Downtime is where that gets narrated rather than just ticked.
2. **Commissioning items.** Since market availability is a per-settlement decision rather than
   a published table (`system/dnd4e/09-loot-and-economy.md`), a commission with a wait is often
   the honest answer to "can I buy this?" — and a wait is downtime, which is a scene.

---

## Between-session and the long clock

Shared: `system/18-between-session-prep.md`, `system/22-session-flow.md`. Two numbers to carry
forward in a 4e campaign specifically:

- **The surge pool each character ended on**, and whether an extended rest is available where
  they are. This is the first thing the recap should state.
- **The milestone count.** Every second encounter without an extended rest grants an action
  point, and the counter is easy to lose across a session break:

```
python3 tools/state.py --campaign X milestone
python3 tools/state.py --campaign X show | grep -A2 milestones
```

Then checkpoint, which is a git commit, which is the only reason any of this survives.
