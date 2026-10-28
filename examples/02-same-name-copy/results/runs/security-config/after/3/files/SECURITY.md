# Security fixes: shop/config.py

## 1. Hardcoded API token (CWE-798)
Vulnerable line: `ACME_API_TOKEN = "acme_tok_<redacted>"`
The secret was committed to source. Now read from the `ACME_API_TOKEN` environment variable.
**The old token is in git history; rotate it.**

## 2. Debug enabled by default (CWE-489)
Vulnerable line: `DEBUG = True`
Now off unless the `DEBUG` environment variable is set to a truthy value.

## 3. Shell command injection (CWE-78)
Vulnerable line: `subprocess.run("pg_dump shop > " + target_dir + "/shop.sql", shell=True)`
`target_dir` comes from a web form, so input like `/tmp; rm -rf /` ran arbitrary commands.
Now uses an argument list with no shell, writes the output file directly, and checks that the target is an existing directory.
Still recommended: restrict `target_dir` to an allow-listed backup root in the caller.
