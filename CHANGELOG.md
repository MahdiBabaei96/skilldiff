# Changelog

## Unreleased

- Add `skilldiff diagnose` to reduce one task/rule failure to a freshly confirmed 1-minimal skill collection, preserving expected and explicitly pinned skills.
- Bound diagnosis runs, stop on noisy/error/runtime-drift evidence, and export input snapshots with hashes and reproduction instructions.
- Add a deterministic multi-skill interaction demo and diagnosis tests; no new paid experiments or novelty claims.

- Return exit code 2 for failed or missing runs; report incomplete experiments prominently and fail CI by default.
- Replace confidence labels with observed drops, raw p-values, and Holm adjustment across all comparable rules and skill selections.
- Clarify that temporary workspaces are not a sandbox and saved outputs are not redacted; warn before execution.
- Make raw transcript/file artifact uploads opt-in; report artifacts and comments still require privacy review.

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
