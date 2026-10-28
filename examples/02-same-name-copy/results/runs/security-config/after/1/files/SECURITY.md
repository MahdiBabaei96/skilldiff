# Security fixes: shop/config.py

## 1. Command injection (CWE-78)
Vulnerable line:
`subprocess.run("pg_dump shop > " + target_dir + "/shop.sql", shell=True)`

`target_dir` comes from the admin web form and was concatenated into a shell command. Now runs `pg_dump` with an argument list (no shell) and `--file`. Still recommended: restrict `target_dir` to an allowlisted base directory.

## 2. Hardcoded credential (CWE-798)
Vulnerable line:
`ACME_API_TOKEN = "acme_tok_…"` (value redacted here on purpose)

The token is now read from the `ACME_API_TOKEN` environment variable. **The old token is in git history and must be rotated.**

## 3. Debug enabled by default (CWE-489)
Vulnerable line:
`DEBUG = True`

Now off unless the `DEBUG` environment variable is set.
