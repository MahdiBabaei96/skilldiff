> Synthetic fake-agent demonstration, not an LLM benchmark. No model calls or API charges.

# skilldiff diagnosis

**confirmed-1-minimal** — Failure reproduced; every single unpinned deletion passed fresh confirmation.

Task: `review` · rule: `read-only` · agent runs: 39/120

Pinned: `review`
Candidate: `formatter`, `policy`, `review`

| Probe | Phase | Skills | Failures / repeats | Result |
|---|---|---|---|---|
| 0 | baseline | review | 0/3 | pass |
| 1 | full-after | formatter, noise-docs, noise-sql, policy, review | 3/3 | fail |
| 2 | search | noise-sql, policy, review | 0/3 | pass |
| 3 | search | formatter, noise-docs, review | 0/3 | pass |
| 4 | search | noise-docs, noise-sql, policy, review | 0/3 | pass |
| 5 | search | formatter, noise-sql, policy, review | 3/3 | fail |
| 6 | search | formatter, policy, review | 3/3 | fail |
| 7 | search | policy, review | 0/3 | pass |
| 8 | search | formatter, review | 0/3 | pass |
| 9 | baseline-confirmation | review | 0/3 | pass |
| 10 | candidate-confirmation | formatter, policy, review | 3/3 | fail |
| 11 | deletion-confirmation | policy, review | 0/3 | pass |
| 12 | deletion-confirmation | formatter, review | 0/3 | pass |

A confirmed result is **1-minimal relative to pinned skills**, not a globally smallest set or proof of causality. Every single unpinned deletion was freshly tested. Thresholds are empirical failure-frequency criteria, not confidence levels. Further trials or runtime changes can disagree.

Temporary workspaces are not a security sandbox. Outputs and exported inputs are not redacted.
