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

import rules  # noqa: E402


class StateError(Exception):
    """A refused mutation. The message says what was asked and why it cannot happen."""


# Schema 3 adds a `system` key naming the campaign's ruleset. A schema 2 state has no
# such key and reads as Pathfinder, which is what every state written before the second
# ruleset existed is; `migrate` stamps the field in on first write.
SCHEMA_VERSION = 3
LEGACY_SCHEMA_SYSTEM = "pf2e"


def system_of(data: dict[str, Any]) -> str:
    """The ruleset a loaded state belongs to."""
    return rules.canonical(data.get("system") or LEGACY_SCHEMA_SYSTEM)


def rs(data: dict[str, Any]):
    """The rules module for a loaded state. Every per-game difference goes through this."""
    return rules.load(system_of(data))


def _hint(data: dict[str, Any], what: str) -> str:
    """The other ruleset's name for a resource this one does not have, if it has one.

    Tries the whole phrase, then its first word, so both `attunement` and `short rest`
    find their entry. A refusal with no hint is a refusal the GM has to go and look up.
    """
    hints = getattr(rs(data), "RESOURCE_HINTS", {})
    key = str(what).strip().lower()
    return hints.get(key) or hints.get(key.replace(" ", "-")) or hints.get(key.split()[0], "")


def _wrong_game(data: dict[str, Any], what: str, needs: str) -> StateError:
    sid = system_of(data)
    msg = f"{what} is a {rules.short_of(needs)} concept and this is a {rules.short_of(sid)} campaign."
    hint = _hint(data, what.split()[0].lower())
    return StateError(msg + (f" {hint}" if hint else ""))


# The names below stay at module scope because callers import them, and they hold
# Pathfinder's sets so that behaviour is unchanged for anything that reads them directly.
# Everything inside this file asks the campaign's ruleset instead — see `rs()`.
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
    return migrate(slug, data)


def migrate(slug: str, data: dict[str, Any]) -> dict[str, Any]:
    """Bring an older state forward in memory. The file updates on the next save.

    Schema 2 -> 3 is one field: a campaign written before the second ruleset existed
    declares no `system`, and is Pathfinder. Where `CAMPAIGN.md` says otherwise that is
    used instead, so a campaign whose Markdown was updated first is not mislabelled.
    Nothing else about an older state changes, and no numbers are touched.
    """
    version = int(data.get("schema_version", 2))
    if not data.get("system"):
        declared = rules.declared_in_campaign_md(slug) if slug else None
        data["system"] = declared or LEGACY_SCHEMA_SYSTEM
    data["system"] = rules.canonical(data["system"])
    if version < 3:
        data["schema_version"] = SCHEMA_VERSION
        data.setdefault("migrated_from_schema", version)
    return data


def save(slug: str, data: dict[str, Any]) -> None:
    data["updated_at"] = utc_now()
    atomic_write(state_path(slug), json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False) + "\n")


def blank_state(slug: str, title: str = "", transparency: str = "standard",
                system: str | None = None) -> dict[str, Any]:
    sid = rules.canonical(system)
    mod = rules.load(sid)
    return {
        "schema_version": SCHEMA_VERSION,
        "system": sid,
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
        "time": (pf2e.blank_time() if sid == "pf2e"
                 else rules.blank_time(calendar=mod.DEFAULT_CALENDAR)),
        "location": "unset",
        "party": {
            "level": 1,
            "xp": 0,
            "gold": {c: 0 for c in mod.COIN_ORDER},
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


def blank_character(name: str, kind: str = "pc", level: int = 1,
                    system: str | None = None) -> dict[str, Any]:
    """A fresh sheet. The shared half is here; the ruleset supplies its own half.

    Pathfinder contributes Hero Points, Focus, saves by name and the dying track. D&D
    contributes death saves, Hit Dice, Exhaustion, Heroic Inspiration, Concentration and
    attunement. Neither game's fields appear on the other game's sheet, so nothing on a
    character implies a rule that does not exist in their campaign.
    """
    mod = rules.load(system)
    return {
        "name": name,
        "kind": kind,  # pc | ally | sidekick | companion | familiar | eidolon
        "level": level,
        "hp": {"current": 0, "max": 0, "temp": 0},
        "conditions": [],
        "items": [],
        "sheet": None,
        "notes": "",
        **mod.blank_character_fields(level),
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
    overflow = max(0, left - hp["current"])
    hp["current"] = max(0, hp["current"] - left)
    notes.append(f"{pc['name']} HP {hp['current']}/{hp['max']}")

    if not was_down and hp["current"] > 0:
        return notes

    # What 0 HP means is the single biggest difference between the three games, so the
    # ruleset decides and this function only carries the instruction out.
    #   PF2e   dying 1 (or 2 from a crit), plus the wounded value; dying 4 is death.
    #   D&D 24 unconscious and making Death Saves; massive damage kills outright.
    #   D&D 4e dying with hit points that keep falling below zero; death at negative
    #          bloodied, or at the third death saving throw failure.
    instruction = rs(data).on_zero_hp(
        pc, from_crit=from_crit, overflow=overflow, already_down=was_down)
    notes += instruction.get("notes", [])
    action = instruction.get("action")
    # A ruleset may need a field of its own written back — 4e's below-zero total is the
    # only one so far, and it has to survive between one hit and the next.
    for field, value in (instruction.get("set") or {}).items():
        pc[field] = value

    if action == "dying":
        notes += set_dying(data, key, int(instruction["value"]),
                           reason=instruction.get("reason", ""))
    elif action == "down":
        pc.setdefault("death_saves", dict(blank_death_saves(data)))
        if "stable" in pc["death_saves"]:
            pc["death_saves"]["stable"] = False
    elif action == "death-save-failures":
        notes += record_death_save_failures(data, key, int(instruction["value"]),
                                            reason=instruction.get("reason", ""))
    elif action == "dead":
        notes += mark_dead(data, key, reason=instruction.get("reason", ""))
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
    if hp["current"] >= 1:
        instruction = rs(data).on_healed_from_zero(pc)
        for field, value in (instruction.get("set") or {}).items():
            pc[field] = value
        if instruction.get("action") == "dying":
            notes += set_dying(data, key, int(instruction["value"]),
                               reason=instruction.get("reason", ""))
        elif instruction.get("action") == "reset-death-saves":
            pc["death_saves"] = dict(blank_death_saves(data))
            notes.append(f"{pc['name']}: {death_save_word(data)} counters reset "
                         f"({instruction.get('reason', 'regained hit points')})")
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


def blank_death_saves(data: dict[str, Any]) -> dict[str, Any]:
    """The death-save record this ruleset keeps, or `{}` for one that keeps none.

    PF2e counts dying instead, D&D 2024 counts three successes and three failures with a
    Stable flag, and 4e counts failures only. Reading the shape off the ruleset keeps
    `state.json` from carrying fields the game at the table does not have.
    """
    return dict(getattr(rs(data), "BLANK_DEATH_SAVES", {}) or {})


def death_save_word(data: dict[str, Any]) -> str:
    return "Death Saving Throw" if system_of(data) == "dnd5e" else "death saving throw"


def record_death_save_failures(data: dict[str, Any], who: str, n: int,
                               *, reason: str = "") -> list[str]:
    """Add death-save failures, through whichever ruleset's clock this campaign runs."""
    sid = system_of(data)
    if sid == "dnd4e":
        return death_save_record_4e(data, who, failures=n, reason=reason)
    return death_save_record(data, who, failures=n, reason=reason)


def set_dying(data: dict[str, Any], who: str, value: int, *, reason: str = "") -> list[str]:
    if system_of(data) != "pf2e":
        raise _wrong_game(data, "dying", "pf2e")
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


def death_save_record(data: dict[str, Any], who: str, *, successes: int = 0,
                      failures: int = 0, reason: str = "") -> list[str]:
    """Record Death Saving Throw results, and resolve the third of either.

    Source: see `python3 tools/dnd5e.py sources` (death_saves). Three successes make the
    character Stable; three failures kill them; a natural 20 on the save itself heals them
    to 1 HP, which `roll.py death-save` reports and `heal` then applies.
    """
    if system_of(data) != "dnd5e":
        raise _wrong_game(data, "death saves", "dnd5e")
    key, pc = find_character(data, who)
    import dnd5e

    if successes < 0 or failures < 0:
        raise StateError("death save counts do not go down; `heal` resets them instead")
    ds = pc.setdefault("death_saves", {"successes": 0, "failures": 0, "stable": False})
    if int((pc.get("hp") or {}).get("current", 1)) > 0:
        raise StateError(
            f"{pc['name']} is on {pc['hp']['current']} HP and does not make Death Saves — "
            f"they are only made while at 0 HP"
        )
    if ds.get("stable") and failures:
        ds["stable"] = False
        note_stable = [f"{pc['name']} stops being Stable and resumes Death Saves"]
    else:
        note_stable = []
    ds["successes"] = int(ds.get("successes", 0)) + int(successes)
    ds["failures"] = int(ds.get("failures", 0)) + int(failures)
    notes = note_stable + [
        f"{pc['name']}: Death Saves {ds['successes']}/3 successes, {ds['failures']}/3 failures"
        + (f" ({reason})" if reason else "")
    ]
    if ds["failures"] >= dnd5e.DEATH_SAVES_TO_RESOLVE:
        notes += mark_dead(data, key, reason="third Death Saving Throw failure")
    elif ds["successes"] >= dnd5e.DEATH_SAVES_TO_RESOLVE:
        ds["stable"] = True
        notes.append(
            f"⚠ {pc['name']} is STABLE — no more Death Saves, still Unconscious at 0 HP, "
            f"and regains 1 HP after 1d4 hours if nobody heals them"
        )
    return notes


def death_save_stabilise(data: dict[str, Any], who: str) -> list[str]:
    """A successful DC 10 Wisdom (Medicine) check stabilises a creature at 0 HP."""
    if system_of(data) != "dnd5e":
        raise _wrong_game(data, "death saves", "dnd5e")
    _, pc = find_character(data, who)
    if int((pc.get("hp") or {}).get("current", 1)) > 0:
        raise StateError(f"{pc['name']} is not at 0 HP and does not need stabilising")
    ds = pc.setdefault("death_saves", {"successes": 0, "failures": 0, "stable": False})
    if ds.get("dead"):
        raise StateError(f"{pc['name']} is dead; stabilising is past the point")
    ds["stable"] = True
    return [f"{pc['name']} is Stable — Death Saves stop, still Unconscious at 0 HP, "
            f"and regains 1 HP after 1d4 hours if unhealed"]


def mark_dead(data: dict[str, Any], who: str, *, reason: str = "") -> list[str]:
    """Record a death. The tool does not decide one — it writes down one that happened."""
    _, pc = find_character(data, who)
    pc["dead"] = True
    pc["dead_reason"] = reason
    ds = pc.get("death_saves")
    if isinstance(ds, dict):
        ds["stable"] = False
    return [f"☠ {pc['name']} is DEAD" + (f" — {reason}" if reason else "")]


def exhaustion_set(data: dict[str, Any], who: str, value: int) -> list[str]:
    """Set an Exhaustion level. Six is death; this records it rather than clamping."""
    if system_of(data) != "dnd5e":
        raise _wrong_game(data, "exhaustion", "dnd5e")
    key, pc = find_character(data, who)
    import dnd5e

    if value < 0:
        raise StateError("Exhaustion does not go below 0; the condition just ends")
    if value > dnd5e.EXHAUSTION_MAX:
        raise StateError(
            f"Exhaustion {value} is past {dnd5e.EXHAUSTION_MAX}, which is death — "
            f"set it to {dnd5e.EXHAUSTION_MAX} and the death is recorded"
        )
    pc["exhaustion"] = int(value)
    e = dnd5e.exhaustion_effect(value)
    notes = [f"{pc['name']}: Exhaustion {value}"
             + (f" — {e['d20_penalty']} to every D20 Test, {e['speed_penalty_feet']} ft Speed"
                if value else " — the condition ends")]
    if e["dead"]:
        notes += mark_dead(data, key, reason=f"Exhaustion level {dnd5e.EXHAUSTION_MAX}")
    return notes


def inspiration_set(data: dict[str, Any], who: str, held: bool) -> list[str]:
    """Heroic Inspiration is binary: you have it or you do not.

    Source: see `python3 tools/dnd5e.py sources`. "You can never have more than one
    instance of Heroic Inspiration. If something gives you Heroic Inspiration and you
    already have it, you can give it to a player character in your group who lacks it."
    """
    if system_of(data) != "dnd5e":
        raise _wrong_game(data, "inspiration", "dnd5e")
    _, pc = find_character(data, who)
    had = bool(pc.get("heroic_inspiration"))
    if held and had:
        raise StateError(
            f"{pc['name']} already holds Heroic Inspiration, and it does not stack — "
            f"give it to a character who lacks it instead"
        )
    if not held and not had:
        raise StateError(f"{pc['name']} does not hold Heroic Inspiration to spend")
    pc["heroic_inspiration"] = bool(held)
    return [f"{pc['name']} {'gains' if held else 'spends'} Heroic Inspiration"]


def hit_dice_spend(data: dict[str, Any], who: str, n: int = 1) -> list[str]:
    """Spend Hit Dice on a Short Rest. The HP they restore is a real roll, so `heal` applies it."""
    if system_of(data) != "dnd5e":
        raise _wrong_game(data, "hit-dice", "dnd5e")
    _, pc = find_character(data, who)
    hd = pc.setdefault("hit_dice", {"die": 8, "max": int(pc.get("level", 1)), "used": 0})
    left = int(hd.get("max", 0)) - int(hd.get("used", 0))
    if n > left:
        raise StateError(f"{pc['name']} has {left} Hit Dice left and cannot spend {n}")
    hd["used"] = int(hd.get("used", 0)) + int(n)
    return [
        f"{pc['name']} spends {n}d{hd.get('die', 8)} Hit Dice "
        f"→ {int(hd['max']) - int(hd['used'])}/{hd['max']} left",
        f"Roll it: `roll.py expr \"{n}d{hd.get('die', 8)}+<Con mod x {n}>\" --campaign "
        f"{data.get('campaign', '<slug>')}` then apply the total with `heal`.",
    ]


def concentration_set(data: dict[str, Any], who: str, on: str | None) -> list[str]:
    """Start or drop Concentration. Starting a second effect ends the first."""
    if system_of(data) != "dnd5e":
        raise _wrong_game(data, "concentration", "dnd5e")
    _, pc = find_character(data, who)
    before = pc.get("concentration")
    before_name = (before or {}).get("on") if isinstance(before, dict) else before
    if on is None:
        if not before:
            raise StateError(f"{pc['name']} is not concentrating on anything")
        pc["concentration"] = None
        return [f"{pc['name']} stops concentrating on {before_name}"]
    pc["concentration"] = {"on": on}
    if before_name:
        return [f"{pc['name']} concentrates on {on} — which ends Concentration on {before_name}"]
    return [f"{pc['name']} concentrates on {on}"]


def attune(data: dict[str, Any], who: str, item: str, *, remove: bool = False) -> list[str]:
    """Attune to or release a magic item, against the character's own limit."""
    if system_of(data) != "dnd5e":
        raise _wrong_game(data, "attunement", "dnd5e")
    _, pc = find_character(data, who)
    import dnd5e

    att = pc.setdefault("attunement", {"max": dnd5e.ATTUNEMENT_LIMIT, "items": []})
    items = att.setdefault("items", [])
    cap = int(att.get("max", dnd5e.ATTUNEMENT_LIMIT))
    lowered = {i.lower() for i in items}
    if remove:
        if item.lower() not in lowered:
            raise StateError(f"{pc['name']} is not attuned to {item!r} (attuned: "
                             f"{', '.join(items) or 'nothing'})")
        att["items"] = [i for i in items if i.lower() != item.lower()]
        return [f"{pc['name']} ends Attunement with {item} → {len(att['items'])}/{cap}"]
    if item.lower() in lowered:
        raise StateError(f"{pc['name']} is already attuned to {item!r}")
    if len(items) >= cap:
        raise StateError(
            f"{pc['name']} is attuned to {len(items)} items, which is the limit of {cap} "
            f"({', '.join(items)}) — end one first"
        )
    items.append(item)
    return [f"{pc['name']} attunes to {item} → {len(items)}/{cap}"]


# --------------------------------------------------------------------------------------
# D&D 4e: healing surges, Second Wind, action points, powers, and a death clock of its own
# --------------------------------------------------------------------------------------


def _need_4e(data: dict[str, Any], what: str) -> None:
    if system_of(data) != "dnd4e":
        raise _wrong_game(data, what, "dnd4e")


def death_save_record_4e(data: dict[str, Any], who: str, *, failures: int = 0,
                         natural: int | None = None, reason: str = "") -> list[str]:
    """Record a 4e death saving throw: failures only, three of them being death.

    4e's clock counts in one direction. A roll of 10 or more is not a success that
    accumulates — it is simply not a failure — so there is no success counter to keep. A
    natural 20 lets the character spend a healing surge and act, which this reports and
    `surge spend` then applies.
    """
    _need_4e(data, "death saves")
    import dnd4e

    key, pc = find_character(data, who)
    if failures < 0:
        raise StateError("death saving throw failures do not go down; `heal` clears them")
    if int((pc.get("hp") or {}).get("current", 1)) > 0 and not int(pc.get("hp_below_zero", 0)):
        raise StateError(
            f"{pc['name']} is on {pc['hp']['current']} hit points and is not dying — "
            f"a 4e death saving throw is made only while dying"
        )
    ds = pc.setdefault("death_saves", {"failures": 0})
    ds.pop("successes", None)   # in case a sheet was migrated from the 2024 shape
    ds.pop("stable", None)
    ds["failures"] = int(ds.get("failures", 0)) + int(failures)
    notes = [f"{pc['name']}: death saving throw failures {ds['failures']}/"
             f"{dnd4e.DEATH_SAVE_FAILURES}" + (f" ({reason})" if reason else "")]
    if natural == dnd4e.DEATH_SAVE_SURGE_ON:
        notes.append(
            f"⚠ natural 20 — {pc['name']} may spend a healing surge and act; "
            f"apply it with `surge spend {key}`"
        )
    if ds["failures"] >= dnd4e.DEATH_SAVE_FAILURES:
        notes += mark_dead(data, key, reason=f"{dnd4e.DEATH_SAVE_FAILURES} death saving "
                                             f"throw failures in one encounter")
    return notes


def death_save_roll_4e(data: dict[str, Any], who: str, slug: str) -> list[str]:
    """Roll a real 4e death saving throw through roll.py and write down what it said."""
    _need_4e(data, "death saves")
    key, pc = find_character(data, who)
    ds = pc.get("death_saves") or {}
    res = subprocess.run(
        [sys.executable, str(Path(__file__).resolve().parent / "roll.py"), "death-save",
         "--campaign", slug, "--system", "dnd4e",
         "--actor", pc.get("name", key),
         "--failures", str(int(ds.get("failures", 0))),
         "--json", "--quiet"],
        capture_output=True, text=True,
    )
    if res.returncode != 0:
        raise StateError(f"the death saving throw could not be rolled: {res.stderr.strip()}")
    rolled = json.loads(res.stdout)[0]
    out = [rolled["line"]]
    natural = rolled.get("natural")
    incurred = int((rolled.get("extra") or {}).get("failures_incurred", 0))
    out += death_save_record_4e(data, key, failures=incurred, natural=natural,
                                reason="rolled death saving throw")
    return out


def hp_below_set(data: dict[str, Any], who: str, value: int) -> list[str]:
    """Set how far below zero a dying 4e character's hit points have fallen.

    `damage` keeps this itself; the command exists for the case where the GM is correcting
    the number rather than applying a hit.
    """
    _need_4e(data, "below-zero hit points")
    import dnd4e

    key, pc = find_character(data, who)
    if value < 0:
        raise StateError("pass the depth as a positive number: `hp-below <who> 7` means −7 "
                         "hit points")
    hp_max = int((pc.get("hp") or {}).get("max", 0))
    pc["hp_below_zero"] = int(value)
    threshold = dnd4e.death_threshold(hp_max)
    notes = [f"{pc['name']}: {-int(value)} hit points (death threshold {threshold})"]
    if hp_max and value and -value <= threshold:
        notes += mark_dead(data, key, reason=f"{-value} hit points, at or past the death "
                                             f"threshold of {threshold}")
    return notes


def surge_spend(data: dict[str, Any], who: str, n: int = 1) -> list[str]:
    """Spend healing surges. The hit points they restore are applied with `heal`."""
    _need_4e(data, "healing surges")
    import dnd4e

    _, pc = find_character(data, who)
    surges = pc.setdefault("healing_surges", {"max": 0, "used": 0})
    left = int(surges.get("max", 0)) - int(surges.get("used", 0))
    if n > left:
        raise StateError(f"{pc['name']} has {left} healing surge(s) left and cannot spend {n}")
    surges["used"] = int(surges.get("used", 0)) + int(n)
    hp_max = int((pc.get("hp") or {}).get("max", 0))
    value = dnd4e.surge_value(hp_max)
    notes = [
        f"{pc['name']} spends {n} healing surge(s) → "
        f"{int(surges['max']) - int(surges['used'])}/{surges['max']} left"
    ]
    if hp_max:
        notes.append(
            f"A surge is worth a quarter of maximum hit points: {value} each, {value * n} in "
            f"all. Apply it with `heal {who} {value * n}`."
        )
    else:
        notes.append("No maximum hit points recorded, so the surge value is unknown — set "
                     "maximum HP first.")
    return notes


def surge_set(data: dict[str, Any], who: str, maximum: int | None, used: int | None) -> list[str]:
    _need_4e(data, "healing surges")
    _, pc = find_character(data, who)
    surges = pc.setdefault("healing_surges", {"max": 0, "used": 0})
    if maximum is not None:
        if maximum < 0:
            raise StateError("a healing surge pool cannot be negative")
        surges["max"] = int(maximum)
    if used is not None:
        if used < 0:
            raise StateError("surges used cannot be negative")
        if used > int(surges.get("max", 0)):
            raise StateError(f"{used} used is more than the pool of {surges.get('max', 0)}")
        surges["used"] = int(used)
    return [f"{pc['name']}: healing surges {int(surges['max']) - int(surges['used'])}/"
            f"{surges['max']} left"]


def second_wind(data: dict[str, Any], who: str, *, reset: bool = False) -> list[str]:
    """Use Second Wind, which spends a surge and grants a defence bonus for the round."""
    _need_4e(data, "Second Wind")
    import dnd4e

    key, pc = find_character(data, who)
    if reset:
        pc["second_wind_used"] = False
        return [f"{pc['name']}: Second Wind available again"]
    if pc.get("second_wind_used"):
        raise StateError(f"{pc['name']} has already used Second Wind this encounter — "
                         f"a short rest restores it")
    surges = pc.setdefault("healing_surges", {"max": 0, "used": 0})
    if int(surges.get("max", 0)) - int(surges.get("used", 0)) < 1:
        raise StateError(f"{pc['name']} has no healing surge left to spend on Second Wind")
    pc["second_wind_used"] = True
    notes = surge_spend(data, key, 1)
    notes.insert(0, f"{pc['name']} uses Second Wind")
    notes.append("Second Wind also grants a bonus to all defences until the start of their "
                 "next turn — record it as a condition if it matters.")
    return notes


def action_point_spend(data: dict[str, Any], who: str, n: int = 1) -> list[str]:
    """Spend an action point for an extra action. One per encounter, by the rules."""
    _need_4e(data, "action points")
    _, pc = find_character(data, who)
    have = int(pc.get("action_points", 0))
    if have < n:
        raise StateError(f"{pc['name']} has {have} action point(s) and cannot spend {n}")
    pc["action_points"] = have - n
    return [f"{pc['name']} spends {n} action point → {pc['action_points']} left",
            "Only one action point may be spent per encounter, and spending one gives an "
            "extra action this turn."]


def action_point_set(data: dict[str, Any], who: str, value: int) -> list[str]:
    _need_4e(data, "action points")
    _, pc = find_character(data, who)
    if value < 0:
        raise StateError("action points cannot be negative")
    pc["action_points"] = int(value)
    return [f"{pc['name']}: {value} action point(s)"]


def milestone_reach(data: dict[str, Any], who: str | None = None) -> list[str]:
    """Record a milestone, which grants an action point.

    A milestone is every second encounter completed without an extended rest, so it is a
    party-wide event unless a single character is named.
    """
    _need_4e(data, "milestones")
    pcs = data.get("pcs") or {}
    if who:
        key, pc = find_character(data, who)
        targets = {key: pc}
    else:
        targets = pcs
    if not targets:
        raise StateError("no characters to credit a milestone to")
    notes = []
    for _, pc in targets.items():
        pc["milestones"] = int(pc.get("milestones", 0)) + 1
        pc["action_points"] = int(pc.get("action_points", 0)) + 1
        notes.append(f"{pc['name']}: milestone {pc['milestones']} → "
                     f"{pc['action_points']} action point(s)")
    return notes


def power_use(data: dict[str, Any], who: str, name: str, *, release: bool = False) -> list[str]:
    """Mark an encounter or daily power used, or hand it back.

    At-will powers are not tracked — they have no expenditure to record.
    """
    _need_4e(data, "powers")
    _, pc = find_character(data, who)
    powers = pc.setdefault("powers", {"encounter": [], "daily": []})
    for bucket in ("encounter", "daily"):
        for entry in powers.get(bucket) or []:
            if str(entry.get("name", "")).lower() == name.lower():
                if release:
                    entry["used"] = False
                    return [f"{pc['name']}: {entry['name']} ({bucket}) is available again"]
                if entry.get("used"):
                    raise StateError(
                        f"{pc['name']} has already used {entry['name']} ({bucket}) — "
                        + ("a short rest restores it" if bucket == "encounter"
                           else "an extended rest restores it")
                    )
                entry["used"] = True
                return [f"{pc['name']} uses {entry['name']} ({bucket} power)"]
    known = ", ".join(
        f"{e.get('name')} [{b}]" for b in ("encounter", "daily") for e in (powers.get(b) or [])
    ) or "none recorded"
    raise StateError(
        f"{pc['name']} has no encounter or daily power called {name!r} recorded "
        f"(has: {known}) — add it with `power add`. At-will powers are not tracked."
    )


def power_add(data: dict[str, Any], who: str, name: str, bucket: str) -> list[str]:
    _need_4e(data, "powers")
    _, pc = find_character(data, who)
    kind = str(bucket).strip().lower()
    if kind not in ("encounter", "daily"):
        raise StateError("a tracked power is either 'encounter' or 'daily'; at-will powers "
                         "have nothing to track")
    powers = pc.setdefault("powers", {"encounter": [], "daily": []})
    entries = powers.setdefault(kind, [])
    if any(str(e.get("name", "")).lower() == name.lower() for e in entries):
        raise StateError(f"{pc['name']} already has {name!r} recorded as a {kind} power")
    entries.append({"name": name, "used": False})
    return [f"{pc['name']}: {name} recorded as a {kind} power"]


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
    mod = rs(data)
    tracked, known, valued = mod.TRACKED_SEPARATELY, mod.KNOWN_CONDITIONS, mod.VALUED_CONDITIONS
    slug = slugify(name)
    if slug in tracked:
        raise StateError(
            f"{slug} is tracked as its own field, not as a condition entry — "
            f"use `{slug} set <who> <value>` so there is only one copy of the number"
        )
    if slug not in known:
        other = [sid for sid in rules.SYSTEMS if sid != system_of(data)
                 and slug in rules.load(sid).KNOWN_CONDITIONS]
        extra = (f" It is a {rules.short_of(other[0])} condition, and this is a "
                 f"{rules.short_of(system_of(data))} campaign." if other else "")
        raise StateError(
            f"{name!r} is not a {mod.SYSTEM_SHORT} condition.{extra} Known: "
            + ", ".join(sorted(known))
        )
    if slug in valued:
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
            if slug in valued:
                # The stronger value wins; a condition does not stack with itself in
                # the rulesets that have one (PF2e condition entries; SRD 5.2 "Condition").
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
    if system_of(data) != "pf2e":
        raise _wrong_game(data, "hero", "pf2e")
    _, pc = find_character(data, who)
    have = int(pc.get("hero_points", 0))
    if have < n:
        raise StateError(f"{pc['name']} has {have} Hero Point(s) and cannot spend {n}")
    pc["hero_points"] = have - n
    return [f"{pc['name']} spends {n} Hero Point → {pc['hero_points']} left"]


def hero_gain(data: dict[str, Any], who: str, n: int = 1) -> list[str]:
    if system_of(data) != "pf2e":
        raise _wrong_game(data, "hero", "pf2e")
    _, pc = find_character(data, who)
    cap = int(pc.get("hero_points_max", 3))
    new = int(pc.get("hero_points", 0)) + n
    if new > cap:
        raise StateError(f"{pc['name']} would hold {new} Hero Points, above the cap of {cap}")
    pc["hero_points"] = new
    return [f"{pc['name']} gains {n} Hero Point → {new}"]


def focus_spend(data: dict[str, Any], who: str, n: int = 1) -> list[str]:
    if system_of(data) != "pf2e":
        raise _wrong_game(data, "focus", "pf2e")
    _, pc = find_character(data, who)
    f = pc.setdefault("focus", {"current": 0, "max": 0, "refocus_available": True})
    if int(f.get("current", 0)) < n:
        raise StateError(f"{pc['name']} has {f.get('current', 0)} Focus Point(s) and cannot spend {n}")
    f["current"] = int(f["current"]) - n
    return [f"{pc['name']} spends {n} Focus Point → {f['current']}/{f.get('max', 0)}"]


def focus_refocus(data: dict[str, Any], who: str, n: int = 1) -> list[str]:
    """Refocus recovers 1 Focus Point (more only with a specific ability that says so)."""
    if system_of(data) != "pf2e":
        raise _wrong_game(data, "refocus", "pf2e")
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


def xp_threshold_note(data: dict[str, Any], total: int) -> list[str]:
    """Whether this XP total has reached a level, in whichever way this ruleset counts.

    The three disagree completely. Pathfinder is a flat amount per level with a counter that
    **resets**; both D&D editions keep a **cumulative** total that never resets and read it
    against a threshold table. Hardcoding either one would mis-advise two of the three
    campaigns, so this asks the ruleset.
    """
    mod = rs(data)
    level = int((data.get("party") or {}).get("level", 1) or 1)
    doc = ("system/dnd5e/11-leveling-up.md" if mod.SYSTEM_ID == "dnd5e"
           else "system/dnd4e/11-leveling-up.md" if mod.SYSTEM_ID == "dnd4e"
           else "system/11-leveling-up.md")
    try:
        cumulative = bool(mod.xp_is_cumulative())
    except Exception:
        return []
    try:
        need = mod.xp_to_level(level + 1)
    except Exception as exc:
        # 4e's advancement table is owner-supplied, so "I cannot tell you" is a real answer
        # and is more use than a threshold borrowed from another ruleset.
        return [f"(cannot say whether that is a level-up: {exc})"]
    if need is None:
        return [f"level {level} is the top of this ruleset's scale; no further threshold"]
    if cumulative:
        if int(total) < int(need):
            return [f"next level at {need:,} cumulative ({int(need) - int(total):,} to go)"]
        # A big award can cross more than one threshold, so say which level the total
        # actually reaches rather than only the next one up, and quote THAT level's threshold.
        reached, at = level + 1, int(need)
        try:
            best = int(mod.level_for_xp(int(total)))
            if best > reached:
                reached, at = best, int(mod.xp_to_level(best) or need)
        except Exception:
            pass
        more = (f" — {reached - level} levels at once, so re-derive every number at each step"
                if reached > level + 1 else "")
        return [f"⚠ {int(total):,} cumulative XP reaches level {reached} (its threshold is "
                f"{at:,}){more} ({doc}). The total is cumulative and is NOT reset."]
    if int(total) >= int(need):
        return [f"⚠ {need:,} XP reached — level up ({doc}), then subtract {need:,}"]
    return [f"next level at {need:,} ({int(need) - int(total):,} to go); "
            f"the counter resets on levelling"]


#: Pathfinder calls a spell's tier its rank; D&D 2024 calls it its level. Same slot, same
#: storage, different word at the table — so the word follows the campaign. 4e has no slots
#: at all, which `require_slots` refuses rather than letting the word stand in for the rule.
SLOT_WORD = {"pf2e": "rank", "dnd5e": "level"}

#: Rulesets with no spell-slot machinery. 4e's powers are at-will, encounter or daily, and
#: a slot table would be a different game's structure wearing 4e's names.
NO_SPELL_SLOTS = ("dnd4e",)


def slot_word(data: dict[str, Any]) -> str:
    return SLOT_WORD.get(system_of(data), "rank")


def require_slots(data: dict[str, Any]) -> None:
    sid = system_of(data)
    if sid in NO_SPELL_SLOTS:
        hint = _hint(data, "slots")
        raise StateError(
            f"{rules.short_of(sid)} has no spell slots." + (f" {hint}" if hint else "")
        )


def slots_use(data: dict[str, Any], who: str, rank: str, n: int = 1) -> list[str]:
    require_slots(data)
    _, pc = find_character(data, who)
    word = slot_word(data)
    slots = pc.setdefault("spell_slots", {})
    key = str(rank)
    if key not in slots:
        have = ", ".join(sorted(slots, key=lambda r: int(r))) or "none"
        raise StateError(f"{pc['name']} has no {word}-{key} slots recorded (has: {have})")
    entry = slots[key]
    used = int(entry.get("used", 0)) + n
    if used > int(entry.get("max", 0)):
        raise StateError(
            f"{pc['name']} has {entry.get('max', 0)} {word}-{key} slot(s) and "
            f"{entry.get('used', 0)} already used"
        )
    entry["used"] = used
    return [f"{pc['name']} {word} {key}: {used}/{entry['max']} used"]


# --------------------------------------------------------------------------------------
# Money and items
# --------------------------------------------------------------------------------------

# Both rulesets' denominations, so a purse parses whichever game wrote it. Which coins a
# campaign may actually hold is enforced against its own ruleset below.
_COIN_RE = re.compile(r"^(\d+)\s*(pp|gp|ep|sp|cp)$", re.IGNORECASE)


def coin_order(data: dict[str, Any] | None = None) -> tuple[str, ...]:
    return COIN_ORDER if data is None else tuple(rs(data).COIN_ORDER)


def coin_in_cp(data: dict[str, Any] | None = None) -> dict[str, int]:
    return dict(COIN_IN_CP) if data is None else dict(rs(data).COIN_IN_CP)


def parse_coins(tokens: Iterable[str], order: Sequence[str] = COIN_ORDER) -> dict[str, int]:
    out = {c: 0 for c in order}
    seen = False
    for tok in tokens:
        for piece in re.findall(r"\d+\s*(?:pp|gp|ep|sp|cp)", str(tok), re.IGNORECASE):
            m = _COIN_RE.match(piece.replace(" ", ""))
            if not m:
                continue
            coin = m.group(2).lower()
            if coin not in out:
                raise StateError(
                    f"{coin} is not a coin in this campaign's ruleset "
                    f"(it uses {', '.join(order)}). Electrum is a D&D denomination; "
                    f"Pathfinder has no equivalent."
                )
            out[coin] += int(m.group(1))
            seen = True
    if not seen:
        raise StateError("no coins found — write amounts like '42gp 3sp'")
    return out


def coins_to_cp(coins: dict[str, int], rates: dict[str, int] = COIN_IN_CP) -> int:
    return sum(int(coins.get(c, 0)) * rates[c] for c in rates)


def cp_to_coins(total: int, rates: dict[str, int] = COIN_IN_CP) -> dict[str, int]:
    """Break a copper total into the largest coins first, per the ruleset's own set."""
    out = {}
    left = total
    for c in sorted(rates, key=lambda k: -rates[k]):
        out[c], left = divmod(left, rates[c])
    return out


def format_coins(coins: dict[str, int], order: Sequence[str] = COIN_ORDER) -> str:
    parts = [f"{coins[c]} {c}" for c in order if coins.get(c)]
    return ", ".join(parts) if parts else "0 cp"


def gold_change(data: dict[str, Any], tokens: Sequence[str], sign: int) -> list[str]:
    """Add or spend coins.

    Gaining coins keeps the denominations as received, so a purse reads back as what the
    party actually picked up rather than as the tidiest equivalent. Spending pays from the
    matching denominations first and only breaks larger coins when it has to, which is what
    happens at a table.
    """
    order = coin_order(data)
    rates = coin_in_cp(data)
    amount = parse_coins(tokens, order)
    purse = data.setdefault("party", {}).setdefault("gold", {c: 0 for c in order})
    for c in order:
        purse.setdefault(c, 0)
    if sign > 0:
        for c in order:
            purse[c] = int(purse[c]) + int(amount.get(c, 0))
        return [f"party gains {format_coins(amount, order)} → {format_coins(purse, order)}"]

    have = coins_to_cp(purse, rates)
    cost = coins_to_cp(amount, rates)
    if cost > have:
        raise StateError(
            f"the party holds {format_coins(purse, order)} (worth {have} cp) and cannot part "
            f"with {format_coins(amount, order)} (worth {cost} cp) — refusing to go negative"
        )
    owed = cost
    broke = False
    for c in order:  # pay from the largest matching denomination down
        want = min(int(amount.get(c, 0)), int(purse[c]))
        if want:
            purse[c] -= want
            owed -= want * rates[c]
    if owed > 0:
        # Break the largest coins available until the rest is covered, then give change.
        pool = coins_to_cp(purse, rates)
        purse.update(cp_to_coins(pool - owed, rates))
        broke = True
    out = [f"party spends {format_coins(amount, order)} → {format_coins(purse, order)}"]
    if broke:
        out.append("(larger coins were broken to make the payment)")
    return out


def gold_set(data: dict[str, Any], tokens: Sequence[str]) -> list[str]:
    order = coin_order(data)
    coins = parse_coins(tokens, order)
    if any(v < 0 for v in coins.values()):
        raise StateError("coin counts cannot be negative")
    data.setdefault("party", {})["gold"] = {c: int(coins.get(c, 0)) for c in order}
    return [f"purse set to {format_coins(data['party']['gold'], order)}"]


def item_container(data: dict[str, Any], owner: str | None) -> tuple[str, list[dict[str, Any]]]:
    if owner in (None, "", "stash", "party"):
        return "party stash", data.setdefault("party", {}).setdefault("stash", [])
    key, pc = find_character(data, owner)
    return pc["name"], pc.setdefault("items", [])


#: How each ruleset measures what an item weighs, and which field holds it. Both D&D
#: editions count pounds; only Pathfinder uses Bulk. The field is what `state.json` stores,
#: so an item recorded under one ruleset reads correctly under the other D&D edition and
#: is refused by name under Pathfinder.
ENCUMBRANCE_FIELD = {
    "pf2e": ("bulk", "--bulk", "Bulk"),
    "dnd5e": ("weight", "--weight", "pounds"),
    "dnd4e": ("weight", "--weight", "pounds"),
}


def item_add(
    data: dict[str, Any],
    name: str,
    qty: int,
    owner: str | None,
    bulk: str | None,
    kind: str | None,
    charges: int | None,
    level: int | None,
    weight: str | None = None,
) -> list[str]:
    """Add an item, recording its weight in whichever unit the campaign's game uses.

    Pathfinder measures Bulk; D&D measures pounds. Writing the wrong one would produce a
    carried total that silently means nothing, so the wrong flag is refused by name
    rather than stored.
    """
    if qty < 1:
        raise StateError(f"cannot add {qty} of an item")
    sid = system_of(data)
    field, flag, unit = ENCUMBRANCE_FIELD[sid]
    given = {"bulk": bulk, "weight": weight}
    # Any unit that is not this ruleset's own is refused by name. Keyed on the field rather
    # than the ruleset, so the two D&D editions sharing pounds is not a special case.
    for other_field, other_flag, other_unit in ENCUMBRANCE_FIELD.values():
        if other_field != field and given.get(other_field) is not None:
            raise StateError(
                f"{other_flag} measures {other_unit}, which is another ruleset's unit — this "
                f"is a {rules.short_of(sid)} campaign, so use {flag} ({unit})"
            )
    value = given[field]
    where, items = item_container(data, owner)
    for it in items:
        if it["name"].lower() == name.lower() and charges is None:
            it["qty"] = int(it.get("qty", 1)) + qty
            return [f"{where}: {it['name']} ×{it['qty']}"]
    items.append(
        {
            "name": name,
            "qty": qty,
            field: value if value is not None else ("-" if sid == "pf2e" else 0),
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


def carry_report(data: dict[str, Any]) -> list[dict[str, Any]]:
    """What each carrier is carrying, against this ruleset's own limits.

    Pathfinder measures Bulk against an encumbered threshold and a hard maximum; D&D
    measures pounds against a single capacity and has no intermediate encumbered band.
    Both return rows with `name`, `carried`, `counted`, `max`, `unit`, `over_max`,
    `encumbered` and a ready-made `line`, so the renderers do not need to know which.
    The per-game reasoning and sources live in `pf2e.carry_report` / `dnd5e.carry_report`.
    """
    return rs(data).carry_report(data)


def bulk_report(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Pathfinder's name for `carry_report`, kept for callers that already use it."""
    return carry_report(data)


def daily_prep(data: dict[str, Any]) -> list[str]:
    """What a night's rest restores: daily preparations in PF2e, a Long Rest in D&D."""
    return rs(data).daily_reset(data)


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


def blank_combatant(name: str, side: str, system: str | None = None, **kw: Any) -> dict[str, Any]:
    """A combatant in the tracker. The action economy half comes from the ruleset.

    Pathfinder gives three actions, a reaction and a multiple attack penalty step.
    D&D gives one action, a Bonus Action where a feature grants one, a movement
    allowance in feet and a reaction. Neither shape appears in the other's tracker, so
    a column can never imply a resource the game does not have.
    """
    mod = rules.load(system)
    c = {
        "id": kw.get("id") or slugify(name),
        "name": name,
        "side": side,  # party | adversary | neutral
        "ref": kw.get("ref"),  # a key in state["pcs"]; HP and conditions live there
        "initiative": kw.get("initiative"),
        "initiative_natural": kw.get("initiative_natural"),
        "hp": None if kw.get("ref") else {"current": kw.get("hp", 0), "max": kw.get("hp", 0), "temp": 0},
        "conditions": [] if not kw.get("ref") else None,
        "position": kw.get("position"),
        "squad": kw.get("squad"),
        "level": kw.get("level"),
        "cr": kw.get("cr"),
        "notes": kw.get("notes", ""),
        "defeated": False,
        **mod.blank_combatant_fields(**kw),
    }
    if mod.SYSTEM_ID == "pf2e":
        c["dying"] = 0 if not kw.get("ref") else None
    else:
        # Both D&D editions keep a death clock on the combatant; its shape comes from the
        # ruleset, because 4e counts failures only and 2024 counts successes and Stable too.
        c["base_speed"] = c.get("speed", 30 if mod.SYSTEM_ID == "dnd5e" else 6)
        blank = dict(getattr(mod, "BLANK_DEATH_SAVES", {}) or {})
        c["death_saves"] = None if kw.get("ref") else blank
        if mod.SYSTEM_ID == "dnd4e" and not kw.get("ref"):
            c["hp_below_zero"] = 0
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
    c = blank_combatant(name, side, system=system_of(data), **kw)
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
    mod = rs(data)
    if mod.SYSTEM_ID in ("dnd5e", "dnd4e"):
        # Dash (2024) and a run action (4e) raised the Speed for one turn only; put it back
        # before the reset.
        if nxt.get("base_speed") is not None:
            nxt["speed"] = nxt["base_speed"]
    have = mod.reset_turn(nxt)
    notes.append(f"{nxt['name']}'s turn (round {e['round']}), {have}")
    if mod.SYSTEM_ID in ("dnd5e", "dnd4e") and int((combatant_hp(data, nxt) or {}).get("current", 1)) == 0:
        ref = nxt.get("ref")
        target = None
        if ref:
            try:
                _, target = find_character(data, ref)
            except StateError:
                target = None
        else:
            target = nxt
        if target is not None and not target.get("dead") and not (
                target.get("death_saves") or {}).get("stable"):
            notes.append(
                f"⚠ {nxt['name']} starts their turn at 0 HP — roll a Death Saving Throw now: "
                f"`state.py --campaign {data.get('campaign', '<slug>')} death-save roll "
                f"{ref or nxt['id']}`"
            )
    return notes


def encounter_action(data: dict[str, Any], who: str, n: int, kind: str = "action") -> list[str]:
    c = find_combatant(data, who)
    try:
        note = rs(data).spend_action(c, kind, n)
    except ValueError as exc:
        raise StateError(str(exc)) from exc
    return [f"{c['name']}: {note}"]


def encounter_map_step(data: dict[str, Any], who: str, step: int | None) -> list[str]:
    if system_of(data) != "pf2e":
        raise StateError(
            "the multiple attack penalty is a Pathfinder rule and this is a "
            f"{rules.short_of(system_of(data))} campaign. D&D 2024 has no such penalty: extra "
            "attacks come from the Attack action and the Extra Attack feature, at no penalty."
        )
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
    mod = rs(data)
    cols = mod.ENCOUNTER_COLUMNS
    head = "".join(f"{name:<{width}} " for name, width in cols)
    out.append(f"{'':2} {'combatant':<22} {'init':>4} {'HP':>12} {head}{'pos':<5} conditions")
    for i, c in enumerate(e["combatants"]):
        hp = combatant_hp(data, c)
        hp_s = f"{hp['current']}/{hp['max']}" if hp else "?"
        conds: list[dict[str, Any]] = []
        flags: list[str] = []
        if c.get("ref"):
            try:
                _, pc = find_character(data, c["ref"])
            except StateError:
                cs_note = f"⚠ ref {c['ref']!r} has no character in pcs"
                conds = [{"name": cs_note}]
            else:
                conds = pc.get("conditions", [])
                flags = mod.tracked_condition_flags(pc)
        else:
            conds = c.get("conditions") or []
            flags = mod.tracked_condition_flags(c)
        # The separately-tracked fields come only from the ruleset's own flags. Rendering
        # `dying` again here printed it twice in the column the GM reads every turn.
        cs = ", ".join(f"{x['name']}{' ' + str(x['value']) if x.get('value') else ''}" for x in conds)
        cs = ", ".join(flags + ([cs] if cs else []))
        mark = "→" if i == int(e.get("turn_index", 0)) else " "
        cells = "".join(f"{v:<{w}} " for v, (_, w) in zip(mod.combatant_action_cells(c), cols))
        out.append(
            f"{mark:2} {c['name']:<22} {str(c.get('initiative') or '-'):>4} {hp_s:>12} "
            f"{cells}{str(c.get('position') or '-'):<5} {cs}"
        )
    out.append("")
    out.append(mod.ACTION_ECONOMY["summary"])
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
    a(f"- Ruleset: **{rs(data).SYSTEM_NAME}**")
    a("")
    a("## Scene")
    a("")
    a(f"- **Where:** {data.get('location', 'unset')}")
    a(f"- **When:** {pf2e.format_time(data.get('time', {}))}")
    sit = (data.get("notes") or {}).get("situation") or "_(no situation paragraph recorded yet)_"
    a("")
    a(sit)
    a("")

    mod = rs(data)
    a("## Party")
    a("")
    a("| Character | " + " | ".join(mod.SHEET_COLUMNS) + " |")
    a("|---" * (len(mod.SHEET_COLUMNS) + 1) + "|")
    for key, pc in data.get("pcs", {}).items():
        conds = []
        for c in pc.get("conditions", []):
            conds.append(f"{c['name']}" + (f" {c['value']}" if c.get("value") else "") +
                         (f" [{describe_duration(c.get('duration') or {})}]" if (c.get("duration") or {}).get("kind") != "until-removed" else ""))
        conds = mod.tracked_condition_flags(pc) + conds
        cells = mod.sheet_lines(pc, conditions=", ".join(conds) or "—")
        a(f"| {pc.get('name', key)} | " + " | ".join(cells) + " |")
    a("")

    slotted = [(k, pc) for k, pc in data.get("pcs", {}).items() if pc.get("spell_slots")]
    if slotted:
        word = slot_word(data)
        a("### Spell slots")
        a("")
        for key, pc in slotted:
            bits = []
            for rank in sorted(pc["spell_slots"], key=lambda r: int(r)):
                e = pc["spell_slots"][rank]
                bits.append(f"{word} {rank}: {int(e.get('max', 0)) - int(e.get('used', 0))}/{e.get('max', 0)}")
            a(f"- **{pc.get('name', key)}** — " + "; ".join(bits))
        a("")

    a("## Money and carried items")
    a("")
    a(f"- **Purse:** {format_coins(data.get('party', {}).get('gold', {}), coin_order(data))}")
    for row in carry_report(data):
        flag = " — **OVER THE LIMIT**" if row["over_max"] else (" — **encumbered**" if row["encumbered"] else "")
        a(f"- **{row['name']}** {row['line']}{flag}")
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
    p.add_argument("--system", default=None,
                   help="ruleset: pf2e, dnd5e (also '5.5e') or dnd4e (also '4e'). "
                        "Required for a new campaign.")
    p.add_argument("--force", action="store_true")

    sub.add_parser("migrate", help="bring state.json forward to the current schema and re-render")

    p = sub.add_parser("add-character", help="add a PC, ally, sidekick or companion")
    p.add_argument("name")
    p.add_argument("--kind", default="pc", choices=["pc", "ally", "sidekick", "companion", "familiar", "eidolon"])
    p.add_argument("--level", type=int, default=1)
    p.add_argument("--hp", type=int, default=0)
    p.add_argument("--ac", type=int, default=0)
    p.add_argument("--speed", type=int, default=None)
    p.add_argument("--sheet", default=None)
    g = p.add_argument_group("Pathfinder")
    g.add_argument("--fort", type=int, default=0)
    g.add_argument("--ref", type=int, default=0)
    g.add_argument("--will", type=int, default=0)
    g.add_argument("--perception", type=int, default=0)
    g.add_argument("--str-mod", type=int, default=0)
    g.add_argument("--hero-points", type=int, default=1)
    g = p.add_argument_group("D&D 2024")
    for ab in ("str", "dex", "con", "int", "wis", "cha"):
        g.add_argument(f"--{ab}", type=int, default=None, help=f"{ab.upper()} score")
    g.add_argument("--save", action="append", default=[], metavar="ABIL:MOD",
                   help="a saving throw modifier, e.g. --save dex:+5; repeatable")
    g.add_argument("--passive-perception", type=int, default=None)
    g.add_argument("--initiative", type=int, default=None, help="initiative modifier")
    g.add_argument("--hit-die", type=int, default=None, choices=[6, 8, 10, 12])
    g.add_argument("--size", default=None)
    g = p.add_argument_group("D&D 4e")
    g.add_argument("--surges", type=int, default=None,
                   help="the class's healing surges per day, from its class entry; the "
                        "Constitution modifier is added to it here")

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

    p = sub.add_parser("death-save",
                       help="both D&D editions: record death saving throw results "
                            "(2024 counts successes too; 4e counts failures only)")
    q = p.add_subparsers(dest="sub", required=True)
    r = q.add_parser("record", help="add successes and/or failures from rolled saves")
    r.add_argument("who")
    r.add_argument("--successes", type=int, default=0,
                   help="D&D 2024 only; 4e has no success counter")
    r.add_argument("--failures", type=int, default=0)
    r.add_argument("--natural", type=int, default=None,
                   help="4e: the natural die result, so a 20 reports the healing surge")
    r.add_argument("--reason", default="")
    r = q.add_parser("roll", help="roll a real death saving throw and apply it")
    r.add_argument("who")
    r = q.add_parser("stabilise", help="D&D 2024: a successful DC 10 Wisdom (Medicine) check")
    r.add_argument("who")
    r = q.add_parser("reset", help="clear the counters (healing does this automatically)")
    r.add_argument("who")

    p = sub.add_parser("exhaustion", help="D&D: set an Exhaustion level (6 is death)")
    q = p.add_subparsers(dest="sub", required=True)
    r = q.add_parser("set")
    r.add_argument("who")
    r.add_argument("value", type=int)
    r = q.add_parser("add")
    r.add_argument("who")
    r.add_argument("n", type=int, nargs="?", default=1)

    p = sub.add_parser("inspiration", help="D&D: Heroic Inspiration, which does not stack")
    q = p.add_subparsers(dest="sub", required=True)
    for verb in ("give", "spend"):
        r = q.add_parser(verb)
        r.add_argument("who")

    p = sub.add_parser("hit-dice", help="D&D: spend Hit Dice on a Short Rest")
    q = p.add_subparsers(dest="sub", required=True)
    r = q.add_parser("spend")
    r.add_argument("who")
    r.add_argument("n", type=int, nargs="?", default=1)
    r = q.add_parser("set")
    r.add_argument("who")
    r.add_argument("--max", type=int, required=True)
    r.add_argument("--die", type=int, default=8, choices=[6, 8, 10, 12])
    r.add_argument("--used", type=int, default=0)

    p = sub.add_parser("concentration", help="D&D: start or drop Concentration")
    q = p.add_subparsers(dest="sub", required=True)
    r = q.add_parser("start")
    r.add_argument("who")
    r.add_argument("on")
    r = q.add_parser("drop")
    r.add_argument("who")
    r = q.add_parser("check", help="the Constitution save DC after taking damage")
    r.add_argument("who")
    r.add_argument("damage", type=int)

    p = sub.add_parser("attune", help="D&D: attune to or release a magic item")
    q = p.add_subparsers(dest="sub", required=True)
    r = q.add_parser("add")
    r.add_argument("who")
    r.add_argument("item")
    r = q.add_parser("remove")
    r.add_argument("who")
    r.add_argument("item")
    r = q.add_parser("list")
    r.add_argument("who")

    p = sub.add_parser("surge", help="D&D 4e: healing surges, the per-day healing pool")
    q = p.add_subparsers(dest="sub", required=True)
    r = q.add_parser("spend")
    r.add_argument("who")
    r.add_argument("n", nargs="?", type=int, default=1)
    r = q.add_parser("set")
    r.add_argument("who")
    r.add_argument("--max", dest="maximum", type=int, default=None)
    r.add_argument("--used", type=int, default=None)
    r = q.add_parser("list")
    r.add_argument("who", nargs="?", default=None)

    p = sub.add_parser("second-wind",
                       help="D&D 4e: spend a surge and take a defence bonus, once per encounter")
    q = p.add_subparsers(dest="sub", required=True)
    r = q.add_parser("use")
    r.add_argument("who")
    r = q.add_parser("reset", help="a short rest restores it; this is the manual form")
    r.add_argument("who")

    p = sub.add_parser("action-point", help="D&D 4e: action points, one spend per encounter")
    q = p.add_subparsers(dest="sub", required=True)
    r = q.add_parser("spend")
    r.add_argument("who")
    r.add_argument("n", nargs="?", type=int, default=1)
    r = q.add_parser("set")
    r.add_argument("who")
    r.add_argument("value", type=int)

    p = sub.add_parser("milestone",
                       help="D&D 4e: every second encounter without an extended rest, which "
                            "grants an action point")
    p.add_argument("--who", default=None, help="one character, or omit for the whole party")

    p = sub.add_parser("power", help="D&D 4e: encounter and daily powers (at-will is not tracked)")
    q = p.add_subparsers(dest="sub", required=True)
    r = q.add_parser("add")
    r.add_argument("who")
    r.add_argument("name")
    r.add_argument("bucket", choices=["encounter", "daily"])
    r = q.add_parser("use")
    r.add_argument("who")
    r.add_argument("name")
    r = q.add_parser("restore", help="hand a power back, e.g. after a rewind")
    r.add_argument("who")
    r.add_argument("name")
    r = q.add_parser("list")
    r.add_argument("who")

    p = sub.add_parser("hp-below",
                       help="D&D 4e: how far below zero a dying character has fallen "
                            "(damage keeps this itself; this is the correction)")
    p.add_argument("who")
    p.add_argument("value", type=int, help="the depth as a positive number: 7 means -7 HP")

    p = sub.add_parser("short-rest",
                       help="D&D 2024: a one-hour Short Rest. D&D 4e: five minutes")
    p.add_argument("--who", default=None, help="limit the rest to one character")

    sub.add_parser("daily-prep",
                   help="a night's rest: PF2e daily preparations, or a D&D Long Rest")
    sub.add_parser("long-rest", help="D&D 2024's name for daily-prep")
    sub.add_parser("extended-rest", help="D&D 4e's name for daily-prep: six hours")

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
    r.add_argument("--bulk", default=None,
                   help="PF2e: '1', '2', 'L' for light, '-' for negligible")
    r.add_argument("--weight", default=None,
                   help="both D&D editions: weight in pounds, e.g. 55 or '1/2'")
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
    r.add_argument("--level", type=int, default=None,
                   help="PF2e and D&D 4e: creature level")
    r.add_argument("--cr", default=None, help="D&D 2024: Challenge Rating, e.g. 1/4")
    r.add_argument("--speed", type=int, default=None,
                   help="D&D 2024: movement allowance in feet. D&D 4e: in squares")
    r.add_argument("--bonus-action", action="store_true",
                   help="D&D 2024: this combatant has a feature granting a Bonus Action")
    r.add_argument("--role", default=None,
                   help="D&D 4e: artillery, brute, controller, lurker, minion, "
                        "skirmisher or soldier")
    r.add_argument("--rank", default=None,
                   help="D&D 4e: standard, elite, solo or minion (a minion has 1 HP)")
    r.add_argument("--id", default=None)
    r.add_argument("--notes", default="")
    q.add_parser("next")
    q.add_parser("status")
    q.add_parser("end")
    r = q.add_parser("action")
    r.add_argument("who")
    r.add_argument("n", nargs="?", type=int, default=1)
    r.add_argument("--kind", default="action",
                   help="PF2e: actions. D&D: action, bonus-action, move (n is feet), dash")
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
    sub.add_parser("carry", help="report what each carrier is carrying against their limits")
    sub.add_parser("bulk", help="Pathfinder's name for `carry`")

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
        system = args.system or rules.declared_in_campaign_md(slug)
        if not system:
            raise StateError(
                "a new campaign must say which game it runs: pass --system pf2e, "
                "--system 5.5e or --system 4e (or put a `System:` line in CAMPAIGN.md "
                "first). Nothing defaults here, because a state written under the wrong "
                "ruleset carries the wrong fields from its first line."
            )
        data = blank_state(slug, args.title, args.transparency, system=system)
        save(slug, data)
        write_render(slug, data)
        return [f"wrote {p.relative_to(repo_root())} and CHECKPOINT.md "
                f"for a {rules.short_of(system)} campaign"], False, None

    data = load(slug)

    if cmd == "migrate":
        was = data.get("migrated_from_schema")
        write_render(slug, data)
        note = (f"schema {was} → {SCHEMA_VERSION}" if was else
                f"already at schema {SCHEMA_VERSION}")
        return [f"{slug}: {note}, ruleset {rs(data).SYSTEM_SHORT}", "re-rendered CHECKPOINT.md"], True, data

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
        sid = system_of(data)
        pc = blank_character(args.name, args.kind, args.level, system=sid)
        pc["hp"] = {"current": args.hp, "max": args.hp, "temp": 0}
        pc["ac"] = args.ac
        pc["sheet"] = args.sheet or f"characters/{key}.md"
        wrong: list[str] = []
        if sid == "pf2e":
            pc.update({
                "saves": {"fortitude": args.fort, "reflex": args.ref, "will": args.will},
                "perception": args.perception,
                "speed": args.speed if args.speed is not None else 25,
                "str_mod": args.str_mod,
                "hero_points": args.hero_points,
            })
            wrong = [f"--{a}" for a in ("str", "dex", "con", "int", "wis", "cha")
                     if getattr(args, a, None) is not None]
            wrong += [n for n, v in (("--save", args.save), ("--passive-perception", args.passive_perception),
                                     ("--initiative", args.initiative), ("--hit-die", args.hit_die),
                                     ("--size", args.size), ("--surges", args.surges)) if v]
        elif sid == "dnd5e":
            import dnd5e
            abil = {a: getattr(args, a) for a in dnd5e.ABILITIES}
            scores = {a: (v if v is not None else 10) for a, v in abil.items()}
            saves = dict(pc["saves"])
            for spec in args.save:
                if ":" not in spec:
                    raise StateError(f"--save wants ABIL:MOD, e.g. dex:+5 (got {spec!r})")
                ab, mod = spec.split(":", 1)
                ab = ab.strip().lower()[:3]
                if ab not in dnd5e.ABILITIES:
                    raise StateError(f"{ab!r} is not an ability ({', '.join(dnd5e.ABILITIES)})")
                saves[ab] = int(mod)
            die = args.hit_die or 8
            pc.update({
                "abilities": scores,
                "strength": scores["str"],
                "saves": saves,
                "proficiency_bonus": dnd5e.proficiency_bonus(args.level),
                "passive_perception": (args.passive_perception if args.passive_perception is not None
                                       else 10 + dnd5e.ability_modifier(scores["wis"])),
                "initiative_mod": (args.initiative if args.initiative is not None
                                   else dnd5e.ability_modifier(scores["dex"])),
                "speed": args.speed if args.speed is not None else 30,
                "size": args.size or "Medium",
                "hit_dice": {"die": die, "max": int(args.level), "used": 0},
            })
            wrong = [n for n, v in (("--fort", args.fort), ("--ref", args.ref), ("--will", args.will),
                                    ("--perception", args.perception), ("--str-mod", args.str_mod),
                                    ("--surges", args.surges))
                     if v]
        else:
            import dnd4e
            scores = {a: (getattr(args, a, None) or 10) for a in dnd4e.ABILITIES}
            # In 4e, Fortitude / Reflex / Will are defence NUMBERS like AC, not the save
            # modifiers the same three flags mean in Pathfinder.
            if args.surges is None:
                surges = 0
            else:
                surges = dnd4e.surges_per_day(args.surges, scores["con"])
            pc.update({
                "abilities": scores,
                "strength": scores["str"],
                "defences": {"ac": args.ac, "fortitude": args.fort,
                             "reflex": args.ref, "will": args.will},
                "half_level": int(args.level) // 2,
                "initiative_mod": (args.initiative if args.initiative is not None
                                   else dnd4e.ability_modifier(scores["dex"])),
                "speed": args.speed if args.speed is not None else 6,
                "healing_surges": {"max": surges, "used": 0},
            })
            wrong = [n for n, v in (("--perception", args.perception),
                                    ("--str-mod", args.str_mod),
                                    ("--save", args.save),
                                    ("--passive-perception", args.passive_perception),
                                    ("--hit-die", args.hit_die),
                                    ("--size", args.size)) if v]
        data.setdefault("pcs", {})[key] = pc
        out = [f"added {args.name} ({args.kind}, level {args.level}, {args.hp} HP) as `{key}` "
               f"— {rs(data).SYSTEM_SHORT} sheet"]
        if sid == "dnd4e":
            import dnd4e
            if not int((pc.get("healing_surges") or {}).get("max", 0)):
                out.append(
                    "⚠ no healing surge pool set. It is the class's own surges-per-day plus the "
                    "Constitution modifier, and the class number is not open content — pass "
                    "`--surges <class value>` or set the pool with `surge set`. Surges are 4e's "
                    "attrition clock, so a pool of 0 makes the character unhealable."
                )
            if args.hp:
                out.append(
                    f"A healing surge is worth {dnd4e.surge_value(args.hp)} hit points; "
                    f"bloodied at {args.hp // 2}; death at "
                    f"{dnd4e.death_threshold(args.hp)} hit points."
                )
        if wrong:
            out.append(f"⚠ ignored {', '.join(sorted(set(wrong)))}: "
                       f"not {rs(data).SYSTEM_SHORT} fields")
        return out, True, data

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
        # The ruleset guard comes first: told to make a recovery check on a D&D campaign,
        # "there is no recovery check in this game" is the useful answer, and "they are not
        # dying" is a confusing one about a field that game does not have.
        if system_of(data) != "pf2e":
            raise _wrong_game(data, "dying", "pf2e")
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
        require_slots(data)
        word = slot_word(data)
        if sub == "use":
            return slots_use(data, args.who, args.rank, args.n), True, data
        if sub == "set":
            _, pc = find_character(data, args.who)
            pc.setdefault("spell_slots", {})[str(args.rank)] = {"max": args.max, "used": 0}
            return [f"{pc['name']}: {word} {args.rank} — {args.max} slot(s)"], True, data
        _, pc = find_character(data, args.who)
        for e in pc.get("spell_slots", {}).values():
            e["used"] = 0
        return [f"{pc['name']}: all slots restored"], True, data

    if cmd in ("daily-prep", "long-rest", "extended-rest"):
        if cmd == "long-rest" and system_of(data) != "dnd5e":
            raise _wrong_game(data, "long rest", "dnd5e")
        if cmd == "extended-rest" and system_of(data) != "dnd4e":
            raise _wrong_game(data, "extended rest", "dnd4e")
        return daily_prep(data), True, data

    if cmd == "short-rest":
        if system_of(data) == "dnd4e":
            import dnd4e
            who = getattr(args, "who", None)
            out = dnd4e.short_rest(data, who if who in (data.get("pcs") or {}) else None)
            return out, True, data
        if system_of(data) != "dnd5e":
            raise _wrong_game(data, "short rest", "dnd5e")
        import dnd5e
        who = getattr(args, "who", None)
        targets = ([find_character(data, who)] if who
                   else list((data.get("pcs") or {}).items()))
        out = [f"Short Rest ({dnd5e.SHORT_REST_HOURS} hour). What it restores and what it does not:"]
        for _, pc in targets:
            hd = pc.get("hit_dice") or {}
            left = int(hd.get("max", 0)) - int(hd.get("used", 0))
            pc["concentration"] = None
            out.append(
                f"  {pc['name']}: {left}d{hd.get('die', 8)} Hit Dice available to spend "
                f"(`hit-dice spend`), Concentration dropped"
            )
        out += [
            "Spell slots do NOT come back on a Short Rest — only features whose own text says so.",
            "Hit Dice restore HP only when spent: roll them, then apply the total with `heal`.",
            "An interrupted Short Rest confers no benefits (SRD 5.2, 'Short Rest').",
        ]
        return out, True, data

    if cmd == "death-save":
        four = system_of(data) == "dnd4e"
        if sub == "record":
            if four:
                if args.successes:
                    raise StateError(
                        "a 4e death saving throw has no success counter — 10 or better is "
                        "simply not a failure, and a natural 20 lets the character spend a "
                        "healing surge. Record only failures."
                    )
                return death_save_record_4e(data, args.who, failures=args.failures,
                                            natural=args.natural,
                                            reason=args.reason), True, data
            return death_save_record(data, args.who, successes=args.successes,
                                     failures=args.failures, reason=args.reason), True, data
        if sub == "stabilise":
            if four:
                raise StateError(
                    "4e has no Stable state — a dying character keeps making death saving "
                    "throws until they are healed or the third failure kills them. Healing "
                    "any amount ends dying: use `heal`."
                )
            return death_save_stabilise(data, args.who), True, data
        if sub == "reset":
            if system_of(data) not in ("dnd5e", "dnd4e"):
                raise _wrong_game(data, "death saves", "dnd5e")
            _, pc = find_character(data, args.who)
            pc["death_saves"] = dict(blank_death_saves(data))
            if four:
                pc["hp_below_zero"] = 0
            return [f"{pc['name']}: {death_save_word(data)} counters reset"], True, data
        if sub == "roll":
            if four:
                return death_save_roll_4e(data, args.who, slug), True, data
            if system_of(data) != "dnd5e":
                raise _wrong_game(data, "death saves", "dnd5e")
            key, pc = find_character(data, args.who)
            ds = pc.get("death_saves") or {}
            # The save is a real roll from roll.py, logged like every other roll, and the
            # result is then written down here. Nothing is decided before it is rolled.
            res = subprocess.run(
                [sys.executable, str(Path(__file__).resolve().parent / "roll.py"), "death-save",
                 "--campaign", slug, "--system", "dnd5e",
                 "--actor", pc.get("name", key),
                 "--successes", str(int(ds.get("successes", 0))),
                 "--failures", str(int(ds.get("failures", 0))),
                 "--json", "--quiet"],
                capture_output=True, text=True,
            )
            if res.returncode != 0:
                raise StateError(f"the death save could not be rolled: {res.stderr.strip()}")
            rolled = json.loads(res.stdout)[0]
            out = [rolled["line"]]
            if rolled.get("natural") == 20:
                out += apply_healing(data, key, 1)
            else:
                succ = 1 if rolled["degree"] == "success" else 0
                fail = 2 if rolled.get("natural") == 1 else (0 if succ else 1)
                out += death_save_record(data, key, successes=succ, failures=fail,
                                         reason="rolled Death Saving Throw")
            return out, True, data

    if cmd == "surge":
        if sub == "spend":
            return surge_spend(data, args.who, args.n), True, data
        if sub == "set":
            return surge_set(data, args.who, args.maximum, args.used), True, data
        _need_4e(data, "healing surges")
        import dnd4e
        pcs = ([find_character(data, args.who)] if args.who
               else list((data.get("pcs") or {}).items()))
        out = []
        for _, pc in pcs:
            sg = pc.get("healing_surges") or {}
            hp_max = int((pc.get("hp") or {}).get("max", 0))
            out.append(
                f"{pc['name']}: {int(sg.get('max', 0)) - int(sg.get('used', 0))}/"
                f"{sg.get('max', 0)} healing surges"
                + (f", {dnd4e.surge_value(hp_max)} hit points each" if hp_max else "")
                + ("" if not pc.get("second_wind_used") else ", Second Wind already used")
            )
        return out or ["no characters"], False, data

    if cmd == "second-wind":
        return second_wind(data, args.who, reset=sub == "reset"), True, data

    if cmd == "action-point":
        if sub == "spend":
            return action_point_spend(data, args.who, args.n), True, data
        return action_point_set(data, args.who, args.value), True, data

    if cmd == "milestone":
        return milestone_reach(data, args.who), True, data

    if cmd == "power":
        if sub == "add":
            return power_add(data, args.who, args.name, args.bucket), True, data
        if sub == "use":
            return power_use(data, args.who, args.name), True, data
        if sub == "restore":
            return power_use(data, args.who, args.name, release=True), True, data
        _need_4e(data, "powers")
        _, pc = find_character(data, args.who)
        powers = pc.get("powers") or {}
        out = [f"{pc['name']}:"]
        for bucket in ("encounter", "daily"):
            for e in powers.get(bucket) or []:
                out.append(f"  {e.get('name')} [{bucket}] — "
                           + ("spent" if e.get("used") else "available"))
        if len(out) == 1:
            out.append("  no encounter or daily powers recorded (at-will powers are not tracked)")
        return out, False, data

    if cmd == "hp-below":
        return hp_below_set(data, args.who, args.value), True, data

    if cmd == "exhaustion":
        if sub == "set":
            return exhaustion_set(data, args.who, args.value), True, data
        _, pc = find_character(data, args.who)
        return exhaustion_set(data, args.who, int(pc.get("exhaustion", 0)) + args.n), True, data

    if cmd == "inspiration":
        return inspiration_set(data, args.who, held=sub == "give"), True, data

    if cmd == "hit-dice":
        if sub == "spend":
            return hit_dice_spend(data, args.who, args.n), True, data
        if system_of(data) != "dnd5e":
            raise _wrong_game(data, "hit-dice", "dnd5e")
        _, pc = find_character(data, args.who)
        if args.used > args.max:
            raise StateError(f"{args.used} spent of {args.max} Hit Dice is impossible")
        pc["hit_dice"] = {"die": args.die, "max": args.max, "used": args.used}
        return [f"{pc['name']}: {args.max - args.used}/{args.max}d{args.die} Hit Dice"], True, data

    if cmd == "concentration":
        if sub == "start":
            return concentration_set(data, args.who, args.on), True, data
        if sub == "drop":
            return concentration_set(data, args.who, None), True, data
        if system_of(data) != "dnd5e":
            raise _wrong_game(data, "concentration", "dnd5e")
        import dnd5e
        _, pc = find_character(data, args.who)
        conc = pc.get("concentration")
        if not conc:
            raise StateError(f"{pc['name']} is not concentrating on anything")
        name = conc.get("on") if isinstance(conc, dict) else conc
        dc = dnd5e.concentration_dc(args.damage)
        return [
            f"{pc['name']} took {args.damage} damage while concentrating on {name}",
            f"Constitution save DC {dc} to keep it (10 or half the damage, whichever is higher, max 30)",
            f"Roll it: `roll.py save \"1d20+<Con save>\" --dc {dc} --campaign {slug} "
            f"--label \"Concentration ({name})\"`",
        ], False, data

    if cmd == "attune":
        if sub == "list":
            if system_of(data) != "dnd5e":
                raise _wrong_game(data, "attunement", "dnd5e")
            _, pc = find_character(data, args.who)
            att = pc.get("attunement") or {}
            items = att.get("items") or []
            return [f"{pc['name']}: attuned to {len(items)}/{att.get('max', 3)} — "
                    f"{', '.join(items) or 'nothing'}"], False, data
        return attune(data, args.who, args.item, remove=sub == "remove"), True, data

    if cmd == "gold":
        if sub == "add":
            return gold_change(data, args.coins, +1), True, data
        if sub == "spend":
            return gold_change(data, args.coins, -1), True, data
        return gold_set(data, args.coins), True, data

    if cmd == "item":
        if sub == "add":
            return item_add(data, args.name, args.qty, args.owner, args.bulk, args.kind,
                            args.charges, args.level, weight=args.weight), True, data
        if sub == "remove":
            return item_remove(data, args.name, args.qty, args.owner), True, data
        if sub == "use":
            return item_use(data, args.name, args.owner, args.n), True, data
        out = []
        for key, pc in data.get("pcs", {}).items():
            out.append(f"{pc.get('name', key)}:")
            for it in pc.get("items", []) or [None]:
                field, _, unit = ENCUMBRANCE_FIELD[system_of(data)]
                out.append("  " + (f"{it['name']} ×{it.get('qty', 1)} "
                                   f"[{unit.lower()} {it.get(field, '-')}, {it.get('kind')}]"
                                   + (f", {it['charges']} charges" if it.get("charges") is not None else "")
                                   if it else "(nothing carried)"))
        stash = data.get("party", {}).get("stash", [])
        out.append("party stash:")
        out += ["  " + f"{it['name']} ×{it.get('qty', 1)}" for it in stash] or ["  (empty)"]
        out.append("")
        for row in carry_report(data):
            out.append(f"{row['name']}: {row['line']}")
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
        notes += xp_threshold_note(data, new)
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
            extra: dict[str, Any] = {}
            sid = system_of(data)
            role = getattr(args, "role", None)
            rank = getattr(args, "rank", None)
            if sid != "dnd4e" and (role or rank):
                bad = [f for f, v in (("--role", role), ("--rank", rank)) if v]
                raise StateError(
                    f"{', '.join(bad)} name D&D 4e's monster roles and ranks, and this is a "
                    f"{rules.short_of(sid)} campaign. Put the creature's role in --notes "
                    f"instead; neither sibling ruleset keys any rule off it."
                )
            if sid == "dnd5e":
                extra = {
                    "speed": args.speed if args.speed is not None else 30,
                    "bonus_action": 1 if args.bonus_action else 0,
                    "cr": args.cr,
                }
                if args.level is not None:
                    raise StateError(
                        "--level is Pathfinder's and 4e's creature scale; a D&D 2024 creature "
                        "has a Challenge Rating. Pass --cr instead (e.g. --cr 1/4)."
                    )
            elif sid == "dnd4e":
                import dnd4e
                if args.cr is not None:
                    raise StateError(
                        "--cr is D&D 2024's creature scale; a 4e monster has a level and a "
                        "role. Pass --level, and --role / --rank for its shape."
                    )
                if args.bonus_action:
                    raise StateError(
                        "--bonus-action is a D&D 2024 concept. 4e's near equivalent is the "
                        "minor action, which every combatant already has — the tracker's "
                        "`min` column."
                    )
                if role and role.lower() not in dnd4e.MONSTER_ROLES + dnd4e.PC_ROLES:
                    raise StateError(
                        f"{role!r} is not a 4e role (monsters: "
                        f"{', '.join(dnd4e.MONSTER_ROLES)}; characters: "
                        f"{', '.join(dnd4e.PC_ROLES)})"
                    )
                if rank and rank.lower() not in dnd4e.MONSTER_RANKS:
                    raise StateError(f"{rank!r} is not a 4e rank "
                                     f"({', '.join(dnd4e.MONSTER_RANKS)})")
                extra = {
                    "speed": args.speed if args.speed is not None else 6,
                    "role": role.lower() if role else None,
                    "rank": (rank or "standard").lower(),
                }
            elif args.cr is not None or args.bonus_action or args.speed is not None:
                bad = [f for f, v in (("--cr", args.cr), ("--bonus-action", args.bonus_action),
                                      ("--speed", args.speed)) if v]
                noun = ("are D&D 2024 concepts" if len(bad) > 1
                        else "is a D&D 2024 concept")
                raise StateError(
                    f"{', '.join(bad)} {noun} and this is a Pathfinder campaign — use --level "
                    f"for a creature's level, and Stride costs an action rather than drawing on "
                    f"a movement allowance"
                )
            out = encounter_add(
                data, args.name, args.side, ref=args.ref, initiative=args.initiative, hp=args.hp,
                position=args.position, squad=args.squad, level=args.level, id=args.id,
                notes=args.notes, **extra,
            )
            if sid == "dnd4e" and (rank or "").lower() == "minion" and args.hp not in (0, 1):
                out.append(
                    f"⚠ a 4e minion has exactly 1 hit point and takes no damage from a missed "
                    f"attack; {args.hp} was recorded. Set it with `hp` if that was not intended."
                )
            return out, True, data
        if sub == "next":
            return encounter_next(data), True, data
        if sub == "status":
            return encounter_status(data), False, data
        if sub == "end":
            return encounter_end(data), True, data
        if sub == "action":
            return encounter_action(data, args.who, args.n, args.kind), True, data
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

    if cmd in ("carry", "bulk"):
        # Each ruleset builds its own `line`, because the units and the thresholds differ:
        # Bulk against an encumbered band and a maximum, against pounds and a single
        # capacity. Reading row['bulk'] here used to raise KeyError on a D&D campaign.
        out = []
        for row in carry_report(data):
            flag = " OVER THE LIMIT" if row["over_max"] else (" encumbered" if row["encumbered"] else "")
            extra = ""
            if row.get("bulk_free"):
                extra = f" ({row['counted']:.1f} counted, {row['bulk_free']:.1f} free)"
            if row.get("bulk_bonus"):
                extra += f" (includes +{row['bulk_bonus']} from a feat)"
            if row.get("strength_assumed"):
                extra += " ⚠ Strength not recorded; assumed 10"
            out.append(f"{row['name']}: {row['line']}{extra}{flag}")
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
