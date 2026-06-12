# 18 - Deterministic POC Status

Date: 2026-06-11

This document separates the implemented local deterministic Sentinel POC from deferred work and from requirements that would be necessary before any real clinical, prospective, or production use.

The `GOAL.md` transparent-demo completion audit is saved in `docs/21_goal_completion_audit.md`.

## Implemented Deterministic POC

- Local Python project under `sentinel_codex_handoff` with installable package metadata in `pyproject.toml`.
- Synthetic ED disposition replay cases in `data/cases/`.
- Explicit T0 through T3 replay timepoints and hidden T4 validation labels.
- Future-fact blocking for current-time replay views.
- Static role outputs and static EvidenceFlow outputs in `data/static_inputs/static_inputs.json`.
- Schema validation for ED cases, static role outputs, static EvidenceFlow outputs, and receipts.
- Constructed/deidentified-style input preparation with deterministic redaction and residual-risk reporting.
- Reviewer approval artifacts for prepared constructed input.
- Approved constructed-input deterministic analysis with receipt JSON, receipt Markdown, and review HTML output.
- Local stdlib HTTP clinician-review console for sample-case selection, constructed text entry, file upload, redaction status review, structured clinical section review, methodology exploration, ensemble contribution review, approval, deterministic analysis, and output review.
- Deterministic graph metrics for information sufficiency, material gap strength, harm clock, information clock, recoverability, future correction opportunity, decision weight, AI provenance risk, commission risk, omission risk, therapy-response relevance, next-best-information ranking, preventability-opportunity score, and final posture.
- First-class commission, omission, and therapy-response lanes.
- Schema-backed node audits with dependencies, evidence, estimates, ranges, medians, distributions, confidence/method fields, and sensitivity notes.
- Normalized ensemble contributions with accepted/downgraded dispositions and rejected unsupported targets.
- Reconstructable JSON receipts and human-readable Markdown receipts in `data/receipts/`, including node audit and ensemble contribution methodology.
- Evaluation report in `validation/reports/latest.json`.
- Validation report proof payloads for redaction gating, node audit completeness, ensemble contribution completeness, receipt completeness, workbench completeness, local app completeness, fixture categories, future leakage, schema validity, and forbidden phrase checks.
- Static reviewer workbench at `data/workbench/index.html`, including node audit methodology and ensemble contribution panels.
- Constructed-demo review output at `data/prepared_inputs/constructed_demo_case/analysis/review.html`.
- Summary-first result page with deeper-dive navigation for methodology, node evidence, ensemble contributions, receipt artifacts, trace hashes, validation status, and optional comparison-only model output.
- OpenRouter model comparison harness and local app skip/configuration status messaging. OpenRouter output is comparison-only and does not control graph values or final posture.
- Safety scanners for forbidden disposition phrasing, named institution examples, credential-like strings, and basic PHI-like patterns.

The deterministic graph computes Sentinel posture categories only. It does not generate clinical orders, diagnoses, prescribing instructions, clearance language, or patient-specific medical advice.

## Deferred

- app-authoritative LLM prompt mode.
- OpenEvidence or live evidence retrieval.
- model-swap evaluation.
- prompt-ablation evaluation.
- dynamic role-agent execution.
- external adapter interfaces.
- prospective deployment.
- production signing.
- cryptographic trace chains.
- reviewer authentication or multi-user workflow.
- production web application hardening.
- calibration on larger synthetic or public-style case sets.
- automatic browser screenshot capture when Browser/Playwright is unavailable; deterministic rendered-HTML verification is used instead.

These items are intentionally deferred rather than partially implemented.

## Required Before Real Clinical, Prospective, Or Production Use

- Institutional governance review and explicit use-policy approval.
- Real privacy, security, audit, access-control, and retention design.
- Production signing and key-management design.
- Clinical safety validation with qualified reviewers.
- Regulatory compliance analysis.
- Prospective validation protocol with stop rules.
- Bias, subgroup, and failure-mode analysis.
- External evidence governance and source-quality review.
- Human factors testing with intended reviewer groups.
- Incident response, rollback, and monitoring procedures.
- Formal separation between governance review output and clinical care actions.

No current artifact satisfies these requirements. The current system remains a local deterministic governance-review POC using synthetic data only.

## Not Claimed

- No claim of clinical outcome improvement.
- No claim of real-world harm prevention.
- No claim of clinical safety validation.
- No claim of regulatory compliance.
- No claim of production readiness.
- No claim that the scoring constants are clinically calibrated.
- No claim that optional LLM prompt mode is implemented.

## Local Verification

The current deterministic verification commands are:

```bash
python3 -m pytest -q
PYTHONPATH=src python3 -m sentinel_workbench.validate data/cases
PYTHONPATH=src python3 -m sentinel_workbench.static_inputs --static-inputs data/static_inputs/static_inputs.json --case-dir data/cases
PYTHONPATH=src python3 -m sentinel_workbench.constructed_intake --input data/constructed_inputs/constructed_demo_case.txt --out data/prepared_inputs/constructed_demo_case --episode-id constructed_demo_case --title "Constructed demo case"
PYTHONPATH=src python3 -m sentinel_workbench.approval --prepared-dir data/prepared_inputs/constructed_demo_case --reviewer-id reviewer_demo --approval-note "Demo structured episode reviewed for local deterministic workflow."
PYTHONPATH=src python3 -m sentinel_workbench.approval --validate-approved data/prepared_inputs/constructed_demo_case
PYTHONPATH=src python3 -m sentinel_workbench.demo_run --prepared-dir data/prepared_inputs/constructed_demo_case --static-inputs data/static_inputs/static_inputs.json --out data/prepared_inputs/constructed_demo_case/analysis
PYTHONPATH=src python3 -m sentinel_workbench.receipts --case-dir data/cases --static-inputs data/static_inputs/static_inputs.json --out data/receipts
PYTHONPATH=src python3 -m sentinel_workbench.evaluate --case-dir data/cases --out validation/reports/latest.json --receipt-dir data/receipts
PYTHONPATH=src python3 -m sentinel_workbench.workbench --case-dir data/cases --receipt-dir data/receipts --report validation/reports/latest.json --out data/workbench/index.html
PYTHONPATH=src python3 -m sentinel_workbench.ux_verification
PYTHONPATH=src python3 -m sentinel_workbench.final_verification
PYTHONPATH=src python3 -m sentinel_workbench.goal_audit --out-json validation/reports/goal_completion_audit.json --out-markdown docs/21_goal_completion_audit.md
PYTHONPATH=src python3 -m sentinel_workbench.schema_export schemas/ed_decision_episode.schema.json
PYTHONPATH=src python3 -m sentinel_workbench.local_app --host 127.0.0.1 --port 8765
python3 -m pip install -e . --dry-run --no-deps
git diff --check
```
