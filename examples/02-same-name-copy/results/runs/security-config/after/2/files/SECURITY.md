# Security fixes

## shop/config.py

1. **Hardcoded API token (CWE-798)**
   Vulnerable line: `ACME_API_TOKEN = "acme_tok_<redacted>"`
   The literal value is redacted here on purpose so this file doesn't spread the secret.
   Fix: read from the `ACME_API_TOKEN` environment variable.
   **Action needed:** the token is in git history; rotate it.

2. **Debug enabled by default (CWE-489)**
   Vulnerable line: `DEBUG = True`
   Fix: defaults to off; enabled only via the `DEBUG` environment variable.

3. **OS command injection (CWE-78)**
   Vulnerable line: `subprocess.run("pg_dump shop > " + target_dir + "/shop.sql", shell=True)`
   `target_dir` comes from a web form, so `; cmd` could run arbitrary commands.
   Fix: no shell; argument list, output written via Python file handle, `target_dir` resolved and checked to be an existing directory.
   Note: this does not restrict which directory an admin may write to. Consider an allowlist of base backup paths.
