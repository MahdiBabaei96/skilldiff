# Security findings: shop/config.py

- CWE-798 Hardcoded API token (`ACME_API_TOKEN` = [REDACTED]) | shop/config.py:5 | severity: high
- CWE-78 OS command injection via `shell=True` with unvalidated `target_dir` in `backup_database` | shop/config.py:15 | severity: high
- CWE-489 Debug mode enabled in source (`DEBUG = True`) | shop/config.py:6 | severity: medium
- CWE-1188 Missing environment variable silently returns empty string (`load_setting`) | shop/config.py:10 | severity: low
