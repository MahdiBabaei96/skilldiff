"""Turn raw run records into a before/after comparison."""
from __future__ import annotations

from collections import Counter
from math import fsum
from statistics import mean

from .stats import confidence, fisher_one_sided, rate

VERDICT_ORDER = ["regressed", "substituted", "less-reliable", "improved", "unchanged", "no-data"]


def _ranked(c: Counter) -> dict:
    """Counts sorted by count, then name, so reports are byte-for-byte reproducible."""
    return dict(sorted(c.items(), key=lambda kv: (-kv[1], kv[0])))


def _r(x, nd=6):
    """Fixed precision so reports are identical across Python versions
    (3.12 changed float summation in sum())."""
    return None if x is None else round(x, nd)


def _mean(xs, nd=6):
    xs = [x for x in xs if x is not None]
    return _r(mean(xs), nd) if xs else None


def _arm_summary(recs: list[dict], task: dict) -> dict:
    valid = [r for r in recs if not r["transcript"].get("is_error")]
    first = Counter(r["transcript"].get("first_skill") or "(none)" for r in valid)
    anyuse = Counter()
    for r in valid:
        for s in sorted(set(r["transcript"].get("skills_invoked") or [])):
            anyuse[s] += 1
    rules = {}
    for rule in task["rules"]:
        k = sum(1 for r in valid for rr in r["rules"] if rr["id"] == rule["id"] and rr["passed"])
        rules[rule["id"]] = {"pass": k, "n": len(valid)}
    exp = task.get("expect_skill")
    files = Counter()
    for r in valid:
        before, after = r.get("files_before", {}), r.get("files_after", {})
        for path, meta in after.items():
            if before.get(path, {}).get("sha256") != meta["sha256"]:
                files[path] += 1
        for path in before:
            if path not in after:
                files[f"{path} (deleted)"] += 1
    return {
        "runs": len(recs),
        "errors": len(recs) - len(valid),
        "error_messages": sorted({(r["transcript"].get("error") or "")[:200] for r in recs if r["transcript"].get("is_error")}),
        "valid": len(valid),
        "first_skill": _ranked(first),
        "skills_used": _ranked(anyuse),
        "expected_first": sum(1 for r in valid if exp and r["transcript"].get("first_skill") == exp) if exp else None,
        "rules": rules,
        "files_changed": _ranked(files),
        "cost_usd": _mean([r["transcript"].get("cost_usd") for r in valid]),
        "cost_usd_total": _r(fsum(r["transcript"].get("cost_usd") or 0 for r in recs)),
        "duration_s": _r((_mean([r["transcript"].get("duration_ms") for r in valid]) or 0) / 1000, 3) or None,
        "turns": _mean([r["transcript"].get("num_turns") for r in valid], 2),
        "input_tokens": _mean([r["transcript"].get("input_tokens") for r in valid], 1),
        "output_tokens": _mean([r["transcript"].get("output_tokens") for r in valid], 1),
    }


def _evidence(recs: list[dict], rule_id: str, limit: int = 2) -> list[dict]:
    """Failing after-runs for a rule, grouped so identical evidence is shown once."""
    groups: dict[str, dict] = {}
    for r in sorted(recs, key=lambda r: r["rep"]):
        if r["transcript"].get("is_error"):
            continue
        for rr in r["rules"]:
            if rr["id"] == rule_id and not rr["passed"]:
                key = rr.get("evidence", "")
                if key in groups:
                    groups[key]["count"] += 1
                else:
                    groups[key] = {"rep": r["rep"], "first_skill": r["transcript"].get("first_skill"),
                                   "evidence": key, "count": 1, "run": f"runs/{r['task']}/{r['arm']}/{r['rep']}"}
    return sorted(groups.values(), key=lambda g: -g["count"])[:limit]


def compare(meta: dict, records: list[dict]) -> dict:
    th = meta["thresholds"]
    new_skills = sorted(set(meta["skills"]["after"]) - set(meta["skills"]["before"]))
    removed_skills = sorted(set(meta["skills"]["before"]) - set(meta["skills"]["after"]))
    tasks_out = []
    for task in meta["tasks"]:
        tid = task["id"]
        b_recs = [r for r in records if r["task"] == tid and r["arm"] == "before"]
        a_recs = [r for r in records if r["task"] == tid and r["arm"] == "after"]
        b, a = _arm_summary(b_recs, task), _arm_summary(a_recs, task)

        rule_rows = []
        for rule in task["rules"]:
            rb, ra = b["rules"][rule["id"]], a["rules"][rule["id"]]
            pb, pa = rate(rb["pass"], rb["n"]), rate(ra["pass"], ra["n"])
            row = {"id": rule["id"], "type": rule["type"], "description": rule.get("description", ""),
                   "before": rb, "after": ra, "status": "unchanged", "p": None, "confidence": None, "evidence": []}
            if pb is not None and pa is not None:
                if pb - pa >= th["min_drop"] - 1e-9:
                    p = fisher_one_sided(rb["pass"], rb["n"], ra["pass"], ra["n"])
                    row.update(status="regressed", p=_r(p), confidence=confidence(p), evidence=_evidence(a_recs, rule["id"]))
                elif pa - pb >= th["min_drop"] - 1e-9:
                    row["status"] = "improved"
                elif pb > pa:
                    row["status"] = "weaker"   # dropped, but by less than min_drop
            rule_rows.append(row)

        selection = None
        if task.get("expect_skill"):
            eb, ea = b["expected_first"], a["expected_first"]
            rb_, ra_ = rate(eb, b["valid"]), rate(ea, a["valid"])
            # "(none)" matters: an ambiguous pair can make the agent skip skills entirely
            takers = {s: c for s, c in a["first_skill"].items() if s != task["expect_skill"]}
            selection = {"expected": task["expect_skill"], "before": {"pass": eb, "n": b["valid"]},
                         "after": {"pass": ea, "n": a["valid"]}, "taken_by": takers, "status": "unchanged",
                         "p": None, "confidence": None}
            if rb_ is not None and ra_ is not None and rb_ - ra_ >= th["selection_min_drop"] - 1e-9:
                p = fisher_one_sided(eb, b["valid"], ea, a["valid"])
                selection.update(status="changed", p=_r(p), confidence=confidence(p))
            elif rb_ is not None and ra_ is not None and rb_ > ra_:
                selection["status"] = "weaker"

        if not b["valid"] or not a["valid"]:
            verdict = "no-data"
        elif any(r["status"] == "regressed" for r in rule_rows):
            verdict = "regressed"
        elif selection and selection["status"] == "changed":
            verdict = "substituted"   # rules still pass, but a different skill did the job
        elif a["errors"] - b["errors"] >= max(1, round(th["min_drop"] * max(a["runs"], 1))):
            verdict = "less-reliable"
        elif any(r["status"] == "improved" for r in rule_rows):
            verdict = "improved"
        else:
            verdict = "unchanged"

        weak = any(r["status"] == "weaker" for r in rule_rows) or bool(selection and selection["status"] == "weaker")
        all_files = sorted(set(b["files_changed"]) | set(a["files_changed"]))
        artifacts = [{"path": f, "before": b["files_changed"].get(f, 0), "after": a["files_changed"].get(f, 0)}
                     for f in all_files]
        tasks_out.append({
            "id": tid, "prompt": task["prompt"], "expect_skill": task.get("expect_skill"), "verdict": verdict,
            "weak_signal": weak and verdict in ("unchanged", "improved"),
            "before": b, "after": a, "rules": rule_rows, "selection": selection, "artifacts": artifacts,
            "cost_delta_usd": _r(a["cost_usd"] - b["cost_usd"]) if (a["cost_usd"] is not None and b["cost_usd"] is not None) else None,
        })

    counts = Counter(t["verdict"] for t in tasks_out)
    totals = {arm: _r(fsum(t[arm]["cost_usd_total"] for t in tasks_out)) for arm in ("before", "after")}
    broken_rules = sum(1 for t in tasks_out for r in t["rules"] if r["status"] == "regressed")
    return {
        "meta": meta,
        "new_skills": new_skills,
        "removed_skills": removed_skills,
        "tasks": sorted(tasks_out, key=lambda t: VERDICT_ORDER.index(t["verdict"])),
        "counts": dict(counts),
        "broken_rules": broken_rules,
        "cost_total_usd": totals,
        "warnings": meta.get("warnings", []),
        "regression": counts.get("regressed", 0) > 0,
        "substitution": counts.get("substituted", 0) > 0,
    }
