import json
import hashlib
import sys
from dataclasses import replace
from pathlib import Path

import pytest

from skilldiff import cli, config, runner
from skilldiff.diagnose import classify, diagnose, reduce_set


def record(passed=True, error=False, model="fake-model"):
    return {"transcript": {"is_error": error, "model": model, "agent_version": "9.9.9",
                           "error": "simulated failure" if error else None},
            "rules": [{"id": "read-only", "passed": passed}]}


def test_classify_requires_complete_unambiguous_evidence():
    assert classify([record(False)] * 3, "read-only", 3, 0, 1) == ("fail", 3)
    assert classify([record()] * 3, "read-only", 3, 0, 1) == ("pass", 0)
    assert classify([record(), record(False)], "read-only", 2, 0, 1) == ("unknown", 1)
    assert classify([record(error=True)] * 3, "read-only", 3, 0, 1)[0] == "unknown"
    assert classify([record()], "read-only", 3, 0, 1)[0] == "unknown"
    assert classify([record()], "missing", 1, 0, 1)[0] == "unknown"


def test_reducer_preserves_multi_skill_interaction():
    result = reduce_set(["a", "b", "c", "noise"], lambda xs: {"a", "c"} <= set(xs))
    assert result == ["a", "c"]
    assert reduce_set(["noise"], lambda xs: True) == []


def test_reducer_does_not_claim_global_minimality_for_nonmonotonic_failure():
    fails = lambda xs: set(xs) in ({"a", "b", "c"}, {"a", "b"}, {"c"})
    result = reduce_set(["a", "b", "c"], fails)
    assert fails(result)
    assert all(not fails(result[:i] + result[i + 1:]) for i in range(len(result)))


@pytest.fixture
def project(tmp_path):
    for name in ("review", "a", "b", "noise1", "noise2"):
        root = tmp_path / "skills" / name
        root.mkdir(parents=True)
        (root / "SKILL.md").write_text(f"---\nname: {name}\ndescription: {name}\n---\nSynthetic test skill.\n")
    (tmp_path / "fixture").mkdir()
    (tmp_path / "fixture/app.py").write_text("x = 1\n")
    plan = {"routes": [{"prompt": "review", "skill": "a", "if_all_installed": ["a", "b"]},
                       {"prompt": "review", "skill": "review"}],
            "actions": {"a": [{"write": "app.py", "content": "x = 2\n"}]}}
    (tmp_path / "plan.json").write_text(json.dumps(plan))
    fake = Path(__file__).parent / "fake_claude.py"
    agent = f"{sys.executable} {fake}"
    (tmp_path / "skilldiff.toml").write_text(
        '[before]\nskills=["skills/review"]\n[after]\nskills=["skills"]\n'
        f'[run]\nagent_cmd={json.dumps(agent)}\nrepeats=2\n'
        '[[tasks]]\nid="review"\nprompt="review app.py"\nfixture="fixture"\nexpect_skill="review"\n'
        'rules=[{id="read-only",type="files_unchanged",path="app.py"}]\n')
    return config.load(tmp_path / "skilldiff.toml")


def test_cli_reduces_confirms_and_exports_real_fake_agent_runs(project, monkeypatch, tmp_path):
    monkeypatch.setenv("FAKE_CLAUDE_PLAN", str(tmp_path / "plan.json"))
    out = tmp_path / "diagnosis"
    assert cli.main(["diagnose", "-c", str(project.path), "--task", "review", "--rule", "read-only",
                     "-o", str(out), "--max-runs", "100"]) == 0
    result = json.loads((out / "diagnosis.json").read_text())
    assert result['status'] == "confirmed-1-minimal"
    assert result['candidate'] == ["a", "b", "review"]
    assert result['pinned'] == ["review"]
    assert {x['removed'] for x in result['confirmation']} == {"a", "b"}
    assert all(x['outcome'] == "pass" for x in result['confirmation'])
    assert len({p['id'] for p in result['probes']}) == len(result['probes'])
    assert result['runs_used'] == len(result['probes']) * 2
    cfg = config.load(out / "reproducer/skilldiff.toml")
    assert cfg.tasks[0].fixture.is_dir()
    assert cfg.tasks[0].expect_skill == "review"
    assert cli.main(["run", "-c", str(out / "reproducer/skilldiff.toml"),
                     "-o", str(tmp_path / "rerun")]) == 1
    manifest = json.loads((out / "reproducer/manifest.json").read_text())
    assert "fixture/app.py" in manifest and "after/a/SKILL.md" in manifest
    for path, digest in manifest.items():
        assert hashlib.sha256((out / "reproducer" / path).read_bytes()).hexdigest() == digest
    assert (out / "probes/0/runs/review/before/0/events.jsonl").exists()
    assert "not a globally smallest set" in (out / "diagnosis.md").read_text()


def oracle(monkeypatch, predicate):
    calls = []

    def run(cfg, job, skills, out, **kwargs):
        names = {s.name for s in skills}
        calls.append((names, out.name))
        return predicate(names, out.name, job.rep)

    monkeypatch.setattr(runner, "run_one", run)
    return calls


def test_budget_includes_confirmations_and_never_overruns(project, tmp_path, monkeypatch):
    calls = oracle(monkeypatch, lambda names, pid, rep: record(not {"a", "b"} <= names))
    result = diagnose(project, "review", "read-only", tmp_path / "budget", repeats=2, max_runs=5)
    assert result['status'] == "budget-exhausted"
    assert result['runs_used'] == len(calls) == 4
    assert not (tmp_path / "budget/reproducer").exists()


@pytest.mark.parametrize("mode,expected", [("mixed", "inconclusive"), ("error", "inconclusive"),
                                         ("runtime", "inconclusive"), ("baseline", "baseline-failed"),
                                         ("pass", "not-reproduced")])
def test_rejects_noise_errors_and_bad_baselines(project, tmp_path, monkeypatch, mode, expected):
    def predicate(names, pid, rep):
        if mode == "baseline":
            return record(False)
        if mode == "pass":
            return record()
        if pid == "1":
            if mode == "runtime":
                return record(False, model="different-model")
            if mode == "error":
                return record(error=True)
            return record(rep == 0)
        return record()

    oracle(monkeypatch, predicate)
    result = diagnose(project, "review", "read-only", tmp_path / mode, repeats=2)
    assert result['status'] == expected
    assert not (tmp_path / mode / "reproducer").exists()


def test_fresh_confirmation_cannot_reuse_search_cache(project, tmp_path, monkeypatch):
    seen = {}

    def predicate(names, pid, rep):
        key = tuple(sorted(names))
        seen.setdefault(key, set()).add(pid)
        failed = {"a", "b"} <= names
        # Same reduced collection changes behavior on a fresh probe.
        if key == ("a", "b", "review") and len(seen[key]) > 1:
            failed = False
        return record(not failed)

    oracle(monkeypatch, predicate)
    result = diagnose(project, "review", "read-only", tmp_path / "drift", repeats=2)
    assert result['status'] == "inconclusive"
    assert "fresh confirmation" in result['message']


def test_expected_and_extra_pins_are_never_removed(project, tmp_path, monkeypatch):
    calls = oracle(monkeypatch, lambda names, pid, rep: record(not {"a", "b"} <= names))
    result = diagnose(project, "review", "read-only", tmp_path / "pins", repeats=2, keep_skills=["noise1"])
    assert result['status'] == "confirmed-1-minimal"
    assert result['candidate'] == ["a", "b", "noise1", "review"]
    assert all({"review", "noise1"} <= names for names, pid in calls if pid != "0" and len(names) != 1)


@pytest.mark.parametrize("options", [{"repeats": 1}, {"pass_rate": 0.8, "failure_rate": 0.2},
                                   {"max_runs": 0}, {"keep_skills": ["missing"]}])
def test_invalid_input_runs_nothing(project, tmp_path, monkeypatch, options):
    calls = oracle(monkeypatch, lambda *args: pytest.fail("must not run"))
    with pytest.raises(config.ConfigError):
        diagnose(project, "review", "read-only", tmp_path / "invalid", **options)
    assert not calls


def test_rejects_plugin_and_shell_check_bundles(project, tmp_path):
    project.after.plugins = [tmp_path]
    with pytest.raises(config.ConfigError, match="plugin"):
        diagnose(project, "review", "read-only", tmp_path / "out")
    project.after.plugins = []
    project.tasks[0].rules[0].type = "check"
    with pytest.raises(config.ConfigError, match="shell-check"):
        diagnose(project, "review", "read-only", tmp_path / "out")


def test_existing_output_is_preserved(project, tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    (out / "keep").write_text("keep")
    with pytest.raises(config.ConfigError, match="already exists"):
        diagnose(project, "review", "read-only", out)
    assert (out / "keep").read_text() == "keep"


def test_fresh_deletion_failure_invalidates_minimality(project, tmp_path, monkeypatch):
    calls = {}

    def predicate(names, pid, rep):
        key = tuple(sorted(names))
        calls.setdefault(key, set()).add(pid)
        fails = {"a", "b"} <= names
        if key == ("b", "review") and len(calls[key]) > 1:
            fails = True
        return record(not fails)

    oracle(monkeypatch, predicate)
    result = diagnose(project, "review", "read-only", tmp_path / "deletion", repeats=2)
    assert result['status'] == "inconclusive"
    assert "single-deletion" in result['message']


def test_pinned_only_failure_is_not_labelled_a_multi_skill_interaction(project, tmp_path, monkeypatch):
    # Distinguish the before control from all after probes, including anchor-only.
    monkeypatch.setattr(runner, "run_one", lambda cfg, job, skills, out:
                        record(job.arm.name == "before"))
    result = diagnose(project, "review", "read-only", tmp_path / "anchor", repeats=2)
    assert result['status'] == "confirmed-1-minimal"
    assert result['candidate'] == ["review"]
    assert "pinned collection alone" in result['message']


def test_unrelated_shell_checks_are_not_executed(project, tmp_path, monkeypatch):
    project.tasks[0].rules.append(config.Rule("dangerous", "check", {"run": "exit 1"}))

    def run(cfg, job, skills, out):
        assert [r.id for r in job.task.rules] == ["read-only"]
        return record(not {"a", "b"} <= {s.name for s in skills})

    monkeypatch.setattr(runner, "run_one", run)
    result = diagnose(project, "review", "read-only", tmp_path / "selected", repeats=2)
    assert result['status'] == "confirmed-1-minimal"


def test_interruption_writes_inconclusive_report(project, tmp_path, monkeypatch):
    def interrupt(*args, **kwargs):
        raise KeyboardInterrupt

    monkeypatch.setattr(runner, "run_one", interrupt)
    result = diagnose(project, "review", "read-only", tmp_path / "interrupted", repeats=2)
    assert result['status'] == "interrupted"
    assert (tmp_path / "interrupted/diagnosis.md").exists()


def test_interruption_terminates_agent_process_group(tmp_path, monkeypatch):
    import signal

    class Process:
        pid = 12345
        calls = 0

        def communicate(self, **kwargs):
            self.calls += 1
            if self.calls == 1:
                raise KeyboardInterrupt
            return None, ""

    proc = Process()
    killed = []
    monkeypatch.setattr(runner.subprocess, "Popen", lambda *a, **kw: proc)
    monkeypatch.setattr(runner.os, "killpg", lambda pid, sig: killed.append((pid, sig)))
    with pytest.raises(KeyboardInterrupt):
        runner._run_process(["fake"], tmp_path, {}, 10, tmp_path / "events.jsonl")
    assert killed == [(12345, signal.SIGKILL)]
    assert proc.calls == 2


def test_inputs_are_frozen_before_any_probe(project, tmp_path, monkeypatch):
    original = tmp_path / "skills/a/SKILL.md"
    expected = original.read_text()

    def run(cfg, job, skills, out):
        original.write_text("changed during diagnosis")
        for entry in skills:
            assert entry.source.is_relative_to(tmp_path / "frozen/inputs")
            if entry.name == "a":
                assert (entry.source / "SKILL.md").read_text() == expected
        assert job.task.fixture.is_relative_to(tmp_path / "frozen/inputs")
        return record(not {"a", "b"} <= {s.name for s in skills})

    monkeypatch.setattr(runner, "run_one", run)
    result = diagnose(project, "review", "read-only", tmp_path / "frozen", repeats=2)
    assert result['status'] == "confirmed-1-minimal"
    assert "after/a/SKILL.md" in result['input_manifest']
    assert (tmp_path / "frozen/reproducer/after/a/SKILL.md").read_text() == expected
