"""Evaluate expected-behaviour rules against one finished run."""
from __future__ import annotations

import difflib
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .config import Rule
from .transcript import Transcript
from .workspace import glob_match


@dataclass
class RunState:
    transcript: Transcript
    before_files: dict      # snapshot before the agent ran
    after_files: dict       # snapshot after the agent ran
    git: dict
    workspace: Path | None  # None when re-scoring saved runs (check rules can't re-run)
    config_dir: Path | None = None


@dataclass
class RuleResult:
    id: str
    type: str
    passed: bool
    evidence: str = ""

    def to_dict(self):
        return {"id": self.id, "type": self.type, "passed": self.passed, "evidence": self.evidence}


def _flags(rule: Rule) -> int:
    return re.I if rule.params.get("ignore_case") else 0


def _clip(s: str, n: int = 600) -> str:
    return s if len(s) <= n else s[:n] + f"\n… ({len(s) - n} more chars)"


def _matching(files: dict, pattern: str) -> list[str]:
    return sorted(p for p in files if glob_match(p, pattern))


def _diff(a: str, b: str, path: str, max_lines: int = 40) -> str:
    lines = list(difflib.unified_diff(a.splitlines(), b.splitlines(), f"a/{path}", f"b/{path}", lineterm="", n=1))
    if len(lines) > max_lines:
        lines = lines[:max_lines] + [f"… ({len(lines) - max_lines} more diff lines)"]
    return "\n".join(lines)


def evaluate(rule: Rule, st: RunState) -> RuleResult:
    p = rule.params
    t = st.transcript
    ok, ev = True, ""
    kind = rule.type

    if kind in ("no_command", "command_used"):
        rx = re.compile(p["pattern"], _flags(rule))
        hits = [c for c in t.commands if rx.search(c)]
        if kind == "no_command":
            ok = not hits
            ev = ("ran: " + " | ".join(_clip(h, 200) for h in hits[:3])) if hits else ""
        else:
            ok = bool(hits)
            ev = "" if ok else f"no Bash command matched /{p['pattern']}/ ({len(t.commands)} commands run)"

    elif kind in ("no_tool", "tool_used"):
        n = t.tools.count(p["tool"])
        ok = (n == 0) if kind == "no_tool" else (n > 0)
        ev = f"{p['tool']} called {n}×" if not ok else ""

    elif kind in ("skill_used", "skill_not_used"):
        used = p["skill"] in t.skills_invoked
        ok = used if kind == "skill_used" else not used
        if not ok:
            ev = f"skills invoked: {', '.join(t.skills_invoked) or 'none'}"

    elif kind in ("reply_contains", "reply_not_contains"):
        found = re.search(p["pattern"], t.reply or "", _flags(rule) | re.M)
        ok = bool(found) if kind == "reply_contains" else not found
        if not ok:
            ev = ("reply matched: " + found.group(0)) if found else "final reply: " + _clip(t.reply or "(empty)", 300)

    elif kind in ("file_exists", "file_absent"):
        m = _matching(st.after_files, p["path"])
        ok = bool(m) if kind == "file_exists" else not m
        if not ok:
            if kind == "file_exists":
                created = sorted(set(st.after_files) - set(st.before_files))
                ev = f"{p['path']} not found; files created instead: {', '.join(created[:8]) or 'none'}"
            else:
                ev = f"found: {', '.join(m[:5])}"

    elif kind in ("file_contains", "file_not_contains"):
        m = _matching(st.after_files, p["path"])
        rx = re.compile(p["pattern"], _flags(rule) | re.M)
        if not m:
            ok = kind == "file_not_contains"
            ev = "" if ok else f"{p['path']} does not exist"
        else:
            hits = [f for f in m if rx.search(st.after_files[f].get("text", ""))]
            if kind == "file_contains":
                ok = bool(hits)
                if not ok:
                    ev = f"{m[0]} has no match for /{p['pattern']}/. Starts with:\n" + _clip(
                        st.after_files[m[0]].get("text", "(binary)"), 300
                    )
            else:
                ok = not hits
                if not ok:
                    mt = rx.search(st.after_files[hits[0]].get("text", ""))
                    ev = f"{hits[0]} contains: {mt.group(0) if mt else ''}"

    elif kind == "files_unchanged":
        changed = []
        for path in sorted(set(_matching(st.before_files, p["path"])) | set(_matching(st.after_files, p["path"]))):
            a, b = st.before_files.get(path), st.after_files.get(path)
            if (a or {}).get("sha256") != (b or {}).get("sha256"):
                changed.append(path)
        ok = not changed
        if changed:
            first = changed[0]
            a, b = st.before_files.get(first), st.after_files.get(first)
            if a is None:
                detail = "(created)"
            elif b is None:
                detail = "(deleted)"
            else:
                detail = _diff(a.get("text", ""), b.get("text", ""), first)
            ev = f"modified: {', '.join(changed[:6])}\n{detail}"

    elif kind == "commit_message":
        commits = st.git.get("commits", [])
        if not commits:
            ok, ev = False, "no new commit was made"
        else:
            rx = re.compile(p["pattern"], _flags(rule) | re.M)
            bad = [c for c in commits if not rx.search(c["message"])]
            ok = not bad
            if bad:
                ev = "commit message: " + _clip(bad[0]["message"], 200)

    elif kind == "no_new_commits":
        commits = st.git.get("commits", [])
        ok = not commits
        if commits:
            ev = f"{len(commits)} commit(s): " + _clip(commits[0]["message"].splitlines()[0] if commits[0]["message"] else "", 120)

    elif kind == "check":
        if st.workspace is None:
            return RuleResult(rule.id, kind, False, "check rules can only run during `skilldiff run`")
        try:
            proc = subprocess.run(
                p["run"], shell=True, cwd=st.workspace, capture_output=True, text=True,
                timeout=int(p.get("timeout_seconds", 120)),
                env={**os.environ, "SKILLDIFF_WORKSPACE": str(st.workspace),
                     "SKILLDIFF_CONFIG_DIR": str(st.config_dir or "")},
            )
            ok = proc.returncode == 0
            if not ok:
                ev = f"`{p['run']}` exited {proc.returncode}\n" + _clip((proc.stdout + proc.stderr).strip()[-600:], 600)
        except subprocess.TimeoutExpired:
            ok, ev = False, f"`{p['run']}` timed out"

    return RuleResult(rule.id, kind, ok, ev)
