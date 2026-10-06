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
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

from roll import atomic_write, campaign_dir, repo_root, utc_now, world_dir  # noqa: E402
import pf2e  # noqa: E402
import rules  # noqa: E402

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

#: `Position:` is both a live-state word (a combatant's square) and the name of the field a
#: world README uses to say where it sits in the universe. The declaration block is exempt,
#: so the framework's own template does not trip its own validator. Matched on the whole
#: line, so a stray "position: B3" elsewhere in a world file is still caught.
WORLD_DECLARATION_FIELDS = ("universe", "position", "era", "reachable from")


def is_world_declaration_line(line: str) -> bool:
    """True for a line like `- **Position:** a plane` in a world's own README."""
    text = line.strip().lstrip("-*").strip()
    text = text.lstrip("*").strip()
    for field in WORLD_DECLARATION_FIELDS:
        if text.lower().startswith(field):
            after = text[len(field):].lstrip("*").lstrip()
            if after.startswith(":"):
                return True
    return False


class WorldError(Exception):
    pass


# --------------------------------------------------------------------------------------
# Dates
# --------------------------------------------------------------------------------------

# Month names from every registered calendar, because a world is read by every ruleset and
# its dates have to parse the same way for each. A world that defines its own calendar in
# CALENDAR.md registers it here too — see `month_lookup`.
#: The year an undated entry sorts at. LEGENDS.md may hold entries with no date — the
#: file's own header calls those "always current" — so they sort before everything and
#: render without a Date line rather than being rejected.
UNDATED_YEAR = -(10 ** 9)

#: Era abbreviations in common use, so a date reads the same whichever ruleset wrote it.
#: A world that declares its own era in CALENDAR.md adds to this — see `era_names`.
BUILTIN_ERAS = ("AR", "IC", "AG", "AD", "CE", "BCE", "BC")


def _register_world_calendar(world: str | None) -> None:
    if not world:
        return
    try:
        rules.load_world_calendar(world)
    except rules.RulesError:
        pass  # a malformed block is the validator's problem, not the date parser's


def month_lookup(world: str | None = None) -> dict[str, int]:
    """Month name -> month number, across every calendar this world might be written in."""
    _register_world_calendar(world)
    rules.load_all()
    out: dict[str, int] = {}
    for cal in rules.CALENDARS.values():
        for i, (name, _) in enumerate(cal["months"]):
            out.setdefault(name.lower(), i + 1)
    return out


def era_names(world: str | None = None) -> tuple[str, ...]:
    """Every era abbreviation a date in this world might carry.

    A world defining its own calendar declares its own era with it, and that era then has
    to be strippable from a date string or the date will not parse. Longest first, so that
    a two-letter era cannot shadow a three-letter one sharing its prefix.
    """
    _register_world_calendar(world)
    rules.load_all()
    found = {e.upper() for e in BUILTIN_ERAS}
    for cal in rules.CALENDARS.values():
        if cal.get("era"):
            found.add(str(cal["era"]).upper())
    return tuple(sorted(found, key=lambda e: (-len(e), e)))


def _era_re(world: str | None = None) -> re.Pattern[str]:
    return re.compile(r"\b(" + "|".join(re.escape(e) for e in era_names(world)) + r")\b",
                      re.IGNORECASE)


_MONTH_LOOKUP = month_lookup()


@dataclass(frozen=True, order=True)
class WorldDate:
    year: int
    month: int
    day: int
    era: str = ""
    raw: str = ""

    def key(self) -> tuple[int, int, int]:
        return (self.year, self.month, self.day)

    @property
    def undated(self) -> bool:
        return self.year == UNDATED_YEAR

    def __str__(self) -> str:
        if self.raw:
            return self.raw
        # A date built without its raw text falls back to naming the month numerically
        # rather than guessing a calendar's month names; a world may use any calendar.
        return f"{self.day}/{self.month}/{self.year} {self.era}".strip()


def parse_date(text: str, world: str | None = None) -> WorldDate:
    """Read '4712 AR', '12 Desnus 4712 AR', 'Desnus 4712', or a bare year.

    An entry with no day or month sorts at the start of its month or year, so a whole-year
    entry never accidentally sorts after a dated one inside the same year.

    Pass `world` and the world's own calendar is consulted too, so a shared world may use a
    calendar no ruleset ships with and every ruleset will still read its dates.
    """
    lookup = month_lookup(world) if world else _MONTH_LOOKUP
    raw = str(text).strip()
    if not raw:
        raise WorldError("an empty date cannot be ordered")
    era = ""
    era_re = _era_re(world)
    m = era_re.search(raw)
    if m:
        era = m.group(1).upper()
    body = era_re.sub("", raw).strip().strip(",")
    day = 1
    month = 1
    dm = re.match(r"^(\d{1,2})\s+([A-Za-z]+)\s+(-?\d+)$", body)
    if dm:
        day, mname, year = int(dm.group(1)), dm.group(2).lower(), int(dm.group(3))
        if mname not in lookup:
            raise WorldError(
                f"{dm.group(2)!r} is not a month name in any calendar this world uses. "
                f"Known: {', '.join(sorted(lookup))}. A world with its own calendar declares "
                f"it in CALENDAR.md; see `python3 tools/rules.py calendars`."
            )
        month = lookup[mname]
        return WorldDate(year, month, day, era, raw)
    mm = re.match(r"^([A-Za-z]+)\s+(-?\d+)$", body)
    if mm:
        mname, year = mm.group(1).lower(), int(mm.group(2))
        if mname not in lookup:
            raise WorldError(
                f"{mm.group(1)!r} is not a month name in any calendar this world uses. "
                f"Known: {', '.join(sorted(lookup))}."
            )
        return WorldDate(year, lookup[mname], 1, era, raw)
    ym = re.match(r"^(-?\d+)$", body)
    if ym:
        return WorldDate(int(ym.group(1)), 1, 1, era, raw)
    iso = re.match(r"^(-?\d+)-(\d{1,2})-(\d{1,2})$", body)
    if iso:
        return WorldDate(int(iso.group(1)), int(iso.group(2)), int(iso.group(3)), era, raw)
    raise WorldError(
        f"cannot order the date {text!r}. Write it as '4712 AR', 'Desnus 4712 AR' or "
        f"'12 Desnus 4712 AR'. Months known here: {', '.join(sorted(lookup))}. "
        f"Eras known here: {', '.join(era_names(world))}."
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
    """One concluded event in a world's chronicle.

    `system` names the ruleset of the campaign that promoted it, and `scope` the band of
    the world it reached. Both exist so that one world can hold entries written by both
    games without either one's numbers leaking into the shared record: a later campaign
    reads *what happened and how far it reached*, never a level or a stat block. An entry
    written before the second ruleset existed carries neither field and reads as
    Pathfinder, at unknown scope.
    """

    title: str
    date: WorldDate
    campaign: str
    characters: str
    visibility: str
    happened: str
    changed: str
    system: str = ""
    scope: str = ""
    raw: str = ""

    def render(self) -> str:
        lines = [f"## {self.title}", ""]
        if not self.date.undated:
            lines.append(f"- **Date:** {self.date}")
        lines += [
            f"- **Campaign:** {self.campaign}",
            f"- **System:** {self.system or 'unrecorded'}",
            f"- **Characters:** {self.characters or '—'}",
            f"- **Visibility:** {self.visibility}",
        ]
        if self.scope:
            lines.append(f"- **Scope:** {self.scope}")
        lines += [
            f"- **What happened:** {self.happened}",
            f"- **What it changed:** {self.changed}",
            "",
        ]
        return "\n".join(lines)


_FIELD_RE = re.compile(r"^\s*[-*]\s*\*\*(.+?):\*\*\s*(.*)$")


def parse_chronicle(text: str, world: str | None = None, *,
                    require_date: bool = True) -> list[Entry]:
    """Read dated entries out of a chronicle or a legends file.

    `require_date` is True for CHRONICLE.md, where an undated entry cannot be ordered and
    so cannot be gated. It is False for LEGENDS.md, whose own header says a legend with no
    date is treated as always current: those parse, sort first, and render without a Date
    line. (Before this, appending a legend to a file that already held an undated one
    failed outright, which made `promote --legend` unusable after the first hand-written
    legend.)
    """
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
            if require_date:
                raise WorldError(f"chronicle entry {title!r} has no **Date:** field")
            fields["date"] = ""
        vis = (fields.get("visibility") or "").lower()
        sysname = (fields.get("system") or "").strip()
        if sysname and sysname.lower() not in ("unrecorded", "unknown", "—", "-"):
            try:
                sysname = rules.canonical(sysname)
            except rules.RulesError:
                pass  # keep it verbatim; validate.py reports it rather than losing it
        else:
            sysname = ""
        entries.append(
            Entry(
                title=title,
                date=(parse_date(fields["date"], world) if fields["date"].strip()
                      else WorldDate(UNDATED_YEAR, 1, 1, "", "")),
                campaign=fields.get("campaign", ""),
                characters=fields.get("characters", ""),
                visibility=vis,
                happened=fields.get("what happened", ""),
                changed=fields.get("what it changed", ""),
                system=sysname,
                scope=(fields.get("scope") or "").strip().lower(),
                raw="## " + block.rstrip() + "\n",
            )
        )
    return entries


def insert_by_date(path: Path, entry: Entry, marker: str, world: str | None = None,
                   *, require_date: bool = True) -> None:
    """Add an entry in date order.

    The chronicle is append-only in the sense that matters — no entry is ever edited or
    removed — but it is also *read* in date order, so a new entry goes where its date puts
    it rather than at the end of the file. A campaign concluding a prequel arc would
    otherwise leave the file unreadable and fail validation.
    """
    text = path.read_text(encoding="utf-8")
    head, sep, body = text.partition(marker)
    if not sep:
        head, sep, body = text, "", ""
    existing = parse_chronicle(body, world, require_date=require_date)
    block = entry.render()
    if not existing:
        path.write_text(head + sep + "\n\n" + block, encoding="utf-8")
        return
    pieces = []
    placed = False
    for e in existing:
        if not placed and entry.date.key() < e.date.key():
            pieces.append(block)
            placed = True
        pieces.append(e.raw.rstrip() + "\n")
    if not placed:
        pieces.append(block)
    path.write_text(head + sep + "\n\n" + "\n".join(pieces), encoding="utf-8")


def read_chronicle(world: str) -> tuple[Path, list[Entry]]:
    path = world_dir(world) / "CHRONICLE.md"
    if not path.exists():
        raise WorldError(f"{path} does not exist — run `world.py init` first")
    return path, parse_chronicle(path.read_text(encoding="utf-8"), world)


# --------------------------------------------------------------------------------------
# init
# --------------------------------------------------------------------------------------
# The living history — the world's own book about itself
# --------------------------------------------------------------------------------------
#
# Four layers hold the past, and they are deliberately different shapes. Writing in the
# wrong one is the most common way a shared world turns into either a spreadsheet or a
# novel nobody can query:
#
#   CHRONICLE.md          the spine. Dated, structured, terse, machine-read, date-gated.
#                         One entry per concluded event. This is what `as-of` filters.
#   HISTORY.md            the book. Prose, shared by every ruleset, deliberately LESS
#                         PRECISE — it carries a span rather than a date and a stated
#                         certainty, because a world's memory of itself is uncertain and
#                         pretending otherwise is the lie. No numbers from any ruleset.
#   <system>/<campaign>.md  the full account. One file per campaign, grouped by ruleset,
#                         as detailed and as system-flavoured as it likes, because only
#                         that ruleset's campaigns read it.
#   LEGENDS.md            the distortions. How the above is told wrongly in-world.
#
# `system/24-the-living-history.md` is the long version, including which to write in.

#: How sure the world is that a chapter happened the way it says.
CERTAINTIES = ("attested", "recorded", "disputed", "legendary", "lost")

CERTAINTY_MEANS = {
    "attested": "more than one campaign saw it, or it left physical proof; treat as fact",
    "recorded": "one campaign saw it and wrote it down; treat as fact unless contradicted",
    "disputed": "accounts disagree on what happened, or who did it, or when",
    "legendary": "the world tells it, nobody alive saw it, and the details have drifted",
    "lost": "something happened here and the world no longer knows what",
}

HISTORY_HEADER = """# The history of {title}

The world's own book about itself. **Prose, shared by every ruleset, and deliberately less
precise than `CHRONICLE.md`.**

This is the layer a GM reads to know what kind of place this is, and the layer a player's
character could plausibly have been taught. It is written as history is written: in spans
rather than dates, with the certainty of each account stated, and with the gaps left visible
rather than filled.

## What goes in here, and what does not

| | |
|---|---|
| **In** | What happened and why it mattered. Causes, consequences, who was changed. Named people, places, factions. The shape of an age. What the world believes about itself |
| **In** | Uncertainty, stated: who disagrees, what was never established, what is only remembered |
| **Out** | **Any ruleset's numbers.** No levels, DCs, ACs, CRs, stat blocks, treasure or dice. A reader of this file may be playing a different game from the one that wrote the chapter |
| **Out** | Live state of any kind. That stays in `campaigns/<slug>/state.json`, permanently |
| **Out** | The blow-by-blow. That is the per-ruleset narrative in `<system>/<campaign>.md` |

## How a chapter is shaped

Each chapter carries three fields and then as much prose as it earns:

- **Span** — the range it covers, in this world's calendar. The *end* of the span is what
  the date gate reads, so a chapter is withheld from a campaign that has not reached it.
- **Certainty** — one of `attested`, `recorded`, `disputed`, `legendary`, `lost`.
- **Sources** — which campaigns contributed, each with its ruleset in brackets. A chapter
  with no source is the world's own background, written before any campaign ran.

Append with `python3 tools/world.py history add`, read with
`python3 tools/world.py history {slug}`, and the date-gated read in `as-of` includes it.

<!-- HISTORY-CHAPTERS-BELOW -->
"""


@dataclass
class Chapter:
    """One chapter of a world's living history. Prose, with a span rather than a date."""

    title: str
    span: str
    span_end: WorldDate
    certainty: str
    sources: str
    body: str
    raw: str = ""

    @property
    def systems(self) -> list[str]:
        """The rulesets named in the Sources field, canonicalised."""
        found = []
        for m in re.finditer(r"\(([^)]+)\)", self.sources):
            try:
                sid = rules.canonical(m.group(1).strip())
            except rules.RulesError:
                continue
            if sid not in found:
                found.append(sid)
        return found

    def render(self) -> str:
        lines = [
            f"## {self.title}",
            "",
            f"- **Span:** {self.span}",
            f"- **Certainty:** {self.certainty}",
            f"- **Sources:** {self.sources or 'the world itself'}",
            "",
            self.body.strip(),
            "",
        ]
        return "\n".join(lines)


def _span_end(span: str, world: str | None = None) -> WorldDate:
    """The latest date a span reaches, which is what the date gate reads.

    A span may be written '4726-4729 AR', '4726 to 4729 AR', 'before 4700 AR', or a single
    date. Anything unparseable raises, because a chapter that cannot be ordered cannot be
    gated, and a chapter that cannot be gated will eventually spoil somebody.
    """
    text = str(span).strip()
    if not text:
        raise WorldError("a history chapter needs a Span; without one it cannot be date-gated")
    # Normalise the separators a person would actually type.
    norm = re.sub(r"\s*(?:--|–|—|\bto\b|\bthrough\b)\s*", "-", text, flags=re.IGNORECASE)
    norm = re.sub(r"^\s*(?:before|by|up to|until)\s+", "", norm, flags=re.IGNORECASE)
    parts = [p.strip() for p in norm.split("-") if p.strip()]
    if not parts:
        raise WorldError(f"cannot read a span out of {span!r}")
    # A span like '4726-4729 AR' puts the era only on the last part, so carry it backwards.
    era = ""
    m = _era_re(world).search(parts[-1])
    if m:
        era = m.group(1)
    best: WorldDate | None = None
    for part in parts:
        candidate = part if _era_re(world).search(part) else f"{part} {era}".strip()
        try:
            d = parse_date(candidate, world)
        except WorldError:
            continue
        if best is None or d.key() > best.key():
            best = d
    if best is None:
        raise WorldError(
            f"cannot order the span {span!r}. Write it as '4726-4729 AR', '4729 AR', or "
            f"'before 4700 AR'."
        )
    return best


def parse_history(text: str, world: str | None = None) -> list[Chapter]:
    """Read the chapters out of a HISTORY.md."""
    out: list[Chapter] = []
    blocks = re.split(r"^##\s+", text, flags=re.MULTILINE)[1:]
    for block in blocks:
        lines = block.splitlines()
        title = lines[0].strip()
        fields: dict[str, str] = {}
        body_from = 1
        for i, line in enumerate(lines[1:], start=1):
            m = _FIELD_RE.match(line)
            if m:
                fields[m.group(1).strip().lower()] = m.group(2).strip()
                body_from = i + 1
            elif line.strip() and not line.lstrip().startswith(("-", "*")):
                break
        if "span" not in fields:
            raise WorldError(
                f"history chapter {title!r} has no **Span:** field, so it cannot be date-gated"
            )
        body = "\n".join(lines[body_from:]).strip()
        out.append(
            Chapter(
                title=title,
                span=fields["span"],
                span_end=_span_end(fields["span"], world),
                certainty=(fields.get("certainty") or "").strip().lower(),
                sources=fields.get("sources", ""),
                body=body,
                raw="## " + block.rstrip() + "\n",
            )
        )
    return out


HISTORY_MARKER = "<!-- HISTORY-CHAPTERS-BELOW -->"


def history_body(text: str) -> str:
    """Only the part of HISTORY.md below the marker holds chapters.

    The header explains what the file is for and does so in `##` sections, so parsing the
    whole file reads "What goes in here, and what does not" as a chapter with no Span and
    refuses to write anything. The chronicle has the same marker for the same reason; its
    header simply has no headings, which hid the problem until this file did.
    """
    _, sep, body = text.partition(HISTORY_MARKER)
    return body if sep else text


def read_history(world: str) -> tuple[Path, list[Chapter]]:
    path = world_dir(world) / "HISTORY.md"
    if not path.exists():
        return path, []
    return path, parse_history(history_body(path.read_text(encoding="utf-8")), world)


def cmd_history(args: argparse.Namespace) -> int:
    """Read the living history, date-gated unless --all is passed."""
    wdir = world_dir(args.world)
    if not wdir.is_dir():
        raise WorldError(f"no world at {wdir}")
    path, chapters = read_history(args.world)
    if not path.exists():
        print(f"worlds/{args.world}/HISTORY.md does not exist yet.")
        print("Create it with `python3 tools/world.py init ... --force`, or write the first")
        print("chapter with `python3 tools/world.py history add`.")
        return 0
    chapters.sort(key=lambda c: c.span_end.key())

    cutoff = parse_date(args.date, args.world) if args.date else None
    shown = [c for c in chapters if cutoff is None or c.span_end.key() <= cutoff.key()]
    later = len(chapters) - len(shown)

    print(f"# The history of {args.world}"
          + (f" — as of {cutoff}" if cutoff else " — in full"))
    print()
    if cutoff:
        print(f"{len(shown)} chapter(s) at or before this date"
              + (f"; {later} reaching later are withheld by the date gate." if later else "."))
    else:
        print(f"{len(shown)} chapter(s). **Not date-gated** — do not read this during a campaign "
              f"that has not reached the end of it.")
    print()
    if not shown:
        print("_(the world has no recorded history at or before this date.)_")
        return 0
    for c in shown:
        print(c.raw)
    if later and cutoff:
        print("---")
        print()
        print(f"**Withheld by the date gate:** {later} chapter(s) reaching past {cutoff}. "
              f"Titles are not shown — reading them would defeat the gate.")
    return 0


def cmd_history_add(args: argparse.Namespace) -> int:
    """Append a chapter to the living history, in span order."""
    wdir = world_dir(args.world)
    if not wdir.is_dir():
        raise WorldError(f"no world at {wdir}")
    path = wdir / "HISTORY.md"
    if not path.exists():
        atomic_write(path, HISTORY_HEADER.format(title=args.world, slug=args.world))
        print(f"created worlds/{args.world}/HISTORY.md")

    certainty = args.certainty.strip().lower()
    if certainty not in CERTAINTIES:
        raise WorldError(f"certainty must be one of {', '.join(CERTAINTIES)} (got {certainty!r})")

    sources = args.sources or ""
    if args.campaign:
        system = rules.for_campaign(args.campaign)
        tag = f"{args.campaign} ({rules.short_of(system)})"
        sources = f"{sources}; {tag}" if sources else tag

    chapter = Chapter(
        title=args.title,
        span=args.span,
        span_end=_span_end(args.span, args.world),
        certainty=certainty,
        sources=sources,
        body=args.body,
    )

    # The same refusal the chronicle uses: nothing live, and nothing from a ruleset.
    blob = f"{args.title} {args.body}".lower()
    for marker in LIVE_STATE_MARKERS:
        if marker in blob:
            raise WorldError(
                f"refusing to write this chapter: the text contains {marker!r}, which looks like "
                f"live state. The history gets what happened and why it mattered."
            )
    numbers = _ruleset_numbers(f"{args.title} {args.body}")
    if numbers and not args.allow_numbers:
        raise WorldError(
            "refusing to write this chapter: it mentions " + ", ".join(numbers) + ". The living "
            "history is read by every ruleset in this world, and a reader playing the other game "
            "cannot use those. Say what happened instead — `python3 tools/world.py crossing` has "
            "the before-and-after table. Pass --allow-numbers only if the number is an in-world "
            "quantity (a count of ships, a span of years) rather than a rules value."
        )

    print("About to append this chapter to the world's living history:")
    print()
    print(f"  worlds/{args.world}/HISTORY.md")
    print(chapter.render().replace("\n", "\n  "))
    others = [sid for sid in rules.for_world(args.world) if sid not in chapter.systems]
    if others:
        print(f"  NOTE: {', '.join(rules.short_of(x) for x in others)} campaign(s) also read this "
              f"history.")
    if not args.yes:
        try:
            answer = input("\nAppend it? [y/N] ").strip().lower()
        except EOFError:
            answer = ""
        if answer not in ("y", "yes"):
            print("Nothing written.")
            return 1

    _insert_chapter(path, chapter, args.world)
    # The chapter is written at this point. Counting it back is a courtesy, so a failure
    # here must not be reported as a failure of the write — an earlier version of this
    # function raised on the re-read and told the user nothing had been written while the
    # file on disk had in fact grown by one chapter, which is the worst of both.
    try:
        _, after = read_history(args.world)
        count = f"{len(after)} chapter(s), in span order"
    except WorldError as exc:
        count = (f"written, but the file no longer parses ({exc}) — fix it by hand before "
                 f"the next append")
    print(f"\nappended to worlds/{args.world}/HISTORY.md — {count}")
    print(f"certainty `{certainty}`: {CERTAINTY_MEANS[certainty]}")
    print("\nNo live state and no ruleset's numbers were written. The blow-by-blow belongs in")
    print(f"`worlds/{args.world}/<system>/<campaign>.md` — see `world.py narrative`.")
    return 0


_NUMBER_PATTERNS = (
    (r"\bDC\s*\d+", "a DC"),
    (r"\bAC\s*\d+", "an AC"),
    (r"\bCR\s*\d+", "a Challenge Rating"),
    (r"\blevel[- ]\d+\b", "a level"),
    (r"\b\d+d\d+\b", "a dice expression"),
    (r"\b\d+\s*(?:gp|sp|cp|ep|pp)\b", "a coin value"),
    (r"\b\d+\s*(?:hp|hit points)\b", "hit points"),
)


def _ruleset_numbers(text: str) -> list[str]:
    """Which ruleset numbers a passage mentions. Used to keep the shared layer neutral."""
    found = []
    for pat, what in _NUMBER_PATTERNS:
        if re.search(pat, text, re.IGNORECASE) and what not in found:
            found.append(what)
    return found


def _insert_chapter(path: Path, chapter: Chapter, world: str) -> None:
    """Add a chapter in span order, the way `insert_by_date` does for the chronicle."""
    text = path.read_text(encoding="utf-8")
    head, sep, body = text.partition(HISTORY_MARKER)
    if not sep:
        head, sep, body = text, HISTORY_MARKER, ""
    existing = parse_history(body, world)
    block = chapter.render()
    if not existing:
        atomic_write(path, head + sep + "\n\n" + block)
        return
    pieces, placed = [], False
    for c in existing:
        if not placed and chapter.span_end.key() < c.span_end.key():
            pieces.append(block)
            placed = True
        pieces.append(c.raw.rstrip() + "\n")
    if not placed:
        pieces.append(block)
    atomic_write(path, head + sep + "\n\n" + "\n".join(pieces))


# --------------------------------------------------------------------------------------
# Per-ruleset narrative history — one thorough account per campaign
# --------------------------------------------------------------------------------------

SYSTEM_FOLDER_README = """# {system_name} campaigns in {world}

One file per campaign, holding the **thorough narrative history** of what happened in it.

This folder is read by {system_short} campaigns only, which is what lets it be detailed in a
way the shared `HISTORY.md` cannot be. Here you may name the rules, the class, the spell,
the creature and the roll that turned a scene — a reader of this folder is playing the same
game, so none of it is noise to them.

## How this relates to the rest of the world

| File | Shape | Who reads it |
|---|---|---|
| `../CHRONICLE.md` | dated, structured, terse, one entry per event | every ruleset, date-gated |
| `../HISTORY.md` | prose, spans rather than dates, certainty stated, **no numbers** | every ruleset, date-gated |
| **this folder** | prose, thorough, system-flavoured, as long as it earns | **{system_short} only** |
| `../LEGENDS.md` | how the above is told wrongly in-world | every ruleset |

So one event can appear in all four: a line in the chronicle, a paragraph in the history,
three pages here, and a distorted song in the legends.

## The rule that still applies

**Nothing live.** Current hit points, coins, inventory, conditions, positions, checkpoints
and roll logs stay in `campaigns/<slug>/` permanently, even here. What belongs here is the
*account* — what happened, what it cost, who changed — written after the fact.

`python3 tools/validate.py --world {world}` fails a file here that reads like live state.
"""

NARRATIVE_TEMPLATE = """# {title}

The thorough narrative history of this campaign. Written for a {system_short} reader, so the
rules may be named.

- **Campaign:** {campaign}
- **System:** {system_name}
- **World:** worlds/{world}
- **Span:** {span}
- **Status:** active / concluded / abandoned / on hold
- **Protagonists:** {characters}

> The shared, system-neutral version of these events lives in `../HISTORY.md`, and the dated
> index in `../CHRONICLE.md`. This file is where the detail goes. Write it as the account a
> player would want to re-read in two years, not as a log.

---

## Before it started

_What was already true. The situation the first scene walked into._

## The arcs

_One section per arc, in order. For each: what the party wanted, what stood in the way, what
it cost, and what was different afterwards. Name the moments that mattered and say why they
mattered — a reader who was not there should be able to feel the turn._

### _(arc name)_

- **Span:**
- **What changed:**

_Prose._

---

## The people

_Who mattered, and what became of them. Allies, enemies, the ones who were neither._

| Who | What they were to the party | Where they ended |
|---|---|---|
| | | |

## What it cost

_Deaths, losses, debts, bargains, things that cannot be undone. This is the section that
makes a campaign's history worth keeping._

## What is still unresolved

_Threads a later campaign in this world could pick up. World-level ones also belong in
`../gm-private/threads.md`._

---

## Promoted to the shared layer

_Which of the above reached `../CHRONICLE.md` and `../HISTORY.md`, so the two do not drift._

| What | Chronicle entry | History chapter |
|---|---|---|
| | | |
"""


def system_dir(world: str, system: str) -> Path:
    return world_dir(world) / rules.canonical(system)


def ensure_system_folder(world: str, system: str) -> tuple[Path, bool]:
    """The per-ruleset narrative folder for a world, created on first use."""
    sid = rules.canonical(system)
    d = system_dir(world, sid)
    created = not d.exists()
    d.mkdir(parents=True, exist_ok=True)
    readme = d / "README.md"
    if not readme.exists():
        atomic_write(readme, SYSTEM_FOLDER_README.format(
            system_name=rules.name_of(sid), system_short=rules.short_of(sid), world=world))
    return d, created


def cmd_narrative(args: argparse.Namespace) -> int:
    """Create or report the per-ruleset narrative history file for a campaign."""
    world = args.world or _world_of(args.campaign)
    if not world:
        raise WorldError(
            f"{args.campaign} has no `World:` field, so it has no world to keep a narrative in. "
            f"A standalone campaign's history lives in its own `sessions/` folder."
        )
    if not world_dir(world).is_dir():
        raise WorldError(f"no world at {world_dir(world)}")
    system = rules.for_campaign(args.campaign)
    d, created = ensure_system_folder(world, system)
    if created:
        print(f"created worlds/{world}/{system}/ with its README")

    path = d / f"{args.campaign}.md"
    if path.exists() and not args.force:
        chapters = path.read_text(encoding="utf-8")
        print(f"worlds/{world}/{system}/{args.campaign}.md already exists "
              f"({len(chapters.splitlines())} lines). Pass --force to overwrite it.")
        print("\nIt is yours to write by hand — the tool only scaffolds it. Add to it at the end")
        print("of each arc, while the detail is still in reach.")
        return 0

    cm = campaign_dir(args.campaign) / "CAMPAIGN.md"
    title = args.campaign
    span = "_(start date to now)_"
    if cm.exists():
        text = cm.read_text(encoding="utf-8")
        first = text.splitlines()[0].lstrip("# ").strip()
        if first:
            title = first
        start = pf2e.read_field(text, "Start date")
        if start:
            span = f"{start} to _(now)_"
    chars = []
    spath = campaign_dir(args.campaign) / "state.json"
    if spath.exists():
        try:
            data = json.loads(spath.read_text(encoding="utf-8"))
            chars = [pc.get("name", k) for k, pc in (data.get("pcs") or {}).items()
                     if pc.get("kind") == "pc"]
        except (OSError, ValueError):
            pass

    atomic_write(path, NARRATIVE_TEMPLATE.format(
        title=title, campaign=args.campaign, world=world,
        system_name=rules.name_of(system), system_short=rules.short_of(system),
        span=span, characters=", ".join(chars) or "_(not yet)_"))
    print(f"wrote worlds/{world}/{system}/{args.campaign}.md")
    print(f"  the thorough {rules.short_of(system)} account — the rules may be named here")
    print(f"  the shared, neutral version goes in worlds/{world}/HISTORY.md "
          f"(`world.py history add`)")
    return 0


# --------------------------------------------------------------------------------------
# The universe — the layer above worlds
# --------------------------------------------------------------------------------------

UNIVERSE_FILE = "UNIVERSE.md"

UNIVERSE_TEMPLATE = """# The universe

The layer above `worlds/`. **Optional, and only worth having once a second world exists.**

A world is a place campaigns are set in. A universe is what is true *across* places — so
that a campaign on another continent, another plane or in another age can be the same
universe as the first without sharing its geography, its factions or its history.

## The worlds in it

| World | Where it sits | Era | Rulesets | Reachable from |
|---|---|---|---|---|
| | | | | |

`python3 tools/world.py universe` rebuilds this table from the world folders themselves, so
it does not drift. Each world declares its own position with a `Position:` field in its
README.

## What is true everywhere

_The things a character from any of these worlds would recognise. Keep this short — the
longer it is, the less room each world has to be itself._

### Cosmology

_Planes, afterlives, where magic comes from, what the stars are. Only the parts that hold
in every world below._

### The deep past

_What happened before any of these worlds had a history of its own, and is remembered
everywhere — usually wrongly, and differently in each place._

### Powers that span worlds

_Gods, empires, orders, things that are worshipped or feared in more than one of them.
A power named here can appear in any world; one named in a single world's `PANTHEON.md`
cannot._

## How the worlds connect

_The honest answer is often "they do not, yet", and that is a fine answer. Write it down
anyway, because "no known route" is itself a fact a campaign can work against._

| From | To | Route | Who knows it | Cost |
|---|---|---|---|---|
| | | | | |

## What crosses between worlds

The same discipline as `system/23-cross-system-worlds.md`, one layer up. Across worlds:

| Crosses | Does not cross |
|---|---|
| Cosmology, planar structure, the deep past | Local history, local factions, local geography |
| Powers named in this file | Powers named in a single world's PANTHEON.md |
| A character who physically travelled, with their story | A character's reputation, unless news travelled with them |
| Items, with their histories | Any ruleset's numbers — see `world.py crossing` |

**A world's history is its own.** A chapter in one world's `HISTORY.md` is not known in
another unless something carried it there, and saying what carried it is more interesting
than assuming it did.

## The rules that keep this layer clean

- **Nothing live, ever.** Same as `worlds/`.
- **No ruleset's numbers.** This file may be read by a campaign in any of the games.
- **Write here only what is true in every world listed.** A fact true in one world belongs
  in that world's files. This is the most commonly broken rule and the one that makes the
  layer worthless when broken.
"""


def universe_path() -> Path:
    return repo_root() / "worlds" / UNIVERSE_FILE


def world_position(world: str) -> dict[str, str]:
    """A world's declared place in the universe, from its README."""
    p = world_dir(world) / "README.md"
    if not p.exists():
        return {}
    text = p.read_text(encoding="utf-8")
    out = {}
    for field in ("Universe", "Position", "Era", "Reachable from"):
        v = pf2e.read_field(text, field)
        if v:
            out[field] = v.strip()
    return out


def list_worlds() -> list[str]:
    root = repo_root() / "worlds"
    if not root.is_dir():
        return []
    return sorted(d.name for d in root.iterdir()
                  if d.is_dir() and (d / "README.md").exists())


def cmd_universe(args: argparse.Namespace) -> int:
    """Show the universe register, rebuilding the world table from the folders."""
    path = universe_path()
    if args.init:
        if path.exists() and not args.force:
            raise WorldError(f"{path} already exists (pass --force to overwrite it)")
        atomic_write(path, UNIVERSE_TEMPLATE)
        print(f"wrote worlds/{UNIVERSE_FILE}")
        print("\nIt is optional and only worth having once a second world exists. Declare each")
        print("world's place in it with a `Universe:` and `Position:` field in its README.")
        return 0

    worlds = list_worlds()
    print("# The universe — worlds registered in it")
    print()
    if not path.exists():
        print(f"_(worlds/{UNIVERSE_FILE} does not exist. `world.py universe --init` writes it. "
              f"It is optional.)_")
        print()
    rows = []
    for w in worlds:
        pos = world_position(w)
        systems = rules.for_world(w)
        rows.append({
            "world": w,
            "universe": pos.get("Universe", "—"),
            "position": pos.get("Position", "—"),
            "era": pos.get("Era", "—"),
            "rulesets": ", ".join(rules.short_of(s) for s in systems) or "none yet",
            "reachable from": pos.get("Reachable from", "—"),
        })
    if not rows:
        print("_(no worlds yet. `world.py init \"<name>\"` makes one.)_")
        return 0
    cols = ["world", "universe", "position", "era", "rulesets", "reachable from"]
    widths = {c: max(len(c), *(len(str(r[c])) for r in rows)) for c in cols}
    print("  ".join(c.ljust(widths[c]) for c in cols))
    print("  ".join("-" * widths[c] for c in cols))
    for r in rows:
        print("  ".join(str(r[c]).ljust(widths[c]) for c in cols))
    print()
    named = {r["universe"] for r in rows if r["universe"] != "—"}
    if len(named) > 1:
        print(f"⚠ These worlds name {len(named)} different universes: {', '.join(sorted(named))}.")
        print("  That is legal, but nothing crosses between universes — not even cosmology.")
    elif named:
        print(f"All of them are in **{named.pop()}**, so what `{UNIVERSE_FILE}` says is true in "
              f"every one.")
    else:
        print(f"None of them declares a `Universe:` field, so they are unrelated places that")
        print(f"happen to live in the same repository. Add the field to link them.")
    unlinked = [r["world"] for r in rows if r["rulesets"] == "none yet"]
    if unlinked:
        print(f"\nNo campaign is set in: {', '.join(unlinked)}.")
    return 0


# --------------------------------------------------------------------------------------

def _slug(name: str) -> str:
    """'The Verdant Reach' -> 'verdant-reach'. A leading article is dropped, because a folder
    called `the-verdant-reach` reads badly in every path that mentions it. Pass --slug to
    override."""
    text = re.sub(r"^\s*(the|a|an)\s+", "", str(name), flags=re.IGNORECASE)
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s or "world"


WORLD_FILES: dict[str, str] = {
    "README.md": """# {title}

A shared setting. Several campaigns can be set here, in different eras.

A world here is **system-neutral**: campaigns running any supported ruleset can be set in
it, and the shared layer records what happened rather than anyone's numbers.

## Where this world sits

- **Universe:** none
- **Position:** _(a continent, a plane, an age — whatever distinguishes it from the others)_
- **Era:** _(the present day here)_
- **Reachable from:** _(other worlds, and how; "no known route" is a fine answer)_

> `Universe:` links this world to others in `worlds/UNIVERSE.md`, so a campaign somewhere
> else entirely can be the same universe without sharing this world's history or geography.
> `none` keeps it standalone. `python3 tools/world.py universe` lists the register.

## Campaigns set in this world

| Campaign | System | Era / start date | Status |
|---|---|---|---|
| _(none yet — `tools/world.py link` adds a row)_ | | | |

## What this world is

_Two or three paragraphs: the shape of the place, what makes it itself, and the one thing
a newcomer needs to know._

## What lives where

- `CHRONICLE.md` — dated record of concluded events, append-only, one line of visibility each.
- `HISTORY.md` — the living history: prose, shared by every ruleset, spans rather than dates,
  the certainty of each account stated, and **no ruleset's numbers**.
- `<system>/<campaign>.md` — the thorough narrative history of one campaign, read only by
  campaigns of that ruleset, so it may name the rules.
- `LEGENDS.md` — how those events are *remembered* in-world, distortions included.
- `GAZETTEER.md` — places, regions, settlements and what can be bought in each.
- `FACTIONS.md` — long-lived organisations, their standing and leadership.
- `PANTHEON.md` — gods and cosmology.
- `CALENDAR.md` — the calendar, eras, and the current present day. The calendar belongs to
  the world, not to a ruleset, so every game reads the same dates.
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
- **No ruleset's numbers go in here.** Events, people, places, debts and reputations
  cross between the games; levels, DCs, stat blocks and treasure do not. Chronicle
  entries carry a `System:` line saying which game wrote them and a `Scope:` line saying
  how far the event reached — scope is the only translation this framework will make.
  `python3 tools/world.py crossing` is the full statement.
""",
    "CHRONICLE.md": CHRONICLE_HEADER,
    "HISTORY.md": HISTORY_HEADER,
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

Places, regions and settlements. A market is the one place where a world fact and a
ruleset's numbers meet, so each settlement carries **one column per ruleset** and a campaign
reads its own column.

| Place | Type | Region | Item level (PF2e) | Buys up to (D&D) | One line |
|---|---|---|---|---|---|
| | | | | | |

- **Item level (PF2e)** governs what can be bought there (GM Core p.168, Marketplaces).
  Set it explicitly per settlement, then `python3 tools/pf2e.py settlement --level N`
  reads off what is available. The size names in `tools/pf2e.py` are only a suggestion
  for picking one.
- **Buys up to (D&D)** is the highest magic item rarity on sale: common, uncommon, rare,
  very rare or legendary. `python3 tools/dnd5e.py settlement <kind>` gives the published
  guidance behind it.

Fill in the column for whichever ruleset is playing and leave the other blank until a
campaign in that game needs it. **Do not derive one from the other** — the two economies
are not the same shape, and a converted number would be a guess wearing a source's
clothes. Pick the second column's value from the place as described, the same way the
first was picked.
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

For an original setting, the gods and the shape of the afterlife. For a published one, a
pointer is enough — _"Golarion as published; see Player Core and Divine Mysteries"_ — and
the same goes for any published D&D setting.

Gods and planes are world facts, so they cross between the rulesets unchanged. What does
not cross is the mechanical attachment: a Pathfinder deity's granted spells, favoured
weapon and sanctification are Pathfinder's, and a D&D cleric's subclass is D&D's. Record
who the gods **are** here, and let each campaign's ruleset supply how they are served.
""",
    "CALENDAR.md": """# Calendar

**The calendar belongs to this world, not to a ruleset.** One shared world keeps one
calendar no matter which game is being played in it this month, which is what lets a
D&D campaign and a Pathfinder campaign sit on the same timeline and read each other's
dates. `python3 tools/rules.py calendars` lists every calendar the tools know.

- **Calendar in use:** golarion (Absalom Reckoning) / generic / this world's own
- **Present day of this world:** _(the latest date any campaign has reached)_
- **Eras:** _(named spans, if the world has them)_

## Built-in calendars

- `golarion` — Absalom Reckoning, which maps month for month onto the Gregorian calendar
  and keeps its month lengths: Abadius 31, Calistril 28, Pharast 31, Gozran 30, Desnus 31,
  Sarenith 30, Erastus 31, Arodus 31, Rova 30, Lamashan 31, Neth 30, Kuthona 31, with
  weekdays Moonday, Toilday, Wealday, Oathday, Fireday, Starday, Sunday.
  Source: `python3 tools/pf2e.py sources` (`calendar`).
- `generic` — twelve 30-day months and a seven-day week, with no era. This framework's
  own placeholder, not a published calendar.

SRD 5.2 publishes no calendar, so a D&D campaign uses `generic` unless this world defines
its own below. Leap years are not modelled in any of them.

## This world's own calendar

This world has none yet, and uses a built-in. To define one:

1. Copy the JSON below and edit it.
2. Put an HTML comment reading `CALENDAR-BEGIN` on the line above the fenced block, and
   one reading `CALENDAR-END` on the line below it — the same `<!--` / `-->` syntax this
   file's other comments use.
3. Check the result with `python3 tools/rules.py calendars`.

The tools read the JSON between those two comments and ignore everything else on this
page, so the prose around it stays yours. The markers are deliberately **not** written in
for you: a live example would quietly give this world a two-month year.

The example, with the shape of every field:

```json
{
  "name": "verdant-reach",
  "era": "VR",
  "months": [
    {"name": "Thawmonth", "days": 31},
    {"name": "Seedfall", "days": 30}
  ],
  "weekdays": ["Firstday", "Seconday", "Thirday", "Fourthday", "Fifthday", "Restday"]
}
```

`name` is what `state.json` stores in `time.calendar`, `era` is appended to every rendered
date (leave it `""` for none), `months` may be any number of any lengths, and `weekdays`
may be any number. Once it reads back correctly, point the campaigns at it:
`python3 tools/state.py --campaign <slug> set time.calendar <name>`.
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
    parse_date(args.start_date, args.world)  # fail early on an unorderable date
    system = rules.for_campaign(args.campaign)

    cpath = cdir / "CAMPAIGN.md"
    if not cpath.exists():
        raise WorldError(f"{cpath} does not exist")
    text = cpath.read_text(encoding="utf-8")
    text = _set_field(text, "World", f"worlds/{args.world}")
    text = _set_field(text, "Era", args.era or args.start_date)
    text = _set_field(text, "Start date", args.start_date)
    atomic_write(cpath, text)

    already = [sid for sid in rules.for_world(args.world) if sid != system]

    rpath = wdir / "README.md"
    rtext = rpath.read_text(encoding="utf-8")
    row = f"| {args.campaign} | {rules.short_of(system)} | {args.era or args.start_date} | active |"
    placeholder = "| _(none yet — `tools/world.py link` adds a row)_ | | | |"
    old_placeholder = "| _(none yet — `tools/world.py link` adds a row)_ | | |"
    if placeholder in rtext:
        rtext = rtext.replace(placeholder, row)
    elif old_placeholder in rtext:
        # A world scaffolded before the System column existed. Widen its table in place.
        rtext = rtext.replace(
            "| Campaign | Era / start date | Status |\n|---|---|---|\n" + old_placeholder,
            "| Campaign | System | Era / start date | Status |\n|---|---|---|---|\n" + row,
        )
        rtext = rtext.replace(old_placeholder, row)
    elif row not in rtext:
        rtext = re.sub(r"(\n\| ---.*\n(?:\|.*\n)*)", lambda m: m.group(1) + row + "\n", rtext, count=1)
        if row not in rtext:
            rtext = rtext.replace("## What this world is", row + "\n\n## What this world is", 1)
    atomic_write(rpath, rtext)

    # The world owns the calendar, so adopt it into state.json as well as writing the
    # date into CAMPAIGN.md. Writing only the Markdown left the two disagreeing, and
    # nothing caught it: the campaign file said 3 Gozran 4729 AR while every rendered
    # date said "1 Month 1 1".
    adopted = None
    cal = world_calendar_name(args.world)
    if cal:
        spath = campaign_dir(args.campaign) / "state.json"
        if spath.exists():
            try:
                data = json.loads(spath.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                data = None
            if isinstance(data, dict):
                t = dict(data.get("time") or {})
                if str(t.get("calendar", "")).lower() != cal:
                    before = t.get("calendar")
                    t["calendar"] = cal
                    # Seat the clock on the start date so the two files agree from the
                    # first render rather than from the first `advance-time`.
                    d = parse_date(args.start_date, args.world)
                    t["year"], t["month"], t["day"] = d.year, d.month, d.day
                    t.setdefault("minute_of_day", 8 * 60)
                    t.setdefault("elapsed_minutes", 0)
                    data["time"] = t
                    atomic_write(spath, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
                    adopted = (before, cal, rules.format_time(t))

    print(f"{args.campaign} ({rules.short_of(system)}) → worlds/{args.world}, "
          f"starting {args.start_date}")
    print(f"  wrote World:, Era: and Start date: into {cpath.relative_to(repo_root())}")
    print(f"  added a row to {rpath.relative_to(repo_root())}")
    if adopted:
        before, cal, rendered = adopted
        print(f"  adopted the world's calendar into state.json: {before!r} → {cal!r}, "
              f"clock set to {rendered}")
        print(f"  (re-render with `python3 tools/state.py --campaign {args.campaign} render`)")
    elif cal:
        print(f"  calendar already {cal!r}, matching the world")
    else:
        print(f"  ⚠ worlds/{args.world}/CALENDAR.md names no calendar, so this campaign keeps "
              f"its own — declare one there so every campaign in the world shares a timeline")
    print("\nThe date gate is now live: when running this campaign, read world material dated at or")
    print(f"before its current in-world date and nothing later. `world.py as-of {args.world} <date>`.")
    # The per-ruleset narrative folder, so there is somewhere for the thorough account to
    # go from the first session rather than after someone remembers it exists.
    _, made = ensure_system_folder(args.world, system)
    print(f"  {'created' if made else 'using'} worlds/{args.world}/{system}/ for this ruleset's "
          f"narrative histories")
    npath = system_dir(args.world, system) / f"{args.campaign}.md"
    if not npath.exists():
        print(f"  write the campaign's own account with `python3 tools/world.py narrative "
              f"--campaign {args.campaign}`")

    if already:
        print(f"\nThis world is now shared across rulesets: {', '.join(rules.short_of(x) for x in already)}"
              f" campaign(s) are already set here.")
        print("  The world layer stays system-neutral. Read `python3 tools/world.py crossing` and")
        print("  system/23-cross-system-worlds.md before the first promotion.")
    return 0


# --------------------------------------------------------------------------------------
# as-of
# --------------------------------------------------------------------------------------


def cmd_as_of(args: argparse.Namespace) -> int:
    cutoff = parse_date(args.date, args.world)
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
        if args.gm:
            print("**Withheld by the date gate** (shown because --gm was passed):")
            for e in later:
                print(f"- {e.date} — {e.title} ({e.campaign})")
        else:
            # A gate that names what it is hiding is not a gate: reading the title is
            # already the spoiler. Count only, same as the secret-visibility path below.
            print(f"**Withheld by the date gate:** {len(later)} entry/entries dated later "
                  f"than {args.date}. Titles are not shown — reading them would defeat "
                  f"the gate. Use --gm if you need them.")
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

    # The living history, gated the same way. Its chapters carry a span, and the END of the
    # span is what the gate reads, so a chapter still running at the cutoff is withheld.
    hpath, chapters = read_history(args.world)
    if hpath.exists():
        chapters.sort(key=lambda c: c.span_end.key())
        shown = [c for c in chapters if c.span_end.key() <= cutoff.key()]
        held = len(chapters) - len(shown)
        print("## The living history at this date")
        print()
        if shown:
            print(f"{len(shown)} chapter(s)"
                  + (f"; {held} reaching later are withheld." if held else ".")
                  + " Prose, shared by every ruleset, and imprecise on purpose.")
            print()
            for c in shown:
                print(f"### {c.title}")
                print()
                print(f"- **Span:** {c.span} · **Certainty:** {c.certainty or 'unstated'}"
                      + (f" · **Sources:** {c.sources}" if c.sources else ""))
                print()
                print(c.body)
                print()
        else:
            print("_(no chapter of the history reaches this date yet"
                  + (f"; {held} are withheld by the gate.)_" if held else ".)_"))
            print()

    # The thorough per-ruleset account, named rather than printed: it is long, and a
    # campaign of another ruleset should not read it at all.
    sys_dirs = [d for d in sorted(world_dir(args.world).iterdir())
                if d.is_dir() and rules.is_known(d.name)] if world_dir(args.world).is_dir() else []
    if sys_dirs:
        print("## Per-ruleset narrative histories")
        print()
        for d in sys_dirs:
            files = sorted(f.stem for f in d.glob("*.md") if f.name != "README.md")
            print(f"- `worlds/{args.world}/{d.name}/` — {rules.short_of(d.name)}: "
                  + (", ".join(files) if files else "_(no campaign accounts yet)_"))
        print()
        print("Read only your own ruleset's folder. These are thorough and name the rules, so")
        print("another game's is noise at best and a spoiler at worst — and they are NOT")
        print("date-gated, so read a campaign's own file and not a later one's.")
        print()

    print("## Undated setting material (read in full)")
    print()
    for name in ("GAZETTEER.md", "FACTIONS.md", "PANTHEON.md", "CALENDAR.md", "canon.md"):
        p = world_dir(args.world) / name
        print(f"- `worlds/{args.world}/{name}`" + ("" if p.exists() else "  _(absent)_"))
    print()
    pos = world_position(args.world)
    if pos.get("Universe") and pos["Universe"].lower() not in ("none", "—", "-"):
        print(f"## Universe: {pos['Universe']}")
        print()
        print(f"- This world sits at: {pos.get('Position', '_(unstated)_')}")
        if pos.get("Reachable from"):
            print(f"- Reachable from: {pos['Reachable from']}")
        print(f"- What is true across every world in it: `worlds/{UNIVERSE_FILE}`")
        print()
        print("Another world's history is **not** known here unless something carried it.")
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
    date = parse_date(args.date, world)
    path, entries = read_chronicle(world)

    # Which ruleset this campaign runs, and how far its characters reach. The band is
    # recorded rather than the level, because a level means nothing to the other game.
    system = rules.for_campaign(args.campaign)
    scope = args.scope
    if not scope and args.level is not None:
        scope = rules.scope_band(system, args.level)
    if scope and scope not in rules.SCOPE_NAMES:
        raise WorldError(f"scope must be one of {', '.join(rules.SCOPE_NAMES)} (got {scope!r})")

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
        system=system,
        scope=scope or "",
    )

    # Parse the legends file now, not after the chronicle has been written: a promotion
    # that appends the event and then fails on the telling leaves the world half-updated,
    # and the chronicle is append-only so there is no clean way back.
    lpath = world_dir(world) / "LEGENDS.md"
    if args.legend and lpath.exists():
        head, sep, body = lpath.read_text(encoding="utf-8").partition("<!-- LEGEND-ENTRIES-BELOW -->")
        try:
            parse_chronicle(body if sep else "", world, require_date=False)
        except WorldError as exc:
            raise WorldError(
                f"{lpath.relative_to(repo_root())} cannot be read, so the telling cannot be "
                f"appended: {exc}. Nothing has been written."
            ) from exc

    print("About to append this to the world chronicle — it is append-only and permanent:")
    print()
    print(f"  world:      worlds/{world}/CHRONICLE.md")
    print(entry.render().replace("\n", "\n  "))
    others = [sid for sid in rules.for_world(world) if sid != system]
    if others:
        print(f"  NOTE: {', '.join(rules.short_of(x) for x in others)} campaign(s) also read this "
              f"world.")
        print(f"        Write the entry so it survives being read by them: what happened, who did")
        print(f"        it, and what changed. No levels, no DCs, no stat blocks — those do not")
        print(f"        cross. `python3 tools/world.py crossing` explains why.")
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

    insert_by_date(path, entry, "<!-- CHRONICLE-ENTRIES-BELOW -->", world)
    _, after = read_chronicle(world)
    pos = next((i for i, e in enumerate(after, start=1) if e.title == entry.title), len(after))
    print(f"\nappended to worlds/{world}/CHRONICLE.md as entry {pos} of {len(after)}, in date order")
    if args.legend:
        legend = Entry(
            title=f"How it is told: {args.title}",
            date=date,
            campaign=args.campaign,
            characters=args.characters or "",
            visibility="public",
            happened=args.legend,
            changed="_(what the telling gets wrong, and who benefits from the version told)_",
            system=system,
            scope=scope or "",
        )
        insert_by_date(lpath, legend, "<!-- LEGEND-ENTRIES-BELOW -->", world,
                       require_date=False)
        print(f"appended the telling to worlds/{world}/LEGENDS.md, in date order")
    print("\nNo live state was promoted. Current HP, coins, inventory, conditions, checkpoints and")
    print("roll logs stay in the campaign folder permanently.")
    return 0


def _world_of(campaign: str) -> str | None:
    """Moved to rules.py so that every tool resolves a `World:` field identically."""
    return rules.world_of_campaign(campaign)


# --------------------------------------------------------------------------------------
# legacy
# --------------------------------------------------------------------------------------

LEGACY_TEMPLATE = """# {name}

A legacy record. Written at retirement or campaign end, updated if they return.

- **Campaign:** {campaign}
- **World:** worlds/{world}
- **System:** {system_name}
- **Ancestry / class:** {ancestry_class}
- **Level reached:** {level} ({system_short})
- **Scope reached:** {scope} — {scope_means}
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

## If they appear in a campaign running another ruleset

**Do not convert the numbers.** The level above means something in {system_short} and nothing
in the other game; `Scope reached` is the field that crosses. Rebuild them from this page —
who they are, what they did, what they are owed — and let the target ruleset's own
character rules decide the statistics.

{crossing_note}

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
    system = rules.for_campaign(args.campaign)
    band = rules.scope_band(system, level) if isinstance(level, int) else ""
    others = [sid for sid in rules.SYSTEMS if sid != system]
    if band:
        low, high = rules.levels_in_band(others[0], band)
        crossing = (f"In {rules.short_of(others[0])} that scope is roughly levels {low}-{high} — "
                    f"a range, not a conversion. See `python3 tools/world.py crossing`.")
    else:
        crossing = ("Record the scope band once their level is known; it is the only field that "
                    "means anything to another ruleset.")
    atomic_write(
        path,
        LEGACY_TEMPLATE.format(
            name=name,
            campaign=args.campaign,
            world=world,
            level=level if level is not None else "_(level)_",
            ancestry_class=ancestry_class,
            availability=args.availability,
            system_name=rules.name_of(system),
            system_short=rules.short_of(system),
            scope=band or "_(scope band)_",
            scope_means=rules.scope_describe(band) if band else "_(what they can plausibly reach)_",
            crossing_note=crossing,
        ),
    )
    print(f"wrote {path.relative_to(repo_root())} ({rules.short_of(system)}"
          + (f", scope '{band}'" if band else "") + ")")
    print("Fill in the deeds, the reputation, and the gap between them. Set availability deliberately —")
    print("the GM honours it in every other campaign in this world.")
    if band:
        print(f"\nScope '{band}' is what crosses to another ruleset; the level does not. "
              f"See `world.py crossing`.")
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


CROSSING_NOTE = """\
# What crosses between the rulesets, and what does not

A world in this framework is **system-neutral**. It records what happened, when, who did it
and what changed — never a level, a DC, an AC or a stat block. That is not tidiness; it is
the only version of a shared world that survives being read by two games.

## What crosses

| Crosses | Why |
|---|---|
| Events, dates, causes and consequences | A tower falling is a tower falling in any ruleset |
| People, factions, places and their standing | Who holds the harbour does not depend on the dice |
| Debts, titles, oaths, reputations, grudges | All fiction |
| Items *as objects with histories* | "The blade Roderic carried" is a story; "+1 longsword" is not |
| **Scope** — the band of the world a character could reach | See below |

## What does not cross

| Does not cross | Why not |
|---|---|
| Character levels, one for one | A level is a position on one game's power curve. The curves differ in shape, not just scale. |
| Stat blocks | A CR 5 monster and a level 5 Pathfinder creature are not the same creature, and neither set of numbers survives the trip. |
| DCs | Pathfinder DCs rise with level; D&D's do not. A "DC 20 lock" means something different in each game. |
| Treasure, piece for piece | Pathfinder publishes a per-level treasure allotment; D&D 2024's equivalent is not open content and its economy is shaped differently. Electrum exists in one game and not the other. |
| Encounter budgets | One is a per-party budget with a party-size adjustment; the other is strictly per character. |

## Scope: the one translation this framework will do

Four bands, named for the size of the thing a character can plausibly threaten or protect:

    local      a farmstead, a village, a city ward
    regional   a city and the land that feeds it
    national   a kingdom, a region, the doorstep of another plane
    worldly    the world itself, or the order of the planes

D&D 2024 publishes these as its four tiers of play and says in as many words that they
carry no rules — they describe how big the stakes get. That is exactly what a shared world
needs. Pathfinder publishes no tier table, so the same 1-4 / 5-10 / 11-16 / 17-20 split is
**this framework's own convention** there, and `python3 tools/rules.py bands` says so.

    python3 tools/world.py convert --level 7 --from pf2e --to dnd5e

returns a band and a level *range*, never a single number, and lists what it refuses to do.

## Writing an entry that survives both readers

- Name the deed, not the die roll. "Broke the siege" rather than "rolled a critical success".
- Name the obstacle's nature, not its numbers. "A warded door nobody local could open"
  rather than "a DC 28 Thievery check".
- Name what an item *is* and *did*, not its bonus.
- Record the scope band. A later campaign in another ruleset reads that to know whether
  this was a village matter or a kingdom one.
"""


def world_calendar_name(world: str) -> str | None:
    """The calendar this world uses: its own CALENDAR block, else the name it declares.

    A world owns its calendar, so every campaign in it has to share one. This is the
    single place that answers "which one", for `link` to adopt and for `validate.py` to
    check against.
    """
    own = rules.load_world_calendar(world)
    if own:
        return own
    path = world_dir(world) / "CALENDAR.md"
    if not path.exists():
        return None
    raw = pf2e.read_field(path.read_text(encoding="utf-8"), "Calendar in use")
    if not raw:
        return None
    rules.load_all()
    # The field is prose ("golarion (Absalom Reckoning)"), so match the registered names
    # longest-first — otherwise a name that is a prefix of another would win wrongly.
    for name in sorted(rules.CALENDARS, key=len, reverse=True):
        if name in raw.lower():
            return name
    return None


def cmd_crossing(args: argparse.Namespace) -> int:
    print(CROSSING_NOTE)
    if args.world:
        systems = rules.for_world(args.world)
        if not systems:
            print(f"\nNo campaign is linked to worlds/{args.world} yet.")
        else:
            print(f"\nworlds/{args.world} currently hosts: "
                  + ", ".join(rules.short_of(x) for x in systems))
            if len(systems) > 1:
                print("It is a cross-system world, so every promotion has to survive both readers.")
    return 0


def cmd_systems(args: argparse.Namespace) -> int:
    """Which rulesets play in this world, and what that means for its chronicle."""
    wdir = world_dir(args.world)
    if not wdir.is_dir():
        raise WorldError(f"no world at {wdir}")
    systems = rules.for_world(args.world)
    print(f"# worlds/{args.world} — rulesets in play")
    print()
    if not systems:
        print("No campaign is linked to this world yet. It is system-neutral and stays that way;")
        print("linking a campaign of any supported ruleset is all it takes.")
    else:
        for sid in systems:
            camps = []
            croot = repo_root() / "campaigns"
            for d in sorted(croot.iterdir()) if croot.exists() else []:
                cm = d / "CAMPAIGN.md"
                if not d.is_dir() or not cm.exists():
                    continue
                if (rules.world_of_campaign(d.name) or "").lower() == args.world.lower():
                    if rules.for_campaign(d.name) == sid:
                        start = pf2e.read_field(cm.read_text(encoding="utf-8"), "Start date") or "?"
                        camps.append(f"{d.name} (from {start})")
            print(f"- **{rules.name_of(sid)}** — {', '.join(camps) or 'no campaign'}")
        if len(systems) > 1:
            print()
            print("This is a **cross-system world**. The chronicle is read by both, so entries")
            print("carry a `System:` line saying which game wrote them and a `Scope:` line saying")
            print("how far the event reached. Neither game's numbers go into the shared layer.")
            print("`python3 tools/world.py crossing` is the full statement of what crosses.")

    print()
    cal = rules.load_world_calendar(args.world)
    if cal:
        c = rules.CALENDARS[cal]
        print(f"Calendar: **{cal}** — {len(c['months'])} months, "
              f"{sum(d for _, d in c['months'])} days a year, era {c['era'] or '(none)'}")
        print("  Defined by this world in CALENDAR.md, so every ruleset reads its dates identically.")
        return 0

    # No block of its own. The prose field still says which built-in it uses, and naming
    # one is enough for a shared world — what matters is that there is a single answer.
    cpath = wdir / "CALENDAR.md"
    declared = None
    if cpath.exists():
        raw = pf2e.read_field(cpath.read_text(encoding="utf-8"), "Calendar in use")
        if raw:
            for name in rules.CALENDARS:
                if name in raw.lower():
                    declared = name
                    break
    if declared:
        c = rules.CALENDARS[declared]
        print(f"Calendar: **{declared}** (a built-in, named in CALENDAR.md) — "
              f"{len(c['months'])} months, {sum(d for _, d in c['months'])} days a year, "
              f"era {c['era'] or '(none)'}")
        print("  One calendar for the whole world, which is what a shared timeline needs.")
    else:
        print("Calendar: CALENDAR.md names none, so dates are parsed against every calendar the")
        print("  rulesets ship with. Name one in `Calendar in use:`, or define this world's own")
        print("  in the CALENDAR block — a shared timeline needs a single answer.")
    return 0


def cmd_convert(args: argparse.Namespace) -> int:
    out = rules.translate_level(args.level, source=args.source, target=args.target)
    if args.json:
        print(json.dumps(out, indent=2))
        return 0
    print(f"{rules.short_of(out['source_system'])} level {out['source_level']} "
          f"→ scope band **{out['band']}**")
    print(f"  which is: {out['band_means']}")
    print(f"  in {rules.short_of(out['target_system'])}, that band is "
          f"levels {out['target_levels'][0]}-{out['target_levels'][1]}")
    print()
    print("A range, not a conversion. This deliberately will not:")
    for r in out["refuses"]:
        print(f"  - {r}")
    print()
    print(f"Source: {out['source_note']}")
    return 0


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
    p.add_argument("--scope", default=None, choices=list(rules.SCOPE_NAMES),
                   help="how far this event reached: the one field that crosses rulesets")
    p.add_argument("--level", type=int, default=None,
                   help="the characters' level, used to derive --scope if it is not given")
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

    p = sub.add_parser("systems", help="which rulesets play in this world, and its calendar")
    p.add_argument("world")

    p = sub.add_parser("crossing", help="what crosses between the rulesets, and what does not")
    p.add_argument("--world", default=None)

    p = sub.add_parser("history", help="the world's living history, date-gated")
    p.add_argument("world")
    p.add_argument("--date", default=None,
                   help="read as of this in-world date; omit for the whole book (not gated)")

    p = sub.add_parser("history-add", help="append a chapter to the living history")
    p.add_argument("--world", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--span", required=True,
                   help="the range it covers, e.g. '4726-4729 AR'. Its END is what the gate reads")
    p.add_argument("--certainty", required=True, choices=list(CERTAINTIES))
    p.add_argument("--body", required=True, help="the prose; as long as it earns")
    p.add_argument("--sources", default=None, help="free text, e.g. 'the Cove's own records'")
    p.add_argument("--campaign", default=None,
                   help="a campaign that contributed; its ruleset is added automatically")
    p.add_argument("--allow-numbers", action="store_true",
                   help="permit a number that is an in-world quantity, not a rules value")
    p.add_argument("--yes", action="store_true", help="skip the confirmation prompt")

    p = sub.add_parser("narrative", help="the thorough per-ruleset narrative for one campaign")
    p.add_argument("--campaign", required=True)
    p.add_argument("--world", default=None)
    p.add_argument("--force", action="store_true", help="overwrite an existing file")

    p = sub.add_parser("universe", help="the layer above worlds: what is true across them")
    p.add_argument("--init", action="store_true", help="write worlds/UNIVERSE.md")
    p.add_argument("--force", action="store_true")

    p = sub.add_parser("convert", help="what a level in one ruleset means in the other")
    p.add_argument("--level", type=int, required=True)
    p.add_argument("--from", dest="source", required=True)
    p.add_argument("--to", dest="target", required=True)
    p.add_argument("--json", action="store_true")
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
        "systems": cmd_systems,
        "crossing": cmd_crossing,
        "convert": cmd_convert,
        "history": cmd_history,
        "history-add": cmd_history_add,
        "narrative": cmd_narrative,
        "universe": cmd_universe,
    }
    try:
        return fns[args.cmd](args)
    except WorldError as exc:
        print(f"world.py: {exc}", file=sys.stderr)
        return 2
    except rules.RulesError as exc:
        print(f"world.py: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
