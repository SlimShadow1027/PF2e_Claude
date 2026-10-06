#!/usr/bin/env python3
"""dnd4e.py — the D&D 4e ruleset, with its numbers left to the owner on purpose.

The third ruleset, and the one that works differently from the other two for a reason that
is not a design choice:

    pf2e.py    Pathfinder 2e Remaster    rules published under the ORC License
    dnd5e.py   D&D 2024                  rules published as SRD 5.2 under CC-BY-4.0
    dnd4e.py   D&D 4e                    **no open-content release of any kind**

Fourth edition was licensed to third parties under the Game System License, which — unlike
the OGL before it and CC-BY after it — permitted no Open Game Content at all: not rules
text, not tables, not monster stat blocks. The document WotC published alongside it as a
"System Reference Document" was an index of terms and templates for referencing the books,
not a restatement of the rules. The GSL is no longer offered to new licensees.

So this file cannot do what its two siblings do. What it does instead:

**It states mechanics in its own words.** How a turn is structured, what the four defences
are, what bloodied means, how dying works. Game mechanics are not themselves copyrightable;
their expression is. Nothing here is quoted, and every statement is marked as read from the
published rules rather than verified against an open source — a weaker provenance than
either sibling can claim, and `sources` says so in those words rather than burying it.

**It ships no numeric tables.** XP by level, DCs by level, monster benchmarks, treasure
parcels and item prices live in `tools/dnd4e_tables.json`, every value `null`, each with a
note naming the book and the table to read it from. **Any function needing an unfilled value
raises instead of guessing.** That is the point: a framework whose first rule is "numbers get
verified, not remembered" must not invent a number it cannot source, and inventing one here
would be exactly that.

The practical effect: a 4e campaign in this framework runs its dice, its state, its
conditions and its encounter tracker out of the box, and asks you to type in a handful of
tables from your own books before it will do encounter or treasure maths. See
`system/dnd4e/README.md`.

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

import rules  # noqa: E402

#: How every statement in this file is sourced. There is no better answer available.
PROVENANCE = (
    "Stated from the published D&D 4e rules in this file's own words. D&D 4e has no "
    "open-content release — the Game System License permitted no Open Game Content, and the "
    "4e 'SRD' was an index rather than the rules — so there is NO open source to cite or "
    "verify against, and nothing here is quoted. Treat every mechanic in this file as "
    "'believed correct, unverifiable from open content' and check it against your own books "
    "before it matters. Numeric tables are not here at all; they are yours to supply in "
    "tools/dnd4e_tables.json."
)

SOURCES: dict[str, str] = {}
UNVERIFIED_TABLES: list[str] = []
CONVENTION_TABLES: list[str] = []
#: Mechanics stated from the books with no open source to verify against. Everything this
#: file asserts about how 4e works is in here, which is the honest shape for this ruleset.
UNSOURCEABLE: list[str] = []


def _src(key: str, text: str, verified: bool = True, convention: bool = False,
         unsourceable: bool = False) -> str:
    SOURCES[key] = text
    if not verified:
        UNVERIFIED_TABLES.append(key)
    if convention:
        CONVENTION_TABLES.append(key)
    if unsourceable:
        UNSOURCEABLE.append(key)
    return text


#: The short marker each mechanic carries. The full statement is `PROVENANCE`, printed once
#: by `sources` — repeating a paragraph on every entry makes the list unreadable, and an
#: unread provenance note is no provenance at all.
PROVENANCE_TAG = (
    " [D&D 4e mechanic, stated in this framework's own words; no open content exists to cite "
    "or verify against — see `python3 tools/dnd4e.py sources`]"
)


def _mech(key: str, text: str) -> str:
    """A mechanic stated from the books, with no open source to verify it against."""
    return _src(key, text + PROVENANCE_TAG, verified=False, unsourceable=True)


# --------------------------------------------------------------------------------------
# Identity
# --------------------------------------------------------------------------------------

SYSTEM_ID = "dnd4e"
SYSTEM_NAME = "Dungeons & Dragons 4th Edition"
SYSTEM_SHORT = "D&D 4e"

#: Pass or fail against a defence. No degree ladder.
USES_DEGREES = False

CRIT_RULE = (
    "A natural 20 on an attack roll hits automatically and is a critical hit; a natural 1 "
    "misses automatically. A critical hit deals **maximum damage** for the attack's normal "
    "damage dice — it does not double them — plus any extra critical dice a magic item "
    "grants, which the GM adds separately."
)
_mech(
    "crit_rule",
    "D&D 4e: a natural 20 is an automatic hit and a critical hit; a natural 1 is an automatic "
    "miss. A critical hit deals the maximum result of the attack's damage dice rather than "
    "doubling them, and magic weapons add their own critical dice on top. This is the sharpest "
    "difference from both siblings: Pathfinder doubles the whole roll, D&D 2024 doubles the "
    "dice, and 4e maximises them. `roll.py damage --crit` on a 4e campaign rewrites the "
    "expression to its maximum and shows the working",
)

DEFAULT_CALENDAR = "generic"
_src(
    "calendar",
    "4e publishes no calendar this framework can reproduce, and its published settings are not "
    "open content. A campaign defaults to the placeholder calendar in tools/rules.py; a named "
    "setting's calendar goes in the world's CALENDAR.md, where every ruleset reads it.",
    convention=True,
)

#: The three tiers. Levels run to 30, not 20, which is the structural difference that
#: matters most when a 4e campaign shares a world with a 20-level one.
TIERS: list[tuple[int, int, str]] = [
    (1, 10, "Heroic"),
    (11, 20, "Paragon"),
    (21, 30, "Epic"),
]
MAX_LEVEL = 30
_mech(
    "tiers",
    "D&D 4e runs to level 30 in three tiers of ten: Heroic 1-10, Paragon 11-20, Epic 21-30. "
    "Both sibling rulesets stop at 20, so a 4e character's level number means something "
    "different again and must not be read across — see `python3 tools/world.py crossing`",
)


def tier_name(level: int) -> str:
    for low, high, name in TIERS:
        if low <= int(level) <= high:
            return name
    return "Epic" if int(level) > MAX_LEVEL else "Heroic"


def tier_of(level: int) -> str:
    return rules.scope_band(SYSTEM_ID, level)


# --------------------------------------------------------------------------------------
# The owner-supplied tables
# --------------------------------------------------------------------------------------

TABLES_PATH = Path(__file__).resolve().parent / "dnd4e_tables.json"


class TableMissing(Exception):
    """A number was asked for that this framework cannot supply and the owner has not."""


_TABLES_CACHE: dict[str, Any] | None = None


def tables(reload: bool = False) -> dict[str, Any]:
    global _TABLES_CACHE
    if _TABLES_CACHE is None or reload:
        if not TABLES_PATH.exists():
            raise TableMissing(
                f"{TABLES_PATH.name} is missing. It holds the 4e numbers this framework cannot "
                f"ship; restore it from the repository and fill in what your campaign needs."
            )
        try:
            _TABLES_CACHE = json.loads(TABLES_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise TableMissing(f"{TABLES_PATH.name} is not valid JSON: {exc}") from exc
    return _TABLES_CACHE


def _table(name: str) -> dict[str, Any]:
    t = tables().get(name)
    if not isinstance(t, dict):
        raise TableMissing(f"{TABLES_PATH.name} has no table called {name!r}")
    return t


def _need(name: str, key: Any = None) -> Any:
    """Read an owner-supplied value, or raise with the book to read it from.

    This is the function that keeps this ruleset honest. Everything numeric goes through
    it, so an unfilled table can never silently become a plausible-looking answer.
    """
    t = _table(name)
    values = t.get("values")
    if key is None:
        if not values:
            raise TableMissing(_unfilled_message(name, t))
        return values
    if not isinstance(values, dict) or str(key) not in values or values[str(key)] is None:
        raise TableMissing(_unfilled_message(name, t, key))
    return values[str(key)]


def _unfilled_message(name: str, t: dict[str, Any], key: Any = None) -> str:
    where = t.get("_source") or "your own books"
    shape = t.get("_shape")
    bits = [
        f"the 4e table {name!r} has no value" + (f" for {key!r}" if key is not None else "") + ".",
        f"Read it from: {where}.",
    ]
    if shape:
        bits.append(f"Shape: {shape}.")
    if t.get("_note"):
        bits.append(str(t["_note"]))
    bits.append(
        f"Fill it in {TABLES_PATH.name} and run `python3 tools/dnd4e.py tables` to check. "
        f"This framework will not guess: D&D 4e has no open-content release, so a number it "
        f"invented here would be exactly the 'recalled from memory' error the charter forbids."
    )
    return " ".join(bits)


def table_status() -> list[dict[str, Any]]:
    """Which owner tables are filled, for `tables` and for the validator."""
    out = []
    for name, t in tables().items():
        if name.startswith("_") or not isinstance(t, dict):
            continue
        values = t.get("values")
        if isinstance(values, dict):
            total = len(values)
            filled = sum(1 for v in values.values() if v is not None)
        else:
            total, filled = 0, 0
        out.append({
            "table": name,
            "filled": filled,
            "entries": total,
            "source": t.get("_source", ""),
            "ready": filled > 0,
        })
    return out


_src(
    "owner_tables",
    "EVERY NUMERIC TABLE IN THIS RULESET IS OWNER-SUPPLIED. tools/dnd4e_tables.json holds "
    "character XP by level, monster XP by level, the elite/solo/minion multipliers, the "
    "encounter budget, DCs by level, treasure parcels, magic item prices and the monster "
    "benchmarks — every value null until the owner types it in from books they own, each with "
    "a note naming the book and table to read it from. Functions needing an unfilled value "
    "raise TableMissing naming the table and the source. See `python3 tools/dnd4e.py tables`.",
    verified=False,
    unsourceable=True,
)


# --------------------------------------------------------------------------------------
# Resolution
# --------------------------------------------------------------------------------------

#: 4e attacks target one of four defences rather than being opposed by a save.
DEFENCES = ("ac", "fortitude", "reflex", "will")
DEFENCE_NAMES = {"ac": "AC", "fortitude": "Fortitude", "reflex": "Reflex", "will": "Will"}
_mech(
    "defences",
    "D&D 4e gives every creature four defences — AC, Fortitude, Reflex and Will — and an attack "
    "targets one of them with an attack roll. There are no saving throws made in defence against "
    "an attack: the attacker rolls against the defender's static number. 4e's 'saving throw' is a "
    "separate thing entirely (see `saving_throws`), which is why the attacker always rolls here "
    "and the Pathfinder and 2024 habit of asking the defender for a save is wrong at this table",
)

SAVE_DC = 10
_mech(
    "saving_throws",
    "A D&D 4e saving throw is not made against an attack. It is a flat d20 against 10, made at the "
    "end of your turn, to end an ongoing effect marked 'save ends' — no ability modifier and no "
    "level term, though bonuses to saves apply. This is the single most confusing overlap in "
    "vocabulary across the three rulesets: 'save' means a defence roll in the other two and an "
    "effect-ending roll here",
)

COMBAT_ADVANTAGE = 2
_mech(
    "combat_advantage",
    "Combat advantage in D&D 4e grants a +2 bonus to the attack roll, rather than a second die as "
    "Advantage does in D&D 2024. It does not stack with itself",
)

HALF_LEVEL_APPLIES_TO = ("attack rolls", "defences", "skill checks", "initiative")
_mech(
    "half_level",
    "D&D 4e adds half the character's level, rounded down, to attack rolls, all four defences, all "
    "skill checks and initiative. This is why 4e numbers climb steadily with level and why a 4e "
    "level is not comparable to a level in either sibling ruleset",
)

ATTACK_SCALE = ("miss", "hit", "critical hit")
ATTACK_LABELS = ("MISS", "HIT", "CRITICAL HIT")
TEST_SCALE = ("failure", "success")
TEST_LABELS = ("FAILURE", "SUCCESS")
# A death saving throw has no success to record — 10 or better is simply not a failure —
# so its two outcomes are named for what they actually do to the character.
DEATH_SAVE_SCALE = ("failure", "held on")
DEATH_SAVE_LABELS = ("FAILURE", "NO FAILURE")

OUTCOME_SCALES = {
    "attack": (ATTACK_SCALE, ATTACK_LABELS),
    "check": (TEST_SCALE, TEST_LABELS),
    "save": (TEST_SCALE, TEST_LABELS),
    "flat": (TEST_SCALE, TEST_LABELS),
    "death-save": (DEATH_SAVE_SCALE, DEATH_SAVE_LABELS),
}


def resolve(total: int, dc: int, natural: int | None = None, *, kind: str = "check") -> dict[str, Any]:
    """One d20 against one defence or DC, as the shared tools consume it."""
    k = str(kind).lower()
    scale, labels = OUTCOME_SCALES.get(k, (TEST_SCALE, TEST_LABELS))
    total, dc = int(total), int(dc)
    forced: str | None = None

    if k == "attack":
        if natural == 20:
            idx, forced = 2, "natural 20: hits automatically, and is a critical hit (maximum damage)"
        elif natural == 1:
            idx, forced = 0, "natural 1: misses automatically"
        else:
            idx = 1 if total >= dc else 0
    elif k in ("save", "death-save"):
        # A 4e saving throw is a flat d20 against 10, whatever was passed as the DC.
        target = SAVE_DC
        if k == "death-save" and natural == 20:
            idx, forced = 1, "natural 20: spend a healing surge instead of recording a failure"
        else:
            idx = 1 if total >= target else 0
        dc = target
    else:
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
        out["failures_incurred"] = 0 if idx else 1
        out["spends_surge"] = natural == 20
    return out


# --------------------------------------------------------------------------------------
# Advancement, encounters and wealth — all owner-supplied
# --------------------------------------------------------------------------------------


def xp_to_level(level: int) -> int | None:
    """The cumulative XP to be `level`. Owner-supplied; raises if unfilled."""
    if int(level) < 1 or int(level) > MAX_LEVEL:
        return None
    if int(level) == 1:
        return 0
    return int(_need("character_xp", int(level)))


def xp_is_cumulative() -> bool:
    """True: 4e's XP total climbs and is never reset."""
    return True


def level_for_xp(xp: int) -> int:
    values = _need("character_xp")
    best = 1
    for lvl, need in sorted(((int(k), v) for k, v in values.items() if v is not None)):
        if int(xp) >= int(need):
            best = lvl
    return best


def creature_xp(level: int, role: str = "standard") -> int:
    """XP for a monster of this level and role. Owner-supplied."""
    base = int(_need("monster_xp_by_level", int(level)))
    mult = _table("monster_role_multipliers").get("values", {}).get(str(role).lower())
    if mult is None:
        raise TableMissing(
            _unfilled_message("monster_role_multipliers", _table("monster_role_multipliers"), role)
        )
    return int(round(base * float(mult)))


def encounter_budgets(party_size: int, party_level: int = 1, **_: Any) -> dict[str, int]:
    """The XP budget for an encounter. Owner-supplied.

    4e's standard encounter is level-appropriate by default and difficulty is usually tuned
    by raising or lowering the encounter's level against the party's, rather than by a
    separate budget column. So the default shape here is one budget, not three — and if
    your printing does give difficulty columns, fill `encounter_budget_columns` instead.
    """
    if party_size < 1:
        raise ValueError("a party needs at least one character")
    cols = _table("encounter_budget_columns").get("values") or {}
    if cols:
        return {
            name: int(per[str(int(party_level))]) * int(party_size)
            for name, per in cols.items()
            if isinstance(per, dict) and per.get(str(int(party_level))) is not None
        }
    per_char = int(_need("encounter_budget_per_character", int(party_level)))
    return {"standard": per_char * int(party_size)}


def degenerate_budgets(party_size: int, party_level: int = 1) -> list[str]:
    """Budgets that collapse at this party size. 4e's is linear, so none."""
    return []


def rate_encounter(total_xp: int, party_size: int, party_level: int = 1, **_: Any) -> str:
    b = encounter_budgets(party_size, party_level)
    standard = b.get("standard") or max(b.values())
    ratio = total_xp / standard if standard else 0
    # Labelled as this framework's reading, because 4e tunes difficulty by encounter level
    # rather than by a published budget-to-label mapping.
    if ratio >= 1.5:
        return "well above a standard encounter"
    if ratio >= 1.15:
        return "above a standard encounter"
    if ratio >= 0.85:
        return "a standard encounter"
    if ratio >= 0.5:
        return "below a standard encounter"
    return "well below a standard encounter"


_src(
    "encounter_rating",
    "THIS FRAMEWORK'S OWN CONVENTION. 4e tunes an encounter's difficulty by its level relative to "
    "the party rather than by a published budget-to-difficulty mapping, so the five labels "
    "`rate_encounter` returns are this framework's reading of how far a build sits from a "
    "standard encounter, not a published rating. The budget it compares against is yours.",
    convention=True,
)


def xp_award(total_xp_spent: int, party_size: int = 4, **_: Any) -> int:
    """XP awarded for clearing an encounter: the monsters' own XP, divided by the party.

    4e divides the encounter's total XP among the characters, which is the opposite of
    Pathfinder (budget shrinks, award stays whole) and of D&D 2024 (budget scales, award
    undivided). Three rulesets, three answers; do not carry one across.
    """
    if party_size < 1:
        raise ValueError("a party needs at least one character")
    return int(total_xp_spent) // int(party_size)


_mech(
    "xp_award",
    "D&D 4e awards an encounter's total monster XP divided evenly among the characters who took "
    "part. Note how differently the three rulesets solve the small-party problem: Pathfinder "
    "shrinks the budget and awards the four-character figure undivided, D&D 2024 scales the "
    "budget per character and awards the monsters' XP undivided, and 4e divides the award — so "
    "a solo 4e character clearing a one-character-sized encounter gets all of its XP",
)


def treasure_for(level: int, party_size: int = 4, **_: Any) -> dict[str, Any]:
    """The treasure parcels for a level. Owner-supplied."""
    parcels = _need("treasure_parcels", int(level))
    return {
        "level": int(level),
        "convention": False,
        "owner_supplied": True,
        "parcels": parcels,
        "party_size": int(party_size),
        "note": (
            "4e hands out treasure as a numbered set of parcels per level rather than a lump "
            "sum, so this is the list you transcribed, not a budget. Magic item prices are in "
            "`magic_item_prices` if you filled them."
        ),
    }


def difficulty_dc(level: int, difficulty: str = "moderate") -> int:
    """A DC by level. Owner-supplied, and the table was revised by errata."""
    row = _need("dc_by_level", int(level))
    key = str(difficulty).lower()
    if not isinstance(row, dict) or row.get(key) is None:
        raise TableMissing(
            _unfilled_message("dc_by_level", _table("dc_by_level"), f"{level}/{difficulty}")
        )
    return int(row[key])


_mech(
    "dcs_scale_with_level",
    "D&D 4e DCs rise with level, as Pathfinder's do and D&D 2024's do not. The published "
    "Difficulty Class by Level table was REVISED by errata partway through the edition's life, so "
    "two printings give different numbers for the same level — which is why dnd4e_tables.json has "
    "a `_printing` field to record which one you transcribed. Getting this wrong shifts every "
    "skill check in the campaign",
)


def settlement_availability(settlement: str) -> dict[str, Any]:
    """What can be bought where. 4e prices items by level, so this needs the price table."""
    raise TableMissing(
        "4e sets what is available by item level and market price rather than by settlement "
        "size, and this framework has no published mapping for it. Fill `magic_item_prices` in "
        f"{TABLES_PATH.name} and decide per settlement what level of item its market carries, "
        "recording that in the world's GAZETTEER.md alongside the other rulesets' columns."
    )


# --------------------------------------------------------------------------------------
# Conditions
# --------------------------------------------------------------------------------------

#: 4e's conditions. The ones that carry a number do so as a value here, same as elsewhere.
VALUED_CONDITIONS = {"ongoing-damage", "regeneration"}
UNVALUED_CONDITIONS = {
    "blinded", "bloodied", "dazed", "deafened", "dominated", "dying", "helpless",
    "immobilized", "marked", "petrified", "prone", "restrained", "slowed", "stunned",
    "surprised", "unconscious", "weakened",
}
KNOWN_CONDITIONS = VALUED_CONDITIONS | UNVALUED_CONDITIONS
#: Healing surges, action points and death-save failures are first-class fields.
TRACKED_SEPARATELY: set[str] = set()
_mech(
    "conditions",
    "D&D 4e's condition list differs from both siblings in membership and in effect. `marked` and "
    "`dominated` exist here and in neither of the others; `dazed` is 4e's and is not 2024's "
    "`stunned`; `weakened` halves damage dealt. Ongoing damage is a valued condition because it "
    "carries an amount. Note that `bloodied` is a real condition here with effects keyed off it, "
    "where in D&D 2024 it is a flag with no effect of its own",
)

#: 4e marks an effect's duration differently from the other two.
DURATION_NOTES = (
    "4e durations are: until the end of your next turn, until the end of the encounter, "
    "until you take a short rest, 'save ends' (a flat d20 vs 10 at the end of your turn), "
    "or sustained. The framework's duration kinds cover these; record a 'save ends' effect "
    "as until-removed and roll the save with `roll.py save`."
)


# --------------------------------------------------------------------------------------
# Hit points, surges, and dying
# --------------------------------------------------------------------------------------

SURGE_FRACTION = 4  # a healing surge restores one quarter of maximum HP
DEATH_SAVE_FAILURES = 3
_mech(
    "healing_surges",
    "A D&D 4e character has a per-day pool of healing surges; spending one restores a quarter of "
    "maximum hit points, rounded down. Most healing in 4e spends a surge rather than being free, "
    "which makes the surge pool the real attrition clock — not hit points. The pool refills on an "
    "extended rest. Second Wind spends a surge as a standard action, once per encounter, and also "
    "grants a +2 bonus to all defences until the start of your next turn",
)
_mech(
    "bloodied_and_death",
    "A D&D 4e creature is bloodied at half its maximum hit points or fewer, and bloodied is a real "
    "condition other rules key off. Hit points go below zero: a character dies when reduced to a "
    "negative total equal to their bloodied value — so a 40 HP character dies at -20, not at 0. At "
    "0 or below a character is dying and unconscious, and makes a death saving throw at the end of "
    "each of their turns: a flat d20, 10 or better to hold on, and three failures before an "
    "extended rest is death. A natural 20 on it lets them spend a healing surge instead",
)


def surge_value(max_hp: int) -> int:
    return int(max_hp) // SURGE_FRACTION


def death_threshold(max_hp: int) -> int:
    """The negative total at which a character dies: their bloodied value, negated."""
    return -(int(max_hp) // 2)


#: The shape of the death-save record in this ruleset. 4e counts failures only — there is
#: no success counter and no Stable state, so writing D&D 2024's shape here would invent two
#: fields the game does not have.
BLANK_DEATH_SAVES: dict[str, Any] = {"failures": 0}
DEATH_SAVE_SUCCESS_DC = 10
DEATH_SAVE_SURGE_ON = 20
_mech(
    "death_saves",
    "A dying D&D 4e character makes a saving throw at the end of each of their turns against a "
    "flat 10, as all 4e saving throws are. Below 10 is a failure, and the third failure in an "
    "encounter is death; 10 or more is simply no failure, and nothing accumulates on a success. "
    "A natural 20 lets the character spend a healing surge and act. This is a different clock "
    "from both siblings: Pathfinder counts dying upward to 4 and D&D 2024 counts three "
    "successes as well as three failures",
)


def on_zero_hp(pc: dict[str, Any], *, from_crit: bool = False, overflow: int = 0,
               already_down: bool = False) -> dict[str, Any]:
    """What 4e does at 0 HP or below: dying, with a floor that is not zero.

    The returned `set` keys are written to the character by `state.py` — 4e is the only
    ruleset here whose hit points keep meaning something below zero, so the below-zero
    total has to persist between one hit and the next.
    """
    hp = pc.get("hp") or {}
    hp_max = int(hp.get("max", 0))
    # The framework stores current HP with 0 as the floor, so the overflow is what carries
    # a 4e character past it toward the death threshold.
    below = int(pc.get("hp_below_zero", 0)) + int(overflow)
    threshold = death_threshold(hp_max)
    write = {"hp_below_zero": below}
    if hp_max and below and -below <= threshold:
        return {
            "action": "dead",
            "set": write,
            "reason": f"reduced to {-below} hit points, at or past the death threshold of "
                      f"{threshold} (negative bloodied value)",
            "notes": [f"{-below} hit points — at or past {threshold}, which is death in 4e"],
        }
    if already_down:
        return {
            "action": "death-save-failures",
            "value": 1,
            "set": write,
            "reason": "took damage while dying",
            "notes": [f"damage while dying — 1 death saving throw failure"
                      + (f"; now at {-below} hit points of a {threshold} threshold" if hp_max else "")],
        }
    return {
        "action": "down",
        "set": write,
        "reason": "reduced to 0 hit points or below",
        "notes": ["reduced to 0 hit points or below — dying and unconscious, making a death "
                  "saving throw at the end of each turn"]
        + ([f"hit points continue below zero; death at {threshold}"] if hp_max else []),
    }


def on_healed_from_zero(pc: dict[str, Any]) -> dict[str, Any]:
    """Any healing from dying ends it, and clears the below-zero total."""
    ds = pc.get("death_saves") or {}
    if int(ds.get("failures", 0)) or int(pc.get("hp_below_zero", 0)):
        return {
            "action": "reset-death-saves",
            "set": {"hp_below_zero": 0},
            "reason": "regained hit points, which ends dying and clears the below-zero total",
        }
    return {"action": "none", "set": {"hp_below_zero": 0}}


# --------------------------------------------------------------------------------------
# Rest and the daily reset
# --------------------------------------------------------------------------------------

SHORT_REST_MINUTES = 5
EXTENDED_REST_HOURS = 6
_mech(
    "rests",
    "A D&D 4e short rest is about 5 minutes and restores encounter powers and the use of Second "
    "Wind; it does not restore hit points by itself, though you may spend healing surges during "
    "it. An extended rest is about 6 hours, restores hit points to maximum and the full healing "
    "surge pool, returns daily powers, and clears death saving throw failures; you may take only "
    "one in a 24-hour period. Note the contrast with D&D 2024's one-hour short rest and 8-hour "
    "long rest, and with Pathfinder, which has neither",
)


def daily_reset(data: dict[str, Any]) -> list[str]:
    """What an extended rest restores."""
    notes = []
    for _, pc in (data.get("pcs") or {}).items():
        hp = pc.get("hp") or {}
        if int(hp.get("max", 0)):
            hp["current"] = int(hp["max"])
        hp["temp"] = 0
        pc["hp_below_zero"] = 0
        surges = pc.setdefault("healing_surges", {"max": 0, "used": 0})
        recovered = int(surges.get("used", 0))
        surges["used"] = 0
        pc["second_wind_used"] = False
        pc["death_saves"] = {"failures": 0}
        powers = pc.setdefault("powers", {"encounter": [], "daily": []})
        for bucket in ("encounter", "daily"):
            for entry in powers.get(bucket) or []:
                entry["used"] = False
        # Action points reset to 1 on an extended rest; milestones accrue them during a day.
        pc["action_points"] = 1
        pc["milestones"] = 0
        bits = [f"HP {hp.get('current', 0)}/{hp.get('max', 0)}"]
        if recovered:
            bits.append(f"{recovered} healing surge(s) back")
        bits += ["daily and encounter powers back", "Second Wind available", "1 action point"]
        notes.append(f"{pc['name']}: " + ", ".join(bits))
    notes.append(
        "Death saving throw failures cleared. Only one extended rest per 24 hours. Temporary "
        "hit points ended with the rest."
    )
    return notes


def short_rest(data: dict[str, Any], who: str | None = None) -> list[str]:
    """What a 5-minute short rest restores."""
    out = [f"Short rest ({SHORT_REST_MINUTES} minutes)."]
    pcs = (data.get("pcs") or {})
    targets = {who: pcs[who]} if who and who in pcs else pcs
    for _, pc in targets.items():
        powers = pc.setdefault("powers", {"encounter": [], "daily": []})
        for entry in powers.get("encounter") or []:
            entry["used"] = False
        pc["second_wind_used"] = False
        surges = pc.get("healing_surges") or {}
        left = int(surges.get("max", 0)) - int(surges.get("used", 0))
        out.append(f"  {pc['name']}: encounter powers back, Second Wind available, "
                   f"{left} healing surge(s) left to spend")
    out += [
        "Daily powers do NOT come back on a short rest, and hit points do not return by "
        "themselves — spend healing surges to regain them.",
        "Action points are not restored by a short rest; they come from milestones.",
    ]
    return out


# --------------------------------------------------------------------------------------
# Money and carrying
# --------------------------------------------------------------------------------------

COIN_ORDER = ("pp", "gp", "sp", "cp")
COIN_IN_CP = {"pp": 10000, "gp": 100, "sp": 10, "cp": 1}
BASE_COIN = "gp"
_mech(
    "coins",
    "D&D 4e uses copper, silver, gold, platinum and astral diamonds. The ratios differ from both "
    "siblings: 10 cp to a silver, 10 sp to a gold, and **100 gp to a platinum** rather than 10, "
    "which is why a purse cannot be read across rulesets even where the coin names match. Astral "
    "diamonds are worth 10,000 gp each and are left out of this framework's coin set — record one "
    "as an item, because treating it as a denomination makes every small purchase unreadable",
)

CARRY_PER_STRENGTH = 10
_mech(
    "carrying_capacity",
    "A D&D 4e character carries up to ten times their Strength score in pounds as a normal load, "
    "twice that as a heavy load at the cost of being slowed, and five times the normal load as a "
    "maximum drag. This framework reports the normal load as the limit and names the heavy load, "
    "and does not model the slowed condition automatically",
)


def carry_capacity(strength: int) -> dict[str, int]:
    s = int(strength)
    return {
        "normal": s * CARRY_PER_STRENGTH,
        "heavy": s * CARRY_PER_STRENGTH * 2,
        "drag": s * CARRY_PER_STRENGTH * 5,
    }


def item_weight(spec: Any) -> float:
    if spec is None:
        return 0.0
    text = str(spec).strip().lower()
    if text in ("", "-", "--", "0", "negligible", "none"):
        return 0.0
    text = re.sub(r"(lbs?\.?|pounds?)$", "", text).strip()
    try:
        from fractions import Fraction
        return float(Fraction(text))
    except (ValueError, ZeroDivisionError):
        return 0.0


def carry_report(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Weight carried against the normal load, per carrier, in pounds."""
    rows = []
    for key, pc in (data.get("pcs") or {}).items():
        carried = 0.0
        for it in pc.get("items", []) or []:
            carried += item_weight(it.get("weight", it.get("lb", 0))) * int(it.get("qty", 1))
        strength = pc.get("strength")
        assumed = strength is None
        cap = carry_capacity(10 if assumed else int(strength))
        rows.append({
            "id": key,
            "name": pc.get("name", key),
            "unit": "lb",
            "carried": round(carried, 2),
            "counted": round(carried, 2),
            "strength": 10 if assumed else int(strength),
            "strength_assumed": assumed,
            "max": cap["normal"],
            "heavy": cap["heavy"],
            "drag": cap["drag"],
            "encumbered_after": None,  # 4e's heavy load is a separate state, not a band
            "encumbered": carried > cap["normal"],
            "over_max": carried > cap["heavy"],
            "line": (f"{carried:.1f} lb of {cap['normal']} lb normal load "
                     f"(heavy {cap['heavy']} lb; Str {10 if assumed else int(strength)}"
                     f"{' assumed' if assumed else ''})"),
        })
    return rows


# --------------------------------------------------------------------------------------
# A blank character
# --------------------------------------------------------------------------------------

ABILITIES = ("str", "con", "dex", "int", "wis", "cha")
#: 4e lists the six abilities in this order — Str/Con/Dex/Int/Wis/Cha, paired by defence —
#: rather than the Str/Dex/Con order both siblings use. Only the printing order differs.


def ability_modifier(score: int) -> int:
    """Half the amount a score is above ten, rounded down. The same arithmetic in all three
    rulesets this framework runs, which is why nothing here has to be transcribed."""
    return (int(score) - 10) // 2


def surges_per_day(class_surges: int | None, con_score: int) -> int:
    """A character's healing surge pool: the class's own number plus the Constitution modifier.

    The class number comes from the class entry in a book this framework may not reproduce,
    so it is a required argument rather than a default. Passing None refuses rather than
    inventing a pool, because the surge pool is 4e's real attrition clock and a wrong one
    silently rewrites the difficulty of every day.
    """
    if class_surges is None:
        raise TableMissing(
            "a healing surge pool is the class's own number of surges per day plus the "
            "Constitution modifier. The class number is in the class entry of the Player's "
            "Handbook, which has no open-content release — pass it with --surges, or set it "
            "later with `state.py surge set <who> --max <n>`."
        )
    return int(class_surges) + ability_modifier(con_score)
PC_ROLES = ("controller", "defender", "leader", "striker")
MONSTER_ROLES = ("artillery", "brute", "controller", "lurker", "minion", "skirmisher", "soldier")
MONSTER_RANKS = ("standard", "elite", "solo", "minion")
_mech(
    "roles",
    "D&D 4e assigns every class one of four roles — controller, defender, leader, striker — and "
    "every monster one of seven roles plus a rank of standard, elite, solo or minion. A minion has "
    "exactly 1 hit point and takes no damage from a missed attack. The roles are the edition's "
    "main encounter-design handle, and are why a 4e fight is built by composition rather than by "
    "spending a budget on whatever fits",
)


def blank_character_fields(level: int = 1) -> dict[str, Any]:
    """The 4e-shaped half of a character in state.json."""
    return {
        "role": None,
        "abilities": {a: 10 for a in ABILITIES},
        "defences": {"ac": 10, "fortitude": 10, "reflex": 10, "will": 10},
        "half_level": int(level) // 2,
        "initiative_mod": 0,
        "speed": 6,  # 4e measures movement in squares, not feet
        "strength": 10,
        "healing_surges": {"max": 0, "used": 0},
        "second_wind_used": False,
        "hp_below_zero": 0,
        "death_saves": {"failures": 0},
        "action_points": 1,
        "milestones": 0,
        "powers": {"encounter": [], "daily": []},
        "magic_items": [],
    }


RESOURCES = ("healing_surges", "action_points", "powers", "second_wind_used", "death_saves")
RESOURCE_HINTS = {
    "hero": "4e has action points, not Hero Points — use `action-point spend`.",
    "inspiration": "4e has action points, not Heroic Inspiration — use `action-point spend`.",
    "focus": "4e has no Focus Points — encounter and daily powers do that work.",
    "dying": "4e tracks dying with death saving throw failures and a below-zero hit point "
             "total — use `death-save` and `hp-below`.",
    "wounded": "4e has no wounded condition; the bloodied condition is keyed to half hit points.",
    "doomed": "4e has no doomed condition; three death saving throw failures is the death clock.",
    "refocus": "4e has no Refocus — a short rest restores encounter powers.",
    "hit": "4e has no Hit Dice; healing surges are the per-day healing pool.",
    "hit-dice": "4e has no Hit Dice; healing surges are the per-day healing pool — use `surge spend`.",
    "exhaustion": "4e has no Exhaustion track.",
    "attunement": "4e has no attunement limit; magic items are limited by slot and by item level.",
    "concentration": "4e has sustained powers rather than Concentration — record them as conditions.",
    "slots": "4e has no spell slots; powers are at-will, encounter or daily — use `power use`.",
    "long": "4e's equivalent is an extended rest — use `extended-rest`.",
    "short": "4e's short rest is 5 minutes — use `short-rest`.",
}


# --------------------------------------------------------------------------------------
# The action economy
# --------------------------------------------------------------------------------------

ACTION_ECONOMY = {
    "kind": "slots",
    "actions_per_turn": 1,
    "has_map": False,
    "has_bonus_action": False,
    "tracks_movement_separately": False,
    "summary": "One standard, one move and one minor action a turn, in any order, plus any number "
               "of free actions; a standard can be traded down for a move or a minor, and a move "
               "for a minor. One immediate action per round (an interrupt or a reaction, on "
               "somebody else's turn) and one opportunity action per other creature's turn. "
               "Movement is spent by the move action and measured in squares.",
}
_mech(
    "action_economy",
    "A D&D 4e turn is one standard action, one move action and one minor action, usable in any "
    "order, plus any number of free actions. A standard action may be traded down for a move or a "
    "minor and a move for a minor, but never upward. Separately, a creature gets one immediate "
    "action per round — an interrupt or a reaction, taken on another creature's turn — and one "
    "opportunity action per other creature's turn. Movement belongs to the move action and is "
    "counted in squares of five feet rather than in feet, which is the unit this framework stores",
)

ENCOUNTER_COLUMNS = (("std", 4), ("mov", 4), ("min", 4), ("imm", 4), ("rxn", 4))


def blank_combatant_fields(**kw: Any) -> dict[str, Any]:
    return {
        "standard_available": True,
        "move_available": True,
        "minor_available": True,
        "immediate_available": True,
        "squares_moved": 0,
        "speed": int(kw.get("speed", 6) or 6),
        "reaction_available": True,
        "reaction_used_for": None,
        "marked_by": None,
        "rank": kw.get("rank") or "standard",
        "role": kw.get("role"),
    }


def reset_turn(c: dict[str, Any]) -> str:
    """Reset per-turn resources. The immediate action is per ROUND, not per turn."""
    c["standard_available"] = True
    c["move_available"] = True
    c["minor_available"] = True
    c["squares_moved"] = 0
    c["immediate_available"] = True
    c["reaction_available"] = True
    c["reaction_used_for"] = None
    return (f"standard + move + minor, {int(c.get('speed', 6) or 6)} squares of movement, "
            f"immediate and opportunity actions available")


def combatant_action_cells(c: dict[str, Any]) -> list[str]:
    def pip(flag: Any) -> str:
        return "◆" if flag else "◇"
    speed = int(c.get("speed", 6) or 6)
    moved = int(c.get("squares_moved", 0))
    return [
        pip(c.get("standard_available")),
        f"{pip(c.get('move_available'))}{max(0, speed - moved)}",
        pip(c.get("minor_available")),
        pip(c.get("immediate_available")),
        "yes" if c.get("reaction_available") else "used",
    ]


def spend_action(c: dict[str, Any], kind: str, n: int = 1) -> str:
    """Spend a standard, move, minor or immediate action, or squares of movement."""
    k = str(kind).lower().replace("_", "-")
    aliases = {"any": "standard", "action": "standard", "std": "standard",
               "mov": "move", "min": "minor", "imm": "immediate", "move-action": "move"}
    k = aliases.get(k, k)

    if k in ("standard", "move", "minor", "immediate"):
        field = f"{k}_available"
        if not c.get(field):
            # 4e lets you trade down, so say what is still possible rather than just refusing.
            spare = [x for x in ("standard", "move", "minor")
                     if c.get(f"{x}_available") and _can_trade(x, k)]
            hint = (f" You still have a {spare[0]} action, which can be traded down to a {k}."
                    if spare else "")
            raise ValueError(f"{c['name']} has already used their {k} action this turn.{hint}")
        c[field] = False
        return f"{k} action spent"

    if k in ("squares", "square"):
        speed = int(c.get("speed", 6) or 6)
        moved = int(c.get("squares_moved", 0)) + n
        if moved > speed:
            raise ValueError(
                f"{c['name']} has {speed - int(c.get('squares_moved', 0))} square(s) of movement "
                f"left of a speed of {speed} and cannot move {n}"
            )
        c["squares_moved"] = moved
        return f"moved {n} square(s) ({speed - moved} of {speed} left)"

    if k in ("trade", "trade-down"):
        raise ValueError(
            "say what you are trading for: `--kind move` or `--kind minor` spends the action "
            "itself, and 4e lets a standard be traded down for a move or a minor, and a move "
            "for a minor"
        )

    raise ValueError(
        f"{kind!r} is not something a 4e turn spends (standard, move, minor, immediate, squares)"
    )


def _can_trade(have: str, want: str) -> bool:
    """4e allows trading down only: standard -> move -> minor."""
    order = {"standard": 3, "move": 2, "minor": 1}
    return order.get(have, 0) > order.get(want, 0)


# --------------------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------------------

SHEET_COLUMNS = ("HP", "AC", "Fort", "Ref", "Will", "Surges", "AP", "2nd wind", "Conditions")
SLOT_ABBREV = "P"


def sheet_lines(pc: dict[str, Any], *, conditions: str = "—") -> list[str]:
    hp = pc.get("hp", {})
    temp = f" +{hp.get('temp')}t" if hp.get("temp") else ""
    below = int(pc.get("hp_below_zero", 0))
    cur = f"{hp.get('current', 0)}/{hp.get('max', 0)}{temp}"
    if below:
        cur = f"{-below}/{hp.get('max', 0)}{temp}"
    d = pc.get("defences", {})
    s = pc.get("healing_surges") or {}
    return [
        cur,
        str(d.get("ac", 0)),
        str(d.get("fortitude", 0)),
        str(d.get("reflex", 0)),
        str(d.get("will", 0)),
        f"{int(s.get('max', 0)) - int(s.get('used', 0))}/{s.get('max', 0)}",
        str(pc.get("action_points", 0)),
        "used" if pc.get("second_wind_used") else "ready",
        conditions,
    ]


def status_lines(pc: dict[str, Any]) -> list[str]:
    out: list[str] = []
    hp = pc.get("hp") or {}
    below = int(pc.get("hp_below_zero", 0))
    mx = int(hp.get("max", 0))
    if mx:
        if below:
            out.append(f"at {-below} hit points — dying; death at {death_threshold(mx)}")
        elif int(hp.get("current", 0)) <= mx // 2:
            out.append(f"BLOODIED ({hp.get('current')}/{mx})")
    ds = pc.get("death_saves") or {}
    if int(ds.get("failures", 0)):
        out.append(f"death saving throw failures {ds['failures']}/{DEATH_SAVE_FAILURES}")
    s = pc.get("healing_surges") or {}
    if int(s.get("max", 0)):
        left = int(s["max"]) - int(s.get("used", 0))
        out.append(f"healing surges {left}/{s['max']}"
                   + (f" (each restores {surge_value(mx)} HP)" if mx else ""))
    out.append(f"action points {pc.get('action_points', 0)}"
               + (f", {pc['milestones']} milestone(s) this day" if pc.get("milestones") else ""))
    out.append("Second Wind: " + ("used this encounter" if pc.get("second_wind_used") else "ready"))
    powers = pc.get("powers") or {}
    for bucket in ("encounter", "daily"):
        entries = powers.get(bucket) or []
        if entries:
            left = [e["name"] for e in entries if not e.get("used")]
            out.append(f"{bucket} powers {len(left)}/{len(entries)}"
                       + (f" — {', '.join(left)}" if left else " — all spent"))
    return out


def tracked_condition_flags(pc: dict[str, Any]) -> list[str]:
    out = ["**DEAD**"] if pc.get("dead") else []
    if pc.get("dead"):
        return out
    hp = pc.get("hp") or {}
    mx = int(hp.get("max", 0))
    below = int(pc.get("hp_below_zero", 0))
    ds = pc.get("death_saves") or {}
    if below or (mx and int(hp.get("current", 1)) == 0):
        out.append(f"**dying {ds.get('failures', 0)}/{DEATH_SAVE_FAILURES}**")
    elif mx and int(hp.get("current", 0)) <= mx // 2:
        out.append("**bloodied**")
    if pc.get("marked_by"):
        out.append(f"marked by {pc['marked_by']}")
    return out


DASHBOARD_RESOURCE_COLUMNS = ("Surges", "AP", "2nd wind", "Encounter powers", "Daily powers")


def dashboard_stats(pc: dict[str, Any]) -> list[tuple[str, Any]]:
    d = pc.get("defences") or {}
    return [
        ("AC", d.get("ac", 0)),
        ("Fort", d.get("fortitude", 0)),
        ("Ref", d.get("reflex", 0)),
        ("Will", d.get("will", 0)),
        ("Init", f"{int(pc.get('initiative_mod', 0)):+d}"),
        ("Speed", f"{pc.get('speed', 6)} sq"),
    ]


def dashboard_resource_cells(pc: dict[str, Any]) -> list[str]:
    s = pc.get("healing_surges") or {}
    powers = pc.get("powers") or {}

    def bucket(name: str) -> str:
        entries = powers.get(name) or []
        if not entries:
            return ""
        left = sum(1 for e in entries if not e.get("used"))
        return f"{left} / {len(entries)}"

    return [
        f"{int(s.get('max', 0)) - int(s.get('used', 0))} / {s.get('max', 0)}" if s.get("max") else "",
        str(pc.get("action_points", 0)),
        "used" if pc.get("second_wind_used") else "ready",
        bucket("encounter"),
        bucket("daily"),
    ]


def dashboard_dire_tags(pc: dict[str, Any]) -> list[str]:
    return [t.replace("**", "") for t in tracked_condition_flags(pc)]


# --------------------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------------------


def validate_character(pc: dict[str, Any], name: str, current_hp: int, max_hp: int) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []

    s = pc.get("healing_surges") or {}
    smax, sused = int(s.get("max", 0)), int(s.get("used", 0))
    if sused < 0:
        out.append(("error", f"{name}: negative healing surges spent ({sused})"))
    if sused > smax:
        out.append(("error", f"{name}: {sused} healing surges spent of {smax}"))
    if max_hp and not smax:
        out.append(("warn", f"{name}: no healing surge pool recorded — in 4e the surge pool is the "
                            f"real attrition clock, so set it before play"))

    ap = pc.get("action_points", 0)
    if isinstance(ap, int) and ap < 0:
        out.append(("error", f"{name}: negative action points ({ap})"))

    below = int(pc.get("hp_below_zero", 0))
    if below < 0:
        out.append(("error", f"{name}: hp_below_zero is {below}; it counts how far BELOW zero the "
                             f"character is and so is never negative"))
    if below and current_hp > 0:
        out.append(("error", f"{name}: {below} hit points below zero recorded while at "
                             f"{current_hp} HP"))
    if below and max_hp and -below <= death_threshold(max_hp) and not pc.get("dead"):
        out.append(("error", f"{name}: at {-below} hit points, which is at or past the death "
                             f"threshold of {death_threshold(max_hp)}, but not recorded dead"))

    ds = pc.get("death_saves") or {}
    fails = int(ds.get("failures", 0))
    if fails < 0:
        out.append(("error", f"{name}: negative death saving throw failures ({fails})"))
    elif fails > DEATH_SAVE_FAILURES:
        out.append(("error", f"{name}: {fails} death saving throw failures, above the "
                             f"{DEATH_SAVE_FAILURES} that kill"))
    elif fails >= DEATH_SAVE_FAILURES and not pc.get("dead"):
        out.append(("error", f"{name}: {fails} death saving throw failures but not recorded dead"))
    if fails and current_hp > 0:
        out.append(("error", f"{name}: death saving throw failures recorded while at "
                             f"{current_hp} HP — they clear on regaining hit points"))

    if pc.get("role") and str(pc["role"]).lower() not in PC_ROLES:
        out.append(("warn", f"{name}: role {pc['role']!r} is not one of "
                            f"{', '.join(PC_ROLES)}"))

    half = pc.get("half_level")
    if half is not None and int(half) != int(pc.get("level", 1)) // 2:
        out.append(("warn", f"{name}: half_level {half} recorded, but level "
                            f"{pc.get('level')} gives {int(pc.get('level', 1)) // 2}"))
    if int(pc.get("level", 1)) > MAX_LEVEL:
        out.append(("error", f"{name}: level {pc.get('level')} is above 4e's maximum of {MAX_LEVEL}"))

    powers = pc.get("powers") or {}
    for bucket in powers:
        if bucket not in ("encounter", "daily"):
            out.append(("error", f"{name}: power bucket {bucket!r} — 4e powers this framework "
                                 f"tracks are `encounter` and `daily` (at-will powers need no "
                                 f"tracking)"))

    for stray in ("hero_points", "focus", "dying", "wounded", "doomed", "hit_dice",
                  "exhaustion", "heroic_inspiration", "attunement", "spell_slots"):
        if pc.get(stray):
            out.append(("error", f"{name}: has a `{stray}` field, which belongs to another "
                                 f"ruleset — this campaign runs {SYSTEM_SHORT}"))
    return out


def validate_combatant(c: dict[str, Any], name: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    if c.get("map_step") is not None:
        out.append(("error", f"combatant {name} has a MAP step, which is a Pathfinder rule"))
    speed, moved = int(c.get("speed", 6) or 6), int(c.get("squares_moved", 0))
    if moved < 0:
        out.append(("error", f"combatant {name} has moved {moved} squares"))
    elif moved > speed:
        out.append(("error", f"combatant {name} has moved {moved} squares of a {speed}-square speed"))
    if c.get("rank") and str(c["rank"]).lower() not in MONSTER_RANKS:
        out.append(("warn", f"combatant {name} has rank {c['rank']!r}; 4e ranks are "
                            f"{', '.join(MONSTER_RANKS)}"))
    if c.get("role") and str(c["role"]).lower() not in MONSTER_ROLES + PC_ROLES:
        out.append(("warn", f"combatant {name} has role {c['role']!r}, which is not a 4e role"))
    if str(c.get("rank", "")).lower() == "minion":
        hp = c.get("hp") or {}
        if hp and int(hp.get("max", 1)) != 1:
            out.append(("warn", f"combatant {name} is a minion with {hp.get('max')} hit points; "
                                f"a 4e minion has exactly 1"))
    return out


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------


def _print_table(rows: Sequence[dict[str, Any]], cols: Sequence[str]) -> None:
    if not rows:
        print("(nothing)")
        return
    widths = {c: max(len(c), *(len(str(r.get(c, ""))) for r in rows)) for c in cols}
    print("  ".join(c.ljust(widths[c]) for c in cols))
    print("  ".join("-" * widths[c] for c in cols))
    for r in rows:
        print("  ".join(str(r.get(c, "")).ljust(widths[c]) for c in cols))


def cmd_tables(args: argparse.Namespace) -> int:
    status = table_status()
    print("# D&D 4e tables — what is filled and what is not\n")
    print(f"File: tools/{TABLES_PATH.name}\n")
    _print_table(
        [{"table": s["table"], "filled": f"{s['filled']}/{s['entries']}" if s["entries"] else "—",
          "ready": "yes" if s["ready"] else "NO"} for s in status],
        ["table", "filled", "ready"],
    )
    missing = [s for s in status if not s["ready"]]
    print()
    if not missing:
        print("Every table has at least one value. Run the commands you need and they will say if "
              "a specific level is missing.")
    else:
        print(f"{len(missing)} of {len(status)} table(s) are empty:\n")
        for s in missing:
            print(f"  {s['table']}")
            print(f"      read from: {s['source']}")
        print()
        print("D&D 4e has no open-content release, so this framework ships none of these values.")
        print("Fill in what your campaign needs — a heroic-tier campaign needs levels 1-10 of")
        print("three tables and nothing else. The tools refuse to compute rather than guessing.")
    meta = tables().get("_meta") or {}
    if meta.get("books_used"):
        print(f"\nTranscribed from: {meta['books_used']}")
    if (tables().get("dc_by_level") or {}).get("_printing"):
        print(f"DC table printing: {tables()['dc_by_level']['_printing']}")
    return 0


def cmd_sources(args: argparse.Namespace) -> int:
    print("Provenance of everything in tools/dnd4e.py\n")
    print("⚠ THIS RULESET'S PROVENANCE IS WEAKER THAN ITS TWO SIBLINGS', AND NOT BY CHOICE.\n")
    print(PROVENANCE)
    print()
    for key in sorted(SOURCES):
        flags = []
        if key in UNSOURCEABLE:
            flags.append("MECHANIC, NO OPEN SOURCE")
        if key in CONVENTION_TABLES:
            flags.append("FRAMEWORK CONVENTION")
        print(f"[{' / '.join(flags) or 'verified'}] {key}")
        print(f"    {SOURCES[key]}\n")
    total = len(SOURCES)
    print(f"{len(UNSOURCEABLE)} of {total} entries are mechanics stated from the books with no "
          f"open source to verify against.")
    print(f"{len(CONVENTION_TABLES)} of {total} are this framework's own convention.")
    print("0 numeric tables ship with this ruleset. See `python3 tools/dnd4e.py tables`.")
    print("\nContrast: `pf2e.py sources` cites Archives of Nethys page by page under the ORC")
    print("License, and `dnd5e.py sources` cites SRD 5.2 under CC-BY-4.0 with an independent")
    print("cross-check. Neither is possible here. LICENSE_NOTES.md explains why.")
    return 0


def cmd_encounter(args: argparse.Namespace) -> int:
    try:
        budgets = encounter_budgets(args.party_size, args.party_level)
    except TableMissing as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"Party: {args.party_size} character(s) at level {args.party_level} "
          f"({tier_name(args.party_level)} tier)\n")
    _print_table([{"difficulty": k, "party budget": v} for k, v in budgets.items()],
                 ["difficulty", "party budget"])
    print("\n4e builds an encounter by composition — roles and ranks — as much as by budget.")
    print(f"Roles: {', '.join(MONSTER_ROLES)}. Ranks: {', '.join(MONSTER_RANKS)}.")
    print("A minion has 1 hit point. An elite counts as more than one standard monster and a")
    print("solo as several; the multipliers are in your tables file.")
    if args.monster:
        total = 0
        parts = []
        for spec in args.monster:
            m = re.fullmatch(r"(?:(\d+)x)?(\d+)(?::(\w+))?", spec.strip(), re.IGNORECASE)
            if not m:
                print(f"error: cannot read {spec!r}; write it as LEVEL, LEVEL:ROLE or "
                      f"Nx LEVEL:ROLE, e.g. 3x4:minion", file=sys.stderr)
                return 2
            n = int(m.group(1) or 1)
            lvl = int(m.group(2))
            rank = (m.group(3) or "standard").lower()
            try:
                xp = creature_xp(lvl, rank)
            except TableMissing as exc:
                print(f"error: {exc}", file=sys.stderr)
                return 2
            total += n * xp
            parts.append(f"{n} x level {lvl} {rank} ({xp} XP each)")
        print(f"\nBuilt encounter: {', '.join(parts)}")
        print(f"  total {total} XP → {rate_encounter(total, args.party_size, args.party_level)}")
        print(f"  XP awarded, divided among {args.party_size}: "
              f"{xp_award(total, args.party_size)} each")
    return 0


def cmd_dc(args: argparse.Namespace) -> int:
    try:
        if args.level is None:
            raise TableMissing("pass --level; 4e DCs rise with level")
        row = _need("dc_by_level", args.level)
    except TableMissing as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"Level {args.level} DCs: " + ", ".join(f"{k} {v}" for k, v in row.items()))
    print("\n4e DCs rise with level, as Pathfinder's do and D&D 2024's do not.")
    print("NOTE the published table was revised by errata; "
          f"this file records the printing as {tables()['dc_by_level'].get('_printing')!r}.")
    return 0


def cmd_treasure(args: argparse.Namespace) -> int:
    try:
        t = treasure_for(args.level, args.party_size)
    except TableMissing as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"Level {args.level} treasure parcels:\n")
    for i, parcel in enumerate(t["parcels"], start=1):
        print(f"  {i}. {parcel}")
    print(f"\n{t['note']}")
    return 0


def cmd_settlement(args: argparse.Namespace) -> int:
    try:
        settlement_availability(args.settlement)
    except TableMissing as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


def cmd_advancement(args: argparse.Namespace) -> int:
    rows = []
    for lvl in range(1, MAX_LEVEL + 1):
        try:
            xp = xp_to_level(lvl)
            xp_s = f"{xp:,}" if xp is not None else "—"
        except TableMissing:
            xp_s = "(not filled)"
        rows.append({"level": lvl, "XP (cumulative)": xp_s, "tier": tier_name(lvl),
                     "scope band": rules.scope_band(SYSTEM_ID, lvl)})
    _print_table(rows, ["level", "XP (cumulative)", "tier", "scope band"])
    print(f"\n4e runs to level {MAX_LEVEL} in three tiers of ten. Both sibling rulesets stop at")
    print("20, so a 4e level number is not comparable — `world.py convert` maps scope instead.")
    return 0


def cmd_mechanics(args: argparse.Namespace) -> int:
    print("# D&D 4e, in the shape this framework stores it\n")
    print(f"Tiers: " + ", ".join(f"{n} {lo}-{hi}" for lo, hi, n in TIERS) + f" (max {MAX_LEVEL})")
    print(f"Defences: {', '.join(DEFENCE_NAMES[d] for d in DEFENCES)} — the attacker rolls "
          f"against these; there is no defensive save")
    print(f"Saving throw: a flat d20 against {SAVE_DC}, at the end of your turn, to end a "
          f"'save ends' effect")
    print(f"Combat advantage: +{COMBAT_ADVANTAGE} to attack")
    print(f"Half level is added to: {', '.join(HALF_LEVEL_APPLIES_TO)}")
    print(f"\nTurn: {ACTION_ECONOMY['summary']}")
    print(f"\nHealing surge: one quarter of maximum hit points; the per-day pool is the real")
    print(f"attrition clock. Second Wind spends one as a standard action, once per encounter,")
    print(f"and grants +2 to all defences until the start of your next turn.")
    print(f"Bloodied at half hit points or fewer. Death at a negative total equal to the")
    print(f"bloodied value, so a 40 HP character dies at -20.")
    print(f"Dying: a flat d20 death saving throw at the end of each turn, "
          f"{DEATH_SAVE_FAILURES} failures before an extended rest is death; a natural 20")
    print(f"spends a healing surge instead.")
    print(f"\nShort rest: {SHORT_REST_MINUTES} minutes — encounter powers and Second Wind back.")
    print(f"Extended rest: {EXTENDED_REST_HOURS} hours — everything back, one per 24 hours.")
    print(f"\nPC roles: {', '.join(PC_ROLES)}")
    print(f"Monster roles: {', '.join(MONSTER_ROLES)}")
    print(f"Monster ranks: {', '.join(MONSTER_RANKS)} — a minion has exactly 1 hit point")
    print(f"\nCoins: {', '.join(COIN_ORDER)}, where 1 pp = 100 gp (not 10, as in the siblings).")
    print(f"Movement is in squares of five feet, not feet.")
    print(f"\n{CRIT_RULE}")
    print(f"\n⚠ {PROVENANCE}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dnd4e.py",
        description="D&D 4e rules structure. The numbers are yours to supply — see `tables`.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("tables", help="which owner-supplied tables are filled")
    sub.add_parser("sources", help="the provenance of everything here, and why it is weaker")
    sub.add_parser("mechanics", help="4e's shape as this framework stores it")
    sub.add_parser("advancement", help="levels, tiers and scope bands")

    e = sub.add_parser("encounter", help="encounter budget and composition")
    e.add_argument("--party-level", type=int, required=True)
    e.add_argument("--party-size", type=int, default=5)
    e.add_argument("--monster", nargs="*",
                   help="monsters to price: LEVEL, LEVEL:ROLE, or Nx LEVEL:ROLE (e.g. 3x4:minion)")

    d = sub.add_parser("dc", help="DCs by level")
    d.add_argument("--level", type=int, default=None)

    t = sub.add_parser("treasure", help="the treasure parcels for a level")
    t.add_argument("--level", type=int, required=True)
    t.add_argument("--party-size", type=int, default=5)

    s = sub.add_parser("settlement", help="what can be bought where")
    s.add_argument("settlement")

    r = sub.add_parser("resolve", help="resolve one d20 (what roll.py uses)")
    r.add_argument("--total", type=int, required=True)
    r.add_argument("--dc", type=int, required=True)
    r.add_argument("--natural", type=int)
    r.add_argument("--kind", default="check",
                   choices=["check", "save", "attack", "flat", "death-save"])
    return p


def cmd_resolve(args: argparse.Namespace) -> int:
    print(json.dumps(resolve(args.total, args.dc, args.natural, kind=args.kind), indent=2))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    fns = {
        "tables": cmd_tables, "sources": cmd_sources, "mechanics": cmd_mechanics,
        "advancement": cmd_advancement, "encounter": cmd_encounter, "dc": cmd_dc,
        "treasure": cmd_treasure, "settlement": cmd_settlement, "resolve": cmd_resolve,
    }
    try:
        return fns[args.cmd](args)
    except TableMissing as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except (ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
