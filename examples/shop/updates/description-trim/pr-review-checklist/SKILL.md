---
name: pr-review-checklist
description: Team review checklist.
---

# PR review checklist

Reviews on this team are written down and read-only. Follow every rule.

1. **Never modify source files during a review.** The author fixes issues, not the reviewer.
2. Write findings to `REVIEW.md` at the repository root. Each finding is one bullet that starts
   with a severity label, `[blocker]`, `[major]` or `[nit]`, followed by `file:line` and the issue.
3. End `REVIEW.md` with exactly one line: `Verdict: APPROVE` or `Verdict: REQUEST CHANGES`.
4. In chat, reply with one or two sentences that point to `REVIEW.md`.

What to check: correctness, error handling, money handling (use `Decimal`, never `float`),
input validation, and missing tests.
