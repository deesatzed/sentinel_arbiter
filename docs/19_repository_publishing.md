# 19 - Repository Publishing

Date: 2026-06-11

## Repository

Canonical GitHub target:

```text
https://github.com/deesatzed/sentinel_arbiter.git
```

The local project is a standalone git repository rooted at `sentinel_codex_handoff`.

## Branch Policy

- Primary branch: `main`
- Remote name: `origin`
- Push target: `origin/main`

## Publish Boundary

This repository contains the deterministic local Sentinel ED disposition replay POC and its synthetic artifacts only. It does not contain production credentials, real patient data, named clinical-site data, or a production deployment configuration.

## Pre-Push Verification

Run the local deterministic verification commands from `README.md` before pushing substantive changes.

Minimum final checks:

```bash
python3 -m pytest -q
PYTHONPATH=src python3 -m sentinel_workbench.validate data/cases
PYTHONPATH=src python3 -m sentinel_workbench.static_inputs --static-inputs data/static_inputs/static_inputs.json --case-dir data/cases
PYTHONPATH=src python3 -m sentinel_workbench.receipts --case-dir data/cases --static-inputs data/static_inputs/static_inputs.json --out data/receipts
PYTHONPATH=src python3 -m sentinel_workbench.evaluate --case-dir data/cases --out validation/reports/latest.json --receipt-dir data/receipts
PYTHONPATH=src python3 -m sentinel_workbench.workbench --case-dir data/cases --receipt-dir data/receipts --report validation/reports/latest.json --out data/workbench/index.html
PYTHONPATH=src python3 -m sentinel_workbench.schema_export schemas/ed_decision_episode.schema.json
python3 -m pip install -e . --dry-run --no-deps
git diff --check
```
