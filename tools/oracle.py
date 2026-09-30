#!/usr/bin/env python3
"""oracle.py — ask the fiction a question and let the dice answer.

Every oracle result goes through the same engine and the same audit log as any other
roll, tagged `oracle`. The rule that makes the oracle worth having is in
system/19-solo-oracle.md: **an oracle result is binding on the GM.** It is taken as
established fact and built forward from, including when it wrecks the prep.

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

from roll import (  # noqa: E402
    DiceError,
    append_log,
    campaign_dir,
    find_table,
    make_roll,
    parse_tables,
    repo_root,
    roll_expression,
)

# The likelihood ladder. A d20 at or above the threshold is a yes.
#   yes-rate = (21 - threshold) / 20
LADDER: dict[str, int] = {
    "almost-certain": 2,
    "very-likely": 4,
    "likely": 6,
    "even": 11,
    "unlikely": 16,
    "very-unlikely": 18,
    "almost-impossible": 20,
}
LADDER_LABELS = {
    "almost-certain": "Almost certain",
    "very-likely": "Very likely",
    "likely": "Likely",
    "even": "Even",
    "unlikely": "Unlikely",
    "very-unlikely": "Very unlikely",
    "almost-impossible": "Almost impossible",
}

AND_BUT_MARGIN = 5  # clearing (or missing) by this much or more adds an "and"
BUT_MARGIN = 2  # landing within this of the threshold adds a "but"

# Scene check thresholds on a d20. This ladder is the framework's own design, not a
# published PF2e or Mythic table; it is stated here so it can be argued with.
SCENE_INTERRUPTED_MAX = 2
SCENE_ALTERED_MAX = 7

TABLES_DOC = "system/16-random-tables.md"
MEANING_PAIRS = {
    "action-theme": ("Oracle Actions", "Oracle Themes"),
    "descriptor-focus": ("Oracle Descriptors", "Oracle Focuses"),
}

REACTION_LADDER = [
    (2, "hostile — they act against you now"),
    (5, "unfriendly — they refuse and remember it"),
    (9, "wary — they hedge, and want something first"),
    (14, "indifferent — they will deal, on ordinary terms"),
    (18, "friendly — they help, within reason"),
    (20, "helpful — they go out of their way, and say why"),
]


def normalise_odds(text: str) -> str:
    key = re.sub(r"[^a-z]+", "-", str(text).strip().lower()).strip("-")
    if key in LADDER:
        return key
    aliases = {
        "certain": "almost-certain",
        "sure": "almost-certain",
        "probable": "likely",
        "fifty-fifty": "even",
        "even-odds": "even",
        "coin-flip": "even",
        "doubtful": "unlikely",
        "improbable": "very-unlikely",
        "impossible": "almost-impossible",
        "no-way": "almost-impossible",
    }
    if key in aliases:
        return aliases[key]
    hits = [k for k in LADDER if k.startswith(key)]
    if len(hits) == 1:
        return hits[0]
    raise DiceError(f"{text!r} is not on the ladder. Use one of: {', '.join(LADDER)}")


def interpret(natural: int, threshold: int, odds: str) -> dict[str, Any]:
    """Turn a d20 face into a yes/no with its and/but qualifier and any flags."""
    yes = natural >= threshold
    margin = natural - threshold
    if yes:
        if margin >= AND_BUT_MARGIN:
            answer = "yes, and"
            gloss = "yes, plus something extra in your favour"
        elif margin <= BUT_MARGIN:
            answer = "yes, but"
            gloss = "yes, with a complication attached"
        else:
            answer = "yes"
            gloss = "a plain yes"
    else:
        if margin <= -AND_BUT_MARGIN:
            answer = "no, and"
            gloss = "no, and it is worse than that"
        elif margin >= -BUT_MARGIN:
            answer = "no, but"
            gloss = "no, but something softens it"
        else:
            answer = "no"
            gloss = "a plain no"

    flags: list[str] = []
    if natural in (1, 20):
        flags.append("random event — roll on a table in system/16-random-tables.md and fold it in")
    if natural == 20 and threshold <= LADDER["likely"]:
        flags.append("exceptional: an emphatic yes to an already-likely question — it comes with consequences")
    if natural == 1 and threshold >= LADDER["unlikely"]:
        flags.append("exceptional: an emphatic no to an already-unlikely question — the door is shut hard")
    return {
        "answer": answer,
        "gloss": gloss,
        "yes": yes,
        "margin": margin,
        "flags": flags,
        "odds": odds,
        "threshold": threshold,
    }


def log(campaign: str | None, r: Any, extra: dict[str, Any] | None = None) -> None:
    if not campaign:
        return
    rec = r.log_record(campaign, None, None)
    if extra:
        rec.setdefault("extra", {}).update(extra)
    append_log(campaign_dir(campaign) / "logs" / "rolls.jsonl", rec)


def cmd_ask(args: argparse.Namespace) -> int:
    odds = normalise_odds(args.odds)
    threshold = LADDER[odds]
    question = " ".join(args.question) if isinstance(args.question, list) else args.question
    out: list[dict[str, Any]] = []
    for _ in range(max(1, args.repeat)):
        r = make_roll(
            "oracle",
            "1d20",
            label=f"Oracle ({LADDER_LABELS[odds]}, yes on {threshold}+): {question}",
            tags=["oracle"],
            transparency="glass",  # an oracle answer is always shown; that is the point
        )
        nat = r.result.natural or 0
        res = interpret(nat, threshold, odds)
        log(args.campaign, r, {"oracle": res, "question": question})
        out.append({"natural": nat, **res})
    if args.json:
        print(json.dumps({"question": question, "odds": odds, "threshold": threshold, "results": out}, indent=2))
        return 0
    if args.repeat > 1:
        yes = sum(1 for o in out if o["yes"])
        print(f"{yes}/{args.repeat} yes ({yes / args.repeat:.1%}); expected {(21 - threshold) / 20:.1%}")
        return 0
    res = out[0]
    print(f"🔮 {question}")
    print(f"   {LADDER_LABELS[odds]} — yes on {threshold}+ · rolled [{res['natural']}]")
    print(f"   → **{res['answer'].upper()}** — {res['gloss']}")
    for f in res["flags"]:
        print(f"   ! {f}")
    print("   This answer is binding. Build forward from it (system/19-solo-oracle.md).")
    return 0


def cmd_scene(args: argparse.Namespace) -> int:
    expectation = " ".join(args.expectation) if isinstance(args.expectation, list) else (args.expectation or "")
    r = make_roll("oracle-scene", "1d20", label=f"Scene check: {expectation}", tags=["oracle", "scene"],
                  transparency="glass")
    nat = r.result.natural or 0
    if nat <= SCENE_INTERRUPTED_MAX:
        verdict = "INTERRUPTED"
        gloss = "something else arrives first and the scene you expected does not get to start"
    elif nat <= SCENE_ALTERED_MAX:
        verdict = "ALTERED"
        gloss = "the scene happens, but one of its assumptions is wrong — change a detail that matters"
    else:
        verdict = "AS EXPECTED"
        gloss = "the scene opens the way you thought it would"
    log(args.campaign, r, {"scene": {"verdict": verdict, "expectation": expectation}})
    if args.json:
        print(json.dumps({"natural": nat, "verdict": verdict, "expectation": expectation}, indent=2))
        return 0
    print(f"🔮 Scene check — expected: {expectation or '(unstated)'}")
    print(f"   rolled [{nat}] on d20 → **{verdict}** — {gloss}")
    print(f"   Ladder: 1-{SCENE_INTERRUPTED_MAX} interrupted, "
          f"{SCENE_INTERRUPTED_MAX + 1}-{SCENE_ALTERED_MAX} altered, {SCENE_ALTERED_MAX + 1}-20 as expected.")
    if verdict == "INTERRUPTED":
        print("   Roll the interruption on a table in system/16-random-tables.md.")
    return 0


def _tables() -> dict[str, list[tuple[int, int, str]]]:
    path = repo_root() / TABLES_DOC
    if not path.exists():
        raise DiceError(f"{TABLES_DOC} is not present, so there are no meaning tables to roll on")
    return parse_tables(path.read_text(encoding="utf-8"))


def cmd_meaning(args: argparse.Namespace) -> int:
    if args.pair not in MEANING_PAIRS:
        raise DiceError(f"pair must be one of {', '.join(MEANING_PAIRS)}")
    tables = _tables()
    words = []
    for name in MEANING_PAIRS[args.pair]:
        heading, entries = find_table(tables, name)
        die = max(h for _, h, _ in entries)
        r = make_roll("oracle-meaning", f"1d{die}", label=heading, tags=["oracle", "meaning"],
                      transparency="glass")
        value = r.result.total
        text = next((t for lo, hi, t in entries if lo <= value <= hi), "(gap)")
        log(args.campaign, r, {"table": heading, "entry": text})
        words.append((heading, value, text))
    if args.json:
        print(json.dumps([{"table": h, "rolled": v, "entry": t} for h, v, t in words], indent=2))
        return 0
    print("🔮 Meaning — " + args.pair)
    for h, v, t in words:
        print(f"   {h} [{v}] → {t}")
    print("   Read the pair together. If it says nothing, re-roll once and say you did.")
    return 0


def cmd_howmany(args: argparse.Namespace) -> int:
    m = re.fullmatch(r"\s*(\d+)\s*-\s*(\d+)\s*", args.range)
    if not m:
        raise DiceError(f"cannot read a range out of {args.range!r} (want '1-6')")
    lo, hi = int(m.group(1)), int(m.group(2))
    if hi < lo:
        raise DiceError("the range runs backwards")
    span = hi - lo + 1
    r = make_roll("oracle-quantity", f"1d{span}", label=f"How many: {args.label or args.range}",
                  tags=["oracle", "quantity"], transparency="glass")
    value = lo + r.result.total - 1
    log(args.campaign, r, {"range": [lo, hi], "value": value})
    if args.json:
        print(json.dumps({"range": [lo, hi], "value": value}, indent=2))
        return 0
    print(f"🔮 {args.label or 'How many'} — range {lo}-{hi}, rolled 1d{span} → **{value}**")
    return 0


def cmd_reaction(args: argparse.Namespace) -> int:
    mod = args.mod
    expr = f"1d20{mod:+d}" if mod else "1d20"
    r = make_roll("oracle-reaction", expr, label=f"NPC reaction: {args.who or 'NPC'}",
                  tags=["oracle", "reaction"], transparency="glass")
    total = r.result.total
    verdict = REACTION_LADDER[-1][1]
    for cap, text in REACTION_LADDER:
        if total <= cap:
            verdict = text
            break
    log(args.campaign, r, {"reaction": verdict, "who": args.who})
    if args.json:
        print(json.dumps({"total": total, "reaction": verdict}, indent=2))
        return 0
    print(f"🔮 Reaction — {args.who or 'NPC'}: {r.result.faces_line()} = {total} → **{verdict}**")
    print("   Use this only where the rules do not already cover it — a real Diplomacy check beats it.")
    return 0


def cmd_calibrate(args: argparse.Namespace) -> int:
    """Roll each rung of the ladder many times and show the observed yes-rate."""
    n = args.n
    print(f"Oracle ladder calibration — {n} rolls per rung, real dice through roll.py\n")
    print(f"{'odds':<20} {'yes on':>7} {'expected':>9} {'observed':>9} {'diff':>7} {'2 s.e.':>7}  verdict")
    print("-" * 82)
    ok = True
    for key, threshold in LADDER.items():
        p = (21 - threshold) / 20
        yes = 0
        for _ in range(n):
            if (roll_expression("1d20").total) >= threshold:
                yes += 1
        obs = yes / n
        se = (p * (1 - p) / n) ** 0.5
        diff = obs - p
        within = abs(diff) <= 2 * se + 1e-12
        ok = ok and within
        print(f"{LADDER_LABELS[key]:<20} {str(threshold) + '+':>7} {p:>8.2%} {obs:>8.2%} "
              f"{diff:>+7.2%} {2 * se:>7.2%}  {'ok' if within else 'OUT OF RANGE'}")
    print()
    print("Expected yes-rate is (21 - threshold) / 20. 'ok' means the observed rate is within")
    print("two standard errors of it, which is the ~95% band for a fair d20.")
    return 0 if ok else 1


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="oracle.py", description="Ask the world a question; the dice answer.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name: str, help_: str) -> argparse.ArgumentParser:
        p = sub.add_parser(name, help=help_)
        p.add_argument("--campaign", default=None, help="log the roll to this campaign's rolls.jsonl")
        p.add_argument("--json", action="store_true")
        return p

    p = add("ask", "a yes/no question at stated odds")
    p.add_argument("question", nargs="+")
    p.add_argument("--odds", default="even", help=", ".join(LADDER))
    p.add_argument("--repeat", type=int, default=1, help="roll it many times (for testing the ladder)")

    p = add("scene", "does the scene open as expected, altered, or interrupted")
    p.add_argument("--expectation", nargs="+", default=[])

    p = add("meaning", "an interpretive word pair")
    p.add_argument("--pair", default="action-theme", choices=list(MEANING_PAIRS))

    p = add("howmany", "a bounded quantity")
    p.add_argument("--range", required=True, help="e.g. 1-6")
    p.add_argument("--label", default=None)

    p = add("reaction", "an NPC's reaction where no rule covers it")
    p.add_argument("--who", default=None)
    p.add_argument("--mod", type=int, default=0)

    p = sub.add_parser("ladder", help="print the published ladder")
    p = sub.add_parser("calibrate", help="verify the ladder's yes-rates against the dice")
    p.add_argument("-n", type=int, default=2000)
    return ap


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.cmd == "ask":
            return cmd_ask(args)
        if args.cmd == "scene":
            return cmd_scene(args)
        if args.cmd == "meaning":
            return cmd_meaning(args)
        if args.cmd == "howmany":
            return cmd_howmany(args)
        if args.cmd == "reaction":
            return cmd_reaction(args)
        if args.cmd == "calibrate":
            return cmd_calibrate(args)
        if args.cmd == "ladder":
            print(f"{'Odds':<20} {'Yes on':>8} {'Yes-rate':>9}")
            for k, v in LADDER.items():
                print(f"{LADDER_LABELS[k]:<20} {str(v) + '+':>8} {(21 - v) / 20:>8.0%}")
            print(f"\nClear the threshold by {AND_BUT_MARGIN}+ → 'yes, and'. "
                  f"Land within {BUT_MARGIN} of it → 'yes, but' or 'no, but'.")
            print(f"Miss it by {AND_BUT_MARGIN}+ → 'no, and'. A natural 1 or 20 triggers a random event.")
            return 0
    except DiceError as exc:
        print(f"oracle.py: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
