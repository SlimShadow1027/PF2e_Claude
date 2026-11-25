#!/usr/bin/env python3
"""dnd5e.py — the D&D Fifth Edition (2024 rules, SRD 5.2.1) tables as data.

The 5e counterpart of `pf2e.py`. A campaign whose `state.json` says `"system": "dnd5e"` reads
its numbers from here instead of from `pf2e.py`: proficiency bonus, the XP needed to level,
monster XP by Challenge Rating, the per-character encounter XP budget, typical DCs, coins,
conditions, exhaustion, death saves, criticals and rests.

Every table carries a `Source:` line through `_src()`, exactly as `pf2e.py` does.

**Every table in this file is currently UNVERIFIED.** They were written from the SRD 5.2.1
section names cited on each line, but the SRD host (media.dndbeyond.com) could not be reached
from the environment the file was written in, so not one number has yet been read back against
the document. `python3 tools/dnd5e.py sources` says so for each table, and DESIGN_NOTES.md lists
them under "To verify before first play". Do not launder them into confidence: verify, then
flip `verified=False` to `True` one table at a time, citing the page.

Licence: SRD 5.2.1 is CC-BY-4.0. The attribution lives in LICENSE_NOTES.md.

Standard library only.
"""

from __future__ import annotations

import argparse
import re
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

SRD = "SRD 5.2.1 (Wizards of the Coast, CC-BY-4.0)"

SOURCES: dict[str, str] = {}
UNVERIFIED_TABLES: list[str] = []


def _src(key: str, text: str, verified: bool = True) -> str:
    SOURCES[key] = text
    if not verified:
        UNVERIFIED_TABLES.append(key)
    return text


SYSTEM_NAME = "D&D 5e (2024 / SRD 5.2.1)"

# --------------------------------------------------------------------------------------
# Character advancement
# --------------------------------------------------------------------------------------

# XP needed to *reach* each level (index 0 = level 1).
XP_FOR_LEVEL = [
    0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000,
    85000, 100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000,
]
PROFICIENCY_BONUS = [2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6]
_src(
    "advancement",
    f"{SRD}, Character Creation — 'Character Advancement' table (Experience Points and "
    "Proficiency Bonus by level 1-20). Written from the section named; not yet read back.",
    verified=False,
)


def proficiency_bonus(level: int) -> int:
    if not 1 <= level <= 20:
        raise ValueError(f"level {level} is outside 1-20")
    return PROFICIENCY_BONUS[level - 1]


def level_for_xp(xp: int) -> int:
    lvl = 1
    for i, need in enumerate(XP_FOR_LEVEL):
        if xp >= need:
            lvl = i + 1
    return lvl


def xp_to_next(xp: int) -> int | None:
    lvl = level_for_xp(xp)
    if lvl >= 20:
        return None
    return XP_FOR_LEVEL[lvl] - xp


# --------------------------------------------------------------------------------------
# Encounter building
# --------------------------------------------------------------------------------------

# XP budget *per character*, by character level: (Low, Moderate, High).
XP_BUDGET_PER_CHARACTER = {
    1: (50, 75, 100),
    2: (100, 150, 200),
    3: (150, 225, 400),
    4: (250, 375, 500),
    5: (500, 750, 1100),
    6: (600, 1000, 1400),
    7: (750, 1300, 1700),
    8: (1000, 1700, 2100),
    9: (1300, 2000, 2600),
    10: (1600, 2300, 3100),
    11: (1900, 2900, 4100),
    12: (2200, 3700, 4700),
    13: (2600, 4200, 5400),
    14: (2900, 4900, 6200),
    15: (3300, 5400, 7800),
    16: (3800, 6100, 9800),
    17: (4500, 7200, 11700),
    18: (5000, 8700, 14200),
    19: (5500, 10700, 17200),
    20: (6400, 13200, 22000),
}
DIFFICULTIES = ("low", "moderate", "high")
_src(
    "encounter_budget",
    f"{SRD}, Gameplay Toolbox — 'Combat Encounters', XP Budget per Character table (Low / "
    "Moderate / High by level). The 2024 method sums monster XP against the party's total "
    "budget with no group-size multiplier. Written from the section named; not yet read back.",
    verified=False,
)

# XP by Challenge Rating. CR 0 is 10 XP, or 0 for a creature with no effective attacks.
XP_BY_CR: dict[str, int] = {
    "0": 10, "1/8": 25, "1/4": 50, "1/2": 100,
    "1": 200, "2": 450, "3": 700, "4": 1100, "5": 1800, "6": 2300, "7": 2900, "8": 3900,
    "9": 5000, "10": 5900, "11": 7200, "12": 8400, "13": 10000, "14": 11500, "15": 13000,
    "16": 15000, "17": 18000, "18": 20000, "19": 22000, "20": 25000, "21": 33000,
    "22": 41000, "23": 50000, "24": 62000, "25": 75000, "26": 90000, "27": 105000,
    "28": 120000, "29": 135000, "30": 155000,
}
_src(
    "xp_by_cr",
    f"{SRD}, Monsters — 'Experience Points by Challenge Rating' table (CR 0 to 30; CR 0 is "
    "0 or 10 XP). Written from the section named; not yet read back.",
    verified=False,
)


def norm_cr(cr: str | int | float) -> str:
    text = str(cr).strip()
    if text in XP_BY_CR:
        return text
    try:
        frac = Fraction(text)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"cannot read a Challenge Rating out of {cr!r}") from exc
    key = str(frac) if frac.denominator != 1 else str(frac.numerator)
    if key not in XP_BY_CR:
        raise ValueError(f"CR {cr} is not on the table (0, 1/8, 1/4, 1/2, 1-30)")
    return key


def cr_xp(cr: str | int | float) -> int:
    return XP_BY_CR[norm_cr(cr)]


def party_budget(levels: Sequence[int]) -> dict[str, int]:
    out = {d: 0 for d in DIFFICULTIES}
    for lvl in levels:
        if lvl not in XP_BUDGET_PER_CHARACTER:
            raise ValueError(f"character level {lvl} is outside 1-20")
        for d, v in zip(DIFFICULTIES, XP_BUDGET_PER_CHARACTER[lvl]):
            out[d] += v
    return out


def rate_encounter(total_xp: int, budget: dict[str, int]) -> str:
    if total_xp > budget["high"]:
        return "ABOVE HIGH — beyond the published guidance; deadly territory"
    if total_xp > budget["moderate"]:
        return "high"
    if total_xp > budget["low"]:
        return "moderate"
    return "low"


# --------------------------------------------------------------------------------------
# Difficulty classes
# --------------------------------------------------------------------------------------

TYPICAL_DCS = {
    "very easy": 5,
    "easy": 10,
    "medium": 15,
    "hard": 20,
    "very hard": 25,
    "nearly impossible": 30,
}
_src(
    "typical_dcs",
    f"{SRD}, Playing the Game — 'Typical Difficulty Classes' table. Written from the section "
    "named; not yet read back.",
    verified=False,
)


def save_dc(prof: int, ability_mod: int) -> int:
    """Spell save DC and most feature DCs: 8 + proficiency bonus + ability modifier."""
    return 8 + prof + ability_mod


_src(
    "save_dc",
    f"{SRD}, Spells — 'Spell save DC = 8 + spellcasting ability modifier + Proficiency Bonus'. "
    "Written from the section named; not yet read back.",
    verified=False,
)

# --------------------------------------------------------------------------------------
# d20 tests, criticals, death
# --------------------------------------------------------------------------------------

D20_RULES = {
    "attack_nat20": "a natural 20 on an attack roll hits regardless of AC and is a Critical Hit",
    "attack_nat1": "a natural 1 on an attack roll misses regardless of modifiers or AC",
    "checks_and_saves": "a natural 20 or 1 on an ability check or saving throw has no special "
                        "effect; the total against the DC decides",
    "ties": "meeting the DC (or AC) exactly succeeds",
    "advantage": "roll two d20s and use the higher; disadvantage uses the lower; one of each "
                 "cancels to a single d20 however many sources there are",
}
_src(
    "d20_tests",
    f"{SRD}, Rules Glossary — 'D20 Test', 'Attack Roll', 'Critical Hit', 'Advantage', "
    "'Disadvantage'. Written from the entries named; not yet read back.",
    verified=False,
)

CRIT_RULE = "roll the attack's damage dice twice and add them together, then add modifiers once"
_src(
    "critical_damage",
    f"{SRD}, Rules Glossary — 'Critical Hit': extra damage dice, modifiers not doubled. "
    "Written from the entry named; not yet read back.",
    verified=False,
)

DEATH_SAVES = {
    "dc": 10,
    "successes_to_stabilise": 3,
    "failures_to_die": 3,
    "nat20": "regain 1 Hit Point (which ends the dying state)",
    "nat1": "counts as two failures",
    "damage_at_0": "any damage while at 0 HP is one failure; a Critical Hit is two",
    "massive_damage": "if damage reduces you to 0 HP and the damage left over equals or exceeds "
                      "your Hit Point maximum, you die outright",
    "healing": "any healing at 0 HP restores consciousness and resets the death saves",
    "stable": "a stable creature regains 1 HP after 1d4 hours",
}
_src(
    "death_saves",
    f"{SRD}, Playing the Game — 'Dropping to 0 Hit Points' (Instant Death, Falling "
    "Unconscious, Death Saving Throws, Stabilizing). Written from the section named; not yet "
    "read back.",
    verified=False,
)

EXHAUSTION_MAX = 6
EXHAUSTION_RULE = ("each level: d20 Tests take -2 x level and Speed drops by 5 ft x level; "
                   "level 6 is death; a Long Rest removes 1 level")
_src(
    "exhaustion",
    f"{SRD}, Rules Glossary — 'Exhaustion [Condition]'. Written from the entry named; not yet "
    "read back.",
    verified=False,
)


def exhaustion_penalty(level: int) -> tuple[int, int]:
    """(d20 penalty, speed penalty in feet) for an exhaustion level."""
    if not 0 <= level <= EXHAUSTION_MAX:
        raise ValueError(f"exhaustion {level} is outside 0-{EXHAUSTION_MAX}")
    return -2 * level, -5 * level


def concentration_dc(damage: int) -> int:
    """Constitution save to keep Concentration: DC 10 or half the damage, whichever is higher,
    to a maximum of DC 30."""
    return min(30, max(10, damage // 2))


_src(
    "concentration",
    f"{SRD}, Rules Glossary — 'Concentration': Constitution save, DC 10 or half the damage "
    "taken (round down), maximum DC 30. Written from the entry named; not yet read back.",
    verified=False,
)

# --------------------------------------------------------------------------------------
# Conditions
# --------------------------------------------------------------------------------------

# Exhaustion is the one valued condition and lives in its own field, like dying in PF2e.
CONDITIONS = {
    "blinded", "charmed", "deafened", "frightened", "grappled", "incapacitated", "invisible",
    "paralyzed", "petrified", "poisoned", "prone", "restrained", "stunned", "unconscious",
}
TRACKED_SEPARATELY = {"exhaustion"}
_src(
    "conditions",
    f"{SRD}, Rules Glossary — the fifteen entries tagged [Condition] (Blinded through "
    "Unconscious, Exhaustion included). Written from the glossary named; not yet read back.",
    verified=False,
)

# --------------------------------------------------------------------------------------
# Rests
# --------------------------------------------------------------------------------------

SHORT_REST = "1 hour; spend Hit Point Dice, each rolled + Constitution modifier, to heal"
LONG_REST = ("8 hours; regain all lost HP and all spent Hit Point Dice, restore spell slots, "
             "reduce Exhaustion by 1; at most one Long Rest in 24 hours")
_src(
    "rests",
    f"{SRD}, Rules Glossary — 'Short Rest' and 'Long Rest'. Note: the 2024 Long Rest restores "
    "ALL spent Hit Point Dice (the 2014 rules restored half). Written from the entries named; "
    "not yet read back.",
    verified=False,
)

# --------------------------------------------------------------------------------------
# Coins
# --------------------------------------------------------------------------------------

COIN_ORDER = ("pp", "gp", "ep", "sp", "cp")
COIN_IN_CP = {"pp": 1000, "gp": 100, "ep": 50, "sp": 10, "cp": 1}
_src(
    "coins",
    f"{SRD}, Equipment — 'Coin Values' table (1 pp = 10 gp; 1 gp = 2 ep = 10 sp = 100 cp). "
    "Written from the table named; not yet read back.",
    verified=False,
)

# --------------------------------------------------------------------------------------
# Carrying
# --------------------------------------------------------------------------------------


def carrying_capacity(strength_score: int, size: str = "medium") -> int:
    """Pounds a creature can carry: Strength score x 15, doubled for Large, halved for Tiny."""
    mult = {"tiny": 0.5, "small": 1, "medium": 1, "large": 2, "huge": 4, "gargantuan": 8}
    if size not in mult:
        raise ValueError(f"unknown size {size!r}")
    return int(strength_score * 15 * mult[size])


_src(
    "carrying_capacity",
    f"{SRD}, Rules Glossary — 'Carrying Capacity' (Strength score x 15 lb., size multipliers). "
    "Written from the entry named; not yet read back.",
    verified=False,
)

# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------


def _parse_monsters(spec: str) -> list[tuple[str, int]]:
    """'goblin:1/4x4, bugbear:1' -> [('goblin', 1/4) x4, ('bugbear', 1)]."""
    out: list[tuple[str, int]] = []
    for part in [p.strip() for p in spec.split(",") if p.strip()]:
        m = re.fullmatch(r"(.+?):([\d/.]+)(?:\s*[x×]\s*(\d+))?", part)
        if not m:
            raise ValueError(f"cannot read {part!r}; write 'name:CR' or 'name:CRx3'")
        name, cr, n = m.group(1).strip(), m.group(2), int(m.group(3) or 1)
        out += [(f"{name} (CR {norm_cr(cr)})", cr_xp(cr))] * n
    return out


def cmd_encounter(args: argparse.Namespace) -> int:
    levels = [int(x) for x in args.levels.split(",")] if args.levels else [args.party_level] * args.party_size
    budget = party_budget(levels)
    print(f"Party: {len(levels)} character(s) at level(s) {', '.join(map(str, levels))}")
    print(f"{'difficulty':<10} {'XP budget':>10}")
    for d in DIFFICULTIES:
        mark = "  ←" if args.difficulty == d else ""
        print(f"{d:<10} {budget[d]:>10}{mark}")
    if args.monsters:
        rows = _parse_monsters(args.monsters)
        total = sum(x for _, x in rows)
        print("\nMonsters:")
        for name, xp in rows:
            print(f"  {name:<32} {xp:>7} XP")
        print(f"  {'total':<32} {total:>7} XP  → {rate_encounter(total, budget).upper()}")
        if args.difficulty:
            left = budget[args.difficulty] - total
            print(f"  {abs(left)} XP {'left in' if left >= 0 else 'over'} the {args.difficulty} budget")
        print(f"  XP award if all are defeated: {total} total, {total // len(levels)} each")
    print(f"\nSource: {SOURCES['encounter_budget']}")
    print(f"Source: {SOURCES['xp_by_cr']}")
    if "encounter_budget" in UNVERIFIED_TABLES:
        print("⚠ UNVERIFIED — see DESIGN_NOTES.md 'To verify before first play'.")
    return 0


def cmd_level(args: argparse.Namespace) -> int:
    if args.xp is not None:
        lvl = level_for_xp(args.xp)
        nxt = xp_to_next(args.xp)
        print(f"{args.xp} XP → level {lvl}, proficiency +{proficiency_bonus(lvl)}"
              + (f", {nxt} XP to level {lvl + 1}" if nxt is not None else ", maximum level"))
    else:
        print(f"{'lvl':>3} {'XP':>7} {'prof':>4}")
        for i, xp in enumerate(XP_FOR_LEVEL):
            print(f"{i + 1:>3} {xp:>7} {'+' + str(PROFICIENCY_BONUS[i]):>4}")
    print(f"\nSource: {SOURCES['advancement']}")
    return 0


def cmd_dc(args: argparse.Namespace) -> int:
    if args.difficulty:
        key = args.difficulty.lower().replace("-", " ")
        if key not in TYPICAL_DCS:
            raise ValueError(f"difficulty must be one of: {', '.join(TYPICAL_DCS)}")
        print(f"{key}: DC {TYPICAL_DCS[key]}")
    else:
        for k, v in TYPICAL_DCS.items():
            print(f"{k:<18} DC {v}")
    if args.prof is not None and args.mod is not None:
        print(f"save DC = 8 + {args.prof} + {args.mod} = {save_dc(args.prof, args.mod)}")
    print(f"\nSource: {SOURCES['typical_dcs']}")
    return 0


def cmd_rules(args: argparse.Namespace) -> int:
    blocks = {
        "d20": (D20_RULES, "d20_tests"),
        "crit": ({"critical damage": CRIT_RULE}, "critical_damage"),
        "death": (DEATH_SAVES, "death_saves"),
        "exhaustion": ({"exhaustion": EXHAUSTION_RULE}, "exhaustion"),
        "rest": ({"short rest": SHORT_REST, "long rest": LONG_REST}, "rests"),
        "conditions": ({"conditions": ", ".join(sorted(CONDITIONS | TRACKED_SEPARATELY))}, "conditions"),
        "coins": ({k: f"{v} cp" for k, v in COIN_IN_CP.items()}, "coins"),
    }
    want = [args.topic] if args.topic else list(blocks)
    for t in want:
        if t not in blocks:
            raise ValueError(f"topic must be one of: {', '.join(blocks)}")
        rows, key = blocks[t]
        print(f"## {t}")
        for k, v in rows.items():
            print(f"- {k}: {v}")
        mark = " ⚠ UNVERIFIED" if key in UNVERIFIED_TABLES else ""
        print(f"Source:{mark} {SOURCES[key]}\n")
    return 0


def cmd_sources(args: argparse.Namespace) -> int:
    print("Provenance of every table in tools/dnd5e.py\n")
    for key in sorted(SOURCES):
        mark = "⚠ UNVERIFIED" if key in UNVERIFIED_TABLES else "verified"
        print(f"[{mark}] {key}\n    {SOURCES[key]}\n")
    print(f"{len(UNVERIFIED_TABLES)} of {len(SOURCES)} tables are unverified"
          + (": " + ", ".join(sorted(UNVERIFIED_TABLES)) if UNVERIFIED_TABLES else "."))
    if UNVERIFIED_TABLES:
        print("\nThese are listed in DESIGN_NOTES.md under 'To verify before first play'.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="dnd5e.py", description="D&D 5e (SRD 5.2.1) tables with sources.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("encounter", help="XP budget by difficulty, and what a monster list costs")
    p.add_argument("--party-level", type=int, default=1)
    p.add_argument("--party-size", type=int, default=1)
    p.add_argument("--levels", default=None, help="comma list of character levels, for a mixed party")
    p.add_argument("--difficulty", choices=DIFFICULTIES, default=None)
    p.add_argument("--monsters", default=None, help="'goblin:1/4x4, bugbear:1'")

    p = sub.add_parser("level", help="the advancement table, or the level for an XP total")
    p.add_argument("--xp", type=int, default=None)

    p = sub.add_parser("dc", help="typical DCs, and 8 + prof + mod")
    p.add_argument("difficulty", nargs="?")
    p.add_argument("--prof", type=int)
    p.add_argument("--mod", type=int)

    p = sub.add_parser("rules", help="the short rule statements the tools rely on")
    p.add_argument("topic", nargs="?")

    sub.add_parser("sources", help="print the provenance of every table, verified or not")
    return ap


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return {
            "encounter": cmd_encounter,
            "level": cmd_level,
            "dc": cmd_dc,
            "rules": cmd_rules,
            "sources": cmd_sources,
        }[args.cmd](args)
    except ValueError as exc:
        print(f"dnd5e.py: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
