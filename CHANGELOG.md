# Changelog

## [0.1.0] - 2026-10-28

First release.

- `skilldiff run`: before/after experiments in isolated temp workspaces, interleaved repeats, parallel runs.
- Skill selection tracking (Skill tool calls and SKILL.md reads), 16 rule types, file snapshots, git commit capture, cost and token totals.
- Reports in Markdown (PR comments), JSON, and standalone HTML with per-run timelines.
- One-sided Fisher exact test and confidence labels for every regression.
- `skilldiff report`, `validate`, `init`; shared task files via `include`.
- GitHub Action that compares a PR's skills with its base and posts a sticky comment.
- Claude Code plugin with a `skilldiff` skill that helps write tasks and read reports.
- Five measured examples.
