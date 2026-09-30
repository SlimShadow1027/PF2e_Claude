# 03 — Difficulty and the solo levers

Solo PF2e breaks in specific, predictable ways. This document names them and gives the fixes.

---

## The problems, named

### Action economy

One PC against four creatures takes four turns of incoming attacks and gets one turn back. The
XP budget does not model this: it prices four level-minus-2 creatures and one level-plus-2
creature at similar totals, and for a single character those are wildly different fights.

**Many-weak-enemies encounters are far deadlier solo than the XP budget implies.** This is the
most important sentence in this document.

`python3 tools/pf2e.py encounter --party-size 1` prints a warning to this effect every time,
because the number it gives is correct and still misleading.

### No role coverage

A party of four covers healing, knowledge, locks and traps, and social work between them. One
character covers one or two.

- No healer → Dying spirals, and Treat Wounds out of combat becomes the only lever.
- No one with Thievery → locked doors are walls and traps are damage.
- No one Recalling Knowledge → every fight is fought blind against unknown resistances.
- No one with a high Will → one save ends the character.

### Focused fire

Enemies with any tactical sense all target the only target. In a party of four, damage spreads
across four HP pools and four sets of defences; solo it all lands in one place.

### Death spiral

Dying and Wounded assume an ally who can Administer First Aid. With nobody there, dying 1
becomes dying 2 becomes dead, across three rounds where the player has no actions.

### Single point of failure

One failed save can end the campaign. That is a bad story, not a challenge. A party of four
can lose a member and continue; a solo party cannot lose anything.

---

## The levers

Each is a line in `RULES_DELTAS.md` with its effect and its difficulty delta. Nothing here is
on by default except where a preset says so.

### Party-shape levers

| Lever | What it does |
|---|---|
| Solo PC | The baseline. Needs the safety nets. |
| Solo PC + a GM-run ally built as a full PC | Two turns per round. The single largest fix to the action economy. |
| Solo PC + a sidekick | A simplified companion: one job, fewer decisions, still a body in the initiative order. |
| Troupe play | The player controls 2–4 characters. PF2e as designed, with more bookkeeping. |
| A rotating guest ally per arc | A full PC who arrives and leaves with the story. Keeps the spotlight on the player's character. |

### Math levers

| Lever | What it does |
|---|---|
| Encounter XP budget scaled for party size | On by default. `pf2e.py encounter --party-size N`. |
| Weak adjustment as the default for mooks | −2 to most numbers and reduced HP. Makes a crowd survivable without reducing its number. |
| Prefer fewer, higher-level enemies over swarms | The structural fix to the action economy. One level+2 creature is a fight; four level−2 creatures is a mugging. |
| Cap the number of enemies acting per round | e.g. "at most three act each round; the rest reposition". Blunt, effective, and visible to the player. |
| A bonus reaction for the solo PC | One extra reaction per round. **Homebrew.** |
| A once-per-encounter extra action | One extra action, once. **Homebrew.** |

### Safety-net levers

| Lever | What it does |
|---|---|
| Starting Hero Points 2–3 | Instead of 1. More rerolls, more stabilisations. |
| Per-scene Hero Point refresh | Instead of per session. **Homebrew.** Large effect on a long sitting. |
| Hero Point converts a critical failure to a failure | **Homebrew.** Removes the single-bad-roll campaign ender. |
| No character death without the player's consent | Defeat becomes capture, loss, injury, or a narrative cost. |
| Auto-stabilise at dying 3, first time per session | **Homebrew.** Turns the death spiral into a scare. |
| A free Treat Wounds between encounters | Removes the attrition that a solo party cannot absorb. |
| Retreat is always available | A guarantee that a fight can be left, with a cost but without a chase the player cannot win. |

### Information levers

| Lever | What it does |
|---|---|
| Free or generous Recall Knowledge | Solo, nobody else can make the check. Give it for one action, or for free. |
| Enemy HP shown as a bar or a descriptor | "badly hurt" instead of 11/28. Lets the player make the press-or-run decision. |
| The GM lists legal actions each turn | Removes the "I forgot I had that" tax of playing a full PF2e character alone. |
| The GM flags a likely-fatal plan before it is committed to | One out-of-character line, before the action is spent. |
| Telegraph big attacks a round ahead | "It draws breath and the air goes cold." The player gets to respond. |

---

## The four presets

Pick one word instead of twelve toggles. Each preset is a concrete list of values written into
`RULES_DELTAS.md`.

### `Story` — fiction first, combat rarely lethal

| Lever | Value |
|---|---|
| Party shape | solo PC + a GM-run full-PC ally |
| Weak on mooks | on |
| Fewer, higher-level enemies | on |
| Enemies acting per round | capped at 3 |
| Starting Hero Points | 3 |
| Hero Point refresh | per scene |
| Hero Point → critical failure becomes failure | on |
| No death without consent | **on** |
| Auto-stabilise at dying 3 | on, once per session |
| Free Treat Wounds between encounters | on |
| Retreat always available | on |
| Recall Knowledge | free, one fact per creature, no action |
| Enemy HP shown | descriptors |
| GM lists legal actions | on |
| GM flags fatal plans | on |
| Telegraph big attacks | on |
| Encounter threat target | low to moderate |

### `Standard` — PF2e as written, tuned for party size

| Lever | Value |
|---|---|
| Party shape | as chosen at intake |
| Weak on mooks | on for groups of three or more |
| Fewer, higher-level enemies | on |
| Enemies acting per round | uncapped |
| Starting Hero Points | 2 |
| Hero Point refresh | per session |
| No death without consent | off |
| Auto-stabilise | off |
| Free Treat Wounds | off — but Treat Wounds is always offered |
| Retreat always available | on |
| Recall Knowledge | as written, one action, generous on a success |
| Enemy HP shown | descriptors |
| GM lists legal actions | when the player seems stuck |
| GM flags fatal plans | on |
| Telegraph big attacks | on |
| Encounter threat target | moderate, with severe at story beats |

### `Gritty` — resources matter, retreat is common, death is real

| Lever | Value |
|---|---|
| Party shape | as chosen; no extra ally granted |
| Weak on mooks | off |
| Fewer, higher-level enemies | on |
| Enemies acting per round | uncapped |
| Starting Hero Points | 1 (as written) |
| Hero Point refresh | per session |
| No death without consent | off |
| Auto-stabilise | off |
| Free Treat Wounds | off |
| Retreat always available | off — retreat is possible but has to be bought |
| Recall Knowledge | as written |
| Enemy HP shown | vague descriptors only |
| GM lists legal actions | off |
| GM flags fatal plans | off |
| Telegraph big attacks | on — this one stays, because a surprise instant death is not grit |
| Encounter threat target | moderate to severe; attrition between them |

### `Nightmare` — no safety nets, Elite adjustments, full attrition

| Lever | Value |
|---|---|
| Party shape | as chosen |
| Elite on significant enemies | on |
| Weak on mooks | off |
| Enemies acting per round | uncapped |
| Starting Hero Points | 1 |
| Hero Point refresh | per session |
| No death without consent | off |
| Auto-stabilise | off |
| Free Treat Wounds | off |
| Retreat always available | off |
| Recall Knowledge | as written |
| Enemy HP shown | nothing |
| GM lists legal actions | off |
| GM flags fatal plans | off |
| Telegraph big attacks | off |
| Encounter threat target | severe, with extreme at story beats |

> `Telegraph big attacks` is on in three of four presets on purpose. An unannounced
> save-or-die is not difficulty; it is a coin flip the player was not told about.

### Changing preset mid-campaign

**One sentence is enough.** "Switch to Gritty." The GM:

1. Rewrites the toggle values in `RULES_DELTAS.md` and adds a change-log row.
2. `python3 tools/state.py --campaign <slug> preset Gritty`
3. Applies it **going forward only**. Nothing is retconned — a fight already won stays won,
   a character already dead stays dead, a Hero Point already spent stays spent.
4. Says in one line what will feel different next session.

---

## The difficulty check-in

A GM that wants the player to have a good time will quietly get easier. This is the mechanism
that catches it.

### After every significant encounter

Write the `encounters/history.md` entry, and fill in the last field honestly:

> **Difficulty landed as:** trivial / appropriate / brutal — _one sentence on why_

"Appropriate" means the player spent real resources and the outcome was in doubt at some point.
If the player was never in doubt, it was trivial, whatever the XP budget said.

### Every few sessions

Read the pattern, not the last night. Say something like:

> "Out of character: the last six fights went appropriate, appropriate, trivial, trivial,
> trivial, appropriate. Two of those trivial ones were Weak-adjusted groups I could have run
> straight. Want me to stop applying Weak by default, or leave it?"

Give the **numbers**, from `encounters/history.md` and from
`python3 tools/analyze.py --campaign <slug>`:

- How many encounters landed trivial / appropriate / brutal.
- How often the player dropped below a quarter HP.
- How many times they reached Dying, and at what value.
- Hero Point spends per session.
- Success rate per save, with sample sizes — which save is actually the weak one.

Then **offer an adjustment and let the player decide.** Do not adjust silently in either
direction. An automated GM drifting easier is the failure mode this catches; an automated GM
drifting harder without saying so is the same failure with a different sign.

The cadence lives in `PLAYER_PREFS.md` (`Offer an adjustment every N sessions`).
