import json
import os
import sys
import textwrap
from pathlib import Path

import pytest

from skilldiff import cli
from skilldiff import config as config_mod
from skilldiff import rules as rules_mod
from skilldiff import transcript as transcript_mod
from skilldiff import workspace as ws_mod
from skilldiff.stats import fisher_one_sided, holm_adjust

HERE = Path(__file__).parent
FAKE = f"{sys.executable} {HERE / 'fake_claude.py'}"


# ---------------------------------------------------------------- stats

def test_fisher_extremes():
    assert fisher_one_sided(3, 3, 0, 3) == pytest.approx(0.05)
    assert fisher_one_sided(5, 5, 0, 5) == pytest.approx(1 / 252)
    assert fisher_one_sided(3, 3, 3, 3) == pytest.approx(1.0)
    assert fisher_one_sided(0, 0, 0, 3) == 1.0


def test_holm_adjusts_the_full_family_in_original_order():
    assert holm_adjust([]) == []
    assert holm_adjust([0.05]) == [0.05]
    assert holm_adjust([0.04, 0.01, 1.0]) == pytest.approx([0.08, 0.03, 1.0])
    assert holm_adjust([0.03, 0.04, 0.01]) == pytest.approx([0.06, 0.06, 0.03])


# ---------------------------------------------------------------- transcript

def test_parse_real_claude_code_stream():
    with open(HERE / "data" / "claude_code_2.1.312_stream.jsonl") as fh:
        t = transcript_mod.parse(fh)
    assert t.agent_version == "2.1.312"
    assert t.skills_invoked == ["greet"] and t.first_skill == "greet"
    assert "Write" in t.tools
    assert t.cost_usd and t.cost_usd > 0
    assert t.num_turns == 4 and not t.is_error
    assert "HELLO FROM SKILL" in t.reply
    assert t.timeline[0].kind == "skill"


def test_skill_detected_from_read_of_skill_md():
    lines = [json.dumps({"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": "Read", "input": {"file_path": "/x/ws/.claude/skills/pr-review/SKILL.md"}}]}})]
    t = transcript_mod.parse(lines)
    assert t.skills_invoked == ["pr-review"]
    assert t.is_error  # no result event


# ---------------------------------------------------------------- rules

def _state(**kw):
    t = transcript_mod.Transcript(commands=kw.get("commands", []), tools=kw.get("tools", []),
                                  reply=kw.get("reply", ""), skills_invoked=kw.get("skills", []))
    f = lambda d: {k: {"sha256": str(hash(v)), "size": len(v), "text": v} for k, v in d.items()}
    return rules_mod.RunState(t, f(kw.get("before", {})), f(kw.get("after", {})), {"commits": kw.get("commits", [])}, None)


def _rule(rtype, **params):
    return config_mod.Rule(id=rtype, type=rtype, params=params)


@pytest.mark.parametrize("rule,state,expected", [
    (_rule("no_command", pattern=r"git\s+push"), dict(commands=["git status", "git push origin main"]), False),
    (_rule("no_command", pattern=r"git\s+push"), dict(commands=["git commit -m x"]), True),
    (_rule("command_used", pattern="unittest"), dict(commands=["python -m unittest"]), True),
    (_rule("no_tool", tool="WebFetch"), dict(tools=["Read", "WebFetch"]), False),
    (_rule("skill_used", skill="a"), dict(skills=["b", "a"]), True),
    (_rule("skill_not_used", skill="a"), dict(skills=["a"]), False),
    (_rule("reply_not_contains", pattern="secret123"), dict(reply="the token is secret123"), False),
    (_rule("reply_contains", pattern="REVIEW.md"), dict(reply="See REVIEW.md"), True),
    (_rule("file_exists", path="REVIEW.md"), dict(after={"REVIEW.md": "x"}), True),
    (_rule("file_exists", path="tests/test_*.py"), dict(after={"tests/test_a.py": "x"}), True),
    (_rule("file_absent", path="*.log"), dict(after={"a.log": "x"}), False),
    (_rule("file_contains", path="R.md", pattern=r"^Verdict: APPROVE$"), dict(after={"R.md": "a\nVerdict: APPROVE\n"}), True),
    (_rule("file_contains", path="R.md", pattern="x"), dict(after={}), False),
    (_rule("file_not_contains", path="R.md", pattern="x"), dict(after={}), True),
    (_rule("files_unchanged", path="src/**"), dict(before={"src/a.py": "1"}, after={"src/a.py": "2"}), False),
    (_rule("files_unchanged", path="src/**"), dict(before={"src/a.py": "1"}, after={"src/a.py": "1", "R.md": "n"}), True),
    (_rule("files_unchanged", path="src/**"), dict(before={}, after={"src/new.py": "1"}), False),
    (_rule("commit_message", pattern=r"^feat: "), dict(commits=[{"message": "feat: x"}]), True),
    (_rule("commit_message", pattern=r"^feat: "), dict(commits=[]), False),
    (_rule("no_new_commits"), dict(commits=[{"message": "x"}]), False),
])
def test_rules(rule, state, expected):
    assert rules_mod.evaluate(rule, _state(**state)).passed is expected


def test_files_unchanged_evidence_has_diff():
    r = rules_mod.evaluate(_rule("files_unchanged", path="src/**"),
                           _state(before={"src/a.py": "x = 1\n"}, after={"src/a.py": "x = 2\n"}))
    assert "-x = 1" in r.evidence and "+x = 2" in r.evidence


# ---------------------------------------------------------------- config

def test_config_errors(tmp_path):
    p = tmp_path / "s.toml"
    p.write_text('[before]\nskills=[]\n[after]\nskills=[]\n[[tasks]]\nid="a"\nprompt="x"\nrules=[{type="nope"}]\n')
    with pytest.raises(config_mod.ConfigError, match="unknown type"):
        config_mod.load(p)
    p.write_text('[before]\nskills=["missing"]\n[after]\nskills=[]\n')
    with pytest.raises(config_mod.ConfigError, match="does not exist"):
        config_mod.load(p)


def test_starter_config_is_valid(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert cli.main(["init"]) == 0
    for d in ("skills/commit-helper", "candidate", "fixtures/app"):
        (tmp_path / d).mkdir(parents=True)
    (tmp_path / "skills/commit-helper/SKILL.md").write_text("---\nname: commit-helper\ndescription: x\n---\n")
    (tmp_path / "candidate/SKILL.md").write_text("---\nname: c\ndescription: x\n---\n")
    cfg = config_mod.load(tmp_path / "skilldiff.toml")
    assert cfg.tasks[0].rules[0].params["pattern"] == r"git\s+push"


def test_discover_and_override(tmp_path):
    for base, name in (("a", "one"), ("b", "one")):
        d = tmp_path / base / name
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(f"---\nname: {name}\ndescription: from {base}\n---\n")
    skills, warnings = ws_mod.discover_skills([tmp_path / "a", tmp_path / "b"])
    assert len(skills) == 1 and skills[0].description == "from b"
    assert any("replaces" in w for w in warnings)


# ---------------------------------------------------------------- end to end with the fake agent

def _skill(dir_: Path, name: str, desc: str):
    (dir_ / name).mkdir(parents=True)
    (dir_ / name / "SKILL.md").write_text(f"---\nname: {name}\ndescription: {desc}\n---\nbody\n")


@pytest.fixture
def project(tmp_path):
    _skill(tmp_path / "skills", "careful-review", "Review code into REVIEW.md")
    _skill(tmp_path / "skills", "committer", "Commit changes")
    _skill(tmp_path / "cand", "greedy-review", "Review and fix anything")
    _skill(tmp_path / "control", "sql-style", "Format SQL")
    (tmp_path / "fx" / "src").mkdir(parents=True)
    (tmp_path / "fx" / "src" / "app.py").write_text("x = 1\n")
    (tmp_path / "fx" / "CHANGELOG.md").write_text("# Changelog\n")
    plan = {
        "routes": [
            {"prompt": "review", "skill": "greedy-review", "if_installed": "greedy-review"},
            {"prompt": "review", "skill": "careful-review"},
            {"prompt": "commit", "skill": "committer"},
        ],
        "actions": {
            "careful-review": [{"write": "REVIEW.md", "content": "- [nit] src/app.py:1 name\nVerdict: APPROVE\n"}],
            "greedy-review": [{"append": "src/app.py", "content": "y = 2\n"}],
            "committer": [{"append": "CHANGELOG.md", "content": "- thing\n"},
                          {"bash": "git add -A && git commit -qm 'feat: thing'"}],
        },
    }
    (tmp_path / "plan.json").write_text(json.dumps(plan))
    (tmp_path / "skilldiff.toml").write_text(textwrap.dedent(f"""
        [before]
        skills = ["skills"]
        [after]
        skills = ["skills", "cand/greedy-review"]
        [run]
        repeats = 3
        parallel = 4
        agent_cmd = "{FAKE}"
        [[tasks]]
        id = "review"
        prompt = "please review src/app.py"
        fixture = "fx"
        expect_skill = "careful-review"
        rules = [
          {{ id = "read-only", type = "files_unchanged", path = "src/**" }},
          {{ id = "review-file", type = "file_exists", path = "REVIEW.md" }},
          {{ id = "check-ok", type = "check", run = "test -f CHANGELOG.md" }},
        ]
        [[tasks]]
        id = "commit"
        prompt = "commit it"
        fixture = "fx"
        expect_skill = "committer"
        rules = [
          {{ id = "conventional", type = "commit_message", pattern = "^feat: " }},
          {{ id = "no-push", type = "no_command", pattern = "git\\\\s+push" }},
        ]
    """))
    os.environ["FAKE_CLAUDE_PLAN"] = str(tmp_path / "plan.json")
    return tmp_path


def test_end_to_end_detects_regression(project, monkeypatch):
    monkeypatch.chdir(project)
    code = cli.main(["run", "-o", "out"])
    assert code == 1
    rep = json.loads((project / "out" / "report.json").read_text())
    by = {t["id"]: t for t in rep["tasks"]}
    assert by["review"]["verdict"] == "regressed"
    assert by["commit"]["verdict"] == "unchanged"
    assert all(r["after"]["pass"] == 3 for r in by["commit"]["rules"]), "agent commits must work in the workspace"
    rules = {r["id"]: r for r in by["review"]["rules"]}
    assert rules["read-only"]["before"] == {"pass": 3, "n": 3}
    assert rules["read-only"]["after"] == {"pass": 0, "n": 3}
    assert rules["read-only"]["drop_pp"] == 100
    assert rules["read-only"]["p"] == pytest.approx(0.05)
    assert rep["statistics"]["comparisons"] == 7  # five rules and two skill selections
    assert rules["read-only"]["p_adjusted"] == pytest.approx(0.35)
    assert not rep["inconclusive"]
    assert "+y = 2" in rules["read-only"]["evidence"][0]["evidence"]
    assert rules["read-only"]["evidence"][0]["count"] == 3
    assert rules["check-ok"]["status"] == "unchanged"
    assert by["review"]["selection"]["taken_by"] == {"greedy-review": 3}
    assert rep["new_skills"] == ["greedy-review"]
    md = (project / "out" / "report.md").read_text()
    assert "rule failures in 1 of 2 workflows" in md
    assert "Holm p=0.350" in md and "confidence high" not in md
    assert "not redacted" in md
    assert "<!-- skilldiff-report -->" in md
    html = (project / "out" / "report.html").read_text()
    assert "greedy-review" in html and "<table>" in html
    # raw artifacts are kept for inspection
    assert (project / "out/runs/review/after/0/files/src/app.py").read_text().endswith("y = 2\n")
    assert (project / "out/runs/review/after/0/original/src/app.py").read_text() == "x = 1\n"
    # re-rendering from disk gives the same verdicts
    assert cli.main(["report", "out", "--fail-on", "regression"]) == 1


def test_control_shows_no_change(project, monkeypatch):
    monkeypatch.chdir(project)
    code = cli.main(["run", "-o", "out2", "--after-skills", "skills", "control/sql-style", "--repeats", "2"])
    assert code == 0
    rep = json.loads((project / "out2" / "report.json").read_text())
    assert {t["verdict"] for t in rep["tasks"]} == {"unchanged"}
    assert "no detected regressions" in (project / "out2" / "report.md").read_text()


@pytest.mark.parametrize("fail_on,expected", [("regression", 2), ("substitution", 2), ("never", 0)])
def test_crashing_agent_is_inconclusive(project, monkeypatch, fail_on, expected):
    monkeypatch.chdir(project)
    monkeypatch.setenv("FAKE_CLAUDE_CRASH", "1")
    code = cli.main(["run", "-o", "out3", "--repeats", "1", "--task", "commit", "--fail-on", fail_on])
    assert code == expected
    rep = json.loads((project / "out3" / "report.json").read_text())
    t = rep["tasks"][0]
    assert t["verdict"] == "no-data" and t["after"]["errors"] == 1
    assert rep["inconclusive"] and t["incomplete"]
    assert "Inconclusive" in (project / "out3/report.md").read_text()
    assert "Inconclusive" in (project / "out3/report.html").read_text()
    assert cli.main(["report", "out3", "--fail-on", "regression"]) == 2
    assert any("simulated crash" in m or "exited 3" in m for m in t["after"]["error_messages"])


def test_dry_run_lists_isolated_commands(project, monkeypatch, capsys):
    monkeypatch.chdir(project)
    assert cli.main(["run", "-o", "out4", "--dry-run"]) == 0
    out = capsys.readouterr().out
    assert out.count("--setting-sources project") == 12
    assert "--output-format stream-json" in out
    assert not (project / "out4").exists()


@pytest.mark.parametrize("missing", [False, True])
def test_partial_runs_cannot_produce_a_clean_pass(project, monkeypatch, missing):
    from skilldiff.compare import compare
    from skilldiff import report

    monkeypatch.chdir(project)
    assert cli.main(["run", "-o", "partial", "--task", "commit"]) == 0
    meta, records = cli._load_records(project / "partial")
    i = next(i for i, r in enumerate(records) if r["arm"] == "after")
    if missing:
        records.pop(i)
    else:
        records[i]["transcript"].update(is_error=True, error="rate limited")
    cmp = compare(meta, records)
    assert cmp["inconclusive"]
    assert cmp["tasks"][0]["after"]["valid"] == 2
    assert cli._exit_code(cmp, "regression") == 2
    assert cli._exit_code(cmp, "substitution") == 2
    assert cli._exit_code(cmp, "never") == 0
    assert "Inconclusive" in report.headline(cmp)
    md = report.to_markdown(cmp)
    assert "incomplete" in md and "✅" not in report.headline(cmp)
    if not missing:
        assert "rate limited" in md


def test_nonzero_exit_overrides_success_event(project, monkeypatch):
    from skilldiff import runner

    cfg = config_mod.load(project / "skilldiff.toml")
    skills, _ = ws_mod.discover_skills(cfg.before.skills)

    def failed_process(cmd, cwd, env, timeout, out_path):
        out_path.write_text(json.dumps({"type": "result", "subtype": "success", "result": "done"}) + "\n")
        return 1, False, "late process failure"

    monkeypatch.setattr(runner, "_run_process", failed_process)
    rec = runner.run_one(cfg, runner.Job(cfg.tasks[0], cfg.before, 0), skills, project / "nonzero")
    assert rec["transcript"]["is_error"]
    assert "agent exited 1" in rec["transcript"]["error"]


def test_compact_events_strips_chunks_and_identifiers(tmp_path):
    from skilldiff.runner import _compact_events
    p = tmp_path / "events.jsonl"
    p.write_text("\n".join(json.dumps(e) for e in [
        {"type": "system", "subtype": "init", "session_id": "S", "skills": ["a"], "model": "m",
         "scratchpad_path": "/private/x", "mcp_servers": [{"name": "secret"}]},
        {"type": "stream_event", "event": {"delta": "x"}},
        {"type": "assistant", "session_id": "S", "uuid": "U", "message": {"content": []}},
        "not json",
    ]) + "\n")
    _compact_events(p)
    lines = [json.loads(x) for x in p.read_text().splitlines()]
    assert len(lines) == 2
    assert lines[0] == {"type": "system", "subtype": "init", "model": "m", "skills": ["a"]}
    assert "session_id" not in lines[1] and "uuid" not in lines[1]
