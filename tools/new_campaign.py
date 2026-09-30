#!/usr/bin/env python3
"""new_campaign.py — scaffold `campaigns/<slug>/` from `templates/`.

Every `{{PLACEHOLDER}}` is filled with a neutral default so a fresh campaign folder holds no
unreplaced placeholder the moment it is created. The intake interview
(`system/01-campaign-intake.md`) then overwrites those defaults with the player's real
answers — the defaults exist so the scaffold is valid, not so it is finished.

Files whose name begins with `_` stay in `templates/` and are not copied: they are the
per-character, per-NPC, per-creature, per-map and per-session forms the GM copies as needed,
and they are only useful with their placeholders intact.

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

from roll import atomic_write, campaign_dir, repo_root, utc_now  # noqa: E402
import pf2e  # noqa: E402
import state as st  # noqa: E402

PLACEHOLDER_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")

# Directories that exist from the start even while empty, so the layout is obvious.
EMPTY_DIRS = ["characters", "npcs", "bestiary", "encounters", "maps", "sessions", "checkpoints",
              "logs", "gm-private/prep"]


def defaults(title: str, slug: str) -> dict[str, str]:
    """Neutral values for every placeholder. Intake replaces these with real answers."""
    return {
        "CAMPAIGN_TITLE": title,
        "CAMPAIGN_SLUG": slug,
        "CREATED_DATE": utc_now()[:10],
        "START_DATE": "1 Abadius 4725 AR",
        "ERA": "present day",
        "CALENDAR": "golarion (Absalom Reckoning)",
        "SHAPE": "not yet decided — see system/01-campaign-intake.md",
        "LEVEL_RANGE": "not yet decided",
        "ADVANCEMENT": "not yet decided",
        "GENRE": "not yet decided",
        "TONE": "not yet decided",
        "LETHALITY": "not yet decided",
        "SETTING": "not yet decided",
        "PITCH": "_Not written yet. Intake ends with three one-page pitches; the player picks one "
                 "before anything else is generated._",
        "PREMISE": "not yet decided",
        "ANTAGONIST": "not yet decided",
        "STAKES": "not yet decided",
        "PROTAGONIST_FRAMING": "_Not yet decided._",
        "PLAYER_CHARACTERS": "1",
        "GM_CHARACTERS": "0",
        "ALLY_STATUS": "none yet",
        "ASSUMPTION_GODS": "not yet decided",
        "ASSUMPTION_PLANES": "not yet decided",
        "ASSUMPTION_ANCESTRIES": "not yet decided",
        "ASSUMPTION_MAGIC": "not yet decided",
        "ASSUMPTION_TECH": "not yet decided",
        "THEMES": "_Not yet decided._",
        "INTAKE_NOTES": "_Intake has not been run yet._",
        "REGION": "not yet decided",
        "HOME_BASE": "not yet decided",
        "CLIMATE": "not yet decided",
        "SEASON": "not yet decided",
        # Rules deltas
        "DIFFICULTY_PRESET": "Standard",
        "ADJUSTMENT_DEFAULT": "off",
        "PARTY_SHAPE": "solo PC",
        "GM_ALLY": "off",
        "WEAK_MOOKS": "off",
        "FEWER_ENEMIES": "on",
        "ENEMY_CAP": "none",
        "HERO_POINTS": "1 (PF2e as written)",
        "HERO_REFRESH": "per session (PF2e as written)",
        "HP_CRIT_FIX": "off",
        "DEATH_CONSENT": "off",
        "AUTO_STABILISE": "off",
        "FREE_TREAT_WOUNDS": "off",
        "RETREAT_GUARANTEE": "off",
        "RECALL_GENEROSITY": "as written",
        "ENEMY_HP_DISPLAY": "wounded descriptors",
        "LIST_ACTIONS": "off",
        "FLAG_LETHAL_PLANS": "off",
        "TELEGRAPH": "off",
        # Player prefs
        "LINES": "_Not asked yet. Ask plainly, once, during intake._",
        "VEILS": "_Not asked yet._",
        "CHECK_IN_BEFORE": "_Not asked yet._",
        "TRANSPARENCY": "standard",
        "NARRATION_LENGTH": "not yet decided",
        "PROSE_VS_BULLETS": "not yet decided",
        "PERSON": "second person",
        "TENSE": "present",
        "NAME_RULES": "not yet decided",
        "TACTICAL_HINTS": "not yet decided",
        "REMIND_ACTIONS": "not yet decided",
        "SITTING_LENGTH": "not yet decided",
        "SCENE_BUDGET": "not yet decided",
        "SESSION_OPEN": "trailer",
        "CLIFFHANGER": "not yet decided",
        "CHECKPOINT_AGGRESSION": "as specified in system/05-checkpoint-protocol.md",
        "WORLDPREP_ENABLED": "off",
        "WORLDPREP_CADENCE": "—",
        "WORLD_PACE": "steady",
        "WORLDPREP_CAP": "3",
        "GRAPH_ENABLED": "off",
        "DIFFICULTY_CHECKIN": "3",
        # Forms that are not copied but whose names appear in prose
        "PC_NAME": "unnamed character",
        "PC_BACKSTORY": "_Not written yet._",
        "NPC_NAME": "unnamed NPC",
        "CREATURE_NAME": "unnamed creature",
        "MAP_NAME": "unnamed map",
        "SESSION_NUMBER": "0",
        "SESSION_TITLE": "not run yet",
        "PREP_NUMBER": "000",
        "PREP_DATE": utc_now()[:10],
    }


def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", str(name).lower()).strip("-")
    return s or "campaign"


def fill(text: str, values: dict[str, str]) -> tuple[str, set[str]]:
    missing: set[str] = set()

    def sub(m: re.Match[str]) -> str:
        key = m.group(1)
        if key in values:
            return values[key]
        missing.add(key)
        return m.group(0)

    return PLACEHOLDER_RE.sub(sub, text), missing


def scaffold(title: str, slug: str, overrides: dict[str, str], force: bool) -> tuple[Path, list[str]]:
    tdir = repo_root() / "templates"
    if not tdir.is_dir():
        raise SystemExit(f"new_campaign.py: no templates/ directory at {tdir}")
    cdir = campaign_dir(slug)
    if cdir.exists() and not force:
        raise SystemExit(
            f"new_campaign.py: campaigns/{slug}/ already exists. Pass --force only if you mean to "
            "overwrite a live campaign's files."
        )

    values = defaults(title, slug)
    values.update(overrides)
    written: list[str] = []
    missing: set[str] = set()

    for src in sorted(tdir.rglob("*")):
        if src.is_dir():
            continue
        rel = src.relative_to(tdir)
        if rel.name.startswith("_"):
            continue  # a form, not a campaign file
        dst = cdir / rel
        text = src.read_text(encoding="utf-8")
        filled, miss = fill(text, values)
        missing |= miss
        atomic_write(dst, filled)
        written.append(str(rel))

    for d in EMPTY_DIRS:
        (cdir / d).mkdir(parents=True, exist_ok=True)
        keep = cdir / d / ".gitkeep"
        if not any(p for p in (cdir / d).iterdir() if p.name != ".gitkeep"):
            keep.touch()

    # The audit log exists from the first moment, empty, so nothing has to create it later.
    log = cdir / "logs" / "rolls.jsonl"
    if not log.exists():
        log.write_text("", encoding="utf-8")
        written.append("logs/rolls.jsonl")
    dice_audit = cdir / "logs" / "dice-audit.md"
    if not dice_audit.exists():
        atomic_write(
            dice_audit,
            f"# Dice audit — {title}\n\nNot generated yet. Run:\n\n```\npython3 tools/analyze.py "
            f"--campaign {slug}\n```\n",
        )
        written.append("logs/dice-audit.md")

    if missing:
        raise SystemExit(
            "new_campaign.py: these placeholders have no default and were left unreplaced: "
            + ", ".join(sorted(missing))
            + ". Add them to defaults() in tools/new_campaign.py or pass --set KEY=VALUE."
        )
    return cdir, written


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="new_campaign.py", description="Scaffold a new campaign folder.")
    ap.add_argument("title")
    ap.add_argument("--slug", default=None)
    ap.add_argument("--transparency", default="standard", choices=["glass", "standard", "mystery"])
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE",
                    help="override a placeholder; repeatable")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--commit", action="store_true", help="git-commit the new folder")
    args = ap.parse_args(argv)

    slug = args.slug or slugify(args.title)
    overrides: dict[str, str] = {"TRANSPARENCY": args.transparency}
    for item in args.set:
        if "=" not in item:
            ap.error(f"--set wants KEY=VALUE, got {item!r}")
        k, v = item.split("=", 1)
        overrides[k.strip().upper()] = v

    cdir, written = scaffold(args.title, slug, overrides, args.force)

    rc = st.main(["--campaign", slug, "init", "--title", args.title,
                  "--transparency", args.transparency, "--force"])
    if rc != 0:
        return rc

    dash = repo_root() / "tools" / "dashboard.py"
    if dash.exists():
        proc = subprocess.run([sys.executable, str(dash), "--campaign", slug],
                              capture_output=True, text=True, cwd=str(repo_root()))
        print(proc.stdout.strip() if proc.returncode == 0
              else f"dashboard not generated: {(proc.stderr or proc.stdout).strip()}")

    # Prove the claim rather than asserting it.
    leftovers = []
    for p in sorted(cdir.rglob("*")):
        if not p.is_file() or p.suffix not in (".md", ".json", ".html"):
            continue
        hits = sorted(set(PLACEHOLDER_RE.findall(p.read_text(encoding="utf-8", errors="replace"))))
        if hits:
            leftovers.append(f"{p.relative_to(repo_root())}: {', '.join(hits)}")

    print(f"\ncampaigns/{slug}/ created from templates/ — {len(written)} file(s)")
    for w in written:
        print(f"  + {w}")
    print()
    if leftovers:
        print("⚠ unreplaced placeholders remain:")
        for l in leftovers:
            print(f"  {l}")
        return 1
    print("No unreplaced {{PLACEHOLDER}} anywhere in the new folder.")
    print()
    print("Per-character, per-NPC, per-creature, per-map and per-session forms stay in templates/")
    print("with their placeholders intact. Copy one when you need it:")
    for f in ("characters/_CHARACTER_TEMPLATE.md", "npcs/_NPC_TEMPLATE.md",
              "bestiary/_CREATURE_TEMPLATE.md", "maps/_MAP_TEMPLATE.md",
              "sessions/_SESSION_TEMPLATE.md", "gm-private/prep/_PREP_TEMPLATE.md"):
        print(f"  templates/{f}")
    print()
    print("Next: run the intake interview — system/01-campaign-intake.md. Nothing in this folder is")
    print("decided yet; the defaults exist so the scaffold is valid, not so it is finished.")

    if args.commit:
        subprocess.run(["git", "add", "-A", f"campaigns/{slug}"], cwd=str(repo_root()), check=False)
        subprocess.run(["git", "commit", "-q", "-m", f"new campaign: {args.title}", "--",
                        f"campaigns/{slug}"], cwd=str(repo_root()), check=False)
        print(f"\ncommitted campaigns/{slug}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
