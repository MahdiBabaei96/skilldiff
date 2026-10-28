---
name: commit-helper
description: Use when the user asks to commit, save, or check in their changes. Writes a Conventional Commit and records the change in CHANGELOG.md.
---

# Commit helper

1. Add one bullet under `## [Unreleased]` in `CHANGELOG.md` describing the change, and include
   `CHANGELOG.md` in the same commit.
2. Commit message: `<type>(<scope>): <summary>` where type is one of
   feat, fix, docs, refactor, test, chore. Summary starts lowercase, at most 72 characters.
3. Commit the user's change exactly as it is. Do not edit source files while committing.
4. **Never run `git push`. Never use `--no-verify`. Never amend existing commits.**
