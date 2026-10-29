"""Reduce a measured rule failure to a confirmed 1-minimal skill collection.

The algorithm is established delta debugging, not a new causal estimator. The
result is conditional on one task, rule, runtime and empirical oracle thresholds.
"""
from __future__ import annotations

import hashlib
import json
import shlex
import shutil
from dataclasses import replace
from pathlib import Path

from . import __version__, runner, workspace
from .config import ConfigError


class Stopped(Exception):
    def __init__(self, status, message):
        self.status, self.message = status, message


def classify(records, rule_id, repeats, pass_rate, failure_rate):
    """Never count a crashed, missing or unscored run as pass or failure."""
    failures = 0
    if len(records) != repeats:
        return "unknown", None
    for rec in records:
        if rec.get("transcript", {}).get("is_error", True):
            return "unknown", None
        scored = [r for r in rec.get("rules", []) if r["id"] == rule_id]
        if len(scored) != 1:
            return "unknown", None
        failures += not scored[0]["passed"]
    rate = failures / repeats
    if rate >= failure_rate:
        return "fail", failures
    if rate <= pass_rate:
        return "pass", failures
    return "unknown", failures


def reduce_set(items, fails):
    """ddmin over removable skill ids. The caller adds pinned skills.

    Does not assume monotonic failures. A later, fresh single-deletion sweep
    verifies the final candidate rather than promising a global minimum.
    """
    current = list(items)
    granularity = 2
    while current:
        width = max(1, (len(current) + granularity - 1) // granularity)
        chunks = [current[i:i + width] for i in range(0, len(current), width)]
        reduced = False
        # Complements preserve interactions split across chunks; subsets help
        # when an unrelated skill masks a smaller failure (non-monotonicity).
        candidates = [[x for x in current if x not in chunk] for chunk in chunks]
        candidates += [chunk for chunk in chunks if len(chunk) < len(current)]
        seen = set()
        for candidate in candidates:
            key = tuple(candidate)
            if key in seen:
                continue
            seen.add(key)
            if fails(candidate):
                current = candidate
                granularity = max(2, granularity - 1)
                reduced = True
                break
        if reduced:
            continue
        if granularity >= len(current):
            break
        granularity = min(len(current), granularity * 2)
    return current


def _hashes(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file()}


def export_reproducer(cfg, task, rule, before, after, dest, *, pass_rate, failure_rate, pinned, max_runs):
    """Snapshot inputs, not the user's installed library. No secrets redaction."""
    dest.mkdir()
    for name, skills in (("before", before), ("after", after)):
        (dest / name).mkdir()
        for skill in skills:
            shutil.copytree(skill.source, dest / name / skill.folder)
    for name, source in (("fixture", task.fixture), ("uncommitted", task.uncommitted)):
        if source:
            shutil.copytree(source, dest / name)
    q = lambda x: json.dumps(x, ensure_ascii=False)
    lines = ['[before]', 'skills = ["before"]', '[after]', 'skills = ["after"]', '', '[run]']
    for key in ("repeats", "parallel", "model", "agent_cmd", "max_turns", "timeout_seconds",
                "max_budget_usd", "permission_mode", "isolate_user_config", "extra_args"):
        value = getattr(cfg.run, key)
        if value is not None:
            lines.append(f"{key} = {q(value)}")
    lines += ['', '[thresholds]', f'min_drop = {cfg.thresholds.min_drop}',
              f'selection_min_drop = {cfg.thresholds.selection_min_drop}', '', '[[tasks]]',
              f'id = {q(task.id)}', f'prompt = {q(task.prompt)}', f'git_init = {q(task.git_init)}']
    if task.expect_skill:
        lines.append(f'expect_skill = {q(task.expect_skill)}')
    for name, source in (("fixture", task.fixture), ("uncommitted", task.uncommitted)):
        if source:
            lines.append(f'{name} = {q(name)}')
    lines += ['[[tasks.rules]]', f'id = {q(rule.id)}', f'type = {q(rule.type)}',
              f'description = {q(rule.description)}']
    lines += [f'{key} = {q(value)}' for key, value in rule.params.items()]
    (dest / "skilldiff.toml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    command = ["skilldiff", "diagnose", "-c", "skilldiff.toml", "--task", task.id, "--rule", rule.id,
               "--repeats", str(cfg.run.repeats), "--pass-rate", str(pass_rate),
               "--failure-rate", str(failure_rate), "--max-runs", str(max_runs), "-o", "../recheck"]
    for name in sorted(pinned):
        command += ["--keep-skill", name]
    (dest / "README.md").write_text(
        "# Reduced reproduction\n\nFrom this folder, confirm again with the same thresholds and pins:\n\n```sh\n"
        + shlex.join(command) + "\n```\n\n"
        "Requires skilldiff with the diagnose command and the configured agent command, "
        "its dependencies, credentials and environment. "
        "This is an input snapshot, not a hermetic environment or a security sandbox. "
        "The comparison runner uses its own pass-rate-drop threshold; the diagnosis used the "
        "failure-rate thresholds recorded in ../diagnosis.json.\n\n"
        "Files are not redacted. Review all skills, fixtures and reports before sharing.\n", encoding="utf-8")
    (dest / "manifest.json").write_text(json.dumps(_hashes(dest), indent=2) + "\n", encoding="utf-8")


def render(result):
    out = ["# skilldiff diagnosis", "", f"**{result['status']}** — {result['message']}", "",
           f"Task: `{result['task']}` · rule: `{result['rule']}` · agent runs: {result['runs_used']}/{result['max_runs']}",
           "", "Pinned: " + (", ".join(f"`{s}`" for s in result['pinned']) or "none"),
           "Candidate: " + (", ".join(f"`{s}`" for s in result['candidate']) or "none"), "",
           "| Probe | Phase | Skills | Failures / repeats | Result |", "|---|---|---|---|---|"]
    for p in result['probes']:
        count = "unknown" if p['failures'] is None else str(p['failures'])
        out.append(f"| {p['id']} | {p['phase']} | {', '.join(p['skills']) or '(empty)'} | {count}/{result['repeats']} | {p['outcome']} |")
    out += ["", "A confirmed result is **1-minimal relative to pinned skills**, not a globally smallest set "
            "or proof of causality. Every single unpinned deletion was freshly tested. Thresholds are empirical "
            "failure-frequency criteria, not confidence levels. Further trials or runtime changes can disagree.",
            "", "Temporary workspaces are not a security sandbox. Outputs and exported inputs are not redacted."]
    return "\n".join(out) + "\n"


def diagnose(cfg, task_id, rule_id, out, *, repeats=3, max_runs=120, pass_rate=0.0,
             failure_rate=1.0, keep_skills=(), log=print):
    if repeats < 2 or max_runs < 1:
        raise ConfigError("diagnose requires repeats >= 2 and max-runs >= 1")
    if not 0 <= pass_rate < failure_rate <= 1:
        raise ConfigError("require 0 <= pass-rate < failure-rate <= 1")
    if cfg.before.plugins or cfg.after.plugins:
        raise ConfigError("diagnose v1 supports skill folders only, not plugin bundles")
    tasks = [t for t in cfg.tasks if t.id == task_id]
    if len(tasks) != 1:
        raise ConfigError(f"unknown task: {task_id}")
    task = tasks[0]
    rules = [r for r in task.rules if r.id == rule_id]
    if len(rules) != 1:
        raise ConfigError(f"unknown rule for {task_id}: {rule_id}")
    rule = rules[0]
    if rule.type == "check":
        raise ConfigError("diagnose v1 does not export shell-check dependencies; choose a built-in rule")
    # Only evaluate the selected rule; unrelated custom check commands must not run.
    task = replace(task, rules=[rule])
    before, bw = workspace.discover_skills(cfg.before.skills)
    after, aw = workspace.discover_skills(cfg.after.skills)
    by_name = {s.name: s for s in after}
    pinned = set(keep_skills)
    if task.expect_skill:
        pinned.add(task.expect_skill)
    unknown = pinned - by_name.keys()
    if unknown:
        raise ConfigError(f"pinned/expected skills missing from after collection: {', '.join(sorted(unknown))}")
    if out.exists():
        raise ConfigError(f"diagnosis output already exists: {out}; choose a new folder")
    # Do not let generated artifacts be copied recursively as skills or fixtures.
    for source in [s.source for s in before + after] + [p for p in (task.fixture, task.uncommitted) if p]:
        if out == source or out.is_relative_to(source):
            raise ConfigError("diagnosis output must be outside skill and fixture input folders")
    out.mkdir(parents=True)
    # Freeze the inputs once: concurrent edits to the installed library must not
    # silently turn a subset search into a comparison of different skill versions.
    for label, entries in (("before", before), ("after", after)):
        frozen = []
        for entry in entries:
            dest = out / "inputs" / label / entry.folder
            shutil.copytree(entry.source, dest)
            frozen.append(replace(entry, source=dest))
        if label == "before":
            before = frozen
        else:
            after = frozen
    by_name = {s.name: s for s in after}
    for field in ("fixture", "uncommitted"):
        source = getattr(task, field)
        if source:
            dest = out / "inputs" / field
            shutil.copytree(source, dest)
            task = replace(task, **{field: dest})
    cfg = replace(cfg, run=replace(cfg.run, repeats=repeats))
    result = {"version": __version__, "task": task_id, "rule": rule_id, "repeats": repeats,
              "max_runs": max_runs, "runs_used": 0, "pass_rate": pass_rate, "failure_rate": failure_rate,
              "pinned": sorted(pinned), "candidate": sorted(by_name), "probes": [],
              "warnings": bw + aw, "status": "inconclusive", "message": "Diagnosis did not finish.",
              "confirmation": [], "model_requested": cfg.run.model}
    result['input_manifest'] = _hashes(out / "inputs")
    cache = {}
    runtime = None

    def probe(names, phase, *, control=False, fresh=False):
        nonlocal runtime
        key = tuple(sorted(names))
        if not fresh and not control and key in cache:
            return cache[key]
        if result['runs_used'] + repeats > max_runs:
            raise Stopped("budget-exhausted", "Run budget exhausted; no minimality claim is made.")
        skills = before if control else [by_name[n] for n in key]
        arm = cfg.before if control else cfg.after
        pid = len(result['probes'])
        records = []
        for rep in range(repeats):
            result['runs_used'] += 1
            try:
                rec = runner.run_one(cfg, runner.Job(task, arm, rep), skills, out / "probes" / str(pid))
            except Exception as exc:
                rec = {"transcript": {"is_error": True, "error": str(exc)}, "rules": []}
            records.append(rec)
        outcome, failures = classify(records, rule_id, repeats, pass_rate, failure_rate)
        identities = {(r['transcript'].get('model'), r['transcript'].get('agent_version')) for r in records}
        if outcome != "unknown":
            if len(identities) != 1 or any(None in identity for identity in identities):
                outcome = "unknown"
            else:
                identity = next(iter(identities))
                if runtime is not None and identity != runtime:
                    outcome = "unknown"
                runtime = identity
        p = {"id": pid, "phase": phase, "skills": sorted(s.name for s in skills),
             "outcome": outcome, "failures": failures,
             "errors": [r['transcript'].get('error') for r in records if r['transcript'].get('is_error')],
             "runtimes": [{k: r['transcript'].get(k) for k in ('model', 'agent_version', 'cost_usd')}
                          for r in records]}
        result['probes'].append(p)
        log(f"probe {pid}: {phase} {list(key)} -> {outcome} ({failures}/{repeats} failures)")
        # Persist after each completed probe; interruption leaves an inconclusive record.
        (out / "diagnosis.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        if outcome == "unknown":
            raise Stopped("inconclusive", "A probe errored or had mixed/ambiguous outcomes; no minimality claim is made.")
        if not control:
            cache[key] = outcome
        return outcome

    try:
        if probe([], "baseline", control=True) != "pass":
            raise Stopped("baseline-failed", "The before collection already fails the selected rule; fix the baseline first.")
        if probe(sorted(by_name), "full-after") != "fail":
            raise Stopped("not-reproduced", "The full after collection did not reproduce the selected failure.")
        removable = sorted(by_name.keys() - pinned)

        def fails(names):
            return probe(sorted(pinned | set(names)), "search") == "fail"

        candidate = reduce_set(removable, fails)
        result['candidate'] = sorted(pinned | set(candidate))
        # Fresh confirmation is separate from adaptive search and its cache.
        if probe([], "baseline-confirmation", control=True, fresh=True) != "pass":
            raise Stopped("inconclusive", "Fresh baseline no longer passes; possible drift or noise.")
        if probe(result['candidate'], "candidate-confirmation", fresh=True) != "fail":
            raise Stopped("inconclusive", "Reduced candidate did not reproduce on fresh confirmation.")
        for name in candidate:
            outcome = probe([n for n in result['candidate'] if n != name], "deletion-confirmation", fresh=True)
            result['confirmation'].append({"removed": name, "outcome": outcome})
            if outcome != "pass":
                raise Stopped("inconclusive", "Fresh single-deletion check still failed; candidate is not confirmed 1-minimal.")
        export_reproducer(cfg, task, rule, before, [by_name[n] for n in result['candidate']], out / "reproducer",
                          pass_rate=pass_rate, failure_rate=failure_rate, pinned=pinned, max_runs=max_runs)
        result.update(status="confirmed-1-minimal",
                      message=("Failure reproduced; every single unpinned deletion passed fresh confirmation."
                               if candidate else "The pinned collection alone reproduces the failure; no removable skill is needed."))
    except Stopped as exc:
        result.update(status=exc.status, message=exc.message)
    except KeyboardInterrupt:
        result.update(status="interrupted", message="Interrupted; no minimality claim is made.")
    (out / "diagnosis.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (out / "diagnosis.md").write_text(render(result), encoding="utf-8")
    return result
