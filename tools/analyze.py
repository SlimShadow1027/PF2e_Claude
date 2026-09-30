#!/usr/bin/env python3
"""analyze.py — read the roll log back and say what it shows.

An audit log is only worth keeping if something reads it. This reports over
`campaigns/<slug>/logs/rolls.jsonl`, writes `logs/dice-audit.md`, and prints a summary.

The section that matters is **fairness**, and specifically the public-versus-private split:
if secret checks and enemy saves drift favourable or unfavourable relative to public rolls,
that shows up here and nowhere else. Numbers are reported with their sample size and their
standard error, so a gap can be read as noise or not rather than being handed over as a
verdict.

Standard library only — the chi-square p-value is computed from the series for the
incomplete gamma function rather than pulled from scipy.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

from roll import atomic_write, campaign_dir, repo_root, utc_now  # noqa: E402

D20_MEAN = 10.5
D20_VARIANCE = (20 * 20 - 1) / 12.0  # 33.25

# A chi-square p-value below this on a large sample is worth saying out loud.
SUSPICIOUS_P = 0.01
WATCH_P = 0.05


# --------------------------------------------------------------------------------------
# Statistics, from the standard library only
# --------------------------------------------------------------------------------------


def _lower_gamma_reg(s: float, x: float) -> float:
    """Regularised lower incomplete gamma P(s, x), by series then continued fraction."""
    if x < 0 or s <= 0:
        raise ValueError("bad arguments to the incomplete gamma function")
    if x == 0:
        return 0.0
    if x < s + 1:
        term = 1.0 / s
        total = term
        n = s
        for _ in range(1000):
            n += 1
            term *= x / n
            total += term
            if abs(term) < abs(total) * 1e-15:
                break
        return total * math.exp(-x + s * math.log(x) - math.lgamma(s))
    # continued fraction for Q(s, x), then P = 1 - Q
    tiny = 1e-300
    b = x + 1 - s
    c = 1 / tiny
    d = 1 / b
    h = d
    for i in range(1, 1000):
        an = -i * (i - s)
        b += 2
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < 1e-15:
            break
    q = math.exp(-x + s * math.log(x) - math.lgamma(s)) * h
    return 1 - q


def chi_square_p(stat: float, df: int) -> float:
    """P(X > stat) for a chi-square with df degrees of freedom."""
    if df <= 0:
        return float("nan")
    if stat <= 0:
        return 1.0
    return max(0.0, min(1.0, 1.0 - _lower_gamma_reg(df / 2.0, stat / 2.0)))


def uniform_chi_square(counts: dict[int, int], faces: int) -> tuple[float, int, float]:
    n = sum(counts.values())
    if n == 0:
        return float("nan"), faces - 1, float("nan")
    expected = n / faces
    stat = sum((counts.get(f, 0) - expected) ** 2 / expected for f in range(1, faces + 1))
    df = faces - 1
    return stat, df, chi_square_p(stat, df)


def longest_run(values: Sequence[int], pred) -> int:
    best = cur = 0
    for v in values:
        cur = cur + 1 if pred(v) else 0
        best = max(best, cur)
    return best


def binom_se(p: float, n: int) -> float:
    return math.sqrt(p * (1 - p) / n) if n > 0 else float("nan")


# --------------------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------------------


def log_path(campaign: str | None, explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).expanduser()
    if not campaign:
        raise SystemExit("analyze.py: pass --campaign <slug> or --log <path>")
    return campaign_dir(campaign) / "logs" / "rolls.jsonl"


def load_records(path: Path) -> tuple[list[dict[str, Any]], int]:
    if not path.exists():
        raise SystemExit(f"analyze.py: no roll log at {path}")
    records: list[dict[str, Any]] = []
    bad = 0
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                bad += 1
                continue
            if isinstance(rec, dict):
                records.append(rec)
            else:
                bad += 1
    return records, bad


def filter_records(
    records: list[dict[str, Any]],
    since: str | None,
    actor: str | None,
    kind: str | None,
    tag: str | None,
) -> list[dict[str, Any]]:
    out = records
    if since:
        m = re.fullmatch(r"session-(\d+)", since.strip(), re.IGNORECASE)
        if m:
            n = int(m.group(1))
            out = [r for r in out if (r.get("session") or 0) >= n]
        elif re.fullmatch(r"\d+", since.strip()):
            n = int(since)
            out = [r for r in out if (r.get("seq") or 0) >= n]
        else:
            out = [r for r in out if str(r.get("ts", "")) >= since]
    if actor:
        a = actor.lower()
        out = [r for r in out if str(r.get("actor") or "").lower() == a]
    if kind:
        out = [r for r in out if r.get("kind") == kind]
    if tag:
        out = [r for r in out if tag in (r.get("tags") or [])]
    return out


def d20_faces(records: Iterable[dict[str, Any]]) -> list[int]:
    """Every d20 face rolled, kept or dropped.

    Dropped dice count: the question this answers is whether the random source is fair,
    and a die that was rolled and then discarded by a keep-highest still came out of it.
    """
    faces: list[int] = []
    for r in records:
        for g in r.get("dice") or []:
            if g.get("faces") == 20:
                faces.extend(int(v) for v in g.get("rolls") or [])
    return faces


def is_private(r: dict[str, Any]) -> bool:
    return bool(r.get("secret")) or bool(r.get("private")) or not r.get("shown", True)


# --------------------------------------------------------------------------------------
# Report sections
# --------------------------------------------------------------------------------------


def fairness_block(records: list[dict[str, Any]], label: str) -> list[str]:
    faces = d20_faces(records)
    n = len(faces)
    L: list[str] = []
    if n == 0:
        return [f"**{label}** — no d20 faces in this subset."]
    mean = sum(faces) / n
    se = math.sqrt(D20_VARIANCE / n)
    z = (mean - D20_MEAN) / se if se else float("nan")
    counts = Counter(faces)
    stat, df, p = uniform_chi_square(counts, 20)
    nat20, nat1 = counts.get(20, 0), counts.get(1, 0)
    exp_nat = n / 20
    L.append(f"**{label}** — {n} d20 face(s)")
    L.append("")
    L.append(f"- Mean **{mean:.4f}** against an expected {D20_MEAN}. "
             f"Standard error {se:.4f}, so the gap is {mean - D20_MEAN:+.4f} — that is "
             f"{abs(z):.2f} standard errors.")
    L.append(f"- Chi-square against a uniform d20: **{stat:.2f}** on {df} degrees of freedom, "
             f"p = **{p:.4f}**.")
    L.append(f"- Natural 20s: {nat20} against an expected {exp_nat:.1f} "
             f"({nat20 / n:.2%} vs 5.00%, s.e. {binom_se(0.05, n):.2%}).")
    L.append(f"- Natural 1s: {nat1} against an expected {exp_nat:.1f} "
             f"({nat1 / n:.2%} vs 5.00%, s.e. {binom_se(0.05, n):.2%}).")
    L.append(f"- Longest run of 11 or more: {longest_run(faces, lambda v: v >= 11)}; "
             f"of 10 or less: {longest_run(faces, lambda v: v <= 10)}.")
    L.append("")
    L.append("Face distribution:")
    L.append("")
    L.append("```")
    widest = max(counts.get(f, 0) for f in range(1, 21)) or 1
    for f in range(1, 21):
        c = counts.get(f, 0)
        bar = "#" * max(0, round(c / widest * 40))
        dev = c - exp_nat
        L.append(f"{f:>2} {c:>7} {dev:>+8.1f} {bar}")
    L.append("```")
    L.append("")
    return L


def verdict_lines(records: list[dict[str, Any]]) -> list[str]:
    """Say something unprompted when the numbers look off, and nothing when they do not."""
    out: list[str] = []
    pub = [r for r in records if not is_private(r)]
    prv = [r for r in records if is_private(r)]
    for label, subset in (("all rolls", records), ("public rolls", pub), ("private rolls", prv)):
        faces = d20_faces(subset)
        if len(faces) < 200:
            continue
        stat, df, p = uniform_chi_square(Counter(faces), 20)
        mean = sum(faces) / len(faces)
        se = math.sqrt(D20_VARIANCE / len(faces))
        z = (mean - D20_MEAN) / se
        if p < SUSPICIOUS_P:
            out.append(f"⚠ {label}: the face distribution is a poor fit to a uniform d20 "
                       f"(chi-square p = {p:.4f} on {len(faces)} faces). That is worth looking at.")
        elif p < WATCH_P:
            out.append(f"· {label}: chi-square p = {p:.4f} on {len(faces)} faces — inside the range "
                       "a fair die produces about one time in twenty, so worth a second look later, "
                       "not an alarm.")
        if abs(z) > 3:
            out.append(f"⚠ {label}: mean {mean:.3f} is {z:+.2f} standard errors from 10.5.")
    pf, vf = d20_faces(pub), d20_faces(prv)
    if len(pf) >= 200 and len(vf) >= 200:
        pm, vm = sum(pf) / len(pf), sum(vf) / len(vf)
        se = math.sqrt(D20_VARIANCE / len(pf) + D20_VARIANCE / len(vf))
        z = (vm - pm) / se
        line = (f"Public mean {pm:.3f} ({len(pf)} faces) against private mean {vm:.3f} "
                f"({len(vf)} faces): difference {vm - pm:+.3f}, {abs(z):.2f} standard errors.")
        if abs(z) > 2.5:
            out.append("⚠ " + line + " The two subsets do not look like the same die.")
        else:
            out.append("· " + line + " No drift between what is shown and what is withheld.")
    if not out:
        out.append("· Nothing in the fairness numbers looks off. Sample sizes are printed above so "
                   "you can judge that for yourself rather than take it on faith.")
    return out


def play_block(records: list[dict[str, Any]]) -> list[str]:
    L: list[str] = []
    checks = [r for r in records if r.get("degree") and r.get("kind") in
              ("check", "save", "recovery", "fortune", "misfortune")]

    # Per character
    by_actor: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in checks:
        by_actor[str(r.get("actor") or "(unnamed)")].append(r)
    if by_actor:
        L.append("### Per character")
        L.append("")
        L.append("| Character | Checks | Mean d20 | Success rate | s.e. | Crit success | Crit failure |")
        L.append("|---|---|---|---|---|---|---|")
        for actor, rs in sorted(by_actor.items(), key=lambda kv: -len(kv[1])):
            faces = d20_faces(rs)
            mean = sum(faces) / len(faces) if faces else float("nan")
            succ = sum(1 for r in rs if (r.get("degree_index") or 0) >= 2)
            rate = succ / len(rs)
            L.append(f"| {actor} | {len(rs)} | {mean:.2f} | {rate:.1%} | "
                     f"{binom_se(rate, len(rs)):.1%} | "
                     f"{sum(1 for r in rs if r.get('degree_index') == 3)} | "
                     f"{sum(1 for r in rs if r.get('degree_index') == 0)} |")
        L.append("")
        L.append("Sample size sits next to every rate on purpose: a three-roll weakness is not a pattern.")
        L.append("")

    # Per label (skill / save)
    by_label: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in checks:
        lbl = re.sub(r"\s*\(.*?\)\s*", "", str(r.get("label") or "(unlabelled)")).strip() or "(unlabelled)"
        by_label[lbl].append(r)
    interesting = {k: v for k, v in by_label.items() if len(v) >= 1}
    if interesting:
        L.append("### Per check")
        L.append("")
        L.append("| Check | n | Success rate | s.e. | Mean d20 |")
        L.append("|---|---|---|---|---|")
        for lbl, rs in sorted(interesting.items(), key=lambda kv: -len(kv[1]))[:25]:
            faces = d20_faces(rs)
            rate = sum(1 for r in rs if (r.get("degree_index") or 0) >= 2) / len(rs)
            L.append(f"| {lbl} | {len(rs)} | {rate:.1%} | {binom_se(rate, len(rs)):.1%} | "
                     f"{(sum(faces) / len(faces)) if faces else float('nan'):.2f} |")
        L.append("")

    # Degrees overall
    if checks:
        L.append("### Degrees of success")
        L.append("")
        counts = Counter(r.get("degree") for r in checks)
        L.append("| Degree | n | Share |")
        L.append("|---|---|---|")
        for d in ("critical success", "success", "failure", "critical failure"):
            c = counts.get(d, 0)
            L.append(f"| {d} | {c} | {c / len(checks):.1%} |")
        L.append("")

    # Saves specifically — which one is actually the weak one
    saves = [r for r in checks if r.get("kind") == "save"]
    if saves:
        by_save: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for r in saves:
            lbl = str(r.get("label") or "")
            which = next((w for w in ("Fortitude", "Reflex", "Will") if w.lower() in lbl.lower()), "(unnamed)")
            by_save[which].append(r)
        L.append("### Saves")
        L.append("")
        L.append("| Save | n | Success rate | s.e. |")
        L.append("|---|---|---|---|")
        rows = []
        for w, rs in by_save.items():
            rate = sum(1 for r in rs if (r.get("degree_index") or 0) >= 2) / len(rs)
            rows.append((w, len(rs), rate))
            L.append(f"| {w} | {len(rs)} | {rate:.1%} | {binom_se(rate, len(rs)):.1%} |")
        L.append("")
        usable = [r for r in rows if r[1] >= 10]
        if len(usable) >= 2:
            usable.sort(key=lambda t: t[2])
            lo, hi = usable[0], usable[-1]
            L.append(f"Weakest save so far: **{lo[0]}** at {lo[2]:.1%} over {lo[1]} rolls, against "
                     f"{hi[0]} at {hi[2]:.1%} over {hi[1]}. Gap: {hi[2] - lo[2]:.1%}.")
        else:
            L.append("Not enough save rolls yet to call one of them the weak one.")
        L.append("")

    # Multiple attack penalty steps
    attacks = [r for r in checks if r.get("map_step") is not None or r.get("kind") == "check"]
    by_map: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for r in attacks:
        step = int(r.get("map_step") or 0)
        if re.search(r"strike|attack|slam|claw|bite|jaws|shot", str(r.get("label") or ""), re.IGNORECASE):
            by_map[step].append(r)
    if by_map:
        L.append("### Attack routines by multiple-attack-penalty step")
        L.append("")
        L.append("| MAP step | n | Hit rate | s.e. | Crit rate |")
        L.append("|---|---|---|---|---|")
        for step in sorted(by_map):
            rs = by_map[step]
            rate = sum(1 for r in rs if (r.get("degree_index") or 0) >= 2) / len(rs)
            crit = sum(1 for r in rs if r.get("degree_index") == 3) / len(rs)
            L.append(f"| {step} ({0 if step == 0 else -5 * step} nominal) | {len(rs)} | {rate:.1%} | "
                     f"{binom_se(rate, len(rs)):.1%} | {crit:.1%} |")
        L.append("")
        L.append("This is the table that tends to show whether a third attack is worth taking.")
        L.append("")

    # Damage taken and combat load, from the log's own tags
    dmg = [r for r in records if r.get("kind") == "damage"]
    if dmg:
        totals = [int(r.get("total") or 0) for r in dmg]
        L.append("### Damage rolled")
        L.append("")
        L.append(f"- {len(dmg)} damage roll(s), total {sum(totals)}, mean {sum(totals) / len(totals):.1f}, "
                 f"largest {max(totals)}.")
        crits = [r for r in dmg if r.get("crit")]
        L.append(f"- {len(crits)} of them critical ({len(crits) / len(dmg):.1%}).")
        L.append("")

    recoveries = [r for r in records if r.get("kind") == "recovery"]
    if recoveries:
        L.append("### Dying and recovery")
        L.append("")
        vals = [int(((r.get("extra") or {}).get("dying_before")) or 0) for r in recoveries]
        L.append(f"- {len(recoveries)} recovery check(s) made"
                 + (f", at dying values {', '.join(str(v) for v in sorted(set(v for v in vals if v)))}"
                    if any(vals) else "")
                 + ".")
        succ = sum(1 for r in recoveries if (r.get("degree_index") or 0) >= 2)
        L.append(f"- {succ} succeeded, {len(recoveries) - succ} did not.")
        L.append("")

    hero = [r for r in records if "fortune" in (r.get("tags") or []) or r.get("kind") == "fortune"]
    L.append("### Hero Points")
    L.append("")
    if hero:
        L.append(f"- {len(hero)} fortune reroll(s) in the log. What each was spent on:")
        for r in hero[:20]:
            L.append(f"  - seq {r.get('seq')}: {r.get('label') or '(unlabelled)'} "
                     f"→ {r.get('degree') or r.get('total')}")
    else:
        L.append("- No fortune rerolls in the log yet. Hero Point *spends* are recorded in "
                 "`state.json` and the checkpoint commits; only rerolls leave a die behind.")
    L.append("")

    oracle = [r for r in records if "oracle" in (r.get("tags") or [])]
    if oracle:
        yes = sum(1 for r in oracle if ((r.get("extra") or {}).get("oracle") or {}).get("yes"))
        asks = [r for r in oracle if ((r.get("extra") or {}).get("oracle"))]
        L.append("### Oracle")
        L.append("")
        L.append(f"- {len(oracle)} oracle roll(s), of which {len(asks)} were yes/no questions; "
                 f"{yes} came back yes.")
        L.append("- Every one of them is binding on the GM (system/19-solo-oracle.md).")
        L.append("")

    offscreen = [r for r in records if "offscreen" in (r.get("tags") or [])]
    if offscreen:
        L.append(f"### Off-screen turns\n\n- {len(offscreen)} roll(s) tagged `offscreen` — the world "
                 "moving between sessions.\n")
    return L


def kind_table(records: list[dict[str, Any]]) -> list[str]:
    counts = Counter(r.get("kind") for r in records)
    L = ["| Kind | n |", "|---|---|"]
    for k, c in counts.most_common():
        L.append(f"| {k} | {c} |")
    return L


def build_report(campaign: str | None, path: Path, records: list[dict[str, Any]], bad: int,
                 args: argparse.Namespace) -> str:
    pub = [r for r in records if not is_private(r)]
    prv = [r for r in records if is_private(r)]
    L: list[str] = []
    a = L.append
    a(f"# Dice audit — {campaign or path}")
    a("")
    a(f"Generated {utc_now()} from `{path}`.")
    a("")
    a(f"{len(records)} roll(s) in scope"
      + (f" (filtered: {args.since or ''} {args.actor or ''} {args.kind or ''} {args.tag or ''})".rstrip()
         if (args.since or args.actor or args.kind or args.tag) else "")
      + (f"; {bad} unparseable line(s) skipped" if bad else "") + ".")
    a("")
    if not records:
        a("The log is empty. Nothing to report — and nothing has been invented to fill the space.")
        return "\n".join(L) + "\n"
    a("## Fairness")
    a("")
    a("Does the framework actually roll straight? Every number below carries its sample size and, "
      "where it applies, its standard error, so you can tell noise from a pattern yourself.")
    a("")
    L += fairness_block(records, "All d20 rolls")
    a("### Public versus private")
    a("")
    a("This is the check that matters. A GM that quietly tilts secret checks and enemy saves would "
      "show up here and nowhere else, so the two subsets are reported side by side.")
    a("")
    L += fairness_block(pub, "Public rolls (shown to the player)")
    L += fairness_block(prv, "Private and secret rolls (number withheld)")
    a("### What that adds up to")
    a("")
    for line in verdict_lines(records):
        a(f"- {line}")
    a("")
    a("## Play")
    a("")
    a("What the numbers say about the campaign.")
    a("")
    L += play_block(records)
    a("## Rolls by kind")
    a("")
    L += kind_table(records)
    a("")
    a("---")
    a("")
    a("Regenerate with `python3 tools/analyze.py --campaign " + (campaign or "<slug>") + "`.")
    return "\n".join(L) + "\n"


def one_line_summary(records: list[dict[str, Any]]) -> str:
    faces = d20_faces(records)
    if not faces:
        return "Dice: no d20 rolls logged this session."
    n = len(faces)
    mean = sum(faces) / n
    se = math.sqrt(D20_VARIANCE / n)
    stat, df, p = uniform_chi_square(Counter(faces), 20)
    pub, prv = d20_faces([r for r in records if not is_private(r)]), d20_faces(
        [r for r in records if is_private(r)])
    split = ""
    if pub and prv:
        split = (f"; public mean {sum(pub) / len(pub):.2f} over {len(pub)}, "
                 f"private {sum(prv) / len(prv):.2f} over {len(prv)}")
    return (f"Dice: {n} d20 face(s), mean {mean:.2f} against 10.5 (s.e. {se:.2f}), "
            f"chi-square p = {p:.3f}{split}.")


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="analyze.py", description="Audit the roll log.")
    ap.add_argument("--campaign", default=None)
    ap.add_argument("--log", default=None, help="an explicit rolls.jsonl path")
    ap.add_argument("--out", default=None, help="where to write the report (default logs/dice-audit.md)")
    ap.add_argument("--since", default=None, help="'session-7', a seq number, or an ISO timestamp")
    ap.add_argument("--actor", default=None)
    ap.add_argument("--kind", default=None)
    ap.add_argument("--tag", default=None)
    ap.add_argument("--fairness", action="store_true", help="print only the fairness section")
    ap.add_argument("--one-line", action="store_true", help="print the one-line session summary only")
    ap.add_argument("--no-write", action="store_true", help="print, do not write dice-audit.md")
    args = ap.parse_args(argv)

    path = log_path(args.campaign, args.log)
    records, bad = load_records(path)
    records = filter_records(records, args.since, args.actor, args.kind, args.tag)

    if args.one_line:
        print(one_line_summary(records))
        return 0

    report = build_report(args.campaign, path, records, bad, args)

    if args.fairness:
        head, _, _ = report.partition("## Play")
        print(head.rstrip())
    else:
        print(report)

    if not args.no_write and args.campaign:
        out = Path(args.out) if args.out else campaign_dir(args.campaign) / "logs" / "dice-audit.md"
        atomic_write(out, report)
        print(f"\nwritten to {out.relative_to(repo_root()) if repo_root() in out.parents else out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
