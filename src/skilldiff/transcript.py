"""Parse Claude Code `--output-format stream-json` output into facts we can score."""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field

_SKILL_READ = re.compile(r"(?:^|/)(?:\.claude/)?skills/([^/]+)/SKILL\.md$")


@dataclass
class Step:
    kind: str          # "skill" | "tool" | "text"
    name: str
    detail: str = ""


@dataclass
class Transcript:
    available_skills: list[str] = field(default_factory=list)
    skills_invoked: list[str] = field(default_factory=list)   # in order, may repeat
    tools: list[str] = field(default_factory=list)
    commands: list[str] = field(default_factory=list)
    timeline: list[Step] = field(default_factory=list)
    reply: str = ""
    cost_usd: float | None = None
    duration_ms: int | None = None
    num_turns: int | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    model: str | None = None
    agent_version: str | None = None
    is_error: bool = False
    error: str | None = None
    got_result: bool = False

    @property
    def first_skill(self) -> str | None:
        return self.skills_invoked[0] if self.skills_invoked else None

    def to_dict(self) -> dict:
        d = asdict(self)
        d["first_skill"] = self.first_skill
        return d


def _short(v, n=160) -> str:
    s = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
    s = s.replace("\n", " ⏎ ")
    return s if len(s) <= n else s[: n - 1] + "…"


def _skill_from_tool(name: str, inp: dict) -> str | None:
    if name == "Skill":
        return inp.get("skill") or inp.get("command") or inp.get("name")
    if name == "Read":
        m = _SKILL_READ.search(str(inp.get("file_path", "")))
        if m:
            return m.group(1)
    return None


def parse(lines) -> Transcript:
    t = Transcript()
    texts: list[str] = []
    for raw in lines:
        raw = raw.strip()
        if not raw or not raw.startswith("{"):
            continue
        try:
            e = json.loads(raw)
        except json.JSONDecodeError:
            continue
        etype = e.get("type")
        if etype == "system" and e.get("subtype") == "init":
            t.available_skills = list(e.get("skills") or [])
            t.model = e.get("model")
            t.agent_version = e.get("claude_code_version")
        elif etype == "assistant":
            # Subagent messages carry parent_tool_use_id; we still count their skill use.
            for c in (e.get("message") or {}).get("content") or []:
                ctype = c.get("type")
                if ctype == "tool_use":
                    name = c.get("name", "?")
                    inp = c.get("input") or {}
                    skill = _skill_from_tool(name, inp)
                    if skill:
                        t.skills_invoked.append(skill)
                        t.timeline.append(Step("skill", skill, f"via {name}"))
                    else:
                        t.tools.append(name)
                        if name == "Bash":
                            cmd = str(inp.get("command", ""))
                            t.commands.append(cmd)
                            t.timeline.append(Step("tool", name, _short(cmd)))
                        else:
                            detail = inp.get("file_path") or inp.get("path") or inp.get("pattern") or inp.get("url") or inp
                            t.timeline.append(Step("tool", name, _short(detail)))
                elif ctype == "text" and c.get("text", "").strip():
                    texts.append(c["text"])
                    t.timeline.append(Step("text", "assistant", _short(c["text"], 220)))
        elif etype == "result":
            t.got_result = True
            t.cost_usd = e.get("total_cost_usd")
            t.duration_ms = e.get("duration_ms")
            t.num_turns = e.get("num_turns")
            usage = e.get("usage") or {}
            t.input_tokens = int(usage.get("input_tokens") or 0) + int(usage.get("cache_creation_input_tokens") or 0) + int(
                usage.get("cache_read_input_tokens") or 0
            )
            t.output_tokens = int(usage.get("output_tokens") or 0)
            t.is_error = bool(e.get("is_error")) or e.get("subtype") not in (None, "success")
            if isinstance(e.get("result"), str):
                t.reply = e["result"]
            if t.is_error:
                t.error = f"{e.get('subtype')}: {_short(e.get('result') or '', 300)}"
    if not t.reply and texts:
        t.reply = texts[-1]
    if not t.got_result and not t.error:
        t.is_error = True
        t.error = "agent produced no result event (crashed or timed out)"
    return t
