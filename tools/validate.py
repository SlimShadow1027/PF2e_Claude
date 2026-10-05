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
import rules  # noqa: E402
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

    # Which game this campaign runs decides which resources exist and so which checks
    # mean anything. A campaign whose two files disagree is reported rather than resolved.
    declared_state = rules.declared_in_state(slug)
    declared_md = rules.declared_in_campaign_md(slug)
    if declared_state and declared_md and declared_state != declared_md:
        r.error(f"state.json says the ruleset is {declared_state!r} and CAMPAIGN.md says "
                f"{declared_md!r} — state.json wins; fix CAMPAIGN.md or re-run "
                f"`state.py --campaign {slug} migrate`")
    system = st.system_of(data)
    mod = rules.load(system)
    slot_word = st.SLOT_WORD.get(system, "rank")
    r.ok(f"ruleset: {mod.SYSTEM_NAME}")

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

        if isinstance(pc.get("level"), int) and pc["level"] < 0:
            r.error(f"{name}: level is negative ({pc['level']})")

        # The resources are the ruleset's, so the ruleset checks them. Before this, the
        # Pathfinder checks ran against every sheet — and on a D&D sheet every field they
        # look for is absent, so each one passed vacuously and a 5.5e campaign got no
        # resource validation at all.
        for level, message in mod.validate_character(pc, name, cur, mx):
            (r.error if level == "error" else r.warn)(message)

        for rank, e in (pc.get("spell_slots") or {}).items():
            if int(e.get("used", 0)) > int(e.get("max", 0)):
                r.error(f"{name}: {slot_word} {rank} has {e.get('used')} of {e.get('max')} slots used")
            if int(e.get("used", 0)) < 0:
                r.error(f"{name}: {slot_word} {rank} has negative slots used")

        # The condition lists belong to the ruleset, and the two games' lists overlap in
        # name while differing in effect — so checking a D&D sheet against Pathfinder's
        # list rejects `grappled` and accepts nothing it should.
        for c in pc.get("conditions") or []:
            cname = c.get("name")
            if cname not in mod.KNOWN_CONDITIONS:
                other = [sid for sid in rules.SYSTEMS
                         if sid != system and cname in rules.load(sid).KNOWN_CONDITIONS]
                extra = (f" It is a {rules.short_of(other[0])} condition." if other else "")
                r.error(f"{name}: {cname!r} is not a {mod.SYSTEM_SHORT} condition.{extra}")
            if cname in mod.TRACKED_SEPARATELY:
                r.error(f"{name}: {cname} is in the conditions list as well as its own field — "
                        "two copies of the same number")
            if cname in mod.VALUED_CONDITIONS and not c.get("value"):
                r.error(f"{name}: {cname} carries no value but always takes one")
            if cname in mod.UNVALUED_CONDITIONS and c.get("value") is not None:
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
            for level, message in mod.validate_combatant(c, str(c.get("name"))):
                (r.error if level == "error" else r.warn)(message)
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
    check_campaign_calendar(slug, data, r)
    check_campaign_world_link(slug, data, r)


def _strip_timestamps(text: str) -> str:
    return re.sub(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", "<ts>", text)


def check_campaign_calendar(slug: str, data: dict[str, Any], r: Report) -> None:
    """A linked campaign must keep its world's calendar, or the dates mean nothing.

    Found by the test_campaign run: `world.py link` wrote `Start date: 3 Gozran 4729 AR`
    into CAMPAIGN.md while state.json still held the D&D default `generic` calendar, so
    `status`, CHECKPOINT.md and the dashboard all showed "1 Month 1 1" for a campaign the
    campaign file dated in Absalom Reckoning — two places holding disagreeing copies of
    the same fact, which is the exact failure the framework exists to prevent.
    """
    world = rules.world_of_campaign(slug)
    if not world:
        return
    in_state = str((data.get("time") or {}).get("calendar") or "").lower()
    if not in_state:
        r.error(f"state.json has no time.calendar, but this campaign is linked to worlds/{world}")
        return
    try:
        declared = wd.world_calendar_name(world)
    except Exception:  # a malformed CALENDAR.md is reported by check_world
        return
    if declared and in_state != declared:
        r.error(
            f"state.json uses the {in_state!r} calendar but worlds/{world} uses {declared!r} — "
            f"the world owns the calendar, so dates in this campaign do not line up with the "
            f"chronicle. Fix with `python3 tools/state.py --campaign {slug} "
            f"set time.calendar {declared}` and set the year, month and day to match "
            f"CAMPAIGN.md's start date."
        )
    elif declared:
        r.ok(f"calendar matches worlds/{world}: {declared}")


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

    # Which rulesets actually read this world. A world hosting both has a higher bar: its
    # entries have to say which game wrote them and how far the event reached, because a
    # reader in the other game has no way to recover either from the prose.
    systems = rules.for_world(wslug)
    cross = len(systems) > 1
    if cross:
        r.ok(f"cross-system world: {', '.join(rules.short_of(x) for x in systems)}")

    for e in entries:
        if not e.campaign:
            r.error(f"chronicle entry {e.title!r} has no **Campaign:** tag")
        if e.visibility not in wd.VISIBILITIES:
            r.error(f"chronicle entry {e.title!r} has visibility {e.visibility!r}; "
                    f"it must be one of {', '.join(wd.VISIBILITIES)}")
        if not e.happened.strip():
            r.error(f"chronicle entry {e.title!r} says nothing under **What happened:**")
        if e.system and not rules.is_known(e.system):
            r.error(f"chronicle entry {e.title!r} names system {e.system!r}, which is not a "
                    f"ruleset this framework knows ({', '.join(sorted(rules.SYSTEMS))})")
        elif not e.system:
            if cross:
                r.error(f"chronicle entry {e.title!r} has no **System:** line, and this world is "
                        f"read by {', '.join(rules.short_of(x) for x in systems)} — a reader in "
                        f"the other game cannot tell which rules produced it")
            else:
                r.warn(f"chronicle entry {e.title!r} has no **System:** line (written before the "
                       f"field existed; harmless while only one ruleset reads this world)")
        if e.scope and e.scope not in rules.SCOPE_NAMES:
            r.error(f"chronicle entry {e.title!r} has scope {e.scope!r}; it must be one of "
                    f"{', '.join(rules.SCOPE_NAMES)}")
        elif not e.scope and cross:
            r.warn(f"chronicle entry {e.title!r} has no **Scope:** line — scope is the one field "
                   f"that means anything to the other ruleset in this world")

    # A cross-system world needs one calendar, or its two campaigns cannot share a timeline.
    if cross:
        try:
            declared = rules.load_world_calendar(wslug)
        except rules.RulesError as exc:
            r.error(f"worlds/{wslug}/CALENDAR.md: {exc}")
            declared = None
        cals = {e.date.era for e in entries if e.date.era}
        if len(cals) > 1:
            r.warn(f"worlds/{wslug}/CHRONICLE.md mixes eras ({', '.join(sorted(cals))}) — a shared "
                   f"world should keep one calendar so both campaigns read one timeline")
        # A world may either define its own calendar in a block or name a built-in in the
        # `Calendar in use:` field. Either is a single written answer, which is all a shared
        # timeline needs; only naming neither is a problem.
        named = wd.world_calendar_name(wslug)
        if not named:
            r.warn(f"worlds/{wslug}/CALENDAR.md names no calendar and defines none, and this "
                   f"world is read by more than one ruleset — name a built-in in "
                   f"`Calendar in use:` or define one in the CALENDAR block, so every campaign "
                   f"here shares a timeline")
        else:
            r.ok(f"calendar: {named}, shared by every campaign in this world")

    # The forbidden crossing: a ruleset's own numbers in the shared layer.
    for e in entries:
        blob = f"{e.happened} {e.changed}"
        for pat, what in (
            (r"\bDC\s*\d+", "a DC"),
            (r"\bAC\s*\d+", "an AC"),
            (r"\bCR\s*\d+", "a Challenge Rating"),
            (r"\blevel[- ]\d+\b", "a level"),
            (r"\b\d+d\d+\b", "a dice expression"),
        ):
            if re.search(pat, blob, re.IGNORECASE):
                r.warn(f"chronicle entry {e.title!r} mentions {what} — the shared layer records "
                       f"what happened, not anyone's numbers, because the other ruleset's reader "
                       f"cannot use them (`python3 tools/world.py crossing`)")
                break

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
            sysname = pf2e.read_field(text, "System")
            if sysname and not rules.is_known(sysname):
                # The field holds a display name, so try the campaign's own answer before failing.
                by_campaign = (rules.for_campaign(cname.strip())
                               if cname and cname.strip() in known else None)
                if not by_campaign or rules.short_of(by_campaign) not in sysname:
                    r.warn(f"{p.relative_to(repo_root())} names system {sysname!r}, which does not "
                           f"resolve to a known ruleset")
            elif not sysname and len(rules.for_world(wslug)) > 1:
                r.error(f"{p.relative_to(repo_root())} has no **System:** field, and this world is "
                        f"read by more than one ruleset — the level on this page means nothing "
                        f"without it")
            scope = pf2e.read_field(text, "Scope reached")
            if scope:
                band = scope.split("—")[0].strip().lower()
                if band and band not in rules.SCOPE_NAMES and not band.startswith("_("):
                    r.warn(f"{p.relative_to(repo_root())} has scope {band!r}; it must be one of "
                           f"{', '.join(rules.SCOPE_NAMES)}")


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
