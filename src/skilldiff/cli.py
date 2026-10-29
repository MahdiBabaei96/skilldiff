"""skilldiff command line."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from . import __version__
from . import compare as compare_mod
from . import config as config_mod
from . import report as report_mod
from . import runner
from . import workspace as ws_mod

STARTER = '''# skilldiff experiment: does adding (or changing) a skill break the workflows you rely on?
# Docs: https://github.com/MahdiBabaei96/skilldiff#configuration

[before]
skills = ["skills"]                        # your installed collection (a folder of skill folders)

[after]
skills = ["skills", "candidate"]           # the same collection plus the skill you want to add
# plugins = ["path/to/plugin"]             # plugins are loaded with --plugin-dir

[run]
repeats = 3          # runs per arm per task; use 5+ for stronger evidence
parallel = 4
model = "sonnet"
max_turns = 30
timeout_seconds = 900
# max_budget_usd = 1.0   # per-run cap

[[tasks]]
id = "commit-change"
prompt = "Commit my change."
fixture = "fixtures/app"                   # copied into a fresh temp git repo for every run
# uncommitted = "fixtures/app-change"      # copied on top after the initial commit
expect_skill = "commit-helper"             # which skill *should* handle this
rules = [
  { id = "never-push", type = "no_command", pattern = "git\\\\s+push", description = "commit-helper forbids pushing" },
  { id = "conventional", type = "commit_message", pattern = "^(feat|fix|docs|chore|refactor|test)(\\\\(.+\\\\))?: " },
]
'''


def _skill_hash(path: Path) -> str:
    h = hashlib.sha256()
    for f in sorted(p for p in path.rglob("*") if p.is_file()):
        h.update(f.relative_to(path).as_posix().encode())
        h.update(f.read_bytes())
    return h.hexdigest()


def _apply_overrides(cfg, args) -> None:
    cwd = Path.cwd()
    for arm_name in ("before", "after"):
        arm = getattr(cfg, arm_name)
        sk = getattr(args, f"{arm_name}_skills", None)
        pl = getattr(args, f"{arm_name}_plugins", None)
        if sk is not None:
            arm.skills = [(cwd / s).resolve() for s in sk]
        if pl is not None:
            arm.plugins = [(cwd / p).resolve() for p in pl]
        for p in arm.skills + arm.plugins:
            if not p.exists():
                raise config_mod.ConfigError(f"{arm_name}: path does not exist: {p}")
    if getattr(args, "repeats", None):
        cfg.run.repeats = args.repeats
    if getattr(args, "parallel", None):
        cfg.run.parallel = args.parallel
    if getattr(args, "model", None):
        cfg.run.model = args.model
    if getattr(args, "agent_cmd", None):
        cfg.run.agent_cmd = args.agent_cmd
    if getattr(args, "task", None):
        keep = set(args.task)
        unknown = keep - {t.id for t in cfg.tasks}
        if unknown:
            raise config_mod.ConfigError(f"unknown task id(s): {', '.join(sorted(unknown))}")
        cfg.tasks = [t for t in cfg.tasks if t.id in keep]


def _meta(cfg) -> dict:
    sk = {}
    hashes = {}
    warns: list[str] = []
    for arm in (cfg.before, cfg.after):
        found, w = ws_mod.discover_skills(arm.skills)
        warns += [x for x in w if x not in warns and "replaces the one from" not in x]
        sk[arm.name] = sorted(s.name for s in found) + [f"plugin:{p.name}" for p in arm.plugins]
        hashes[arm.name] = {s.name: _skill_hash(s.source) for s in found}
    changed = sorted(n for n in hashes["before"] if n in hashes["after"] and hashes["before"][n] != hashes["after"][n])
    return {
        "skilldiff_version": __version__,
        "config": str(cfg.path),
        "repeats": cfg.run.repeats,
        "model": cfg.run.model,
        "thresholds": {"min_drop": cfg.thresholds.min_drop, "selection_min_drop": cfg.thresholds.selection_min_drop},
        "skills": sk,
        "changed_skills": changed,
        "warnings": warns,
        "tasks": [{"id": t.id, "prompt": t.prompt, "expect_skill": t.expect_skill,
                   "rules": [{"id": r.id, "type": r.type, "description": r.description, **r.params} for r in t.rules]}
                  for t in cfg.tasks],
    }


def _write_reports(out: Path, meta: dict, records: list[dict]) -> dict:
    cmp = compare_mod.compare(meta, records)
    (out / "report.json").write_text(report_mod.to_json(cmp), encoding="utf-8")
    (out / "report.md").write_text(report_mod.to_markdown(cmp), encoding="utf-8")
    (out / "report.html").write_text(report_mod.to_html(cmp, records), encoding="utf-8")
    return cmp


def _exit_code(cmp: dict, fail_on: str) -> int:
    if fail_on == "never":
        return 0
    if cmp.get("inconclusive"):
        return 2
    if cmp["regression"]:
        return 1
    if fail_on == "substitution" and (cmp["substitution"] or cmp["counts"].get("less-reliable")):
        return 1
    return 0


def cmd_run(args) -> int:
    cfg = config_mod.load(args.config)
    _apply_overrides(cfg, args)
    out = Path(args.out).resolve()
    meta = _meta(cfg)
    if args.dry_run:
        for j in runner.plan(cfg, cfg.run.repeats):
            print(f"{j.task.id}\t{j.arm.name}\t#{j.rep}\t" + " ".join(runner.agent_command(cfg, j.task, j.arm)))
        return 0
    print("Notice: temporary workspaces are not a security sandbox. Agents inherit your environment; "
          "bypassPermissions disables permission prompts. Use a disposable container or runner for untrusted skills. "
          "Reports, transcripts, and file artifacts are not redacted; review them before sharing.", file=sys.stderr)
    if out.exists() and any(out.iterdir()):
        if not args.force:
            print(f"error: output folder {out} is not empty (use --force to replace it)", file=sys.stderr)
            return 2
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    if meta["skills"]["before"] == meta["skills"]["after"] and not meta["changed_skills"]:
        print("warning: before and after arms install the same skills; expect no differences", file=sys.stderr)
    meta["started_at"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    records = runner.run_all(cfg, out, cfg.run.repeats, cfg.run.parallel, keep_workspaces=args.keep_workspaces)
    versions = [r["transcript"].get("agent_version") for r in records if r.get("transcript", {}).get("agent_version")]
    models = [r["transcript"].get("model") for r in records if r.get("transcript", {}).get("model")]
    meta["agent_version"] = versions[0] if versions else None
    meta["model_requested"] = cfg.run.model
    meta["model"] = models[0] if models else cfg.run.model
    meta["finished_at"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    (out / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    cmp = _write_reports(out, meta, records)
    print("\n" + report_mod.headline(cmp))
    print(f"Reports: {out / 'report.md'}\n         {out / 'report.html'}")
    return _exit_code(cmp, args.fail_on)


def _load_records(out: Path) -> tuple[dict, list[dict]]:
    meta_path = out / "meta.json"
    if not meta_path.exists():
        raise config_mod.ConfigError(f"{out} has no meta.json; is it a skilldiff output folder?")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    records = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(out.glob("runs/*/*/*/run.json"))]
    return meta, records


def cmd_report(args) -> int:
    out = Path(args.out).resolve()
    meta, records = _load_records(out)
    if args.min_drop is not None:
        meta["thresholds"]["min_drop"] = args.min_drop
    cmp = _write_reports(out, meta, records)
    if args.format == "md":
        sys.stdout.write(report_mod.to_markdown(cmp))
    elif args.format == "json":
        sys.stdout.write(report_mod.to_json(cmp))
    else:
        print(report_mod.headline(cmp))
    return _exit_code(cmp, args.fail_on)


def cmd_validate(args) -> int:
    cfg = config_mod.load(args.config)
    _apply_overrides(cfg, args)
    ok = True
    for arm in (cfg.before, cfg.after):
        found, warnings = ws_mod.discover_skills(arm.skills)
        print(f"[{arm.name}] {len(found)} skill(s): {', '.join(s.name for s in found) or 'none'}"
              + (f" + {len(arm.plugins)} plugin(s)" if arm.plugins else ""))
        for w in warnings:
            print(f"  warning: {w}")
        names = {s.name for s in found}
        for t in cfg.tasks:
            if t.expect_skill and t.expect_skill not in names and ":" not in t.expect_skill:
                print(f"  warning: task {t.id} expects skill '{t.expect_skill}', which is not installed in this arm")
    n = len(cfg.tasks) * 2 * cfg.run.repeats
    print(f"{len(cfg.tasks)} task(s), {sum(len(t.rules) for t in cfg.tasks)} rule(s) → {n} runs at {cfg.run.repeats} repeats")
    agent = os.path.expandvars(cfg.run.agent_cmd).split()[0]
    if shutil.which(agent):
        try:
            v = subprocess.run([agent, "--version"], capture_output=True, text=True, timeout=60).stdout.strip()
            print(f"agent: {v}")
        except Exception as e:  # pragma: no cover
            print(f"agent: found but `--version` failed: {e}")
    else:
        print(f"agent: '{agent}' not found on PATH; install Claude Code: npm i -g @anthropic-ai/claude-code")
        ok = False
    return 0 if ok else 2


def cmd_init(args) -> int:
    p = Path(args.path)
    if p.exists() and not args.force:
        print(f"error: {p} already exists (use --force)", file=sys.stderr)
        return 2
    p.write_text(STARTER, encoding="utf-8")
    print(f"Wrote {p}. Edit the paths and tasks, then run: skilldiff validate && skilldiff run")
    return 0


def cmd_diagnose(args) -> int:
    from .diagnose import diagnose

    cfg = config_mod.load(args.config)
    if args.model:
        cfg.run.model = args.model
    if args.agent_cmd:
        cfg.run.agent_cmd = args.agent_cmd
    print("Notice: diagnose executes skills in temporary workspaces, not a security sandbox. "
          "Agents inherit your environment; outputs and exported inputs are not redacted. "
          f"At most {args.max_runs} agent runs will be started.", file=sys.stderr)
    result = diagnose(cfg, args.task, args.rule, Path(args.out).resolve(),
                      repeats=args.repeats if args.repeats is not None else cfg.run.repeats,
                      max_runs=args.max_runs, pass_rate=args.pass_rate, failure_rate=args.failure_rate,
                      keep_skills=args.keep_skill, log=lambda s: print(s, file=sys.stderr))
    print(f"{result['status']}: {result['message']}")
    print(f"Report: {Path(args.out).resolve() / 'diagnosis.md'}")
    return 0 if result['status'] in ('confirmed-1-minimal', 'not-reproduced') else 2


def _arm_flags(sp):
    sp.add_argument("--before-skills", nargs="+", metavar="PATH", help="override [before].skills")
    sp.add_argument("--after-skills", nargs="+", metavar="PATH", help="override [after].skills")
    sp.add_argument("--before-plugins", nargs="*", metavar="PATH", help="override [before].plugins")
    sp.add_argument("--after-plugins", nargs="*", metavar="PATH", help="override [after].plugins")
    sp.add_argument("--task", action="append", metavar="ID", help="only run this task (repeatable)")
    sp.add_argument("--repeats", type=int, help="override [run].repeats")
    sp.add_argument("--parallel", type=int, help="override [run].parallel")
    sp.add_argument("--model", help="override [run].model")
    sp.add_argument("--agent-cmd", help="override [run].agent_cmd (default: claude)")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="skilldiff", description="Before/after experiments that show whether adding or changing a Claude skill breaks the workflows you already rely on.")
    ap.add_argument("--version", action="version", version=f"skilldiff {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="run the experiment and write reports")
    r.add_argument("-c", "--config", default="skilldiff.toml")
    r.add_argument("-o", "--out", default="skilldiff-out")
    r.add_argument("--force", action="store_true", help="replace an existing output folder")
    r.add_argument("--fail-on", choices=["regression", "substitution", "never"], default="regression",
                   help="exit 1 for findings, 2 for incomplete experiments; never opts out of both (default: regression)")
    r.add_argument("--keep-workspaces", action="store_true", help="keep temp workspaces for inspection")
    r.add_argument("--dry-run", action="store_true", help="print the planned agent commands and exit")
    _arm_flags(r)
    r.set_defaults(fn=cmd_run)

    rep = sub.add_parser("report", help="re-render reports from a finished output folder")
    rep.add_argument("out", nargs="?", default="skilldiff-out")
    rep.add_argument("--format", choices=["md", "json", "headline"], default="headline")
    rep.add_argument("--min-drop", type=float, help="re-score with a different threshold")
    rep.add_argument("--fail-on", choices=["regression", "substitution", "never"], default="never")
    rep.set_defaults(fn=cmd_report)

    d = sub.add_parser("diagnose", help="reduce a rule failure to a freshly confirmed 1-minimal skill set")
    d.add_argument("-c", "--config", default="skilldiff.toml")
    d.add_argument("--task", required=True, help="one task id from the config")
    d.add_argument("--rule", required=True, help="one built-in rule id from that task")
    d.add_argument("-o", "--out", default="skilldiff-diagnosis")
    d.add_argument("--repeats", type=int, help="runs per probe (at least 2; default: config)")
    d.add_argument("--max-runs", type=int, default=120, help="hard cap including fresh confirmations")
    d.add_argument("--keep-skill", action="append", default=[], help="pin a skill (repeatable; expected skill is always pinned)")
    d.add_argument("--pass-rate", type=float, default=0.0, help="maximum failure frequency considered passing")
    d.add_argument("--failure-rate", type=float, default=1.0, help="minimum failure frequency considered failing")
    d.add_argument("--model", help="override model")
    d.add_argument("--agent-cmd", help="override agent command")
    d.set_defaults(fn=cmd_diagnose)

    v = sub.add_parser("validate", help="check the config, list skills per arm, count runs")
    v.add_argument("-c", "--config", default="skilldiff.toml")
    _arm_flags(v)
    v.set_defaults(fn=cmd_validate)

    i = sub.add_parser("init", help="write a starter skilldiff.toml")
    i.add_argument("path", nargs="?", default="skilldiff.toml")
    i.add_argument("--force", action="store_true")
    i.set_defaults(fn=cmd_init)

    args = ap.parse_args(argv)
    try:
        return args.fn(args)
    except config_mod.ConfigError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
