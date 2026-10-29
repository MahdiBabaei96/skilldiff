"""Run one task once, in one arm, in a fresh workspace, and record everything."""
from __future__ import annotations

import json
import os
import shlex
import signal
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

from . import rules as rules_mod
from . import transcript as transcript_mod
from . import workspace as ws_mod
from .config import Arm, Config, Task


@dataclass
class Job:
    task: Task
    arm: Arm
    rep: int


def agent_command(cfg: Config, task: Task, arm: Arm) -> list[str]:
    r = cfg.run
    cmd = shlex.split(os.path.expandvars(r.agent_cmd)) + [
        "-p", task.prompt,
        "--output-format", "stream-json",
        "--verbose",
        "--no-session-persistence",
        # Only project-level settings/skills: the user's personal ~/.claude skills
        # must not leak into either arm.
        "--setting-sources", "project",
        "--permission-mode", r.permission_mode,
        "--max-turns", str(r.max_turns),
    ]
    if r.model:
        cmd += ["--model", r.model]
    if r.max_budget_usd:
        cmd += ["--max-budget-usd", str(r.max_budget_usd)]
    for p in arm.plugins:
        cmd += ["--plugin-dir", str(p)]
    cmd += list(r.extra_args)
    return cmd


def _run_process(cmd: list[str], cwd: Path, env: dict, timeout: int, out_path: Path) -> tuple[int | None, bool, str]:
    """Stream stdout to a file. Returns (exit code, timed_out, stderr tail)."""
    with open(out_path, "w", encoding="utf-8") as out:
        try:
            proc = subprocess.Popen(
                cmd, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.PIPE,
                text=True, start_new_session=True,
            )
        except FileNotFoundError:
            return None, False, f"agent command not found: {cmd[0]}. Install Claude Code (npm i -g @anthropic-ai/claude-code) or set [run].agent_cmd."
        try:
            _, err = proc.communicate(timeout=timeout)
            return proc.returncode, False, (err or "")[-2000:]
        except (subprocess.TimeoutExpired, KeyboardInterrupt) as exc:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                proc.kill()
            _, err = proc.communicate()
            if isinstance(exc, KeyboardInterrupt):
                raise
            return proc.returncode, True, (err or "")[-2000:]


_INIT_KEEP = ("type", "subtype", "cwd", "model", "claude_code_version", "skills", "permissionMode")


def _compact_events(path: Path) -> None:
    """Compact the transcript. This is not redaction: prompts, tool payloads,
    file content, and credentials in them can remain in the saved events."""
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return
    out = []
    for ln in lines:
        try:
            e = json.loads(ln)
        except json.JSONDecodeError:
            continue
        if not isinstance(e, dict) or e.get("type") == "stream_event":
            continue
        if e.get("type") == "system" and e.get("subtype") == "init":
            e = {k: e[k] for k in _INIT_KEEP if k in e}
        for k in ("session_id", "uuid", "parent_uuid"):
            e.pop(k, None)
        out.append(json.dumps(e, ensure_ascii=False))
    path.write_text("\n".join(out) + ("\n" if out else ""), encoding="utf-8")


def run_one(cfg: Config, job: Job, skills: list, out_dir: Path, keep_workspace: bool = False) -> dict:
    run_dir = out_dir / "runs" / job.task.id / job.arm.name / str(job.rep)
    run_dir.mkdir(parents=True, exist_ok=True)
    ws, base = ws_mod.build_workspace(job.task, job.arm, skills)
    before_files = ws_mod.snapshot(ws)

    env = dict(os.environ)
    env.pop("CLAUDECODE", None)  # allow running from inside a Claude Code session
    env.pop("CLAUDE_CODE_INCLUDE_PARTIAL_MESSAGES", None)  # token-by-token chunks: large, never needed
    cfg_dir = None
    if cfg.run.isolate_user_config:
        cfg_dir = Path(tempfile.mkdtemp(prefix="skilldiff-cfg-"))
        env["CLAUDE_CONFIG_DIR"] = str(cfg_dir)

    cmd = agent_command(cfg, job.task, job.arm)
    started = time.time()
    code, timed_out, stderr = _run_process(cmd, ws, env, cfg.run.timeout_seconds, run_dir / "events.jsonl")
    wall = time.time() - started

    _compact_events(run_dir / "events.jsonl")
    with open(run_dir / "events.jsonl", encoding="utf-8", errors="replace") as fh:
        tr = transcript_mod.parse(fh)
    if timed_out:
        tr.is_error, tr.error = True, f"timed out after {cfg.run.timeout_seconds}s"
    elif code is None:
        tr.is_error, tr.error = True, stderr
    elif code != 0:
        tr.is_error = True
        if not tr.got_result or not tr.error:
            tr.error = f"agent exited {code}: {stderr.strip()[-400:]}"
    if tr.duration_ms is None:
        tr.duration_ms = int(wall * 1000)

    after_files = ws_mod.snapshot(ws)
    git = ws_mod.git_state(ws, base)
    st = rules_mod.RunState(tr, before_files, after_files, git, ws, job.task.root or cfg.root)
    results = [rules_mod.evaluate(r, st).to_dict() for r in job.task.rules]

    record = {
        "task": job.task.id,
        "arm": job.arm.name,
        "rep": job.rep,
        "command": ["<prompt>" if x == job.task.prompt else x for x in cmd],
        "skills_installed": [s.name for s in skills],
        "transcript": tr.to_dict(),
        "rules": results,
        "git": git,
        "files_before": {k: {"sha256": v["sha256"], "size": v["size"]} for k, v in before_files.items()},
        "files_after": {k: {"sha256": v["sha256"], "size": v["size"]} for k, v in after_files.items()},
        "stderr_tail": stderr[-1000:] if (tr.is_error and stderr) else "",
    }
    # keep text of created/changed files as artifacts for the report
    art_dir = run_dir / "files"
    for path, meta in after_files.items():
        if before_files.get(path, {}).get("sha256") != meta["sha256"] and "text" in meta:
            dest = art_dir / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(meta["text"], encoding="utf-8")
    orig_dir = run_dir / "original"
    for path, meta in before_files.items():
        if after_files.get(path, {}).get("sha256") != meta["sha256"] and "text" in meta:
            dest = orig_dir / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(meta["text"], encoding="utf-8")
    (run_dir / "run.json").write_text(json.dumps(record, indent=2), encoding="utf-8")

    if keep_workspace:
        record["workspace"] = str(ws)
    else:
        ws_mod.cleanup(ws)
    if cfg_dir:
        import shutil
        shutil.rmtree(cfg_dir, ignore_errors=True)
    return record


def plan(cfg: Config, repeats: int) -> list[Job]:
    """Interleave arms and repeats so time-varying noise (API load, model
    rollouts) hits both arms evenly instead of all 'before' runs going first."""
    jobs: list[Job] = []
    for rep in range(repeats):
        for task in cfg.tasks:
            first, second = (cfg.before, cfg.after) if rep % 2 == 0 else (cfg.after, cfg.before)
            jobs.append(Job(task, first, rep))
            jobs.append(Job(task, second, rep))
    return jobs


def run_all(cfg: Config, out_dir: Path, repeats: int, parallel: int, keep_workspaces: bool = False,
            log=lambda s: print(s, file=sys.stderr, flush=True)) -> list[dict]:
    skills = {}
    for arm in (cfg.before, cfg.after):
        found, warnings = ws_mod.discover_skills(arm.skills)
        for w in warnings:
            log(f"  warning [{arm.name}]: {w}")
        skills[arm.name] = found
    jobs = plan(cfg, repeats)
    log(f"skilldiff: {len(jobs)} runs ({len(cfg.tasks)} tasks × 2 arms × {repeats} repeats), {parallel} at a time")
    records: list[dict] = []
    lock = threading.Lock()
    done = 0
    with ThreadPoolExecutor(max_workers=parallel) as pool:
        futs = {pool.submit(run_one, cfg, j, skills[j.arm.name], out_dir, keep_workspaces): j for j in jobs}
        for fut in as_completed(futs):
            j = futs[fut]
            try:
                rec = fut.result()
            except Exception as e:  # keep going; one broken run shouldn't lose the rest
                rec = {"task": j.task.id, "arm": j.arm.name, "rep": j.rep, "crash": repr(e), "rules": [],
                       "transcript": {"is_error": True, "error": repr(e), "skills_invoked": []}}
            with lock:
                records.append(rec)
                done += 1
                tr = rec.get("transcript", {})
                fails = sum(1 for r in rec.get("rules", []) if not r["passed"])
                status = "ERROR" if tr.get("is_error") else (f"{fails} rule(s) failed" if fails else "ok")
                cost = tr.get("cost_usd")
                log(f"  [{done:>3}/{len(jobs)}] {j.task.id:<28} {j.arm.name:<6} #{j.rep}  "
                    f"skill={tr.get('first_skill') or '-':<22} {status}" + (f"  ${cost:.3f}" if cost else ""))
    return records
