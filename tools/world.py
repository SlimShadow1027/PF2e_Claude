#!/usr/bin/env python3
"""world.py — the optional shared-setting layer under `worlds/`.

A world holds setting material and a record of what has already been **concluded**.
Nothing live ever lands here: no hit points, no coins, no inventory, no conditions, no
checkpoints, no roll logs. Writes happen only at promotion points, with confirmation.

Reads are date-gated. A campaign set two centuries before another must not be informed by
events that, from its perspective, have not happened — and the player must not be spoiled
on a world event from a campaign they have not reached. `as-of` is what the boot sequence
loads. See system/21-shared-worlds.md.

Standard library only.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

from roll import atomic_write, campaign_dir, repo_root, utc_now, world_dir  # noqa: E402
import pf2e  # noqa: E402

VISIBILITIES = ("public", "rumor", "secret")
AVAILABILITY = ("playable", "npc-free", "npc-with-permission", "off-limits")

# Field names that would mean live state had leaked into the world layer. validate.py
# refuses any of these under worlds/.
LIVE_STATE_MARKERS = (
    "current hp",
    "current_hp",
    "hp:",
    "temp hp",
    "hero points",
    "hero_points",
    "focus points",
    "focus_points",
    "spell slots used",
    "slots used",
    "conditions:",
    "dying",
    "wounded ",
    "gold:",
    "coins:",
    "inventory:",
    "bulk:",
    "position:",
    "initiative:",
    "checkpoint:",
)


class WorldError(Exception):
    pass


# --------------------------------------------------------------------------------------
# Dates
# --------------------------------------------------------------------------------------

_MONTH_LOOKUP = {name.lower(): i + 1 for i, (name, _) in enumerate(pf2e.GOLARION_MONTHS)}
_MONTH_LOOKUP.update({name.lower(): i + 1 for i, (name, _) in enumerate(pf2e.GENERIC_MONTHS)})


@dataclass(frozen=True, order=True)
class WorldDate:
    year: int
    month: int
    day: int
    era: str = ""
    raw: str = ""

    def key(self) -> tuple[int, int, int]:
        return (self.year, self.month, self.day)

    def __str__(self) -> str:
        return self.raw or f"{self.day} {pf2e.GOLARION_MONTHS[self.month - 1][0]} {self.year} {self.era}".strip()


def parse_date(text: str) -> WorldDate:
    """Read '4712 AR', '12 Desnus 4712 AR', 'Desnus 4712', or a bare year.

    An entry with no day or month sorts at the start of its month or year, so a whole-year
    entry never accidentally sorts after a dated one inside the same year.
    """
    raw = str(text).strip()
    if not raw:
        raise WorldError("an empty date cannot be ordered")
    era = ""
    m = re.search(r"\b(AR|IC|AG|AD|CE|BCE|BC)\b", raw, re.IGNORECASE)
    if m:
        era = m.group(1).upper()
    body = re.sub(r"\b(AR|IC|AG|AD|CE|BCE|BC)\b", "", raw, flags=re.IGNORECASE).strip().strip(",")
    day = 1
    month = 1
    dm = re.match(r"^(\d{1,2})\s+([A-Za-z]+)\s+(-?\d+)$", body)
    if dm:
        day, mname, year = int(dm.group(1)), dm.group(2).lower(), int(dm.group(3))
        if mname not in _MONTH_LOOKUP:
            raise WorldError(f"{dm.group(2)!r} is not a month name in this calendar")
        month = _MONTH_LOOKUP[mname]
        return WorldDate(year, month, day, era, raw)
    mm = re.match(r"^([A-Za-z]+)\s+(-?\d+)$", body)
    if mm:
        mname, year = mm.group(1).lower(), int(mm.group(2))
        if mname not in _MONTH_LOOKUP:
            raise WorldError(f"{mm.group(1)!r} is not a month name in this calendar")
        return WorldDate(year, _MONTH_LOOKUP[mname], 1, era, raw)
    ym = re.match(r"^(-?\d+)$", body)
    if ym:
        return WorldDate(int(ym.group(1)), 1, 1, era, raw)
    iso = re.match(r"^(-?\d+)-(\d{1,2})-(\d{1,2})$", body)
    if iso:
        return WorldDate(int(iso.group(1)), int(iso.group(2)), int(iso.group(3)), era, raw)
    raise WorldError(
        f"cannot order the date {text!r}. Write it as '4712 AR', 'Desnus 4712 AR' or '12 Desnus 4712 AR'."
    )


# --------------------------------------------------------------------------------------
# The chronicle
# --------------------------------------------------------------------------------------

CHRONICLE_HEADER = """# Chronicle

The overarching record of this world, ordered by in-world date. **Append-only.** Never
edit or delete an entry; add a correcting entry instead.

Each entry carries a date, the campaign that produced it, the characters involved, what
happened, what it changed, and whether it is public knowledge, rumor, or secret. A later
campaign can only have heard the `public` and `rumor` entries — `secret` ones are the
world's GM-side truth and `tools/world.py as-of` withholds them unless you pass `--gm`.

Written only by `tools/world.py promote`, at a promotion point, with confirmation.
Nothing live is ever promoted: no hit points, coins, inventory, conditions or positions.

<!-- CHRONICLE-ENTRIES-BELOW -->
"""


@dataclass
class Entry:
    title: str
    date: WorldDate
    campaign: str
    characters: str
    visibility: str
    happened: str
    changed: str
    raw: str = ""

    def render(self) -> str:
        return "\n".join(
            [
                f"## {self.title}",
                "",
                f"- **Date:** {self.date}",
                f"- **Campaign:** {self.campaign}",
                f"- **Characters:** {self.characters or '—'}",
                f"- **Visibility:** {self.visibility}",
                f"- **What happened:** {self.happened}",
                f"- **What it changed:** {self.changed}",
                "",
            ]
        )


_FIELD_RE = re.compile(r"^\s*[-*]\s*\*\*(.+?):\*\*\s*(.*)$")


def parse_chronicle(text: str) -> list[Entry]:
    entries: list[Entry] = []
    blocks = re.split(r"^##\s+", text, flags=re.MULTILINE)[1:]
    for block in blocks:
        lines = block.splitlines()
        title = lines[0].strip()
        fields: dict[str, str] = {}
        for line in lines[1:]:
            m = _FIELD_RE.match(line)
            if m:
                fields[m.group(1).strip().lower()] = m.group(2).strip()
        if "date" not in fields:
            raise WorldError(f"chronicle entry {title!r} has no **Date:** field")
        vis = (fields.get("visibility") or "").lower()
        entries.append(
            Entry(
                title=title,
                date=parse_date(fields["date"]),
                campaign=fields.get("campaign", ""),
                characters=fields.get("characters", ""),
                visibility=vis,
                happened=fields.get("what happened", ""),
                changed=fields.get("what it changed", ""),
                raw="## " + block.rstrip() + "\n",
            )
        )
    return entries


def read_chronicle(world: str) -> tuple[Path, list[Entry]]:
    path = world_dir(world) / "CHRONICLE.md"
    if not path.exists():
        raise WorldError(f"{path} does not exist — run `world.py init` first")
    return path, parse_chronicle(path.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------------------
# init
# --------------------------------------------------------------------------------------

def _slug(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", str(name).lower()).strip("-")
    return s or "world"


WORLD_FILES: dict[str, str] = {
    "README.md": """# {title}

A shared setting. Several campaigns can be set here, in different eras.

## Campaigns set in this world

| Campaign | Era / start date | Status |
|---|---|---|
| _(none yet — `tools/world.py link` adds a row)_ | | |

## What this world is

_Two or three paragraphs: the shape of the place, what makes it itself, and the one thing
a newcomer needs to know._

## What lives where

- `CHRONICLE.md` — dated record of concluded events, append-only, one line of visibility each.
- `LEGENDS.md` — how those events are *remembered* in-world, distortions included.
- `GAZETTEER.md` — places, regions, settlements and their item levels.
- `FACTIONS.md` — long-lived organisations, their standing and leadership.
- `PANTHEON.md` — gods and cosmology.
- `CALENDAR.md` — calendar, eras, and the current present day.
- `canon.md` — world-level established facts, append-only.
- `characters/` — one legacy record per character who has played here.
- `npcs/` — NPCs who persist beyond one campaign.
- `gm-private/threads.md` — unresolved world-level threads a future campaign could pick up.

## The rules that keep this layer clean

- **Nothing live is ever written here.** No hit points, coins, inventory, conditions,
  positions, checkpoints or roll logs. Those stay in `campaigns/<slug>/` permanently.
- **Writes happen only at promotion points** — an arc concludes, a campaign concludes, or
  the player says an event is world-significant — through `tools/world.py promote`.
- **Campaign canon wins locally.** Where a campaign contradicts world canon, the campaign
  records a local divergence; the world keeps the version other campaigns inherit.
- **Reads are date-gated.** A campaign reads world material dated at or before its own
  current in-world date and nothing later.
""",
    "CHRONICLE.md": CHRONICLE_HEADER,
    "LEGENDS.md": """# Legends

How the events in `CHRONICLE.md` are *told* in this world: exaggerated, misattributed,
politically edited, or plain wrong. When an NPC refers to a past event, they speak from
here, not from the chronicle.

Keep the two separate on purpose. A player hearing their old character's story told wrong
— and knowing it is wrong — is most of what a shared world is for.

Entries may carry a `- **Date:**` line, in which case `as-of` gates them like chronicle
entries. A legend with no date is treated as always current.

<!-- LEGEND-ENTRIES-BELOW -->
""",
    "GAZETTEER.md": """# Gazetteer

Places, regions and settlements. Each settlement carries the item level available there,
because that is the number play actually needs.

| Place | Type | Region | Item level | One line |
|---|---|---|---|---|
| | | | | |

Settlement item levels are a campaign-agnostic default in `tools/pf2e.py`
(`ITEM_LEVEL_BY_SETTLEMENT`, marked UNVERIFIED) — set them explicitly here per world.
""",
    "FACTIONS.md": """# Factions

Long-lived organisations. A faction here outlives any one campaign.

## _Faction name_

- **Standing:** rising / stable / fracturing / broken
- **Leadership:** who, and how secure
- **Wants:** in one sentence
- **Method:** how they usually get it
- **Known-to-players:** yes / partly / no
- **Relationships:** `ally-of:`, `rival-of:`, `serves:`, `fears:` — one per line, naming
  another faction or an NPC, with a one-phrase reason. `tools/graph.py` reads these.
""",
    "PANTHEON.md": """# Pantheon and cosmology

For an original setting, the gods and the shape of the afterlife. For Golarion, a pointer
is enough: _"Golarion as published; see Player Core and Divine Mysteries."_
""",
    "CALENDAR.md": """# Calendar

- **Calendar in use:** golarion (Absalom Reckoning) / generic / custom
- **Present day of this world:** _(the latest date any campaign has reached)_
- **Eras:** _(named spans, if the world has them)_

The Golarion calendar maps month for month onto the Gregorian one and keeps its month
lengths — Abadius 31, Calistril 28, Pharast 31, Gozran 30, Desnus 31, Sarenith 30,
Erastus 31, Arodus 31, Rova 30, Lamashan 31, Neth 30, Kuthona 31 — with weekdays Moonday,
Toilday, Wealday, Oathday, Fireday, Starday, Sunday. Leap years are not modelled.

Source: see `python3 tools/pf2e.py sources` (`calendar`).
""",
    "canon.md": """# World canon

Append-only. World-level facts that no campaign may contradict. A campaign that needs to
contradict one records a **local divergence** in its own `CANON.md` instead; the world
keeps the version other campaigns inherit.

| Added | Fact | Source (campaign / promotion) |
|---|---|---|
| | | |
""",
    "characters/.gitkeep": "",
    "npcs/.gitkeep": "",
    "gm-private/threads.md": """# Unresolved world threads

> **GM-ONLY.** The player has agreed not to read this file.

Loose ends a future campaign could pick up. One heading each: what is unresolved, who
cares, and what would make it urgent again.
""",
    "gm-private/README.md": """# World GM-private

> **GM-ONLY.** The player has agreed not to read this folder.

`secret`-visibility chronicle entries and world-level threads live here. `world.py as-of`
withholds them from a normal read; `--gm` includes them.
""",
}


def cmd_init(args: argparse.Namespace) -> int:
    slug = args.slug or _slug(args.title)
    root = world_dir(slug)
    if root.exists() and not args.force:
        raise WorldError(f"{root} already exists (pass --force to fill in missing files only)")
    made = []
    for rel, body in WORLD_FILES.items():
        p = root / rel
        if p.exists():
            continue
        atomic_write(p, body.replace("{title}", args.title))
        made.append(str(p.relative_to(repo_root())))
    print(f"world '{args.title}' → worlds/{slug}/")
    for m in made:
        print(f"  + {m}")
    print("\nNothing live is ever written here. Attach a campaign with:")
    print(f"  python3 tools/world.py link --campaign <slug> --world {slug} --start-date '4712 AR'")
    return 0


# --------------------------------------------------------------------------------------
# link
# --------------------------------------------------------------------------------------


def _set_field(text: str, field: str, value: str) -> str:
    return pf2e.set_field(text, field, value)


def cmd_link(args: argparse.Namespace) -> int:
    cdir = campaign_dir(args.campaign)
    if not cdir.is_dir():
        raise WorldError(f"no campaign folder at {cdir}")
    wdir = world_dir(args.world)
    if not wdir.is_dir():
        raise WorldError(f"no world at {wdir} — run `world.py init` first")
    parse_date(args.start_date)  # fail early on an unorderable date

    cpath = cdir / "CAMPAIGN.md"
    if not cpath.exists():
        raise WorldError(f"{cpath} does not exist")
    text = cpath.read_text(encoding="utf-8")
    text = _set_field(text, "World", f"worlds/{args.world}")
    text = _set_field(text, "Era", args.era or args.start_date)
    text = _set_field(text, "Start date", args.start_date)
    atomic_write(cpath, text)

    rpath = wdir / "README.md"
    rtext = rpath.read_text(encoding="utf-8")
    row = f"| {args.campaign} | {args.era or args.start_date} | active |"
    placeholder = "| _(none yet — `tools/world.py link` adds a row)_ | | |"
    if placeholder in rtext:
        rtext = rtext.replace(placeholder, row)
    elif row not in rtext:
        rtext = re.sub(r"(\n\| ---.*\n(?:\|.*\n)*)", lambda m: m.group(1) + row + "\n", rtext, count=1)
        if row not in rtext:
            rtext = rtext.replace("## What this world is", row + "\n\n## What this world is", 1)
    atomic_write(rpath, rtext)

    print(f"{args.campaign} → worlds/{args.world}, starting {args.start_date}")
    print(f"  wrote World:, Era: and Start date: into {cpath.relative_to(repo_root())}")
    print(f"  added a row to {rpath.relative_to(repo_root())}")
    print("\nThe date gate is now live: when running this campaign, read world material dated at or")
    print(f"before its current in-world date and nothing later. `world.py as-of {args.world} <date>`.")
    return 0


# --------------------------------------------------------------------------------------
# as-of
# --------------------------------------------------------------------------------------


def cmd_as_of(args: argparse.Namespace) -> int:
    cutoff = parse_date(args.date)
    path, entries = read_chronicle(args.world)
    entries.sort(key=lambda e: e.date.key())
    visible, later, withheld = [], [], []
    for e in entries:
        if e.date.key() > cutoff.key():
            later.append(e)
        elif e.visibility == "secret" and not args.gm:
            withheld.append(e)
        else:
            visible.append(e)

    print(f"# {args.world} — world view as of {cutoff}")
    print()
    if args.gm:
        print("> **GM view.** Includes `secret` entries. Never paste this into play.")
        print()
    print(f"Chronicle: {len(visible)} entry/entries at or before this date"
          f"; {len(later)} dated later are withheld by the date gate"
          + (f"; {len(withheld)} secret entry/entries withheld" if withheld else "")
          + ".")
    print()
    if visible:
        for e in visible:
            print(e.raw)
    else:
        print("_(nothing has happened in this world at or before this date.)_")
        print()
    if later:
        print("---")
        print()
        print("**Withheld by the date gate** (do not read, do not let them inform this campaign):")
        for e in later:
            print(f"- {e.date} — {e.title} ({e.campaign})")
        print()
    if withheld and not args.gm:
        print(f"**Withheld as secret:** {len(withheld)} entry/entries. They are in the world's gm-private view.")
        print()

    lpath = world_dir(args.world) / "LEGENDS.md"
    if lpath.exists():
        ltext = lpath.read_text(encoding="utf-8")
        try:
            legends = parse_chronicle(ltext)
        except WorldError:
            legends = []
        if legends:
            ok = [l for l in legends if l.date.key() <= cutoff.key()]
            print("## Legends current at this date")
            print()
            print("NPCs speak from these, not from the chronicle.")
            print()
            for l in ok:
                print(f"- **{l.title}** ({l.date}) — {l.happened}")
            if len(ok) < len(legends):
                print(f"\n_{len(legends) - len(ok)} later legend(s) withheld._")
            print()

    print("## Undated setting material (read in full)")
    print()
    for name in ("GAZETTEER.md", "FACTIONS.md", "PANTHEON.md", "CALENDAR.md", "canon.md"):
        p = world_dir(args.world) / name
        print(f"- `worlds/{args.world}/{name}`" + ("" if p.exists() else "  _(absent)_"))
    print()
    print("Nothing under `worlds/` holds live state. Hit points, coins, inventory and conditions")
    print("live only in `campaigns/<slug>/state.json`.")
    return 0


# --------------------------------------------------------------------------------------
# promote
# --------------------------------------------------------------------------------------


def cmd_promote(args: argparse.Namespace) -> int:
    cdir = campaign_dir(args.campaign)
    if not cdir.is_dir():
        raise WorldError(f"no campaign folder at {cdir}")
    world = args.world or _world_of(args.campaign)
    if not world:
        raise WorldError(
            f"{args.campaign}/CAMPAIGN.md has no `World:` field pointing at a worlds/ folder. "
            "A standalone campaign has nothing to promote to."
        )
    if args.visibility not in VISIBILITIES:
        raise WorldError(f"visibility must be one of {', '.join(VISIBILITIES)}")
    date = parse_date(args.date)
    path, entries = read_chronicle(world)

    collisions = [
        e for e in entries
        if e.date.key() == date.key() and e.campaign != args.campaign
    ]
    entry = Entry(
        title=args.title,
        date=date,
        campaign=args.campaign,
        characters=args.characters or "",
        visibility=args.visibility,
        happened=args.happened,
        changed=args.changed,
    )

    print("About to append this to the world chronicle — it is append-only and permanent:")
    print()
    print(f"  world:      worlds/{world}/CHRONICLE.md")
    print(entry.render().replace("\n", "\n  "))
    if collisions:
        print("  ⚠ COLLISION: another campaign already claims this date:")
        for c in collisions:
            print(f"      {c.date} — {c.title} ({c.campaign})")
        print("      The chronicle records both; the reader resolves order by date. Say so in the entry")
        print("      if they describe the same event differently.")
    for marker in LIVE_STATE_MARKERS:
        blob = f"{args.happened} {args.changed} {args.title}".lower()
        if marker in blob:
            raise WorldError(
                f"refusing to promote: the text contains {marker!r}, which looks like live state. "
                "The world gets concluded facts — what happened, when, who did it, what it changed."
            )
    if not args.yes:
        try:
            answer = input("\nAppend it? [y/N] ").strip().lower()
        except EOFError:
            answer = ""
        if answer not in ("y", "yes"):
            print("Nothing written.")
            return 1

    text = path.read_text(encoding="utf-8")
    atomic_write(path, text.rstrip() + "\n\n" + entry.render())
    print(f"\nappended to worlds/{world}/CHRONICLE.md")
    if args.legend:
        lpath = world_dir(world) / "LEGENDS.md"
        legend = Entry(
            title=f"How it is told: {args.title}",
            date=date,
            campaign=args.campaign,
            characters=args.characters or "",
            visibility="public",
            happened=args.legend,
            changed="_(what the telling gets wrong, and who benefits from the version told)_",
        )
        atomic_write(lpath, lpath.read_text(encoding="utf-8").rstrip() + "\n\n" + legend.render())
        print(f"appended the telling to worlds/{world}/LEGENDS.md")
    print("\nNo live state was promoted. Current HP, coins, inventory, conditions, checkpoints and")
    print("roll logs stay in the campaign folder permanently.")
    return 0


def _world_of(campaign: str) -> str | None:
    p = campaign_dir(campaign) / "CAMPAIGN.md"
    if not p.exists():
        return None
    value = pf2e.read_field(p.read_text(encoding="utf-8"), "World")
    if value is None:
        return None
    value = value.strip().strip("`")
    if value.lower() in ("none", "—", "-", ""):
        return None
    return value.split("/")[-1]


# --------------------------------------------------------------------------------------
# legacy
# --------------------------------------------------------------------------------------

LEGACY_TEMPLATE = """# {name}

A legacy record. Written at retirement or campaign end, updated if they return.

- **Campaign:** {campaign}
- **World:** worlds/{world}
- **Ancestry / class:** {ancestry_class}
- **Level reached:** {level}
- **Status:** alive / dead / retired / ascended / missing / unknown even to the GM
- **Whereabouts:** _(where they are now, or why nobody knows)_
- **Availability in other campaigns:** {availability}
  _(playable returning character / npc-free / npc-with-permission / off-limits — the player
  sets this and the GM honours it)_

## What they actually did

_One line per deed, each pointing at the chronicle entry it produced._

- _(deed)_ — see `CHRONICLE.md`: _(entry title)_

## What they are known for

_Not the same list. Reputation is lossy; `LEGENDS.md` is where a deed becomes a distorted
story. Record both and note the gap._

- _(the version people tell)_
- **The gap:** _(what the telling gets wrong, and who benefits)_

## Titles, holdings and ties

- **Titles:**
- **Holdings and organisations founded:**
- **Debts owed:**
- **Debts held:**
- **Surviving relationships:** _(who still cares, and how)_

## Notable items they carried, and where those items are now

| Item | Where it is now |
|---|---|
| | |

---

Nothing on this page is live state. This character's hit points, coins, conditions and
inventory remain in `campaigns/{campaign}/state.json` and are never copied here.
"""


def cmd_legacy(args: argparse.Namespace) -> int:
    world = args.world or _world_of(args.campaign)
    if not world:
        raise WorldError(f"{args.campaign} has no `World:` field, so it has no world to leave a legacy in")
    wdir = world_dir(world)
    if not wdir.is_dir():
        raise WorldError(f"no world at {wdir}")
    name = args.character
    level = args.level
    ancestry_class = args.ancestry_class or "_(ancestry and class)_"
    if level is None:
        try:
            import json

            state = json.loads((campaign_dir(args.campaign) / "state.json").read_text(encoding="utf-8"))
            for key, pc in (state.get("pcs") or {}).items():
                if key == _slug(name) or str(pc.get("name", "")).lower() == name.lower():
                    level = pc.get("level")
                    name = pc.get("name", name)
                    break
        except (OSError, ValueError):
            pass
    path = wdir / "characters" / f"{_slug(name)}.md"
    if path.exists() and not args.force:
        raise WorldError(f"{path} already exists (pass --force to overwrite)")
    atomic_write(
        path,
        LEGACY_TEMPLATE.format(
            name=name,
            campaign=args.campaign,
            world=world,
            level=level if level is not None else "_(level)_",
            ancestry_class=ancestry_class,
            availability=args.availability,
        ),
    )
    print(f"wrote {path.relative_to(repo_root())}")
    print("Fill in the deeds, the reputation, and the gap between them. Set availability deliberately —")
    print("the GM honours it in every other campaign in this world.")
    return 0


# --------------------------------------------------------------------------------------
# timeline
# --------------------------------------------------------------------------------------


def cmd_timeline(args: argparse.Namespace) -> int:
    _, entries = read_chronicle(args.world)
    entries.sort(key=lambda e: e.date.key())
    if not entries:
        print(f"worlds/{args.world}/CHRONICLE.md holds no entries yet.")
        return 0
    campaigns = sorted({e.campaign for e in entries})
    print(f"# {args.world} — all campaigns on one axis\n")
    print(f"{'date':<26} {'campaign':<22} {'vis':<8} event")
    print("-" * 96)
    for e in entries:
        print(f"{str(e.date):<26} {e.campaign:<22} {e.visibility:<8} {e.title}")
    print()
    print(f"{len(entries)} entry/entries across {len(campaigns)} campaign(s): {', '.join(campaigns)}")
    dupes = {}
    for e in entries:
        dupes.setdefault(e.date.key(), []).append(e)
    clashes = {k: v for k, v in dupes.items() if len({x.campaign for x in v}) > 1}
    if clashes:
        print("\n⚠ Two campaigns claim the same date. The chronicle records both; check they are not the")
        print("  same event told differently:")
        for k, v in clashes.items():
            print(f"  {v[0].date}: " + "; ".join(f"{x.title} ({x.campaign})" for x in v))
    return 0


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="world.py", description="The optional shared-setting layer.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init", help="create a world folder")
    p.add_argument("title")
    p.add_argument("--slug", default=None)
    p.add_argument("--force", action="store_true", help="fill in missing files in an existing world")

    p = sub.add_parser("link", help="attach a campaign to a world with a start date")
    p.add_argument("--campaign", required=True)
    p.add_argument("--world", required=True)
    p.add_argument("--start-date", required=True)
    p.add_argument("--era", default=None)

    p = sub.add_parser("as-of", help="the date-gated read the boot sequence loads")
    p.add_argument("world")
    p.add_argument("date")
    p.add_argument("--gm", action="store_true", help="include secret entries — never paste this into play")

    p = sub.add_parser("promote", help="move a concluded event into the chronicle")
    p.add_argument("--campaign", required=True)
    p.add_argument("--world", default=None)
    p.add_argument("--date", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--happened", required=True, help="two or three sentences")
    p.add_argument("--changed", required=True, help="what it changed about the world")
    p.add_argument("--visibility", required=True, choices=list(VISIBILITIES))
    p.add_argument("--characters", default="")
    p.add_argument("--legend", default=None, help="also append how it comes to be told")
    p.add_argument("--yes", action="store_true", help="skip the confirmation prompt")

    p = sub.add_parser("legacy", help="write a per-character legacy record")
    p.add_argument("--campaign", required=True)
    p.add_argument("--character", required=True)
    p.add_argument("--world", default=None)
    p.add_argument("--level", type=int, default=None)
    p.add_argument("--ancestry-class", default=None)
    p.add_argument("--availability", default="npc-with-permission", choices=list(AVAILABILITY))
    p.add_argument("--force", action="store_true")

    p = sub.add_parser("timeline", help="every campaign's events on one axis")
    p.add_argument("world")
    return ap


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    fns = {
        "init": cmd_init,
        "link": cmd_link,
        "as-of": cmd_as_of,
        "promote": cmd_promote,
        "legacy": cmd_legacy,
        "timeline": cmd_timeline,
    }
    try:
        return fns[args.cmd](args)
    except WorldError as exc:
        print(f"world.py: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
