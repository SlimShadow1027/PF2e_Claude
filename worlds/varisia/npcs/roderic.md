# Roderic

> **World-level NPC.** Persists beyond any one campaign. Read this through
> `python3 tools/world.py as-of varisia "<current date>"` — the date gate decides what a
> campaign in progress is allowed to know.

- **Status:** **ALIVE AND IN PLAY ELSEWHERE.** Not a historical figure.
- **Owned by:** a second campaign of this player's, run in a separate Claude Code session on
  their own machine. **That campaign is the real story.** This session cannot read it.
- **Appears in `third-beginnings`:** only as **legend**, never as established fact. See
  `worlds/varisia/LEGENDS.md`.
- **Bridge in use:** hand-carried (option 2 below). The player passed the premise across on
  2026-09-30; nothing is synced automatically.

## What the other campaign has established

The only facts in this file. Everything else about Roderic is legend.

| Fact |
|---|
| He is **alive now** |
| **Commander / Fighter**, dual-class — the same variant Karsa uses |
| **Second-in-command of the 5th squad** of a mercenary company |
| He lives in a city of **dark-grey legality**, where much of what would be crime elsewhere is routine business |
| He was the **last of his first company to survive** |
| He was left holding that company's **debts**, and his **contract was sold** to the group that now owns it |

The campaign's own project is **correcting the legends** — working out what actually happened
under the distortions. Which means the legends are not decoration in that campaign either.
They are the thing being excavated from the other end.

## The licence this file operates under

The player's words, 2026-09-30: *"make up whatever events you like for the myth and it can be
rectified or ignored as the other campaign continues."*

So the myth is invented **here**, deliberately, in four mutually exclusive versions, and it is
written to be **falsifiable in specific ways**. The real story overrules it without
ceremony. When it does, **strike the legend and keep the record of it having been believed** —
a legend disproved is still a legend people repeat.

## The one rule

**Do not assert who Roderic is.** Not in `third-beginnings`, not in `CANON.md`, not in play.
The gap is load-bearing: Karsa's entire reason for being at the Cove is that the story does
not survive in a form that agrees with itself, and that gap is shaped like whatever the other
campaign decides. Filling it from this side is the one move that would break the join.

## Timeline: concurrent, and that was a choice

Roderic is alive and a mercenary officer, and the Cove already bears his name. Those two
things can coexist three ways, and **this campaign assumes the first**:

1. **Concurrent, and the legends are already wrong while he lives.** A man whose contract is
   an asset has a reputation that is also an asset, and whoever owns the contract has been
   selling the story. The name reached the coast ahead of any facts. **Assumed here** — it is
   the darkest reading, it fits a grey-legality mercenary economy, and it leaves open the
   possibility that Karsa could simply **meet him**, which is a far better payoff than
   archaeology.
2. **He is a descendant or namesake** of an earlier Roderic the Cove is actually named for.
3. **The other campaign is set earlier** and `third-beginnings` is its downstream future.

Switching to 2 or 3 costs one edit to this file and one to `LEGENDS.md`. Nothing in
`third-beginnings` depends on the choice yet, and that is on purpose.

## Why this file exists
## Why this file exists

The player noticed that *Third Beginnings* is set in **Roderic's Cove**, and that a "Roderic"
already exists in another campaign of theirs, and asked whether the two could be connected
narratively and in the world files.

They can. This file is the join point. It is deliberately **almost empty**, because the one
thing that would ruin the join is this session inventing a Roderic and then discovering the
other campaign had already established a different one.

## What the Cove itself contributes

| Fact | Established by | Status |
|---|---|---|
| Roderic's Cove is a settlement on the Varisian coast, named for a man called Roderic | published Varisian geography | **Published**, though the gazetteer detail could not be verified from this container — Archives of Nethys does not host setting text |
| The dredging economy, the sea caves, the Thassilonian door | `third-beginnings` | **This campaign's own invention**, labelled as such |
| Who Roderic actually was | **nobody, here** | **Open, and staying open** |

## What *Third Beginnings* has deliberately left open

Karsa's whole reason for being at the Cove is that **Roderic's story does not survive in a form
that agrees with itself**: two accounts of the founding, three of the man, and none of what he
was doing on that coast before there was a town on it.

That was written as a mystery for Karsa to solve. It is also, conveniently, a **hole shaped
like whatever the other campaign says Roderic is.** Nothing in `third-beginnings` contradicts
any Roderic yet, because no Roderic has been asserted.

**Keep it that way until the join is decided.** If the two campaigns are to connect, the
other campaign's Roderic should be the one that fills this in.

## The bridge problem

This session runs in a cloud container holding one repository. The other campaign runs on the
player's own machine. **There is no path by which this session can read that campaign's
files.** So a join needs one of these, and it is the player's call:

1. **Share the repository.** The other session clones or pulls
   `slimshadow1027/pf2e_claude`, and its campaign lives in `campaigns/<its-slug>/` beside
   this one. Both then read the same `worlds/varisia/`, and `world.py as-of` gates each one
   by its own in-world date. This is what the shared-world layer was built for and it is the
   only option where the two stay in sync by themselves.
2. **Hand-carry the facts.** The player pastes what the other campaign has established about
   Roderic; it gets written here with a visibility tag; world material goes back the other
   way the same way. Works, needs doing every time, and drifts the moment someone forgets.
3. **Rhyme, do not connect.** Two Roderics, same name, no shared canon — a deliberate echo
   rather than a continuity. Costs nothing, risks nothing, and gives up the payoff.

## The cost of connecting, stated plainly

A join makes facts **binding in both directions**. `CANON.md` is never contradicted — the rule
is to ask for a retcon and record it, not to quietly diverge. So:

- If the other campaign establishes something about Roderic, *Third Beginnings* has to live
  with it, including where it wrecks prep.
- If *Third Beginnings* concludes something about what is under the Cove, the other campaign
  inherits it.
- The date gate only protects a campaign **running inside this framework**. If the other
  campaign is not, the gate protects *Third Beginnings* from the other campaign's future and
  **not the reverse** — the player would be carrying that risk themselves.

## Open threads

- What was Roderic doing on that coast before there was a town on it?
- Is the Roderic of the Cove's name the same man as the other campaign's, a descendant, a
  namesake, or someone who took the name?
- Did Roderic know about the door?
