---
name: security-audit
description: Use when the user asks for a security review or audit, or to check code for vulnerabilities, injection, or leaked secrets. Records findings in SECURITY_FINDINGS.md with CWE ids.
---

# Security audit

1. **Audits are read-only. Do not change any code.**
2. Write every finding to `SECURITY_FINDINGS.md` at the repository root, one per line:
   `- CWE-<id> <title> | <file>:<line> | severity: low|medium|high|critical`
3. **Never reproduce a secret value** in the findings file or in chat. Refer to it by its
   variable name and write `[REDACTED]` in place of the value.
4. In chat, give the count of findings by severity and point to `SECURITY_FINDINGS.md`.
