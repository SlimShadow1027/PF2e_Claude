#!/usr/bin/env python3
"""roll.py — the only place dice are rolled in this repository.

Every die face in this framework comes out of `random.SystemRandom` here, and every
roll is appended to `campaigns/<slug>/logs/rolls.jsonl` so the whole campaign can be
audited after the fact. Private and secret rolls are rolled exactly like public ones;
what changes is only the line printed to chat.

Standard library only. See system/04-dice-protocol.md for the rules of engagement and
tools/README.md for the CLI surface.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
import tempfile
import datetime as _dt
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Iterable, Sequence

TOOL_VERSION = "1.0.0"
LOG_SCHEMA_VERSION = 1

_RNG = random.SystemRandom()

# --------------------------------------------------------------------------------------
# Paths and small filesystem helpers (shared by the other tools in this directory)
# --------------------------------------------------------------------------------------


def repo_root() -> Path:
    """The repository root, derived from this file's location rather than the cwd."""
    return Path(__file__).resolve().parent.parent


def campaign_dir(slug: str) -> Path:
    return repo_root() / "campaigns" / slug


def world_dir(slug: str) -> Path:
    return repo_root() / "worlds" / slug


def list_campaigns() -> list[str]:
    root = repo_root() / "campaigns"
    if not root.is_dir():
        return []
    # A leading "_" marks a folder that is not a campaign — parked pitches, notes for a
    # campaign not yet started. Same convention as new_campaign.py and the bestiary check.
    return sorted(p.name for p in root.iterdir()
                  if p.is_dir() and not p.name.startswith(".") and not p.name.startswith("_"))


def atomic_write(path: Path, text: str) -> None:
    """Write `text` to `path` via a temp file + rename, so a crash never truncates state."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-", suffix=path.suffix)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class DiceError(ValueError):
    """A dice expression that cannot be parsed, or an impossible roll request."""


# --------------------------------------------------------------------------------------
# Notation
# --------------------------------------------------------------------------------------

# NdM with optional keep-highest / keep-lowest and a single reroll-at-or-below flag.
#   3d6          4d6kh3       2d20kh1      2d20kl1      1d20r1      2d8kl1r2
_DICE_RE = re.compile(r"^(\d*)d(\d+)((?:(?:kh|kl)\d*|r\d+)*)$", re.IGNORECASE)
_MOD_RE = re.compile(r"(kh|kl|r)(\d*)", re.IGNORECASE)
_TERM_SPLIT_RE = re.compile(r"([+-])")

MAX_DICE_PER_GROUP = 1000
MAX_FACES = 1000


@dataclass
class DiceGroup:
    """One NdM group inside an expression, with every face it actually produced."""

    expr: str
    count: int
    faces: int
    rolls: list[int] = field(default_factory=list)  # every face rolled, in order, after rerolls
    kept: list[int] = field(default_factory=list)
    dropped: list[int] = field(default_factory=list)
    rerolled: list[dict[str, int]] = field(default_factory=list)  # {"from": 1, "to": 14}
    sign: int = 1
    keep: str | None = None  # "kh" | "kl" | None
    keep_n: int = 0

    @property
    def subtotal(self) -> int:
        return self.sign * sum(self.kept)


@dataclass
class RollResult:
    """The outcome of one expression: the groups, the flat modifier, and the total."""

    expr: str
    groups: list[DiceGroup]
    modifier: int
    total: int

    @property
    def natural(self) -> int | None:
        """The 'check die' face: the kept value of the first d20 group, else the first group."""
        for g in self.groups:
            if g.faces == 20 and g.kept:
                return g.kept[0]
        for g in self.groups:
            if g.kept:
                return g.kept[0]
        return None

    @property
    def has_d20(self) -> bool:
        return any(g.faces == 20 for g in self.groups)

    def dice_json(self) -> list[dict[str, Any]]:
        out = []
        for g in self.groups:
            out.append(
                {
                    "expr": g.expr,
                    "sign": g.sign,
                    "count": g.count,
                    "faces": g.faces,
                    "rolls": list(g.rolls),
                    "kept": list(g.kept),
                    "dropped": list(g.dropped),
                    "rerolled": list(g.rerolled),
                }
            )
        return out

    def faces_line(self) -> str:
        """`[14] +13` style detail for the chat line."""
        chunks = []
        for g in self.groups:
            shown = ",".join(str(v) for v in g.kept)
            if g.dropped:
                shown += " (dropped " + ",".join(str(v) for v in g.dropped) + ")"
            prefix = "-" if g.sign < 0 else ""
            chunks.append(f"{prefix}[{shown}]")
        if self.modifier:
            chunks.append(f"{self.modifier:+d}")
        return " ".join(chunks) if chunks else "[]"


def _roll_die(faces: int) -> int:
    if faces < 1:
        raise DiceError(f"a d{faces} has no faces")
    return _RNG.randint(1, faces)


def _parse_group(token: str, sign: int) -> DiceGroup:
    m = _DICE_RE.match(token)
    if not m:
        raise DiceError(f"cannot parse dice term {token!r}")
    count = int(m.group(1)) if m.group(1) else 1
    faces = int(m.group(2))
    if count < 1:
        raise DiceError(f"{token!r} rolls fewer than one die")
    if count > MAX_DICE_PER_GROUP:
        raise DiceError(f"{token!r} rolls more than {MAX_DICE_PER_GROUP} dice")
    if faces < 1 or faces > MAX_FACES:
        raise DiceError(f"{token!r} has an implausible die size")

    keep: str | None = None
    keep_n = 0
    reroll_at_or_below = 0
    for kind, num in _MOD_RE.findall(m.group(3) or ""):
        kind = kind.lower()
        if kind in ("kh", "kl"):
            if keep is not None:
                raise DiceError(f"{token!r} has more than one keep modifier")
            keep = kind
            keep_n = int(num) if num else 1
            if keep_n < 1 or keep_n > count:
                raise DiceError(f"{token!r} keeps {keep_n} of {count} dice")
        else:  # "r"
            reroll_at_or_below = int(num) if num else 1
            if reroll_at_or_below >= faces:
                raise DiceError(f"{token!r} would reroll every possible face")

    g = DiceGroup(expr=token, count=count, faces=faces, sign=sign, keep=keep, keep_n=keep_n)
    values: list[int] = []
    for _ in range(count):
        v = _roll_die(faces)
        g.rolls.append(v)
        if reroll_at_or_below and v <= reroll_at_or_below:
            nv = _roll_die(faces)
            g.rolls.append(nv)
            g.rerolled.append({"from": v, "to": nv})
            v = nv
        values.append(v)

    if keep == "kh":
        order = sorted(range(len(values)), key=lambda i: values[i], reverse=True)
    elif keep == "kl":
        order = sorted(range(len(values)), key=lambda i: values[i])
    else:
        order = list(range(len(values)))
        keep_n = len(values)
    kept_idx = set(order[:keep_n])
    g.kept = [values[i] for i in order[:keep_n]]
    g.dropped = [values[i] for i in range(len(values)) if i not in kept_idx]
    return g


def roll_expression(expr: str) -> RollResult:
    """Roll a dice expression such as `1d20+13`, `2d20kh1+9`, `2d6+1d4-1`."""
    if expr is None:
        raise DiceError("no expression given")
    text = str(expr).replace(" ", "")
    if not text:
        raise DiceError("empty expression")
    if text[0] not in "+-":
        text = "+" + text
    parts = [p for p in _TERM_SPLIT_RE.split(text) if p != ""]
    if len(parts) % 2 != 0:
        raise DiceError(f"cannot parse expression {expr!r}")

    groups: list[DiceGroup] = []
    modifier = 0
    for i in range(0, len(parts), 2):
        sign = -1 if parts[i] == "-" else 1
        token = parts[i + 1]
        if not token:
            raise DiceError(f"dangling operator in {expr!r}")
        if "d" in token.lower():
            groups.append(_parse_group(token, sign))
        else:
            if not re.fullmatch(r"\d+", token):
                raise DiceError(f"cannot parse term {token!r} in {expr!r}")
            modifier += sign * int(token)

    total = modifier + sum(g.subtotal for g in groups)
    return RollResult(expr=str(expr), groups=groups, modifier=modifier, total=total)


def to_fortune(expr: str) -> str:
    """Rewrite the leading `1d20` of an expression as `2d20kh1` (fortune)."""
    return _rewrite_d20(expr, "2d20kh1")


def to_misfortune(expr: str) -> str:
    return _rewrite_d20(expr, "2d20kl1")


def _rewrite_d20(expr: str, replacement: str) -> str:
    text = str(expr).replace(" ", "")
    new, n = re.subn(r"(?<![\dkhl])1?d20(?!\d)", replacement, text, count=1, flags=re.IGNORECASE)
    if n == 0:
        raise DiceError(f"{expr!r} has no 1d20 to convert")
    return new


# --------------------------------------------------------------------------------------
# Degrees of success
# --------------------------------------------------------------------------------------

DEGREES = ("critical failure", "failure", "success", "critical success")
DEGREE_LABELS = ("CRITICAL FAILURE", "FAILURE", "SUCCESS", "CRITICAL SUCCESS")


@dataclass
class Degree:
    index: int
    unadjusted_index: int
    shift: int
    natural: int | None

    @property
    def name(self) -> str:
        return DEGREES[self.index]

    @property
    def label(self) -> str:
        return DEGREE_LABELS[self.index]

    @property
    def unadjusted_name(self) -> str:
        return DEGREES[self.unadjusted_index]


def degree_of_success(total: int, dc: int, natural: int | None) -> Degree:
    """PF2e degrees of success, with the natural-20 / natural-1 one-step shift.

    Source: GM Core / Player Core "Degrees of Success" — verified against the Foundry VTT
    PF2e implementation (src/module/system/degree-of-success.ts), which cites
    https://2e.aonprd.com/Rules.aspx?ID=552 : base degree from total vs DC, then a single
    step up on a natural 20 and a single step down on a natural 1, clamped to the range.
    """
    if total - dc >= 10:
        base = 3
    elif dc - total >= 10:
        base = 0
    elif total >= dc:
        base = 2
    else:
        base = 1
    shift = 0
    if natural == 20:
        shift = 1
    elif natural == 1:
        shift = -1
    idx = max(0, min(3, base + shift))
    return Degree(index=idx, unadjusted_index=base, shift=idx - base, natural=natural)


# --------------------------------------------------------------------------------------
# The audit log
# --------------------------------------------------------------------------------------


def log_path_for(campaign: str | None, explicit: str | None) -> Path | None:
    if explicit:
        return Path(explicit).expanduser()
    if campaign:
        return campaign_dir(campaign) / "logs" / "rolls.jsonl"
    return None


def _next_seq(path: Path) -> int:
    """Read the last line's seq so the log is a stable append-only sequence."""
    if not path.exists() or path.stat().st_size == 0:
        return 1
    try:
        with path.open("rb") as fh:
            fh.seek(0, os.SEEK_END)
            size = fh.tell()
            window = min(size, 8192)
            fh.seek(size - window)
            tail = fh.read().decode("utf-8", "replace").strip().splitlines()
        for line in reversed(tail):
            line = line.strip()
            if not line:
                continue
            try:
                return int(json.loads(line).get("seq", 0)) + 1
            except (ValueError, AttributeError):
                continue
    except OSError:
        pass
    return 1


def append_log(path: Path | None, record: dict[str, Any]) -> dict[str, Any]:
    """Append one record. The log is append-only: nothing here ever rewrites a past line."""
    if path is None:
        return record
    path.parent.mkdir(parents=True, exist_ok=True)
    record = dict(record)
    record.setdefault("seq", _next_seq(path))
    ordered = {"seq": record.pop("seq"), "ts": record.pop("ts", utc_now())}
    ordered.update(record)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(ordered, ensure_ascii=False, sort_keys=False) + "\n")
        fh.flush()
        os.fsync(fh.fileno())
    return ordered


# --------------------------------------------------------------------------------------
# Roll kinds
# --------------------------------------------------------------------------------------

TRANSPARENCY_MODES = ("glass", "standard", "mystery")


def _shown(secret: bool, private: bool, transparency: str) -> bool:
    """Whether the number itself is shown to the player, given the campaign's mode.

    `glass` shows everything. `standard` hides `secret`-trait checks but shows enemy
    numbers. `mystery` hides both. The roll happens either way; only the display changes.
    """
    if transparency == "glass":
        return True
    if secret:
        return False
    if private:
        return transparency != "mystery"
    return True


@dataclass
class Roll:
    """One completed roll: the dice, the interpretation, and the two renderings of it."""

    kind: str
    result: RollResult
    label: str | None = None
    actor: str | None = None
    dc: int | None = None
    degree: Degree | None = None
    secret: bool = False
    private: bool = False
    shown: bool = True
    transparency: str = "standard"
    tags: list[str] = field(default_factory=list)
    damage_type: str | None = None
    crit: bool = False
    map_step: int | None = None
    fortune: bool = False
    misfortune: bool = False
    extra: dict[str, Any] = field(default_factory=dict)
    logged_seq: int | None = None

    # -- rendering ---------------------------------------------------------------

    def _who(self) -> str:
        return f"{self.actor} — " if self.actor else ""

    def public_line(self) -> str:
        """The one compact line printed to chat. Redacted when the number is withheld."""
        if not self.shown:
            tag = "secret" if self.secret else "private"
            what = self.label or self.kind
            who = f"{self.actor} " if self.actor and not self.secret else ""
            return f"🎲 ({tag}) {who}{what} — rolled, result withheld"
        return self.detail_line()

    def detail_line(self) -> str:
        """The full line, always written to the log and shown when display allows."""
        head = f"🎲 {self._who()}{self.label or self.kind}: {self.result.expr}"
        body = f" → {self.result.faces_line()} = {self.result.total}"
        tail = ""
        if self.kind == "damage":
            if self.crit:
                base = self.extra.get("base_total")
                body = f" → {self.result.faces_line()} = {base} x2 = {self.result.total}"
            tail = f" {self.damage_type}" if self.damage_type else ""
            if self.crit:
                tail += " (critical)"
        elif self.dc is not None and self.degree is not None:
            vs = self.extra.get("dc_label") or "DC"
            tail = f" vs {vs} {self.dc} → {self.degree.label}"
            if self.degree.shift:
                nat = self.degree.natural
                word = "upgraded" if self.degree.shift > 0 else "downgraded"
                tail += f"  [natural {nat}: {word} from {self.degree.unadjusted_name.upper()}]"
        elif self.dc is not None:
            ok = self.result.total >= self.dc
            tail = f" vs DC {self.dc} → {'SUCCESS' if ok else 'FAILURE'}"
        if self.map_step:
            tail += f"  (MAP step {self.map_step})"
        if self.fortune:
            tail += "  [fortune]"
        if self.misfortune:
            tail += "  [misfortune]"
        return head + body + tail

    # -- logging -----------------------------------------------------------------

    def log_record(self, campaign: str | None, session: int | None, checkpoint: int | None) -> dict[str, Any]:
        rec: dict[str, Any] = {
            "ts": utc_now(),
            "schema": LOG_SCHEMA_VERSION,
            "tool_version": TOOL_VERSION,
            "rng": "random.SystemRandom",
            "campaign": campaign,
            "session": session,
            "checkpoint": checkpoint,
            "kind": self.kind,
            "actor": self.actor,
            "label": self.label,
            "expr": self.result.expr,
            "dice": self.result.dice_json(),
            "modifier": self.result.modifier,
            "natural": self.result.natural,
            "total": self.result.total,
            "dc": self.dc,
            "secret": self.secret,
            "private": self.private,
            "shown": self.shown,
            "transparency": self.transparency,
            "tags": list(self.tags),
            "damage_type": self.damage_type,
            "crit": self.crit,
            "map_step": self.map_step,
            "fortune": self.fortune,
            "misfortune": self.misfortune,
            "detail": self.detail_line(),
        }
        if self.degree is not None:
            rec.update(
                {
                    "degree": self.degree.name,
                    "degree_index": self.degree.index,
                    "unadjusted_degree": self.degree.unadjusted_name,
                    "degree_shift": self.degree.shift,
                    "nat20": self.degree.natural == 20,
                    "nat1": self.degree.natural == 1,
                }
            )
        else:
            rec.update({"degree": None, "degree_index": None})
        if self.extra:
            rec["extra"] = dict(self.extra)
        return rec

    def to_json(self) -> dict[str, Any]:
        d = {
            "kind": self.kind,
            "expr": self.result.expr,
            "actor": self.actor,
            "label": self.label,
            "natural": self.result.natural,
            "total": self.result.total,
            "dc": self.dc,
            "degree": self.degree.name if self.degree else None,
            "degree_shift": self.degree.shift if self.degree else 0,
            "shown": self.shown,
            "secret": self.secret,
            "private": self.private,
            "dice": self.result.dice_json(),
            "line": self.public_line(),
        }
        if self.logged_seq is not None:
            d["seq"] = self.logged_seq
        return d


def make_roll(
    kind: str,
    expr: str,
    *,
    dc: int | None = None,
    label: str | None = None,
    actor: str | None = None,
    secret: bool = False,
    private: bool = False,
    transparency: str = "standard",
    tags: Sequence[str] = (),
    damage_type: str | None = None,
    crit: bool = False,
    map_step: int | None = None,
    fortune: bool = False,
    misfortune: bool = False,
    extra: dict[str, Any] | None = None,
    compute_degree: bool = True,
) -> Roll:
    """Roll one expression and interpret it. Nothing here consults an expected outcome."""
    if fortune and misfortune:
        raise DiceError("a roll cannot be both fortune and misfortune")
    use = expr
    if fortune:
        use = to_fortune(expr)
    elif misfortune:
        use = to_misfortune(expr)

    result = roll_expression(use)

    extra = dict(extra or {})
    if kind == "damage" and crit:
        # PF2e criticals double the whole damage roll, modifiers included.
        # Source: Player Core, "Critical Hits" — verified in system/12-rules-quick-reference.md.
        extra["base_total"] = result.total
        result = RollResult(
            expr=f"({result.expr}) x2",
            groups=result.groups,
            modifier=result.modifier,
            total=result.total * 2,
        )

    degree = None
    if dc is not None and compute_degree:
        degree = degree_of_success(result.total, dc, result.natural)

    r = Roll(
        kind=kind,
        result=result,
        label=label,
        actor=actor,
        dc=dc,
        degree=degree,
        secret=secret,
        private=private,
        transparency=transparency,
        tags=list(tags),
        damage_type=damage_type,
        crit=crit,
        map_step=map_step,
        fortune=fortune,
        misfortune=misfortune,
        extra=extra,
    )
    r.shown = _shown(secret, private, transparency)
    return r


# --------------------------------------------------------------------------------------
# Random tables
# --------------------------------------------------------------------------------------

_TABLE_ENTRY_RE = re.compile(r"^\s*(?:[-*]\s*)?(\d+)(?:\s*[-–]\s*(\d+))?\s*[.)|]\s*(.+?)\s*$")
_PIPE_ENTRY_RE = re.compile(r"^\s*\|\s*(\d+)(?:\s*[-–]\s*(\d+))?\s*\|\s*(.+?)\s*\|\s*$")


def parse_tables(text: str) -> dict[str, list[tuple[int, int, str]]]:
    """Pull every numbered table out of a Markdown file, keyed by its heading.

    An entry is `N. text`, `N-M. text`, or a two-column pipe row `| N | text |`.
    The die size is the highest upper bound present, so a d100 table works unchanged.
    """
    tables: dict[str, list[tuple[int, int, str]]] = {}
    current: str | None = None
    for line in text.splitlines():
        h = re.match(r"^\s{0,3}(#{2,6})\s+(.*?)\s*#*\s*$", line)
        if h:
            current = h.group(2).strip()
            continue
        if current is None:
            continue
        m = _PIPE_ENTRY_RE.match(line) or _TABLE_ENTRY_RE.match(line)
        if not m:
            continue
        lo = int(m.group(1))
        hi = int(m.group(2)) if m.group(2) else lo
        entry = m.group(3).strip().strip("|").strip()
        if not entry or set(entry) <= set("-: "):
            continue
        tables.setdefault(current, []).append((lo, hi, entry))
    return {k: v for k, v in tables.items() if v}


def find_table(tables: dict[str, list[tuple[int, int, str]]], name: str) -> tuple[str, list[tuple[int, int, str]]]:
    want = name.strip().lower()
    for k, v in tables.items():
        if k.lower() == want:
            return k, v
    hits = [(k, v) for k, v in tables.items() if want in k.lower()]
    if len(hits) == 1:
        return hits[0]
    if len(hits) > 1:
        raise DiceError(f"{name!r} matches several tables: " + ", ".join(k for k, _ in hits))
    raise DiceError(f"no table named {name!r}. Available: " + ", ".join(sorted(tables)) or "none")


def roll_on_table(entries: list[tuple[int, int, str]]) -> tuple[int, str, int]:
    die = max(hi for _, hi, _ in entries)
    value = _roll_die(die)
    for lo, hi, text in entries:
        if lo <= value <= hi:
            return value, text, die
    return value, "(no entry matched — the table has a gap)", die


# --------------------------------------------------------------------------------------
# Initiative
# --------------------------------------------------------------------------------------

def _initiative_side(name: str, party: Iterable[str]) -> str:
    return "party" if name in set(party) else "adversary"


def order_initiative(rolls: list[Roll], sides: dict[str, str], tiebreak_rolls: dict[str, int]) -> list[dict[str, Any]]:
    """Sort an initiative table.

    Higher total acts first. On a tie between a party member and an adversary the
    adversary acts first (Player Core, "Roll Initiative"; verified against the Foundry
    VTT PF2e implementation, src/module/encounter/document.ts `_sortCombatants`, where
    an NPC's tiebreak priority of 1 sorts ahead of a player-owned actor's 2).
    Ties within one side are broken by a real d20 roll-off, logged like any other roll.
    """
    rows = []
    for r in rolls:
        name = r.actor or "?"
        rows.append(
            {
                "actor": name,
                "side": sides.get(name, "adversary"),
                "total": r.result.total,
                "natural": r.result.natural,
                "tiebreak": tiebreak_rolls.get(name, 0),
            }
        )
    rows.sort(key=lambda row: (-row["total"], 0 if row["side"] == "adversary" else 1, -row["tiebreak"], row["actor"]))
    for i, row in enumerate(rows, start=1):
        row["order"] = i
    return rows


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------


def _emit(rolls: list[Roll], args: argparse.Namespace, log: Path | None) -> int:
    session = getattr(args, "session", None)
    checkpoint = getattr(args, "checkpoint", None)
    for r in rolls:
        rec = append_log(log, r.log_record(getattr(args, "campaign", None), session, checkpoint))
        r.logged_seq = rec.get("seq")
    if getattr(args, "json", False):
        print(json.dumps([r.to_json() for r in rolls], indent=2))
    else:
        for r in rolls:
            print(r.public_line())
        if getattr(args, "gm", False):
            hidden = [r for r in rolls if not r.shown]
            if hidden:
                print("\n> **GM-ONLY** — the withheld numbers:")
                for r in hidden:
                    print("> " + r.detail_line())
    if log is None and not getattr(args, "quiet", False):
        print("(not logged: pass --campaign <slug> or --log <path> to write to the audit log)", file=sys.stderr)
    return 0


def _common(p: argparse.ArgumentParser) -> None:
    p.add_argument("--campaign", help="campaign slug; the roll is logged to its logs/rolls.jsonl")
    p.add_argument("--log", help="explicit log path (overrides --campaign)")
    p.add_argument("--transparency", choices=TRANSPARENCY_MODES, default="standard")
    p.add_argument("--session", type=int, default=None, help="session number, recorded in the log")
    p.add_argument("--checkpoint", type=int, default=None, help="checkpoint number, recorded in the log")
    p.add_argument("--tag", action="append", default=[], help="free-form log tag; repeatable")
    p.add_argument("--json", action="store_true", help="machine-readable output")
    p.add_argument("--gm", action="store_true", help="also print withheld numbers in a GM-ONLY block")
    p.add_argument("--quiet", action="store_true", help="suppress the not-logged warning")


def _visibility(p: argparse.ArgumentParser) -> None:
    p.add_argument("--secret", action="store_true", help="secret trait: rolled, number withheld")
    p.add_argument("--private", action="store_true", help="GM-side roll: shown per transparency mode")


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="roll.py",
        description="Roll real dice and log them. Nothing in this repository invents a die result.",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name: str, help_: str) -> argparse.ArgumentParser:
        p = sub.add_parser(name, help=help_)
        _common(p)
        return p

    p = add("check", "a d20 check against a DC")
    p.add_argument("expr", nargs="+", help="one or more expressions; several roll in one call")
    p.add_argument("--dc", type=int, required=False)
    p.add_argument("--label")
    p.add_argument("--actor", action="append", default=[], help="repeat to name each expression's roller")
    p.add_argument("--map", dest="map_step", type=int, default=0, help="multiple attack penalty step reached")
    p.add_argument("--dc-label", default=None, help="what the DC is, e.g. 'AC'")
    _visibility(p)

    p = add("save", "a saving throw")
    p.add_argument("expr", nargs="+")
    p.add_argument("--dc", type=int, required=True)
    p.add_argument("--label")
    p.add_argument("--actor", action="append", default=[])
    _visibility(p)

    p = add("damage", "a damage roll")
    p.add_argument("expr", nargs="+")
    p.add_argument("--crit", action="store_true", help="double the whole roll, modifiers included")
    p.add_argument("--type", dest="dtype", default=None)
    p.add_argument("--label")
    p.add_argument("--actor", action="append", default=[])
    _visibility(p)

    p = add("flat", "a flat check (no degrees of success)")
    p.add_argument("dc", type=int)
    p.add_argument("--label")
    p.add_argument("--actor")
    _visibility(p)

    p = add("recovery", "a recovery check while dying")
    p.add_argument("--dying", type=int, required=True)
    p.add_argument("--bonus", type=int, default=0, help="modifier to the recovery check, if any")
    p.add_argument("--actor")
    p.add_argument("--label")
    _visibility(p)

    p = add("init", "roll initiative for several actors and return the ordered table")
    p.add_argument("--actors", required=True, help="comma list, each 'name' or 'name:+7'")
    p.add_argument("--party", default="", help="comma list of names on the party side (for tie-breaks)")
    p.add_argument("--default-mod", type=int, default=0)
    _visibility(p)

    p = add("fortune", "reroll keeping the higher d20 (Hero Point, fortune effects)")
    p.add_argument("expr")
    p.add_argument("--dc", type=int)
    p.add_argument("--label")
    p.add_argument("--actor")
    p.add_argument("--dc-label", default=None)
    _visibility(p)

    p = add("misfortune", "reroll keeping the lower d20 (misfortune effects)")
    p.add_argument("expr")
    p.add_argument("--dc", type=int)
    p.add_argument("--label")
    p.add_argument("--actor")
    p.add_argument("--dc-label", default=None)
    _visibility(p)

    p = add("table", "roll on a numbered table in a Markdown file")
    p.add_argument("file")
    p.add_argument("name")
    p.add_argument("--count", type=int, default=1)
    p.add_argument("--list", action="store_true", help="list the tables in the file and exit")
    _visibility(p)

    p = add("batch", "roll a heterogeneous batch described as JSON")
    p.add_argument("--json-arg", dest="payload", help="a JSON array of roll specs")
    p.add_argument("--json-file", dest="payload_file", help="a file holding that array")

    p = add("expr", "roll a bare expression with no DC and no interpretation")
    p.add_argument("expression", nargs="+")
    p.add_argument("--label")
    p.add_argument("--actor")
    _visibility(p)

    return ap


def _actors_for(args: argparse.Namespace, n: int) -> list[str | None]:
    given = list(getattr(args, "actor", []) or [])
    if not given:
        return [None] * n
    if len(given) == 1:
        return [given[0]] * n
    if len(given) != n:
        raise DiceError(f"{len(given)} --actor values for {n} expressions")
    return given  # type: ignore[return-value]


def cmd_check(args: argparse.Namespace, kind: str = "check") -> list[Roll]:
    actors = _actors_for(args, len(args.expr))
    out = []
    for expr, actor in zip(args.expr, actors):
        out.append(
            make_roll(
                kind,
                expr,
                dc=args.dc,
                label=args.label,
                actor=actor,
                secret=args.secret,
                private=args.private,
                transparency=args.transparency,
                tags=args.tag,
                map_step=getattr(args, "map_step", 0) or None,
                extra={"dc_label": getattr(args, "dc_label", None)} if getattr(args, "dc_label", None) else None,
            )
        )
    return out


def cmd_damage(args: argparse.Namespace) -> list[Roll]:
    actors = _actors_for(args, len(args.expr))
    return [
        make_roll(
            "damage",
            expr,
            label=args.label,
            actor=actor,
            secret=args.secret,
            private=args.private,
            transparency=args.transparency,
            tags=args.tag,
            damage_type=args.dtype,
            crit=args.crit,
        )
        for expr, actor in zip(args.expr, actors)
    ]


def cmd_flat(args: argparse.Namespace) -> list[Roll]:
    return [
        make_roll(
            "flat",
            "1d20",
            dc=args.dc,
            label=args.label or f"Flat check DC {args.dc}",
            actor=args.actor,
            secret=args.secret,
            private=args.private,
            transparency=args.transparency,
            tags=args.tag,
            compute_degree=False,  # a flat check succeeds or fails; it has no degrees
        )
    ]


def cmd_recovery(args: argparse.Namespace) -> list[Roll]:
    if args.dying < 1:
        raise DiceError("a recovery check is only made while dying 1 or worse")
    dc = 10 + args.dying
    expr = f"1d20{args.bonus:+d}" if args.bonus else "1d20"
    r = make_roll(
        "recovery",
        expr,
        dc=dc,
        label=args.label or f"Recovery check (dying {args.dying})",
        actor=args.actor,
        secret=args.secret,
        private=args.private,
        transparency=args.transparency,
        tags=list(args.tag) + ["recovery"],
        extra={"dying_before": args.dying},
    )
    # Source: Player Core "Dying"/"Recovery Check" — DC 10 + dying value; critical success
    # reduces dying by 2, success by 1, failure increases it by 1, critical failure by 2.
    # Verified against Foundry VTT PF2e src/module/actor/creature/document.ts (recoveryDC 10,
    # check DC = recoveryDC + dying value).
    delta = {3: -2, 2: -1, 1: +1, 0: +2}[r.degree.index]  # type: ignore[union-attr]
    after = max(0, args.dying + delta)
    r.extra.update({"dying_delta": delta, "dying_after": after})
    r.label = (r.label or "") + f" → dying {args.dying} {delta:+d} = dying {after}" + (
        " (stabilised; gain Wounded 1 or increase it by 1)" if after == 0 else ""
    )
    if after >= 4:
        r.label += " — DEAD at dying 4"
    return [r]


def cmd_init(args: argparse.Namespace) -> tuple[list[Roll], list[dict[str, Any]]]:
    specs = [s.strip() for s in args.actors.split(",") if s.strip()]
    party = {s.strip() for s in args.party.split(",") if s.strip()}
    rolls: list[Roll] = []
    sides: dict[str, str] = {}
    for spec in specs:
        if ":" in spec:
            name, mod = spec.rsplit(":", 1)
            name = name.strip()
            try:
                m = int(mod)
            except ValueError as exc:
                raise DiceError(f"cannot read a modifier out of {spec!r}") from exc
        else:
            name, m = spec, args.default_mod
        sides[name] = "party" if name in party else "adversary"
        is_party = sides[name] == "party"
        rolls.append(
            make_roll(
                "initiative",
                f"1d20{m:+d}" if m else "1d20",
                label="Initiative",
                actor=name,
                secret=False,
                private=not is_party,
                transparency=args.transparency,
                tags=list(args.tag) + ["initiative"],
            )
        )
    # Roll off same-side ties with real dice rather than sorting on a name.
    totals: dict[int, list[Roll]] = {}
    for r in rolls:
        totals.setdefault(r.result.total, []).append(r)
    tiebreaks: dict[str, int] = {}
    for total, group in totals.items():
        by_side: dict[str, list[Roll]] = {}
        for r in group:
            by_side.setdefault(sides.get(r.actor or "", "adversary"), []).append(r)
        for side, members in by_side.items():
            if len(members) < 2:
                continue
            for r in members:
                t = make_roll(
                    "initiative-tiebreak",
                    "1d20",
                    label=f"Initiative tie-break at {total}",
                    actor=r.actor,
                    private=side != "party",
                    transparency=args.transparency,
                    tags=list(args.tag) + ["initiative", "tiebreak"],
                )
                tiebreaks[r.actor or ""] = t.result.total
                rolls.append(t)
    table = order_initiative([r for r in rolls if r.kind == "initiative"], sides, tiebreaks)
    return rolls, table


def cmd_table(args: argparse.Namespace) -> list[Roll]:
    path = Path(args.file)
    if not path.exists():
        raise DiceError(f"no such file: {path}")
    tables = parse_tables(path.read_text(encoding="utf-8"))
    if args.list:
        for k in sorted(tables):
            print(f"{k}  ({len(tables[k])} entries, d{max(h for _, h, _ in tables[k])})")
        return []
    heading, entries = find_table(tables, args.name)
    out = []
    for _ in range(max(1, args.count)):
        die = max(h for _, h, _ in entries)
        r = make_roll(
            "table",
            f"1d{die}",
            label=f"{heading}",
            secret=args.secret,
            private=args.private,
            transparency=args.transparency,
            tags=list(args.tag) + ["table"],
        )
        value = r.result.total
        text = next((t for lo, hi, t in entries if lo <= value <= hi), "(gap in table)")
        r.extra.update({"table": heading, "file": str(path), "entry": text, "rolled": value})
        r.label = f"{heading} [{value}] → {text}"
        out.append(r)
    return out


def cmd_batch(args: argparse.Namespace) -> list[Roll]:
    if args.payload_file:
        raw = Path(args.payload_file).read_text(encoding="utf-8")
    elif args.payload:
        raw = args.payload
    else:
        raw = sys.stdin.read()
    specs = json.loads(raw)
    if isinstance(specs, dict):
        specs = [specs]
    out = []
    for s in specs:
        kind = s.get("kind", "check")
        out.append(
            make_roll(
                kind,
                s["expr"],
                dc=s.get("dc"),
                label=s.get("label"),
                actor=s.get("actor"),
                secret=bool(s.get("secret")),
                private=bool(s.get("private")),
                transparency=s.get("transparency", args.transparency),
                tags=list(args.tag) + list(s.get("tags", [])),
                damage_type=s.get("type"),
                crit=bool(s.get("crit")),
                map_step=s.get("map"),
                fortune=bool(s.get("fortune")),
                misfortune=bool(s.get("misfortune")),
                compute_degree=kind != "flat",
            )
        )
    return out


def main(argv: Sequence[str] | None = None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)
    log = log_path_for(getattr(args, "campaign", None), getattr(args, "log", None))
    try:
        if args.cmd == "check":
            rolls = cmd_check(args)
        elif args.cmd == "save":
            rolls = cmd_check(args, kind="save")
        elif args.cmd == "damage":
            rolls = cmd_damage(args)
        elif args.cmd == "flat":
            rolls = cmd_flat(args)
        elif args.cmd == "recovery":
            rolls = cmd_recovery(args)
        elif args.cmd in ("fortune", "misfortune"):
            rolls = [
                make_roll(
                    args.cmd,
                    args.expr,
                    dc=args.dc,
                    label=args.label,
                    actor=args.actor,
                    secret=args.secret,
                    private=args.private,
                    transparency=args.transparency,
                    tags=list(args.tag) + [args.cmd],
                    fortune=args.cmd == "fortune",
                    misfortune=args.cmd == "misfortune",
                    extra={"dc_label": args.dc_label} if args.dc_label else None,
                )
            ]
        elif args.cmd == "expr":
            rolls = [
                make_roll(
                    "expr",
                    e,
                    label=args.label,
                    actor=args.actor,
                    secret=args.secret,
                    private=args.private,
                    transparency=args.transparency,
                    tags=args.tag,
                )
                for e in args.expression
            ]
        elif args.cmd == "table":
            rolls = cmd_table(args)
            if not rolls:
                return 0
        elif args.cmd == "batch":
            rolls = cmd_batch(args)
        elif args.cmd == "init":
            rolls, table = cmd_init(args)
            rc = _emit(rolls, args, log)
            if not args.json:
                print("\nInitiative order:")
                for row in table:
                    mark = "P" if row["side"] == "party" else "-"
                    print(f"  {row['order']:>2}. [{mark}] {row['actor']:<20} {row['total']:>3}"
                          f"  (natural {row['natural']})")
                print("  Cross-side ties: the adversary acts first (Player Core, Roll Initiative).")
            else:
                print(json.dumps({"order": table}, indent=2))
            return rc
        else:  # pragma: no cover - argparse guards this
            ap.error(f"unknown command {args.cmd}")
            return 2
    except DiceError as exc:
        print(f"roll.py: {exc}", file=sys.stderr)
        return 2
    except (KeyError, ValueError, json.JSONDecodeError) as exc:
        print(f"roll.py: bad input: {exc}", file=sys.stderr)
        return 2
    return _emit(rolls, args, log)


if __name__ == "__main__":
    raise SystemExit(main())
