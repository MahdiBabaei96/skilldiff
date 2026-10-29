# Localize a skill interaction with `skilldiff diagnose`

`run` detects changes across a collection. `diagnose` asks which **subset of the
after collection** still reproduces one selected rule failure. It keeps the
configured before collection as the control and pins the task's expected skill,
so deleting that skill cannot create a misleading reduction.

```sh
skilldiff diagnose -c skilldiff.toml --task review-payments --rule review-file \
  --repeats 3 --max-runs 120 -o diagnosis-review
```

## What a confirmed result means

1. The before control passes the selected rule in every initial repeat.
2. The full after collection fails the selected rule in every initial repeat.
3. Delta debugging removes chunks of unpinned skills while preserving failure.
4. Fresh runs confirm that the before control still passes and the reduced
   candidate still fails; cached search results do not count as confirmation.
5. Fresh single-deletion tests confirm that removing any one unpinned skill from
   the candidate makes the selected rule pass.

This is **1-minimal relative to pinned skills under the tested conditions**. It
does not establish a globally smallest collection or prove a causal mechanism.
Non-monotonic interactions may admit several different minimal sets, and a
pairwise-minimal set can coexist with a smaller failure elsewhere in the search
space. If only pinned skills remain, the report explicitly says they alone
reproduce the failure; it does not claim a multi-skill interaction.

The algorithm is established delta debugging. This feature applies it to
empirical skill-rule failures; it is not a claim to invent delta debugging,
conflict detection, or skill compression. Related work includes
[SkillReducer](https://arxiv.org/abs/2603.29919),
[skill-conflict-poc](https://github.com/yiweiren123-arch/skill-conflict-poc), and
[SkillClash](https://github.com/prazmara/skillclash). No exhaustive novelty claim
is made.

## Repeats, uncertainty and budget

The defaults are conservative empirical criteria: failure rate **0** means pass,
**1** means fail. Any mixture, errored run, missing score, or observed model/agent
version change stops with an inconclusive report. At least two repeats are
required. Use `--pass-rate` and `--failure-rate` only when you intentionally want
different empirical thresholds, for example `--pass-rate 0.2 --failure-rate 0.8`.
They are not probabilities, statistical significance tests, or confidence levels.

Adaptive search can overfit noisy outcomes; fresh confirmation helps but does not
eliminate that risk. Increasing repeats and independent reproduction remain
important. No amount of small-sample repetition proves a skill always fails.

`--max-runs` is a hard cap on agent subprocess launches, including fresh
confirmations, not a dollar limit. Each subprocess may use the per-run
`max_budget_usd` setting from the configuration. If there is not enough budget
to complete a whole probe, it is not started. The partial report makes no
minimality claim. Existing output directories are never overwritten.

## Inputs and limits

- Select exactly one task and built-in rule with `--task` and `--rule`.
- The task's `expect_skill` is always pinned. Add `--keep-skill NAME` to preserve
  dependencies or other context. Minimality excludes all pins.
- Both arms must use explicit skill folders. Plugin bundles are rejected in v1:
  their hooks, tools and other components cannot be isolated by removing a folder.
- Shell `check` rules are rejected in v1 because their external dependencies
  cannot be reliably exported. Unselected rules, including shell checks, do not run.
- The configured runtime, environment and fixture context remain fixed inputs;
  this does not identify arbitrary hook, model, MCP, or environment interactions.
- Skill directories and fixtures are snapshotted before probing, and their hashes
  are recorded. Later edits to the source collection do not change the search.
  External resources referenced by skills or the agent command are not frozen.

## Outputs and exit codes

- `diagnosis.md`: probe table, pinned and retained skills, status and limitations.
- `diagnosis.json`: counts, thresholds, per-probe runtime versions and outcomes.
- `inputs/`: frozen skill and fixture inputs (unredacted), with hashes in the JSON.
- `probes/<id>/runs/...`: ordinary skilldiff transcripts and file-change evidence.
- `reproducer/`: on confirmation only, snapshots before/reduced-after skills and
  fixtures, a runnable config, a SHA-256 manifest, and exact confirmation command.
  The configured agent, credentials and external environment are still required.

Exit **0** means confirmed 1-minimal or explicitly not reproduced; read the status
to distinguish them. Exit **2** means invalid input, baseline failure, exhausted
budget, ambiguous evidence, or interruption. A failed baseline is not evidence
that any added skill caused a regression.

Temporary workspaces are not a security sandbox. Agents inherit the environment
and the default configuration disables permission prompts. Reports, transcripts,
skills and exported fixtures are not redacted; review them before sharing. For
untrusted inputs use a disposable environment with restricted credentials.

See [the deterministic demo](../examples/diagnose/) to try the workflow without
making paid model calls.
