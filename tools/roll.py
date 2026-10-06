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

sys.path.insert(0, str(Path(__file__).resolve().parent))

import rules  # noqa: E402
import pf2e  # noqa: E402

TOOL_VERSION = "1.1.0"
# Schema 2 adds `system`, `test_kind` and `degree_rungs` to every record, so a log can be
# read back without assuming which game produced it. Schema 1 records are still valid and
# analyze.py reads both; a record with no `system` key is a Pathfinder record.
LOG_SCHEMA_VERSION = 2

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


_DICE_TERM_RE = re.compile(r"(?<![\dkhl])(\d*)d(\d+)(?![\dkhl])", re.IGNORECASE)


def double_damage_dice(expr: str) -> str:
    """Double the number of dice in every term, leaving flat modifiers alone.

    This is the D&D 2024 critical-hit rule written as an expression rewrite, which keeps
    the extra dice *rolled* rather than multiplying a number that was already rolled.

    Source: SRD 5.2, "Damage and Healing" -> "Critical Hits": "Roll the attack's damage
    dice twice, add them together, and add any relevant modifiers as normal. For example,
    if you score a Critical Hit with a Dagger, roll 2d4 for the damage rather than 1d4,
    and add your relevant ability modifier." So `1d8+4` becomes `2d8+4` — the modifier is
    added once, not twice, which is the difference from Pathfinder's doubled total.

    A term carrying a keep-highest or keep-lowest modifier is refused rather than guessed
    at, because doubling it has no single obvious meaning; write the doubled expression
    by hand in that case.
    """
    text = str(expr).replace(" ", "")
    if re.search(r"d\d+k[hl]", text, re.IGNORECASE):
        raise DiceError(
            f"cannot mechanically double {expr!r}: it keeps highest/lowest dice, and what "
            f"'roll the damage dice twice' means for that is a judgement call — write the "
            f"doubled expression out instead"
        )

    def grow(m: re.Match[str]) -> str:
        n = int(m.group(1) or 1)
        return f"{n * 2}d{m.group(2)}"

    new, count = _DICE_TERM_RE.subn(grow, text)
    if count == 0:
        raise DiceError(f"{expr!r} has no dice to double")
    return new


def maximise_damage_dice(expr: str) -> str:
    """Replace every dice term with its maximum, leaving flat modifiers alone.

    This is D&D 4th Edition's critical-hit rule written as an expression rewrite: a
    critical hit in 4e deals maximum damage rather than rolling anything extra, so
    `2d6+5` becomes `12+5`. The three rulesets this framework runs disagree completely
    here — Pathfinder doubles the whole roll, D&D 2024 doubles the dice and adds the
    modifier once, and 4e rolls nothing at all — which is why the rule lives with the
    ruleset and not with the dice.

    Stated as a mechanic rather than quoted: 4e has no open-content release, so nothing
    of its text is reproduced here. Extra dice from a high-crit weapon or a critical-only
    power are rolled separately and added — pass them as their own damage roll, because
    those dice **are** rolled and must not be maximised.

    A term carrying a keep-highest or keep-lowest modifier is refused rather than guessed
    at, for the same reason doubling one is.
    """
    text = str(expr).replace(" ", "")
    if re.search(r"d\d+k[hl]", text, re.IGNORECASE):
        raise DiceError(
            f"cannot mechanically maximise {expr!r}: it keeps highest/lowest dice, and the "
            f"maximum of that is a judgement call — write the maximised expression instead"
        )

    def top(m: re.Match[str]) -> str:
        n = int(m.group(1) or 1)
        return str(n * int(m.group(2)))

    new, count = _DICE_TERM_RE.subn(top, text)
    if count == 0:
        raise DiceError(f"{expr!r} has no dice to maximise")
    return new


def _rewrite_d20(expr: str, replacement: str) -> str:
    text = str(expr).replace(" ", "")
    new, n = re.subn(r"(?<![\dkhl])1?d20(?!\d)", replacement, text, count=1, flags=re.IGNORECASE)
    if n == 0:
        raise DiceError(f"{expr!r} has no 1d20 to convert")
    return new


# --------------------------------------------------------------------------------------
# Degrees of success
# --------------------------------------------------------------------------------------

# Pathfinder's four-rung ladder, kept at module scope because callers import these names.
# The scale is no longer assumed: each outcome carries the ladder it was measured on, so a
# two-rung D&D hit/miss and a four-rung Pathfinder degree can share one carrier.
DEGREES = pf2e.DEGREES
DEGREE_LABELS = pf2e.DEGREE_LABELS


@dataclass
class Degree:
    """One roll's interpretation, with the scale it was interpreted on.

    `scale` and `labels` default to Pathfinder's four degrees, so every existing caller
    that built a Degree without naming a scale keeps the behaviour it had.
    """

    index: int
    unadjusted_index: int
    shift: int
    natural: int | None
    scale: tuple[str, ...] = DEGREES
    labels: tuple[str, ...] = DEGREE_LABELS
    system: str = rules.DEFAULT_SYSTEM
    test_kind: str = "check"
    note: str | None = None

    @property
    def name(self) -> str:
        return self.scale[self.index]

    @property
    def label(self) -> str:
        return self.labels[self.index]

    @property
    def unadjusted_name(self) -> str:
        return self.scale[self.unadjusted_index]

    @property
    def rungs(self) -> int:
        return len(self.scale)

    @property
    def succeeded(self) -> bool:
        """True on a hit or better. Index 2 on a four-rung ladder, the top of a two-rung one."""
        return self.index >= (2 if len(self.scale) == 4 else len(self.scale) - 1)


def degree_of_success(total: int, dc: int, natural: int | None,
                      *, system: str | None = None, kind: str = "check") -> Degree:
    """Interpret one roll against one target number, using the campaign's ruleset.

    The arithmetic lives in the ruleset modules — `pf2e.resolve` and `dnd5e.resolve` —
    because it is a rules statement and belongs beside the other rules statements, each
    with its own `Source:` note. What differs between them:

      PF2e    four degrees, and the natural-20 / natural-1 one-step shift applies to
              every check and save.
      D&D     pass or fail, and the natural-20 / natural-1 rules apply to ATTACK ROLLS
              only — which is why `kind` here is no longer cosmetic.

    Passing three positional arguments and nothing else keeps this function's original
    Pathfinder behaviour exactly.
    """
    mod = rules.load(system)
    out = mod.resolve(total, dc, natural, kind=kind)
    return Degree(
        index=out["index"],
        unadjusted_index=out["unadjusted_index"],
        shift=out["shift"],
        natural=natural,
        scale=tuple(out["scale"]),
        labels=tuple(out["labels"]),
        system=out["system"],
        test_kind=out["kind"],
        note=out.get("forced"),
    )


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
    system: str = rules.DEFAULT_SYSTEM
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
            if self.crit and self.extra.get("base_total") is not None:
                # Pathfinder: the whole roll doubled, so show what it doubled.
                base = self.extra.get("base_total")
                body = f" → {self.result.faces_line()} = {base} x2 = {self.result.total}"
            tail = f" {self.damage_type}" if self.damage_type else ""
            if self.crit:
                tail += " (critical)"
                undoubled = self.extra.get("undoubled_expr")
                unmaxed = self.extra.get("unmaximised_expr")
                if undoubled:
                    # D&D 2024: the dice themselves were doubled, so name what was rolled.
                    tail += f" — dice doubled from {undoubled}"
                elif unmaxed:
                    # D&D 4e: nothing was rolled at all, so say so rather than implying dice.
                    tail += (f" — maximum damage, dice not rolled "
                             f"({unmaxed} maximised to {self.extra.get('maximised_expr')})")
        elif self.dc is not None and self.degree is not None:
            default_vs = "AC" if (self.degree.test_kind == "attack" and self.system != "pf2e") else "DC"
            vs = self.extra.get("dc_label") or default_vs
            tail = f" vs {vs} {self.dc} → {self.degree.label}"
            if self.degree.shift:
                nat = self.degree.natural
                word = "upgraded" if self.degree.shift > 0 else "downgraded"
                tail += f"  [natural {nat}: {word} from {self.degree.unadjusted_name.upper()}]"
            elif self.degree.note:
                tail += f"  [{self.degree.note}]"
        elif self.dc is not None:
            ok = self.result.total >= self.dc
            tail = f" vs DC {self.dc} → {'SUCCESS' if ok else 'FAILURE'}"
        if self.map_step:
            tail += f"  (MAP step {self.map_step})"
        # The same two dice have two names. Print the one the table actually uses. 4e has
        # no such mechanic at all, and `make_roll` refuses it rather than labelling it.
        swing = ("advantage", "disadvantage") if self.system != "pf2e" else ("fortune", "misfortune")
        if self.fortune:
            tail += f"  [{swing[0]}]"
        if self.misfortune:
            tail += f"  [{swing[1]}]"
        return head + body + tail

    # -- logging -----------------------------------------------------------------

    def log_record(self, campaign: str | None, session: int | None, checkpoint: int | None) -> dict[str, Any]:
        rec: dict[str, Any] = {
            "ts": utc_now(),
            "schema": LOG_SCHEMA_VERSION,
            "tool_version": TOOL_VERSION,
            "rng": "random.SystemRandom",
            "system": self.system,
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
                    "degree_rungs": self.degree.rungs,
                    "test_kind": self.degree.test_kind,
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
            "system": self.system,
            "degree": self.degree.name if self.degree else None,
            "degree_shift": self.degree.shift if self.degree else 0,
            "shown": self.shown,
            "secret": self.secret,
            "private": self.private,
            "dice": self.result.dice_json(),
            "line": self.public_line(),
        }
        if self.extra:
            # The per-ruleset fields a caller needs to act on the roll — the crit rule
            # applied, the death-save counters after it, what the natural 20 permits.
            d["extra"] = dict(self.extra)
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
    system: str | None = None,
    test_kind: str | None = None,
) -> Roll:
    """Roll one expression and interpret it. Nothing here consults an expected outcome.

    `system` selects the ruleset; `test_kind` says what sort of d20 test this is, which
    matters in D&D (attack rolls crit, checks and saves do not) and not in Pathfinder.
    """
    if fortune and misfortune:
        raise DiceError("a roll cannot be both fortune and misfortune")
    sid = rules.canonical(system)
    rs = rules.load(sid)
    if (fortune or misfortune) and sid == "dnd4e":
        # 4e has no two-dice swing under any name. Its equivalents are flat numbers: a +2
        # for combat advantage, a -2 for a penalty. Rolling 2d20 and keeping one would be
        # another game's mechanic wearing 4e's label, so it is refused rather than renamed.
        raise DiceError(
            "D&D 4e has neither Advantage/Disadvantage nor fortune/misfortune — every swing "
            "in 4e is a flat modifier. Combat advantage is +2 to the attack roll; put it in "
            "the expression (`1d20+9+2`) so the log shows the real arithmetic."
        )
    tk = test_kind or ("attack" if kind == "attack" else kind if kind in ("save", "flat") else "check")

    use = expr
    if fortune:
        use = to_fortune(expr)
    elif misfortune:
        use = to_misfortune(expr)

    extra = dict(extra or {})

    if kind == "damage" and crit and sid == "dnd5e":
        # D&D 2024 rolls the damage DICE twice and adds the modifier once, so the extra
        # dice are genuinely rolled rather than being a doubled total.
        doubled = double_damage_dice(use)
        extra["crit_rule"] = "dice doubled, modifier added once (SRD 5.2 Critical Hits)"
        extra["undoubled_expr"] = use
        use = doubled

    if kind == "damage" and crit and sid == "dnd4e":
        # D&D 4e criticals deal MAXIMUM damage — nothing extra is rolled, so the dice are
        # replaced by their highest faces before anything is thrown. High-crit weapons and
        # critical-only powers add dice that genuinely are rolled; roll those separately.
        maxed = maximise_damage_dice(use)
        extra["crit_rule"] = ("maximum damage; no dice rolled (D&D 4e critical hits — "
                              "mechanic, no open source to cite)")
        extra["unmaximised_expr"] = use
        extra["maximised_expr"] = maxed
        use = maxed

    result = roll_expression(use)

    if kind == "damage" and crit and sid == "pf2e":
        # Pathfinder criticals double the whole damage roll, modifiers included.
        # Source: Player Core, "Critical Hits" — verified in system/12-rules-quick-reference.md.
        extra["base_total"] = result.total
        extra["crit_rule"] = "whole roll doubled, modifiers included (PF2e Critical Hits)"
        result = RollResult(
            expr=f"({result.expr}) x2",
            groups=result.groups,
            modifier=result.modifier,
            total=result.total * 2,
        )

    degree = None
    if dc is not None and compute_degree:
        degree = degree_of_success(result.total, dc, result.natural, system=sid, kind=tk)

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
        system=sid,
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


#: How a cross-side initiative tie resolves, per ruleset, and where that comes from.
TIE_RULES = {
    "pf2e": (
        "adversary-first",
        'Cross-side ties: the adversary acts first (Player Core, "Roll Initiative"; verified '
        "against the Foundry VTT PF2e implementation, src/module/encounter/document.ts "
        "`_sortCombatants`, where an NPC's tiebreak priority of 1 sorts ahead of a "
        "player-owned actor's 2). Same-side ties were rolled off with real dice.",
    ),
    "dnd5e": (
        "rolled-off",
        'Ties: the published rule is that the GM decides — "If a tie occurs, the GM decides the '
        "order among tied monsters, and the players decide the order among tied characters. The "
        'GM decides the order if the tie is between a monster and a player character" (SRD 5.2, '
        '"Combat" -> "Initiative" -> "Ties"). This framework rolls every tie off with real dice '
        "instead, so the ordering is auditable rather than an unlogged GM choice. That "
        "substitution is this framework's convention, not the published rule; say so at the "
        "table, and override the order by hand if the player would rather decide.",
    ),
    "dnd4e": (
        "rolled-off",
        "Ties: in D&D 4e a tie on initiative is broken in favour of the higher initiative "
        "modifier, and a tie on that too is decided by the DM. Stated as a mechanic — 4e has "
        "no open-content release, so nothing of its text is quoted. This framework rolls "
        "every remaining tie off with real dice rather than deciding unlogged, which is this "
        "framework's convention and not the published rule; say so at the table.",
    ),
}


def order_initiative(rolls: list[Roll], sides: dict[str, str], tiebreak_rolls: dict[str, int],
                     *, system: str | None = None) -> list[dict[str, Any]]:
    """Sort an initiative table.

    Higher total acts first. What happens on a tie differs between the rulesets, and
    `TIE_RULES` holds both statements with their sources. Pathfinder gives the adversary
    priority on a cross-side tie; D&D leaves ties to the GM, and this framework rolls
    them off with dice so the choice is logged. Ties within one side are a real d20
    roll-off in both.
    """
    sid = rules.canonical(system)
    adversary_first = TIE_RULES[sid][0] == "adversary-first"
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
    rows.sort(key=lambda row: (
        -row["total"],
        (0 if row["side"] == "adversary" else 1) if adversary_first else 0,
        -row["tiebreak"],
        row["actor"],
    ))
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


def _system_for(args: argparse.Namespace) -> str:
    """Which ruleset this roll is made under.

    An explicit --system wins; otherwise the campaign's own declaration decides, so the
    GM does not have to repeat it on every call. A campaign that declares nothing reads
    as Pathfinder, which is what every campaign created before the second ruleset did.
    """
    explicit = getattr(args, "system", None)
    if explicit:
        return rules.canonical(explicit)
    return rules.for_campaign(getattr(args, "campaign", None))


def _advantage_flags(args: argparse.Namespace) -> tuple[bool, bool]:
    """Advantage/Disadvantage and fortune/misfortune are the same dice, differently named.

    D&D 2024: "roll a second d20 ... Use the higher of the two rolls if you have
    Advantage, and use the lower roll if you have Disadvantage" (SRD 5.2,
    "Advantage/Disadvantage"). Pathfinder calls the same operation a fortune or
    misfortune effect. Both land on 2d20kh1 / 2d20kl1, so one implementation serves both
    and the log records which word the table used.

    "If circumstances cause a roll to have both Advantage and Disadvantage, the roll has
    neither of them, and you roll one d20" — so passing both cancels, per the published
    rule, rather than erroring.
    """
    adv = bool(getattr(args, "advantage", False))
    dis = bool(getattr(args, "disadvantage", False))
    if adv and dis:
        return False, False
    return adv, dis


def _common(p: argparse.ArgumentParser) -> None:
    p.add_argument("--system", help="ruleset for this roll; defaults to the campaign's own")
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


def _swing(p: argparse.ArgumentParser) -> None:
    """Advantage/Disadvantage, which are also Pathfinder's fortune/misfortune."""
    p.add_argument("--advantage", "--adv", action="store_true", dest="advantage",
                   help="roll two d20 and keep the higher (PF2e: a fortune effect)")
    p.add_argument("--disadvantage", "--dis", action="store_true", dest="disadvantage",
                   help="roll two d20 and keep the lower (PF2e: a misfortune effect)")


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
    _swing(p)

    p = add("save", "a saving throw")
    p.add_argument("expr", nargs="+")
    p.add_argument("--dc", type=int, required=True)
    p.add_argument("--label")
    p.add_argument("--actor", action="append", default=[])
    _visibility(p)
    _swing(p)

    p = add("attack", "an attack roll against an AC (D&D: only this kind of roll can crit)")
    p.add_argument("expr", nargs="+")
    p.add_argument("--dc", "--ac", dest="dc", type=int, required=True, help="the target's AC")
    p.add_argument("--label")
    p.add_argument("--actor", action="append", default=[])
    p.add_argument("--map", dest="map_step", type=int, default=0,
                   help="PF2e multiple attack penalty step reached; ignored in D&D")
    p.add_argument("--dc-label", default=None)
    _visibility(p)
    _swing(p)

    p = add("damage", "a damage roll")
    p.add_argument("expr", nargs="+")
    p.add_argument("--crit", action="store_true",
                   help="PF2e: double the whole roll, modifiers included. "
                        "D&D: double the dice and add the modifier once")
    p.add_argument("--type", dest="dtype", default=None)
    p.add_argument("--label")
    p.add_argument("--actor", action="append", default=[])
    _visibility(p)

    p = add("flat", "a flat check (no degrees of success)")
    p.add_argument("dc", type=int)
    p.add_argument("--label")
    p.add_argument("--actor")
    _visibility(p)

    p = add("recovery", "PF2e: a recovery check while dying")
    p.add_argument("--dying", type=int, required=True)
    p.add_argument("--bonus", type=int, default=0, help="modifier to the recovery check, if any")
    p.add_argument("--actor")
    p.add_argument("--label")
    _visibility(p)

    p = add("death-save", "D&D: a Death Saving Throw at 0 HP (DC 10, no ability modifier)")
    p.add_argument("--successes", type=int, default=0, help="successes already held")
    p.add_argument("--failures", type=int, default=0, help="failures already held")
    p.add_argument("--bonus", type=int, default=0,
                   help="modifier, if a feature grants one; the save normally takes none")
    p.add_argument("--actor")
    p.add_argument("--label")
    _visibility(p)
    _swing(p)

    p = add("init", "roll initiative for several actors and return the ordered table")
    p.add_argument("--actors", required=True, help="comma list, each 'name' or 'name:+7'")
    p.add_argument("--party", default="", help="comma list of names on the party side (for tie-breaks)")
    p.add_argument("--surprised", default="",
                   help="D&D: comma list of names surprised by the fight starting, who roll "
                        "initiative with Disadvantage")
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
    sid = _system_for(args)
    adv, dis = _advantage_flags(args)
    extra_tags = (["advantage"] if adv else []) + (["disadvantage"] if dis else [])
    if getattr(args, "advantage", False) and getattr(args, "disadvantage", False):
        extra_tags = ["advantage-and-disadvantage-cancelled"]
    dc_label = getattr(args, "dc_label", None)
    if kind == "attack" and not dc_label:
        dc_label = "AC"
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
                tags=list(args.tag) + extra_tags,
                map_step=getattr(args, "map_step", 0) or None,
                fortune=adv,
                misfortune=dis,
                extra={"dc_label": dc_label} if dc_label else None,
                system=sid,
                test_kind=kind,
            )
        )
    return out


def cmd_damage(args: argparse.Namespace) -> list[Roll]:
    actors = _actors_for(args, len(args.expr))
    sid = _system_for(args)
    return [
        make_roll(
            "damage",
            expr,
            system=sid,
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
            system=_system_for(args),
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
    sid = _system_for(args)
    if sid != "pf2e":
        raise DiceError(
            f"a recovery check is a Pathfinder procedure, and this is a "
            f"{rules.short_of(sid)} campaign. Both D&D editions make a death saving throw "
            f"instead: `roll.py death-save --campaign {args.campaign or '<slug>'}`"
        )
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
        system=sid,
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


def _death_save_4e(args: argparse.Namespace) -> list[Roll]:
    """A D&D 4e death saving throw: a flat d20 against 10, counting failures only.

    Stated as a mechanic, with nothing quoted — 4e has no open-content release. Below 10
    is a failure and the third failure before an extended rest is death; 10 or better
    simply is not a failure, and nothing accumulates on it; a natural 20 lets the
    character spend a healing surge and act. Unlike D&D 2024's version there is no
    success counter and no Stable state, so this does not pretend to track either.
    """
    import dnd4e

    expr = f"1d20{args.bonus:+d}" if args.bonus else "1d20"
    if int(getattr(args, "successes", 0) or 0):
        raise DiceError(
            "a 4e death saving throw has no success counter — pass only --failures. "
            "Ten or better is not a success that accumulates; it is simply not a failure."
        )
    r = make_roll(
        "death-save",
        expr,
        dc=dnd4e.DEATH_SAVE_SUCCESS_DC,
        label=args.label or "Death saving throw",
        actor=args.actor,
        secret=args.secret,
        private=args.private,
        transparency=args.transparency,
        tags=list(args.tag) + ["death-save"],
        system="dnd4e",
        test_kind="death-save",
        extra={"failures_before": int(getattr(args, "failures", 0) or 0),
               "dc_label": "flat DC"},
    )
    out = dnd4e.resolve(r.result.total, dnd4e.DEATH_SAVE_SUCCESS_DC, r.result.natural,
                        kind="death-save")
    incurred = int(out.get("failures_incurred", 0 if out["success"] else 1))
    fail = int(getattr(args, "failures", 0) or 0) + incurred
    r.extra.update({
        "failures_incurred": incurred,
        "failures_after": fail,
        "spends_a_surge": bool(out.get("spends_surge")),
    })
    r.label = (r.label or "") + f" → {fail}/{dnd4e.DEATH_SAVE_FAILURES} failures"
    if out.get("spends_surge"):
        r.label += " — natural 20: spend a healing surge and act"
        r.extra["resolution"] = "may spend a healing surge"
    elif fail >= dnd4e.DEATH_SAVE_FAILURES:
        r.label += " — DEAD on the third failure"
        r.extra["resolution"] = "dead"
    elif out["success"]:
        r.extra["resolution"] = "still dying, no failure incurred"
    else:
        r.extra["resolution"] = "still dying"
    return [r]


def cmd_death_save(args: argparse.Namespace) -> list[Roll]:
    """A D&D 2024 Death Saving Throw, with its own natural-20 and natural-1 rules.

    Source: see `python3 tools/dnd5e.py sources` (death_saves). The save takes no ability
    modifier — "Unlike other saving throws, this one isn't tied to an ability score" — so
    the expression is a bare d20 unless the table has a feature that says otherwise.
    """
    sid = _system_for(args)
    if sid == "dnd4e":
        return _death_save_4e(args)
    if sid != "dnd5e":
        raise DiceError(
            f"a Death Saving Throw is a D&D 2024 procedure, and this is a "
            f"{rules.short_of(sid)} campaign. Pathfinder has recovery checks instead: "
            f"`roll.py recovery --dying N --campaign {args.campaign or '<slug>'}`"
        )
    import dnd5e

    adv, dis = _advantage_flags(args)
    expr = f"1d20{args.bonus:+d}" if args.bonus else "1d20"
    r = make_roll(
        "death-save",
        expr,
        dc=dnd5e.DEATH_SAVE_DC,
        label=args.label or "Death Saving Throw",
        actor=args.actor,
        secret=args.secret,
        private=args.private,
        transparency=args.transparency,
        tags=list(args.tag) + ["death-save"],
        fortune=adv,
        misfortune=dis,
        system=sid,
        test_kind="death-save",
        extra={"successes_before": args.successes, "failures_before": args.failures},
    )
    out = dnd5e.resolve(r.result.total, dnd5e.DEATH_SAVE_DC, r.result.natural, kind="death-save")
    succ = int(args.successes) + out["successes_incurred"]
    fail = int(args.failures) + out["failures_incurred"]
    r.extra.update(
        {
            "successes_incurred": out["successes_incurred"],
            "failures_incurred": out["failures_incurred"],
            "successes_after": succ,
            "failures_after": fail,
            "heals_to_one": out["heals_to_one"],
        }
    )
    bits = [f"{succ}/3 successes", f"{fail}/3 failures"]
    r.label = (r.label or "") + " → " + ", ".join(bits)
    if out["heals_to_one"]:
        r.label += " — natural 20: regains 1 HP and stops saving"
        r.extra["resolution"] = "conscious at 1 HP"
    elif fail >= dnd5e.DEATH_SAVES_TO_RESOLVE:
        r.label += " — DEAD on the third failure"
        r.extra["resolution"] = "dead"
    elif succ >= dnd5e.DEATH_SAVES_TO_RESOLVE:
        r.label += " — STABLE on the third success (still Unconscious at 0 HP)"
        r.extra["resolution"] = "stable"
    else:
        r.extra["resolution"] = "still dying"
    return [r]


def cmd_init(args: argparse.Namespace) -> tuple[list[Roll], list[dict[str, Any]]]:
    specs = [s.strip() for s in args.actors.split(",") if s.strip()]
    party = {s.strip() for s in args.party.split(",") if s.strip()}
    surprised = {s.strip() for s in (getattr(args, "surprised", "") or "").split(",") if s.strip()}
    sid = _system_for(args)
    unknown = surprised - {sp.split(":", 1)[0].strip() for sp in specs}
    if unknown:
        raise DiceError(f"--surprised names nobody rolling initiative: {', '.join(sorted(unknown))}")
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
        # Surprise in D&D 2024 is Disadvantage on the Initiative roll, not a lost turn.
        # Source: SRD 5.2, "Combat" -> "Initiative" -> "Surprise". Pathfinder has no
        # equivalent initiative penalty, so the flag is refused there rather than applied
        # under a Pathfinder label it does not have.
        is_surprised = name in surprised
        if is_surprised and sid != "dnd5e":
            instead = {
                "pf2e": "In Pathfinder, an unaware creature is off-guard and the ambusher may "
                        "get a free round",
                "dnd4e": "In 4e, surprised creatures do not act in the surprise round at all "
                         "and grant combat advantage until they do",
            }.get(sid, "That ruleset handles surprise some other way")
            raise DiceError(
                f"--surprised is a D&D 2024 rule (Disadvantage on the Initiative roll) and "
                f"this is a {rules.short_of(sid)} campaign. {instead} — handle it in the "
                f"fiction and the encounter tracker, not on the initiative roll."
            )
        rolls.append(
            make_roll(
                "initiative",
                f"1d20{m:+d}" if m else "1d20",
                label="Initiative" + (" (surprised: Disadvantage)" if is_surprised else ""),
                actor=name,
                secret=False,
                private=not is_party,
                transparency=args.transparency,
                tags=list(args.tag) + ["initiative"] + (["surprised"] if is_surprised else []),
                misfortune=is_surprised,
                system=sid,
                test_kind="check",
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
                    system=sid,
                )
                tiebreaks[r.actor or ""] = t.result.total
                rolls.append(t)
    table = order_initiative(
        [r for r in rolls if r.kind == "initiative"], sides, tiebreaks, system=sid)
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
        elif args.cmd == "attack":
            rolls = cmd_check(args, kind="attack")
        elif args.cmd == "damage":
            rolls = cmd_damage(args)
        elif args.cmd == "flat":
            rolls = cmd_flat(args)
        elif args.cmd == "recovery":
            rolls = cmd_recovery(args)
        elif args.cmd == "death-save":
            rolls = cmd_death_save(args)
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
                    system=_system_for(args),
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
                    system=_system_for(args),
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
                print("\n  " + TIE_RULES[_system_for(args)][1])
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
