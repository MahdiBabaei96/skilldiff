"""Build isolated, throwaway workspaces and snapshot what an agent left in them."""
from __future__ import annotations

import fnmatch
import hashlib
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .config import Arm

IGNORED_DIRS = {".git", ".claude", "__pycache__", ".pytest_cache", "node_modules", ".venv"}
MAX_SNAPSHOT_BYTES = 256 * 1024
_GIT_ENV = {
    "GIT_AUTHOR_NAME": "skilldiff",
    "GIT_AUTHOR_EMAIL": "skilldiff@example.invalid",
    "GIT_COMMITTER_NAME": "skilldiff",
    "GIT_COMMITTER_EMAIL": "skilldiff@example.invalid",
}


@dataclass
class SkillEntry:
    declared_name: str  # `name:` from SKILL.md frontmatter
    name: str          # the id Claude Code uses: the skill's folder name
    folder: str        # same as name; kept for clarity at copy time
    source: Path
    description: str


def _frontmatter(skill_md: Path) -> dict:
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^---\s*\n(.*?)\n---\s*(\n|$)", text, re.S)
    out: dict = {}
    if not m:
        return out
    for line in m.group(1).splitlines():
        mm = re.match(r"^([A-Za-z_-]+)\s*:\s*(.*)$", line)
        if mm:
            out[mm.group(1)] = mm.group(2).strip().strip("'\"")
    return out


def discover_skills(paths: list[Path]) -> tuple[list[SkillEntry], list[str]]:
    """Each path is a skill folder (has SKILL.md) or a folder of skill folders.

    Later paths override earlier ones with the same folder name, which is how a
    PR that *updates* an existing skill is modelled. Returns (skills, warnings).
    """
    found: dict[str, SkillEntry] = {}
    warnings: list[str] = []
    for p in paths:
        if (p / "SKILL.md").is_file():
            candidates = [p]
        else:
            candidates = sorted(c for c in p.iterdir() if c.is_dir() and (c / "SKILL.md").is_file())
            if not candidates:
                warnings.append(f"no skills found in {p}")
        for c in candidates:
            fm = _frontmatter(c / "SKILL.md")
            entry = SkillEntry(
                declared_name=fm.get("name") or c.name,
                name=c.name,
                folder=c.name,
                source=c,
                description=fm.get("description", ""),
            )
            if entry.declared_name != c.name:
                warnings.append(f"folder '{c.name}' declares name '{entry.declared_name}'; "
                                f"Claude Code lists and invokes it as '{c.name}'")
            if c.name in found and found[c.name].source != c:
                warnings.append(f"skill folder '{c.name}' from {c} replaces the one from {found[c.name].source}")
            found[c.name] = entry
    declared = [s.declared_name for s in found.values()]
    for n in sorted({n for n in declared if declared.count(n) > 1}):
        folders = ", ".join(s.folder for s in found.values() if s.declared_name == n)
        warnings.append(f"skills in folders {folders} all declare name '{n}'; Claude Code lists them by folder name")
    return list(found.values()), warnings


def _git(ws: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    env = {**os.environ, **_GIT_ENV}
    return subprocess.run(["git", *args], cwd=ws, env=env, capture_output=True, text=True, check=check)


def _copy_tree(src: Path, dst: Path) -> None:
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)


def build_workspace(task, arm: Arm, skills: list[SkillEntry]) -> tuple[Path, str | None]:
    """Create a fresh temp directory with the fixture, git history and skills.

    The workspace lives in the system temp dir, never inside the user's repo, so
    no parent CLAUDE.md or .claude/ folder can leak into the experiment.
    Returns (workspace, base_commit).
    """
    root = Path(tempfile.mkdtemp(prefix="skilldiff-"))
    ws = root / "ws"
    ws.mkdir()
    if task.fixture:
        _copy_tree(task.fixture, ws)
    base = None
    if task.git_init:
        _git(ws, "init", "-q", "-b", "main")
        # the agent's own git commands need an identity, but must not see the user's
        _git(ws, "config", "user.name", "skilldiff")
        _git(ws, "config", "user.email", "skilldiff@example.invalid")
        _git(ws, "config", "commit.gpgsign", "false")
        (ws / ".git" / "info").mkdir(parents=True, exist_ok=True)
        with open(ws / ".git" / "info" / "exclude", "a") as fh:
            fh.write("\n.claude/\n")
        _git(ws, "add", "-A")
        _git(ws, "commit", "-q", "--allow-empty", "-m", "initial fixture")
        base = _git(ws, "rev-parse", "HEAD").stdout.strip()
    if task.uncommitted:
        _copy_tree(task.uncommitted, ws)
    skills_dir = ws / ".claude" / "skills"
    skills_dir.mkdir(parents=True)
    for s in skills:
        shutil.copytree(s.source, skills_dir / s.folder)
    return ws, base


def _walk(ws: Path):
    for dirpath, dirnames, filenames in os.walk(ws):
        dirnames[:] = sorted(d for d in dirnames if d not in IGNORED_DIRS)
        for f in sorted(filenames):
            full = Path(dirpath) / f
            yield full.relative_to(ws).as_posix(), full


def snapshot(ws: Path) -> dict[str, dict]:
    """path -> {sha256, size, text (if small and decodable)}"""
    out: dict[str, dict] = {}
    for rel, full in _walk(ws):
        try:
            data = full.read_bytes()
        except OSError:
            continue
        entry = {"sha256": hashlib.sha256(data).hexdigest(), "size": len(data)}
        if len(data) <= MAX_SNAPSHOT_BYTES:
            try:
                entry["text"] = data.decode("utf-8")
            except UnicodeDecodeError:
                pass
        out[rel] = entry
    return out


def git_state(ws: Path, base: str | None) -> dict:
    if base is None or not (ws / ".git").exists():
        return {"commits": [], "branch": None}
    log = _git(ws, "log", "--format=%H%x1f%B%x1e", f"{base}..HEAD", check=False).stdout
    commits = []
    for chunk in log.split("\x1e"):
        chunk = chunk.strip()
        if not chunk:
            continue
        sha, _, msg = chunk.partition("\x1f")
        commits.append({"sha": sha.strip(), "message": msg.strip()})
    branch = _git(ws, "rev-parse", "--abbrev-ref", "HEAD", check=False).stdout.strip()
    return {"commits": list(reversed(commits)), "branch": branch}


def glob_match(path: str, pattern: str) -> bool:
    if fnmatch.fnmatch(path, pattern):
        return True
    # make "src/**" also match "src/a.py" and "src/x/y.py"
    if pattern.endswith("/**") and path.startswith(pattern[:-2]):
        return True
    return False


def cleanup(ws: Path) -> None:
    shutil.rmtree(ws.parent, ignore_errors=True)
