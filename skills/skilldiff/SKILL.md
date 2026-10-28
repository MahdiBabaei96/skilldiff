---
name: skilldiff
description: Use when the user wants to know whether adding, updating, or removing a Claude skill or plugin will break the skills and workflows they already have, or wants regression tests for a skill collection. Runs real before/after experiments with the skilldiff CLI and explains the report.
---

# skilldiff: will this skill break my setup?

skilldiff answers one question with measured evidence: when a skill is added, changed, or
removed, do the workflows the *existing* skills guard still run the right skill and still
follow their rules? It runs every task several times with the current collection ("before")
and with the proposed collection ("after"), each run in a fresh temp workspace, then
compares skill selection, rule pass rates, changed files, and cost.

A task can pass while the wrong skill ran and quietly dropped the rules only the intended
skill enforces. That is what this tool is for. Don't use it as a general eval framework for
a single skill; `claude plugin eval` covers that.

## 1. Make sure the CLI is available

```bash
skilldiff --version || pipx install git+https://github.com/MahdiBabaei96/skilldiff
```

If `pipx` is missing, `pip install git+https://github.com/MahdiBabaei96/skilldiff` works too.
It needs Python 3.11+ and Claude Code (`claude`) on PATH, signed in or with
`ANTHROPIC_API_KEY` set.

## 2. Work out the two arms

- **Adding a skill:** before = the installed collection; after = the collection plus the candidate.
- **Changing a skill:** before = the current version; after = the edited version. List the
  edited copy *after* the collection; a later folder with the same name replaces the earlier one.
- **Removing a skill:** before = with it; after = without it.
- **Plugins:** list plugin folders under `plugins = [...]`; they load with `--plugin-dir`.

Project skills usually live in `.claude/skills/`. Claude Code identifies a skill by its
**folder name**, not the `name:` in SKILL.md, so two folders declaring the same name are two
different skills.

## 3. Write the tasks (this is the part that matters)

Read each existing SKILL.md that the change could plausibly affect. Look for its
**exclusive rules**: things only that skill enforces (never push, write REVIEW.md, redact
secrets, no edits during review). Those are the rules that disappear when another skill
takes over, so each one should become a skilldiff rule.

For each affected skill, write one task:

- `prompt`: what a user would actually type. Do **not** name the skill.
- `fixture`: a small folder copied into a fresh git repo for each run. Keep it tiny.
- `uncommitted`: optional folder copied on top after the initial commit (for commit workflows).
- `expect_skill`: the folder name of the skill that should handle it.
- `rules`: one per exclusive rule. Pick the narrowest type that proves it:

| Rule type | Passes when |
|---|---|
| `files_unchanged` (path glob) | files matching the glob are byte-identical to the start |
| `file_exists` / `file_absent` (path glob) | a matching file exists / doesn't |
| `file_contains` / `file_not_contains` (path, pattern) | regex found / not found in matching files |
| `no_command` / `command_used` (pattern) | no Bash command / some Bash command matches the regex |
| `no_tool` / `tool_used` (tool) | the tool was never / at least once called |
| `skill_used` / `skill_not_used` (skill) | the skill was / wasn't opened |
| `reply_contains` / `reply_not_contains` (pattern) | regex in the final reply / not |
| `commit_message` (pattern) | at least one new commit, and every new commit matches |
| `no_new_commits` | the agent made no commits |
| `check` (run) | a shell command in the workspace exits 0 (`$SKILLDIFF_CONFIG_DIR` points at the config's folder) |

Add one task for a skill that should be *unaffected*. If it changes, the setup is noisy.
Shared suites can live in their own file and be pulled in with `include = ["tasks.toml"]`.

## 4. Validate, estimate, and ask before spending

```bash
skilldiff validate -c skilldiff.toml
skilldiff run -c skilldiff.toml --dry-run | head
```

Runs = tasks × 2 × repeats. On Sonnet a small task costs roughly $0.05–0.10 per run, and
on Haiku less than a cent. **Tell the user the run count and a rough cost, and get a yes
before running.** Use `repeats = 3` to explore and 5 or more before acting on a result.

## 5. Run and read the report

```bash
skilldiff run -c skilldiff.toml -o skilldiff-out
```

Exit code 1 means at least one workflow regressed. Read `skilldiff-out/report.md`; the
HTML report has per-run timelines. Explain it in this order:

1. The headline: which workflows broke and which rules stopped being followed.
2. For each regressed task, which skill ran instead (`no skill` means the agent skipped
   skills entirely) and the evidence (offending command, diff of a protected file, missing file).
3. The confidence label. With 3 repeats the strongest possible p-value is 0.05. Present
   `medium` or `low` results as signals worth re-running with more repeats, not as proof.
4. Cost difference per run.

## 6. Suggest fixes, then re-test

Typical fixes: narrow the candidate's `description` so it no longer claims the other
skill's job; give the existing skill a more specific description; rename a folder that
collides; merge two skills that do the same job. Re-run the same config to confirm the fix.
`skilldiff report <out> --min-drop 0.3` re-scores saved runs without new API calls.

## CI

The repository ships a GitHub Action that runs the experiment on pull requests that touch
skills and posts the report as a comment. See the README's "GitHub Action" section.
