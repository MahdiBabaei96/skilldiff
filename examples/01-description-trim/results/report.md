<!-- skilldiff-report -->
## skilldiff: will this skill break my setup?

**⚠️ Changing `pr-review-checklist` was followed by rule failures in 1 of 5 workflows (3 observed rule drops).**

> Privacy: reports, transcripts, and file artifacts are not redacted. Review before sharing.

| Workflow | Result | Expected skill ran first | Rules followed | Cost / run |
|---|---|---|---|---|
| `review-payments` | 🔴 rules broken | 5/5 → 0/5 (no skill 5×) | 20/20 → 5/20 | −$0.010 |
| `security-config` | ⚪ no change | 5/5 → 5/5 | 25/25 → 25/25 | +$0.001 |
| `commit-discount` | ⚪ no change | 5/5 → 5/5 | 25/25 → 25/25 | −$0.000 |
| `tests-payments` | ⚪ no change | 5/5 → 5/5 | 20/20 → 20/20 | −$0.004 |
| `docs-payments` | ⚪ no change | 5/5 → 5/5 | 20/20 → 20/20 | +$0.000 |

<details open><summary><b>🔴 review-payments</b>: rules broken</summary>

> Can you review shop/payments.py before I merge it?

**First skill opened** (expected `pr-review-checklist`): before `pr-review-checklist` 5× · after no skill 5× · drop 100 pp (raw p=0.004, Holm p=0.107)

| Rule | Before | After | Change |
|---|---|---|---|
| `read-only` – reviews never modify source | 5/5 | 5/5 |  |
| `review-file` – findings go in REVIEW.md | 5/5 | 0/5 | 🔴 observed drop 100 pp (raw p=0.004, Holm p=0.107) |
| `severity-labels` – each finding starts with [blocker]/[major]/[nit] | 5/5 | 0/5 | 🔴 observed drop 100 pp (raw p=0.004, Holm p=0.107) |
| `verdict-line` – ends with a Verdict line | 5/5 | 0/5 | 🔴 observed drop 100 pp (raw p=0.004, Holm p=0.107) |

<sub>Evidence for `review-file`: after-run #0, same in 5 runs · first skill no skill · `runs/review-payments/after/0`</sub>

```text
REVIEW.md not found; files created instead: none
```
<sub>Evidence for `severity-labels`: after-run #0, same in 5 runs · first skill no skill · `runs/review-payments/after/0`</sub>

```text
REVIEW.md does not exist
```
<sub>Evidence for `verdict-line`: after-run #0, same in 5 runs · first skill no skill · `runs/review-payments/after/0`</sub>

```text
REVIEW.md does not exist
```

**Files changed by the agent** (runs that changed each file, before → after): `REVIEW.md` 5→0

</details>

**Cost of this experiment:** $2.85 (before $1.46, after $1.39). Cost / run columns compare mean API cost per run.

<sub>5 repeats per arm, runs interleaved · model `claude-sonnet-5-5` · Claude Code 2.1.312 · skilldiff 0.1.0 · rule broken = pass rate dropped by ≥50 points; p = one-sided Fisher exact test; Holm adjustment across 27 comparisons. Threshold flags describe observed drops, not statistical certainty; small samples need more repeats.</sub>
