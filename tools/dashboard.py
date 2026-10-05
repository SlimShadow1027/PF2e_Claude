#!/usr/bin/env python3
"""dashboard.py — one self-contained HTML file per campaign.

Scrolling terminal history to find current HP mid-combat is the worst part of playing this
way, so this renders `state.json` plus a few Markdown files into
`campaigns/<slug>/dashboard.html`.

- **Read-only.** The dashboard reflects state and never writes it. Every edit goes through
  `tools/state.py`; `state.json` stays the single source of truth.
- **Offline.** Standard library only, no build step, and nothing is fetched at runtime. The
  CSS is inlined and there is no JavaScript. It opens from `file://` with no internet.
- **It respects the transparency mode**, or it would leak enemy hit points.
- **It says when it was generated**, so a stale file is obvious rather than quietly misleading.

Standard library only.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Any, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

from roll import atomic_write, campaign_dir, repo_root, utc_now  # noqa: E402
import pf2e  # noqa: E402
import rules  # noqa: E402
import state as st  # noqa: E402

# Wounded descriptors, used instead of enemy numbers in `standard` and `mystery`. These
# bands are this framework's own convention, not a published rule.
DESCRIPTORS = (
    (1.00, "unhurt"),
    (0.75, "lightly hurt"),
    (0.50, "hurt"),
    (0.25, "badly hurt"),
    (0.01, "barely standing"),
    (0.00, "down"),
)


def esc(x: Any) -> str:
    return html.escape("" if x is None else str(x), quote=True)


def descriptor(current: int, maximum: int) -> str:
    if maximum <= 0:
        return "unknown"
    frac = max(0.0, current / maximum)
    for cut, word in DESCRIPTORS:
        if frac >= cut:
            return word
    return "down"


def hp_class(current: int, maximum: int) -> str:
    if maximum <= 0:
        return "ok"
    frac = current / maximum
    if frac <= 0:
        return "down"
    if frac <= 0.25:
        return "crit"
    if frac <= 0.5:
        return "warn"
    return "ok"


CSS = """
:root {
  color-scheme: light dark;
  --bg: #f6f6f4;
  --panel: #ffffff;
  --panel-2: #f0f0ee;
  --ink: #1b1b1a;
  --ink-dim: #5c5c58;
  --line: #d8d8d2;
  --ok: #2f7d4f;
  --warn: #b26a00;
  --crit: #b3261e;
  --down: #6b2321;
  --accent: #3a4a7a;
  --radius: 10px;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #131315;
    --panel: #1c1c1f;
    --panel-2: #24242a;
    --ink: #ececea;
    --ink-dim: #a0a09c;
    --line: #34343a;
    --ok: #5cc98a;
    --warn: #e0a341;
    --crit: #ef6f66;
    --down: #b3554e;
    --accent: #9fb0e6;
  }
}
:root[data-theme="dark"] {
  --bg: #131315;
  --panel: #1c1c1f;
  --panel-2: #24242a;
  --ink: #ececea;
  --ink-dim: #a0a09c;
  --line: #34343a;
  --ok: #5cc98a;
  --warn: #e0a341;
  --crit: #ef6f66;
  --down: #b3554e;
  --accent: #9fb0e6;
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font: 15px/1.5 ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  padding: 16px;
}
.wrap { max-width: 1100px; margin: 0 auto; }
header { margin-bottom: 18px; }
h1 { font-size: 1.35rem; margin: 0 0 2px; letter-spacing: -0.01em; }
.gen { color: var(--ink-dim); font-size: 0.8rem; font-variant-numeric: tabular-nums; }
.gen strong { color: var(--ink); font-weight: 600; }
h2 { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.08em;
     color: var(--ink-dim); margin: 26px 0 10px; font-weight: 700; }
.grid { display: grid; gap: 12px; grid-template-columns: 1fr; }
@media (min-width: 620px) { .grid.two { grid-template-columns: 1fr 1fr; } }
@media (min-width: 900px) { .grid.cards { grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); } }
.card {
  background: var(--panel); border: 1px solid var(--line); border-radius: var(--radius);
  padding: 12px 14px; min-width: 0;
}
.card h3 { margin: 0 0 8px; font-size: 1.02rem; display: flex; justify-content: space-between;
           align-items: baseline; gap: 8px; flex-wrap: wrap; }
.card h3 .sub { font-size: 0.75rem; color: var(--ink-dim); font-weight: 400; }
.bar { height: 12px; background: var(--panel-2); border-radius: 6px; overflow: hidden;
       border: 1px solid var(--line); }
.bar > span { display: block; height: 100%; }
.bar .ok { background: var(--ok); }
.bar .warn { background: var(--warn); }
.bar .crit { background: var(--crit); }
.bar .down { background: var(--down); }
.bar .temp { background: var(--accent); opacity: 0.55; }
.hpline { display: flex; justify-content: space-between; font-variant-numeric: tabular-nums;
          font-size: 0.85rem; margin: 5px 0 2px; }
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(58px, 1fr)); gap: 6px;
         margin-top: 10px; }
.stat { background: var(--panel-2); border-radius: 7px; padding: 5px 6px; text-align: center; }
.stat b { display: block; font-size: 0.95rem; font-variant-numeric: tabular-nums; }
.stat span { font-size: 0.64rem; text-transform: uppercase; letter-spacing: 0.05em;
             color: var(--ink-dim); }
.tags { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 10px; }
.tag { font-size: 0.74rem; padding: 2px 7px; border-radius: 99px; background: var(--panel-2);
       border: 1px solid var(--line); }
.tag.bad { border-color: var(--crit); color: var(--crit); font-weight: 600; }
.tag.dire { background: var(--crit); color: var(--panel); border-color: var(--crit); font-weight: 700; }
table { width: 100%; border-collapse: collapse; font-size: 0.86rem; }
th, td { text-align: left; padding: 5px 7px; border-bottom: 1px solid var(--line);
         vertical-align: top; }
th { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--ink-dim); }
td.n, th.n { text-align: right; font-variant-numeric: tabular-nums; }
tr.turn td { background: var(--panel-2); font-weight: 600; }
.clock { font-variant-numeric: tabular-nums; }
.seg { letter-spacing: 1px; font-size: 1.05rem; }
pre { background: var(--panel-2); border: 1px solid var(--line); border-radius: var(--radius);
      padding: 10px; overflow-x: auto; font-size: 0.8rem; line-height: 1.35;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
.muted { color: var(--ink-dim); }
.scene p { margin: 6px 0; }
footer { margin-top: 30px; color: var(--ink-dim); font-size: 0.78rem;
         border-top: 1px solid var(--line); padding-top: 12px; }
.mode { display: inline-block; padding: 1px 7px; border-radius: 99px; border: 1px solid var(--line);
        background: var(--panel-2); font-size: 0.72rem; }
.empty { color: var(--ink-dim); font-style: italic; font-size: 0.86rem; }
"""


def read_markdown_section(path: Path, heading_re: str, limit: int = 40) -> list[str]:
    if not path.exists():
        return []
    out: list[str] = []
    grab = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if re.match(r"^#{1,6}\s", line):
            grab = bool(re.match(heading_re, line, re.IGNORECASE))
            continue
        if grab and line.strip():
            out.append(line.rstrip())
        if len(out) >= limit:
            break
    return out


def map_block(cdir: Path, slug_name: str | None) -> tuple[str, str] | None:
    """The current ASCII grid and its terrain key, if there is one."""
    mdir = cdir / "maps"
    if not mdir.is_dir():
        return None
    path = None
    if slug_name:
        cand = mdir / f"{slug_name}.md"
        if cand.exists():
            path = cand
    if path is None:
        files = [p for p in sorted(mdir.glob("*.md")) if not p.name.startswith("_")]
        if not files:
            return None
        path = max(files, key=lambda p: p.stat().st_mtime)
    text = path.read_text(encoding="utf-8")
    fences = re.findall(r"```[a-z]*\n(.*?)```", text, re.DOTALL)
    grid = fences[0].rstrip() if fences else ""
    key_lines = [l for l in text.splitlines() if l.strip().startswith("|")]
    return (path.stem, grid) if grid else None


def render(slug: str) -> str:
    cdir = campaign_dir(slug)
    data = st.load(slug)
    # Which game this campaign runs decides the stat tiles, the resources columns, the
    # unit weight is measured in, and what gets the prominent "decides a death" treatment.
    system = st.system_of(data)
    mod = st.rs(data)
    weight_field = st.ENCUMBRANCE_FIELD[system][0]
    mode = data.get("transparency", "standard")
    cp = data.get("last_checkpoint") or {}
    title = data.get("title") or slug
    enc = data.get("encounter")
    P: list[str] = []
    a = P.append

    a("<!doctype html>")
    a('<html lang="en"><head><meta charset="utf-8">')
    a('<meta name="viewport" content="width=device-width, initial-scale=1">')
    a(f"<title>{esc(title)} — dashboard</title>")
    a(f"<style>{CSS}</style>")
    a("</head><body><div class=\"wrap\">")

    # ---- header -----------------------------------------------------------
    a("<header>")
    a(f"<h1>{esc(title)}</h1>")
    a('<div class="gen">generated at <strong>' + esc(utc_now()) + "</strong> from checkpoint <strong>"
      + esc(cp.get("id") or "—") + "</strong>"
      + (f" ({esc(cp.get('name'))})" if cp.get("name") else "")
      + f' &middot; transparency <span class="mode">{esc(mode)}</span>'
      + f" &middot; session {esc(data.get('session_number', 0))}"
      + (" (in progress)" if data.get("session_in_progress") else "")
      + "</div>")
    a('<div class="gen">Read-only. Every edit goes through <code>tools/state.py</code>; '
      "<code>state.json</code> is the single source of truth.</div>")
    a("</header>")

    # ---- party ------------------------------------------------------------
    pcs = data.get("pcs") or {}
    a("<h2>Party</h2>")
    if not pcs:
        a('<p class="empty">No characters yet.</p>')
    else:
        a('<div class="grid cards">')
        for key, pc in pcs.items():
            hp = pc.get("hp") or {}
            cur, mx, temp = int(hp.get("current", 0)), int(hp.get("max", 0)), int(hp.get("temp", 0))
            cls = hp_class(cur, mx)
            pct = 0 if mx <= 0 else max(0, min(100, round(cur / mx * 100)))
            tpct = 0 if mx <= 0 else max(0, min(100 - pct, round(temp / mx * 100)))
            a('<div class="card">')
            a(f'<h3>{esc(pc.get("name", key))}<span class="sub">'
              f'{esc(pc.get("kind", "pc"))} &middot; level {esc(pc.get("level", 1))}</span></h3>')
            a(f'<div class="hpline"><span>HP</span><span>{cur} / {mx}'
              + (f' <span class="muted">+{temp} temp</span>' if temp else "")
              + "</span></div>")
            a(f'<div class="bar"><span class="{cls}" style="width:{pct}%"></span>'
              + (f'<span class="temp" style="width:{tpct}%"></span>' if tpct else "")
              + "</div>")
            a('<div class="stats">')
            for label, value in mod.dashboard_stats(pc):
                a(f'<div class="stat"><b>{esc(value)}</b><span>{esc(label)}</span></div>')
            a("</div>")
            # Whatever decides a death in this ruleset gets its own prominent treatment:
            # Pathfinder's dying/wounded/doomed, D&D's death saves and Exhaustion.
            dire = [f'<span class="tag dire">{esc(t)}</span>'
                    for t in mod.dashboard_dire_tags(pc)]
            conds = []
            for c in pc.get("conditions") or []:
                name = c["name"] + (f" {c['value']}" if c.get("value") else "")
                dur = c.get("duration") or {}
                if dur.get("kind") not in (None, "until-removed"):
                    name += f" &middot; {esc(st.describe_duration(dur))}"
                conds.append(f'<span class="tag bad">{name}</span>')
            for p_ in pc.get("persistent") or []:
                conds.append(f'<span class="tag bad">persistent {esc(p_.get("expr"))} '
                             f'{esc(p_.get("type", ""))}</span>')
            if dire or conds:
                a('<div class="tags">' + "".join(dire + conds) + "</div>")
            else:
                a('<div class="tags"><span class="tag">no conditions</span></div>')
            a("</div>")
        a("</div>")

    # ---- resources --------------------------------------------------------
    if pcs:
        a("<h2>Resources</h2>")
        a('<div class="card"><table><thead><tr><th>Character</th>'
          + "".join(f'<th>{esc(c)}</th>' for c in mod.DASHBOARD_RESOURCE_COLUMNS)
          + "<th>Consumables, ammunition, charges</th></tr></thead><tbody>")
        for key, pc in pcs.items():
            cells = mod.dashboard_resource_cells(pc)
            cons = []
            for it in pc.get("items") or []:
                if it.get("kind") in ("consumable", "ammunition") or it.get("charges") is not None:
                    bits = esc(it["name"])
                    if int(it.get("qty", 1)) != 1:
                        bits += f" &times;{it['qty']}"
                    if it.get("charges") is not None:
                        bits += f" ({it['charges']} charges)"
                    cons.append(bits)
            dash = '<span class="muted">—</span>'
            # The cells are pre-rendered by the ruleset and may contain &nbsp; and &middot;,
            # so they are not escaped again here; everything in them is ruleset-generated
            # except a Concentration target, which is escaped where it is built.
            a(f"<tr><td>{esc(pc.get('name', key))}</td>"
              + "".join(f'<td>{c or dash}</td>' for c in cells)
              + f"<td>{', '.join(cons) or dash}</td></tr>")
        a("</tbody></table></div>")

    # ---- encounter strip --------------------------------------------------
    if enc:
        a("<h2>Encounter — live</h2>")
        a('<div class="card">')
        a(f"<h3>{esc(enc.get('name'))}<span class=\"sub\">round {esc(enc.get('round', 1))}"
          + (f" &middot; maps/{esc(enc.get('map'))}.md" if enc.get("map") else "")
          + "</span></h3>")
        warn = "" if enc.get("telegraphed") else (
            ' <span class="tag bad">not yet telegraphed to the player</span>'
        )
        a(f"<p><strong>Objective:</strong> {esc(enc.get('objective'))}{warn}</p>")
        a('<table><thead><tr><th></th><th>Combatant</th><th class="n">Init</th><th>HP</th>'
          + "".join(f'<th class="n">{esc(n)}</th>' for n, _ in mod.ENCOUNTER_COLUMNS[:-1])
          + '<th>Reaction</th><th>Position</th>'
          "<th>Conditions</th></tr></thead><tbody>")
        idx = int(enc.get("turn_index", 0))
        for i, c in enumerate(enc.get("combatants") or []):
            hp = st.combatant_hp(data, c) or {}
            cur, mx = int(hp.get("current", 0)), int(hp.get("max", 0))
            if c.get("side") == "party" or mode == "glass":
                hp_text = f"{cur} / {mx}"
            else:
                hp_text = f'<span class="muted">{esc(descriptor(cur, mx))}</span>'
            if c.get("ref"):
                try:
                    _, pc = st.find_character(data, c["ref"])
                except st.StateError:
                    pc = {}
                cl = pc.get("conditions") or []
                flags = mod.dashboard_dire_tags(pc)
            else:
                cl = c.get("conditions") or []
                flags = mod.dashboard_dire_tags(c)
            cs = ", ".join(x["name"] + (f" {x['value']}" if x.get("value") else "") for x in cl)
            if flags:
                cs = ", ".join(f"<strong>{esc(t)}</strong>" for t in flags) + (f", {cs}" if cs else "")
            cells = mod.combatant_action_cells(c)
            a(f'<tr class="{"turn" if i == idx else ""}">'
              f'<td>{"&rarr;" if i == idx else ""}</td><td>{esc(c.get("name"))}'
              + (f' <span class="muted">(squad {esc(c["squad"])})</span>' if c.get("squad") else "")
              + f'</td><td class="n">{esc(c.get("initiative") if c.get("initiative") is not None else "—")}</td>'
              f"<td>{hp_text}</td>"
              + "".join(f'<td class="n">{esc(v)}</td>' for v in cells[:-1])
              + f'<td>{"available" if c.get("reaction_available") else esc("used: " + str(c.get("reaction_used_for") or ""))}</td>'
              f'<td>{esc(c.get("position") or "—")}</td><td>{cs or "—"}</td></tr>')
        a("</tbody></table>")
        if mode != "glass":
            a('<p class="gen">Enemy hit points show as descriptors because this campaign\'s '
              f"transparency mode is <code>{esc(mode)}</code>.</p>")
        a("</div>")

    # ---- inventory and money ---------------------------------------------
    a("<h2>Inventory and money</h2>")
    a('<div class="grid two">')
    gold = (data.get("party") or {}).get("gold") or {}
    a('<div class="card"><h3>Purse</h3><div class="stats">')
    for coin in ("pp", "gp", "sp", "cp"):
        a(f'<div class="stat"><b>{esc(int(gold.get(coin, 0)))}</b><span>{coin}</span></div>')
    a("</div>")
    a(f'<p class="gen">Total value {st.coins_to_cp(gold)} cp &middot; XP '
      f"{esc((data.get('party') or {}).get('xp', 0))} &middot; party level "
      f"{esc((data.get('party') or {}).get('level', 1))}</p></div>")

    rows = st.carry_report(data)
    unit = rows[0]["unit"] if rows else ("Bulk" if system == "pf2e" else "lb")
    a(f'<div class="card"><h3>Carried weight ({esc(unit)})</h3>')
    if rows:
        # D&D 2024 defines no intermediate encumbered band, so that column is only shown
        # where the ruleset actually has one rather than printed as a blank.
        has_band = any(r.get("encumbered_after") is not None for r in rows)
        a('<table><thead><tr><th>Carrier</th><th class="n">Carried</th>'
          + ('<th class="n">Encumbered after</th>' if has_band else "")
          + '<th class="n">Max</th><th></th></tr></thead><tbody>')
        for r in rows:
            flag = ('<span class="tag dire">over limit</span>' if r["over_max"]
                    else ('<span class="tag bad">encumbered</span>' if r["encumbered"] else ""))
            a(f'<tr><td>{esc(r["name"])}</td><td class="n">{float(r["carried"]):.1f}</td>'
              + (f'<td class="n">{esc(r["encumbered_after"])}</td>' if has_band else "")
              + f'<td class="n">{esc(r["max"])}</td>'
              f"<td>{flag}</td></tr>")
        a("</tbody></table>")
        if not has_band:
            a('<p class="muted">SRD 5.2 defines no intermediate encumbered band: '
              'you carry freely up to the maximum.</p>')
    else:
        a('<p class="empty">Nobody is carrying anything yet.</p>')
    a("</div></div>")

    carried = [(pc.get("name", k), pc.get("items") or []) for k, pc in pcs.items() if pc.get("items")]
    stash = (data.get("party") or {}).get("stash") or []
    if carried or stash:
        a('<div class="card"><h3>Carried items</h3><table><thead><tr><th>Who</th><th>Item</th>'
          '<th class="n">Qty</th><th class="n">' + esc(unit) + '</th><th>Kind</th><th class="n">Charges</th>'
          "</tr></thead><tbody>")
        for who, items in carried:
            for it in items:
                a(f"<tr><td>{esc(who)}</td><td>{esc(it['name'])}</td>"
                  f"<td class=\"n\">{esc(it.get('qty', 1))}</td>"
                  f"<td class=\"n\">{esc(it.get(weight_field, '-'))}</td>"
                  f"<td>{esc(it.get('kind', 'gear'))}</td>"
                  f"<td class=\"n\">{esc(it.get('charges')) if it.get('charges') is not None else '—'}</td></tr>")
        for it in stash:
            a(f"<tr><td class=\"muted\">stash</td><td>{esc(it['name'])}</td>"
              f"<td class=\"n\">{esc(it.get('qty', 1))}</td>"
              f"<td class=\"n\">{esc(it.get(weight_field, '-'))}</td>"
              f"<td>{esc(it.get('kind', 'gear'))}</td>"
              f"<td class=\"n\">{esc(it.get('charges')) if it.get('charges') is not None else '—'}</td></tr>")
        a("</tbody></table></div>")

    # ---- quests and clocks -----------------------------------------------
    clocks = data.get("clocks") or {}
    quests = data.get("quests") or {}
    if clocks or quests:
        a("<h2>Quests and clocks</h2>")
        a('<div class="grid two">')
        a('<div class="card"><h3>Clocks</h3>')
        if clocks:
            a('<table><thead><tr><th>Clock</th><th>Segments</th><th class="n"></th><th>Ticking</th>'
              "</tr></thead><tbody>")
            for name, c in clocks.items():
                seg, filled = int(c.get("segments", 0)), int(c.get("filled", 0))
                bar = "▰" * filled + "▱" * max(0, seg - filled)
                full = ' <span class="tag dire">full</span>' if filled >= seg and seg else ""
                a(f'<tr><td>{esc(name)}</td><td class="seg clock">{bar}</td>'
                  f'<td class="n">{filled}/{seg}{full}</td>'
                  f"<td>{esc(c.get('rate')) if c.get('ticking') else '—'}</td></tr>")
            a("</tbody></table>")
        else:
            a('<p class="empty">No clocks running.</p>')
        a("</div>")
        a('<div class="card"><h3>Quests</h3>')
        if quests:
            a("<table><thead><tr><th>Quest</th><th>Status</th><th>Next lead</th></tr></thead><tbody>")
            for name, q in quests.items():
                a(f"<tr><td>{esc(name)}</td><td>{esc(q.get('status'))}</td>"
                  f"<td>{esc(q.get('lead') or '—')}</td></tr>")
            a("</tbody></table>")
        else:
            a('<p class="empty">No quests recorded. QUESTS.md holds the prose.</p>')
        a("</div></div>")

    # ---- scene ------------------------------------------------------------
    notes = data.get("notes") or {}
    a("<h2>Scene</h2>")
    a('<div class="card scene">')
    a(f"<p><strong>Where:</strong> {esc(data.get('location', 'unset'))}</p>")
    a(f"<p><strong>When:</strong> {esc(pf2e.format_time(data.get('time')))}</p>")
    if notes.get("present"):
        a(f"<p><strong>Who is present:</strong> {esc(notes['present'])}</p>")
    if notes.get("situation"):
        a(f"<p>{esc(notes['situation'])}</p>")
    else:
        a('<p class="empty">No situation paragraph recorded at the last checkpoint.</p>')
    if notes.get("next_beats"):
        a(f'<p class="muted"><strong>Next likely beats:</strong> {esc(notes["next_beats"])}</p>')
    a("</div>")

    # ---- map --------------------------------------------------------------
    mb = map_block(cdir, (enc or {}).get("map"))
    if mb:
        name, grid = mb
        a("<h2>Tactical map</h2>")
        a(f'<div class="card"><h3>{esc(name)}<span class="sub">1 square = 5 ft</span></h3>')
        a(f"<pre>{esc(grid)}</pre></div>")

    # ---- relationships as a plain adjacency list -------------------------
    wpath = cdir / "WORLD.md"
    adj: list[str] = []
    if wpath.exists():
        text = wpath.read_text(encoding="utf-8")
        for line in text.splitlines():
            m = re.match(r"^\s*(\w+)\s*(-->|-\.->|==>|---)\|\"(.+?)\"\|\s*(\w+)\s*$", line)
            if m:
                adj.append(f"{m.group(1)} → {m.group(4)} ({m.group(3)})")
    if adj:
        a("<h2>Relationships</h2>")
        a('<div class="card"><p class="gen">A plain adjacency list, because this page fetches '
          "nothing at runtime. The rendered diagram is in WORLD.md.</p><ul>")
        for line in adj[:80]:
            a(f"<li>{esc(line)}</li>")
        a("</ul></div>")

    a("<footer>")
    a(f"Rendered by <code>tools/dashboard.py</code> from <code>campaigns/{esc(slug)}/state.json</code>. "
      "Regenerated at every checkpoint. Nothing on this page is fetched from the network, and nothing "
      "on it writes state.")
    a("</footer>")
    a("</div></body></html>")
    return "\n".join(P) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="dashboard.py", description="Render the campaign dashboard.")
    ap.add_argument("--campaign", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--stdout", action="store_true")
    args = ap.parse_args(argv)
    try:
        page = render(args.campaign)
    except st.StateError as exc:
        print(f"dashboard.py: {exc}", file=sys.stderr)
        return 2
    if args.stdout:
        sys.stdout.write(page)
        return 0
    out = Path(args.out) if args.out else campaign_dir(args.campaign) / "dashboard.html"
    atomic_write(out, page)
    try:
        shown = out.relative_to(repo_root())
    except ValueError:
        shown = out
    print(f"dashboard → {shown} ({len(page)} bytes, no network, opens from file://)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
