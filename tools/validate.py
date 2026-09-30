#!/usr/bin/env python3
"""validate.py — catch the mechanical classes of drift before they compound.

This checks the things a language model gets wrong quietly: hit points above maximum,
negative resources, conditions whose duration has run out but which are still listed,
`CHECKPOINT.md` out of step with `state.json`, characters in state with no sheet file,
bestiary entries with no `Source:` line, encounters with no objective, unreplaced template
placeholders, and every rule the shared-world layer depends on — including that no live
state has leaked into `worlds/` and that no campaign is reading world material dated after
its own current in-world date.

Exit status: 0 when clean, 1 when an error was found, 2 on a usage problem.
Warnings do not fail the run unless `--strict` is passed.

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

from roll import campaign_dir, list_campaigns, repo_root, world_dir  # noqa: E402
import pf2e  # noqa: E402
import state as st  # noqa: E402
import world as wd  # noqa: E402

PLACEHOLDER_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.passed: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def ok(self, msg: str) -> None:
        self.passed.append(msg)

    def print(self, verbose: bool = False) -> None:
        if verbose:
            for p in self.passed:
                print(f"  ok    {p}")
        for w in self.warnings:
            print(f"  warn  {w}")
        for e in self.errors:
            print(f"  ERROR {e}")


# --------------------------------------------------------------------------------------
# Campaign checks
# --------------------------------------------------------------------------------------


def check_campaign(slug: str, r: Report) -> None:
    cdir = campaign_dir(slug)
    if not cdir.is_dir():
        r.error(f"no campaign folder at campaigns/{slug}")
        return

    # -- state.json ------------------------------------------------------------
    spath = cdir / "state.json"
    if not spath.exists():
        r.error(f"campaigns/{slug}/state.json is missing — the canonical state has nowhere to live")
        return
    try:
        data = json.loads(spath.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        r.error(f"state.json is not valid JSON: {exc}")
        return
    r.ok("state.json parses")

    if data.get("schema_version") != st.SCHEMA_VERSION:
        r.warn(f"state.json schema_version is {data.get('schema_version')}, this tooling writes "
               f"{st.SCHEMA_VERSION}")
    if data.get("campaign") != slug:
        r.error(f"state.json says campaign {data.get('campaign')!r} but lives in campaigns/{slug}")
    if data.get("transparency") not in ("glass", "standard", "mystery"):
        r.error(f"transparency mode {data.get('transparency')!r} is not one of glass/standard/mystery")

    # -- characters ------------------------------------------------------------
    for key, pc in (data.get("pcs") or {}).items():
        name = pc.get("name", key)
        hp = pc.get("hp") or {}
        cur, mx, temp = hp.get("current", 0), hp.get("max", 0), hp.get("temp", 0)
        if not isinstance(cur, int) or not isinstance(mx, int):
            r.error(f"{name}: HP is not integral ({cur}/{mx})")
        elif cur > mx:
            r.error(f"{name}: HP {cur} is above maximum {mx}")
        elif cur < 0:
            r.error(f"{name}: HP {cur} is negative")
        if isinstance(temp, int) and temp < 0:
            r.error(f"{name}: temporary HP {temp} is negative")
        if mx <= 0:
            r.warn(f"{name}: maximum HP is {mx} — set it before play")

        for field in ("hero_points", "dying", "wounded", "doomed", "level"):
            v = pc.get(field, 0)
            if isinstance(v, int) and v < 0:
                r.error(f"{name}: {field} is negative ({v})")
        if int(pc.get("hero_points", 0)) > int(pc.get("hero_points_max", 3)):
            r.error(f"{name}: {pc.get('hero_points')} Hero Points, above the cap of {pc.get('hero_points_max')}")
        dying_limit = int(pc.get("dying_max", 4)) - int(pc.get("doomed", 0))
        if int(pc.get("dying", 0)) >= dying_limit and dying_limit > 0:
            r.warn(f"{name}: dying {pc.get('dying')} is at or past the death threshold {dying_limit}")
        if int(pc.get("dying", 0)) > 0 and cur > 0:
            r.error(f"{name}: dying {pc.get('dying')} while at {cur} HP — dying ends at 1 HP or more")

        f = pc.get("focus") or {}
        if int(f.get("current", 0)) > int(f.get("max", 0)):
            r.error(f"{name}: {f.get('current')} Focus Points, above the pool maximum {f.get('max')}")
        if int(f.get("current", 0)) < 0:
            r.error(f"{name}: negative Focus Points")
        for rank, e in (pc.get("spell_slots") or {}).items():
            if int(e.get("used", 0)) > int(e.get("max", 0)):
                r.error(f"{name}: rank {rank} has {e.get('used')} of {e.get('max')} slots used")
            if int(e.get("used", 0)) < 0:
                r.error(f"{name}: rank {rank} has negative slots used")

        for c in pc.get("conditions") or []:
            cname = c.get("name")
            if cname not in st.KNOWN_CONDITIONS:
                r.error(f"{name}: {cname!r} is not a PF2e condition")
            if cname in st.TRACKED_SEPARATELY:
                r.error(f"{name}: {cname} is in the conditions list as well as its own field — "
                        "two copies of the same number")
            if cname in st.VALUED_CONDITIONS and not c.get("value"):
                r.error(f"{name}: {cname} carries no value but always takes one")
            if cname in st.UNVALUED_CONDITIONS and c.get("value") is not None:
                r.error(f"{name}: {cname} carries a value but does not take one")
            dur = c.get("duration") or {}
            if dur.get("kind") not in st.DURATION_KINDS:
                r.error(f"{name}: {cname} has duration kind {dur.get('kind')!r}")
            rem = dur.get("remaining")
            if rem is not None and isinstance(rem, (int, float)) and rem <= 0:
                r.error(f"{name}: {cname} has {rem} {dur.get('kind')} left but is still listed — "
                        "expired conditions should be ticked off")

        sheet = pc.get("sheet") or f"characters/{key}.md"
        if not (cdir / sheet).exists():
            r.error(f"{name} is in state.json but has no sheet file at campaigns/{slug}/{sheet}")

    if not (data.get("pcs") or {}):
        r.warn("state.json holds no characters yet")

    # -- party -----------------------------------------------------------------
    gold = (data.get("party") or {}).get("gold") or {}
    for coin in ("pp", "gp", "sp", "cp"):
        if int(gold.get(coin, 0)) < 0:
            r.error(f"the purse holds {gold.get(coin)} {coin} — negative coins")
    if int((data.get("party") or {}).get("xp", 0)) < 0:
        r.error("party XP is negative")

    for row in st.bulk_report(data):
        if row["over_max"]:
            r.error(f"{row['name']} carries {row['counted']:.1f} Bulk that counts, "
                    f"over the maximum of {row['max']}")
        elif row["encumbered"]:
            r.warn(f"{row['name']} carries {row['counted']:.1f} Bulk that counts and is encumbered "
                   f"(clumsy 1 and a 10-foot Speed penalty) — is that recorded as a condition?")

    # -- clocks ----------------------------------------------------------------
    for name, c in (data.get("clocks") or {}).items():
        if int(c.get("filled", 0)) > int(c.get("segments", 0)):
            r.error(f"clock {name!r} is filled {c.get('filled')} of {c.get('segments')}")
        if int(c.get("filled", 0)) < 0:
            r.error(f"clock {name!r} has negative segments filled")
        if c.get("ticking") and not c.get("rate"):
            r.warn(f"clock {name!r} is marked ticking but states no rate, so an off-screen turn "
                   "cannot advance it")

    # -- encounter -------------------------------------------------------------
    enc = data.get("encounter")
    if enc:
        if not enc.get("objective"):
            r.error("the live encounter has no objective — every encounter names one "
                    "(system/17-encounter-objectives.md)")
        if not enc.get("telegraphed"):
            r.warn("the live encounter's objective has not been telegraphed to the player; "
                   "a timer the player cannot see is a trap, not a tactical problem")
        ids = [c.get("id") for c in enc.get("combatants") or []]
        if len(ids) != len(set(ids)):
            r.error("the live encounter has duplicate combatant ids")
        for c in enc.get("combatants") or []:
            if c.get("ref") and c["ref"] not in (data.get("pcs") or {}):
                r.error(f"combatant {c.get('name')} points at character {c['ref']!r}, which is not in pcs")
            if not c.get("ref") and not c.get("hp"):
                r.error(f"combatant {c.get('name')} is not a party member and has no HP block")
            if int(c.get("actions_remaining", 0)) < 0:
                r.error(f"combatant {c.get('name')} has negative actions remaining")
            if int(c.get("map_step", 0)) not in (0, 1, 2):
                r.error(f"combatant {c.get('name')} has MAP step {c.get('map_step')}; it runs 0-2")
        idx = int(enc.get("turn_index", 0))
        if enc.get("combatants") and not 0 <= idx < len(enc["combatants"]):
            r.error(f"the live encounter's turn_index {idx} is outside its combatant list")
        if enc.get("map") and not (cdir / "maps" / f"{enc['map']}.md").exists():
            r.warn(f"the encounter names map {enc['map']!r} but campaigns/{slug}/maps/{enc['map']}.md "
                   "does not exist")

    # -- CHECKPOINT.md in sync -------------------------------------------------
    cpath = cdir / "CHECKPOINT.md"
    if not cpath.exists():
        r.error("CHECKPOINT.md is missing — run `state.py render`")
    else:
        on_disk = cpath.read_text(encoding="utf-8")
        try:
            rendered = st.render_checkpoint(slug, data)
        except (st.StateError, KeyError, TypeError, ValueError) as exc:
            r.error(f"state.json cannot be rendered, so CHECKPOINT.md cannot be checked against it: {exc}")
            rendered = on_disk  # do not also report a spurious mismatch
        if _strip_timestamps(rendered) != _strip_timestamps(on_disk):
            r.error("CHECKPOINT.md does not match state.json — state.json wins; run "
                    f"`python3 tools/state.py --campaign {slug} render`")
        else:
            r.ok("CHECKPOINT.md matches state.json")
        if len(on_disk.splitlines()) > 400:
            r.warn(f"CHECKPOINT.md is {len(on_disk.splitlines())} lines; it should stay under ~400 so "
                   "reloading it is cheap. Move deep history into sessions/ and CANON.md.")

    # -- expected files --------------------------------------------------------
    for rel in ("CAMPAIGN.md", "RULES_DELTAS.md", "PLAYER_PREFS.md", "FLAGS.md", "CANON.md",
                "QUESTS.md", "CLOCKS.md", "TIMELINE.md", "WORLD.md", "npcs/ROSTER.md",
                "characters/PARTY.md", "encounters/history.md", "logs/loot.md",
                "gm-private/README.md"):
        if not (cdir / rel).exists():
            r.warn(f"campaigns/{slug}/{rel} is missing")

    # -- placeholders ----------------------------------------------------------
    for p in sorted(cdir.rglob("*.md")):
        try:
            text = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        hits = sorted(set(PLACEHOLDER_RE.findall(text)))
        if hits:
            r.error(f"{p.relative_to(repo_root())} still holds unreplaced placeholders: {', '.join(hits)}")

    # -- bestiary --------------------------------------------------------------
    bdir = cdir / "bestiary"
    if bdir.is_dir():
        for p in sorted(bdir.glob("*.md")):
            if p.name.startswith("_") or p.name == "README.md":
                continue
            text = p.read_text(encoding="utf-8")
            if not re.search(r"^\s*[-*>#]*\s*\**Source\**\s*:", text, re.MULTILINE | re.IGNORECASE):
                r.error(f"{p.relative_to(repo_root())} has no `Source:` line — creature statistics come "
                        "from published material, cited by name, source and level")
            if re.search(r"homebrew", text, re.IGNORECASE) and not re.search(
                r"reskin of|rebuilt from|benchmark", text, re.IGNORECASE
            ):
                r.warn(f"{p.relative_to(repo_root())} is marked homebrew but names no base creature or "
                       "benchmark table")

    # -- encounter history objectives -----------------------------------------
    hpath = cdir / "encounters" / "history.md"
    if hpath.exists():
        text = hpath.read_text(encoding="utf-8")
        blocks = re.split(r"^##\s+", text, flags=re.MULTILINE)[1:]
        for b in blocks:
            title = b.splitlines()[0].strip()
            if title.lower().startswith(("how to", "template", "format")):
                continue
            if not re.search(r"^\s*[-*]?\s*\**Objective\**\s*:", b, re.MULTILINE | re.IGNORECASE):
                r.error(f"encounters/history.md entry {title!r} has no `Objective:` field")

    # -- the shared-world date gate -------------------------------------------
    check_campaign_world_link(slug, data, r)


def _strip_timestamps(text: str) -> str:
    return re.sub(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", "<ts>", text)


def check_campaign_world_link(slug: str, data: dict[str, Any], r: Report) -> None:
    cdir = campaign_dir(slug)
    cpath = cdir / "CAMPAIGN.md"
    if not cpath.exists():
        return
    text = cpath.read_text(encoding="utf-8")
    value = pf2e.read_field(text, "World")
    if value is None:
        r.warn("CAMPAIGN.md has no `World:` field — write `World: none` for a standalone campaign")
        return
    value = value.strip().strip("`")
    if value.lower() in ("none", "-", "—"):
        # Only a reference naming an actual world folder is a dependency; prose that says
        # "a world under `worlds/`" is just prose.
        dep = re.compile(r"worlds/[a-z0-9][a-z0-9-]*")
        stray = [
            str(p.relative_to(repo_root()))
            for p in cdir.rglob("*.md")
            if p.name != "CAMPAIGN.md" and dep.search(p.read_text(encoding="utf-8", errors="replace"))
        ]
        if stray:
            r.warn("this campaign is `World: none` but these files mention worlds/: " + ", ".join(stray))
        else:
            r.ok("World: none — nothing references the shared-world layer")
        return

    wslug = value.split("/")[-1]
    wdir_ = world_dir(wslug)
    if not wdir_.is_dir():
        r.error(f"CAMPAIGN.md says `World: {value}` but worlds/{wslug}/ does not exist")
        return
    r.ok(f"World: worlds/{wslug} exists")

    # The date gate: nothing the campaign has read may be dated after its own current date.
    cur_raw: str | None = None
    cur_raw = pf2e.read_field(text, "Start date")
    t = data.get("time") or {}
    try:
        current = wd.WorldDate(int(t.get("year", 0)), int(t.get("month", 1)), int(t.get("day", 1)))
        if int(t.get("year", 0)) == 0 and cur_raw:
            current = wd.parse_date(cur_raw)
    except (ValueError, wd.WorldError):
        r.warn("cannot read this campaign's current in-world date, so the date gate cannot be checked")
        return

    try:
        _, entries = wd.read_chronicle(wslug)
    except wd.WorldError as exc:
        r.error(str(exc))
        return
    later = [e for e in entries if e.date.key() > current.key()]
    if later:
        r.ok(f"{len(later)} chronicle entry/entries are dated after {current} and are gated out of this "
             "campaign's reads")
        for e in later:
            for p in list(cdir.rglob("*.md")):
                if p.parts[-2:] == ("checkpoints",):
                    continue
                try:
                    body = p.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    continue
                if e.title and e.title in body:
                    r.error(
                        f"{p.relative_to(repo_root())} mentions the chronicle entry {e.title!r}, dated "
                        f"{e.date}, which is after this campaign's current date {current} — the date gate "
                        "has been breached"
                    )


# --------------------------------------------------------------------------------------
# World checks
# --------------------------------------------------------------------------------------


def check_world(wslug: str, r: Report) -> None:
    root = world_dir(wslug)
    if not root.is_dir():
        r.error(f"no world at worlds/{wslug}")
        return
    for rel in ("README.md", "CHRONICLE.md", "LEGENDS.md", "GAZETTEER.md", "FACTIONS.md",
                "CALENDAR.md", "canon.md"):
        if not (root / rel).exists():
            r.warn(f"worlds/{wslug}/{rel} is missing")

    try:
        _, entries = wd.read_chronicle(wslug)
    except wd.WorldError as exc:
        r.error(str(exc))
        entries = []
    else:
        r.ok(f"CHRONICLE.md parses ({len(entries)} entry/entries)")

    keys = [e.date.key() for e in entries]
    if keys != sorted(keys):
        r.error("CHRONICLE.md entries are not in date order — it is append-only and read in order")
    for e in entries:
        if not e.campaign:
            r.error(f"chronicle entry {e.title!r} has no **Campaign:** tag")
        if e.visibility not in wd.VISIBILITIES:
            r.error(f"chronicle entry {e.title!r} has visibility {e.visibility!r}; "
                    f"it must be one of {', '.join(wd.VISIBILITIES)}")
        if not e.happened.strip():
            r.error(f"chronicle entry {e.title!r} says nothing under **What happened:**")

    # No live state anywhere under worlds/.
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in (".md", ".json", ".jsonl", ".txt"):
            continue
        if p.name == "README.md" and p.parent == root:
            pass  # the README quotes the rule itself
        try:
            text = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        lowered = text.lower()
        for marker in wd.LIVE_STATE_MARKERS:
            for i, line in enumerate(lowered.splitlines(), start=1):
                if marker not in line:
                    continue
                # Skip the places that name the rule rather than break it.
                if any(x in line for x in ("never", "no live", "not copied", "stay in", "remain in",
                                           "would mean", "refuses", "live state")):
                    continue
                if line.lstrip().startswith(("#", ">", "_")):
                    continue
                r.error(f"{p.relative_to(repo_root())}:{i} looks like live state in the world layer "
                        f"({marker!r}) — hit points, coins, inventory, conditions and positions never "
                        "leave campaigns/")
    if not r.errors:
        r.ok("no live-state fields found under worlds/")

    # Legacy records must name a campaign that exists.
    cdir = root / "characters"
    if cdir.is_dir():
        known = set(list_campaigns())
        for p in sorted(cdir.glob("*.md")):
            text = p.read_text(encoding="utf-8")
            cname = pf2e.read_field(text, "Campaign")
            if cname is None:
                r.error(f"{p.relative_to(repo_root())} has no **Campaign:** field, so this character "
                        "cannot be traced to a campaign")
            elif cname.strip() not in known:
                r.warn(f"{p.relative_to(repo_root())} names campaign {cname.strip()!r}, which is not "
                       "in campaigns/ (fine if that campaign has been archived elsewhere)")


# --------------------------------------------------------------------------------------
# Repository-wide checks
# --------------------------------------------------------------------------------------


def check_repo(r: Report) -> None:
    root = repo_root()
    for rel in ("CLAUDE.md", "README.md", "DESIGN_NOTES.md", "LICENSE_NOTES.md"):
        if not (root / rel).exists():
            r.warn(f"{rel} is missing from the repository root")
    for rel in ("system", "tools", "templates", ".claude/commands"):
        if not (root / rel).is_dir():
            r.warn(f"{rel}/ is missing")
    # Nothing campaign-specific outside campaigns/.
    campaigns = list_campaigns()
    for d in ("system", "templates", "tools", ".claude"):
        base = root / d
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*")):
            if not p.is_file() or p.suffix.lower() not in (".md", ".py", ".json"):
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for slug in campaigns:
                if slug in ("test-run",) or slug.startswith("."):
                    continue
                if re.search(rf"campaigns/{re.escape(slug)}\b", text):
                    r.warn(f"{p.relative_to(root)} names the campaign {slug!r}; the root-level files "
                           "must stay campaign-agnostic (an example in prose is fine, a dependency is not)")
    if not r.errors:
        r.ok("no campaign-specific content found outside campaigns/")


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="validate.py", description="Catch mechanical drift.")
    ap.add_argument("--campaign", action="append", default=[], help="repeatable; omit with --all")
    ap.add_argument("--world", action="append", default=[], help="repeatable")
    ap.add_argument("--all", action="store_true", help="every campaign and every world")
    ap.add_argument("--repo", action="store_true", help="also run the repository-wide checks")
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    ap.add_argument("-v", "--verbose", action="store_true", help="also list the checks that passed")
    args = ap.parse_args(argv)

    campaigns = list(args.campaign)
    worlds = list(args.world)
    if args.all:
        campaigns = list_campaigns()
        wroot = repo_root() / "worlds"
        worlds = sorted(p.name for p in wroot.iterdir() if p.is_dir()) if wroot.is_dir() else []
    if not campaigns and not worlds and not args.repo and not args.all:
        ap.error("pass --campaign, --world, --repo or --all")

    total = Report()
    failed = False
    for slug in campaigns:
        r = Report()
        check_campaign(slug, r)
        print(f"campaign {slug}: {len(r.errors)} error(s), {len(r.warnings)} warning(s)")
        r.print(args.verbose)
        total.errors += r.errors
        total.warnings += r.warnings
    for w in worlds:
        r = Report()
        check_world(w, r)
        print(f"world {w}: {len(r.errors)} error(s), {len(r.warnings)} warning(s)")
        r.print(args.verbose)
        total.errors += r.errors
        total.warnings += r.warnings
    if args.repo or args.all:
        r = Report()
        check_repo(r)
        print(f"repository: {len(r.errors)} error(s), {len(r.warnings)} warning(s)")
        r.print(args.verbose)
        total.errors += r.errors
        total.warnings += r.warnings

    print()
    if total.errors:
        print(f"FAIL — {len(total.errors)} error(s), {len(total.warnings)} warning(s)")
        return 1
    if total.warnings and args.strict:
        print(f"FAIL (strict) — {len(total.warnings)} warning(s)")
        return 1
    print(f"PASS — 0 errors, {len(total.warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
