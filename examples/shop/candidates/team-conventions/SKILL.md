---
name: team-conventions
description: Our engineering conventions for code review, security checks, commits, tests, and docs. Use for any review, audit, commit, testing, or documentation task in this repository.
---

# Team conventions

- **Reviews and audits:** post findings in chat, grouped by file. Fix obvious issues directly.
- **Commits:** prefix the message with the ticket id, e.g. `SHOP-123 Add discount`. Use `SHOP-000` if unknown.
- **Tests:** use pytest with plain `assert` statements in `tests/`.
- **Docs:** keep docs in `docs/<module>.md`, not in the README.
