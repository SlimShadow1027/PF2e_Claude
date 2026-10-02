#!/usr/bin/env python3
"""dnd5e.py — the D&D 2024 ("5.5e") rules tables, as data, so nothing is recalled from memory.

The sibling of `tools/pf2e.py`, and it follows the same discipline: every table carries a
`Source:` note naming where the value was read from, anything this framework invented says
so in place, and `python3 tools/dnd5e.py sources` prints the whole provenance list.

Verification note. The PRIMARY source here is the **System Reference Document 5.2** ("SRD
5.2"), which Wizards of the Coast publishes free of charge under CC-BY-4.0 and which
contains the 2024 core rules. It was read from a complete Markdown transcription of the
official PDF:

    github.com/springbov/dndsrd5.2_markdown @6a3547c1d625fb125fbbcb8ded563f5beff197a8
    (file DND-SRD-5.2-CC.md; a `marker` conversion of SRD_CC_v5.2.pdf, CC-BY-4.0)

That transcription is a conversion rather than the publisher's own file, so **every numeric
table below was additionally cross-checked against a second, independent implementation**:

    github.com/foundryvtt/dnd5e v6.0.5 @7bfb3f1c03e107bf65942151ef08d50ddb01ba8a
    (module/config.mjs)

Where the two agreed, the table is marked verified and both are cited. Where the SRD does
not publish a value at all — notably **treasure by level**, which lives in the 2024 Dungeon
Master's Guide and is not SRD material — this file does not guess: the table says it is this
framework's own convention, names what published numbers it was derived from, and appears in
`CONVENTION_TABLES` so the provenance report counts it separately from the quoted rules.

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

import rules  # noqa: E402

SRD = (
    "SRD 5.2 (Wizards of the Coast, CC-BY-4.0), read from the Markdown transcription at "
    "springbov/dndsrd5.2_markdown @6a3547c (DND-SRD-5.2-CC.md)"
)
FOUNDRY = (
    "foundryvtt/dnd5e v6.0.5 @7bfb3f1c03e107bf65942151ef08d50ddb01ba8a "
    "(module/config.mjs), an independent implementation of the same rules"
)

SOURCES: dict[str, str] = {}
UNVERIFIED_TABLES: list[str] = []
#: Tables that are this framework's own convention rather than a published rule. Counted
#: separately from UNVERIFIED_TABLES: these are not unchecked, they are *ours*.
CONVENTION_TABLES: list[str] = []


def _src(key: str, text: str, verified: bool = True, convention: bool = False) -> str:
    SOURCES[key] = text
    if not verified:
        UNVERIFIED_TABLES.append(key)
    if convention:
        CONVENTION_TABLES.append(key)
    return text


# --------------------------------------------------------------------------------------
# Identity
# --------------------------------------------------------------------------------------

SYSTEM_ID = "dnd5e"
SYSTEM_NAME = "Dungeons & Dragons 2024 (5.5e)"
SYSTEM_SHORT = "D&D 5.5e"

#: Pass or fail against a target number. There is no degree ladder in this game.
USES_DEGREES = False

CRIT_RULE = (
    "A natural 20 on an ATTACK ROLL hits regardless of AC and is a Critical Hit; a natural 1 "
    "misses regardless of AC. Critical Hits roll the attack's damage dice twice. Ability checks "
    "and saving throws have NO natural-20 or natural-1 rule — a 20 on a check is just a 20."
)
_src(
    "crit_rule",
    SRD + ", 'Playing the Game' -> 'D20 Tests' -> 'Attack Rolls' -> 'Rolling 20 or 1': \"If you "
    "roll a 20 on the d20 (called a 'natural 20') for an attack roll, the attack hits regardless "
    "of any modifiers or the target's AC. This is called a Critical Hit\" and \"If you roll a 1 on "
    "the d20 (a 'natural 1') for an attack roll, the attack misses regardless of any modifiers or "
    "the target's AC.\" Both statements are scoped to attack rolls; the Ability Checks and Saving "
    "Throws sections state no equivalent rule, which is the 2024 behaviour this file implements. "
    "Critical Hit damage is from 'Damage and Healing' -> 'Critical Hits': \"Roll the attack's "
    "damage dice twice, add them together, and add any relevant modifiers as normal.\"",
)

#: A campaign with no named setting gets the placeholder calendar from rules.py. The SRD
#: publishes no calendar, so this file does not invent one; a setting's calendar belongs in
#: the world's CALENDAR.md, where both rulesets read it.
DEFAULT_CALENDAR = "generic"
_src(
    "calendar",
    "SRD 5.2 publishes no calendar, no month names and no era, so this ruleset registers none. "
    "A campaign defaults to the placeholder calendar in tools/rules.py (twelve 30-day months). A "
    "named setting's calendar goes in `worlds/<slug>/CALENDAR.md`, which both rulesets read — see "
    "`python3 tools/rules.py calendars`. The month names of published D&D settings are not SRD "
    "material and are deliberately not reproduced here.",
    convention=True,
)


# --------------------------------------------------------------------------------------
# Difficulty classes
# --------------------------------------------------------------------------------------

DIFFICULTY_DCS: dict[str, int] = {
    "very easy": 5,
    "easy": 10,
    "medium": 15,
    "hard": 20,
    "very hard": 25,
    "nearly impossible": 30,
}
_src(
    "difficulty_dcs",
    SRD + ", 'Playing the Game' -> 'D20 Tests' -> 'Ability Checks' -> 'Difficulty Class', the "
    "Typical Difficulty Classes table: very easy 5, easy 10, medium 15, hard 20, very hard 25, "
    "nearly impossible 30. NOTE what this table is NOT: D&D 2024 has no DC-by-level table. The "
    "DC of a task does not rise with the party's level, which is the single biggest difference "
    "from Pathfinder's maths and the reason a level 15 party trivially clears a DC 15 lock. "
    "Cross-checked against " + FOUNDRY + " (DND5E.activityConsumptionTypes / difficulty labels).",
)

#: The DC a creature's own abilities set, where a stat block does not state one.
SPELL_SAVE_DC_FORMULA = "8 + proficiency bonus + spellcasting ability modifier"
_src(
    "spell_save_dc",
    SRD + ", 'Spells' -> 'Casting Spells' -> 'Saving Throws': a spell's save DC is 8 plus the "
    "caster's spellcasting ability modifier and Proficiency Bonus. Cross-checked against "
    + FOUNDRY + " (module/documents/actor/actor.mjs, spell DC derivation).",
)


def task_dc(difficulty: str) -> int:
    """The DC for a named task difficulty. There is no level term — that is the point."""
    key = str(difficulty).strip().lower()
    if key not in DIFFICULTY_DCS:
        raise ValueError(f"{difficulty!r} is not a task difficulty ({', '.join(DIFFICULTY_DCS)})")
    return DIFFICULTY_DCS[key]


def concentration_dc(damage: int) -> int:
    """The Constitution save DC to keep Concentration after taking damage."""
    return min(30, max(10, int(damage) // 2))


_src(
    "concentration",
    SRD + ", 'Rules Glossary' -> 'Concentration': \"If you take damage, you must succeed on a "
    "Constitution saving throw to maintain Concentration. The DC equals 10 or half the damage "
    "taken (round down), whichever number is higher, up to a maximum DC of 30.\" Concentration "
    "also ends on casting another Concentration spell, on gaining the Incapacitated condition, "
    "and on death.",
)

COVER: dict[str, dict[str, Any]] = {
    "half": {"ac": 2, "dex_saves": 2, "targetable": True},
    "three-quarters": {"ac": 5, "dex_saves": 5, "targetable": True},
    "total": {"ac": None, "dex_saves": None, "targetable": False},
}
_src(
    "cover",
    SRD + ", 'Rules Glossary' -> 'Cover': Half Cover is a +2 bonus to AC and Dexterity saving "
    "throws, Three-Quarters Cover is +5, and Total Cover means the target \"can't be targeted "
    "directly\". \"If behind more than one degree of cover, a target benefits only from the most "
    "protective degree.\"",
)


# --------------------------------------------------------------------------------------
# Proficiency bonus
# --------------------------------------------------------------------------------------

PROFICIENCY_BONUS_BANDS: list[tuple[int, int, int]] = [
    (1, 4, 2), (5, 8, 3), (9, 12, 4), (13, 16, 5), (17, 20, 6),
    (21, 24, 7), (25, 28, 8), (29, 30, 9),
]
_src(
    "proficiency_bonus",
    SRD + ", 'Playing the Game' -> 'Proficiency', the Proficiency Bonus table, read row by row: "
    "up to 4 is +2, 5-8 is +3, 9-12 is +4, 13-16 is +5, 17-20 is +6, 21-24 is +7, 25-28 is +8, "
    "29-30 is +9. The same column serves character level and monster Challenge Rating. "
    "Cross-checked against the Character Advancement table in 'Character Creation' -> 'Level "
    "Advancement', whose Proficiency Bonus column matches for levels 1-20, and against "
    + FOUNDRY + ".",
)


def proficiency_bonus(level_or_cr: float) -> int:
    """The Proficiency Bonus for a character level or a monster's CR."""
    value = math.floor(float(level_or_cr))
    if value < 1:
        value = 1  # CR 0 and CR fractions all sit in the 'up to 4' band
    for low, high, bonus in PROFICIENCY_BONUS_BANDS:
        if low <= value <= high:
            return bonus
    if value > 30:
        return 9
    return 2


def ability_modifier(score: int) -> int:
    """(score - 10) halved, rounded down."""
    return (int(score) - 10) // 2


_src(
    "ability_modifier",
    SRD + ", 'Rules Glossary' -> 'Ability Score and Modifier' and 'Playing the Game' -> 'The Six "
    "Abilities': the modifier is the score minus 10, halved and rounded down. Python's floor "
    "division gives the published answer for odd scores below 10 as well (score 7 -> -2).",
)


# --------------------------------------------------------------------------------------
# Advancement
# --------------------------------------------------------------------------------------

#: level -> CUMULATIVE XP total needed to be that level. Unlike Pathfinder, the counter is
#: never reset: a level 5 character has at least 6,500 XP on the sheet.
CHARACTER_ADVANCEMENT: dict[int, int] = {
    1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500, 6: 14000, 7: 23000, 8: 34000, 9: 48000,
    10: 64000, 11: 85000, 12: 100000, 13: 120000, 14: 140000, 15: 165000, 16: 195000,
    17: 225000, 18: 265000, 19: 305000, 20: 355000,
}
_src(
    "advancement",
    SRD + ", 'Character Creation' -> 'Level Advancement', the Character Advancement table, read "
    "row by row for all twenty levels: \"When your XP total equals or exceeds a number in the "
    "Experience Points column, you reach the corresponding level.\" The totals are CUMULATIVE and "
    "the counter is not reset on levelling — which is the opposite of Pathfinder's flat 1,000 "
    "per level, so the two games' XP numbers are not interchangeable. Cross-checked value for "
    "value against " + FOUNDRY + " (DND5E.CHARACTER_EXP_LEVELS), which matches exactly. The "
    "level 20+ feat rule (one feat per 30,000 XP above 355,000) is in the same section's 'Bonus "
    "Feats at Level 20' sidebar and is implemented by `xp_to_level` returning None past 20.",
)

#: Published tiers of play. These are the shared scale a cross-system world is written on;
#: see `rules.SCOPE_BANDS` and `system/23-cross-system-worlds.md`.
TIERS: list[tuple[int, int, str, str]] = [
    (1, 4, "Tier 1", "apprentice adventurers; threats to local farmsteads or villages"),
    (5, 10, "Tier 2", "full-fledged adventurers; dangers that threaten cities and kingdoms"),
    (11, 16, "Tier 3", "special among adventurers; threats to whole regions"),
    (17, 20, "Tier 4", "heroic archetypes; the fate of the world or the order of the multiverse"),
]
_src(
    "tiers",
    SRD + ", 'Character Creation' -> 'Level Advancement' -> 'Tiers of Play', quoting the scope of "
    "each tier. The SRD is explicit that \"these tiers don't have any rules associated with "
    "them\" — they describe how big the stakes get, which is the only thing this framework uses "
    "them for (see tools/rules.py `SCOPE_BANDS`).",
)

FIXED_HP_PER_LEVEL: dict[str, int] = {
    "barbarian": 7,
    "fighter": 6, "paladin": 6, "ranger": 6,
    "bard": 5, "cleric": 5, "druid": 5, "monk": 5, "rogue": 5, "warlock": 5,
    "sorcerer": 4, "wizard": 4,
}
HIT_DIE_BY_CLASS: dict[str, int] = {
    "barbarian": 12,
    "fighter": 10, "paladin": 10, "ranger": 10,
    "bard": 8, "cleric": 8, "druid": 8, "monk": 8, "rogue": 8, "warlock": 8,
    "sorcerer": 6, "wizard": 6,
}
_src(
    "hit_points",
    SRD + ", 'Character Creation' -> 'Level Advancement' -> 'Gaining a Level', step 2 and the "
    "Fixed Hit Points by Class table: Barbarian 7 + Con modifier; Fighter, Paladin or Ranger 6 + "
    "Con; Bard, Cleric, Druid, Monk, Rogue or Warlock 5 + Con; Sorcerer or Wizard 4 + Con. The "
    "Hit Die sizes are each class's own table in 'Classes' (d12 Barbarian, d10 Fighter/Paladin/"
    "Ranger, d8 Bard/Cleric/Druid/Monk/Rogue/Warlock, d6 Sorcerer/Wizard) and are the published "
    "average+1 of the fixed values above. At level 1 a character takes the die's full value "
    "rather than the fixed figure.",
)


def xp_to_level(level: int) -> int | None:
    """The CUMULATIVE XP total needed to be `level`. None outside 1-20."""
    return CHARACTER_ADVANCEMENT.get(int(level))


def xp_is_cumulative() -> bool:
    """True: a D&D character's XP total keeps climbing and is never reset."""
    return True


def level_for_xp(xp: int) -> int:
    """The level an XP total has reached."""
    best = 1
    for lvl, need in sorted(CHARACTER_ADVANCEMENT.items()):
        if int(xp) >= need:
            best = lvl
    return best


def tier_of(level: int) -> str:
    return rules.scope_band(SYSTEM_ID, level)


def tier_name(level: int) -> str:
    for low, high, name, _ in TIERS:
        if low <= int(level) <= high:
            return name
    return "Tier 4" if int(level) > 20 else "Tier 1"


# --------------------------------------------------------------------------------------
# Monsters: XP by Challenge Rating
# --------------------------------------------------------------------------------------

#: CR (as a Fraction so 1/8 stays exact) -> XP. CR 0 is published as "0 or 10".
XP_BY_CR: dict[Fraction, int] = {
    Fraction(0): 10,
    Fraction(1, 8): 25, Fraction(1, 4): 50, Fraction(1, 2): 100,
    Fraction(1): 200, Fraction(2): 450, Fraction(3): 700, Fraction(4): 1100,
    Fraction(5): 1800, Fraction(6): 2300, Fraction(7): 2900, Fraction(8): 3900,
    Fraction(9): 5000, Fraction(10): 5900, Fraction(11): 7200, Fraction(12): 8400,
    Fraction(13): 10000, Fraction(14): 11500, Fraction(15): 13000, Fraction(16): 15000,
    Fraction(17): 18000, Fraction(18): 20000, Fraction(19): 22000, Fraction(20): 25000,
    Fraction(21): 33000, Fraction(22): 41000, Fraction(23): 50000, Fraction(24): 62000,
    Fraction(25): 75000, Fraction(26): 90000, Fraction(27): 105000, Fraction(28): 120000,
    Fraction(29): 135000, Fraction(30): 155000,
}
_src(
    "xp_by_cr",
    SRD + ", 'Monsters' -> 'Experience Points', the Experience Points by Challenge Rating table, "
    "read row by row for all 34 rows (CR 0 through 30, including CR 1/8, 1/4 and 1/2). CR 0 is "
    "published as \"0 or 10\" — a CR 0 creature is worth 10 XP unless its stat block says 0 — and "
    "this table stores 10, with `creature_xp(..., zero_xp=True)` for the 0 case. Cross-checked "
    "against " + FOUNDRY + " (DND5E.CR_EXP_LEVELS), which matches every integer CR exactly; the "
    "three fractional rows are not in that array and come from the SRD table alone. NOTE that a "
    "creature's XP does NOT vary with the party's level, unlike Pathfinder's creature XP.",
)


def parse_cr(text: Any) -> Fraction:
    """'1/4', '0.25', 5 -> a Fraction. Raises on anything not a published CR."""
    if isinstance(text, Fraction):
        cr = text
    else:
        s = str(text).strip().lower().replace("cr", "").strip()
        if not s:
            raise ValueError("no Challenge Rating given")
        try:
            cr = Fraction(s)
        except (ValueError, ZeroDivisionError) as exc:
            raise ValueError(f"{text!r} is not a Challenge Rating (try 1/4, 2, 17)") from exc
    if cr not in XP_BY_CR:
        raise ValueError(
            f"CR {cr} is not a published Challenge Rating "
            f"(0, 1/8, 1/4, 1/2, then 1 through 30)"
        )
    return cr


def format_cr(cr: Fraction) -> str:
    return str(cr) if cr.denominator != 1 else str(cr.numerator)


def creature_xp(cr: Any, *, zero_xp: bool = False) -> int:
    """The XP a creature of this CR is worth. Party level does not enter into it."""
    c = parse_cr(cr)
    if c == 0 and zero_xp:
        return 0
    return XP_BY_CR[c]


# --------------------------------------------------------------------------------------
# Encounter building
# --------------------------------------------------------------------------------------

THREATS = ("low", "moderate", "high")

#: party level -> XP budget PER CHARACTER for each difficulty.
XP_BUDGET_PER_CHARACTER: dict[int, dict[str, int]] = {
    1: {"low": 50, "moderate": 75, "high": 100},
    2: {"low": 100, "moderate": 150, "high": 200},
    3: {"low": 150, "moderate": 225, "high": 400},
    4: {"low": 250, "moderate": 375, "high": 500},
    5: {"low": 500, "moderate": 750, "high": 1100},
    6: {"low": 600, "moderate": 1000, "high": 1400},
    7: {"low": 750, "moderate": 1300, "high": 1700},
    8: {"low": 1000, "moderate": 1700, "high": 2100},
    9: {"low": 1300, "moderate": 2000, "high": 2600},
    10: {"low": 1600, "moderate": 2300, "high": 3100},
    11: {"low": 1900, "moderate": 2900, "high": 4100},
    12: {"low": 2200, "moderate": 3700, "high": 4700},
    13: {"low": 2600, "moderate": 4200, "high": 5400},
    14: {"low": 2900, "moderate": 4900, "high": 6200},
    15: {"low": 3300, "moderate": 5400, "high": 7800},
    16: {"low": 3800, "moderate": 6100, "high": 9800},
    17: {"low": 4500, "moderate": 7200, "high": 11700},
    18: {"low": 5000, "moderate": 8700, "high": 14200},
    19: {"low": 5500, "moderate": 10700, "high": 17200},
    20: {"low": 6400, "moderate": 13200, "high": 22000},
}
_src(
    "encounter_budget",
    SRD + ", 'Gameplay Toolbox' -> 'Combat Encounters' -> 'Combat Encounter Difficulty', step 2 "
    "and the XP Budget per Character table, read row by row for all twenty levels. The method is "
    "quoted: \"cross-reference the party's level with the desired encounter difficulty. Multiply "
    "the number in the table by the number of characters in the party to get your XP budget.\" "
    "Cross-checked value for value against " + FOUNDRY + " (DND5E.ENCOUNTER_DIFFICULTY, whose "
    "index 0 is a zero padding row), which matches exactly. Two differences from Pathfinder that "
    "matter at a small table: the budget is strictly LINEAR in party size, so a solo character "
    "simply gets one character's budget and nothing degenerates to zero; and the 2024 rules have "
    "NO encounter multiplier for the number of monsters — the 2014 'adjusted XP' multiplier is "
    "gone. The troubleshooting guidance that replaces it is quoted in `MANY_CREATURES_ADVICE`.",
)

MANY_CREATURES_ADVICE = (
    "If your encounter includes more than two creatures per character, include fragile creatures "
    "that can be defeated quickly. This guideline is especially important for characters of level "
    "1 or 2."
)
_src(
    "many_creatures",
    SRD + ", 'Gameplay Toolbox' -> 'Combat Encounters' -> 'Troubleshooting' -> 'Many Creatures', "
    "quoted. This is what the 2024 rules give instead of the 2014 encounter multiplier: a prose "
    "caution about action economy, not a number. `encounter` warns when the ratio is exceeded.",
)

DIFFICULTY_MEANING = {
    "low": "likely one or two scary moments; the characters should emerge victorious with no "
           "casualties, though one or more might need to spend healing resources",
    "moderate": "absent healing and other resources this could go badly; weaker characters "
                "might be taken out of the fight, and there is a slim chance one or more dies",
    "high": "could be lethal for one or more characters; surviving it will take smart tactics, "
            "quick thinking, and maybe a little luck",
}
_src(
    "difficulty_meaning",
    SRD + ", 'Gameplay Toolbox' -> 'Combat Encounters' -> 'Step 1: Choose a Difficulty', "
    "paraphrasing the three published descriptions closely. The published Low-difficulty "
    "guideline also notes that \"a single monster generally presents a low-difficulty challenge "
    "for a party of four characters whose level equals the monster's Challenge Rating\".",
)


def encounter_budgets(party_size: int, party_level: int = 1, **_: Any) -> dict[str, int]:
    """The XP budget for each difficulty: the per-character figure times the party size."""
    if party_size < 1:
        raise ValueError("a party needs at least one character")
    lvl = int(party_level)
    if lvl not in XP_BUDGET_PER_CHARACTER:
        raise ValueError(f"no published XP budget for party level {lvl} (the table runs 1 to 20)")
    per = XP_BUDGET_PER_CHARACTER[lvl]
    return {t: per[t] * int(party_size) for t in THREATS}


def degenerate_budgets(party_size: int, party_level: int = 1) -> list[str]:
    """Budgets that collapse at this party size. Empty for D&D — the table is linear."""
    return []


def rate_encounter(total_xp: int, party_size: int, party_level: int = 1, **_: Any) -> str:
    """Which published difficulty a built encounter actually lands on."""
    b = encounter_budgets(party_size, party_level)
    if total_xp > b["high"]:
        return "beyond high"
    if total_xp >= b["high"]:
        return "high"
    if total_xp >= b["moderate"]:
        return "moderate"
    if total_xp >= b["low"]:
        return "low"
    return "below low"


def xp_award(total_xp_spent: int, party_size: int = 4, **_: Any) -> int:
    """XP awarded for clearing the encounter: the creatures' own XP, undivided.

    Source: see `sources` entry `xp_award`.
    """
    return int(total_xp_spent)


_src(
    "xp_award",
    SRD + ", 'Monsters' -> 'Experience Points': \"XP is awarded for defeating the monster in "
    "combat or otherwise neutralizing it\", with the amount being the figure in the stat block. "
    "The SRD states no division of that total among the party and no party-size adjustment to "
    "the award, so this framework awards the creatures' own XP as rolled up. NOTE how this "
    "interacts with the budget: the budget is multiplied by party size but the award is not "
    "divided by it, so a solo character fighting one character's worth of monsters earns one "
    "character's worth of XP and advances along the published curve at the published rate. "
    "Contrast Pathfinder, which fixes the same problem the other way round — see `python3 "
    "tools/pf2e.py sources` (xp_award_party_size).",
)


# --------------------------------------------------------------------------------------
# Treasure and the economy
# --------------------------------------------------------------------------------------

COIN_ORDER = ("pp", "gp", "ep", "sp", "cp")
COIN_IN_CP = {"pp": 1000, "gp": 100, "ep": 50, "sp": 10, "cp": 1}
BASE_COIN = "gp"
COINS_PER_POUND = 50
_src(
    "coins",
    SRD + ", 'Equipment' -> 'Coins', the Coin Values table: cp is 1/100 gp, sp is 1/10 gp, ep is "
    "1/2 gp, gp is 1, pp is 10 gp. \"A coin weighs about a third of an ounce, so fifty coins "
    "weigh a pound.\" Cross-checked against " + FOUNDRY + " (DND5E.currencies, whose `conversion` "
    "field is coins-per-gp: pp 0.1, gp 1, ep 2, sp 10, cp 100), which matches. Electrum is the "
    "difference from Pathfinder's four coins, and it is why a shared world cannot simply copy a "
    "purse across rulesets.",
)

MAGIC_ITEM_VALUES: dict[str, int | None] = {
    "common": 100,
    "uncommon": 400,
    "rare": 4000,
    "very rare": 40000,
    "legendary": 200000,
    "artifact": None,  # priceless
}
_src(
    "magic_item_values",
    SRD + ", 'Magic Items' -> 'Magic Item Rarity', the Magic Item Rarities and Values table: "
    "common 100 GP, uncommon 400, rare 4,000, very rare 40,000, legendary 200,000, artifact "
    "priceless. \"Halve the value for a consumable item other than a Spell Scroll.\" Where a "
    "magic item incorporates a mundane item, that item's cost is added on top.",
)

MAGIC_ITEM_AVAILABILITY: dict[str, str] = {
    "common": "can often be bought in a town or city",
    "uncommon": "usually found only in cities",
    "rare": "usually found only in cities",
    "very rare": "might be sold only in wondrous locations, such as a city on another plane",
    "legendary": "might be sold only in wondrous locations, such as a city on another plane",
    "artifact": "not for sale; unique and difficult to acquire",
}
_src(
    "magic_item_availability",
    SRD + ", 'Magic Items' -> 'Magic Item Rarity' -> 'Magic Item Values by Rarity', quoted: "
    "\"Common magic items can often be bought in a town or city. Uncommon and Rare magic items "
    "are usually found only in cities, and rarer magic items might be sold only in wondrous "
    "locations, such as a city on another plane of existence.\" This is the published hook that "
    "`settlement` uses, and it is what a shared world's GAZETTEER.md records alongside "
    "Pathfinder's numeric settlement item level.",
)

ATTUNEMENT_LIMIT = 3
_src(
    "attunement",
    SRD + ", 'Rules Glossary' -> 'Attunement': \"A creature can have Attunement with no more than "
    "three magic items at a time.\" (The Rogue's level 13 Use Magic Device feature raises that "
    "character's own limit to four; the state tool stores the limit per character so a feature "
    "like that is recorded rather than hardcoded away.)",
)

#: Starting wealth and magic items for a character who begins above level 1. PUBLISHED.
STARTING_AT_HIGHER_LEVELS: list[dict[str, Any]] = [
    {"levels": (2, 4), "gp": 0, "bonus_roll": None,
     "items": {"common": 1}},
    {"levels": (5, 10), "gp": 500, "bonus_roll": "1d10 x 25 gp",
     "items": {"common": 1, "uncommon": 1}},
    {"levels": (11, 16), "gp": 5000, "bonus_roll": "1d10 x 250 gp",
     "items": {"common": 2, "uncommon": 3, "rare": 1}},
    {"levels": (17, 20), "gp": 20000, "bonus_roll": "1d10 x 250 gp",
     "items": {"common": 2, "uncommon": 4, "rare": 3, "very rare": 1}},
]
_src(
    "starting_at_higher_levels",
    SRD + ", 'Character Creation' -> 'Starting at Higher Levels' -> 'Starting Equipment', the "
    "Starting Equipment at Higher Levels table, read row by row: levels 2-4 normal starting "
    "equipment plus 1 common item; 5-10 500 GP plus 1d10 x 25 GP plus 1 common and 1 uncommon; "
    "11-16 5,000 GP plus 1d10 x 250 GP plus 2 common, 3 uncommon, 1 rare; 17-20 20,000 GP plus "
    "1d10 x 250 GP plus 2 common, 4 uncommon, 3 rare, 1 very rare. This is the ONLY published "
    "wealth-by-level statement in the SRD, and `treasure_for` is built from it.",
)


def _interpolate_tier(level: int) -> dict[str, Any]:
    for row in STARTING_AT_HIGHER_LEVELS:
        low, high = row["levels"]
        if low <= level <= high:
            return row
    return STARTING_AT_HIGHER_LEVELS[-1] if level > 20 else {
        "levels": (1, 1), "gp": 0, "bonus_roll": None, "items": {}}


def treasure_for(level: int, party_size: int = 4, **_: Any) -> dict[str, Any]:
    """Expected accumulated party wealth at a level. THIS FRAMEWORK'S OWN CONVENTION.

    The SRD publishes no treasure-by-level table — the 2024 treasure tables are Dungeon
    Master's Guide material and are not SRD content. Rather than invent numbers and present
    them as rules, this returns the published *starting-at-this-level* figures, which are the
    nearest published statement of "what a character of this level should have", and says
    plainly that it is a floor for one character rather than a budget to hand out.

    See the `treasure_by_level` entry in `sources` for the full reasoning.
    """
    lvl = max(1, int(level))
    row = _interpolate_tier(lvl)
    low, high = row["levels"]
    return {
        "level": lvl,
        "convention": True,
        "band": f"levels {low}-{high}" if low != high else "level 1",
        "gp_per_character": row["gp"],
        "bonus_roll_per_character": row["bonus_roll"],
        "magic_items_per_character": dict(row["items"]),
        "gp_party": row["gp"] * int(party_size),
        "magic_items_party": {k: v * int(party_size) for k, v in row["items"].items()},
        "note": (
            "This is the SRD's starting-equipment-at-higher-levels figure, not a published "
            "treasure budget. Read it as the floor a character of this level is assumed to have "
            "reached, and pace awards so the party passes it rather than as a per-level "
            "allowance to spend. The 2024 treasure tables are DMG material and not SRD content."
        ),
        "item_values": {k: v for k, v in MAGIC_ITEM_VALUES.items()},
    }


_src(
    "treasure_by_level",
    "THIS FRAMEWORK'S OWN CONVENTION, built from published parts. SRD 5.2 contains NO "
    "treasure-by-level or treasure-hoard table: the 2024 random treasure tables are Dungeon "
    "Master's Guide material and were not released as SRD content, and this file will not "
    "reproduce or reconstruct them. What `treasure_for` returns instead is the published "
    "Starting Equipment at Higher Levels table (see `starting_at_higher_levels`) priced with the "
    "published Magic Item Rarities and Values table (see `magic_item_values`), reported as an "
    "expected floor rather than an award budget. Where Pathfinder's GM Core gives an exact per-"
    "level treasure allotment, D&D 2024's equivalent guidance is not open content, so a 5.5e "
    "campaign in this framework paces treasure by tier and says so. If you own the 2024 DMG, use "
    "its tables and record the deviation in the campaign's RULES_DELTAS.md.",
    convention=True,
)

LIFESTYLE_EXPENSES: dict[str, dict[str, Any]] = {
    "wretched": {"cp_per_day": 0, "label": "Free"},
    "squalid": {"cp_per_day": 10, "label": "1 sp per day"},
    "poor": {"cp_per_day": 20, "label": "2 sp per day"},
    "modest": {"cp_per_day": 100, "label": "1 gp per day"},
    "comfortable": {"cp_per_day": 200, "label": "2 gp per day"},
    "wealthy": {"cp_per_day": 400, "label": "4 gp per day"},
    "aristocratic": {"cp_per_day": 1000, "label": "10 gp per day"},
}
_src(
    "lifestyle",
    SRD + ", 'Equipment' -> 'Lifestyle Expenses', read heading by heading: Wretched free, Squalid "
    "1 sp/day, Poor 2 sp/day, Modest 1 gp/day, Comfortable 2 gp/day, Wealthy 4 gp/day, "
    "Aristocratic 10 gp/day. \"Lifestyles have no inherent consequences, but the GM might take "
    "them into account.\" Stored in copper so downtime arithmetic stays integral.",
)


def settlement_availability(settlement: str) -> dict[str, Any]:
    """Which magic item rarities can be bought in a settlement of this kind."""
    key = str(settlement).strip().lower()
    buckets = {
        "village": ["common"],
        "town": ["common"],
        "city": ["common", "uncommon", "rare"],
        "metropolis": ["common", "uncommon", "rare"],
        "wondrous": ["common", "uncommon", "rare", "very rare", "legendary"],
    }
    if key not in buckets:
        raise ValueError(f"{settlement!r} is not a settlement kind ({', '.join(buckets)})")
    return {
        "settlement": key,
        "purchasable": buckets[key],
        "unavailable": [r for r in MAGIC_ITEM_VALUES if r not in buckets[key]],
        "values": {r: MAGIC_ITEM_VALUES[r] for r in buckets[key]},
        "note": MAGIC_ITEM_AVAILABILITY.get(buckets[key][-1], ""),
        "convention": True,
    }


_src(
    "settlement_availability",
    "THIS FRAMEWORK'S OWN CONVENTION, reading the published availability prose as a lookup. The "
    "rarity-to-place mapping is quoted in `magic_item_availability`; the SRD names \"a town or "
    "city\", \"cities\" and \"wondrous locations\" but publishes no settlement-size table, so the "
    "village/town/city/metropolis/wondrous buckets here are this framework's. The parallel "
    "Pathfinder table (`python3 tools/pf2e.py settlement`) is also a convention, and a shared "
    "world's GAZETTEER.md records both so either ruleset can shop in the same market.",
    convention=True,
)


# --------------------------------------------------------------------------------------
# Carrying capacity
# --------------------------------------------------------------------------------------

CARRY_MULTIPLIERS: dict[str, tuple[float, float]] = {
    "tiny": (7.5, 15),
    "small": (15, 30),
    "medium": (15, 30),
    "large": (30, 60),
    "huge": (60, 120),
    "gargantuan": (120, 240),
}
_src(
    "carrying_capacity",
    SRD + ", 'Rules Glossary' -> 'Carrying Capacity', the Carrying Capacity table: Tiny Str x 7.5 "
    "lb carry and x 15 drag/lift/push; Small/Medium x 15 and x 30; Large x 30 and x 60; Huge x 60 "
    "and x 120; Gargantuan x 120 and x 240. \"While dragging, lifting, or pushing weight in excess "
    "of the maximum weight you can carry, your Speed can be no more than 5 feet.\" NOTE the "
    "multiplier is on the Strength SCORE, not the modifier, and NOTE what is absent: SRD 5.2 "
    "defines no intermediate 'encumbered' band between carrying freely and reaching the maximum. "
    "Pathfinder has one; this ruleset does not, and `carry_report` reports no such threshold "
    "rather than inventing one. The optional variant encumbrance rule is not SRD content.",
)


def carry_capacity(strength: int, size: str = "medium") -> dict[str, float]:
    key = str(size).strip().lower()
    if key not in CARRY_MULTIPLIERS:
        raise ValueError(f"{size!r} is not a creature size ({', '.join(CARRY_MULTIPLIERS)})")
    carry, drag = CARRY_MULTIPLIERS[key]
    return {"carry": int(strength) * carry, "drag_lift_push": int(strength) * drag}


def item_weight(spec: Any) -> float:
    """Weight in pounds. Accepts 2, '2', '2 lb', '1/2 lb', '--' and None."""
    if spec is None:
        return 0.0
    text = str(spec).strip().lower()
    if text in ("", "-", "--", "0", "negligible", "none"):
        return 0.0
    text = re.sub(r"(lbs?\.?|pounds?)$", "", text).strip()
    try:
        return float(Fraction(text))
    except (ValueError, ZeroDivisionError):
        return 0.0


def carry_report(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Weight carried against capacity, per carrier, in pounds.

    Coins are counted: fifty coins weigh a pound (SRD 'Coins'). A character's `strength`
    (the SCORE, not the modifier) and `size` drive the capacity; a character with neither
    is reported against a Strength 10 Medium body and flagged, because a limit computed
    from a missing number is worse than no limit.
    """
    rows = []
    purse = (data.get("party") or {}).get("gold") or {}
    coin_count = sum(int(purse.get(c, 0)) for c in COIN_ORDER)
    coin_lb = coin_count / float(COINS_PER_POUND)
    pcs = data.get("pcs") or {}
    # The purse is shared, so its weight is attributed to the whole party once rather than
    # multiplied across carriers.
    share = coin_lb / len(pcs) if pcs else 0.0
    for key, pc in pcs.items():
        carried = 0.0
        for it in pc.get("items", []):
            carried += item_weight(it.get("weight", it.get("lb", 0))) * int(it.get("qty", 1))
        carried += share
        strength = pc.get("strength")
        assumed = strength is None
        strength = 10 if assumed else int(strength)
        size = str(pc.get("size", "medium")).lower()
        cap = carry_capacity(strength, size)
        rows.append(
            {
                "id": key,
                "name": pc.get("name", key),
                "unit": "lb",
                "carried": round(carried, 2),
                "counted": round(carried, 2),
                "coin_share_lb": round(share, 2),
                "strength": strength,
                "strength_assumed": assumed,
                "size": size,
                "max": cap["carry"],
                "drag_lift_push": cap["drag_lift_push"],
                "encumbered_after": None,  # no such band in SRD 5.2
                "encumbered": False,
                "over_max": carried > cap["carry"],
                "line": (
                    f"{carried:.1f} lb of {cap['carry']:.0f} lb capacity"
                    f" (Str {strength}{' assumed' if assumed else ''}, {size})"
                ),
            }
        )
    return rows


# --------------------------------------------------------------------------------------
# Conditions
# --------------------------------------------------------------------------------------

#: Exhaustion is the only condition in this game that stacks, and it carries a level.
VALUED_CONDITIONS = {"exhaustion"}
UNVALUED_CONDITIONS = {
    "blinded", "charmed", "deafened", "frightened", "grappled", "incapacitated",
    "invisible", "paralyzed", "petrified", "poisoned", "prone", "restrained", "stunned",
    "unconscious",
}
KNOWN_CONDITIONS = VALUED_CONDITIONS | UNVALUED_CONDITIONS
#: Death saves and exhaustion are first-class fields rather than list entries, so nothing
#: can hold two disagreeing copies of the numbers that decide a death.
TRACKED_SEPARATELY = {"exhaustion"}
_src(
    "conditions",
    SRD + ", 'Rules Glossary' -> 'Condition' and the fifteen `[Condition]` glossary entries. The "
    "published list is exactly: Blinded, Charmed, Deafened, Exhaustion, Frightened, Grappled, "
    "Incapacitated, Invisible, Paralyzed, Petrified, Poisoned, Prone, Restrained, Stunned, "
    "Unconscious. \"A condition doesn't stack with itself ... The Exhaustion condition is an "
    "exception to that rule\", which is why Exhaustion is the single valued condition here "
    "against Pathfinder's twelve. The full text of each is quoted in "
    "`system/dnd5e/12-rules-quick-reference.md`.",
)

EXHAUSTION_MAX = 6
EXHAUSTION_PER_LEVEL = {"d20_penalty": -2, "speed_feet": -5}
_src(
    "exhaustion",
    SRD + ", 'Rules Glossary' -> 'Exhaustion [Condition]': \"Each time you receive it, you gain 1 "
    "Exhaustion level. You die if your Exhaustion level is 6.\" \"When you make a D20 Test, the "
    "roll is reduced by 2 times your Exhaustion level.\" \"Your Speed is reduced by a number of "
    "feet equal to 5 times your Exhaustion level.\" \"Finishing a Long Rest removes 1 of your "
    "Exhaustion levels.\" This is the 2024 rewrite: one scaling penalty to every D20 Test, not "
    "the 2014 six-row table of distinct effects.",
)


def exhaustion_effect(level: int) -> dict[str, Any]:
    lvl = max(0, int(level))
    return {
        "level": lvl,
        "d20_penalty": -2 * lvl,
        "speed_penalty_feet": -5 * lvl,
        "dead": lvl >= EXHAUSTION_MAX,
    }


# --------------------------------------------------------------------------------------
# Resolution
# --------------------------------------------------------------------------------------

ATTACK_SCALE = ("miss", "hit", "critical hit")
ATTACK_LABELS = ("MISS", "HIT", "CRITICAL HIT")
TEST_SCALE = ("failure", "success")
TEST_LABELS = ("FAILURE", "SUCCESS")

OUTCOME_SCALES = {
    "attack": (ATTACK_SCALE, ATTACK_LABELS),
    "check": (TEST_SCALE, TEST_LABELS),
    "save": (TEST_SCALE, TEST_LABELS),
    "flat": (TEST_SCALE, TEST_LABELS),
    "death-save": (TEST_SCALE, TEST_LABELS),
}

DEATH_SAVE_DC = 10
DEATH_SAVES_TO_RESOLVE = 3
_src(
    "death_saves",
    SRD + ", 'Playing the Game' -> 'Damage and Healing' -> 'Death Saving Throws': \"Whenever you "
    "start your turn with 0 Hit Points, you must make a Death Saving Throw ... Roll 1d20. If the "
    "roll is 10 or higher, you succeed.\" \"On your third success, you become Stable. On your "
    "third failure, you die.\" \"When you roll a 1 on the d20 for a Death Saving Throw, you suffer "
    "two failures. If you roll a 20 on the d20, you regain 1 Hit Point.\" \"If you take any damage "
    "while you have 0 Hit Points, you suffer a Death Saving Throw failure. If the damage is from a "
    "Critical Hit, you suffer two failures instead. If the damage equals or exceeds your Hit Point "
    "maximum, you die.\" The save is not tied to an ability score, so it takes no modifier. "
    "Successes and failures reset \"when you regain any Hit Points or become Stable\". Stabilising "
    "is a DC 10 Wisdom (Medicine) check, and \"a Stable creature that isn't healed regains 1 Hit "
    "Point after 1d4 hours\".",
)


def resolve(total: int, dc: int, natural: int | None = None, *, kind: str = "check") -> dict[str, Any]:
    """One d20 test against one target number, as the shared tools consume it.

    `kind` matters here in a way it does not in Pathfinder: the natural-20 and natural-1
    rules apply to attack rolls ONLY. A 20 on a Wisdom save is a 20 and nothing more.
    """
    k = str(kind).lower()
    scale, labels = OUTCOME_SCALES.get(k, (TEST_SCALE, TEST_LABELS))
    total, dc = int(total), int(dc)
    forced: str | None = None

    if k == "attack":
        if natural == 20:
            idx, forced = 2, "natural 20: hits regardless of AC, and is a Critical Hit"
        elif natural == 1:
            idx, forced = 0, "natural 1: misses regardless of AC"
        else:
            idx = 1 if total >= dc else 0
    elif k == "death-save":
        if natural == 20:
            idx, forced = 1, "natural 20: regain 1 Hit Point and stop making Death Saves"
        elif natural == 1:
            idx, forced = 0, "natural 1: counts as TWO failures"
        else:
            idx = 1 if total >= DEATH_SAVE_DC else 0
    else:
        # Checks and saves: no natural-20 or natural-1 rule in the 2024 rules.
        idx = 1 if total >= dc else 0

    out: dict[str, Any] = {
        "system": SYSTEM_ID,
        "kind": k,
        "total": total,
        "dc": dc,
        "natural": natural,
        "margin": total - dc,
        "index": idx,
        "unadjusted_index": idx,
        "shift": 0,
        "outcome": scale[idx],
        "label": labels[idx],
        "unadjusted_outcome": scale[idx],
        "scale": list(scale),
        "labels": list(labels),
        "success": idx >= (2 if k == "attack" else 1),
        "critical": k == "attack" and idx == 2,
        "forced": forced,
    }
    if k == "death-save":
        out["failures_incurred"] = 2 if natural == 1 else (0 if idx else 1)
        out["successes_incurred"] = 1 if idx else 0
        out["heals_to_one"] = natural == 20
    return out


# --------------------------------------------------------------------------------------
# A blank character
# --------------------------------------------------------------------------------------

ABILITIES = ("str", "dex", "con", "int", "wis", "cha")


def blank_character_fields(level: int = 1) -> dict[str, Any]:
    """The D&D-shaped half of a character in state.json."""
    return {
        "ac": 10,
        "abilities": {a: 10 for a in ABILITIES},
        "saves": {a: 0 for a in ABILITIES},
        "save_proficiencies": [],
        "skills": {},
        "proficiency_bonus": proficiency_bonus(level),
        "passive_perception": 10,
        "initiative_mod": 0,
        "speed": 30,
        "size": "Medium",
        "strength": 10,
        "hit_dice": {"die": 8, "max": int(level), "used": 0},
        "death_saves": {"successes": 0, "failures": 0, "stable": False},
        "exhaustion": 0,
        "heroic_inspiration": False,
        "concentration": None,
        "spell_slots": {},
        "attunement": {"max": ATTUNEMENT_LIMIT, "items": []},
    }


RESOURCES = ("heroic_inspiration", "hit_dice", "spell_slots", "death_saves", "exhaustion",
             "concentration", "attunement")
RESOURCE_HINTS = {
    "hero": "D&D 2024 has Heroic Inspiration, not Hero Points — use `inspiration give` / `inspiration spend`.",
    "focus": "D&D 2024 has no Focus Points — spell slots and Short Rest recharges do that work.",
    "dying": "D&D 2024 has Death Saving Throws, not a dying value — use `death-save` and `roll.py death-save`.",
    "wounded": "D&D 2024 has no wounded condition — death save counters reset on regaining any HP.",
    "doomed": "D&D 2024 has no doomed condition — Exhaustion 6 is the equivalent death clock.",
    "refocus": "D&D 2024 has no Refocus — a Short Rest and Hit Dice are the mid-day recovery.",
    "recovery": "D&D 2024 has Death Saving Throws, not recovery checks — use `death-save roll`.",
    "daily": "D&D 2024's equivalent is `long-rest`, and `short-rest` for the mid-day one.",
    "daily-prep": "D&D 2024's equivalent is `long-rest`, and `short-rest` for the mid-day one.",
    "bulk": "D&D 2024 measures weight in pounds, not Bulk — use `--weight`.",
}


# --------------------------------------------------------------------------------------
# Dropping to 0 HP
# --------------------------------------------------------------------------------------


def on_zero_hp(pc: dict[str, Any], *, from_crit: bool = False, overflow: int = 0,
               already_down: bool = False) -> dict[str, Any]:
    """What D&D 2024 does at 0 HP: unconscious and making Death Saves — or dead outright.

    Returns the instruction for state.py rather than mutating. Source: see the
    `death_saves` and `instant_death` entries in `sources`.
    """
    hp_max = int((pc.get("hp") or {}).get("max", 0))
    if hp_max and int(overflow) >= hp_max:
        return {
            "action": "dead",
            "reason": f"massive damage: {overflow} damage past 0 HP meets the {hp_max} HP maximum",
            "notes": [
                f"reduced to 0 HP with {overflow} damage remaining, which equals or exceeds the "
                f"{hp_max} HP maximum — instant death"
            ],
        }
    if already_down:
        fails = 2 if from_crit else 1
        return {
            "action": "death-save-failures",
            "value": fails,
            "reason": "took damage at 0 HP" + (" from a critical hit" if from_crit else ""),
            "notes": [f"damage at 0 HP — {fails} Death Saving Throw failure"
                      + ("s" if fails > 1 else "")],
        }
    return {
        "action": "down",
        "reason": "reduced to 0 HP",
        "notes": ["reduced to 0 HP — unconscious, and making Death Saving Throws from the "
                  "start of their next turn"],
    }


def on_healed_from_zero(pc: dict[str, Any]) -> dict[str, Any]:
    """Any healing from 0 HP ends unconsciousness and resets the death save counters."""
    ds = pc.get("death_saves") or {}
    if int(ds.get("successes", 0)) or int(ds.get("failures", 0)) or ds.get("stable"):
        return {"action": "reset-death-saves", "reason": "regained Hit Points"}
    return {"action": "none"}


_src(
    "instant_death",
    SRD + ", 'Playing the Game' -> 'Damage and Healing' -> 'Dropping to 0 Hit Points' -> 'Instant "
    "Death': \"When damage reduces a character to 0 Hit Points and damage remains, the character "
    "dies if the remainder equals or exceeds their Hit Point maximum.\" Also: \"A monster dies the "
    "instant it drops to 0 Hit Points\" (the GM may waive this per monster), and \"a creature dies "
    "if its Hit Point maximum reaches 0\". The published worked example is a 12 HP maximum "
    "character on 6 HP taking 18 damage: 12 damage remains, which equals the maximum, so they die.",
)


# --------------------------------------------------------------------------------------
# Rest and the daily reset
# --------------------------------------------------------------------------------------

SHORT_REST_HOURS = 1
LONG_REST_HOURS = 8
_src(
    "rests",
    SRD + ", 'Rules Glossary' -> 'Short Rest' and 'Long Rest'. A Short Rest is one hour and lets "
    "you spend Hit Point Dice to regain HP (roll the die and add your Constitution modifier, "
    "minimum 1 HP each). A Long Rest is at least 8 hours, of which at least 6 are sleep and no "
    "more than 2 are light activity; it restores all lost Hit Points AND all spent Hit Point "
    "Dice, restores reduced ability scores and a reduced HP maximum, and removes one Exhaustion "
    "level. \"After you finish a Long Rest, you must wait at least 16 hours before starting "
    "another one.\" Both are interrupted by rolling Initiative, casting a non-cantrip spell, or "
    "taking damage; a Long Rest is also interrupted by an hour of physical exertion, and an "
    "interrupted Short Rest \"confers no benefits\".",
)


def hit_dice_recovered_on_long_rest(total: int, used: int) -> int:
    """All spent Hit Dice come back on a Long Rest in the 2024 rules."""
    return int(used)


def daily_reset(data: dict[str, Any]) -> list[str]:
    """What a Long Rest restores."""
    notes = []
    for _, pc in (data.get("pcs") or {}).items():
        for _, entry in pc.get("spell_slots", {}).items():
            entry["used"] = 0
        hd = pc.setdefault("hit_dice", {"die": 8, "max": int(pc.get("level", 1)), "used": 0})
        recovered = int(hd.get("used", 0))
        hd["used"] = 0
        hp = pc.get("hp") or {}
        if int(hp.get("max", 0)):
            hp["current"] = int(hp["max"])
        hp["temp"] = 0  # temporary HP last only until a Long Rest ends
        exh = int(pc.get("exhaustion", 0))
        if exh > 0:
            pc["exhaustion"] = exh - 1
        pc["concentration"] = None
        pc["death_saves"] = {"successes": 0, "failures": 0, "stable": False}
        bits = [f"HP {hp.get('current', 0)}/{hp.get('max', 0)}", "slots restored"]
        if recovered:
            bits.append(f"{recovered} Hit Dice back")
        if exh > 0:
            bits.append(f"Exhaustion {exh} → {pc['exhaustion']}")
        notes.append(f"{pc['name']}: " + ", ".join(bits))
    notes.append(
        "Temporary HP ended with the rest. Heroic Inspiration is not granted by resting — the GM "
        "awards it; a Human character starts each day with it."
    )
    return notes


# --------------------------------------------------------------------------------------
# Travel
# --------------------------------------------------------------------------------------

TRAVEL_HOURS_PER_DAY = 8
TRAVEL_PACES: dict[str, dict[str, Any]] = {
    "fast": {"feet_per_minute": 400, "miles_per_hour": 4, "miles_per_day": 30,
             "effect": "Disadvantage on Wisdom (Perception or Survival) and Dexterity (Stealth) checks"},
    "normal": {"feet_per_minute": 300, "miles_per_hour": 3, "miles_per_day": 24,
               "effect": "Disadvantage on Dexterity (Stealth) checks"},
    "slow": {"feet_per_minute": 200, "miles_per_hour": 2, "miles_per_day": 18,
             "effect": "Advantage on Wisdom (Perception or Survival) checks"},
}
_src(
    "travel_pace",
    SRD + ", 'Playing the Game' -> 'Exploration' -> 'Travel Pace', the Travel Pace table: Fast 400 "
    "feet/minute, 4 miles/hour, 30 miles/day; Normal 300, 3, 24; Slow 200, 2, 18. The per-pace "
    "effects are the three statements that follow the table, quoted. The 8-hour travel day is "
    "implied by the table (3 mph x 8 = 24 miles) and stated in 'Gameplay Toolbox' -> 'Travel "
    "Pace' -> 'Extended Travel': travel beyond 8 hours a day risks Exhaustion on a Constitution "
    "save at \"DC 10 plus 1 for each hour past 8 hours\". Mounts double the distance for one hour, "
    "after which they need a rest.",
)

TRAVEL_TERRAIN: dict[str, dict[str, Any]] = {
    "arctic": {"max_pace": "fast", "encounter_distance": "6d6 x 10 feet", "forage_dc": 20, "navigate_dc": 10, "search_dc": 10},
    "coastal": {"max_pace": "normal", "encounter_distance": "2d10 x 10 feet", "forage_dc": 10, "navigate_dc": 5, "search_dc": 15},
    "desert": {"max_pace": "normal", "encounter_distance": "6d6 x 10 feet", "forage_dc": 20, "navigate_dc": 10, "search_dc": 10},
    "forest": {"max_pace": "normal", "encounter_distance": "2d8 x 10 feet", "forage_dc": 10, "navigate_dc": 15, "search_dc": 15},
    "grassland": {"max_pace": "fast", "encounter_distance": "6d6 x 10 feet", "forage_dc": 15, "navigate_dc": 5, "search_dc": 15},
    "hill": {"max_pace": "normal", "encounter_distance": "2d10 x 10 feet", "forage_dc": 15, "navigate_dc": 10, "search_dc": 15},
    "mountain": {"max_pace": "slow", "encounter_distance": "4d10 x 10 feet", "forage_dc": 20, "navigate_dc": 15, "search_dc": 20},
    "swamp": {"max_pace": "slow", "encounter_distance": "2d8 x 10 feet", "forage_dc": 10, "navigate_dc": 15, "search_dc": 20},
    "underdark": {"max_pace": "normal", "encounter_distance": "2d6 x 10 feet", "forage_dc": 20, "navigate_dc": 10, "search_dc": 20},
    "urban": {"max_pace": "normal", "encounter_distance": "2d6 x 10 feet", "forage_dc": 20, "navigate_dc": 15, "search_dc": 15},
}
_src(
    "travel_terrain",
    SRD + ", 'Gameplay Toolbox' -> 'Travel Pace', the Travel Terrain table, read row by row for "
    "all ten terrains (maximum pace, encounter distance, foraging DC, navigation DC, search DC). "
    "Arctic's Fast is published with an asterisk. \"The presence of a good road increases the "
    "group's maximum pace by one step\", and \"the group must move at a Slow pace if any group "
    "member's Speed is reduced to half or less of normal.\"",
)

EXTENDED_TRAVEL_DC = "10 plus 1 for each hour past 8"


def travel_distance(pace: str, hours: float = TRAVEL_HOURS_PER_DAY) -> dict[str, Any]:
    key = str(pace).strip().lower()
    if key not in TRAVEL_PACES:
        raise ValueError(f"{pace!r} is not a travel pace ({', '.join(TRAVEL_PACES)})")
    p = TRAVEL_PACES[key]
    return {
        "pace": key,
        "hours": hours,
        "miles": p["miles_per_hour"] * float(hours),
        "miles_per_day": p["miles_per_day"],
        "effect": p["effect"],
    }


# --------------------------------------------------------------------------------------
# Spell slots
# --------------------------------------------------------------------------------------

#: Full-caster slots by class level, slot levels 1-9. Bard, Cleric, Druid, Sorcerer, Wizard.
FULL_CASTER_SLOTS: dict[int, list[int]] = {
    1:  [2, 0, 0, 0, 0, 0, 0, 0, 0],
    2:  [3, 0, 0, 0, 0, 0, 0, 0, 0],
    3:  [4, 2, 0, 0, 0, 0, 0, 0, 0],
    4:  [4, 3, 0, 0, 0, 0, 0, 0, 0],
    5:  [4, 3, 2, 0, 0, 0, 0, 0, 0],
    6:  [4, 3, 3, 0, 0, 0, 0, 0, 0],
    7:  [4, 3, 3, 1, 0, 0, 0, 0, 0],
    8:  [4, 3, 3, 2, 0, 0, 0, 0, 0],
    9:  [4, 3, 3, 3, 1, 0, 0, 0, 0],
    10: [4, 3, 3, 3, 2, 0, 0, 0, 0],
    11: [4, 3, 3, 3, 2, 1, 0, 0, 0],
    12: [4, 3, 3, 3, 2, 1, 0, 0, 0],
    13: [4, 3, 3, 3, 2, 1, 1, 0, 0],
    14: [4, 3, 3, 3, 2, 1, 1, 0, 0],
    15: [4, 3, 3, 3, 2, 1, 1, 1, 0],
    16: [4, 3, 3, 3, 2, 1, 1, 1, 0],
    17: [4, 3, 3, 3, 2, 1, 1, 1, 1],
    18: [4, 3, 3, 3, 3, 1, 1, 1, 1],
    19: [4, 3, 3, 3, 3, 2, 1, 1, 1],
    20: [4, 3, 3, 3, 3, 2, 2, 1, 1],
}
_src(
    "spell_slots_full_caster",
    SRD + ", 'Classes' -> 'Wizard', the Wizard Features table's Spell Slots per Spell Level "
    "columns, read row by row for all twenty levels. The Bard, Cleric, Druid and Sorcerer tables "
    "in the same chapter carry the identical progression, which is what makes this one table "
    "serve every full caster. HALF casters (Paladin, Ranger) and the Warlock's Pact Magic are "
    "NOT this table — look those up in their own class tables and record them on the sheet; "
    "`state.py slots` stores whatever is written, so a half caster or a Warlock is recorded "
    "correctly without this table pretending to cover them.",
)


def full_caster_slots(level: int) -> dict[str, int]:
    row = FULL_CASTER_SLOTS.get(int(level))
    if row is None:
        raise ValueError(f"no full-caster slot row for level {level} (the table runs 1 to 20)")
    return {str(i + 1): n for i, n in enumerate(row) if n}


# --------------------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------------------

SHEET_COLUMNS = ("HP", "AC", "Init", "Pass. Perc", "Insp", "Hit Dice", "Exh", "Conditions")


def sheet_lines(pc: dict[str, Any], *, conditions: str = "—") -> list[str]:
    """One row of the party table, in SHEET_COLUMNS order."""
    hp = pc.get("hp", {})
    temp = f" +{hp.get('temp')}t" if hp.get("temp") else ""
    hd = pc.get("hit_dice") or {}
    hd_max, hd_used = int(hd.get("max", 0)), int(hd.get("used", 0))
    hd_txt = f"{hd_max - hd_used}/{hd_max}d{hd.get('die', 8)}" if hd_max else "—"
    return [
        f"{hp.get('current', 0)}/{hp.get('max', 0)}{temp}",
        str(pc.get("ac", 0)),
        f"{int(pc.get('initiative_mod', 0)):+d}",
        str(pc.get("passive_perception", 10)),
        "yes" if pc.get("heroic_inspiration") else "—",
        hd_txt,
        str(pc.get("exhaustion", 0)) if int(pc.get("exhaustion", 0)) else "—",
        conditions,
    ]


def status_lines(pc: dict[str, Any]) -> list[str]:
    """The ruleset-specific resource lines for `status`, below HP and conditions."""
    out: list[str] = []
    hp = pc.get("hp") or {}
    ds = pc.get("death_saves") or {}
    if int(hp.get("current", 1)) == 0:
        if ds.get("stable"):
            out.append("at 0 HP — STABLE (no Death Saves; regains 1 HP after 1d4 hours if unhealed)")
        else:
            out.append(
                f"at 0 HP — Death Saves {ds.get('successes', 0)}/3 successes, "
                f"{ds.get('failures', 0)}/3 failures"
            )
    hd = pc.get("hit_dice") or {}
    if int(hd.get("max", 0)):
        out.append(f"Hit Dice {int(hd['max']) - int(hd.get('used', 0))}/{hd['max']}d{hd.get('die', 8)}")
    out.append("Heroic Inspiration: " + ("held" if pc.get("heroic_inspiration") else "none"))
    if int(pc.get("exhaustion", 0)):
        e = exhaustion_effect(pc["exhaustion"])
        out.append(f"Exhaustion {e['level']} — {e['d20_penalty']} to every D20 Test, "
                   f"{e['speed_penalty_feet']} ft Speed")
    conc = pc.get("concentration")
    if conc:
        name = conc.get("on") if isinstance(conc, dict) else conc
        out.append(f"Concentrating on {name}")
    att = pc.get("attunement") or {}
    items = att.get("items") or []
    if items or att.get("max") not in (None, ATTUNEMENT_LIMIT):
        out.append(f"Attuned {len(items)}/{att.get('max', ATTUNEMENT_LIMIT)}"
                   + (f" — {', '.join(items)}" if items else ""))
    slots = pc.get("spell_slots") or {}
    if slots:
        bits = [f"level {r}: {int(e.get('max', 0)) - int(e.get('used', 0))}/{e.get('max', 0)}"
                for r, e in sorted(slots.items(), key=lambda kv: int(kv[0]))]
        out.append("Slots — " + "; ".join(bits))
    return out


def tracked_condition_flags(pc: dict[str, Any]) -> list[str]:
    """The flags that belong in the conditions column but live in their own fields."""
    out = ["**DEAD**"] if pc.get("dead") else []
    if int(pc.get("exhaustion", 0)):
        out.append(f"**exhaustion {pc['exhaustion']}**")
    hp = pc.get("hp") or {}
    ds = pc.get("death_saves") or {}
    # A dead character is not still saving; the table already shows DEAD.
    if int(hp.get("current", 1)) == 0 and not pc.get("dead"):
        if ds.get("stable"):
            out.append("**stable at 0 HP**")
        else:
            out.append(f"**death saves {ds.get('successes', 0)}✓/{ds.get('failures', 0)}✗**")
    return out


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------


def _print_table(rows: Sequence[dict[str, Any]], cols: Sequence[str]) -> None:
    widths = {c: max(len(c), *(len(str(r.get(c, ""))) for r in rows)) if rows else len(c) for c in cols}
    print("  ".join(c.ljust(widths[c]) for c in cols))
    print("  ".join("-" * widths[c] for c in cols))
    for r in rows:
        print("  ".join(str(r.get(c, "")).ljust(widths[c]) for c in cols))


def cmd_encounter(args: argparse.Namespace) -> int:
    size, level = args.party_size, args.party_level
    budgets = encounter_budgets(size, level)
    print(f"Party: {size} character(s) at level {level}   ({tier_name(level)})")
    print(f"Source: SRD 5.2 XP Budget per Character; {XP_BUDGET_PER_CHARACTER[level]} per character\n")
    rows = [
        {"difficulty": t, "per character": XP_BUDGET_PER_CHARACTER[level][t], "party budget": budgets[t],
         "means": DIFFICULTY_MEANING[t][:58] + "…"}
        for t in THREATS
    ]
    _print_table(rows, ["difficulty", "per character", "party budget", "means"])

    if args.threat:
        budget = budgets[args.threat]
        print(f"\n{args.threat.capitalize()}-difficulty budget: {budget} XP")
        print(f"  {DIFFICULTY_MEANING[args.threat]}")
        print("\n  Creatures that fit inside it, one kind at a time:")
        fits = []
        for cr, xp in sorted(XP_BY_CR.items()):
            if xp <= 0:
                continue
            n = budget // xp
            if n >= 1 and n <= 12:
                fits.append({"CR": format_cr(cr), "XP each": xp, "how many fit": n,
                             "spent": n * xp, "left": budget - n * xp})
        if fits:
            _print_table(fits[-10:], ["CR", "XP each", "how many fit", "spent", "left"])
        print(f"\n  Action-economy caution: more than {2 * size} creatures against {size} "
              f"character(s) is past the published guideline.")
        print(f"  {MANY_CREATURES_ADVICE}")
        print("\n  There is NO encounter multiplier in the 2024 rules: spend the budget at face")
        print("  value. Spend as much as you can without going over; leftovers are fine.")
    if args.cr:
        total = 0
        parts = []
        for spec in args.cr:
            if "x" in spec.lower():
                n_s, cr_s = spec.lower().split("x", 1)
                n, cr_s = int(n_s or 1), cr_s
            else:
                n, cr_s = 1, spec
            xp = creature_xp(cr_s)
            total += n * xp
            parts.append(f"{n} x CR {format_cr(parse_cr(cr_s))} ({xp} XP each)")
        print(f"\nBuilt encounter: {', '.join(parts)}")
        print(f"  total {total} XP → rated **{rate_encounter(total, size, level)}** "
              f"for {size} character(s) at level {level}")
        print(f"  XP awarded on clearing it: {xp_award(total, size)}")
    return 0


def cmd_treasure(args: argparse.Namespace) -> int:
    t = treasure_for(args.level, args.party_size)
    print(f"Level {args.level}, party of {args.party_size} — {t['band']}")
    print("\n⚠ THIS FRAMEWORK'S OWN CONVENTION, not a published table. See the note below.\n")
    print(f"  Per character: {t['gp_per_character']} gp"
          + (f" plus {t['bonus_roll_per_character']}" if t["bonus_roll_per_character"] else ""))
    print(f"  Whole party:   {t['gp_party']} gp")
    if t["magic_items_per_character"]:
        print("  Magic items per character: " + ", ".join(
            f"{n} {r}" for r, n in t["magic_items_per_character"].items()))
        print("  Magic items for the party: " + ", ".join(
            f"{n} {r}" for r, n in t["magic_items_party"].items()))
    print("\n  Rarity values: " + ", ".join(
        f"{r} {v} gp" if v else f"{r} priceless" for r, v in MAGIC_ITEM_VALUES.items()))
    print(f"\n  {t['note']}")
    return 0


def cmd_dc(args: argparse.Namespace) -> int:
    if args.difficulty:
        print(f"{args.difficulty}: DC {task_dc(args.difficulty)}")
        return 0
    rows = [{"task difficulty": k, "DC": v} for k, v in DIFFICULTY_DCS.items()]
    _print_table(rows, ["task difficulty", "DC"])
    print("\nThere is no DC-by-level table in this game: a hard task is DC 20 at level 1 and")
    print("DC 20 at level 20. Scale the opposition, not the lock.")
    if args.damage is not None:
        print(f"\nConcentration save after {args.damage} damage: DC {concentration_dc(args.damage)}")
    return 0


def cmd_cr(args: argparse.Namespace) -> int:
    if args.cr:
        for spec in args.cr:
            cr = parse_cr(spec)
            print(f"CR {format_cr(cr)}: {XP_BY_CR[cr]} XP, Proficiency Bonus "
                  f"{proficiency_bonus(float(cr)):+d}")
        return 0
    rows = [{"CR": format_cr(c), "XP": XP_BY_CR[c], "prof": f"{proficiency_bonus(float(c)):+d}"}
            for c in sorted(XP_BY_CR)]
    _print_table(rows, ["CR", "XP", "prof"])
    return 0


def cmd_settlement(args: argparse.Namespace) -> int:
    info = settlement_availability(args.settlement)
    print(f"{info['settlement'].capitalize()} — magic items purchasable: "
          + ", ".join(info["purchasable"]))
    print(f"  not available here: {', '.join(info['unavailable'])}")
    for r, v in info["values"].items():
        print(f"  {r}: {v} gp" if v else f"  {r}: priceless")
    print(f"\n  {info['note']}")
    print("  (The settlement buckets are this framework's convention; the rarity-to-place")
    print("   guidance behind them is published. See `sources` → settlement_availability.)")
    return 0


def cmd_travel(args: argparse.Namespace) -> int:
    rows = [{"pace": k, "ft/min": v["feet_per_minute"], "mi/hr": v["miles_per_hour"],
             "mi/day": v["miles_per_day"], "effect": v["effect"]}
            for k, v in TRAVEL_PACES.items()]
    _print_table(rows, ["pace", "ft/min", "mi/hr", "mi/day", "effect"])
    print(f"\n{TRAVEL_HOURS_PER_DAY}-hour travel day. Beyond that, a Constitution save each extra")
    print(f"hour at DC {EXTENDED_TRAVEL_DC} or gain 1 Exhaustion level.")
    if args.terrain:
        key = args.terrain.lower()
        if key not in TRAVEL_TERRAIN:
            print(f"\n{args.terrain!r} is not a published terrain "
                  f"({', '.join(TRAVEL_TERRAIN)})")
            return 1
        t = TRAVEL_TERRAIN[key]
        print(f"\n{key.capitalize()}: maximum pace {t['max_pace']}, encounter distance "
              f"{t['encounter_distance']}")
        print(f"  forage DC {t['forage_dc']}, navigate DC {t['navigate_dc']}, "
              f"search DC {t['search_dc']}")
    else:
        print()
        _print_table(
            [{"terrain": k, "max pace": v["max_pace"], "encounter dist": v["encounter_distance"],
              "forage": v["forage_dc"], "navigate": v["navigate_dc"], "search": v["search_dc"]}
             for k, v in TRAVEL_TERRAIN.items()],
            ["terrain", "max pace", "encounter dist", "forage", "navigate", "search"])
    return 0


def cmd_advancement(args: argparse.Namespace) -> int:
    rows = []
    for lvl in range(1, 21):
        rows.append({
            "level": lvl,
            "XP (cumulative)": f"{CHARACTER_ADVANCEMENT[lvl]:,}",
            "prof": f"{proficiency_bonus(lvl):+d}",
            "tier": tier_name(lvl),
            "scope band": rules.scope_band(SYSTEM_ID, lvl),
        })
    _print_table(rows, ["level", "XP (cumulative)", "prof", "tier", "scope band"])
    print("\nXP is CUMULATIVE and never reset — unlike Pathfinder's flat 1,000 per level.")
    if args.xp is not None:
        print(f"\n{args.xp:,} XP is level {level_for_xp(args.xp)}.")
    return 0


def cmd_carry(args: argparse.Namespace) -> int:
    cap = carry_capacity(args.strength, args.size)
    print(f"Strength {args.strength}, size {args.size}:")
    print(f"  carry           {cap['carry']:.0f} lb")
    print(f"  drag/lift/push  {cap['drag_lift_push']:.0f} lb  (Speed capped at 5 ft while doing so)")
    print(f"\n  {COINS_PER_POUND} coins weigh a pound.")
    print("  SRD 5.2 defines no intermediate 'encumbered' band — you carry freely up to the")
    print("  maximum. (Pathfinder does have one; that difference is deliberate here.)")
    return 0


def cmd_tables(args: argparse.Namespace) -> int:
    print("# D&D 2024 (5.5e) tables in this framework\n")
    print("## Typical Difficulty Classes")
    _print_table([{"task": k, "DC": v} for k, v in DIFFICULTY_DCS.items()], ["task", "DC"])
    print("\n## Proficiency Bonus")
    _print_table([{"level or CR": f"{lo}-{hi}", "bonus": f"+{b}"}
                  for lo, hi, b in PROFICIENCY_BONUS_BANDS], ["level or CR", "bonus"])
    print("\n## Character Advancement (cumulative XP)")
    _print_table([{"level": l, "XP": f"{x:,}"} for l, x in CHARACTER_ADVANCEMENT.items()],
                 ["level", "XP"])
    print("\n## XP by Challenge Rating")
    _print_table([{"CR": format_cr(c), "XP": f"{XP_BY_CR[c]:,}"} for c in sorted(XP_BY_CR)],
                 ["CR", "XP"])
    print("\n## XP Budget per Character")
    _print_table([{"level": l, **{t: f"{v[t]:,}" for t in THREATS}}
                  for l, v in XP_BUDGET_PER_CHARACTER.items()], ["level", *THREATS])
    print("\n## Magic Item Rarities and Values")
    _print_table([{"rarity": r, "value": f"{v:,} gp" if v else "priceless",
                   "where": MAGIC_ITEM_AVAILABILITY[r]} for r, v in MAGIC_ITEM_VALUES.items()],
                 ["rarity", "value", "where"])
    print("\n## Carrying Capacity")
    _print_table([{"size": s, "carry": f"Str x {c}", "drag/lift/push": f"Str x {d}"}
                  for s, (c, d) in CARRY_MULTIPLIERS.items()], ["size", "carry", "drag/lift/push"])
    print("\n## Travel Pace")
    _print_table([{"pace": k, "ft/min": v["feet_per_minute"], "mi/hr": v["miles_per_hour"],
                   "mi/day": v["miles_per_day"]} for k, v in TRAVEL_PACES.items()],
                 ["pace", "ft/min", "mi/hr", "mi/day"])
    print("\n## Full-caster spell slots")
    _print_table([{"level": l, **{str(i + 1): (n or "—") for i, n in enumerate(r)}}
                  for l, r in FULL_CASTER_SLOTS.items()],
                 ["level", *[str(i) for i in range(1, 10)]])
    print("\n## Coins")
    _print_table([{"coin": c, "in cp": COIN_IN_CP[c]} for c in COIN_ORDER], ["coin", "in cp"])
    print("\n## Lifestyle expenses")
    _print_table([{"lifestyle": k, "cost": v["label"]} for k, v in LIFESTYLE_EXPENSES.items()],
                 ["lifestyle", "cost"])
    print("\nRun `python3 tools/dnd5e.py sources` for where every one of these came from.")
    return 0


def cmd_sources(args: argparse.Namespace) -> int:
    for key in sorted(SOURCES):
        flags = []
        if key in UNVERIFIED_TABLES:
            flags.append("UNVERIFIED")
        if key in CONVENTION_TABLES:
            flags.append("FRAMEWORK CONVENTION")
        tag = f"[{' / '.join(flags)}]" if flags else "[verified]"
        print(f"{tag} {key}")
        print(f"    {SOURCES[key]}\n")
    total = len(SOURCES)
    print(f"{len(UNVERIFIED_TABLES)} of {total} tables are unverified.")
    print(f"{len(CONVENTION_TABLES)} of {total} are this framework's own convention rather than "
          f"a published rule:")
    for k in CONVENTION_TABLES:
        print(f"    - {k}")
    print("\nPrimary source: " + SRD)
    print("Cross-checked against: " + FOUNDRY)
    print("\nSRD 5.2 is licensed CC-BY-4.0; see LICENSE_NOTES.md for the required attribution.")
    return 0


def cmd_resolve(args: argparse.Namespace) -> int:
    out = resolve(args.total, args.dc, args.natural, kind=args.kind)
    print(json.dumps(out, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dnd5e.py",
        description="D&D 2024 (5.5e) rules tables, each carrying the source it was read from.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("encounter", help="XP budgets and what fits inside them")
    e.add_argument("--party-level", type=int, required=True)
    e.add_argument("--party-size", type=int, default=4)
    e.add_argument("--threat", choices=THREATS)
    e.add_argument("--cr", nargs="*", help="creatures to price, e.g. 2x1/4 1 3")

    t = sub.add_parser("treasure", help="expected wealth by level (framework convention)")
    t.add_argument("--level", type=int, required=True)
    t.add_argument("--party-size", type=int, default=4)

    d = sub.add_parser("dc", help="task difficulty classes")
    d.add_argument("--difficulty")
    d.add_argument("--damage", type=int, help="also show the Concentration save DC for this damage")

    c = sub.add_parser("cr", help="XP and proficiency bonus by Challenge Rating")
    c.add_argument("--cr", nargs="*")

    s = sub.add_parser("settlement", help="which magic item rarities a settlement sells")
    s.add_argument("settlement")

    tr = sub.add_parser("travel", help="travel paces and terrain")
    tr.add_argument("--terrain")

    a = sub.add_parser("advancement", help="XP thresholds, proficiency and tiers by level")
    a.add_argument("--xp", type=int, help="also report what level this XP total is")

    ca = sub.add_parser("carry", help="carrying capacity")
    ca.add_argument("--strength", type=int, required=True)
    ca.add_argument("--size", default="medium")

    sub.add_parser("tables", help="print every table")
    sub.add_parser("sources", help="the provenance of every table")

    r = sub.add_parser("resolve", help="resolve one d20 test (what roll.py uses)")
    r.add_argument("--total", type=int, required=True)
    r.add_argument("--dc", type=int, required=True)
    r.add_argument("--natural", type=int)
    r.add_argument("--kind", default="check",
                   choices=["check", "save", "attack", "flat", "death-save"])
    return p


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    fns = {
        "encounter": cmd_encounter, "treasure": cmd_treasure, "dc": cmd_dc, "cr": cmd_cr,
        "settlement": cmd_settlement, "travel": cmd_travel, "advancement": cmd_advancement,
        "carry": cmd_carry, "tables": cmd_tables, "sources": cmd_sources, "resolve": cmd_resolve,
    }
    try:
        return fns[args.cmd](args)
    except (ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


# --------------------------------------------------------------------------------------
# The action economy, for the encounter tracker
# --------------------------------------------------------------------------------------

ACTION_ECONOMY = {
    "kind": "slots",
    "actions_per_turn": 1,
    "has_map": False,
    "has_bonus_action": True,
    "tracks_movement_separately": True,
    "summary": "One action a turn, plus a Bonus Action only when something grants one, plus one "
               "Reaction, plus movement up to your Speed and one free object interaction. There "
               "is no multiple attack penalty: extra attacks come from the Attack action itself.",
}
_src(
    "action_economy",
    SRD + ", 'Playing the Game' -> 'Combat' -> 'Your Turn': \"On your turn, you can move a "
    "distance up to your Speed and take one action.\" Movement is its own allowance in feet rather "
    "than costing the action, which is the structural difference from Pathfinder's three-action "
    "turn. \"You can interact with one object or feature of the environment for free, during "
    "either your move or action\"; a second interaction takes the Utilize action. Bonus Actions "
    "are from 'Rules Glossary' -> 'Bonus Action': \"A Bonus Action is a special action that you "
    "can take on the same turn that you take an action\", and you only have one when a feature "
    "grants it. Reactions are one per round, from 'Rules Glossary' -> 'Reaction'. There is no "
    "multiple attack penalty anywhere in the rules: the Extra Attack feature and the Attack "
    "action's own text govern how many attacks a turn allows.",
)

ENCOUNTER_COLUMNS = (("act", 4), ("bns", 4), ("move", 7), ("rxn", 4))


def blank_combatant_fields(**kw: Any) -> dict[str, Any]:
    return {
        "actions_remaining": 1,
        "actions_spent": 0,
        # A Bonus Action exists only where a feature grants one, so the tracker starts at
        # zero and `--bonus-action` on `encounter add` turns it on for that combatant.
        "bonus_action_max": int(kw.get("bonus_action", 0) or 0),
        "bonus_action_remaining": int(kw.get("bonus_action", 0) or 0),
        "speed": int(kw.get("speed", 30) or 30),
        "movement_used": 0,
        "object_interaction_used": False,
        "reaction_available": True,
        "reaction_used_for": None,
        "concentrating_on": None,
    }


def reset_turn(c: dict[str, Any]) -> str:
    """Reset a combatant's per-turn resources and describe what they now have."""
    c["actions_remaining"] = 1
    c["actions_spent"] = 0
    c["bonus_action_remaining"] = int(c.get("bonus_action_max", 0) or 0)
    c["movement_used"] = 0
    c["object_interaction_used"] = False
    c["reaction_available"] = True
    c["reaction_used_for"] = None
    speed = int(c.get("speed", 30) or 30)
    bits = ["1 action"]
    if int(c.get("bonus_action_max", 0) or 0):
        bits.append("1 bonus action")
    bits += [f"{speed} ft of movement", "reaction available"]
    return ", ".join(bits)


def combatant_action_cells(c: dict[str, Any]) -> list[str]:
    act = "◆" if int(c.get("actions_remaining", 1)) else "◇"
    bmax = int(c.get("bonus_action_max", 0) or 0)
    if not bmax:
        bns = "—"
    else:
        bns = "◆" if int(c.get("bonus_action_remaining", 0)) else "◇"
    speed = int(c.get("speed", 30) or 30)
    used = int(c.get("movement_used", 0))
    move = f"{max(0, speed - used)}/{speed}ft"
    return [act, bns, move, "yes" if c.get("reaction_available") else "used"]


def spend_action(c: dict[str, Any], kind: str, n: int = 1) -> str:
    """Spend an action, a Bonus Action, or feet of movement."""
    k = str(kind).lower().replace("_", "-")
    if k in ("action", "any"):
        left = int(c.get("actions_remaining", 1)) - n
        if left < 0:
            raise ValueError(
                f"{c['name']} has {c.get('actions_remaining', 1)} action this turn and cannot "
                f"spend {n} — a second action needs a feature that grants one"
            )
        c["actions_remaining"] = left
        c["actions_spent"] = int(c.get("actions_spent", 0)) + n
        return f"action spent ({left} left)"
    if k in ("bonus", "bonus-action"):
        if not int(c.get("bonus_action_max", 0) or 0):
            raise ValueError(
                f"{c['name']} has no Bonus Action this turn. One exists only where a feature "
                f"grants it — add the combatant with --bonus-action if theirs does."
            )
        left = int(c.get("bonus_action_remaining", 0)) - n
        if left < 0:
            raise ValueError(f"{c['name']} has already used their Bonus Action this turn")
        c["bonus_action_remaining"] = left
        return f"bonus action spent ({left} left)"
    if k in ("move", "movement"):
        speed = int(c.get("speed", 30) or 30)
        used = int(c.get("movement_used", 0)) + n
        if used > speed:
            raise ValueError(
                f"{c['name']} has {speed - int(c.get('movement_used', 0))} ft of movement left "
                f"and cannot move {n} ft — take the Dash action for more"
            )
        c["movement_used"] = used
        return f"moved {n} ft ({speed - used} ft left of {speed})"
    if k in ("dash",):
        speed = int(c.get("speed", 30) or 30)
        left = int(c.get("actions_remaining", 1)) - 1
        if left < 0:
            raise ValueError(f"{c['name']} has no action left to Dash with")
        c["actions_remaining"] = left
        c["actions_spent"] = int(c.get("actions_spent", 0)) + 1
        c["speed"] = speed + int(c.get("base_speed", speed) or speed)
        return (f"Dash: action spent for {int(c.get('base_speed', speed) or speed)} ft more "
                f"movement this turn ({c['speed']} ft total)")
    raise ValueError(
        f"{kind!r} is not something a D&D turn spends "
        f"(action, bonus-action, move, dash)"
    )




# --------------------------------------------------------------------------------------
# Dashboard rendering
# --------------------------------------------------------------------------------------


def dashboard_stats(pc: dict[str, Any]) -> list[tuple[str, Any]]:
    """The stat tiles on a character's dashboard card."""
    ab = pc.get("abilities") or {}
    s = pc.get("saves") or {}
    prof = int(pc.get("proficiency_bonus", 2))
    tiles: list[tuple[str, Any]] = [
        ("AC", pc.get("ac", 0)),
        ("Init", f"{int(pc.get('initiative_mod', 0)):+d}"),
        ("Prof", f"{prof:+d}"),
        ("Pass. Perc", pc.get("passive_perception", 10)),
        ("Speed", f"{pc.get('speed', 0)} ft"),
    ]
    # The six saves, where they are recorded. A blank sheet shows none rather than six zeros.
    if any(int(s.get(a, 0)) for a in ABILITIES) or any(int(v) != 10 for v in ab.values()):
        for a in ABILITIES:
            tiles.append((a.upper(), f"{int(s.get(a, 0)):+d}"))
    return tiles


DASHBOARD_RESOURCE_COLUMNS = ("Insp.", "Hit Dice", "Exh.", "Concentrating on", "Attuned", "Spell slots")
SLOT_ABBREV = "L"


def dashboard_resource_cells(pc: dict[str, Any]) -> list[str]:
    hd = pc.get("hit_dice") or {}
    hd_max, hd_used = int(hd.get("max", 0)), int(hd.get("used", 0))
    slots = []
    for lvl in sorted(pc.get("spell_slots") or {}, key=lambda r: int(r)):
        e = (pc["spell_slots"])[lvl]
        left = int(e.get("max", 0)) - int(e.get("used", 0))
        slots.append(f"{SLOT_ABBREV}{lvl}&nbsp;{left}/{e.get('max', 0)}")
    conc = pc.get("concentration")
    conc_name = (conc.get("on") if isinstance(conc, dict) else conc) or ""
    att = pc.get("attunement") or {}
    items = att.get("items") or []
    exh = int(pc.get("exhaustion", 0))
    return [
        "held" if pc.get("heroic_inspiration") else "",
        f"{hd_max - hd_used} / {hd_max}d{hd.get('die', 8)}" if hd_max else "",
        str(exh) if exh else "",
        str(conc_name),
        f"{len(items)} / {att.get('max', ATTUNEMENT_LIMIT)}",
        " &middot; ".join(slots),
    ]


def dashboard_dire_tags(pc: dict[str, Any]) -> list[str]:
    """The things that decide a death, rendered prominently rather than as conditions."""
    out = []
    if pc.get("dead"):
        out.append("DEAD")
        return out
    exh = int(pc.get("exhaustion", 0))
    if exh:
        e = exhaustion_effect(exh)
        out.append(f"EXHAUSTION {exh} ({e['d20_penalty']} to D20 Tests)")
    hp = pc.get("hp") or {}
    ds = pc.get("death_saves") or {}
    if int(hp.get("current", 1)) == 0:
        if ds.get("stable"):
            out.append("STABLE at 0 HP")
        else:
            out.append(f"DEATH SAVES {ds.get('successes', 0)}/3 up, {ds.get('failures', 0)}/3 down")
    return out


if __name__ == "__main__":
    raise SystemExit(main())
