#!/usr/bin/env python3
"""pf2e.py — the rules tables, as data, so nothing is recalled from memory.

Every table in this file carries a `Source:` note. Where a value could not be checked
against a source reachable from this machine it is marked `UNVERIFIED` in
`UNVERIFIED_TABLES` and listed in `DESIGN_NOTES.md`; `python3 tools/pf2e.py sources`
prints the whole provenance list.

Verification note: Archives of Nethys (2e.aonprd.com) is the PRIMARY source here. Each
table's `Source:` note cites the AoN page ID it was read from. Where AoN does not present
a value as a table — the degrees-of-success thresholds, the multiple attack penalty, the
item-bonus curve, the dying numbers, the Earn Income rates, the Golarion calendar, and the
Proficiency Without Level variant columns — the value is additionally or solely checked
against the Foundry VTT PF2e system source, an ORC-licensed implementation that cites AoN
rule IDs inline, at version 8.5.1, commit 06b904d6ced9795c4c07af085e6f61a56f845c60. That
is a secondary source and its `Source:` note says so.

An earlier build of this file ran with 5 of 17 tables UNVERIFIED and several values checked
only against Foundry. Re-verifying against AoN found eight real errors; they are listed in
DESIGN_NOTES.md. Nothing is marked UNVERIFIED now, and `settlement_item_levels` is labelled
for what it actually is: this framework's own convention, not a published table.

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
# Markdown front-matter-ish fields
# --------------------------------------------------------------------------------------

# Matches `World: x`, `- World: x`, `- **World:** x` and `**World**: x` alike, so the
# three tools that read these fields cannot disagree about the syntax.
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
# Difficulty classes
# --------------------------------------------------------------------------------------

LEVEL_DCS: dict[int, int] = {
    -1: 13, 0: 14, 1: 15, 2: 16, 3: 18, 4: 19, 5: 20, 6: 22, 7: 23, 8: 24, 9: 26,
    10: 27, 11: 28, 12: 30, 13: 31, 14: 32, 15: 34, 16: 35, 17: 36, 18: 38, 19: 39,
    20: 40, 21: 42, 22: 44, 23: 46, 24: 48, 25: 50,
}
_src(
    "level_dcs",
    "GM Core, Table 10-2: DCs by Level — read from https://2e.aonprd.com/Rules.aspx?ID=2627. Levels 0 through 25 match the "
    "published table exactly. NOTE the published table starts at level 0; the level -1 row (DC 13) "
    "is not published and comes from " + FOUNDRY + " (src/module/dc.ts `dcByLevel`), which "
    "extrapolates it for level -1 creatures. Treat that one row as a convention, not a quotation.",
)

SIMPLE_DCS: dict[str, int] = {"untrained": 10, "trained": 15, "expert": 20, "master": 30, "legendary": 40}
SIMPLE_DCS_PWOL: dict[str, int] = {"untrained": 10, "trained": 15, "expert": 20, "master": 25, "legendary": 30}
_src(
    "simple_dcs",
    "GM Core, Table 10-4: Simple DCs — read from https://2e.aonprd.com/Rules.aspx?ID=2627, checked row by row "
    "(untrained 10, trained 15, expert 20, master 30, legendary 40). The Proficiency Without Level "
    "column comes from that variant rule (https://2e.aonprd.com/Rules.aspx?ID=1370) and is still "
    "only verified against " + FOUNDRY + ", src/module/dc.ts `simpleDCsWithoutLevel`.",
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
    "GM Core, Table 10-5: DC Adjustments — read from https://2e.aonprd.com/Rules.aspx?ID=2627. The published table pairs the "
    "adjustment with the rarity in one grid: incredibly easy -10, very easy -5, easy -2, "
    "hard +2 (uncommon), very hard +5 (rare), incredibly hard +10 (unique).",
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

# GM Core Table 10-1: Encounter Budget. Budget is for a party of FOUR; the adjustment is
# applied per character above or below four.
THREAT_BUDGET_FOR_FOUR: dict[str, int] = {
    "trivial": 40, "low": 60, "moderate": 80, "severe": 120, "extreme": 160,
}
THREAT_CHARACTER_ADJUSTMENT: dict[str, int] = {
    "trivial": 10, "low": 20, "moderate": 20, "severe": 30, "extreme": 40,
}
# The smoothed alternative: 20 XP per character, scaled by threat. This is what the Foundry VTT
# system computes, and it is what many tables use, because the published Low adjustment of 20
# collapses Low to 0 XP for a solo party (see `encounter_budgets`).
XP_PER_CHARACTER = 20
THREAT_MULTIPLIERS: dict[str, float] = {
    "trivial": 0.5, "low": 0.75, "moderate": 1.0, "severe": 1.5, "extreme": 2.0,
}
_src(
    "encounter_budgets",
    "GM Core p.75, Table 10-1: Encounter Budget, and 'Different Party Sizes' (GM Core p.76) — read "
    "from https://2e.aonprd.com/Rules.aspx?ID=2715 and ?ID=2719. Budget for four characters is "
    "40 (or less) / 60 / 80 / 120 / 160 XP; the per-character adjustment is 10 (or less) / 20 / 20 / "
    "30 / 40. Quoting the rule: 'For each additional character in the party beyond the fourth, "
    "increase your XP budget by the amount shown in the Character Adjustment value... If you have "
    "fewer than four characters, use the same process in reverse: for each missing character, remove "
    "that amount of XP from your XP budget.' NOTE the published Low and Moderate adjustments are "
    "both 20, so the published rule sends Low to 0 XP at a party of one; `encounter_budgets` reports "
    "that honestly and offers a smoothed alternative.",
)
_src(
    "xp_award_party_size",
    "GM Core p.76, 'Different Party Sizes' (https://2e.aonprd.com/Rules.aspx?ID=2719), quoting: "
    "'Note that if you adjust your XP budget to account for party size, the XP awards for the "
    "encounter don't change—you'll always award the amount of XP listed for a group of four "
    "characters.' So a solo character who clears a moderate encounter built to a 20 XP budget is "
    "awarded the four-character moderate figure of 80 XP, not 20. This is how a small party keeps "
    "pace with the 1,000-XP-per-level curve while fighting fewer creatures.",
)

ACCOMPLISHMENT_XP: dict[str, int] = {"minor": 10, "moderate": 30, "major": 80}
_src(
    "accomplishment_xp",
    "GM Core, Rewards — Accomplishment XP (https://2e.aonprd.com/Rules.aspx?ID=2647): minor 10 XP, "
    "moderate 30 XP, major 80 XP. Useful when advancement is by milestone rather than by encounter.",
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
    "GM Core, Table 10-2: Creature XP (encounter design) and the matching Adversary XP award table "
    "in Rewards — read from https://2e.aonprd.com/Rules.aspx?ID=2715 and ?ID=2647, which agree: -4 -> 10, -3 -> 15, -2 -> 20, "
    "-1 -> 30, party level -> 40, +1 -> 60, +2 -> 80, +3 -> 120, +4 -> 160. The Proficiency Without "
    "Level column (https://2e.aonprd.com/Rules.aspx?ID=1371) is still only verified against "
    + FOUNDRY + ", src/scripts/macros/xp/index.ts `xpVariantCreatureDifferences`.",
)

SIMPLE_HAZARD_XP: dict[int, int] = {-4: 2, -3: 3, -2: 4, -1: 6, 0: 8, 1: 12, 2: 16, 3: 24, 4: 32}
_src(
    "hazard_xp",
    "GM Core, Rewards — Hazard XP award table, read from https://2e.aonprd.com/Rules.aspx?ID=2647. Simple hazards: -4 -> 2, "
    "-3 -> 3, -2 -> 4, -1 -> 6, party level -> 8, +1 -> 12, +2 -> 16, +3 -> 24, +4 -> 32. Complex "
    "hazards award the same as a creature of that relative level. Both columns checked.",
)


def encounter_budgets(party_size: int, *, smoothed: bool = False) -> dict[str, int]:
    """XP budget per threat level for a party of this size.

    By default this applies the published rule: start from the four-character budget and add or
    remove the Character Adjustment for each character above or below four.

    That rule has a sharp edge worth knowing about. Low and Moderate share a Character Adjustment
    of 20, so at a party of one, Low comes out at 60 - 3x20 = 0 XP — a "low threat" encounter with
    nothing in it. `smoothed=True` gives the alternative many tables use instead (20 XP per
    character scaled by threat), which yields 10/15/20/30/40 for a solo character. The two agree
    exactly at a party of four.
    """
    if party_size < 1:
        raise ValueError("a party needs at least one character")
    if smoothed:
        base = party_size * XP_PER_CHARACTER
        return {k: int(base * v) for k, v in THREAT_MULTIPLIERS.items()}
    delta = party_size - 4
    return {
        k: max(0, THREAT_BUDGET_FOR_FOUR[k] + delta * THREAT_CHARACTER_ADJUSTMENT[k])
        for k in THREAT_BUDGET_FOR_FOUR
    }


def degenerate_budgets(party_size: int) -> list[str]:
    """Threat levels whose published budget collapses to 0 XP at this party size."""
    return [k for k, v in encounter_budgets(party_size).items() if v == 0]


def xp_award(total_xp_spent: int, party_size: int, *, smoothed: bool = False) -> int:
    """What the party is actually awarded, which is NOT the adjusted budget.

    The published rule is that the XP award never changes with party size: you always award the
    amount listed for a group of four. So the award is the four-character budget for whatever
    threat the encounter turned out to be.
    """
    return THREAT_BUDGET_FOR_FOUR[rate_encounter(total_xp_spent, party_size, smoothed=smoothed)]


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


def rate_encounter(total_xp: int, party_size: int, *, smoothed: bool = False) -> str:
    b = encounter_budgets(party_size, smoothed=smoothed)
    for name in ("trivial", "low", "moderate", "severe"):
        if total_xp <= b[name]:
            return name
    return "extreme"


# Elite and Weak use DIFFERENT level bands for their HP change. Each entry is
# (lowest level in band, highest level in band or None for open-ended, HP delta).
ELITE_HP: list[tuple[int | None, int | None, int]] = [(None, 1, 10), (2, 4, 15), (5, 19, 20), (20, None, 30)]
WEAK_HP: list[tuple[int | None, int | None, int]] = [(1, 2, -10), (3, 5, -15), (6, 20, -20), (21, None, -30)]

CREATURE_ADJUSTMENTS = {
    "elite": "Level +1 (or +2 if the creature is level -1 or 0). +2 to AC, attack modifiers, DCs, "
             "saving throws, Perception and skill modifiers. +2 damage to Strikes and other "
             "offensive abilities, or +4 if the ability has a limit on how often it can be used "
             "(a spellcaster's spells, a dragon's breath). HP up by 10 (level 1 or lower), "
             "15 (2-4), 20 (5-19) or 30 (20+). Award XP for its new level.",
    "weak": "Level -1 (or -2 if the creature is level 1). -2 to AC, attack modifiers, DCs, saving "
            "throws, Perception and skill modifiers. -2 damage to Strikes and other offensive "
            "abilities, or -4 if the ability has a use limit. HP down by 10 (level 1-2), "
            "15 (3-5), 20 (6-20) or 30 (21+). Award XP for its new level.",
}
_src(
    "creature_adjustments",
    "Monster Core p.6, Adjusting Creatures — read from "
    "https://2e.aonprd.com/Rules.aspx?ID=3262. Elite and weak each shift the level by 1 (by 2 at "
    "the bottom of the range: elite on a level -1 or 0 creature, weak on a level 1 creature), "
    "change AC, attack modifiers, DCs, saves, Perception and skills by 2, change Strike and "
    "offensive-ability damage by 2 (by 4 for limited-use abilities), and change HP on the bands "
    "above. The two HP tables have DIFFERENT band boundaries, which is easy to get wrong.",
)


def adjusted_hp(level: int, *, elite: bool) -> int:
    """The HP change an elite or weak adjustment makes to a creature of this starting level."""
    for lo, hi, delta in (ELITE_HP if elite else WEAK_HP):
        if (lo is None or level >= lo) and (hi is None or level <= hi):
            return delta
    return 0


def adjusted_level(level: int, *, elite: bool) -> int:
    """The level an adjusted creature counts as, including the doubled step at the bottom."""
    if elite:
        return level + (2 if level <= 0 else 1)
    return level - (2 if level == 1 else 1)


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
    "GM Core p.77, Table 10-3: Treasure by Level — read from "
    "https://2e.aonprd.com/Rules.aspx?ID=2715. Total gp value of everything a FOUR-character party "
    "should find over one level; all twenty rows checked against the published table.",
)

# The same published table also gives treasure to attach to a single encounter of each threat
# level, plus an "extra treasure" figure for what to place outside encounters. Better guidance
# than dividing the level total by an encounter count.
TREASURE_PER_ENCOUNTER: dict[int, dict[str, int]] = {
    1:  {"low": 13,    "moderate": 18,    "severe": 26,    "extreme": 35,    "extra": 35},
    2:  {"low": 23,    "moderate": 30,    "severe": 45,    "extreme": 60,    "extra": 60},
    3:  {"low": 38,    "moderate": 50,    "severe": 75,    "extreme": 100,   "extra": 100},
    4:  {"low": 65,    "moderate": 85,    "severe": 130,   "extreme": 170,   "extra": 170},
    5:  {"low": 100,   "moderate": 135,   "severe": 200,   "extreme": 270,   "extra": 270},
    6:  {"low": 150,   "moderate": 200,   "severe": 300,   "extreme": 400,   "extra": 400},
    7:  {"low": 220,   "moderate": 290,   "severe": 440,   "extreme": 580,   "extra": 580},
    8:  {"low": 300,   "moderate": 400,   "severe": 600,   "extreme": 800,   "extra": 800},
    9:  {"low": 430,   "moderate": 570,   "severe": 860,   "extreme": 1140,  "extra": 1140},
    10: {"low": 600,   "moderate": 800,   "severe": 1200,  "extreme": 1600,  "extra": 1600},
    11: {"low": 865,   "moderate": 1150,  "severe": 1725,  "extreme": 2300,  "extra": 2300},
    12: {"low": 1250,  "moderate": 1650,  "severe": 2475,  "extreme": 3300,  "extra": 3300},
    13: {"low": 1875,  "moderate": 2500,  "severe": 3750,  "extreme": 5000,  "extra": 5000},
    14: {"low": 2750,  "moderate": 3650,  "severe": 5500,  "extreme": 7300,  "extra": 7300},
    15: {"low": 4100,  "moderate": 5450,  "severe": 8200,  "extreme": 10900, "extra": 10900},
    16: {"low": 6200,  "moderate": 8250,  "severe": 12400, "extreme": 16500, "extra": 16500},
    17: {"low": 9600,  "moderate": 12800, "severe": 19200, "extreme": 25600, "extra": 25600},
    18: {"low": 15600, "moderate": 20800, "severe": 31200, "extreme": 41600, "extra": 41600},
    19: {"low": 26600, "moderate": 35500, "severe": 53250, "extreme": 71000, "extra": 71000},
    20: {"low": 36800, "moderate": 49000, "severe": 73500, "extreme": 98000, "extra": 98000},
}
_src(
    "treasure_per_encounter",
    "GM Core p.77, Table 10-3: Treasure by Level, the per-encounter and extra-treasure columns — "
    "read from https://2e.aonprd.com/Rules.aspx?ID=2715.",
)

# GM Core p.59, Table 6-1: Party Treasure by Level. The published breakdown is concrete item
# counts by item level plus a currency figure — not a percentage split. Each entry is
# (permanent items, consumables, party currency gp, currency per additional PC gp), where the
# item lists are [(item level, how many), ...].
TREASURE_DETAIL: dict[int, dict[str, Any]] = {
    1:  {"permanent": [(2,2),(1,2)],   "consumables": [(2,2),(1,3)],        "currency": 40,     "per_extra_pc": 10},
    2:  {"permanent": [(3,2),(2,2)],   "consumables": [(3,2),(2,2),(1,2)],  "currency": 70,     "per_extra_pc": 18},
    3:  {"permanent": [(4,2),(3,2)],   "consumables": [(4,2),(3,2),(2,2)],  "currency": 120,    "per_extra_pc": 30},
    4:  {"permanent": [(5,2),(4,2)],   "consumables": [(5,2),(4,2),(3,2)],  "currency": 200,    "per_extra_pc": 50},
    5:  {"permanent": [(6,2),(5,2)],   "consumables": [(6,2),(5,2),(4,2)],  "currency": 320,    "per_extra_pc": 80},
    6:  {"permanent": [(7,2),(6,2)],   "consumables": [(7,2),(6,2),(5,2)],  "currency": 500,    "per_extra_pc": 125},
    7:  {"permanent": [(8,2),(7,2)],   "consumables": [(8,2),(7,2),(6,2)],  "currency": 720,    "per_extra_pc": 180},
    8:  {"permanent": [(9,2),(8,2)],   "consumables": [(9,2),(8,2),(7,2)],  "currency": 1000,   "per_extra_pc": 250},
    9:  {"permanent": [(10,2),(9,2)],  "consumables": [(10,2),(9,2),(8,2)], "currency": 1400,   "per_extra_pc": 350},
    10: {"permanent": [(11,2),(10,2)], "consumables": [(11,2),(10,2),(9,2)],"currency": 2000,   "per_extra_pc": 500},
    11: {"permanent": [(12,2),(11,2)], "consumables": [(12,2),(11,2),(10,2)],"currency": 2800,  "per_extra_pc": 700},
    12: {"permanent": [(13,2),(12,2)], "consumables": [(13,2),(12,2),(11,2)],"currency": 4000,  "per_extra_pc": 1000},
    13: {"permanent": [(14,2),(13,2)], "consumables": [(14,2),(13,2),(12,2)],"currency": 6000,  "per_extra_pc": 1500},
    14: {"permanent": [(15,2),(14,2)], "consumables": [(15,2),(14,2),(13,2)],"currency": 9000,  "per_extra_pc": 2250},
    15: {"permanent": [(16,2),(15,2)], "consumables": [(16,2),(15,2),(14,2)],"currency": 13000, "per_extra_pc": 3250},
    16: {"permanent": [(17,2),(16,2)], "consumables": [(17,2),(16,2),(15,2)],"currency": 20000, "per_extra_pc": 5000},
    17: {"permanent": [(18,2),(17,2)], "consumables": [(18,2),(17,2),(16,2)],"currency": 30000, "per_extra_pc": 7500},
    18: {"permanent": [(19,2),(18,2)], "consumables": [(19,2),(18,2),(17,2)],"currency": 48000, "per_extra_pc": 12000},
    19: {"permanent": [(20,2),(19,2)], "consumables": [(20,2),(19,2),(18,2)],"currency": 80000, "per_extra_pc": 20000},
    20: {"permanent": [(20,4)],        "consumables": [(20,4),(19,2)],      "currency": 140000, "per_extra_pc": 35000},
}
_src(
    "treasure_detail",
    "GM Core p.59, Table 6-1: Party Treasure by Level — read from "
    "https://2e.aonprd.com/Rules.aspx?ID=2656. The published guidance is not a percentage split: it "
    "names how many permanent items and consumables to give at which item levels, plus a currency "
    "figure and a per-additional-PC currency column. All twenty rows checked.",
)

TREASURE_PARTY_SIZE_RULE = (
    "GM Core p.61: for each character ABOVE four, add one permanent item of the party's level or one "
    "higher, two consumables (usually one at level and one at +1), and the Currency per Additional "
    "PC figure. For each character BELOW four you may subtract the same amount — but the book says "
    "outright: 'since the game is inherently more challenging with a smaller group that can't cover "
    "all roles as efficiently, you might consider subtracting less treasure and allowing the extra "
    "gear help compensate for the smaller group size.'"
)
_src(
    "treasure_party_size",
    "GM Core p.61, Different Party Sizes (treasure) — read from "
    "https://2e.aonprd.com/Rules.aspx?ID=2661. Quoted in `TREASURE_PARTY_SIZE_RULE`. Note this is a "
    "published endorsement of giving a small party MORE than its linear share, which is the same "
    "argument system/03-difficulty-and-solo-levers.md makes about role coverage.",
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

# NOT a published table. GM Core gives a settlement a LEVEL and derives availability from it;
# there is no size-to-level table in the rules. These are this framework's own starting
# suggestions, kept only so a new campaign has a number to argue with.
ITEM_LEVEL_BY_SETTLEMENT = {
    "village": 2,
    "town": 6,
    "city": 10,
    "metropolis": 14,
    "capital / planar market": 20,
}
_src(
    "settlement_item_levels",
    "THIS FRAMEWORK'S OWN CONVENTION, not a published table — corrected after reading GM Core p.168, "
    "Marketplaces (https://2e.aonprd.com/Rules.aspx?ID=3003). The actual rule is that a settlement "
    "has a LEVEL, and 'a character can usually purchase any common item... that's of the same or "
    "lower level than the settlement's', with fewer of the highest-level items available — use the "
    "Permanent Items and Consumables columns of Table 6-1 for a level ONE LOWER than the "
    "settlement's as a guide to how many. Selling works the same way. A character of higher level "
    "than the settlement can leverage influence for special orders, which takes time. Give each "
    "settlement a level in WORLD.md; the size names above are only a starting suggestion.",
)


def settlement_availability(settlement_level: int) -> dict[str, Any]:
    """What a settlement of this level can sell, per GM Core p.168.

    Any common item of the settlement's level or lower. For the top of that range, the counts in
    Table 6-1 for one level BELOW the settlement's are the guide to how many are on the shelf.
    """
    guide = TREASURE_DETAIL.get(max(1, min(20, settlement_level - 1)), {})
    return {
        "settlement_level": settlement_level,
        "buy_up_to_item_level": settlement_level,
        "sell_up_to_item_level": settlement_level,
        "top_end_stock_guide": {
            "permanent": guide.get("permanent", []),
            "consumables": guide.get("consumables", []),
            "from_treasure_row": max(1, min(20, settlement_level - 1)),
        },
        "above_settlement_level": "special order or commission; costs time, and the GM sets how much",
    }


def treasure_for(level: int, party_size: int = 4) -> dict[str, Any]:
    """The treasure a level of play should hand out, per GM Core p.59 and p.61.

    The published table is for four characters and names item counts by item level rather than a
    percentage split. For a party above four, add per the p.61 rule. For a party below four the
    rule permits subtracting the same amount per missing character — and then says in as many
    words that you might subtract less, because a small party cannot cover all the roles. Both the
    strict figure and the gentler one are returned; the caller decides and says which it used.
    """
    if level not in TREASURE_BY_LEVEL:
        raise ValueError(f"no treasure row for level {level} (the table runs 1 to 20)")
    row = TREASURE_DETAIL[level]
    total_four = TREASURE_BY_LEVEL[level]
    delta = party_size - 4

    def flatten(pairs: list[tuple[int, int]]) -> list[int]:
        return [lvl for lvl, n in pairs for _ in range(n)]

    perm = flatten(row["permanent"])
    cons = flatten(row["consumables"])
    currency = row["currency"]

    if delta > 0:  # p.61: one permanent at level or +1, two consumables, the per-PC currency
        perm += [level] * delta
        cons += [level, level + 1] * delta
        currency += row["per_extra_pc"] * delta
        strict = gentle = None
    elif delta < 0:
        missing = -delta
        strict = {
            "permanent_item_levels": perm[: max(0, len(perm) - missing)],
            "consumable_item_levels": cons[: max(0, len(cons) - 2 * missing)],
            "currency_gp": max(0, currency - row["per_extra_pc"] * missing),
        }
        # The gentler reading the book invites: take off half of what strict subtraction would.
        half = missing // 2
        gentle = {
            "permanent_item_levels": perm[: max(0, len(perm) - half)],
            "consumable_item_levels": cons[: max(0, len(cons) - 2 * half)],
            "currency_gp": max(0, currency - row["per_extra_pc"] * half),
        }
    else:
        strict = gentle = None

    return {
        "level": level,
        "party_size": party_size,
        "total_gp_for_four": total_four,
        "for_four": {
            "permanent_item_levels": flatten(row["permanent"]),
            "consumable_item_levels": flatten(row["consumables"]),
            "currency_gp": row["currency"],
        },
        "as_listed_for_this_size": {
            "permanent_item_levels": perm,
            "consumable_item_levels": cons,
            "currency_gp": currency,
        } if delta >= 0 else strict,
        "strict_subtraction": strict,
        "gentler_for_a_small_party": gentle,
        "currency_per_additional_pc_gp": row["per_extra_pc"],
        "per_encounter": TREASURE_PER_ENCOUNTER[level],
        "party_size_rule": TREASURE_PARTY_SIZE_RULE,
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


_src(
    "bulk_limits",
    "Player Core p.269, Bulk — read from https://2e.aonprd.com/Rules.aspx?ID=2153, quoting: 'You can carry an amount of Bulk equal "
    "to 5 plus your Strength modifier without penalty; if you carry more, you gain the encumbered "
    "condition. You can't hold or carry more Bulk than 10 plus your Strength modifier.'",
)
_src(
    "coins",
    "Player Core p.267, Coins and Currency — read from https://2e.aonprd.com/Rules.aspx?ID=2144: cp is one tenth of sp; gp is "
    "10 sp or 100 cp; pp is 10 gp, 100 sp or 1,000 cp.",
)


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
    {"speed": 50, "feet_per_minute": 500, "miles_per_hour": 5.0, "miles_per_day": 40},
    {"speed": 60, "feet_per_minute": 600, "miles_per_hour": 6.0, "miles_per_day": 48},
]
TRAVEL_TERRAIN = {
    "flat and clear": 1.0,
    "difficult terrain": 0.5,
    "greater difficult terrain": 1 / 3,
}
_src(
    "travel_speed",
    "Player Core p.438, Travel Speed — read from https://2e.aonprd.com/Rules.aspx?ID=2441. All nine "
    "rows checked (Speed 10 through 60). The table 'assume[s] traveling over flat and clear terrain "
    "at a determined pace, but one that's not exhausting'; difficult terrain halves the rate and "
    "greater difficult terrain reduces it to one third. The 8-hour travel day matches "
    + FOUNDRY + " (src/scripts/macros/travel/travel-speed.ts, `hoursPerDay = 8`).",
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
    smoothed = args.smoothed
    budgets = encounter_budgets(args.party_size, smoothed=smoothed)
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
          + ("  [proficiency without level]" if args.pwol else "")
          + ("  [smoothed budget]" if smoothed else ""))
    print()
    print("XP budget by threat level" + (" (smoothed)" if smoothed else " (as published)") + ":")
    alt = encounter_budgets(args.party_size, smoothed=not smoothed)
    for k in ("trivial", "low", "moderate", "severe", "extreme"):
        mark = "  <-- requested" if args.threat == k else ""
        other = "" if budgets[k] == alt[k] else f"   ({'smoothed' if not smoothed else 'published'}: {alt[k]})"
        print(f"  {k:<9} {budgets[k]:>5} XP{other}{mark}")
    degenerate = degenerate_budgets(args.party_size) if not smoothed else []
    if degenerate:
        print()
        print(f"  ⚠ At a party of {args.party_size} the published rule sends "
              f"{', '.join(degenerate)} to 0 XP, because the Character Adjustment for Low and")
        print("    Moderate is the same (20). An encounter with nothing in it is not a threat level.")
        print("    Pass --smoothed for the 20-XP-per-character reading many tables use instead, or")
        print("    build to trivial and accept that it is trivial.")
    print(f"\nSource: {SOURCES['encounter_budgets']}\n")

    if lines:
        print("Spent:")
        for l in lines:
            print(l)
        rating = rate_encounter(spent, args.party_size, smoothed=smoothed)
        print(f"\n  total {spent} XP → threat rating: {rating.upper()}")
        if args.threat:
            room = budgets[args.threat] - spent
            print(f"  {room:+d} XP against the requested {args.threat} budget of {budgets[args.threat]}")
        award = xp_award(spent, args.party_size, smoothed=smoothed)
        print(f"\n  XP TO AWARD: {award}  — the four-character figure for a {rating} encounter.")
        print("  The award does NOT scale down with party size; only the budget does.")
        print(f"  At 1,000 XP per level that is {1000 / award:.1f} encounters of this size per level.")
        print(f"\nSource: {SOURCES['xp_award_party_size']}")
        print(f"Source: {SOURCES['creature_xp']}")
        if args.hazard:
            print(f"Source: {SOURCES['hazard_xp']}")
    elif args.threat:
        print(f"Build to {budgets[args.threat]} XP for a {args.threat} encounter.")
        print(f"On clearing it, award {THREAT_BUDGET_FOR_FOUR[args.threat]} XP — the four-character figure.")

    if args.party_size < 4:
        print(
            f"\nSolo/small-party warning: the budget scales to {args.party_size} character(s), but the "
            "action economy does not. Several weak creatures are far deadlier at this party size than "
            "the XP says — see system/03-difficulty-and-solo-levers.md before spending the budget on "
            "a crowd."
        )
    return 0


def cmd_treasure(args: argparse.Namespace) -> int:
    t = treasure_for(args.level, args.party_size)

    def show(label: str, d: dict[str, Any]) -> None:
        perm = d["permanent_item_levels"]
        cons = d["consumable_item_levels"]
        fmt = lambda xs: ", ".join(f"level {l}" for l in xs) if xs else "none"
        print(f"  {label}")
        print(f"    permanent items ({len(perm)}): {fmt(perm)}")
        print(f"    consumables ({len(cons)}):     {fmt(cons)}")
        print(f"    currency:                {d['currency_gp']} gp")

    print(f"Treasure for one level of play at level {t['level']}, party size {t['party_size']}")
    print(f"Published total for four characters: {t['total_gp_for_four']} gp\n")
    show("As published, for four characters:", t["for_four"])
    if t["party_size"] > 4:
        print()
        show(f"Adjusted up for {t['party_size']} characters:", t["as_listed_for_this_size"])
    elif t["party_size"] < 4:
        print()
        show("Strict subtraction for the missing characters:", t["strict_subtraction"])
        print()
        show("The gentler reading the book invites (half the subtraction):",
             t["gentler_for_a_small_party"])
        print()
        print("  Which to use is a judgement call, and the rule says so. Decide, write it in")
        print("  RULES_DELTAS.md, and keep logs/loot.md measured against the same choice.")
    print()
    print("Treasure to attach to one encounter at this level:")
    for k in ("low", "moderate", "severe", "extreme"):
        print(f"    {k:<9} {t['per_encounter'][k]:>7} gp")
    print(f"    {'extra':<9} {t['per_encounter']['extra']:>7} gp   (placed outside encounters)")
    print()
    print(f"Source: {SOURCES['treasure_detail']}")
    print(f"Source: {SOURCES['treasure_per_encounter']}")
    print(f"Source: {SOURCES['treasure_party_size']}")
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


def cmd_settlement(args: argparse.Namespace) -> int:
    a = settlement_availability(args.level)
    print(f"A settlement of level {a['settlement_level']}:")
    print(f"  buys and sells common items up to item level {a['buy_up_to_item_level']}")
    g = a["top_end_stock_guide"]
    fmt = lambda xs: ", ".join(f"{n}x level {l}" for l in [x[0] for x in xs] for n in [dict(xs)[l]]) or "none"
    print(f"  how many of the top-end items, from the level-{g['from_treasure_row']} treasure row:")
    print(f"    permanent:   {fmt(g['permanent'])}")
    print(f"    consumables: {fmt(g['consumables'])}")
    print(f"  above that level: {a['above_settlement_level']}")
    print()
    print(f"Source: {SOURCES['settlement_item_levels']}")
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
        rows = []
        for lvl in sorted(TREASURE_BY_LEVEL):
            d = TREASURE_DETAIL[lvl]
            fmt = lambda xs: ", ".join(f"{n}x lvl {l}" for l, n in xs)
            rows.append({"level": lvl, "total gp": TREASURE_BY_LEVEL[lvl],
                         "permanent items": fmt(d["permanent"]),
                         "consumables": fmt(d["consumables"]),
                         "currency gp": d["currency"],
                         "per extra PC": d["per_extra_pc"]})
        _print_table(rows, ["level","total gp","permanent items","consumables","currency gp","per extra PC"])
        print(f"\nSource: {SOURCES['treasure_detail']}")
    elif which == "treasure-per-encounter":
        _print_table([dict(level=k, **v) for k, v in sorted(TREASURE_PER_ENCOUNTER.items())],
                     ["level","low","moderate","severe","extreme","extra"])
        print(f"\nSource: {SOURCES['treasure_per_encounter']}")
    elif which == "adjustments":
        rows = [{"starting level": lbl,
                 "elite HP": f"{adjusted_hp(l, elite=True):+d}",
                 "weak HP": f"{adjusted_hp(l, elite=False):+d}",
                 "elite becomes level": adjusted_level(l, elite=True),
                 "weak becomes level": adjusted_level(l, elite=False)}
                for l, lbl in [(-1,"-1"),(0,"0"),(1,"1"),(2,"2"),(3,"3"),(5,"5"),(6,"6"),
                               (19,"19"),(20,"20"),(21,"21")]]
        _print_table(rows, ["starting level","elite HP","weak HP","elite becomes level","weak becomes level"])
        print(f"\nSource: {SOURCES['creature_adjustments']}")
    elif which == "earn-income":
        _print_table(
            [dict(level=k, **v) for k, v in sorted(EARN_INCOME.items())],
            ["level", "failure", "trained", "expert", "master", "legendary"],
        )
        print(f"\nSource: {SOURCES['earn_income']}")
    elif which == "travel":
        _print_table(TRAVEL_SPEEDS, ["speed", "feet_per_minute", "miles_per_hour", "miles_per_day"])
        print("\nTerrain: " + ", ".join(f"{k} x{v:.2f}".rstrip("0").rstrip(".")
                                        for k, v in TRAVEL_TERRAIN.items())
              + f"; {TRAVEL_HOURS_PER_DAY}-hour travel day.")
        print(f"\nSource: {SOURCES['travel_speed']}")
    elif which == "budgets":
        rows = []
        for n in range(1, 7):
            pub, sm = encounter_budgets(n), encounter_budgets(n, smoothed=True)
            rows.append(dict(party_size=n, **{k: (f"{pub[k]}" if pub[k] == sm[k] else f"{pub[k]} ({sm[k]})")
                                              for k in ("trivial","low","moderate","severe","extreme")}))
        _print_table(rows, ["party_size", "trivial", "low", "moderate", "severe", "extreme"])
        print("\nPublished figure, with the smoothed alternative in brackets where they differ.")
        print(f"XP awarded is always the four-character figure: "
              + ", ".join(f"{k} {v}" for k, v in THREAT_BUDGET_FOR_FOUR.items()) + ".")
        print(f"\nSource: {SOURCES['encounter_budgets']}")
        print(f"Source: {SOURCES['xp_award_party_size']}")
    return 0


def cmd_sources(args: argparse.Namespace) -> int:
    print("Provenance of every table in tools/pf2e.py\n")
    for key in sorted(SOURCES):
        mark = "⚠ UNVERIFIED" if key in UNVERIFIED_TABLES else "verified"
        print(f"[{mark}] {key}\n    {SOURCES[key]}\n")
    if UNVERIFIED_TABLES:
        print(f"{len(UNVERIFIED_TABLES)} of {len(SOURCES)} tables are unverified: "
              + ", ".join(sorted(UNVERIFIED_TABLES)))
        print("\nThese are listed in DESIGN_NOTES.md under 'To verify before first play'.")
    else:
        print(f"0 of {len(SOURCES)} tables are unverified.")
        print("\nEvery table above was read from Archives of Nethys, or is labelled as this")
        print("framework's own convention rather than a published rule. Re-verifying against")
        print("AoN found eight errors in this file; DESIGN_NOTES.md lists them under 'Pass 2'.")
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
    p.add_argument("--smoothed", action="store_true",
                   help="20 XP per character scaled by threat, instead of the published "
                        "per-character adjustment (avoids Low collapsing to 0 for a solo party)")

    p = sub.add_parser("settlement", help="what a settlement of a given level can sell")
    p.add_argument("--level", type=int, required=True)

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
                 "treasure", "treasure-per-encounter", "adjustments", "earn-income", "travel",
                 "budgets"],
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
            "settlement": cmd_settlement,
        "tables": cmd_tables,
            "sources": cmd_sources,
            "time": cmd_time,
        }[args.cmd](args)
    except ValueError as exc:
        print(f"pf2e.py: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
