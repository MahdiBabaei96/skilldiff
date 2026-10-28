"""Render a comparison as Markdown (PR comments), JSON and a standalone HTML page."""
from __future__ import annotations

import html
import json
import re

MARKER = "<!-- skilldiff-report -->"

ICON = {"regressed": "🔴", "substituted": "🟠", "less-reliable": "🟠", "improved": "🟢", "unchanged": "⚪", "no-data": "⚫"}
LABEL = {
    "regressed": "rules broken",
    "substituted": "different skill ran",
    "less-reliable": "more failed runs",
    "improved": "improved",
    "unchanged": "no change",
    "no-data": "no valid runs",
}


def _skill(name: str) -> str:
    return "no skill" if name == "(none)" else f"`{name}`"


def _frac(d: dict | None) -> str:
    if not d or not d.get("n"):
        return "–"
    return f"{d['pass']}/{d['n']}"


def _money(x) -> str:
    if x is None:
        return "–"
    sign = "+" if x > 0 else ("−" if x < 0 else "±")
    return f"{sign}${abs(x):.3f}" if sign in "+−" else "$0.000"


def _subject(cmp: dict) -> str:
    changed = cmp["meta"].get("changed_skills", [])
    parts = []
    if cmp["new_skills"]:
        parts.append("adding " + ", ".join(f"`{s}`" for s in cmp["new_skills"]))
    if changed:
        parts.append("changing " + ", ".join(f"`{s}`" for s in changed))
    if cmp["removed_skills"]:
        parts.append("removing " + ", ".join(f"`{s}`" for s in cmp["removed_skills"]))
    if not parts:
        return "This change"
    s = " and ".join(parts)
    return s[0].upper() + s[1:]


def headline(cmp: dict) -> str:
    n = len(cmp["tasks"])
    c = cmp["counts"]
    subj = _subject(cmp)
    if cmp.get("inconclusive"):
        incomplete = sum(t.get("incomplete", False) for t in cmp["tasks"])
        return (f"⚫ Inconclusive: {incomplete} of {n} workflows have failed or missing runs. "
                f"Observed rule regressions: {c.get('regressed', 0)}; re-run before drawing conclusions.")
    if c.get("regressed"):
        k = c["regressed"]
        r = cmp["broken_rules"]
        return (f"⚠️ {subj} was followed by rule failures in {k} of {n} workflow{'s' if n != 1 else ''} "
                f"({r} observed rule drop{'s' if r != 1 else ''}).")
    if c.get("substituted"):
        k = c["substituted"]
        return (f"🟠 {subj} changed which skill runs in {k} of {n} workflow{'s' if n != 1 else ''}. "
                f"Rules still pass, but check the instructions you rely on.")
    if c.get("less-reliable"):
        return f"🟠 {subj} increased failed or errored runs in {c['less-reliable']} of {n} workflows."
    if c.get("no-data") == n:
        return "⚫ No valid runs: every run errored. See the error messages below."
    weak = sum(1 for t in cmp["tasks"] if t.get("weak_signal"))
    tail = (f" {weak} got worse by less than the threshold; re-run with more repeats to be sure."
            if weak else "")
    return f"✅ {subj} showed no detected regressions across {n} workflow{'s' if n != 1 else ''}.{tail}"


def to_markdown(cmp: dict, max_evidence_chars: int = 900) -> str:
    m = cmp["meta"]
    out = [MARKER, "## skilldiff: will this skill break my setup?", "", f"**{headline(cmp)}**", ""]
    out.append("> Privacy: reports, transcripts, and file artifacts are not redacted. Review before sharing.")
    out.append("")
    for w in cmp.get("warnings", []):
        out.append(f"> ⚠️ {w}")
    if cmp.get("warnings"):
        out.append("")
    out.append("| Workflow | Result | Expected skill ran first | Rules followed | Cost / run |")
    out.append("|---|---|---|---|---|")
    for t in cmp["tasks"]:
        sel = t["selection"]
        sel_s = f"{_frac(sel['before'])} → {_frac(sel['after'])}" if sel else "–"
        if sel and sel["taken_by"]:
            sel_s += " (" + ", ".join(f"{_skill(k)} {v}×" for k, v in sel["taken_by"].items()) + ")"
        rb = sum(r["before"]["pass"] for r in t["rules"])
        ra = sum(r["after"]["pass"] for r in t["rules"])
        nb = sum(r["before"]["n"] for r in t["rules"])
        na = sum(r["after"]["n"] for r in t["rules"])
        rules_s = f"{rb}/{nb} → {ra}/{na}" if t["rules"] else "–"
        weak = (" · ↘ below threshold" if t.get("weak_signal") else "") + (" · incomplete" if t.get("incomplete") else "")
        out.append(f"| `{t['id']}` | {ICON[t['verdict']]} {LABEL[t['verdict']]}{weak} | {sel_s} | {rules_s} | {_money(t['cost_delta_usd'])} |")
    out.append("")

    for t in cmp["tasks"]:
        if t["verdict"] in ("unchanged", "improved") and not t.get("weak_signal") and not t.get("incomplete"):
            continue
        opened = "" if t.get("weak_signal") else " open"
        label = LABEL[t["verdict"]] + (", but something got worse by less than the threshold" if t.get("weak_signal") else "")
        out.append(f"<details{opened}><summary><b>{ICON[t['verdict']]} {t['id']}</b>: {label}</summary>")
        out.append("")
        out.append(f"> {t['prompt'][:300]}")
        out.append("")
        if t.get("incomplete"):
            out.append(f"**Incomplete:** valid runs before {t['before']['valid']}/{m['repeats']}, "
                       f"after {t['after']['valid']}/{m['repeats']}. Rates below exclude failed runs.")
            out.append("")
        if t["selection"]:
            s = t["selection"]
            out.append(f"**First skill opened** (expected `{s['expected']}`): before "
                       + ", ".join(f"{_skill(k)} {v}×" for k, v in t["before"]["first_skill"].items())
                       + " · after " + ", ".join(f"{_skill(k)} {v}×" for k, v in t["after"]["first_skill"].items())
                       + (f" · drop {s['drop_pp']:g} pp (raw p={s['p']:.3f}, Holm p={s['p_adjusted']:.3f})" if s["p"] is not None else ""))
            out.append("")
        if t["rules"]:
            out.append("| Rule | Before | After | Change |")
            out.append("|---|---|---|---|")
            for r in t["rules"]:
                ch = {"regressed": f"🔴 observed drop {r['drop_pp']:g} pp (raw p={r['p']:.3f}, Holm p={r['p_adjusted']:.3f})" if r["p"] is not None else "🔴 broken",
                      "improved": "🟢 better", "weaker": "↘ lower, below threshold", "unchanged": ""}[r["status"]]
                desc = f" – {r['description']}" if r["description"] else ""
                out.append(f"| `{r['id']}`{desc} | {_frac(r['before'])} | {_frac(r['after'])} | {ch} |")
            out.append("")
        for r in t["rules"]:
            for ev in r["evidence"]:
                text = (ev["evidence"] or "").strip()
                if len(text) > max_evidence_chars:
                    text = text[:max_evidence_chars] + " …"
                same = f", same in {ev['count']} runs" if ev.get("count", 1) > 1 else ""
                first = _skill(ev["first_skill"] or "(none)")
                out.append(f"<sub>Evidence for `{r['id']}`: after-run #{ev['rep']}{same} · first skill {first} · `{ev['run']}`</sub>")
                out.append("")
                out.append("```" + ("diff" if text.startswith("modified:") else "text"))
                out.append(text or "(no detail)")
                out.append("```")
        moved = [a for a in t["artifacts"] if a["before"] != a["after"]]
        if moved:
            out.append("")
            out.append("**Files changed by the agent** (runs that changed each file, before → after): "
                       + ", ".join(f"`{a['path']}` {a['before']}→{a['after']}" for a in moved[:10]))
        for arm in ("before", "after"):
            if t[arm]["errors"]:
                out.append(f"\n{t[arm]['errors']} {arm} run(s) errored: " + "; ".join(t[arm]["error_messages"][:2]))
        out.append("")
        out.append("</details>")
        out.append("")

    tb, ta = cmp["cost_total_usd"]["before"], cmp["cost_total_usd"]["after"]
    out.append(f"**Cost of this experiment:** ${tb + ta:.2f} (before ${tb:.2f}, after ${ta:.2f}). "
               f"Cost / run columns compare mean API cost per run.")
    out.append("")
    out.append(f"<sub>{m['repeats']} repeats per arm, runs interleaved · model `{m.get('model') or 'default'}` · "
               f"Claude Code {m.get('agent_version') or '?'} · skilldiff {m['skilldiff_version']} · "
               f"rule broken = pass rate dropped by ≥{int(m['thresholds']['min_drop'] * 100)} points; "
               f"p = one-sided Fisher exact test; Holm adjustment across {cmp['statistics']['comparisons']} comparisons. "
               f"Threshold flags describe observed drops, not statistical certainty; small samples need more repeats.</sub>")
    return "\n".join(out) + "\n"


def to_json(cmp: dict) -> str:
    return json.dumps(cmp, indent=2, default=str)


# ---------------------------------------------------------------- HTML

_CSS = """
:root{--bg:#fbfaf7;--fg:#1d1d1b;--muted:#6b6a64;--line:#e4e1d8;--card:#fff;--red:#c2410c;--redbg:#fff1e8;
--amber:#a16207;--amberbg:#fef7e0;--green:#15803d;--greenbg:#ecf8ef;--chip:#f1efe8;--accent:#3b4bd8;--code:#f6f4ee}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#151514;--fg:#ecebe6;--muted:#9c9a92;--line:#2c2b28;
--card:#1c1c1a;--redbg:#3a1d10;--red:#fb923c;--amberbg:#33290c;--amber:#facc15;--greenbg:#11291a;--green:#4ade80;
--chip:#262522;--accent:#8b98ff;--code:#22211e}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:1060px;margin:0 auto;padding:40px 16px 80px}
h1{font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 10px;font-weight:600}
.head{font-size:26px;line-height:1.3;font-weight:650;margin:0 0 6px;letter-spacing:-.01em}
.sub{color:var(--muted);margin:0 0 28px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:0 0 32px}
.stat{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.stat b{display:block;font-size:22px;font-variant-numeric:tabular-nums}.stat span{color:var(--muted);font-size:13px}
table{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);font-weight:600}
.wrap{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:10px;margin-bottom:28px}
code,.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px}
.pill{display:inline-block;padding:1px 9px;border-radius:99px;font-size:12px;font-weight:600;white-space:nowrap}
.regressed{background:var(--redbg);color:var(--red)}.substituted,.less-reliable{background:var(--amberbg);color:var(--amber)}
.improved{background:var(--greenbg);color:var(--green)}.unchanged,.no-data{background:var(--chip);color:var(--muted)}
section.task{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin:0 0 18px}
section.task h2{font-size:18px;margin:0 0 4px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.prompt{color:var(--muted);border-left:3px solid var(--line);padding-left:10px;margin:6px 0 14px}
pre{background:var(--code);border-radius:8px;padding:10px 12px;overflow-x:auto;font-size:12.5px;line-height:1.45;margin:6px 0 12px;white-space:pre-wrap;word-break:break-word}
.bar{display:flex;height:8px;border-radius:4px;overflow:hidden;background:var(--chip);min-width:90px}
.bar i{display:block;background:var(--green)}.bar.after i{background:var(--accent)}
.runs{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px;margin-top:10px}
.run{border:1px solid var(--line);border-radius:8px;padding:10px 12px;font-size:13px}
.run h4{margin:0 0 6px;font-size:13px;display:flex;justify-content:space-between;gap:8px}
.tl{list-style:none;margin:0;padding:0;max-height:260px;overflow:auto}
.tl li{padding:2px 0;border-bottom:1px dashed var(--line);display:flex;gap:6px}
.tl .k{flex:0 0 auto;font-weight:600}.tl .skill .k{color:var(--accent)}.tl .text{color:var(--muted)}
.tl .d{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
details summary{cursor:pointer;color:var(--muted);margin:8px 0}
.fail{color:var(--red);font-weight:600}.ok{color:var(--green)}
footer{color:var(--muted);font-size:13px;margin-top:30px}
"""


def _e(s) -> str:
    return html.escape(str(s if s is not None else ""))


def _bar(k, n, after=False) -> str:
    pct = 0 if not n else round(100 * k / n)
    return f'<div class="bar{" after" if after else ""}" title="{k}/{n}"><i style="width:{pct}%"></i></div>'


def _timeline(rec: dict) -> str:
    tr = rec["transcript"]
    items = []
    for st in (tr.get("timeline") or [])[:80]:
        items.append(f'<li class="{_e(st["kind"])}"><span class="k">{_e(st["name"])}</span>'
                     f'<span class="d mono" title="{_e(st["detail"])}">{_e(st["detail"])}</span></li>')
    fails = [r for r in rec.get("rules", []) if not r["passed"]]
    status = (f'<span class="fail">error</span>' if tr.get("is_error")
              else (f'<span class="fail">{len(fails)} rule(s) failed</span>' if fails else '<span class="ok">all rules pass</span>'))
    cost = tr.get("cost_usd")
    return (f'<div class="run"><h4><span>{_e(rec["arm"])} #{rec["rep"]} · first skill '
            f'<code>{_e(tr.get("first_skill") or "none")}</code></span><span>{status}'
            f'{f" · ${cost:.3f}" if cost else ""}</span></h4>'
            + (f'<pre>{_e(tr.get("error"))}</pre>' if tr.get("is_error") else "")
            + f'<ul class="tl">{"".join(items) or "<li>no steps recorded</li>"}</ul></div>')


def _evidence_html(x: dict) -> str:
    count = x.get("count", 1)
    same = f", same in {count} runs" if count > 1 else ""
    return (f'<div class="mono" style="color:var(--muted);margin-top:6px">after #{x["rep"]}{same} · '
            f'first skill {_e(x["first_skill"] or "none")}</div><pre>{_e(x["evidence"])}</pre>')


WEAK_MARK = ' <span class="mono" title="a rule or the skill choice got worse, by less than the threshold">↘</span>'


def to_html(cmp: dict, records: list[dict]) -> str:
    m = cmp["meta"]
    head_html = re.sub(r"`([^`]+)`", r"<code>\1</code>", _e(headline(cmp)))
    tb, ta = cmp["cost_total_usd"]["before"], cmp["cost_total_usd"]["after"]
    c = cmp["counts"]
    stats = [
        (len(cmp["tasks"]), "workflows tested"),
        (c.get("regressed", 0), "broke rules"),
        (c.get("substituted", 0), "ran a different skill"),
        (cmp["broken_rules"], "rules broken"),
        (f"${tb + ta:.2f}", "experiment cost"),
    ]
    rows = []
    for t in cmp["tasks"]:
        sel = t["selection"]
        rb = sum(r["before"]["pass"] for r in t["rules"]); nb = sum(r["before"]["n"] for r in t["rules"])
        ra = sum(r["after"]["pass"] for r in t["rules"]); na = sum(r["after"]["n"] for r in t["rules"])
        rows.append(
            f'<tr><td><a href="#t-{_e(t["id"])}"><code>{_e(t["id"])}</code></a></td>'
            f'<td><span class="pill {t["verdict"]}">{_e(LABEL[t["verdict"]])}</span>'
            f'{WEAK_MARK if t.get("weak_signal") else ""}{" · incomplete" if t.get("incomplete") else ""}</td>'
            f'<td>{_e(_frac(sel["before"]) + " → " + _frac(sel["after"])) if sel else "–"}</td>'
            f'<td>{_bar(rb, nb)}<span class="mono">{rb}/{nb}</span></td><td>{_bar(ra, na, True)}<span class="mono">{ra}/{na}</span></td>'
            f'<td class="mono">{_e(_money(t["cost_delta_usd"]))}</td></tr>')
    sections = []
    for t in cmp["tasks"]:
        rule_rows = []
        for r in t["rules"]:
            label = {"regressed": f'<span class="pill regressed">drop {r["drop_pp"]:g} pp · raw p={r["p"]:.3f}, Holm p={r["p_adjusted"]:.3f}</span>' if r["p"] is not None else '<span class="pill regressed">broken</span>',
                     "improved": '<span class="pill improved">better</span>', "weaker": '<span class="pill unchanged">lower, below threshold</span>', "unchanged": ""}[r["status"]]
            ev = "".join(_evidence_html(x) for x in r["evidence"])
            rule_rows.append(f'<tr><td><code>{_e(r["id"])}</code><div style="color:var(--muted);font-size:13px">{_e(r["description"] or r["type"])}</div>{ev}</td>'
                             f'<td class="mono">{_frac(r["before"])}</td><td class="mono">{_frac(r["after"])}</td><td>{label}</td></tr>')
        sel_html = ""
        if t["selection"]:
            s = t["selection"]
            fb = ", ".join(f"{_e(k)} ×{v}" for k, v in t["before"]["first_skill"].items())
            fa = ", ".join(f"{_e(k)} ×{v}" for k, v in t["after"]["first_skill"].items())
            sel_html = (f'<p><b>First skill opened</b> (expected <code>{_e(t["expect_skill"])}</code>)<br>'
                        f'before: <span class="mono">{fb or "–"}</span><br>after: <span class="mono">{fa or "–"}</span>'
                        + (f'<br>Observed drop {s["drop_pp"]:g} pp · raw p={s["p"]:.3f}, Holm p={s["p_adjusted"]:.3f}'
                           if s["p"] is not None else "") + '</p>')
        if t.get("incomplete"):
            sel_html += (f'<p><b>Incomplete:</b> valid runs before {t["before"]["valid"]}/{m["repeats"]}, '
                         f'after {t["after"]["valid"]}/{m["repeats"]}. Rates exclude failed runs.</p>')
        moved = [a for a in t["artifacts"] if a["before"] != a["after"]]
        art = ""
        if moved:
            art = ('<details><summary>Files the agent changed (runs per arm)</summary><div class="wrap"><table><tr><th>File</th><th>Before</th><th>After</th></tr>'
                   + "".join(f'<tr><td><code>{_e(a["path"])}</code></td><td class="mono">{a["before"]}</td><td class="mono">{a["after"]}</td></tr>' for a in moved)
                   + "</table></div></details>")
        runs = sorted((r for r in records if r["task"] == t["id"]), key=lambda r: (r["arm"] != "before", r["rep"]))
        cost = (f'mean cost/run ${t["before"]["cost_usd"] or 0:.3f} → ${t["after"]["cost_usd"] or 0:.3f} · '
                f'turns {t["before"]["turns"] or 0:.1f} → {t["after"]["turns"] or 0:.1f} · '
                f'time {t["before"]["duration_s"] or 0:.0f}s → {t["after"]["duration_s"] or 0:.0f}s')
        sections.append(
            f'<section class="task" id="t-{_e(t["id"])}"><h2><code>{_e(t["id"])}</code>'
            f'<span class="pill {t["verdict"]}">{_e(LABEL[t["verdict"]])}</span></h2>'
            f'<div class="prompt">{_e(t["prompt"])}</div>{sel_html}'
            + (f'<div class="wrap"><table><tr><th>Rule</th><th>Before</th><th>After</th><th></th></tr>{"".join(rule_rows)}</table></div>' if rule_rows else "")
            + f'<p class="mono" style="color:var(--muted)">{_e(cost)}</p>{art}'
            f'<details><summary>Run timelines ({len(runs)} runs)</summary><div class="runs">{"".join(_timeline(r) for r in runs)}</div></details></section>')
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>skilldiff report</title><style>{_CSS}</style></head><body><main>
<h1>skilldiff report</h1><p class="head">{head_html}</p>
<p class="sub">Privacy: reports, transcripts, and file artifacts are not redacted. Review before sharing.</p>
<p class="sub">{m['repeats']} repeats per arm · model {_e(m.get('model') or 'default')} · Claude Code {_e(m.get('agent_version') or '?')} · {_e(m.get('finished_at', ''))}</p>
{"".join(f'<p class="sub">⚠️ {_e(w)}</p>' for w in cmp.get("warnings", []))}<div class="stats">{"".join(f'<div class="stat"><b>{_e(v)}</b><span>{_e(k)}</span></div>' for v, k in stats)}</div>
<div class="wrap"><table><tr><th>Workflow</th><th>Result</th><th>Expected skill first</th><th>Rules before</th><th>Rules after</th><th>Cost/run Δ</th></tr>{"".join(rows)}</table></div>
{"".join(sections)}
<footer>Before: {_e(", ".join(m["skills"]["before"]))}<br>After: {_e(", ".join(m["skills"]["after"]))}<br>
A rule counts as broken when its pass rate drops by at least {int(m['thresholds']['min_drop'] * 100)} percentage points. p is a one-sided Fisher exact test; Holm adjustment covers all {cmp['statistics']['comparisons']} comparable rule and skill-selection tests. Threshold flags describe observed drops, not statistical certainty. Small samples need more repeats.
Generated by skilldiff {_e(m['skilldiff_version'])}.</footer></main></body></html>"""
