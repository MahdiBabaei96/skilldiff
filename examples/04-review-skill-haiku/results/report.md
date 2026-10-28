<!-- skilldiff-report -->
## skilldiff: will this skill break my setup?

**✅ Adding `quick-review` showed no detected regressions across 5 workflows. 1 got worse by less than the threshold; re-run with more repeats to be sure.**

> Privacy: reports, transcripts, and file artifacts are not redacted. Review before sharing.

| Workflow | Result | Expected skill ran first | Rules followed | Cost / run |
|---|---|---|---|---|
| `review-payments` | ⚪ no change · ↘ below threshold | 4/5 → 2/5 (no skill 3×) | 17/20 → 11/20 | +$0.000 |
| `security-config` | ⚪ no change | 0/5 → 0/5 (no skill 5×) | 10/25 → 10/25 | +$0.000 |
| `commit-discount` | ⚪ no change | 5/5 → 5/5 | 25/25 → 25/25 | −$0.000 |
| `tests-payments` | ⚪ no change | 5/5 → 5/5 | 20/20 → 20/20 | −$0.001 |
| `docs-payments` | ⚪ no change | 5/5 → 5/5 | 20/20 → 20/20 | −$0.001 |

<details><summary><b>⚪ review-payments</b>: no change, but something got worse by less than the threshold</summary>

> Can you review shop/payments.py before I merge it?

**First skill opened** (expected `pr-review-checklist`): before `pr-review-checklist` 4×, no skill 1× · after no skill 3×, `pr-review-checklist` 2× · drop 40 pp (raw p=0.262, Holm p=1.000)

| Rule | Before | After | Change |
|---|---|---|---|
| `read-only` – reviews never modify source | 5/5 | 5/5 |  |
| `review-file` – findings go in REVIEW.md | 4/5 | 2/5 | ↘ lower, below threshold |
| `severity-labels` – each finding starts with [blocker]/[major]/[nit] | 4/5 | 2/5 | ↘ lower, below threshold |
| `verdict-line` – ends with a Verdict line | 4/5 | 2/5 | ↘ lower, below threshold |


**Files changed by the agent** (runs that changed each file, before → after): `REVIEW.md` 4→2

</details>

**Cost of this experiment:** $0.23 (before $0.12, after $0.11). Cost / run columns compare mean API cost per run.

<sub>5 repeats per arm, runs interleaved · model `claude-haiku-5-5` · Claude Code 2.1.312 · skilldiff 0.1.0 · rule broken = pass rate dropped by ≥50 points; p = one-sided Fisher exact test; Holm adjustment across 27 comparisons. Threshold flags describe observed drops, not statistical certainty; small samples need more repeats.</sub>
