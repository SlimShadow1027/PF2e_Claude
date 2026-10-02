#!/usr/bin/env python3
"""rules.py — which game's numbers a campaign runs on, and the parts both games share.

This framework runs two rulesets:

    pf2e    Pathfinder Second Edition (Remaster)  — tables in tools/pf2e.py
    dnd5e   Dungeons & Dragons 2024 ("5.5e")      — tables in tools/dnd5e.py

A campaign declares one in `state.json` (`"system"`) and in `CAMPAIGN.md` (`System:`).
Campaigns created before the second ruleset existed declare neither, and are read as
`pf2e` — that is the only reason a default exists. **New campaigns always write the field.**

Three things live here rather than in either ruleset, because they belong to neither:

1.  **The registry.** `load("5.5e")` returns the `dnd5e` module. Aliases resolve here so
    that no caller has to know how the player spelled it.
2.  **Markdown field IO.** `read_field` / `set_field`, so the six tools that read a
    `World:` or `System:` line cannot disagree about the syntax. These moved here from
    `pf2e.py`, which re-exports them; nothing that imported them from there broke.
3.  **The calendar.** A calendar belongs to the **world**, not to the ruleset — a shared
    world keeps one calendar no matter which game is being played in it this month. The
    engine is here; each ruleset registers the calendars it ships with, and a world may
    define its own in `worlds/<slug>/CALENDAR.md`.

Also here: `scope_band`, the only honest form of cross-system translation. See
`system/23-cross-system-worlds.md` for why levels do not convert and scope does.

Standard library only.
"""

from __future__ import annotations

import importlib
import json
import re
from pathlib import Path
from typing import Any, Iterable, Sequence

# --------------------------------------------------------------------------------------
# The registry
# --------------------------------------------------------------------------------------

#: canonical id -> everything a caller needs before importing the module itself.
SYSTEMS: dict[str, dict[str, Any]] = {
    "pf2e": {
        "module": "pf2e",
        "name": "Pathfinder Second Edition (Remaster)",
        "short": "PF2e",
        "licence": "ORC",
        "aliases": ("pf2e", "pf2", "p2e", "pathfinder", "pathfinder2e", "pathfinder-2e", "2e"),
    },
    "dnd5e": {
        "module": "dnd5e",
        "name": "Dungeons & Dragons 2024 (5.5e)",
        "short": "D&D 5.5e",
        "licence": "CC-BY-4.0",
        "aliases": (
            "dnd5e", "dnd5.5e", "dnd-5.5e", "5.5e", "55e", "dnd2024", "dnd-2024",
            "5e2024", "5e-2024", "dnd5e2024", "5e", "dnd", "d&d", "dd5e",
        ),
    },
}

#: Read a campaign that declares no system as this one. Only for pre-5.5e campaigns.
DEFAULT_SYSTEM = "pf2e"

_ALIASES: dict[str, str] = {}
for _sid, _meta in SYSTEMS.items():
    _ALIASES[_sid] = _sid
    for _a in _meta["aliases"]:
        _ALIASES[_a] = _sid
    # The display names resolve too, because the Markdown layer writes those: a legacy
    # record's `System:` line and a world README's column hold "D&D 5.5e" or
    # "Pathfinder Second Edition (Remaster)", and those have to read back.
    _ALIASES[re.sub(r"[\s_]+", "", _meta["name"].lower())] = _sid
    _ALIASES[re.sub(r"[\s_]+", "", _meta["short"].lower())] = _sid


class RulesError(Exception):
    """A ruleset was named that does not exist, or asked for something it does not do."""


def _norm(text: str) -> str:
    return re.sub(r"[\s_]+", "", str(text).strip().lower())


def canonical(name: str | None) -> str:
    """'5.5e' -> 'dnd5e'. An unknown name raises rather than silently defaulting."""
    if name is None or not str(name).strip():
        return DEFAULT_SYSTEM
    key = _norm(name)
    if key in _ALIASES:
        return _ALIASES[key]
    known = ", ".join(sorted(SYSTEMS))
    raise RulesError(f"{name!r} is not a ruleset this framework knows ({known})")


def is_known(name: str | None) -> bool:
    try:
        canonical(name)
    except RulesError:
        return False
    return True


def meta(system: str | None = None) -> dict[str, Any]:
    """The registry entry for a system, with its canonical id added as `id`."""
    sid = canonical(system)
    return {"id": sid, **SYSTEMS[sid]}


def name_of(system: str | None) -> str:
    return meta(system)["name"]


def short_of(system: str | None) -> str:
    return meta(system)["short"]


def load(system: str | None = None):
    """The rules module for a system. `load('5.5e').encounter_budgets(...)`."""
    sid = canonical(system)
    return importlib.import_module(SYSTEMS[sid]["module"])


def load_all() -> dict[str, Any]:
    return {sid: load(sid) for sid in SYSTEMS}


def require(system: str | None, attr: str):
    """Fetch an attribute off a ruleset module with an error that names the ruleset.

    Duck typing with a readable failure: a ruleset that does not implement something says
    so by name, instead of raising AttributeError three frames deep in a caller.
    """
    sid = canonical(system)
    mod = load(sid)
    if not hasattr(mod, attr):
        raise RulesError(f"{SYSTEMS[sid]['short']} does not implement {attr!r}")
    return getattr(mod, attr)


def supports(system: str | None, attr: str) -> bool:
    return hasattr(load(system), attr)


# --------------------------------------------------------------------------------------
# Markdown front-matter-ish fields
# --------------------------------------------------------------------------------------

# Matches `World: x`, `- World: x`, `- **World:** x` and `**World**: x` alike, so the
# tools that read these fields cannot disagree about the syntax.
def _field_re(name: str) -> re.Pattern[str]:
    return re.compile(
        rf"^(?P<lead>\s*[-*]?\s*\*{{0,2}}{re.escape(name)}\*{{0,2}}\s*:\*{{0,2}}\s*)(?P<value>.*?)\s*$",
        re.MULTILINE | re.IGNORECASE,
    )


def read_field(text: str, name: str) -> str | None:
    """The value of a `Name:` field in a Markdown file, or None if it is absent."""
    m = _field_re(name).search(text)
    return m.group("value").strip() if m else None


def set_field(text: str, name: str, value: str) -> str:
    """Replace a `Name:` field's value in place, or append the field if it is absent."""
    pat = _field_re(name)
    if pat.search(text):
        return pat.sub(lambda m: m.group("lead") + value, text, count=1)
    return text.rstrip() + f"\n\n- **{name}:** {value}\n"


# --------------------------------------------------------------------------------------
# Which system is this campaign on
# --------------------------------------------------------------------------------------


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def campaign_dir(slug: str) -> Path:
    return repo_root() / "campaigns" / slug


def world_dir(slug: str) -> Path:
    return repo_root() / "worlds" / slug


def for_campaign(slug: str | None) -> str:
    """The ruleset a campaign runs on: `state.json` first, then `CAMPAIGN.md`, then the default.

    `state.json` wins because it is canonical for everything else too. A campaign whose two
    files disagree is a validator error, not something to resolve quietly here.
    """
    if not slug:
        return DEFAULT_SYSTEM
    state = campaign_dir(slug) / "state.json"
    if state.exists():
        try:
            data = json.loads(state.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {}
        if data.get("system"):
            return canonical(data["system"])
    return declared_in_campaign_md(slug) or DEFAULT_SYSTEM


def declared_in_campaign_md(slug: str) -> str | None:
    """The `System:` field of `CAMPAIGN.md`, or None if the file or field is absent."""
    path = campaign_dir(slug) / "CAMPAIGN.md"
    if not path.exists():
        return None
    raw = read_field(path.read_text(encoding="utf-8"), "System")
    if not raw or _norm(raw) in ("none", "unset", "", "tbd"):
        return None
    try:
        return canonical(raw)
    except RulesError:
        return None


def declared_in_state(slug: str) -> str | None:
    path = campaign_dir(slug) / "state.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    raw = data.get("system")
    if not raw:
        return None
    try:
        return canonical(raw)
    except RulesError:
        return None


def world_of_campaign(slug: str) -> str | None:
    """The world slug a campaign is set in, or None for a standalone campaign.

    `CAMPAIGN.md` may write the field as `varisia` or as `worlds/varisia`; both are read
    the same way, because requiring one spelling would make the field a trap.
    """
    p = campaign_dir(slug) / "CAMPAIGN.md"
    if not p.exists():
        return None
    value = read_field(p.read_text(encoding="utf-8"), "World")
    if value is None:
        return None
    value = value.strip().strip("`").rstrip("/")
    if value.lower() in ("none", "—", "-", ""):
        return None
    return value.split("/")[-1]


def for_world(slug: str) -> list[str]:
    """Every ruleset that has a campaign in this world, in registry order.

    A world is system-neutral; this reads the campaigns, not the world folder. An empty
    list means no campaign is linked to it yet.
    """
    found: set[str] = set()
    campaigns = repo_root() / "campaigns"
    want = str(slug).strip().rstrip("/").split("/")[-1].lower()
    if campaigns.exists():
        for d in sorted(campaigns.iterdir()):
            if not d.is_dir() or not (d / "CAMPAIGN.md").exists():
                continue
            if (world_of_campaign(d.name) or "").lower() == want:
                found.add(for_campaign(d.name))
    return [s for s in SYSTEMS if s in found]


# --------------------------------------------------------------------------------------
# Calendar and time — a property of the world, not of the ruleset
# --------------------------------------------------------------------------------------

#: name -> {"months": [(name, days), ...], "weekdays": [...], "era": str, "source": str}
CALENDARS: dict[str, dict[str, Any]] = {}


def register_calendar(name: str, months: Sequence[tuple[str, int]], weekdays: Sequence[str],
                      era: str = "", source: str = "") -> None:
    """Add a calendar to the engine. Rulesets call this at import; worlds call it via `load_world_calendar`."""
    if not months:
        raise RulesError(f"calendar {name!r} needs at least one month")
    for mname, days in months:
        if int(days) < 1:
            raise RulesError(f"calendar {name!r}: month {mname!r} cannot have {days} days")
    CALENDARS[str(name).lower()] = {
        "months": [(str(m), int(d)) for m, d in months],
        "weekdays": [str(w) for w in weekdays] or ["Day 1"],
        "era": era,
        "source": source,
    }


GENERIC_MONTHS: list[tuple[str, int]] = [(f"Month {i}", 30) for i in range(1, 13)]
GENERIC_WEEKDAYS = [f"Day {i}" for i in range(1, 8)]
register_calendar(
    "generic", GENERIC_MONTHS, GENERIC_WEEKDAYS, era="",
    source="This framework's own placeholder: twelve 30-day months, a seven-day week, no era. "
           "Not a published calendar. A campaign in a named setting should either use that "
           "setting's calendar or define one in its world's CALENDAR.md.",
)

_YEAR_DAYS_CACHE: dict[str, int] = {}


def _calendars_for(name: str) -> dict[str, Any]:
    """Resolve a calendar name, importing the rulesets once if it is not registered yet."""
    key = str(name or "generic").lower()
    if key in CALENDARS:
        return CALENDARS[key]
    load_all()  # a ruleset registers its calendars at import time
    if key in CALENDARS:
        return CALENDARS[key]
    raise RulesError(
        f"no calendar named {name!r} is registered "
        f"(have: {', '.join(sorted(CALENDARS))}); define it in the world's CALENDAR.md"
    )


# A machine-readable calendar block in a world's CALENDAR.md, so one shared world keeps one
# calendar across both rulesets. Everything outside the fence stays prose for the GM.
_CAL_BLOCK = re.compile(
    r"<!--\s*CALENDAR-BEGIN\s*-->\s*```json\s*(?P<body>.*?)```\s*<!--\s*CALENDAR-END\s*-->",
    re.DOTALL | re.IGNORECASE,
)


def load_world_calendar(world: str) -> str | None:
    """Register the calendar a world defines in its CALENDAR.md. Returns its name, or None."""
    path = world_dir(world) / "CALENDAR.md"
    if not path.exists():
        return None
    m = _CAL_BLOCK.search(path.read_text(encoding="utf-8"))
    if not m:
        return None
    try:
        spec = json.loads(m.group("body"))
    except json.JSONDecodeError as exc:
        raise RulesError(f"{path}: the CALENDAR block is not valid JSON ({exc})") from exc
    name = str(spec.get("name") or f"world:{world}").lower()
    register_calendar(
        name,
        [(str(mn["name"]), int(mn["days"])) for mn in spec.get("months", [])] or GENERIC_MONTHS,
        spec.get("weekdays") or GENERIC_WEEKDAYS,
        era=str(spec.get("era", "")),
        source=f"defined by this world in worlds/{world}/CALENDAR.md",
    )
    return name


def blank_time(calendar: str = "generic", year: int = 1, month: int = 1, day: int = 1,
               minute: int = 8 * 60) -> dict[str, Any]:
    return {
        "calendar": str(calendar).lower(),
        "year": year,
        "month": month,
        "day": day,
        "minute_of_day": minute,
        "elapsed_minutes": 0,
    }


def format_time(t: dict[str, Any] | None) -> str:
    if not t:
        return "unset"
    cal = _calendars_for(t.get("calendar", "generic"))
    months = cal["months"]
    mi = max(1, min(len(months), int(t.get("month", 1))))
    name = months[mi - 1][0]
    minute = int(t.get("minute_of_day", 0)) % (24 * 60)
    hh, mm = divmod(minute, 60)
    era = f" {cal['era']}" if cal.get("era") else ""
    return f"{int(t.get('day', 1))} {name} {int(t.get('year', 0))}{era}, {hh:02d}:{mm:02d}"


def advance_time(t: dict[str, Any], minutes: int) -> dict[str, Any]:
    """Move the in-world clock forward. Time only ever moves forward during play."""
    if minutes < 0:
        raise ValueError("in-world time does not run backwards; restore a checkpoint instead")
    t = dict(t or blank_time())
    cal = _calendars_for(t.get("calendar", "generic"))
    months = cal["months"]
    total = int(t.get("minute_of_day", 0)) + minutes
    days, minute = divmod(total, 24 * 60)
    t["minute_of_day"] = minute
    day = int(t.get("day", 1)) + days
    month = int(t.get("month", 1))
    year = int(t.get("year", 0))
    while True:
        length = months[(month - 1) % len(months)][1]
        if day <= length:
            break
        day -= length
        month += 1
        if month > len(months):
            month = 1
            year += 1
    t.update({"day": day, "month": month, "year": year})
    t["elapsed_minutes"] = int(t.get("elapsed_minutes", 0)) + minutes
    return t


_INTERVAL_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*(rounds?|minutes?|mins?|hours?|hrs?|days?|weeks?|months?)", re.IGNORECASE
)
# A round is 6 seconds in both rulesets: PF2e Player Core 'Rounds' and D&D 2024
# 'Combat' ("Each round represents 6 seconds in the game world").
_UNIT_MINUTES = {
    "round": 1 / 6,
    "minute": 1,
    "min": 1,
    "hour": 60,
    "hr": 60,
    "day": 60 * 24,
    "week": 60 * 24 * 7,
    "month": 60 * 24 * 30,
}


def parse_interval(text: str) -> tuple[int, str]:
    """'4 hours' -> (240, '4 hours'). Rounds are 6 seconds, so 10 rounds is a minute."""
    hits = _INTERVAL_RE.findall(str(text))
    if not hits:
        raise ValueError(f"cannot read a span of time out of {text!r} (try '4 hours', '10 minutes', '1 day')")
    minutes = 0.0
    for value, unit in hits:
        u = unit.lower().rstrip("s")
        minutes += float(value) * _UNIT_MINUTES[u]
    return int(round(minutes)), str(text).strip()


def tick_wall_clock_conditions(data: dict[str, Any], minutes: int) -> list[str]:
    """Expire minute-, hour- and day-length condition durations when time passes."""
    notes: list[str] = []
    for _, pc in (data.get("pcs") or {}).items():
        keep = []
        for c in pc.get("conditions", []):
            dur = c.get("duration") or {}
            kind = dur.get("kind")
            per = {"minutes": 1, "hours": 60, "days": 60 * 24}.get(kind or "")
            if not per or dur.get("remaining") is None:
                keep.append(c)
                continue
            left = int(dur["remaining"]) - minutes / per
            if left <= 0:
                notes.append(f"{pc.get('name')}: {c['name']} expired as time passed")
                continue
            dur["remaining"] = int(left) if float(left).is_integer() else round(left, 2)
            keep.append(c)
        pc["conditions"] = keep
    return notes


# --------------------------------------------------------------------------------------
# Cross-system translation: scope, not statistics
# --------------------------------------------------------------------------------------

#: The shared scale a cross-system world is written on. Four bands, named for the size of
#: the thing a character at that band can plausibly threaten or protect.
SCOPE_BANDS: list[tuple[str, str]] = [
    ("local", "a farmstead, a village, a city ward — people who know each other by name"),
    ("regional", "a city and the land that feeds it; a barony; a stretch of coast"),
    ("national", "a kingdom, a great city-state, a region; the doorstep of another plane"),
    ("worldly", "the world itself, or the order of the planes"),
]
SCOPE_NAMES = [b for b, _ in SCOPE_BANDS]

#: system -> [(low, high, band), ...]. See `SCOPE_SOURCES` for which of these is published.
_SCOPE_LEVELS: dict[str, list[tuple[int, int, str]]] = {
    "dnd5e": [(1, 4, "local"), (5, 10, "regional"), (11, 16, "national"), (17, 20, "worldly")],
    "pf2e": [(1, 4, "local"), (5, 10, "regional"), (11, 16, "national"), (17, 20, "worldly")],
}

SCOPE_SOURCES: dict[str, str] = {
    "dnd5e": (
        "PUBLISHED. SRD 5.2, 'Character Creation' -> 'Tiers of Play': tier 1 is levels 1-4 "
        "(\"threats ... usually pose a danger to local farmsteads or villages\"), tier 2 is 5-10 "
        "(\"dangers that threaten cities and kingdoms\"), tier 3 is 11-16 (\"threats to whole "
        "regions\"), tier 4 is 17-20 (\"the fate of the world or even the order of the "
        "multiverse\"). The SRD is explicit that \"these tiers don't have any rules associated "
        "with them\" — they describe scope, which is exactly what this mapping uses them for."
    ),
    "pf2e": (
        "THIS FRAMEWORK'S OWN CONVENTION. Pathfinder 2e publishes no tier table; it has levels "
        "1-20 and no banding of them. The four bands above are this framework's reading of the "
        "same 1-4 / 5-10 / 11-16 / 17-20 split, chosen so that one shared world can describe a "
        "character's reach without naming a ruleset. It is not a published rule and it is not a "
        "claim that a PF2e level 7 and a D&D level 7 character are equivalent in play."
    ),
}


def scope_band(system: str | None, level: int) -> str:
    """The scope band a character of this level sits in, for world-level writing."""
    sid = canonical(system)
    lvl = int(level)
    for low, high, band in _SCOPE_LEVELS[sid]:
        if low <= lvl <= high:
            return band
    if lvl < 1:
        return "local"
    return "worldly"


def scope_describe(band: str) -> str:
    key = str(band).strip().lower()
    for name, blurb in SCOPE_BANDS:
        if name == key:
            return blurb
    raise RulesError(f"{band!r} is not a scope band ({', '.join(SCOPE_NAMES)})")


def levels_in_band(system: str | None, band: str) -> tuple[int, int]:
    sid = canonical(system)
    key = str(band).strip().lower()
    for low, high, name in _SCOPE_LEVELS[sid]:
        if name == key:
            return low, high
    raise RulesError(f"{band!r} is not a scope band ({', '.join(SCOPE_NAMES)})")


def translate_level(level: int, *, source: str, target: str) -> dict[str, Any]:
    """What a character of `level` in `source` means to a campaign running `target`.

    Returns the shared scope band and the level range that band covers in the target
    ruleset — **never a single converted level**, because there is no such number. The
    `refuses` field says what this deliberately will not do.
    """
    src = canonical(source)
    tgt = canonical(target)
    band = scope_band(src, level)
    low, high = levels_in_band(tgt, band)
    return {
        "source_system": src,
        "source_level": int(level),
        "band": band,
        "band_means": scope_describe(band),
        "target_system": tgt,
        "target_levels": [low, high],
        "same_system": src == tgt,
        "refuses": [
            "converting a stat block: a CR 5 monster and a level 5 PF2e creature are not the "
            "same creature, and neither set of numbers survives being carried across",
            "converting a character sheet: rebuild the character in the target ruleset from "
            "their story, and let the numbers land where that ruleset puts them",
            "converting treasure piece for piece: the two economies are not the same shape",
        ],
        "source_note": SCOPE_SOURCES[src],
    }


# --------------------------------------------------------------------------------------
# Provenance across both rulesets
# --------------------------------------------------------------------------------------


def all_sources() -> dict[str, dict[str, str]]:
    """Every table in every ruleset, keyed by system then table name."""
    out: dict[str, dict[str, str]] = {}
    for sid, mod in load_all().items():
        out[sid] = dict(getattr(mod, "SOURCES", {}))
    return out


def all_unverified() -> dict[str, list[str]]:
    return {sid: list(getattr(mod, "UNVERIFIED_TABLES", [])) for sid, mod in load_all().items()}


# --------------------------------------------------------------------------------------
# A self-check, so a ruleset that half-implements the contract says so
# --------------------------------------------------------------------------------------

#: What every ruleset module must provide for the shared tools to run it.
REQUIRED: tuple[str, ...] = (
    "SYSTEM_ID", "SYSTEM_NAME", "SYSTEM_SHORT",
    "SOURCES", "UNVERIFIED_TABLES",
    "USES_DEGREES", "CRIT_RULE",
    "DEFAULT_CALENDAR",
    "VALUED_CONDITIONS", "UNVALUED_CONDITIONS", "TRACKED_SEPARATELY",
    "resolve", "encounter_budgets", "rate_encounter", "treasure_for",
    "xp_to_level", "blank_character_fields", "on_zero_hp", "carry_report",
    "daily_reset", "sheet_lines", "status_lines",
)


def check_interface(system: str | None = None) -> list[str]:
    """Names a ruleset is missing. Empty list means it satisfies the contract."""
    mod = load(system)
    return [a for a in REQUIRED if not hasattr(mod, a)]


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    p = argparse.ArgumentParser(
        prog="rules.py", description="The rulesets this framework runs, and what crosses between them."
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="the rulesets, their names and their licences")
    c = sub.add_parser("check", help="verify every ruleset satisfies the shared contract")
    c.add_argument("--system")
    w = sub.add_parser("which", help="which ruleset a campaign runs on")
    w.add_argument("campaign")
    t = sub.add_parser("translate", help="what a level in one ruleset means in the other")
    t.add_argument("--level", type=int, required=True)
    t.add_argument("--from", dest="source", required=True)
    t.add_argument("--to", dest="target", required=True)
    t.add_argument("--json", action="store_true")
    b = sub.add_parser("bands", help="the shared scope bands and how each ruleset maps onto them")
    b.add_argument("--system")
    sub.add_parser("calendars", help="every registered calendar")

    args = p.parse_args(argv)

    if args.cmd == "list":
        for sid, m in SYSTEMS.items():
            print(f"{sid:8} {m['short']:10} {m['name']}")
            print(f"{'':8} licence: {m['licence']}   aliases: {', '.join(m['aliases'])}")
        print(f"\nA campaign that declares no system is read as {DEFAULT_SYSTEM}.")
        return 0

    if args.cmd == "check":
        targets = [args.system] if args.system else list(SYSTEMS)
        bad = 0
        for sid in targets:
            missing = check_interface(sid)
            if missing:
                bad += 1
                print(f"FAIL {canonical(sid)}: missing {', '.join(missing)}")
            else:
                print(f"ok   {canonical(sid)}: implements all {len(REQUIRED)} required names")
        return 1 if bad else 0

    if args.cmd == "which":
        sid = for_campaign(args.campaign)
        state = declared_in_state(args.campaign)
        md = declared_in_campaign_md(args.campaign)
        print(f"{args.campaign}: {short_of(sid)} ({sid})")
        print(f"  state.json:  {state or '(not set)'}")
        print(f"  CAMPAIGN.md: {md or '(not set)'}")
        if state and md and state != md:
            print("  MISMATCH — state.json wins; run validate.py")
            return 1
        return 0

    if args.cmd == "translate":
        out = translate_level(args.level, source=args.source, target=args.target)
        if args.json:
            print(json.dumps(out, indent=2))
            return 0
        print(f"{short_of(out['source_system'])} level {out['source_level']} "
              f"-> scope band '{out['band']}'")
        print(f"  which is: {out['band_means']}")
        print(f"  in {short_of(out['target_system'])} that band is "
              f"levels {out['target_levels'][0]}-{out['target_levels'][1]}")
        print("\nThis translation covers scope and nothing else. It will not:")
        for r in out["refuses"]:
            print(f"  - {r}")
        print(f"\nSource: {out['source_note']}")
        return 0

    if args.cmd == "bands":
        for name, blurb in SCOPE_BANDS:
            print(f"{name:9} {blurb}")
            for sid in ([args.system] if args.system else list(SYSTEMS)):
                low, high = levels_in_band(sid, name)
                print(f"{'':9}   {short_of(sid):10} levels {low}-{high}")
        print()
        for sid in ([args.system] if args.system else list(SYSTEMS)):
            print(f"{short_of(sid)}: {SCOPE_SOURCES[canonical(sid)]}\n")
        return 0

    if args.cmd == "calendars":
        load_all()
        for name, cal in sorted(CALENDARS.items()):
            days = sum(d for _, d in cal["months"])
            print(f"{name}: {len(cal['months'])} months, {days} days/year, "
                  f"{len(cal['weekdays'])}-day week, era {cal['era'] or '(none)'}")
            if cal.get("source"):
                print(f"    {cal['source']}")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
