# 21 - GOAL.md Completion Audit

Current audit replaces the older 16-item audit with a 25-item map to the current `GOAL.md` Full Demo Proof Of Done list.

Proof items: 25
Pass count: 25
All pass: True

Sentinel remains a local deterministic governance-review POC. This audit does not claim clinical safety, production readiness, regulatory compliance, or clinical outcome benefit.

## Full Demo Proof Of Done

| # | Requirement | Verdict | Evidence Surface | Evidence |
|---:|---|---|---|---|
| 1 | A user can open the local app and choose either review question A or B before input is processed. | PASS | `local_app_completeness` | Local app exposes both review questions and requires Pre-process workflow. |
| 2 | The selected review question is saved into the run manifest, receipts, and summary. | PASS | `receipt_completeness, summary_completeness` | Selected review question is present in receipts and summary framing. |
| 3 | A user can paste redacted text or upload a constructed/deidentified local file and click Pre-process. | PASS | `local_app_completeness` | Paste and upload paths are represented in the local app proof payload. |
| 4 | A user can run a local CLI command with constructed text input and receive a redaction report plus draft structured episode. | PASS | `redaction_gating` | Constructed input path emits a redaction report and prepared draft artifacts. |
| 5 | Residual PII/PHI risk is detected and blocks or quarantines unsafe input. | PASS | `redaction_gating` | Residual risk block and quarantine behavior are both checked. |
| 6 | A reviewer-approved structured episode can be saved and used for deterministic analysis. | PASS | `local_app_completeness` | Approved structured episode can be run through the deterministic analysis endpoint. |
| 7 | Synthetic and constructed demo inputs validate against schemas. | PASS | `schema_validity, redaction_gating` | Synthetic case library and constructed demo artifact path validate. |
| 8 | Hidden future facts cannot enter current-time node computation. | PASS | `future_leakage_failures` | Current validation report has zero future-leakage failures. |
| 9 | Every graph node has a NodeAudit or equivalent schema-backed audit object. | PASS | `node_audit_completeness` | Every graph node has a node audit. |
| 10 | Every node audit has dependencies, evidence refs, value, range, median, distribution kind, confidence, method, and sensitivity note. | PASS | `node_audit_completeness` | Node audits have required estimate, evidence, dependency, and sensitivity fields. |
| 11 | The app displays Node Audit Methodology after pre-processing and before processing. | PASS | `local_app_completeness` | Node Audit Methodology is visible before processing. |
| 12 | A reviewer can choose OK, Adjust, or Re-check selected nodes; adjustments require confirmation before replacing generated methodology. | PASS | `local_app_completeness` | OK, Adjust, and Re-check selected-node controls are present and traced. |
| 13 | Every ensemble contribution is accepted, rejected, or downgraded with a reason. | PASS | `ensemble_contribution_completeness` | Every ensemble contribution has a disposition and reason. |
| 14 | The app displays Ensemble Contributions before Process. | PASS | `local_app_completeness` | Ensemble Contributions are visible in the pre-process/review flow before Process. |
| 15 | The graph computes final Sentinel posture from normalized typed node values. | PASS | `expected_posture_agreement` | Graph posture is computed from deterministic typed fixture runs. |
| 16 | Final posture remains one of the Sentinel posture categories, not a disposition recommendation. | PASS | `forbidden_phrase_violations` | Forbidden disposition-language scan reports zero generated-artifact violations. |
| 17 | The primary result is a clinician-readable governance summary of no more than one or two short paragraphs. | PASS | `summary_completeness` | Primary clinician summary is concise and machine-checked. |
| 18 | The primary summary explains what the result means for the selected review question and why, including the main uncertainty drivers. | PASS | `summary_completeness` | Summary includes selected-question framing and governance boundary. |
| 19 | A Deeper Dive button exposes node audit tables, ensemble tables, receipts, trace hashes, validation status, structured episode, and raw JSON/Markdown artifacts. | PASS | `local_app_completeness` | Deeper Dive exposes trace hashes and raw JSON/Markdown receipt links. |
| 20 | JSON receipts include selected review question, redaction, intake, node audit, ensemble, trace, graph, and signature-placeholder fields. | PASS | `receipt_completeness` | JSON receipts include selected question and required audit fields. |
| 21 | Human-readable receipts explain what was known, what was missing, what would have changed the discussion, what facility-based monitoring or treatment might add, what non-inpatient alternatives might add, commission concerns, omission concerns, therapy-response concerns, and why the graph selected the posture. | PASS | `receipt_completeness` | Human-readable receipts include summary and deeper-dive sections. |
| 22 | The workbench renders the redacted input, structured episode, node methodology, distributions, range, median, ensemble disagreement, graph posture, clinician summary, deeper-dive artifacts, receipts, and validation status. | PASS | `workbench_completeness` | Workbench renders summary, methodology, receipts, validation status, and deeper-dive artifact index. |
| 23 | Automated validation reports cover schema validity, future leakage, redaction gating, expected posture agreement on fixtures, omission detection, commission warning detection, therapy-response integration, next-best-information usefulness, node-audit completeness, receipt completeness, workbench completeness, app-flow completeness, summary completeness, and forbidden phrase violations. | PASS | `validation/reports/latest.json` | Validation report covers schema, leakage, redaction, fixture agreement, detection categories, node audit, receipts, workbench, app flow, summary, and forbidden phrases. |
| 24 | The project documents what is implemented, what is deferred, and what would be required before any real clinical, prospective, production, or live-evidence use. | PASS | `docs/18_deterministic_poc_status.md` | Status document separates implemented, deferred, required-before-real-use, and not-claimed boundaries. |
| 25 | Full local verification commands pass and git diff --check is clean. | PASS | `validation/reports/final_verification.json` | Final verification report records passing local commands, JSON syntax checks, and git diff --check. |

## Verification Commands

```bash
python3 -m pytest -q
PYTHONPATH=src python3 -m sentinel_workbench.validate data/cases
PYTHONPATH=src python3 -m sentinel_workbench.static_inputs --static-inputs data/static_inputs/static_inputs.json --case-dir data/cases
PYTHONPATH=src python3 -m sentinel_workbench.evaluate --case-dir data/cases --out validation/reports/latest.json --receipt-dir data/receipts
PYTHONPATH=src python3 -m sentinel_workbench.final_verification
PYTHONPATH=src python3 -m sentinel_workbench.goal_audit --out-json validation/reports/goal_completion_audit.json --out-markdown docs/21_goal_completion_audit.md
git diff --check
```
