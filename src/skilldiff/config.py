"""Load and validate a skilldiff.toml experiment file."""
from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

RULE_TYPES = {
    # transcript rules
    "no_command": ("pattern",),
    "command_used": ("pattern",),
    "no_tool": ("tool",),
    "tool_used": ("tool",),
    "skill_used": ("skill",),
    "skill_not_used": ("skill",),
    "reply_contains": ("pattern",),
    "reply_not_contains": ("pattern",),
    # workspace rules
    "file_exists": ("path",),
    "file_absent": ("path",),
    "file_contains": ("path", "pattern"),
    "file_not_contains": ("path", "pattern"),
    "files_unchanged": ("path",),
    "commit_message": ("pattern",),
    "no_new_commits": (),
    "check": ("run",),
}


class ConfigError(Exception):
    pass


@dataclass
class Arm:
    name: str
    skills: list[Path] = field(default_factory=list)
    plugins: list[Path] = field(default_factory=list)


@dataclass
class Rule:
    id: str
    type: str
    params: dict
    description: str = ""


@dataclass
class Task:
    id: str
    prompt: str
    fixture: Path | None
    uncommitted: Path | None
    expect_skill: str | None
    rules: list[Rule]
    git_init: bool = True
    root: Path | None = None   # folder of the file that defined the task ($SKILLDIFF_CONFIG_DIR for checks)


@dataclass
class RunSettings:
    repeats: int = 3
    parallel: int = 4
    model: str | None = None
    max_turns: int = 30
    timeout_seconds: int = 900
    max_budget_usd: float | None = None
    permission_mode: str = "bypassPermissions"
    isolate_user_config: bool = False
    extra_args: list[str] = field(default_factory=list)
    agent_cmd: str = "claude"


@dataclass
class Thresholds:
    min_drop: float = 0.5
    selection_min_drop: float = 0.5


@dataclass
class Config:
    path: Path
    root: Path
    before: Arm
    after: Arm
    run: RunSettings
    thresholds: Thresholds
    tasks: list[Task]


_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")


def _resolve(root: Path, value, what: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ConfigError(f"{what} must be a non-empty string path")
    p = (root / value).resolve()
    if not p.exists():
        raise ConfigError(f"{what} does not exist: {value} (resolved to {p})")
    return p


def _arm(root: Path, raw: dict, name: str) -> Arm:
    if not isinstance(raw, dict):
        raise ConfigError(f"[{name}] section is missing")
    skills = raw.get("skills", [])
    plugins = raw.get("plugins", [])
    if isinstance(skills, str):
        skills = [skills]
    if isinstance(plugins, str):
        plugins = [plugins]
    return Arm(
        name=name,
        skills=[_resolve(root, s, f"[{name}].skills entry") for s in skills],
        plugins=[_resolve(root, s, f"[{name}].plugins entry") for s in plugins],
    )


def _rule(raw: dict, task_id: str, idx: int) -> Rule:
    if not isinstance(raw, dict):
        raise ConfigError(f"task {task_id}: rule #{idx + 1} must be a table")
    rtype = raw.get("type")
    if rtype not in RULE_TYPES:
        raise ConfigError(
            f"task {task_id}: rule #{idx + 1} has unknown type {rtype!r}. "
            f"Known types: {', '.join(sorted(RULE_TYPES))}"
        )
    for key in RULE_TYPES[rtype]:
        if key not in raw:
            raise ConfigError(f"task {task_id}: rule #{idx + 1} ({rtype}) needs '{key}'")
    for key in ("pattern",):
        if key in raw:
            try:
                re.compile(raw[key])
            except re.error as e:
                raise ConfigError(f"task {task_id}: rule #{idx + 1} bad regex {raw[key]!r}: {e}")
    rid = raw.get("id") or f"{rtype}-{idx + 1}"
    params = {k: v for k, v in raw.items() if k not in ("id", "type", "description")}
    return Rule(id=str(rid), type=rtype, params=params, description=raw.get("description", ""))


def _task(rt: dict, root: Path, i: int, seen: set[str]) -> Task:
    tid = rt.get("id")
    if not tid or not _ID_RE.match(str(tid)):
        raise ConfigError(f"task #{i}: 'id' is required (letters, digits, - _ .)")
    if tid in seen:
        raise ConfigError(f"duplicate task id: {tid}")
    seen.add(tid)
    if not rt.get("prompt"):
        raise ConfigError(f"task {tid}: 'prompt' is required")
    rules = [_rule(x, tid, j) for j, x in enumerate(rt.get("rules", []))]
    rule_ids = [x.id for x in rules]
    if len(rule_ids) != len(set(rule_ids)):
        raise ConfigError(f"task {tid}: rule ids must be unique")
    if not rules and not rt.get("expect_skill"):
        raise ConfigError(f"task {tid}: give at least one rule or an expect_skill")
    return Task(
        id=str(tid),
        prompt=str(rt["prompt"]),
        fixture=_resolve(root, rt["fixture"], f"task {tid} fixture") if rt.get("fixture") else None,
        uncommitted=_resolve(root, rt["uncommitted"], f"task {tid} uncommitted") if rt.get("uncommitted") else None,
        expect_skill=rt.get("expect_skill"),
        rules=rules,
        git_init=bool(rt.get("git_init", True)),
        root=root,
    )


def load(path: str | Path) -> Config:
    path = Path(path).resolve()
    if not path.exists():
        raise ConfigError(f"config file not found: {path}")
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as e:
        raise ConfigError(f"{path.name}: invalid TOML: {e}")
    root = path.parent

    before = _arm(root, data.get("before"), "before")
    after = _arm(root, data.get("after"), "after")

    r = data.get("run", {})
    run = RunSettings(
        repeats=int(r.get("repeats", 3)),
        parallel=int(r.get("parallel", 4)),
        model=r.get("model"),
        max_turns=int(r.get("max_turns", 30)),
        timeout_seconds=int(r.get("timeout_seconds", 900)),
        max_budget_usd=r.get("max_budget_usd"),
        permission_mode=r.get("permission_mode", "bypassPermissions"),
        isolate_user_config=bool(r.get("isolate_user_config", False)),
        extra_args=list(r.get("extra_args", [])),
        agent_cmd=r.get("agent_cmd", "claude"),
    )
    if run.repeats < 1:
        raise ConfigError("[run].repeats must be at least 1")
    if run.parallel < 1:
        raise ConfigError("[run].parallel must be at least 1")

    t = data.get("thresholds", {})
    thresholds = Thresholds(
        min_drop=float(t.get("min_drop", 0.5)),
        selection_min_drop=float(t.get("selection_min_drop", 0.5)),
    )

    # Task lists can live in shared files: include = ["../shared/tasks.toml"].
    # Paths inside an included file resolve relative to that file.
    sources: list[tuple[Path, list]] = []
    for inc in data.get("include", []) or []:
        inc_path = _resolve(root, inc, "include entry")
        try:
            inc_data = tomllib.loads(inc_path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as e:
            raise ConfigError(f"{inc_path.name}: invalid TOML: {e}")
        sources.append((inc_path.parent, inc_data.get("tasks", [])))
    sources.append((root, data.get("tasks", [])))

    tasks: list[Task] = []
    seen: set[str] = set()
    i = 0
    for troot, raw_tasks in sources:
        for rt in raw_tasks:
            i += 1
            tasks.append(_task(rt, troot, i, seen))
    if not tasks:
        raise ConfigError("no [[tasks]] defined")
    return Config(path=path, root=root, before=before, after=after, run=run, thresholds=thresholds, tasks=tasks)
