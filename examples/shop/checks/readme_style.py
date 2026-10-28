"""Checks for the docs-writer rules. Run inside the workspace: readme_style.py fences|width"""
import re
import sys

text = open("README.md", encoding="utf-8").read()
mode = sys.argv[1]

if mode == "fences":
    # opening fences alternate with closing fences; every opening fence must say python
    fences = re.findall(r"^```(.*)$", text, re.M)
    openings = fences[0::2]
    if not openings:
        sys.exit("no code examples found")
    bad = [f for f in openings if f.strip() != "python"]
    sys.exit(f"code fences not tagged python: {bad}" if bad else 0)

if mode == "width":
    long = [i + 1 for i, line in enumerate(text.splitlines()) if len(line) >= 100]
    sys.exit(f"lines >= 100 chars: {long}" if long else 0)

sys.exit(f"unknown mode {mode}")
