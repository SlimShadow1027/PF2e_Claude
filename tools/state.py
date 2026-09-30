#!/usr/bin/env python3
"""state.py — the only writer of `campaigns/<slug>/state.json`.

`state.json` is canonical for every volatile number: hit points, conditions with values
and durations, Hero Points, Focus Points, spell slots, dying/wounded/doomed, coins,
consumables, XP, level, the in-world date, clock segments, position, and the full
encounter tracker. Prose and the built character live in Markdown. `CHECKPOINT.md` is
rendered from here and is never hand-edited.

Every mutation goes through this CLI so it is atomic and validated. Impossible states are
refused with an explanation rather than silently clamped.

Standard library only. See system/05-checkpoint-protocol.md and system/03-*.md.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

from roll import (  # noqa: E402
    DiceError,
    atomic_write,
    campaign_dir,
    make_roll,
    append_log,
    repo_root,
    utc_now,
)
import pf2e  # noqa: E402

SCHEMA_VERSION = 2

VALUED_CONDITIONS = {
    "clumsy",
    "cursebound",
    "doomed",
    "drained",
    "dying",
    "enfeebled",
    "frightened",
    "sickened",
    "slowed",
    "stunned",
    "stupefied",
    "wounded",
}
# Source: Player Core condition entries; the valued/unvalued split is verified against the
# Foundry VTT PF2e condition compendium (packs/pf2e/conditions/*.json, v8.5.1).
UNVALUED_CONDITIONS = {
    "blinded",
    "broken",
    "concealed",
    "confused",
    "controlled",
    "dazzled",
    "deafened",
    "encumbered",
    "fascinated",
    "fatigued",
    "fleeing",
    "friendly",
    "grabbed",
    "helpful",
    "hidden",
    "hostile",
    "immobilized",
    "indifferent",
    "invisible",
    "observed",
    "off-guard",
    "paralyzed",
    "persistent-damage",
    "petrified",
    "prone",
    "quickened",
    "restrained",
    "unconscious",
    "undetected",
    "unfriendly",
    "unnoticed",
}
KNOWN_CONDITIONS = VALUED_CONDITIONS | UNVALUED_CONDITIONS
# dying / wounded / doomed are first-class fields on a combatant rather than list entries,
# so that nothing can hold two disagreeing copies of the number that decides a death.
TRACKED_SEPARATELY = {"dying", "wounded", "doomed"}

DURATION_KINDS = ("rounds", "minutes", "hours", "days", "end-of-turn", "until-removed")

COIN_ORDER = ("pp", "gp", "sp", "cp")
COIN_IN_CP = {"pp": 1000, "gp": 100, "sp": 10, "cp": 1}
# Source: Player Core, "Coins" — 1 pp = 10 gp, 1 gp = 10 sp, 1 sp = 10 cp.


class StateError(Exception):
    """A refused mutation. The message says what was asked and why it cannot happen."""


# --------------------------------------------------------------------------------------
# Load / save
# --------------------------------------------------------------------------------------


def state_path(slug: str) -> Path:
    return campaign_dir(slug) / "state.json"


def load(slug: str) -> dict[str, Any]:
    p = state_path(slug)
    if not p.exists():
        raise StateError(f"no state.json for campaign {slug!r} (looked in {p.parent})")
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise StateError(f"{p} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise StateError(f"{p} does not hold a JSON object")
    return data


def save(slug: str, data: dict[str, Any]) -> None:
    data["updated_at"] = utc_now()
    atomic_write(state_path(slug), json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False) + "\n")


def blank_state(slug: str, title: str = "", transparency: str = "standard") -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "campaign": slug,
        "title": title or slug,
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "transparency": transparency,
        "difficulty_preset": "Standard",
        "session_in_progress": False,
        "session_number": 0,
        "scene_count": 0,
        "checkpoint_counter": 0,
        "last_checkpoint": None,
        "time": pf2e.blank_time(),
        "location": "unset",
        "party": {
            "level": 1,
            "xp": 0,
            "gold": {"pp": 0, "gp": 0, "sp": 0, "cp": 0},
            "stash": [],
        },
        "pcs": {},
        "clocks": {},
        "quests": {},
        "encounter": None,
        "notes": {"situation": "", "next_beats": ""},
    }


# --------------------------------------------------------------------------------------
# Dotted-path access
# --------------------------------------------------------------------------------------


def dig(data: Any, path: str) -> Any:
    cur = data
    for part in [p for p in path.split(".") if p]:
        if isinstance(cur, list):
            try:
                cur = cur[int(part)]
            except (ValueError, IndexError) as exc:
                raise StateError(f"{path!r}: no index {part!r}") from exc
        elif isinstance(cur, dict):
            if part not in cur:
                raise StateError(f"{path!r}: no key {part!r}")
            cur = cur[part]
        else:
            raise StateError(f"{path!r}: {part!r} is not reachable")
    return cur


def poke(data: dict[str, Any], path: str, value: Any) -> None:
    parts = [p for p in path.split(".") if p]
    if not parts:
        raise StateError("empty path")
    cur: Any = data
    for part in parts[:-1]:
        if isinstance(cur, list):
            cur = cur[int(part)]
        else:
            if part not in cur or not isinstance(cur[part], (dict, list)):
                raise StateError(f"{path!r}: {part!r} is not a container in state.json")
            cur = cur[part]
    last = parts[-1]
    if isinstance(cur, list):
        cur[int(last)] = value
    else:
        cur[last] = value


def coerce(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


# --------------------------------------------------------------------------------------
# Characters
# --------------------------------------------------------------------------------------


def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", str(name).lower()).strip("-")
    return s or "unnamed"


def blank_character(name: str, kind: str = "pc", level: int = 1) -> dict[str, Any]:
    return {
        "name": name,
        "kind": kind,  # pc | ally | sidekick | companion | familiar | eidolon
        "level": level,
        "hp": {"current": 0, "max": 0, "temp": 0},
        "ac": 0,
        "saves": {"fortitude": 0, "reflex": 0, "will": 0},
        "perception": 0,
        "speed": 25,
        "str_mod": 0,
        "hero_points": 0,
        "hero_points_max": 3,
        "focus": {"current": 0, "max": 0, "refocus_available": True},
        "spell_slots": {},
        "conditions": [],
        "dying": 0,
        "wounded": 0,
        "doomed": 0,
        "dying_max": 4,
        "persistent": [],
        "items": [],
        "sheet": None,
        "notes": "",
    }


def find_character(data: dict[str, Any], who: str) -> tuple[str, dict[str, Any]]:
    pcs = data.setdefault("pcs", {})
    key = who if who in pcs else slugify(who)
    if key in pcs:
        return key, pcs[key]
    lowered = {k.lower(): k for k in pcs}
    if who.lower() in lowered:
        k = lowered[who.lower()]
        return k, pcs[k]
    for k, v in pcs.items():
        if str(v.get("name", "")).lower() == who.lower():
            return k, v
    known = ", ".join(sorted(pcs)) or "none"
    raise StateError(f"no character {who!r} in state.json (known: {known})")


# --------------------------------------------------------------------------------------
# Hit points, dying, conditions
# --------------------------------------------------------------------------------------


def apply_damage(data: dict[str, Any], who: str, amount: int, *, from_crit: bool = False) -> list[str]:
    """Damage a character: temp HP absorbs first, then current HP; 0 HP starts dying.

    Source: Player Core "Hit Points, Healing, and Dying" and the Dying condition — a
    character reduced to 0 HP falls unconscious and gains dying 1, or dying 2 if the
    damage came from a critical hit or a critical failure on their save; a character who
    already has the wounded condition starts at dying 1 + wounded value. Verified against
    the Foundry VTT PF2e condition compendium entry for Dying (v8.5.1).
    """
    if amount < 0:
        raise StateError(f"damage of {amount} is not damage; use `heal`")
    key, pc = find_character(data, who)
    notes: list[str] = []
    hp = pc["hp"]
    left = amount
    if hp.get("temp", 0) > 0:
        absorbed = min(hp["temp"], left)
        hp["temp"] -= absorbed
        left -= absorbed
        notes.append(f"{absorbed} absorbed by temporary HP ({hp['temp']} temp left)")
    was_down = hp["current"] <= 0
    hp["current"] = max(0, hp["current"] - left)
    notes.append(f"{pc['name']} HP {hp['current']}/{hp['max']}")

    if pc.get("dying", 0) > 0:
        step = 2 if from_crit else 1
        notes += set_dying(data, key, pc["dying"] + step, reason="took damage while dying")
    elif hp["current"] == 0 and not was_down:
        start = 2 if from_crit else 1
        start += int(pc.get("wounded", 0))
        notes.append("reduced to 0 HP — unconscious")
        notes += set_dying(data, key, start, reason="reduced to 0 HP")
    return notes


def apply_healing(data: dict[str, Any], who: str, amount: int) -> list[str]:
    if amount < 0:
        raise StateError(f"healing of {amount} is not healing; use `damage`")
    key, pc = find_character(data, who)
    hp = pc["hp"]
    if hp["max"] <= 0:
        raise StateError(f"{pc['name']} has no maximum HP set; set it before healing")
    new = hp["current"] + amount
    if new > hp["max"]:
        notes = [f"healing capped at maximum: {hp['max'] - hp['current']} of {amount} applied"]
        new = hp["max"]
    else:
        notes = []
    hp["current"] = new
    notes.append(f"{pc['name']} HP {hp['current']}/{hp['max']}")
    if hp["current"] >= 1 and pc.get("dying", 0) > 0:
        notes += set_dying(data, key, 0, reason="back to 1 HP or more")
    return notes


def set_hp(data: dict[str, Any], who: str, current: int | None, maximum: int | None, temp: int | None) -> list[str]:
    _, pc = find_character(data, who)
    hp = pc["hp"]
    new_max = hp["max"] if maximum is None else maximum
    new_cur = hp["current"] if current is None else current
    new_temp = hp.get("temp", 0) if temp is None else temp
    if new_max < 0:
        raise StateError("maximum HP cannot be negative")
    if new_cur < 0:
        raise StateError(f"current HP of {new_cur} is impossible; 0 is the floor and dying tracks the rest")
    if new_cur > new_max:
        raise StateError(f"current HP {new_cur} is above maximum {new_max} — refusing rather than clamping")
    if new_temp < 0:
        raise StateError("temporary HP cannot be negative")
    hp["current"], hp["max"], hp["temp"] = new_cur, new_max, new_temp
    return [f"{pc['name']} HP {new_cur}/{new_max}" + (f" (+{new_temp} temp)" if new_temp else "")]


def set_dying(data: dict[str, Any], who: str, value: int, *, reason: str = "") -> list[str]:
    key, pc = find_character(data, who)
    if value < 0:
        raise StateError("dying cannot be negative")
    before = int(pc.get("dying", 0))
    limit = int(pc.get("dying_max", 4)) - int(pc.get("doomed", 0))
    notes = []
    pc["dying"] = value
    if value == 0 and before > 0:
        pc["wounded"] = int(pc.get("wounded", 0)) + 1
        notes.append(f"{pc['name']} is no longer dying — wounded {pc['wounded']}")
    elif value > 0:
        notes.append(f"{pc['name']} is dying {value}" + (f" ({reason})" if reason else ""))
        if value >= limit:
            notes.append(
                f"⚠ dying {value} meets the death threshold ({pc.get('dying_max', 4)}"
                + (f" reduced to {limit} by doomed {pc.get('doomed', 0)}" if pc.get("doomed") else "")
                + f") — {pc['name']} dies unless something intervenes"
            )
    return notes


def parse_duration(spec: str | None) -> dict[str, Any]:
    if not spec:
        return {"kind": "until-removed", "remaining": None}
    text = str(spec).strip().lower()
    if text in ("eot", "end-of-turn", "end of turn"):
        return {"kind": "end-of-turn", "remaining": None}
    if text in ("permanent", "until-removed", "none", "-"):
        return {"kind": "until-removed", "remaining": None}
    m = re.fullmatch(r"(\d+)\s*(round|rounds|r|minute|minutes|min|m|hour|hours|h|day|days|d)?", text)
    if not m:
        raise StateError(f"cannot read a duration out of {spec!r} (try '2 rounds', '10 minutes', 'end-of-turn')")
    n = int(m.group(1))
    unit = (m.group(2) or "rounds")[0]
    kind = {"r": "rounds", "m": "minutes", "h": "hours", "d": "days"}[unit]
    if "min" in text:
        kind = "minutes"
    return {"kind": kind, "remaining": n}


def condition_add(
    data: dict[str, Any],
    who: str,
    name: str,
    value: int | None,
    duration: str | None,
    source: str | None,
) -> list[str]:
    key, pc = find_character(data, who)
    slug = slugify(name)
    if slug in TRACKED_SEPARATELY:
        raise StateError(
            f"{slug} is tracked as its own field, not as a condition entry — "
            f"use `{slug} set <who> <value>` so there is only one copy of the number"
        )
    if slug not in KNOWN_CONDITIONS:
        raise StateError(
            f"{name!r} is not a PF2e condition. Known: " + ", ".join(sorted(KNOWN_CONDITIONS))
        )
    if slug in VALUED_CONDITIONS:
        if value is None:
            raise StateError(f"{slug} always carries a value — say how much")
        if value < 1:
            raise StateError(f"{slug} {value} is not a condition; remove it instead")
    elif value is not None:
        raise StateError(f"{slug} does not take a value")
    dur = parse_duration(duration)
    conds = pc.setdefault("conditions", [])
    for c in conds:
        if c["name"] == slug:
            if slug in VALUED_CONDITIONS:
                # The stronger value wins; PF2e conditions of the same name do not stack.
                if value is not None and value > int(c.get("value") or 0):
                    c["value"] = value
                    c["duration"] = dur
                    c["source"] = source
                    return [f"{pc['name']}: {slug} raised to {value}"]
                return [f"{pc['name']} already has {slug} {c.get('value')}; the higher value stands"]
            c["duration"] = dur
            return [f"{pc['name']} already has {slug}; duration refreshed"]
    conds.append({"name": slug, "value": value, "duration": dur, "source": source})
    shown = f"{slug} {value}" if value is not None else slug
    return [f"{pc['name']}: {shown} added ({describe_duration(dur)})"]


def describe_duration(dur: dict[str, Any]) -> str:
    kind = dur.get("kind", "until-removed")
    if kind == "until-removed":
        return "until removed"
    if kind == "end-of-turn":
        return "ends at the end of the turn"
    return f"{dur.get('remaining')} {kind}"


def condition_remove(data: dict[str, Any], who: str, name: str) -> list[str]:
    _, pc = find_character(data, who)
    slug = slugify(name)
    conds = pc.setdefault("conditions", [])
    keep = [c for c in conds if c["name"] != slug]
    if len(keep) == len(conds):
        raise StateError(f"{pc['name']} does not have {slug}")
    pc["conditions"] = keep
    return [f"{pc['name']}: {slug} removed"]


def condition_tick(data: dict[str, Any], who: str) -> list[str]:
    """End-of-turn bookkeeping: decrement round durations and drop what expired."""
    _, pc = find_character(data, who)
    notes: list[str] = []
    keep = []
    for c in pc.get("conditions", []):
        dur = c.get("duration") or {"kind": "until-removed"}
        kind = dur.get("kind")
        if kind == "rounds":
            left = int(dur.get("remaining") or 0) - 1
            if left <= 0:
                notes.append(f"{pc['name']}: {c['name']} expired")
                continue
            dur["remaining"] = left
            notes.append(f"{pc['name']}: {c['name']} — {left} round(s) left")
        elif kind == "end-of-turn":
            notes.append(f"{pc['name']}: {c['name']} expired at end of turn")
            continue
        keep.append(c)
    pc["conditions"] = keep
    if pc.get("persistent"):
        notes.append(
            f"{pc['name']} has persistent damage pending: "
            + "; ".join(f"{p.get('expr')} {p.get('type','')}".strip() for p in pc["persistent"])
            + " — roll it and the DC 15 flat check with roll.py, do not resolve it here"
        )
    return notes


# --------------------------------------------------------------------------------------
# Resources
# --------------------------------------------------------------------------------------


def hero_spend(data: dict[str, Any], who: str, n: int = 1) -> list[str]:
    _, pc = find_character(data, who)
    have = int(pc.get("hero_points", 0))
    if have < n:
        raise StateError(f"{pc['name']} has {have} Hero Point(s) and cannot spend {n}")
    pc["hero_points"] = have - n
    return [f"{pc['name']} spends {n} Hero Point → {pc['hero_points']} left"]


def hero_gain(data: dict[str, Any], who: str, n: int = 1) -> list[str]:
    _, pc = find_character(data, who)
    cap = int(pc.get("hero_points_max", 3))
    new = int(pc.get("hero_points", 0)) + n
    if new > cap:
        raise StateError(f"{pc['name']} would hold {new} Hero Points, above the cap of {cap}")
    pc["hero_points"] = new
    return [f"{pc['name']} gains {n} Hero Point → {new}"]


def focus_spend(data: dict[str, Any], who: str, n: int = 1) -> list[str]:
    _, pc = find_character(data, who)
    f = pc.setdefault("focus", {"current": 0, "max": 0, "refocus_available": True})
    if int(f.get("current", 0)) < n:
        raise StateError(f"{pc['name']} has {f.get('current', 0)} Focus Point(s) and cannot spend {n}")
    f["current"] = int(f["current"]) - n
    return [f"{pc['name']} spends {n} Focus Point → {f['current']}/{f.get('max', 0)}"]


def focus_refocus(data: dict[str, Any], who: str, n: int = 1) -> list[str]:
    """Refocus recovers 1 Focus Point (more only with a specific ability that says so)."""
    _, pc = find_character(data, who)
    f = pc.setdefault("focus", {"current": 0, "max": 0, "refocus_available": True})
    if not f.get("refocus_available", True):
        raise StateError(f"{pc['name']} has already Refocused since their last focus spell")
    cap = int(f.get("max", 0))
    if int(f.get("current", 0)) >= cap:
        raise StateError(f"{pc['name']}'s focus pool is already full ({cap})")
    f["current"] = min(cap, int(f.get("current", 0)) + n)
    f["refocus_available"] = False
    return [f"{pc['name']} Refocuses → {f['current']}/{cap}"]


def slots_use(data: dict[str, Any], who: str, rank: str, n: int = 1) -> list[str]:
    _, pc = find_character(data, who)
    slots = pc.setdefault("spell_slots", {})
    key = str(rank)
    if key not in slots:
        raise StateError(f"{pc['name']} has no rank-{key} slots recorded")
    entry = slots[key]
    used = int(entry.get("used", 0)) + n
    if used > int(entry.get("max", 0)):
        raise StateError(
            f"{pc['name']} has {entry.get('max', 0)} rank-{key} slot(s) and {entry.get('used', 0)} already used"
        )
    entry["used"] = used
    return [f"{pc['name']} rank {key}: {used}/{entry['max']} used"]


def daily_prep(data: dict[str, Any]) -> list[str]:
    """Reset what a night's rest and daily preparations restore."""
    notes = []
    for _, pc in data.get("pcs", {}).items():
        for key, entry in pc.get("spell_slots", {}).items():
            entry["used"] = 0
        f = pc.setdefault("focus", {"current": 0, "max": 0, "refocus_available": True})
        f["current"] = int(f.get("max", 0))
        f["refocus_available"] = True
        if int(pc.get("wounded", 0)) > 0:
            pc["wounded"] = max(0, int(pc["wounded"]) - 1)
        if int(pc.get("doomed", 0)) > 0:
            pc["doomed"] = max(0, int(pc["doomed"]) - 1)
        notes.append(f"{pc['name']}: slots and focus restored, wounded {pc.get('wounded', 0)}, doomed {pc.get('doomed', 0)}")
    notes.append("Drained decreases by 1 per night's rest but does not restore the lost HP — adjust by hand.")
    # Source: Player Core Drained, Doomed and Wounded entries (wounded is removed by a
    # successful Treat Wounds or 24 hours; doomed and drained step down by 1 per full rest).
    return notes


# --------------------------------------------------------------------------------------
# Money and items
# --------------------------------------------------------------------------------------

_COIN_RE = re.compile(r"^(\d+)\s*(pp|gp|sp|cp)$", re.IGNORECASE)


def parse_coins(tokens: Iterable[str]) -> dict[str, int]:
    out = {c: 0 for c in COIN_ORDER}
    seen = False
    for tok in tokens:
        for piece in re.findall(r"\d+\s*(?:pp|gp|sp|cp)", str(tok), re.IGNORECASE):
            m = _COIN_RE.match(piece.replace(" ", ""))
            if not m:
                continue
            out[m.group(2).lower()] += int(m.group(1))
            seen = True
    if not seen:
        raise StateError("no coins found — write amounts like '42gp 3sp'")
    return out


def coins_to_cp(coins: dict[str, int]) -> int:
    return sum(int(coins.get(c, 0)) * COIN_IN_CP[c] for c in COIN_ORDER)


def cp_to_coins(total: int) -> dict[str, int]:
    out = {}
    left = total
    for c in COIN_ORDER:
        out[c], left = divmod(left, COIN_IN_CP[c])
    return out


def format_coins(coins: dict[str, int]) -> str:
    parts = [f"{coins[c]} {c}" for c in COIN_ORDER if coins.get(c)]
    return ", ".join(parts) if parts else "0 cp"


def gold_change(data: dict[str, Any], tokens: Sequence[str], sign: int) -> list[str]:
    """Add or spend coins.

    Gaining coins keeps the denominations as received, so a purse reads back as what the
    party actually picked up rather than as the tidiest equivalent. Spending pays from the
    matching denominations first and only breaks larger coins when it has to, which is what
    happens at a table.
    """
    amount = parse_coins(tokens)
    purse = data.setdefault("party", {}).setdefault("gold", {c: 0 for c in COIN_ORDER})
    for c in COIN_ORDER:
        purse.setdefault(c, 0)
    if sign > 0:
        for c in COIN_ORDER:
            purse[c] = int(purse[c]) + int(amount.get(c, 0))
        return [f"party gains {format_coins(amount)} → {format_coins(purse)}"]

    have = coins_to_cp(purse)
    cost = coins_to_cp(amount)
    if cost > have:
        raise StateError(
            f"the party holds {format_coins(purse)} (worth {have} cp) and cannot part with "
            f"{format_coins(amount)} (worth {cost} cp) — refusing to go negative"
        )
    owed = cost
    broke = False
    for c in COIN_ORDER:  # pay from the largest matching denomination down
        want = min(int(amount.get(c, 0)), int(purse[c]))
        if want:
            purse[c] -= want
            owed -= want * COIN_IN_CP[c]
    if owed > 0:
        # Break the largest coins available until the rest is covered, then give change.
        pool = coins_to_cp(purse)
        purse.update(cp_to_coins(pool - owed))
        broke = True
    out = [f"party spends {format_coins(amount)} → {format_coins(purse)}"]
    if broke:
        out.append("(larger coins were broken to make the payment)")
    return out


def gold_set(data: dict[str, Any], tokens: Sequence[str]) -> list[str]:
    coins = parse_coins(tokens)
    if any(v < 0 for v in coins.values()):
        raise StateError("coin counts cannot be negative")
    data.setdefault("party", {})["gold"] = {c: int(coins.get(c, 0)) for c in COIN_ORDER}
    return [f"purse set to {format_coins(data['party']['gold'])}"]


def item_container(data: dict[str, Any], owner: str | None) -> tuple[str, list[dict[str, Any]]]:
    if owner in (None, "", "stash", "party"):
        return "party stash", data.setdefault("party", {}).setdefault("stash", [])
    key, pc = find_character(data, owner)
    return pc["name"], pc.setdefault("items", [])


def item_add(
    data: dict[str, Any],
    name: str,
    qty: int,
    owner: str | None,
    bulk: str | None,
    kind: str | None,
    charges: int | None,
    level: int | None,
) -> list[str]:
    if qty < 1:
        raise StateError(f"cannot add {qty} of an item")
    where, items = item_container(data, owner)
    for it in items:
        if it["name"].lower() == name.lower() and charges is None:
            it["qty"] = int(it.get("qty", 1)) + qty
            return [f"{where}: {it['name']} ×{it['qty']}"]
    items.append(
        {
            "name": name,
            "qty": qty,
            "bulk": bulk if bulk is not None else "-",
            "kind": kind or "gear",  # gear | permanent | consumable | ammunition | container
            "charges": charges,
            "level": level,
        }
    )
    return [f"{where}: added {name} ×{qty}"]


def item_remove(data: dict[str, Any], name: str, qty: int, owner: str | None) -> list[str]:
    where, items = item_container(data, owner)
    for it in items:
        if it["name"].lower() == name.lower():
            have = int(it.get("qty", 1))
            if qty > have:
                raise StateError(f"{where} holds {have} × {it['name']} and cannot give up {qty}")
            it["qty"] = have - qty
            if it["qty"] == 0:
                items.remove(it)
                return [f"{where}: {it['name']} all used up"]
            return [f"{where}: {it['name']} ×{it['qty']}"]
    raise StateError(f"{where} has no item called {name!r}")


def item_use(data: dict[str, Any], name: str, owner: str | None, n: int = 1) -> list[str]:
    where, items = item_container(data, owner)
    for it in items:
        if it["name"].lower() == name.lower():
            if it.get("charges") is not None:
                left = int(it["charges"]) - n
                if left < 0:
                    raise StateError(f"{it['name']} has {it['charges']} charge(s) left and cannot spend {n}")
                it["charges"] = left
                return [f"{where}: {it['name']} — {left} charge(s) left"]
            return item_remove(data, name, n, owner)
    raise StateError(f"{where} has no item called {name!r}")


def bulk_report(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Bulk carried against the encumbered and maximum limits, per carrier.

    Source: Player Core, "Bulk" — 10 light items make 1 Bulk; a creature is encumbered
    while carrying more than 5 + Strength modifier Bulk and cannot carry more than
    10 + Strength modifier. Verified against Foundry VTT PF2e
    src/module/actor/inventory/bulk.ts (`encumberedAfter` = 5 + Str, `max` = 10 + Str).
    """
    rows = []
    for key, pc in data.get("pcs", {}).items():
        tenths = 0
        for it in pc.get("items", []):
            tenths += pf2e.bulk_tenths(it.get("bulk", "-")) * int(it.get("qty", 1))
        str_mod = int(pc.get("str_mod", 0))
        rows.append(
            {
                "id": key,
                "name": pc.get("name", key),
                "bulk_tenths": tenths,
                "bulk": tenths / 10.0,
                "encumbered_after": 5 + str_mod,
                "max": 10 + str_mod,
                "encumbered": tenths > (5 + str_mod) * 10,
                "over_max": tenths > (10 + str_mod) * 10,
            }
        )
    return rows


# --------------------------------------------------------------------------------------
# Clocks, quests, time, location
# --------------------------------------------------------------------------------------


def clock_add(data: dict[str, Any], name: str, segments: int, ticking: bool, rate: str | None, note: str) -> list[str]:
    if segments < 1:
        raise StateError("a clock needs at least one segment")
    clocks = data.setdefault("clocks", {})
    if name in clocks:
        raise StateError(f"a clock called {name!r} already exists")
    clocks[name] = {
        "filled": 0,
        "segments": segments,
        "ticking": bool(ticking),
        "rate": rate,
        "note": note,
        "complete": False,
    }
    return [f"clock '{name}': 0/{segments}" + (f", ticks {rate}" if ticking and rate else "")]


def clock_advance(data: dict[str, Any], name: str, n: int) -> list[str]:
    clocks = data.setdefault("clocks", {})
    if name not in clocks:
        matches = [k for k in clocks if name.lower() in k.lower()]
        if len(matches) == 1:
            name = matches[0]
        else:
            raise StateError(f"no clock called {name!r} (have: {', '.join(sorted(clocks)) or 'none'})")
    c = clocks[name]
    filled = int(c["filled"]) + n
    if filled < 0:
        raise StateError(f"clock '{name}' cannot go below 0 segments")
    seg = int(c["segments"])
    notes = []
    if filled >= seg:
        filled = seg
        if not c.get("complete"):
            notes.append(f"⚠ clock '{name}' is FULL ({seg}/{seg}) — it happens")
        c["complete"] = True
    else:
        c["complete"] = False
    c["filled"] = filled
    bar = "▰" * filled + "▱" * (seg - filled)
    notes.insert(0, f"clock '{name}': {bar} {filled}/{seg}")
    return notes


def quest_set(data: dict[str, Any], name: str, status: str, lead: str | None) -> list[str]:
    ok = ("active", "dormant", "completed", "failed")
    if status not in ok:
        raise StateError(f"quest status must be one of {', '.join(ok)}")
    q = data.setdefault("quests", {})
    entry = q.setdefault(name, {"status": "active", "lead": ""})
    entry["status"] = status
    if lead is not None:
        entry["lead"] = lead
    return [f"quest '{name}': {status}" + (f" — next lead: {entry['lead']}" if entry.get("lead") else "")]


# --------------------------------------------------------------------------------------
# The encounter tracker — the thing a mid-combat checkpoint has to restore exactly
# --------------------------------------------------------------------------------------


def blank_combatant(name: str, side: str, **kw: Any) -> dict[str, Any]:
    c = {
        "id": kw.get("id") or slugify(name),
        "name": name,
        "side": side,  # party | adversary | neutral
        "ref": kw.get("ref"),  # a key in state["pcs"]; HP and conditions live there
        "initiative": kw.get("initiative"),
        "initiative_natural": kw.get("initiative_natural"),
        "hp": None if kw.get("ref") else {"current": kw.get("hp", 0), "max": kw.get("hp", 0), "temp": 0},
        "conditions": [] if not kw.get("ref") else None,
        "dying": 0 if not kw.get("ref") else None,
        "actions_remaining": 3,
        "actions_spent": 0,
        "map_step": 0,
        "reaction_available": True,
        "reaction_used_for": None,
        "position": kw.get("position"),
        "squad": kw.get("squad"),
        "persistent": [],
        "sustained": [],
        "level": kw.get("level"),
        "notes": kw.get("notes", ""),
        "defeated": False,
    }
    return c


def encounter_start(data: dict[str, Any], name: str, objective: str, map_slug: str | None) -> list[str]:
    if data.get("encounter"):
        raise StateError("an encounter is already live; end it before starting another")
    if not objective:
        raise StateError(
            "every encounter names its objective (see system/17-encounter-objectives.md) — pass --objective"
        )
    data["encounter"] = {
        "name": name,
        "objective": objective,
        "map": map_slug,
        "round": 1,
        "turn_index": 0,
        "started_at": utc_now(),
        "combatants": [],
        "log": [],
        "telegraphed": False,
    }
    return [f"encounter '{name}' started — objective: {objective}"]


def _enc(data: dict[str, Any]) -> dict[str, Any]:
    e = data.get("encounter")
    if not e:
        raise StateError("no encounter is live")
    return e


def find_combatant(data: dict[str, Any], who: str) -> dict[str, Any]:
    e = _enc(data)
    want = who.lower()
    for c in e["combatants"]:
        if c["id"].lower() == want or c["name"].lower() == want or slugify(who) == c["id"]:
            return c
    raise StateError(f"no combatant {who!r} (have: {', '.join(c['id'] for c in e['combatants']) or 'none'})")


def combatant_hp(data: dict[str, Any], c: dict[str, Any]) -> dict[str, Any] | None:
    """HP for a combatant. Party members point at `pcs`, so there is one copy only."""
    if c.get("ref"):
        try:
            _, pc = find_character(data, c["ref"])
        except StateError:
            return None
        return pc["hp"]
    return c.get("hp")


def encounter_add(data: dict[str, Any], name: str, side: str, **kw: Any) -> list[str]:
    e = _enc(data)
    if side not in ("party", "adversary", "neutral"):
        raise StateError("side must be party, adversary or neutral")
    if kw.get("ref"):
        find_character(data, kw["ref"])  # raises if absent
    c = blank_combatant(name, side, **kw)
    if any(x["id"] == c["id"] for x in e["combatants"]):
        raise StateError(f"a combatant with id {c['id']!r} is already in this encounter")
    e["combatants"].append(c)
    sort_combatants(e)
    return [f"{name} joins the encounter on the {side} side" + (f" at initiative {c['initiative']}" if c["initiative"] is not None else "")]


def sort_combatants(e: dict[str, Any]) -> None:
    """Descending initiative; on a cross-side tie the adversary acts first."""
    e["combatants"].sort(
        key=lambda c: (
            -(c.get("initiative") if c.get("initiative") is not None else -999),
            0 if c.get("side") != "party" else 1,
            c["id"],
        )
    )


def encounter_next(data: dict[str, Any]) -> list[str]:
    """Advance to the next combatant's turn, resetting their per-turn resources."""
    e = _enc(data)
    live = e["combatants"]
    if not live:
        raise StateError("this encounter has no combatants")
    notes: list[str] = []
    idx = int(e.get("turn_index", 0))
    current = live[idx] if 0 <= idx < len(live) else None
    if current is not None and current.get("ref"):
        notes += condition_tick(data, current["ref"])
    idx += 1
    if idx >= len(live):
        idx = 0
        e["round"] = int(e.get("round", 1)) + 1
        notes.append(f"— round {e['round']} —")
    e["turn_index"] = idx
    nxt = live[idx]
    nxt["actions_remaining"] = 3
    nxt["actions_spent"] = 0
    nxt["map_step"] = 0
    nxt["reaction_available"] = True
    nxt["reaction_used_for"] = None
    notes.append(f"{nxt['name']}'s turn (round {e['round']}), ◆◆◆, reaction available")
    return notes


def encounter_action(data: dict[str, Any], who: str, n: int) -> list[str]:
    c = find_combatant(data, who)
    left = int(c["actions_remaining"]) - n
    if left < 0:
        raise StateError(f"{c['name']} has {c['actions_remaining']} action(s) left and cannot spend {n}")
    c["actions_remaining"] = left
    c["actions_spent"] = int(c["actions_spent"]) + n
    pips = "◆" * left + "◇" * (3 - left) if left <= 3 else f"{left} actions"
    return [f"{c['name']}: {pips} ({left} left)"]


def encounter_map_step(data: dict[str, Any], who: str, step: int | None) -> list[str]:
    c = find_combatant(data, who)
    new = int(c["map_step"]) + 1 if step is None else step
    if new < 0 or new > 2:
        raise StateError("the multiple attack penalty has steps 0, 1 and 2 only")
    c["map_step"] = new
    pen = pf2e.map_penalty(new, agile=False)
    agile = pf2e.map_penalty(new, agile=True)
    return [f"{c['name']}: MAP step {new} → {pen:+d} (agile {agile:+d})"]


def encounter_reaction(data: dict[str, Any], who: str, what: str | None, restore: bool) -> list[str]:
    c = find_combatant(data, who)
    if restore:
        c["reaction_available"] = True
        c["reaction_used_for"] = None
        return [f"{c['name']}: reaction available again"]
    if not c["reaction_available"]:
        raise StateError(f"{c['name']} has already used their reaction this round (for {c['reaction_used_for']})")
    c["reaction_available"] = False
    c["reaction_used_for"] = what or "unspecified"
    return [f"{c['name']}: reaction spent on {c['reaction_used_for']}"]


def encounter_position(data: dict[str, Any], who: str, cell: str) -> list[str]:
    c = find_combatant(data, who)
    c["position"] = cell
    return [f"{c['name']} is at {cell}"]


def encounter_hp(data: dict[str, Any], who: str, current: int | None, maximum: int | None) -> list[str]:
    c = find_combatant(data, who)
    if c.get("ref"):
        return set_hp(data, c["ref"], current, maximum, None)
    hp = c["hp"] or {"current": 0, "max": 0, "temp": 0}
    new_max = hp["max"] if maximum is None else maximum
    new_cur = hp["current"] if current is None else current
    if new_cur > new_max:
        raise StateError(f"{c['name']} current HP {new_cur} is above maximum {new_max}")
    if new_cur < 0:
        raise StateError("HP cannot be negative")
    hp["current"], hp["max"] = new_cur, new_max
    c["hp"] = hp
    if new_cur == 0:
        c["defeated"] = True
    return [f"{c['name']} HP {new_cur}/{new_max}" + (" — down" if new_cur == 0 else "")]


def encounter_end(data: dict[str, Any]) -> list[str]:
    e = _enc(data)
    rounds = e.get("round", 1)
    name = e.get("name")
    data["encounter"] = None
    return [
        f"encounter '{name}' ended after {rounds} round(s)",
        "Now: award XP, record treasure, note which conditions persist, write the",
        "encounters/history.md entry with its Objective: field, and take a checkpoint.",
    ]


def encounter_status(data: dict[str, Any]) -> list[str]:
    e = data.get("encounter")
    if not e:
        return ["no encounter is live"]
    out = [f"{e['name']} — round {e['round']}, objective: {e['objective']}"]
    if e.get("map"):
        out.append(f"map: maps/{e['map']}.md")
    out.append("")
    out.append(f"{'':2} {'combatant':<22} {'init':>4} {'HP':>12} {'act':<4} {'MAP':>4} {'rxn':<4} {'pos':<5} conditions")
    for i, c in enumerate(e["combatants"]):
        hp = combatant_hp(data, c)
        hp_s = f"{hp['current']}/{hp['max']}" if hp else "?"
        conds: list[dict[str, Any]] = []
        dying = 0
        if c.get("ref"):
            try:
                _, pc = find_character(data, c["ref"])
            except StateError:
                cs_note = f"⚠ ref {c['ref']!r} has no character in pcs"
                conds = [{"name": cs_note}]
            else:
                conds = pc.get("conditions", [])
                dying = int(pc.get("dying", 0))
        else:
            conds = c.get("conditions") or []
            dying = int(c.get("dying") or 0)
        cs = ", ".join(f"{x['name']}{' ' + str(x['value']) if x.get('value') else ''}" for x in conds)
        if dying:
            cs = f"dying {dying}" + (f", {cs}" if cs else "")
        mark = "→" if i == int(e.get("turn_index", 0)) else " "
        pips = "◆" * int(c["actions_remaining"]) + "◇" * (3 - int(c["actions_remaining"]))
        rxn = "yes" if c["reaction_available"] else "used"
        out.append(
            f"{mark:2} {c['name']:<22} {str(c.get('initiative') or '-'):>4} {hp_s:>12} "
            f"{pips:<4} {c['map_step']:>4} {rxn:<4} {str(c.get('position') or '-'):<5} {cs}"
        )
    return out


# --------------------------------------------------------------------------------------
# Rendering CHECKPOINT.md
# --------------------------------------------------------------------------------------


def render_checkpoint(slug: str, data: dict[str, Any]) -> str:
    """CHECKPOINT.md is generated from state.json. Never hand-edit it."""
    L: list[str] = []
    a = L.append
    title = data.get("title") or slug
    a(f"# {title} — current state")
    a("")
    a("> Rendered from `state.json` by `tools/state.py render`. **Do not hand-edit this file.**")
    a("> If a number here disagrees with `state.json`, `state.json` wins and this gets re-rendered.")
    a("")
    cp = data.get("last_checkpoint") or {}
    a(f"- Checkpoint: **{cp.get('id', '—')}** {cp.get('name', '')}".rstrip())
    a(f"- Rendered at: {utc_now()}")
    a(f"- Session: {data.get('session_number', 0)}"
      f" ({'in progress' if data.get('session_in_progress') else 'not in session'})")
    a(f"- Party level {data.get('party', {}).get('level', 1)}, "
      f"{data.get('party', {}).get('xp', 0)} XP")
    a(f"- Transparency mode: `{data.get('transparency', 'standard')}` — "
      f"difficulty preset: **{data.get('difficulty_preset', 'Standard')}**")
    a("")
    a("## Scene")
    a("")
    a(f"- **Where:** {data.get('location', 'unset')}")
    a(f"- **When:** {pf2e.format_time(data.get('time', {}))}")
    sit = (data.get("notes") or {}).get("situation") or "_(no situation paragraph recorded yet)_"
    a("")
    a(sit)
    a("")

    a("## Party")
    a("")
    a("| Character | HP | AC | Fort | Ref | Will | Perc | Hero | Focus | Conditions |")
    a("|---|---|---|---|---|---|---|---|---|---|")
    for key, pc in data.get("pcs", {}).items():
        hp = pc.get("hp", {})
        temp = f" +{hp.get('temp')}t" if hp.get("temp") else ""
        s = pc.get("saves", {})
        f = pc.get("focus", {})
        focus = f"{f.get('current', 0)}/{f.get('max', 0)}" + ("" if f.get("refocus_available", True) else " (refocused)")
        conds = []
        for c in pc.get("conditions", []):
            conds.append(f"{c['name']}" + (f" {c['value']}" if c.get("value") else "") +
                         (f" [{describe_duration(c.get('duration') or {})}]" if (c.get("duration") or {}).get("kind") != "until-removed" else ""))
        for name in ("dying", "wounded", "doomed"):
            if int(pc.get(name, 0)):
                conds.insert(0, f"**{name} {pc[name]}**")
        a(f"| {pc.get('name', key)} | {hp.get('current', 0)}/{hp.get('max', 0)}{temp} | {pc.get('ac', 0)} | "
          f"{s.get('fortitude', 0):+d} | {s.get('reflex', 0):+d} | {s.get('will', 0):+d} | "
          f"{pc.get('perception', 0):+d} | {pc.get('hero_points', 0)} | {focus} | {', '.join(conds) or '—'} |")
    a("")

    slotted = [(k, pc) for k, pc in data.get("pcs", {}).items() if pc.get("spell_slots")]
    if slotted:
        a("### Spell slots")
        a("")
        for key, pc in slotted:
            bits = []
            for rank in sorted(pc["spell_slots"], key=lambda r: int(r)):
                e = pc["spell_slots"][rank]
                bits.append(f"rank {rank}: {int(e.get('max', 0)) - int(e.get('used', 0))}/{e.get('max', 0)}")
            a(f"- **{pc.get('name', key)}** — " + "; ".join(bits))
        a("")

    a("## Money and carried items")
    a("")
    a(f"- **Purse:** {format_coins(data.get('party', {}).get('gold', {}))}")
    for row in bulk_report(data):
        flag = " — **OVER THE LIMIT**" if row["over_max"] else (" — **encumbered**" if row["encumbered"] else "")
        a(f"- **{row['name']}** Bulk {row['bulk']:.1f} "
          f"(encumbered after {row['encumbered_after']}, max {row['max']}){flag}")
    for key, pc in data.get("pcs", {}).items():
        items = pc.get("items", [])
        if not items:
            continue
        a(f"  - {pc.get('name', key)}: " + ", ".join(
            f"{it['name']}"
            + (f" ×{it['qty']}" if int(it.get("qty", 1)) > 1 else "")
            + (f" ({it['charges']} charges)" if it.get("charges") is not None else "")
            for it in items
        ))
    stash = data.get("party", {}).get("stash", [])
    if stash:
        a("  - stash (not carried): " + ", ".join(
            f"{it['name']}" + (f" ×{it['qty']}" if int(it.get('qty', 1)) > 1 else "") for it in stash))
    a("")

    clocks = data.get("clocks", {})
    if clocks:
        a("## Clocks")
        a("")
        for name, c in clocks.items():
            seg, filled = int(c["segments"]), int(c["filled"])
            bar = "▰" * filled + "▱" * (seg - filled)
            tick = f" — ticks {c['rate']}" if c.get("ticking") and c.get("rate") else ""
            note = f" · {c['note']}" if c.get("note") else ""
            a(f"- **{name}** `{bar}` {filled}/{seg}{tick}{note}")
        a("")

    quests = data.get("quests", {})
    if quests:
        a("## Quests")
        a("")
        for name, q in quests.items():
            a(f"- **{name}** — {q.get('status')}" + (f" · next lead: {q['lead']}" if q.get("lead") else ""))
        a("")

    if data.get("encounter"):
        a("## Live encounter")
        a("")
        a("```")
        L.extend(encounter_status(data))
        a("```")
        a("")
        a("This encounter is mid-fight. Restoring this checkpoint restores the tracker exactly:")
        a("initiative order, current turn, actions spent, MAP step, reactions, HP, conditions and positions.")
        a("")

    beats = (data.get("notes") or {}).get("next_beats")
    if beats:
        a("## Next likely beats")
        a("")
        a(beats)
        a("")

    a("---")
    a("")
    a("Deep history lives in `sessions/` and `CANON.md`, not here — this file stays cheap to reload.")
    return "\n".join(L) + "\n"


def write_render(slug: str, data: dict[str, Any]) -> Path:
    p = campaign_dir(slug) / "CHECKPOINT.md"
    atomic_write(p, render_checkpoint(slug, data))
    return p


# --------------------------------------------------------------------------------------
# Checkpoints, git, dashboard
# --------------------------------------------------------------------------------------


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=str(repo_root()), capture_output=True, text=True, check=check
    )


def git_available() -> bool:
    if shutil.which("git") is None:
        return False
    return git("rev-parse", "--git-dir", check=False).returncode == 0


def regenerate_dashboard(slug: str) -> tuple[bool, str]:
    script = repo_root() / "tools" / "dashboard.py"
    if not script.exists():
        return False, "tools/dashboard.py is not present"
    proc = subprocess.run(
        [sys.executable, str(script), "--campaign", slug],
        capture_output=True,
        text=True,
        cwd=str(repo_root()),
    )
    if proc.returncode != 0:
        return False, (proc.stderr or proc.stdout).strip()
    return True, (proc.stdout or "").strip()


def checkpoint(
    slug: str,
    data: dict[str, Any],
    message: str,
    *,
    commit: bool = True,
    dashboard: bool = True,
    situation: str | None = None,
    next_beats: str | None = None,
) -> tuple[dict[str, Any], list[str]]:
    notes: list[str] = []
    n = int(data.get("checkpoint_counter", 0)) + 1
    cid = f"{n:03d}"
    cslug = slugify(message)[:60] or "checkpoint"
    if situation is not None:
        data.setdefault("notes", {})["situation"] = situation
    if next_beats is not None:
        data.setdefault("notes", {})["next_beats"] = next_beats

    data["checkpoint_counter"] = n
    data["last_checkpoint"] = {"id": cid, "name": message, "at": utc_now(), "slug": cslug}
    save(slug, data)
    write_render(slug, data)

    cdir = campaign_dir(slug) / "checkpoints"
    cpath = cdir / f"{cid}-{cslug}.md"
    atomic_write(cpath, render_snapshot(slug, data, cid, message))
    notes.append(f"wrote {cpath.relative_to(repo_root())}")

    if dashboard:
        ok, msg = regenerate_dashboard(slug)
        notes.append(f"dashboard regenerated" if ok else f"dashboard NOT regenerated: {msg}")

    if commit:
        if not git_available():
            notes.append("⚠ git is unavailable, so this checkpoint is NOT committed. Nothing was skipped silently.")
        else:
            rel = f"campaigns/{slug}"
            git("add", "-A", rel, check=False)
            staged = git("diff", "--cached", "--name-only", "--", rel, check=False).stdout.strip()
            if not staged:
                notes.append("nothing changed since the last commit, so no new commit was made")
            else:
                msg = f"checkpoint {cid}: {message}"
                proc = git("commit", "-q", "-m", msg, "--", rel, check=False)
                if proc.returncode != 0:
                    notes.append(f"⚠ commit failed: {(proc.stderr or proc.stdout).strip()}")
                else:
                    sha = git("rev-parse", "--short", "HEAD", check=False).stdout.strip()
                    notes.append(f"committed {sha} — {msg}")
    else:
        notes.append("not committed (--no-commit)")
    return data["last_checkpoint"], notes


SNAP_BEGIN = "<!-- STATE-SNAPSHOT-BEGIN -->"
SNAP_END = "<!-- STATE-SNAPSHOT-END -->"


def render_snapshot(slug: str, data: dict[str, Any], cid: str, message: str) -> str:
    notes = data.get("notes") or {}
    enc = data.get("encounter")
    L = [
        f"# Checkpoint {cid} — {message}",
        "",
        "**Immutable.** Never edit a past checkpoint. Restore it with "
        f"`python3 tools/state.py --campaign {slug} restore {cid}`.",
        "",
        f"- Taken: {utc_now()}",
        f"- In-world: {pf2e.format_time(data.get('time', {}))}",
        f"- Location: {data.get('location', 'unset')}",
        f"- Session: {data.get('session_number', 0)}",
        "- Mid-combat: " + (f"yes — {enc['name']}, round {enc['round']}" if enc else "no"),
        "",
        "## Where we are",
        "",
        notes.get("situation") or "_(no situation paragraph recorded)_",
        "",
        "## Immediate situation",
        "",
        f"- Who is present: {notes.get('present', '_unrecorded_')}",
        f"- What is about to happen: {notes.get('pending', '_unrecorded_')}",
        "",
    ]
    if enc:
        L += ["## Encounter tracker at this moment", "", "```"] + encounter_status(data) + ["```", ""]
    L += ["## Active conditions and effects", ""]
    any_cond = False
    for key, pc in data.get("pcs", {}).items():
        bits = [f"{c['name']}" + (f" {c['value']}" if c.get("value") else "") +
                f" ({describe_duration(c.get('duration') or {})})" for c in pc.get("conditions", [])]
        for n2 in ("dying", "wounded", "doomed"):
            if int(pc.get(n2, 0)):
                bits.insert(0, f"{n2} {pc[n2]}")
        if bits:
            any_cond = True
            L.append(f"- **{pc.get('name', key)}**: " + "; ".join(bits))
    if not any_cond:
        L.append("- none")
    L += ["", "## Clocks (what the world is doing off-screen)", ""]
    if data.get("clocks"):
        for name, c in data["clocks"].items():
            seg, filled = int(c["segments"]), int(c["filled"])
            L.append(f"- **{name}** `{'▰' * filled}{'▱' * (seg - filled)}` {filled}/{seg}"
                     + (f" — ticks {c['rate']}" if c.get("ticking") and c.get("rate") else ""))
    else:
        L.append("- none")
    L += ["", "## Unresolved threads", ""]
    if data.get("quests"):
        for name, q in data["quests"].items():
            if q.get("status") in ("active", "dormant"):
                L.append(f"- **{name}** ({q['status']})" + (f" — {q.get('lead')}" if q.get("lead") else ""))
    else:
        L.append("- see QUESTS.md")
    L += ["", "## Next likely beats", "", notes.get("next_beats") or "_(unrecorded)_", ""]
    L += [
        "## State snapshot",
        "",
        "The canonical machine-readable state at this moment. `restore` reads this block.",
        "",
        SNAP_BEGIN,
        "```json",
        json.dumps(data, indent=2, ensure_ascii=False),
        "```",
        SNAP_END,
        "",
    ]
    return "\n".join(L) + "\n"


def find_snapshot(slug: str, cid: str) -> Path:
    cdir = campaign_dir(slug) / "checkpoints"
    if not cdir.is_dir():
        raise StateError(f"{slug} has no checkpoints/ directory yet")
    key = cid.strip()
    if key.isdigit():
        key = f"{int(key):03d}"
    hits = sorted(p for p in cdir.glob(f"{key}-*.md"))
    if not hits:
        hits = sorted(p for p in cdir.glob("*.md") if p.stem.startswith(key))
    if not hits:
        have = ", ".join(sorted(p.stem for p in cdir.glob("*.md"))) or "none"
        raise StateError(f"no checkpoint {cid!r} (have: {have})")
    return hits[-1]


def read_snapshot(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if SNAP_BEGIN not in text or SNAP_END not in text:
        raise StateError(f"{path} has no state snapshot block")
    body = text.split(SNAP_BEGIN, 1)[1].split(SNAP_END, 1)[0]
    m = re.search(r"```json\s*(.*?)\s*```", body, re.DOTALL)
    if not m:
        raise StateError(f"{path}'s snapshot block holds no json fence")
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError as exc:
        raise StateError(
            f"{path}'s snapshot is not valid JSON ({exc}). Fall back to "
            f"`git log --oneline -- {path}` and `git restore` against the checkpoint's commit."
        ) from exc


def highest_checkpoint(slug: str) -> int:
    """The largest checkpoint number on disk, so a restore never rewinds the counter."""
    cdir = campaign_dir(slug) / "checkpoints"
    if not cdir.is_dir():
        return 0
    best = 0
    for p in cdir.glob("*.md"):
        m = re.match(r"(\d+)-", p.name)
        if m:
            best = max(best, int(m.group(1)))
    return best


def restore(slug: str, cid: str, *, commit: bool = True, dashboard: bool = True) -> list[str]:
    path = find_snapshot(slug, cid)
    data = read_snapshot(path)
    if data.get("campaign") != slug:
        raise StateError(f"{path} belongs to campaign {data.get('campaign')!r}, not {slug!r}")
    # The counter never rewinds. A restore is history, not an erasure: the next checkpoint
    # takes a fresh number, so `restore NNN` can never become ambiguous between two snapshots.
    data["checkpoint_counter"] = max(int(data.get("checkpoint_counter", 0)), highest_checkpoint(slug))
    save(slug, data)
    write_render(slug, data)
    notes = [f"restored {path.relative_to(repo_root())}",
             f"state.json and CHECKPOINT.md now match checkpoint {data.get('last_checkpoint', {}).get('id')}"]
    if dashboard:
        ok, msg = regenerate_dashboard(slug)
        notes.append("dashboard regenerated" if ok else f"dashboard NOT regenerated: {msg}")
    if commit and git_available():
        rel = f"campaigns/{slug}"
        git("add", "-A", rel, check=False)
        if git("diff", "--cached", "--name-only", "--", rel, check=False).stdout.strip():
            cpid = (data.get("last_checkpoint") or {}).get("id", cid)
            git("commit", "-q", "-m", f"restore: rewind to checkpoint {cpid}", "--", rel, check=False)
            notes.append(f"committed the rewind ({git('rev-parse', '--short', 'HEAD', check=False).stdout.strip()})")
        else:
            notes.append("nothing to commit — state already matched that checkpoint")
    notes.append("Narrate from the snapshot's situation paragraph. Rewinding is a legitimate table move.")
    return notes


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="state.py", description="Read and mutate a campaign's canonical state.")
    ap.add_argument("--campaign", required=True, help="campaign slug under campaigns/")
    ap.add_argument("--json", action="store_true", help="machine-readable output where it applies")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("show", help="print the whole state as JSON")
    p = sub.add_parser("get", help="read a dotted path, e.g. pcs.kaelen.hp")
    p.add_argument("path")
    p = sub.add_parser("set", help="write a dotted path (JSON value if parseable)")
    p.add_argument("path")
    p.add_argument("value")

    p = sub.add_parser("init", help="create a blank state.json")
    p.add_argument("--title", default="")
    p.add_argument("--transparency", default="standard")
    p.add_argument("--force", action="store_true")

    p = sub.add_parser("add-character", help="add a PC, ally, sidekick or companion")
    p.add_argument("name")
    p.add_argument("--kind", default="pc", choices=["pc", "ally", "sidekick", "companion", "familiar", "eidolon"])
    p.add_argument("--level", type=int, default=1)
    p.add_argument("--hp", type=int, default=0)
    p.add_argument("--ac", type=int, default=0)
    p.add_argument("--fort", type=int, default=0)
    p.add_argument("--ref", type=int, default=0)
    p.add_argument("--will", type=int, default=0)
    p.add_argument("--perception", type=int, default=0)
    p.add_argument("--speed", type=int, default=25)
    p.add_argument("--str-mod", type=int, default=0)
    p.add_argument("--hero-points", type=int, default=1)
    p.add_argument("--sheet", default=None)

    p = sub.add_parser("damage")
    p.add_argument("who")
    p.add_argument("amount", type=int)
    p.add_argument("--from-crit", action="store_true", help="a critical hit or a critical failure on a save")
    p = sub.add_parser("heal")
    p.add_argument("who")
    p.add_argument("amount", type=int)
    p = sub.add_parser("hp", help="set HP directly")
    p.add_argument("who")
    p.add_argument("--current", type=int)
    p.add_argument("--max", dest="maximum", type=int)
    p.add_argument("--temp", type=int)

    p = sub.add_parser("condition")
    csub = p.add_subparsers(dest="sub", required=True)
    q = csub.add_parser("add")
    q.add_argument("who")
    q.add_argument("name")
    q.add_argument("value", nargs="?", type=int)
    q.add_argument("--duration", default=None, help="'2 rounds', '10 minutes', 'end-of-turn'")
    q.add_argument("--source", default=None)
    q = csub.add_parser("remove")
    q.add_argument("who")
    q.add_argument("name")
    q = csub.add_parser("tick", help="end-of-turn: decrement durations and drop what expired")
    q.add_argument("who")
    q = csub.add_parser("list")
    q.add_argument("who")

    for name in ("dying", "wounded", "doomed"):
        p = sub.add_parser(name)
        q = p.add_subparsers(dest="sub", required=True)
        r = q.add_parser("set")
        r.add_argument("who")
        r.add_argument("value", type=int)

    p = sub.add_parser("recovery", help="roll a real recovery check and apply the result")
    p.add_argument("who")

    p = sub.add_parser("hero")
    q = p.add_subparsers(dest="sub", required=True)
    for verb in ("spend", "gain"):
        r = q.add_parser(verb)
        r.add_argument("who")
        r.add_argument("n", nargs="?", type=int, default=1)
    r = q.add_parser("set")
    r.add_argument("who")
    r.add_argument("n", type=int)

    p = sub.add_parser("focus")
    q = p.add_subparsers(dest="sub", required=True)
    r = q.add_parser("spend")
    r.add_argument("who")
    r.add_argument("n", nargs="?", type=int, default=1)
    r = q.add_parser("refocus")
    r.add_argument("who")
    r = q.add_parser("set")
    r.add_argument("who")
    r.add_argument("current", type=int)
    r.add_argument("--max", dest="maximum", type=int)

    p = sub.add_parser("slots")
    q = p.add_subparsers(dest="sub", required=True)
    r = q.add_parser("use")
    r.add_argument("who")
    r.add_argument("rank")
    r.add_argument("n", nargs="?", type=int, default=1)
    r = q.add_parser("set")
    r.add_argument("who")
    r.add_argument("rank")
    r.add_argument("max", type=int)
    r = q.add_parser("reset")
    r.add_argument("who")

    sub.add_parser("daily-prep", help="a night's rest: slots, focus, wounded/doomed step-down")

    p = sub.add_parser("gold")
    q = p.add_subparsers(dest="sub", required=True)
    for verb in ("add", "spend", "set"):
        r = q.add_parser(verb)
        r.add_argument("coins", nargs="+", help="e.g. 42gp 3sp")

    p = sub.add_parser("item")
    q = p.add_subparsers(dest="sub", required=True)
    r = q.add_parser("add")
    r.add_argument("name")
    r.add_argument("qty", nargs="?", type=int, default=1)
    r.add_argument("--owner", default=None, help="character id, or omit for the party stash")
    r.add_argument("--bulk", default="-", help="'1', '2', 'L' for light, '-' for negligible")
    r.add_argument("--kind", default="gear", choices=["gear", "permanent", "consumable", "ammunition", "container"])
    r.add_argument("--charges", type=int, default=None)
    r.add_argument("--level", type=int, default=None)
    r = q.add_parser("remove")
    r.add_argument("name")
    r.add_argument("qty", nargs="?", type=int, default=1)
    r.add_argument("--owner", default=None)
    r = q.add_parser("use")
    r.add_argument("name")
    r.add_argument("--owner", default=None)
    r.add_argument("-n", type=int, default=1)
    q.add_parser("list")

    p = sub.add_parser("clock")
    q = p.add_subparsers(dest="sub", required=True)
    r = q.add_parser("add")
    r.add_argument("name")
    r.add_argument("segments", type=int)
    r.add_argument("--ticking", action="store_true", help="advances on a schedule during an off-screen turn")
    r.add_argument("--rate", default=None, help="e.g. '1 per week'")
    r.add_argument("--note", default="")
    r = q.add_parser("advance")
    r.add_argument("name")
    r.add_argument("n", nargs="?", type=int, default=1)
    q.add_parser("list")

    p = sub.add_parser("quest")
    q = p.add_subparsers(dest="sub", required=True)
    r = q.add_parser("set")
    r.add_argument("name")
    r.add_argument("status", choices=["active", "dormant", "completed", "failed"])
    r.add_argument("--lead", default=None)

    p = sub.add_parser("advance-time")
    p.add_argument("amount", nargs="+", help="e.g. '4 hours', '10 minutes', '1 day'")

    p = sub.add_parser("location")
    p.add_argument("where", nargs="+")

    p = sub.add_parser("transparency")
    p.add_argument("mode", choices=["glass", "standard", "mystery"])

    p = sub.add_parser("preset", help="record the difficulty preset in force")
    p.add_argument("name")

    p = sub.add_parser("xp")
    q = p.add_subparsers(dest="sub", required=True)
    r = q.add_parser("add")
    r.add_argument("n", type=int)
    r = q.add_parser("set")
    r.add_argument("n", type=int)

    p = sub.add_parser("level")
    q = p.add_subparsers(dest="sub", required=True)
    r = q.add_parser("set")
    r.add_argument("n", type=int)
    r.add_argument("--who", default=None, help="one character, or omit for the party and everyone in it")

    p = sub.add_parser("session")
    q = p.add_subparsers(dest="sub", required=True)
    r = q.add_parser("start")
    r.add_argument("--number", type=int, default=None)
    q.add_parser("end")
    r = q.add_parser("scene")
    r.add_argument("n", nargs="?", type=int, default=1)

    p = sub.add_parser("note", help="set the situation / next-beats / present / pending notes")
    p.add_argument("field", choices=["situation", "next_beats", "present", "pending"])
    p.add_argument("text", nargs="+")

    p = sub.add_parser("encounter")
    q = p.add_subparsers(dest="sub", required=True)
    r = q.add_parser("start")
    r.add_argument("name")
    r.add_argument("--objective", required=True)
    r.add_argument("--map", dest="map_slug", default=None)
    r = q.add_parser("add")
    r.add_argument("name")
    r.add_argument("--side", required=True, choices=["party", "adversary", "neutral"])
    r.add_argument("--ref", default=None, help="a character key; HP and conditions stay in pcs")
    r.add_argument("--init", dest="initiative", type=int, default=None)
    r.add_argument("--hp", type=int, default=0)
    r.add_argument("--position", default=None)
    r.add_argument("--squad", default=None)
    r.add_argument("--level", type=int, default=None)
    r.add_argument("--id", default=None)
    r.add_argument("--notes", default="")
    q.add_parser("next")
    q.add_parser("status")
    q.add_parser("end")
    r = q.add_parser("action")
    r.add_argument("who")
    r.add_argument("n", nargs="?", type=int, default=1)
    r = q.add_parser("map-step")
    r.add_argument("who")
    r.add_argument("step", nargs="?", type=int, default=None)
    r = q.add_parser("reaction")
    r.add_argument("who")
    r.add_argument("what", nargs="?", default=None)
    r.add_argument("--restore", action="store_true")
    r = q.add_parser("position")
    r.add_argument("who")
    r.add_argument("cell")
    r = q.add_parser("hp")
    r.add_argument("who")
    r.add_argument("--current", type=int)
    r.add_argument("--max", dest="maximum", type=int)
    r = q.add_parser("telegraph")
    r.add_argument("text", nargs="*")

    sub.add_parser("render", help="rewrite CHECKPOINT.md from state.json")
    sub.add_parser("bulk", help="report Bulk carried against the limits")

    p = sub.add_parser("checkpoint")
    p.add_argument("message")
    p.add_argument("--situation", default=None)
    p.add_argument("--next-beats", default=None)
    p.add_argument("--no-commit", action="store_true")
    p.add_argument("--no-dashboard", action="store_true")

    p = sub.add_parser("restore")
    p.add_argument("id")
    p.add_argument("--no-commit", action="store_true")
    p.add_argument("--no-dashboard", action="store_true")

    sub.add_parser("checkpoints", help="list the checkpoints on file")

    return ap


def dispatch(args: argparse.Namespace) -> tuple[list[str], bool, dict[str, Any] | None]:
    """Run the subcommand. Returns (lines to print, whether state must be saved, the state)."""
    slug = args.campaign
    cmd = args.cmd
    sub = getattr(args, "sub", None)

    if cmd == "init":
        p = state_path(slug)
        if p.exists() and not args.force:
            raise StateError(f"{p} already exists; pass --force to overwrite (this discards live state)")
        data = blank_state(slug, args.title, args.transparency)
        save(slug, data)
        write_render(slug, data)
        return [f"wrote {p.relative_to(repo_root())} and CHECKPOINT.md"], False, None

    data = load(slug)

    if cmd == "show":
        return [json.dumps(data, indent=2, ensure_ascii=False)], False, data
    if cmd == "get":
        v = dig(data, args.path)
        return [json.dumps(v, indent=2, ensure_ascii=False) if isinstance(v, (dict, list)) else str(v)], False, data
    if cmd == "set":
        poke(data, args.path, coerce(args.value))
        return [f"{args.path} = {json.dumps(dig(data, args.path), ensure_ascii=False)}"], True, data

    if cmd == "add-character":
        key = slugify(args.name)
        if key in data.get("pcs", {}):
            raise StateError(f"{key} already exists")
        pc = blank_character(args.name, args.kind, args.level)
        pc.update(
            {
                "hp": {"current": args.hp, "max": args.hp, "temp": 0},
                "ac": args.ac,
                "saves": {"fortitude": args.fort, "reflex": args.ref, "will": args.will},
                "perception": args.perception,
                "speed": args.speed,
                "str_mod": args.str_mod,
                "hero_points": args.hero_points,
                "sheet": args.sheet or f"characters/{key}.md",
            }
        )
        data.setdefault("pcs", {})[key] = pc
        return [f"added {args.name} ({args.kind}, level {args.level}, {args.hp} HP) as `{key}`"], True, data

    if cmd == "damage":
        return apply_damage(data, args.who, args.amount, from_crit=args.from_crit), True, data
    if cmd == "heal":
        return apply_healing(data, args.who, args.amount), True, data
    if cmd == "hp":
        return set_hp(data, args.who, args.current, args.maximum, args.temp), True, data

    if cmd == "condition":
        if sub == "add":
            return condition_add(data, args.who, args.name, args.value, args.duration, args.source), True, data
        if sub == "remove":
            return condition_remove(data, args.who, args.name), True, data
        if sub == "tick":
            return condition_tick(data, args.who), True, data
        _, pc = find_character(data, args.who)
        out = [f"{pc['name']}:"]
        for c in pc.get("conditions", []):
            out.append(f"  {c['name']}" + (f" {c['value']}" if c.get("value") else "")
                       + f" — {describe_duration(c.get('duration') or {})}"
                       + (f" (from {c['source']})" if c.get("source") else ""))
        for n in ("dying", "wounded", "doomed"):
            if int(pc.get(n, 0)):
                out.append(f"  {n} {pc[n]}")
        if len(out) == 1:
            out.append("  none")
        return out, False, data

    if cmd in ("dying", "wounded", "doomed"):
        if cmd == "dying":
            return set_dying(data, args.who, args.value), True, data
        _, pc = find_character(data, args.who)
        if args.value < 0:
            raise StateError(f"{cmd} cannot be negative")
        pc[cmd] = args.value
        return [f"{pc['name']}: {cmd} {args.value}"], True, data

    if cmd == "recovery":
        key, pc = find_character(data, args.who)
        d = int(pc.get("dying", 0))
        if d < 1:
            raise StateError(f"{pc['name']} is not dying, so there is no recovery check to make")
        r = make_roll(
            "recovery",
            "1d20",
            dc=10 + d,
            label=f"Recovery check (dying {d})",
            actor=pc["name"],
            transparency=data.get("transparency", "standard"),
            tags=["recovery"],
        )
        append_log(
            campaign_dir(slug) / "logs" / "rolls.jsonl",
            r.log_record(slug, data.get("session_number"), int(data.get("checkpoint_counter", 0))),
        )
        delta = {3: -2, 2: -1, 1: 1, 0: 2}[r.degree.index]  # type: ignore[union-attr]
        out = [r.detail_line()]
        out += set_dying(data, key, max(0, d + delta), reason="recovery check")
        return out, True, data

    if cmd == "hero":
        if sub == "spend":
            return hero_spend(data, args.who, args.n), True, data
        if sub == "gain":
            return hero_gain(data, args.who, args.n), True, data
        _, pc = find_character(data, args.who)
        if args.n < 0:
            raise StateError("Hero Points cannot be negative")
        pc["hero_points"] = args.n
        return [f"{pc['name']}: {args.n} Hero Point(s)"], True, data

    if cmd == "focus":
        if sub == "spend":
            return focus_spend(data, args.who, args.n), True, data
        if sub == "refocus":
            return focus_refocus(data, args.who), True, data
        _, pc = find_character(data, args.who)
        f = pc.setdefault("focus", {"current": 0, "max": 0, "refocus_available": True})
        if args.maximum is not None:
            f["max"] = args.maximum
        if args.current > int(f.get("max", 0)):
            raise StateError(f"{args.current} Focus Points is above the pool maximum of {f.get('max', 0)}")
        if args.current < 0:
            raise StateError("Focus Points cannot be negative")
        f["current"] = args.current
        return [f"{pc['name']}: focus {f['current']}/{f['max']}"], True, data

    if cmd == "slots":
        if sub == "use":
            return slots_use(data, args.who, args.rank, args.n), True, data
        if sub == "set":
            _, pc = find_character(data, args.who)
            pc.setdefault("spell_slots", {})[str(args.rank)] = {"max": args.max, "used": 0}
            return [f"{pc['name']}: rank {args.rank} — {args.max} slot(s)"], True, data
        _, pc = find_character(data, args.who)
        for e in pc.get("spell_slots", {}).values():
            e["used"] = 0
        return [f"{pc['name']}: all slots restored"], True, data

    if cmd == "daily-prep":
        return daily_prep(data), True, data

    if cmd == "gold":
        if sub == "add":
            return gold_change(data, args.coins, +1), True, data
        if sub == "spend":
            return gold_change(data, args.coins, -1), True, data
        return gold_set(data, args.coins), True, data

    if cmd == "item":
        if sub == "add":
            return item_add(data, args.name, args.qty, args.owner, args.bulk, args.kind, args.charges, args.level), True, data
        if sub == "remove":
            return item_remove(data, args.name, args.qty, args.owner), True, data
        if sub == "use":
            return item_use(data, args.name, args.owner, args.n), True, data
        out = []
        for key, pc in data.get("pcs", {}).items():
            out.append(f"{pc.get('name', key)}:")
            for it in pc.get("items", []) or [None]:
                out.append("  " + (f"{it['name']} ×{it.get('qty', 1)} [bulk {it.get('bulk', '-')}, {it.get('kind')}]"
                                   + (f", {it['charges']} charges" if it.get("charges") is not None else "")
                                   if it else "(nothing carried)"))
        stash = data.get("party", {}).get("stash", [])
        out.append("party stash:")
        out += ["  " + f"{it['name']} ×{it.get('qty', 1)}" for it in stash] or ["  (empty)"]
        out.append("")
        for row in bulk_report(data):
            out.append(f"{row['name']}: Bulk {row['bulk']:.1f} / encumbered after {row['encumbered_after']} / max {row['max']}")
        return out, False, data

    if cmd == "clock":
        if sub == "add":
            return clock_add(data, args.name, args.segments, args.ticking, args.rate, args.note), True, data
        if sub == "advance":
            return clock_advance(data, args.name, args.n), True, data
        out = []
        for name, c in data.get("clocks", {}).items():
            seg, filled = int(c["segments"]), int(c["filled"])
            out.append(f"{name}: {'▰' * filled}{'▱' * (seg - filled)} {filled}/{seg}"
                       + (f" — ticks {c['rate']}" if c.get("ticking") and c.get("rate") else ""))
        return out or ["no clocks"], False, data

    if cmd == "quest":
        return quest_set(data, args.name, args.status, args.lead), True, data

    if cmd == "advance-time":
        minutes, label = pf2e.parse_interval(" ".join(args.amount))
        before = pf2e.format_time(data.get("time", {}))
        data["time"] = pf2e.advance_time(data.get("time", pf2e.blank_time()), minutes)
        notes = [f"{label} passes: {before} → {pf2e.format_time(data['time'])}"]
        notes += pf2e.tick_wall_clock_conditions(data, minutes)
        return notes, True, data

    if cmd == "location":
        data["location"] = " ".join(args.where)
        return [f"location: {data['location']}"], True, data

    if cmd == "transparency":
        data["transparency"] = args.mode
        return [f"transparency mode: {args.mode}"], True, data

    if cmd == "preset":
        data["difficulty_preset"] = args.name
        return [f"difficulty preset: {args.name} (record the toggles in RULES_DELTAS.md)"], True, data

    if cmd == "xp":
        party = data.setdefault("party", {})
        new = int(party.get("xp", 0)) + args.n if sub == "add" else args.n
        if new < 0:
            raise StateError("XP cannot be negative")
        party["xp"] = new
        notes = [f"party XP: {new}"]
        if new >= 1000:
            notes.append("⚠ 1000 XP reached — level up (system/11-leveling-up.md), then subtract 1000")
        return notes, True, data

    if cmd == "level":
        if args.who:
            _, pc = find_character(data, args.who)
            pc["level"] = args.n
            return [f"{pc['name']} is level {args.n}"], True, data
        data.setdefault("party", {})["level"] = args.n
        for pc in data.get("pcs", {}).values():
            pc["level"] = args.n
        return [f"party level {args.n} — re-derive every derived number (system/11-leveling-up.md)"], True, data

    if cmd == "session":
        if sub == "start":
            if data.get("session_in_progress"):
                raise StateError("a session is already in progress; end it first")
            data["session_in_progress"] = True
            data["session_number"] = args.number if args.number is not None else int(data.get("session_number", 0)) + 1
            data["scene_count"] = 0
            return [f"session {data['session_number']} started; off-screen turns will refuse to run"], True, data
        if sub == "end":
            data["session_in_progress"] = False
            return [f"session {data.get('session_number')} closed — write sessions/, canon, quests, "
                    "clocks, flags, the fairness line, then checkpoint"], True, data
        data["scene_count"] = int(data.get("scene_count", 0)) + args.n
        return [f"scene {data['scene_count']} of this session"], True, data

    if cmd == "note":
        data.setdefault("notes", {})[args.field] = " ".join(args.text)
        return [f"note.{args.field} set"], True, data

    if cmd == "encounter":
        if sub == "start":
            return encounter_start(data, args.name, args.objective, args.map_slug), True, data
        if sub == "add":
            return encounter_add(
                data, args.name, args.side, ref=args.ref, initiative=args.initiative, hp=args.hp,
                position=args.position, squad=args.squad, level=args.level, id=args.id, notes=args.notes,
            ), True, data
        if sub == "next":
            return encounter_next(data), True, data
        if sub == "status":
            return encounter_status(data), False, data
        if sub == "end":
            return encounter_end(data), True, data
        if sub == "action":
            return encounter_action(data, args.who, args.n), True, data
        if sub == "map-step":
            return encounter_map_step(data, args.who, args.step), True, data
        if sub == "reaction":
            return encounter_reaction(data, args.who, args.what, args.restore), True, data
        if sub == "position":
            return encounter_position(data, args.who, args.cell), True, data
        if sub == "hp":
            return encounter_hp(data, args.who, args.current, args.maximum), True, data
        if sub == "telegraph":
            _enc(data)["telegraphed"] = True
            _enc(data)["telegraph_text"] = " ".join(args.text)
            return ["objective telegraphed to the player"], True, data

    if cmd == "render":
        p = write_render(slug, data)
        return [f"rewrote {p.relative_to(repo_root())} from state.json"], False, None

    if cmd == "bulk":
        out = []
        for row in bulk_report(data):
            flag = " OVER THE LIMIT" if row["over_max"] else (" encumbered" if row["encumbered"] else "")
            out.append(f"{row['name']}: {row['bulk']:.1f} Bulk / encumbered after {row['encumbered_after']}"
                       f" / max {row['max']}{flag}")
        return out or ["no characters"], False, data

    if cmd == "checkpoint":
        _, notes = checkpoint(
            slug, data, args.message,
            commit=not args.no_commit, dashboard=not args.no_dashboard,
            situation=args.situation, next_beats=args.next_beats,
        )
        return [f"checkpoint {data['last_checkpoint']['id']}: {args.message}"] + notes, False, None

    if cmd == "restore":
        return restore(slug, args.id, commit=not args.no_commit, dashboard=not args.no_dashboard), False, None

    if cmd == "checkpoints":
        cdir = campaign_dir(slug) / "checkpoints"
        files = sorted(cdir.glob("*.md")) if cdir.is_dir() else []
        return [f"{p.stem}" for p in files] or ["no checkpoints yet"], False, None

    raise StateError(f"unhandled command {cmd} {sub or ''}".strip())


def main(argv: Sequence[str] | None = None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)
    try:
        lines, dirty, data = dispatch(args)
        if dirty and data is not None:
            save(args.campaign, data)
    except (StateError, DiceError, ValueError) as exc:
        print(f"state.py: refused: {exc}", file=sys.stderr)
        return 2
    except KeyError as exc:
        print(f"state.py: state.json is missing {exc}", file=sys.stderr)
        return 2
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
