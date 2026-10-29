# skilldiff

**Will this skill break my setup?** skilldiff runs real before/after experiments with Claude Code
to show whether adding, changing, or removing a skill makes the workflows your *other* skills
guard stop following their rules.

[![CI](https://github.com/MahdiBabaei96/skilldiff/actions/workflows/ci.yml/badge.svg)](https://github.com/MahdiBabaei96/skilldiff/actions/workflows/ci.yml)
![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)
![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)
![License: MIT](https://img.shields.io/badge/license-MIT-lightgrey)

```text
$ skilldiff run -c examples/01-description-trim/skilldiff.toml
skilldiff: 50 runs (5 tasks × 2 arms × 5 repeats), 10 at a time
  ...
⚠️ Changing `pr-review-checklist` was followed by rule failures in 1 of 5 workflows (3 observed rule drops).
```

| Workflow | Result | Expected skill ran first | Rules followed |
|---|---|---|---|
| `review-payments` | 🔴 rules broken | 5/5 → 0/5 (no skill 5×) | 20/20 → 5/20 |
| `security-config` | ⚪ no change | 5/5 → 5/5 | 25/25 → 25/25 |
| `commit-discount` | ⚪ no change | 5/5 → 5/5 | 25/25 → 25/25 |
| … | | | |

That PR only shortened one skill's description. Afterwards the agent still reviewed the code
and the answer looked fine, but it stopped opening the review skill, so `REVIEW.md`, the severity
labels, and the verdict line silently disappeared in all 5 runs.
[Full report](examples/01-description-trim/results/report.md).

## Why

Skills come from many places: your team, plugins, copied collections. When two skills can do
the same job, the model picks one by name and description, and the loser's rules vanish. An
October 2026 study of 312 confirmed similar-skill pairs found that a co-installed similar skill
took over roughly one run in five **without lowering task completion**, that runs which opened
the similar skill first lost more than a third of the functions only the intended skill
provides, and that the agent's final reply almost never says which skill it used
([Yan et al., *One Skill Too Many*, arXiv:2610.11647](https://arxiv.org/abs/2610.11647)).

So "the task passed" can hide lost instructions. Static overlap scanners can tell you two
descriptions look alike; they can't tell you whether your workflows actually change. skilldiff
measures that.

## What it does

1. You describe a few representative tasks and the rules each one must follow
   (e.g. "reviews never modify source", "never `git push`", "write findings to `REVIEW.md`").
2. skilldiff runs each task with your current skills (**before**) and with the proposed skills
   (**after**), several times each, every run in a fresh throwaway git workspace.
3. The report shows, per workflow:
   - **skill selection**: which skill opened first, before vs after (including *no skill*),
   - **broken rules**: pass rates before vs after, with raw and Holm-adjusted one-sided Fisher exact p-values,
   - **evidence**: the offending command, a diff of the file that should not have changed, the commit message,
   - **artifact differences**: which files the agent created or changed in each arm,
   - **cost**: mean API cost, turns, and time per run.
4. A GitHub Action posts that comparison on every pull request that touches your skills.

## Measured examples

Five reproducible experiments ship in [`examples/`](examples/). They share one five-skill
collection (review checklist, security audit, commit helper, test writer, docs writer) and
one task suite of five workflows with 22 rules. Every number below comes from the committed
runs: 5 repeats per arm, 250 runs in total, Claude Code 2.1.312, $9.02 of API usage.

| # | Change | Model | Result |
|---|---|---|---|
| 1 | [A PR trims `pr-review-checklist`'s description to "Team review checklist."](examples/01-description-trim/results/report.md) | Sonnet 5.5 | 🔴 Review workflow: the skill was never opened again (5/5 → 0/5) and 3 rules broke in every run (p = 0.004). |
| 2 | [Copying in a community skill that also declares `name: security-audit`](examples/02-same-name-copy/results/report.md) | Sonnet 5.5 | 🔴 Security workflow: the copy ran first in 3/5 runs. In exactly those 3 runs the "read-only" audit rewrote `config.py` and the findings went to the wrong file; the 2 runs that opened the original passed every rule (5/5 → 2/5, p = 0.083). |
| 3 | [Adding a broad `team-conventions` skill](examples/03-broad-conventions-haiku/results/report.md) | Haiku 5.5 | 🔴 Commit workflow: `commit-helper` still ran first in 5/5 runs, yet 3 commits came out as `SHOP-000 feat(...)`, breaking the Conventional Commit rule (5/5 → 2/5). 🟠 Docs workflow: a different skill ran in 3/5. |
| 4 | [Adding a generic `quick-review` skill](examples/04-review-skill-haiku/results/report.md) | Haiku 5.5 | ✅ No regression at the default threshold, but the review workflow got worse below it (expected skill 4/5 → 2/5). |
| 5 | [Control: adding an unrelated `sql-style` skill](examples/05-control-unrelated/results/report.md) | Sonnet 5.5 | ✅ No change in any workflow. The tool doesn't cry wolf on a non-overlapping skill. |

What these taught us:

- **Example 3 is the paper's failure mode in miniature.** Skill selection was perfect, the
  commit was made, CHANGELOG was updated, and a rule from a *different* skill still leaked in.
  Checking "did the right skill run?" isn't enough; you have to check the rules.
- **Small tweaks to existing skills are as risky as new skills** (example 1). That is why the
  GitHub Action compares a PR against its base rather than only checking new skills.
- **Claude Code identifies skills by folder name**, not the `name:` in SKILL.md (verified on
  2.1.312), so a "same-named" copy is a second skill competing for the same prompts (example 2).
  skilldiff warns about this before running.
- **The model matters.** Adding `quick-review` or `team-conventions` changed nothing in
  small exploratory runs (1–2 repeats) on Sonnet 5.5, while Haiku 5.5 was easily swayed. Test with the model your team uses.
- **Repeats matter.** An exploratory 2-repeat run of example 4 looked like a clean break
  (2/2 → 0/2). At 5 repeats it is 4/5 → 2/5, below the threshold. Use 3 repeats to explore and
  5 or more before acting on a result.

## Quick start

Requirements: Python 3.11+, [Claude Code](https://docs.claude.com/en/docs/claude-code/overview)
(`claude`) on your PATH and signed in, or `ANTHROPIC_API_KEY` set.

```bash
pipx install git+https://github.com/MahdiBabaei96/skilldiff
# or: pip install git+https://github.com/MahdiBabaei96/skilldiff

git clone https://github.com/MahdiBabaei96/skilldiff && cd skilldiff

# Look at a finished experiment without spending anything
skilldiff report examples/01-description-trim/results --format md

# One-command demo: re-run example 1 yourself (30 runs at 3 repeats, about $1.70 on Sonnet)
skilldiff run -c examples/01-description-trim/skilldiff.toml --repeats 3
open skilldiff-out/report.html   # or xdg-open
```

For your own collection:

```bash
skilldiff init                 # writes a commented skilldiff.toml
skilldiff validate             # lists skills per arm, warns about name clashes, counts runs
skilldiff run --dry-run        # prints the exact claude commands
skilldiff run                  # runs and writes skilldiff-out/report.{md,html,json}
```

`skilldiff run` exits with code **2** if any workflow has failed or missing runs (inconclusive),
**1** for a detected rule regression, and **0** for a complete run without configured findings.
`--fail-on substitution` also fails when skill selection changes or reliability drops.
`--fail-on never` explicitly opts out of both finding and inconclusive exit codes; the report
still says inconclusive. An incomplete experiment must not be treated as a clean pass.

## Find which skills reproduce a failure

```sh
skilldiff diagnose -c skilldiff.toml --task review-payments --rule review-file \
  --repeats 3 --max-runs 120 -o diagnosis-review
```

Reduces the after collection while keeping the expected skill installed, then
uses fresh control, candidate, and single-deletion runs to confirm a **1-minimal**
set. This is not a globally smallest set or proof of causality. Noisy outcomes,
errors, runtime changes and exhausted budgets are inconclusive. Confirmed cases
export an input snapshot and reproduction instructions.

[Usage and limits](docs/diagnose.md) · [Free deterministic demo](examples/diagnose/)

## Configuration

```toml
include = ["tasks.toml"]                   # optional: pull [[tasks]] from shared files

[before]
skills = [".claude/skills"]                # skill folders, or folders of skill folders

[after]
skills = [".claude/skills", "candidate/my-new-skill"]
# A later folder with the same name replaces an earlier one, which is how you test an edit:
# skills = [".claude/skills", "pr/pr-review-checklist"]
# plugins = ["path/to/plugin"]            # loaded with --plugin-dir

[run]
repeats = 3            # per arm per task
parallel = 4           # concurrent claude processes
model = "sonnet"       # alias or full model name
max_turns = 30
timeout_seconds = 900
max_budget_usd = 2.0   # per-run cap passed to claude
# isolate_user_config = true   # empty CLAUDE_CONFIG_DIR per run (needs ANTHROPIC_API_KEY)
# agent_cmd = "claude"         # env vars are expanded

[thresholds]
min_drop = 0.5            # a rule is "broken" when its pass rate drops by this much
selection_min_drop = 0.5  # "different skill ran" threshold for expect_skill

[[tasks]]
id = "commit-discount"
prompt = "I'm done with the discount feature, please commit it."   # never name the skill
fixture = "fixtures/shop"            # copied into a fresh git repo for every run
uncommitted = "fixtures/shop-discount"   # copied on top after the initial commit
expect_skill = "commit-helper"       # folder name of the skill that should handle this
rules = [
  { id = "conventional", type = "commit_message", pattern = '^(feat|fix|docs|refactor|test|chore)(\([\w.-]+\))?: [a-z]' },
  { id = "no-push", type = "no_command", pattern = 'git\s+push', description = "commit-helper forbids pushing" },
  { id = "code-as-is", type = "files_unchanged", path = "shop/**" },
]
```

### Rule types

| Type | Parameters | Passes when |
|---|---|---|
| `files_unchanged` | `path` (glob) | matching files are byte-identical to the start of the run (created or deleted files count as changes) |
| `file_exists` / `file_absent` | `path` | a matching file exists / none does |
| `file_contains` / `file_not_contains` | `path`, `pattern` | the regex matches in a matching file / in none |
| `no_command` / `command_used` | `pattern` | no Bash command matches / at least one does |
| `no_tool` / `tool_used` | `tool` | the tool was never called / was called |
| `skill_used` / `skill_not_used` | `skill` | the skill was opened / wasn't |
| `reply_contains` / `reply_not_contains` | `pattern` | the regex matches the final reply / doesn't |
| `commit_message` | `pattern` | at least one new commit was made and every new commit matches |
| `no_new_commits` | | no commits were made |
| `check` | `run`, `timeout_seconds` | a shell command run in the workspace exits 0 (`$SKILLDIFF_CONFIG_DIR` is the folder of the file that defined the task) |

Regex rules accept `ignore_case = true`. Patterns use Python `re` syntax; TOML single-quoted
strings avoid double escaping.

**Writing good tasks.** For each skill a change could affect, find its *exclusive* rules:
things only that skill enforces. Those are the ones that disappear when another skill takes
over. Phrase the prompt the way a user would, and keep fixtures tiny so runs are cheap. Include
one task the change should *not* affect, as a noise check.

## How it works

```text
for repeat in 1..N:                      # arms interleaved, so API drift hits both equally
  for task in tasks:
    for arm in (before, after):
      ws = fresh temp dir                # outside your repo: no parent CLAUDE.md can leak in
        ├─ fixture files, git init + commit, optional uncommitted change
        └─ .claude/skills/  ← exactly this arm's skills
      claude -p "<prompt>" --output-format stream-json --setting-sources project \
             --no-session-persistence --permission-mode bypassPermissions ...
      record: skills opened (Skill tool or a SKILL.md read), Bash commands, tools,
              final reply, cost/tokens/turns, file snapshot, new commits
      score every rule
compare arms → report.md (PR comment) · report.html (timelines) · report.json
```

- `--setting-sources project` keeps your personal `~/.claude` skills and settings out of
  both arms. Claude Code's built-in skills are present in both; their interactions with added skills may still differ.
- The first skill opened is what the study found decides the outcome, so it is reported separately
  from "any skill used".
- Saved transcripts drop partial-message chunks and some identifiers to reduce size. This is
  **not redaction**: prompts, tool inputs/outputs, source files, local paths, and secrets can
  remain in reports, transcripts, and file snapshots. Review all outputs before sharing.
- `skilldiff report <out> --min-drop 0.3` re-scores saved runs at a new threshold with no new API calls.

**Execution boundary:** temporary directories separate experiment files; they are **not a
security sandbox**. The default `bypassPermissions` mode disables Claude permission prompts,
and subprocesses inherit your environment. Agents can access files, credentials, and network
resources available to your account outside the temp directory. Only run trusted skills
locally; use a disposable container or runner with restricted credentials and network access
for untrusted skills. Configuration isolation is not OS-level confinement.

## GitHub Action

Add `skilldiff.toml` (tasks and run settings) to the repository that holds your skills, then
copy [`docs/github-action.yml`](docs/github-action.yml) to `.github/workflows/skilldiff.yml`:

```yaml
on:
  pull_request:
    paths: [".claude/skills/**", "skilldiff.toml"]

permissions:
  contents: read
  pull-requests: write

jobs:
  skilldiff:
    runs-on: ubuntu-latest
    if: github.event.pull_request.head.repo.full_name == github.repository
    steps:
      - uses: actions/checkout@v4
      - uses: MahdiBabaei96/skilldiff@v0.1.0
        with:
          skills-path: .claude/skills          # before = PR base, after = PR head
          anthropic-api-key: ${{ secrets.ANTHROPIC_API_KEY }}
          repeats: "3"
```

The action checks out the base commit's skills next to the PR's, runs the experiment, posts
(and on later pushes, updates) one sticky comment with the Markdown report, uploads the reports,
and fails the check on regression or incomplete experiments. Raw transcripts
and file snapshots are **not uploaded by default**; `upload-raw: "true"` opts in. Reports and PR
comments can also contain sensitive evidence; disable `comment` for private experiments and
review artifacts before sharing. Never run untrusted PR code with privileged credentials.

| Input | Default | |
|---|---|---|
| `config` | `skilldiff.toml` | experiment file |
| `skills-path` | | skills folder to compare base vs head; leave empty to use the config's arms |
| `anthropic-api-key` | required | |
| `repeats`, `model` | from config | overrides |
| `fail-on` | `regression` | `regression`, `substitution`, or `never` |
| `comment` | `true` | post the sticky PR comment (may include sensitive evidence) |
| `upload-raw` | `false` | upload unredacted transcripts and file snapshots |
| `claude-code-version` | `latest` | npm version to install |

Outputs: `regression` and `inconclusive` (`true`/`false`), `headline`, `report-dir`.

## Use it from Claude

This repository is also a Claude Code plugin with a `skilldiff` skill that helps you pick the
right tasks and rules from your existing SKILL.md files, estimates the cost and asks before
running, and explains the report.

```text
/plugin marketplace add MahdiBabaei96/skilldiff
/plugin install skilldiff@skilldiff
```

Then ask something like *"Will adding this review skill break any of my existing skills?"*

## How this differs from existing tools

- **Static auditors** such as [skill-audit](https://github.com/scottholdren/skill-audit),
  [skill-doctor](https://github.com/ssamba1/skill-doctor), and the
  [skill-conflict-poc](https://github.com/yiweiren123-arch/skill-conflict-poc) flag overlapping
  descriptions. That's fast and free, and a good first pass. skilldiff runs the agent and
  measures what actually changes, including cases where descriptions don't look alike (example 1)
  or the right skill still runs (example 3).
- **Evaluation frameworks** such as [Agent Skill Evals](https://github.com/akshay5995/agent-skill-evals)
  and `claude plugin eval` score a skill or plugin against its *own* cases, with or without it
  installed. skilldiff scores the *rest of your collection*: the workflows you already rely on.
- **Linters and scanners** ([SkillMD](https://github.com/skillmds/skillmd),
  [Snyk Agent Scan](https://github.com/snyk/agent-scan)) check a skill's content and security.
  Use them too; they answer a different question.

## Limitations

- **It costs money and time.** Runs = tasks × 2 × repeats. Small tasks cost about $0.06 per
  run on Sonnet 5.5 and under a cent on Haiku 5.5. A 5-task, 3-repeat experiment takes a few minutes with `parallel = 10`.
- **Exploratory statistics.** Reports show sample counts, observed drops in percentage points,
  raw one-sided Fisher exact p-values, and Holm-adjusted p-values across all comparable rule
  and expected-skill selection tests, including tests without a drop. With 3 repeats per arm,
  the smallest raw p-value is 0.05; adjustment often makes it larger. Threshold-based regression
  flags describe observed drops, not statistical certainty or a probability the change caused
  them. Rules may overlap (one missing file can fail several checks), and runs can share model
  or service effects. More repeats and independent reproduction are needed for stronger evidence.
- **Incomplete runs.** Any errored or missing run makes the experiment inconclusive. Pass rates
  describe only completed runs and may be biased when failures differ between arms.
- **Your tasks bound what it can see.** A regression in a workflow you didn't describe won't
  show up.
- **Claude Code only** for now. The stream-json parser is tested against a real 2.1.312
  transcript ([`tests/data`](tests/data/)); if a future version changes the event format, the
  tests will say so.

## Development

```bash
pip install -e ".[dev]"
pytest -q
```

The test suite never calls a model: [`tests/fake_claude.py`](tests/fake_claude.py) emits the
same event stream as Claude Code from a small JSON plan, so workspaces, rules, statistics,
reports, exit codes, and the GitHub Action are all tested deterministically. See
[CONTRIBUTING.md](CONTRIBUTING.md). The most useful contribution is a real conflict from
your own collection.

## License

MIT
