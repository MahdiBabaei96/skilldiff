# Contributing

Thanks for helping. The most useful contribution right now is **a real conflict from your own
collection**: a skill that, when added or changed, made another skill's workflow stop following
its rules. Open an issue with the two SKILL.md files (or a trimmed copy), the prompt, and the
skilldiff report.

## Development

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

The test suite never calls a model. `tests/fake_claude.py` emits the same stream-json events as
Claude Code, driven by a small JSON plan, so end-to-end behaviour (workspaces, rules, reports,
exit codes, the GitHub Action) is tested deterministically. `tests/data/` holds a sanitized real
Claude Code transcript that the parser is tested against; refresh it when the event format changes.

## Ground rules

- No runtime dependencies beyond the Python standard library.
- Every new rule type needs a test in `tests/test_skilldiff.py` and a row in the README table.
- Claims in the README and examples must come from committed, reproducible runs.
