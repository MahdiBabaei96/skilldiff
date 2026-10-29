# Diagnose an interaction — deterministic demo

This example uses the **fake agent**, not an LLM. It demonstrates the reduction,
confirmation, budgeting and export workflow. It is not evidence that a real model
will behave this way, and requires no API key or model calls.

From the repository root, after installing the development version of skilldiff:

```sh
export SKILLDIFF_REPO="$PWD"
export FAKE_CLAUDE_PLAN="$PWD/examples/diagnose/plan.json"
skilldiff diagnose -c examples/diagnose/skilldiff.toml \
  --task review --rule read-only -o diagnosis-demo --max-runs 120
```

The plan deliberately edits `app.py` only when **formatter and policy** are both
installed. The five-skill collection reduces to `formatter`, `policy`, and pinned
`review`. Removing either formatter or policy makes the selected rule pass in
fresh confirmation runs. The two unrelated skills disappear.

The [committed sample report](sample-report.md) records 39 fake-agent launches:
controls, search probes, and fresh confirmation. Those are not paid model runs.

Read `diagnosis-demo/diagnosis.md` and inspect `diagnosis-demo/probes/` for the
underlying transcripts and file evidence. `diagnosis-demo/reproducer/` snapshots
the selected inputs, includes a SHA-256 manifest, and documents how to repeat the
check. The fake-agent command and environment still depend on this checkout;
the export is not a standalone environment.

Use a new output directory for each run. `--max-runs` includes initial controls,
search and confirmation; an exhausted budget cannot produce a minimality claim.
