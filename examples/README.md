# Examples

Five experiments on one small "shop" project. Everything in `shop/` is shared:

| Path | What it is |
|---|---|
| `shop/skills/` | The installed collection: `pr-review-checklist`, `security-audit`, `commit-helper`, `test-writer`, `docs-writer`. Each enforces house rules only it knows about. |
| `shop/candidates/` | Skills someone might add: `quick-review`, `team-conventions`, `security-audit-oss` (a copied community skill that reuses the name `security-audit`), and the unrelated `sql-style` control. |
| `shop/updates/description-trim/` | An edited `pr-review-checklist` whose description was shortened in a "cleanup" PR. |
| `shop/fixtures/` | The tiny Python repo each run starts from, plus an uncommitted change for the commit task. |
| `shop/tasks.toml` | Five workflows and 22 rules shared by all experiments. |
| `shop/checks/` | Helper script used by two `check` rules. |

Each numbered folder holds a `skilldiff.toml` and the committed `results/` of a real run
(5 repeats per arm, Claude Code 2.1.312): `report.md`, `report.html`, `report.json`, and every
run's sanitized transcript, rule results, and changed files under `results/runs/`.

| Experiment | Headline |
|---|---|
| `01-description-trim` | ⚠️ Changing `pr-review-checklist` caused 1 of 5 workflows to stop following its rules (3 rules broken). |
| `02-same-name-copy` | ⚠️ Adding `security-audit-oss` caused 1 of 5 workflows to stop following its rules (3 rules broken). |
| `03-broad-conventions-haiku` | ⚠️ Adding `team-conventions` caused 1 of 5 workflows to stop following its rules (1 rule broken). |
| `04-review-skill-haiku` | ✅ No regressions at the default threshold; 1 workflow got worse below it. |
| `05-control-unrelated` | ✅ Adding `sql-style` caused no detected regressions across 5 workflows. |

Reproduce any of them (from the repository root):

```bash
skilldiff run -c examples/02-same-name-copy/skilldiff.toml -o my-run
```

Model output varies run to run, so your counts will differ somewhat. That variation is the
reason skilldiff repeats every task and reports confidence.
