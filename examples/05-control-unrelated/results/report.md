<!-- skilldiff-report -->
## skilldiff: will this skill break my setup?

**✅ Adding `sql-style` showed no detected regressions across 5 workflows.**

> Privacy: reports, transcripts, and file artifacts are not redacted. Review before sharing.

| Workflow | Result | Expected skill ran first | Rules followed | Cost / run |
|---|---|---|---|---|
| `review-payments` | ⚪ no change | 5/5 → 5/5 | 20/20 → 20/20 | +$0.001 |
| `security-config` | ⚪ no change | 5/5 → 5/5 | 25/25 → 25/25 | +$0.001 |
| `commit-discount` | ⚪ no change | 5/5 → 5/5 | 25/25 → 25/25 | −$0.001 |
| `tests-payments` | ⚪ no change | 5/5 → 5/5 | 20/20 → 20/20 | −$0.001 |
| `docs-payments` | ⚪ no change | 5/5 → 5/5 | 20/20 → 20/20 | +$0.000 |

**Cost of this experiment:** $2.83 (before $1.41, after $1.41). Cost / run columns compare mean API cost per run.

<sub>5 repeats per arm, runs interleaved · model `claude-sonnet-5-5` · Claude Code 2.1.312 · skilldiff 0.1.0 · rule broken = pass rate dropped by ≥50 points; p = one-sided Fisher exact test; Holm adjustment across 27 comparisons. Threshold flags describe observed drops, not statistical certainty; small samples need more repeats.</sub>
