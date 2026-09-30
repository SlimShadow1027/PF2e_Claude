#!/usr/bin/env python3
"""pf2e.py — the rules tables, as data, so nothing is recalled from memory.

Every table in this file carries a `Source:` note. Where a value could not be checked
against a source reachable from this machine it is marked `UNVERIFIED` in
`UNVERIFIED_TABLES` and listed in `DESIGN_NOTES.md`; `python3 tools/pf2e.py sources`
prints the whole provenance list.

Verification note: Archives of Nethys (2e.aonprd.com) was unreachable from the machine
that built this framework, so the numeric tables were checked against the Foundry VTT
PF2e system source — an ORC-licensed implementation that cites AoN rule IDs inline —
at version 8.5.1, commit 06b904d6ced9795c4c07af085e6f61a56f845c60. That is a secondary
source: it is a working implementation many tables have been played against, not the
book. Where it does not implement a table, the value here is marked UNVERIFIED.

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

FOUNDRY = (
    "foundryvtt/pf2e v8.5.1 @06b904d6ced9795c4c07af085e6f61a56f845c60 "
    "(ORC implementation citing Archives of Nethys inline)"
)

SOURCES: dict[str, str] = {}
UNVERIFIED_TABLES: list[str] = []


def _src(key: str, text: str, verified: bool = True) -> str:
    SOURCES[key] = text
    if not verified:
        UNVERIFIED_TABLES.append(key)
    return text


# --------------------------------------------------------------------------------------
# Difficulty classes
# --------------------------------------------------------------------------------------

LEVEL_DCS: dict[int, int] = {
    -1: 13, 0: 14, 1: 15, 2: 16, 3: 18, 4: 19, 5: 20, 6: 22, 7: 23, 8: 24, 9: 26,
    10: 27, 11: 28, 12: 30, 13: 31, 14: 32, 15: 34, 16: 35, 17: 36, 18: 38, 19: 39,
    20: 40, 21: 42, 22: 44, 23: 46, 24: 48, 25: 50,
}
_src(
    "level_dcs",
    "GM Core, DCs by Level (https://2e.aonprd.com/Rules.aspx?ID=552). Verified against "
    + FOUNDRY
    + ", src/module/dc.ts `dcByLevel`.",
)

SIMPLE_DCS: dict[str, int] = {"untrained": 10, "trained": 15, "expert": 20, "master": 30, "legendary": 40}
SIMPLE_DCS_PWOL: dict[str, int] = {"untrained": 10, "trained": 15, "expert": 20, "master": 25, "legendary": 30}
_src(
    "simple_dcs",
    "GM Core, Simple DCs (https://2e.aonprd.com/Rules.aspx?ID=552); the Proficiency Without "
    "Level column from the variant rule (https://2e.aonprd.com/Rules.aspx?ID=1370). Verified "
    "against " + FOUNDRY + ", src/module/dc.ts `simpleDCs` / `simpleDCsWithoutLevel`.",
)

DC_ADJUSTMENTS: dict[str, int] = {
    "incredibly easy": -10,
    "very easy": -5,
    "easy": -2,
    "normal": 0,
    "hard": 2,
    "very hard": 5,
    "incredibly hard": 10,
}
RARITY_ADJUSTMENTS: dict[str, int] = {"common": 0, "uncommon": 2, "rare": 5, "unique": 10}
_src(
    "dc_adjustments",
    "GM Core, Adjusting Difficulty and the rarity adjustments (https://2e.aonprd.com/Rules.aspx?ID=555). "
    "Verified against " + FOUNDRY + ", src/module/dc.ts `dcAdjustments` and `rarityToDCAdjustment` "
    "(uncommon → hard +2, rare → very hard +5, unique → incredibly hard +10).",
)


def level_dc(level: int, *, rarity: str = "common", pwol: bool = False) -> int:
    if level not in LEVEL_DCS:
        raise ValueError(f"no published level-based DC for level {level} (the table runs -1 to 25)")
    dc = LEVEL_DCS[level]
    if pwol:
        dc -= max(level, 0)
    return dc + RARITY_ADJUSTMENTS.get(rarity, 0)


def simple_dc(rank: str, *, rarity: str = "common", pwol: bool = False) -> int:
    table = SIMPLE_DCS_PWOL if pwol else SIMPLE_DCS
    key = rank.lower()
    if key not in table:
        raise ValueError(f"{rank!r} is not a proficiency rank ({', '.join(table)})")
    return table[key] + RARITY_ADJUSTMENTS.get(rarity, 0)


def spell_dc_level(rank: int) -> int:
    """The level-based DC a spell of this rank is measured against: rank x 2 - 1."""
    return rank * 2 - 1


# --------------------------------------------------------------------------------------
# Encounter building
# --------------------------------------------------------------------------------------

XP_PER_CHARACTER = 20
THREAT_MULTIPLIERS: dict[str, float] = {
    "trivial": 0.5,
    "low": 0.75,
    "moderate": 1.0,
    "severe": 1.5,
    "extreme": 2.0,
}
_src(
    "encounter_budgets",
    "GM Core, Encounter Budget (https://2e.aonprd.com/Rules.aspx?ID=575): 40/60/80/120/160 XP for a "
    "four-character party, adjusted 10/15/20/30/40 XP per character above or below four. Verified "
    "against " + FOUNDRY + ", src/scripts/macros/xp/index.ts `generateEncounterBudgets`, which "
    "computes partySize x 20 and multiplies by 0.5/0.75/1/1.5/2 — identical for a party of four "
    "and identical to the per-character adjustment for any other size.",
)

CREATURE_XP_BY_RELATIVE_LEVEL: dict[int, int] = {
    -4: 10, -3: 15, -2: 20, -1: 30, 0: 40, 1: 60, 2: 80, 3: 120, 4: 160,
}
CREATURE_XP_PWOL: dict[int, int] = {
    -7: 9, -6: 12, -5: 14, -4: 18, -3: 21, -2: 26, -1: 32, 0: 40,
    1: 48, 2: 60, 3: 72, 4: 90, 5: 108, 6: 135, 7: 160,
}
_src(
    "creature_xp",
    "GM Core, Creature XP by level relative to the party (https://2e.aonprd.com/Rules.aspx?ID=575), "
    "and the Proficiency Without Level column (https://2e.aonprd.com/Rules.aspx?ID=1371). Verified "
    "against " + FOUNDRY + ", src/scripts/macros/xp/index.ts `xpCreatureDifferences` and "
    "`xpVariantCreatureDifferences`.",
)

SIMPLE_HAZARD_XP: dict[int, int] = {-4: 2, -3: 3, -2: 4, -1: 6, 0: 8, 1: 12, 2: 16, 3: 24, 4: 32}
_src(
    "hazard_xp",
    "GM Core, Hazard XP: a simple hazard is worth a fifth of a creature of the same relative level; "
    "a complex hazard is worth the same as a creature. Verified against " + FOUNDRY
    + ", src/scripts/macros/xp/index.ts `xpSimpleHazardDifferences` and `getHazardXp`.",
)


def encounter_budgets(party_size: int) -> dict[str, int]:
    if party_size < 1:
        raise ValueError("a party needs at least one character")
    base = party_size * XP_PER_CHARACTER
    return {k: int(base * v) for k, v in THREAT_MULTIPLIERS.items()}


def creature_xp(party_level: int, creature_level: int, *, pwol: bool = False) -> int:
    table = CREATURE_XP_PWOL if pwol else CREATURE_XP_BY_RELATIVE_LEVEL
    diff = creature_level - party_level
    lo, hi = min(table), max(table)
    return table[max(lo, min(hi, diff))]


def hazard_xp(party_level: int, hazard_level: int, *, complex_hazard: bool = False, pwol: bool = False) -> int:
    if complex_hazard:
        return creature_xp(party_level, hazard_level, pwol=pwol)
    diff = hazard_level - party_level
    lo, hi = min(SIMPLE_HAZARD_XP), max(SIMPLE_HAZARD_XP)
    return SIMPLE_HAZARD_XP[max(lo, min(hi, diff))]


def rate_encounter(total_xp: int, party_size: int) -> str:
    b = encounter_budgets(party_size)
    for name in ("trivial", "low", "moderate", "severe"):
        if total_xp <= b[name]:
            return name
    return "extreme"


CREATURE_ADJUSTMENTS = {
    "weak": "-2 to AC, attack rolls, DCs, saves, Perception, skills and damage; HP down by "
            "10 (level 1-2), 15 (3-4), 20 (5-19) or 30 (level 20+). An adjusted creature's XP "
            "value is that of a creature one level lower.",
    "elite": "+2 to AC, attack rolls, DCs, saves, Perception, skills and damage; HP up by "
             "10 (level 1-2), 15 (3-4), 20 (5-19) or 30 (level 20+). An adjusted creature's XP "
             "value is that of a creature one level higher.",
}
_src(
    "creature_adjustments",
    "GM Core, Elite and Weak adjustments (https://2e.aonprd.com/Rules.aspx?ID=1027 area). "
    "UNVERIFIED — the HP steps by level band could not be checked against a source reachable "
    "from this machine. The +/-2 to numbers is well established; confirm the HP column before "
    "leaning on it.",
    verified=False,
)


# --------------------------------------------------------------------------------------
# Treasure and item bonuses
# --------------------------------------------------------------------------------------

TREASURE_BY_LEVEL: dict[int, int] = {
    1: 175, 2: 300, 3: 500, 4: 850, 5: 1350, 6: 2000, 7: 2900, 8: 4000, 9: 5700,
    10: 8000, 11: 11500, 12: 16500, 13: 25000, 14: 36500, 15: 54500, 16: 82500,
    17: 128000, 18: 208000, 19: 355000, 20: 490000,
}
_src(
    "treasure_by_level",
    "GM Core, Party Treasure by Level — total gp value of everything a FOUR-character party "
    "should find over one level. UNVERIFIED: the Foundry VTT system does not implement this "
    "table, and 2e.aonprd.com was unreachable, so these values come from the model's reading "
    "of GM Core rather than from a checked source. Verify every row before using it to pace a "
    "campaign's economy.",
    verified=False,
)

TREASURE_MIX = {"permanent": 0.50, "consumable": 0.25, "currency": 0.25}
_src(
    "treasure_mix",
    "GM Core's guidance that a level's treasure splits roughly half permanent items, a quarter "
    "consumables and a quarter currency and valuables. UNVERIFIED — treat the split as a "
    "rule of thumb rather than a table.",
    verified=False,
)

# Item bonuses expected at each level, taken from Automatic Bonus Progression, which is the
# official codification of the curve gear is assumed to follow.
ITEM_BONUS_BY_LEVEL: list[dict[str, Any]] = []
for _lvl in range(1, 21):
    ITEM_BONUS_BY_LEVEL.append(
        {
            "level": _lvl,
            "attack": 0 if _lvl < 2 else (1 if _lvl < 10 else (2 if _lvl < 16 else 3)),
            "striking_dice": 0 if _lvl < 4 else (1 if _lvl < 12 else (2 if _lvl < 19 else 3)),
            "ac": 0 if _lvl < 5 else (1 if _lvl < 11 else (2 if _lvl < 18 else 3)),
            "perception": 0 if _lvl < 7 else (1 if _lvl < 13 else (2 if _lvl < 19 else 3)),
            "saves": 0 if _lvl < 8 else (1 if _lvl < 14 else (2 if _lvl < 20 else 3)),
        }
    )
_src(
    "item_bonus_by_level",
    "GM Core variant rule Automatic Bonus Progression, which states the item-bonus curve the "
    "core math assumes: attack potency at levels 2/10/16, striking dice at 4/12/19, defence "
    "potency at 5/11/18, perception potency at 7/13/19, save potency at 8/14/20. Verified against "
    + FOUNDRY + ", src/module/actor/character/automatic-bonus-progression.ts "
    "(`getAttackPotency`, `getStrikingDice`, `getDefensePotency`, `abpValues`).",
)

EARN_INCOME: dict[int, dict[str, str]] = {
    0: {"failure": "1 cp", "trained": "5 cp", "expert": "5 cp", "master": "5 cp", "legendary": "5 cp"},
    1: {"failure": "2 cp", "trained": "2 sp", "expert": "2 sp", "master": "2 sp", "legendary": "2 sp"},
    2: {"failure": "4 cp", "trained": "3 sp", "expert": "3 sp", "master": "3 sp", "legendary": "3 sp"},
    3: {"failure": "8 cp", "trained": "5 sp", "expert": "5 sp", "master": "5 sp", "legendary": "5 sp"},
    4: {"failure": "1 sp", "trained": "7 sp", "expert": "8 sp", "master": "8 sp", "legendary": "8 sp"},
    5: {"failure": "2 sp", "trained": "9 sp", "expert": "1 gp", "master": "1 gp", "legendary": "1 gp"},
    6: {"failure": "3 sp", "trained": "1 gp 5 sp", "expert": "2 gp", "master": "2 gp", "legendary": "2 gp"},
    7: {"failure": "4 sp", "trained": "2 gp", "expert": "2 gp 5 sp", "master": "2 gp 5 sp", "legendary": "2 gp 5 sp"},
    8: {"failure": "5 sp", "trained": "2 gp 5 sp", "expert": "3 gp", "master": "3 gp", "legendary": "3 gp"},
    9: {"failure": "6 sp", "trained": "3 gp", "expert": "4 gp", "master": "4 gp", "legendary": "4 gp"},
    10: {"failure": "7 sp", "trained": "4 gp", "expert": "5 gp", "master": "6 gp", "legendary": "6 gp"},
    11: {"failure": "8 sp", "trained": "5 gp", "expert": "6 gp", "master": "8 gp", "legendary": "8 gp"},
    12: {"failure": "9 sp", "trained": "6 gp", "expert": "8 gp", "master": "10 gp", "legendary": "10 gp"},
    13: {"failure": "1 gp", "trained": "7 gp", "expert": "10 gp", "master": "15 gp", "legendary": "15 gp"},
    14: {"failure": "1 gp 5 sp", "trained": "8 gp", "expert": "15 gp", "master": "20 gp", "legendary": "20 gp"},
    15: {"failure": "2 gp", "trained": "10 gp", "expert": "20 gp", "master": "28 gp", "legendary": "28 gp"},
    16: {"failure": "2 gp 5 sp", "trained": "13 gp", "expert": "25 gp", "master": "36 gp", "legendary": "40 gp"},
    17: {"failure": "3 gp", "trained": "15 gp", "expert": "30 gp", "master": "45 gp", "legendary": "55 gp"},
    18: {"failure": "4 gp", "trained": "20 gp", "expert": "45 gp", "master": "70 gp", "legendary": "90 gp"},
    19: {"failure": "6 gp", "trained": "30 gp", "expert": "60 gp", "master": "100 gp", "legendary": "130 gp"},
    20: {"failure": "8 gp", "trained": "40 gp", "expert": "75 gp", "master": "150 gp", "legendary": "200 gp"},
    21: {"failure": "0 cp", "trained": "50 gp", "expert": "90 gp", "master": "175 gp", "legendary": "300 gp"},
}
_src(
    "earn_income",
    "Player Core, Earn Income — income per day by task level and proficiency, and the failure "
    "row. Verified against " + FOUNDRY
    + ", src/scripts/macros/earn-income.ts `REWARDS_BY_LEVEL`.",
)

ITEM_LEVEL_BY_SETTLEMENT = {
    "village": 2,
    "town": 6,
    "city": 10,
    "metropolis": 14,
    "capital / planar market": 20,
}
_src(
    "settlement_item_levels",
    "GM Core, settlement item-level availability. UNVERIFIED — the exact level cap per "
    "settlement size could not be checked from this machine. These are usable defaults, not "
    "quoted values; set them per campaign in WORLD.md and say so.",
    verified=False,
)


def treasure_for(level: int, party_size: int = 4) -> dict[str, Any]:
    if level not in TREASURE_BY_LEVEL:
        raise ValueError(f"no treasure row for level {level} (the table runs 1 to 20)")
    total_four = TREASURE_BY_LEVEL[level]
    per_character = total_four / 4.0
    total = per_character * party_size
    return {
        "level": level,
        "party_size": party_size,
        "total_gp": round(total, 1),
        "total_gp_for_four": total_four,
        "per_character_gp": round(per_character, 1),
        "permanent_gp": round(total * TREASURE_MIX["permanent"], 1),
        "consumable_gp": round(total * TREASURE_MIX["consumable"], 1),
        "currency_gp": round(total * TREASURE_MIX["currency"], 1),
        "unverified": True,
    }


# --------------------------------------------------------------------------------------
# Action economy
# --------------------------------------------------------------------------------------


def map_penalty(step: int, *, agile: bool = False) -> int:
    """The multiple attack penalty at the second (step 1) and third (step 2) attack.

    Source: Player Core, "Multiple Attack Penalty" — -5 on the second attack and -10 on the
    third, or -4 and -8 with an agile weapon. Verified against the Foundry VTT PF2e
    implementation (src/module/actor/helpers.ts `calculateMAPs`).
    """
    if step <= 0:
        return 0
    if step == 1:
        return -4 if agile else -5
    return -8 if agile else -10


_src(
    "map",
    "Player Core, Multiple Attack Penalty: -5/-10, or -4/-8 agile. Verified against "
    + FOUNDRY
    + ", src/module/actor/helpers.ts `calculateMAPs`.",
)

DEGREES_OF_SUCCESS = (
    "Critical success: total >= DC + 10.",
    "Success: total >= DC.",
    "Failure: total < DC.",
    "Critical failure: total <= DC - 10.",
    "A natural 20 improves the degree by one step; a natural 1 worsens it by one step.",
)
_src(
    "degrees",
    "Player Core / GM Core, Degrees of Success (https://2e.aonprd.com/Rules.aspx?ID=552). "
    "Verified against " + FOUNDRY + ", src/module/system/degree-of-success.ts.",
)

DYING_RULES = {
    "dying_max": 4,
    "recovery_dc": "10 + your current dying value",
    "crit_success": "dying value reduced by 2",
    "success": "dying value reduced by 1",
    "failure": "dying value increased by 1",
    "crit_failure": "dying value increased by 2",
    "damage_while_dying": "+1, or +2 from a critical hit or a critical failure on a save",
    "losing_dying": "you gain wounded 1, or increase wounded by 1",
    "starting_dying": "dying 1 when reduced to 0 HP, +1 if the hit was a critical, plus your wounded value",
    "doomed": "reduces the dying value at which you die by your doomed value",
}
_src(
    "dying",
    "Player Core, the Dying, Wounded and Doomed conditions and the recovery check. Verified "
    "against the Foundry VTT PF2e condition compendium (packs/pf2e/conditions/dying.json, "
    "wounded.json, doomed.json) and src/module/actor/creature/document.ts, where the maximum "
    "dying value is 4 and the recovery DC is 10 + the dying value.",
)


# --------------------------------------------------------------------------------------
# Bulk
# --------------------------------------------------------------------------------------


def bulk_tenths(spec: Any) -> int:
    """Bulk as tenths, so light items add up exactly. 'L' is 1 light = 1/10 Bulk.

    Source: Player Core, "Bulk" — 10 light items equal 1 Bulk; negligible-Bulk items
    ('-') do not count until the GM says a heap of them does.
    """
    if spec is None:
        return 0
    text = str(spec).strip().lower()
    if text in ("", "-", "0", "negligible", "none"):
        return 0
    if text in ("l", "light"):
        return 1
    m = re.fullmatch(r"(\d+)\s*l", text)
    if m:
        return int(m.group(1))
    try:
        return int(round(float(text) * 10))
    except ValueError:
        return 0


# --------------------------------------------------------------------------------------
# Calendar and time
# --------------------------------------------------------------------------------------

GOLARION_MONTHS: list[tuple[str, int]] = [
    ("Abadius", 31), ("Calistril", 28), ("Pharast", 31), ("Gozran", 30),
    ("Desnus", 31), ("Sarenith", 30), ("Erastus", 31), ("Arodus", 31),
    ("Rova", 30), ("Lamashan", 31), ("Neth", 30), ("Kuthona", 31),
]
GOLARION_WEEKDAYS = ["Moonday", "Toilday", "Wealday", "Oathday", "Fireday", "Starday", "Sunday"]
_src(
    "calendar",
    "Golarion's Absalom Reckoning calendar maps month for month onto the Gregorian calendar "
    "(Abadius = January and so on) and keeps its month lengths; the weekdays are Moonday "
    "through Sunday. Verified against " + FOUNDRY + ", the world clock's AR month and weekday "
    "tables in static/lang/en.json (PF2E.WorldClock.AR) and src/module/apps/world-clock/app.ts. "
    "Leap years are not modelled; see DESIGN_NOTES.md.",
)

GENERIC_MONTHS: list[tuple[str, int]] = [(f"Month {i}", 30) for i in range(1, 13)]
GENERIC_WEEKDAYS = [f"Day {i}" for i in range(1, 8)]

CALENDARS = {
    "golarion": {"months": GOLARION_MONTHS, "weekdays": GOLARION_WEEKDAYS, "era": "AR"},
    "generic": {"months": GENERIC_MONTHS, "weekdays": GENERIC_WEEKDAYS, "era": ""},
}


def blank_time(calendar: str = "golarion", year: int = 4725, month: int = 1, day: int = 1, minute: int = 8 * 60) -> dict[str, Any]:
    return {
        "calendar": calendar,
        "year": year,
        "month": month,
        "day": day,
        "minute_of_day": minute,
        "elapsed_minutes": 0,
    }


def _cal(t: dict[str, Any]) -> dict[str, Any]:
    return CALENDARS.get(t.get("calendar", "golarion"), CALENDARS["golarion"])


def format_time(t: dict[str, Any] | None) -> str:
    if not t:
        return "unset"
    cal = _cal(t)
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
    cal = _cal(t)
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
_UNIT_MINUTES = {
    "round": 1 / 6,  # a round is 6 seconds
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
# Travel
# --------------------------------------------------------------------------------------

TRAVEL_HOURS_PER_DAY = 8
TRAVEL_SPEEDS = [
    {"speed": 10, "feet_per_minute": 100, "miles_per_hour": 1.0, "miles_per_day": 8},
    {"speed": 15, "feet_per_minute": 150, "miles_per_hour": 1.5, "miles_per_day": 12},
    {"speed": 20, "feet_per_minute": 200, "miles_per_hour": 2.0, "miles_per_day": 16},
    {"speed": 25, "feet_per_minute": 250, "miles_per_hour": 2.5, "miles_per_day": 20},
    {"speed": 30, "feet_per_minute": 300, "miles_per_hour": 3.0, "miles_per_day": 24},
    {"speed": 35, "feet_per_minute": 350, "miles_per_hour": 3.5, "miles_per_day": 28},
    {"speed": 40, "feet_per_minute": 400, "miles_per_hour": 4.0, "miles_per_day": 32},
]
_src(
    "travel_speed",
    "GM Core, Travel Speed. The 8-hour travel day is verified against " + FOUNDRY
    + ", src/scripts/macros/travel/travel-speed.ts (`hoursPerDay = 8`), and feet per minute is "
    "Speed x 10. The miles-per-hour and miles-per-day columns are UNVERIFIED: they are derived "
    "from Speed / 10 miles per hour x 8 hours, which reproduces the familiar published rows, "
    "but the published table itself could not be checked from this machine.",
    verified=False,
)


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------


def _print_table(rows: Sequence[dict[str, Any]], cols: Sequence[str]) -> None:
    widths = {c: max(len(c), *(len(str(r.get(c, ""))) for r in rows)) for c in cols}
    print(" | ".join(c.ljust(widths[c]) for c in cols))
    print("-|-".join("-" * widths[c] for c in cols))
    for r in rows:
        print(" | ".join(str(r.get(c, "")).ljust(widths[c]) for c in cols))


def cmd_encounter(args: argparse.Namespace) -> int:
    budgets = encounter_budgets(args.party_size)
    spent = 0
    lines: list[str] = []
    for spec in args.add or []:
        m = re.fullmatch(r"\s*(.+?)\s*:\s*(-?\d+)\s*(?:x\s*(\d+))?\s*", spec)
        if not m:
            print(f"pf2e.py: cannot read --add {spec!r} (want 'name:level' or 'name:level x3')", file=sys.stderr)
            return 2
        name, lvl, count = m.group(1), int(m.group(2)), int(m.group(3) or 1)
        each = creature_xp(args.party_level, lvl, pwol=args.pwol)
        spent += each * count
        lines.append(f"  {name} (level {lvl}) x{count}: {each} XP each = {each * count}")
    for spec in args.hazard or []:
        m = re.fullmatch(r"\s*(.+?)\s*:\s*(-?\d+)\s*(complex)?\s*", spec)
        if not m:
            print(f"pf2e.py: cannot read --hazard {spec!r} (want 'name:level' or 'name:level complex')", file=sys.stderr)
            return 2
        name, lvl, cx = m.group(1), int(m.group(2)), bool(m.group(3))
        each = hazard_xp(args.party_level, lvl, complex_hazard=cx, pwol=args.pwol)
        spent += each
        lines.append(f"  {name} ({'complex' if cx else 'simple'} hazard, level {lvl}): {each} XP")

    print(f"Party level {args.party_level}, party size {args.party_size}"
          + ("  [proficiency without level]" if args.pwol else ""))
    print()
    print("XP budget by threat level:")
    for k in ("trivial", "low", "moderate", "severe", "extreme"):
        mark = "  <-- requested" if args.threat == k else ""
        print(f"  {k:<9} {budgets[k]:>5} XP{mark}")
    print(f"\nSource: {SOURCES['encounter_budgets']}\n")
    if lines:
        print("Spent:")
        for l in lines:
            print(l)
        rating = rate_encounter(spent, args.party_size)
        print(f"\n  total {spent} XP → threat rating: {rating.upper()}")
        if args.threat:
            room = budgets[args.threat] - spent
            print(f"  {room:+d} XP against the requested {args.threat} budget of {budgets[args.threat]}")
        print(f"\nSource: {SOURCES['creature_xp']}")
        print(f"Source: {SOURCES['hazard_xp']}")
    elif args.threat:
        print(f"Build to {budgets[args.threat]} XP for a {args.threat} encounter.")
    if args.party_size < 4:
        print(
            f"\nSolo/small-party warning: the budget already scales to {args.party_size} character(s), "
            "but the action economy does not. Several weak creatures are far deadlier at this party "
            "size than the XP says — see system/03-difficulty-and-solo-levers.md before spending the "
            "budget on a crowd."
        )
    return 0


def cmd_treasure(args: argparse.Namespace) -> int:
    t = treasure_for(args.level, args.party_size)
    print(f"Treasure for one level of play at level {t['level']}, party size {t['party_size']}:")
    print(f"  total                {t['total_gp']} gp   (the published four-character row is {t['total_gp_for_four']} gp)")
    print(f"  per character        {t['per_character_gp']} gp")
    print(f"  permanent items      {t['permanent_gp']} gp   (~50%)")
    print(f"  consumables          {t['consumable_gp']} gp   (~25%)")
    print(f"  currency and valuables {t['currency_gp']} gp (~25%)")
    print()
    print("Suggested permanent-item levels to shop from: "
          + ", ".join(str(x) for x in range(max(1, args.level - 1), args.level + 3)))
    print()
    print("⚠ UNVERIFIED — " + SOURCES["treasure_by_level"])
    print("⚠ UNVERIFIED — " + SOURCES["treasure_mix"])
    return 0


def cmd_dc(args: argparse.Namespace) -> int:
    if args.rank:
        dc = simple_dc(args.rank, rarity=args.rarity, pwol=args.pwol)
        print(f"Simple DC, {args.rank}, {args.rarity}: {dc}")
        print(f"Source: {SOURCES['simple_dcs']}")
        print(f"Source: {SOURCES['dc_adjustments']}")
        return 0
    if args.level is None:
        print("pf2e.py dc: pass --level N or --rank trained", file=sys.stderr)
        return 2
    dc = level_dc(args.level, rarity=args.rarity, pwol=args.pwol)
    print(f"Level-based DC, level {args.level}, {args.rarity}: {dc}")
    for name, adj in DC_ADJUSTMENTS.items():
        print(f"  {name:<17} {dc + adj}")
    print(f"Source: {SOURCES['level_dcs']}")
    print(f"Source: {SOURCES['dc_adjustments']}")
    return 0


def cmd_tables(args: argparse.Namespace) -> int:
    which = args.which
    if which == "level-dcs":
        _print_table([{"level": k, "DC": v} for k, v in sorted(LEVEL_DCS.items())], ["level", "DC"])
        print(f"\nSource: {SOURCES['level_dcs']}")
    elif which == "simple-dcs":
        _print_table(
            [{"proficiency": k, "DC": v, "DC (PWoL)": SIMPLE_DCS_PWOL[k]} for k, v in SIMPLE_DCS.items()],
            ["proficiency", "DC", "DC (PWoL)"],
        )
        print(f"\nSource: {SOURCES['simple_dcs']}")
    elif which == "creature-xp":
        _print_table(
            [{"relative level": k, "XP": v} for k, v in sorted(CREATURE_XP_BY_RELATIVE_LEVEL.items())],
            ["relative level", "XP"],
        )
        print(f"\nSource: {SOURCES['creature_xp']}")
    elif which == "hazard-xp":
        _print_table([{"relative level": k, "simple hazard XP": v} for k, v in sorted(SIMPLE_HAZARD_XP.items())],
                     ["relative level", "simple hazard XP"])
        print(f"\nSource: {SOURCES['hazard_xp']}")
    elif which == "item-bonuses":
        _print_table(ITEM_BONUS_BY_LEVEL, ["level", "attack", "striking_dice", "ac", "perception", "saves"])
        print(f"\nSource: {SOURCES['item_bonus_by_level']}")
    elif which == "treasure":
        _print_table([{"level": k, "gp (party of 4)": v} for k, v in sorted(TREASURE_BY_LEVEL.items())],
                     ["level", "gp (party of 4)"])
        print(f"\n⚠ UNVERIFIED — {SOURCES['treasure_by_level']}")
    elif which == "earn-income":
        _print_table(
            [dict(level=k, **v) for k, v in sorted(EARN_INCOME.items())],
            ["level", "failure", "trained", "expert", "master", "legendary"],
        )
        print(f"\nSource: {SOURCES['earn_income']}")
    elif which == "travel":
        _print_table(TRAVEL_SPEEDS, ["speed", "feet_per_minute", "miles_per_hour", "miles_per_day"])
        print(f"\n⚠ PARTLY UNVERIFIED — {SOURCES['travel_speed']}")
    elif which == "budgets":
        rows = [dict(party_size=n, **encounter_budgets(n)) for n in range(1, 7)]
        _print_table(rows, ["party_size", "trivial", "low", "moderate", "severe", "extreme"])
        print(f"\nSource: {SOURCES['encounter_budgets']}")
    return 0


def cmd_sources(args: argparse.Namespace) -> int:
    print("Provenance of every table in tools/pf2e.py\n")
    for key in sorted(SOURCES):
        mark = "⚠ UNVERIFIED" if key in UNVERIFIED_TABLES else "verified"
        print(f"[{mark}] {key}\n    {SOURCES[key]}\n")
    print(f"{len(UNVERIFIED_TABLES)} of {len(SOURCES)} tables are unverified: "
          + ", ".join(sorted(UNVERIFIED_TABLES)))
    print("\nThese are listed in DESIGN_NOTES.md under 'To verify before first play'.")
    return 0


def cmd_time(args: argparse.Namespace) -> int:
    t = blank_time(args.calendar, args.year, args.month, args.day)
    if args.advance:
        minutes, label = parse_interval(args.advance)
        print(f"{format_time(t)}  + {label} ({minutes} min)")
        t = advance_time(t, minutes)
    print(format_time(t))
    print(f"Source: {SOURCES['calendar']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="pf2e.py", description="PF2e rules tables and the helpers over them.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("encounter", help="XP budget, what a creature list costs, and the resulting threat")
    p.add_argument("--party-level", type=int, required=True)
    p.add_argument("--party-size", type=int, default=1)
    p.add_argument("--threat", choices=["trivial", "low", "moderate", "severe", "extreme"], default=None)
    p.add_argument("--add", action="append", default=[], help="'ghoul:2' or 'ghoul:2 x3'")
    p.add_argument("--hazard", action="append", default=[], help="'spiked pit:1' or 'rune trap:3 complex'")
    p.add_argument("--pwol", action="store_true", help="proficiency without level variant")

    p = sub.add_parser("treasure", help="the treasure a level of play should hand out")
    p.add_argument("--level", type=int, required=True)
    p.add_argument("--party-size", type=int, default=1)

    p = sub.add_parser("dc", help="a level-based or simple DC with its adjustments")
    p.add_argument("--level", type=int, default=None)
    p.add_argument("--rank", default=None, choices=["untrained", "trained", "expert", "master", "legendary"])
    p.add_argument("--rarity", default="common", choices=list(RARITY_ADJUSTMENTS))
    p.add_argument("--pwol", action="store_true")

    p = sub.add_parser("tables", help="print one table with its source line")
    p.add_argument(
        "which",
        choices=["level-dcs", "simple-dcs", "creature-xp", "hazard-xp", "item-bonuses",
                 "treasure", "earn-income", "travel", "budgets"],
    )

    sub.add_parser("sources", help="print the provenance of every table, verified or not")

    p = sub.add_parser("time", help="format and advance an in-world date")
    p.add_argument("--calendar", default="golarion", choices=list(CALENDARS))
    p.add_argument("--year", type=int, default=4725)
    p.add_argument("--month", type=int, default=1)
    p.add_argument("--day", type=int, default=1)
    p.add_argument("--advance", default=None, help="e.g. '3 days 4 hours'")
    return ap


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return {
            "encounter": cmd_encounter,
            "treasure": cmd_treasure,
            "dc": cmd_dc,
            "tables": cmd_tables,
            "sources": cmd_sources,
            "time": cmd_time,
        }[args.cmd](args)
    except ValueError as exc:
        print(f"pf2e.py: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
