# PF2e_Claude

A kit for running **Pathfinder Second Edition (Remaster)** campaigns with Claude as Game Master,
built for solo and very small tables.

Right now this repository contains the **setup prompt**, not the framework itself.

## Files

| File | What it is |
|---|---|
| `PROMPT.md` | The prompt to paste into a fresh Claude Code session. That session builds the whole framework — system docs, dice tooling, state tracking, templates, slash commands. Appendices at the bottom hold the short prompts for creating a campaign, making a character, and resuming play. |
| `EXTRAS.md` | Optional features and systems not baked into the prompt, with a recommendation on each. Add the ones you want to `PROMPT.md` before running it, or bolt them on later. |

## How to use it

1. Read `PROMPT.md`. Delete or add anything you disagree with — it's a spec, and it's easier to change
   now than after a framework is built on it.
2. Open a new Claude Code session in this repo and paste the block between `=== BEGIN PROMPT ===` and
   `=== END PROMPT ===`.
3. Let it build and verify the framework, then use Appendix A to create your first campaign.

Campaigns are generated into `campaigns/<slug>/`, so the core stays reusable across as many campaigns
as you want to run.

## Design principles the prompt enforces

- **Dice are real.** Every roll comes out of `tools/roll.py` using a system random source, and every
  roll — public or private — is written to an append-only audit log you can read afterward.
- **Private is not the same as fudged.** Secret checks and enemy saves get rolled genuinely; only the
  display is withheld.
- **Creatures come from published stat blocks**, cited by source. Homebrew names its base creature.
- **One source of truth per kind of fact.** Volatile numbers live in `state.json`; prose and built
  character choices live in Markdown. `CHECKPOINT.md` is rendered from state, never hand-edited.
- **Nothing campaign-specific lives outside `campaigns/`.**
