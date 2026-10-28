#!/usr/bin/env python3
"""A deterministic stand-in for `claude -p ... --output-format stream-json`.

It lets the test-suite exercise skilldiff end to end without API calls. It
emits the same event shapes as Claude Code 2.1.x (see
tests/data/claude_code_2.1.312_stream.jsonl, a sanitized real transcript).

Behaviour comes from the JSON file named in $FAKE_CLAUDE_PLAN:
{
  "routes":  [{"prompt": "regex", "skill": "name", "if_installed": "name"?}],   first match wins
  "actions": {"skill-name": [{"write": "path", "content": "..."} | {"append": "path", "content": "..."}
                              | {"bash": "command"}]},
  "reply":   {"skill-name": "final reply"}
}
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def emit(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


def main():
    args = sys.argv[1:]
    if args == ["--version"]:
        print("9.9.9 (Fake Claude)")
        return 0
    prompt = args[args.index("-p") + 1]
    plan = json.loads(Path(os.environ["FAKE_CLAUDE_PLAN"]).read_text())
    cwd = Path.cwd()
    installed = sorted(p.name for p in (cwd / ".claude" / "skills").iterdir()) if (cwd / ".claude" / "skills").exists() else []
    emit({"type": "system", "subtype": "init", "cwd": str(cwd), "model": "fake-model", "claude_code_version": "9.9.9",
          "skills": installed, "tools": ["Bash", "Read", "Write", "Skill"]})
    if os.environ.get("FAKE_CLAUDE_CRASH"):
        sys.stderr.write("simulated crash\n")
        return 3

    skill = None
    for route in plan["routes"]:
        if route.get("if_installed") and route["if_installed"] not in installed:
            continue
        if re.search(route["prompt"], prompt, re.I) and route["skill"] in installed:
            skill = route["skill"]
            break

    n = 0

    def tool(name, inp):
        nonlocal n
        n += 1
        emit({"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "tool_use", "id": f"toolu_{n}", "name": name, "input": inp}]}})
        emit({"type": "user", "message": {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": f"toolu_{n}", "content": "ok"}]}})

    if skill:
        tool("Skill", {"skill": skill})
        for act in plan["actions"].get(skill, []):
            if "write" in act:
                p = cwd / act["write"]
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(act["content"])
                tool("Write", {"file_path": str(p), "content": act["content"]})
            elif "append" in act:
                p = cwd / act["append"]
                with open(p, "a") as fh:
                    fh.write(act["content"])
                tool("Edit", {"file_path": str(p), "old_string": "", "new_string": act["content"]})
            elif "bash" in act:
                subprocess.run(act["bash"], shell=True, cwd=cwd, capture_output=True)
                tool("Bash", {"command": act["bash"]})
    reply = plan.get("reply", {}).get(skill or "", "Done.")
    emit({"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": reply}]}})
    emit({"type": "result", "subtype": "success", "is_error": False, "duration_ms": 1200, "num_turns": n + 1,
          "result": reply, "total_cost_usd": 0.01 * (n + 1),
          "usage": {"input_tokens": 10, "cache_read_input_tokens": 1000, "cache_creation_input_tokens": 0, "output_tokens": 50}})
    return 0


if __name__ == "__main__":
    sys.exit(main())
