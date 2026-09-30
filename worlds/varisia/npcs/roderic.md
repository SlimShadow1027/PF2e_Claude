# Roderic

> **World-level NPC.** Persists beyond any one campaign. Read this through
> `python3 tools/world.py as-of varisia "<current date>"` — the date gate decides what a
> campaign in progress is allowed to know.

- **Status:** **JOIN CANDIDATE — not yet canon in either direction.**
- **Appears in:** `third-beginnings` (as history, not as a person on screen)
- **Also claimed by:** a second campaign of this player's, run in a separate Claude Code
  session on their own machine. **That campaign's material has not been read and cannot be
  read from here** — see "The bridge problem" below.

## Why this file exists

The player noticed that *Third Beginnings* is set in **Roderic's Cove**, and that a "Roderic"
already exists in another campaign of theirs, and asked whether the two could be connected
narratively and in the world files.

They can. This file is the join point. It is deliberately **almost empty**, because the one
thing that would ruin the join is this session inventing a Roderic and then discovering the
other campaign had already established a different one.

## What is established, and by whom

| Fact | Established by | Status |
|---|---|---|
| Roderic's Cove is a settlement on the Varisian coast, named for a man called Roderic | published Varisian geography | **Published**, though the gazetteer detail could not be verified from this container — Archives of Nethys does not host setting text |
| The Cove's dredging economy, the sea caves beneath the cliff, and the Thassilonian door | `third-beginnings` | **This campaign's own invention**, labelled as such |
| Who Roderic actually was | **nobody yet** | **Open.** This is the gap Karsa is walking into, and the natural place for the other campaign's Roderic to land |
| Anything from the other campaign | — | **Unknown to this session** |

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
