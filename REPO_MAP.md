# REPO_MAP.md

## Project Type

Local deterministic Sentinel Governance Workbench POC. The first build wedge is synthetic Emergency Department disposition replay for governance review, now extended with constructed-input preparation, reviewer approval artifacts, deterministic node-audit methodology, ensemble contribution normalization, transparent receipt/workbench methodology rendering, and a local stdlib demo app.

## Tech Stack

Current target folder has a minimal Python substrate plus planning docs, JSON Schema, deterministic artifacts, a CLI-first constructed-input preparation path, reviewer approval artifacts, node-audit methodology objects, bounded ensemble contribution normalization, approved constructed-input analysis, and a local HTTP demo app.

- Python package
- Pydantic 2 schema models
- JSON Schema export
- Pytest validation tests
- Static JSON fixtures for synthetic cases
- Static offline reviewer workbench UI generated from deterministic artifacts
- Deterministic redaction floor and constructed-text draft intake
- Reviewer approval manifest and hash-chained approval trace
- Node audit bundle with definitions, evidence, estimates, ranges, medians, methods, confidence, and sensitivity notes
- Ensemble contribution bundle with accepted/downgraded contributions and rejected unsupported static targets
- JSON and Markdown receipts that embed node audits, ensemble contributions, rejected inputs, and a methodology summary
- Static workbench panels for node audit methodology and ensemble contribution review
- Approved constructed-input run generator with receipt and review HTML output
- Local stdlib HTTP demo for paste, redaction, editable structured episode review, approval, deterministic analysis, and output review

## Package Manager

Python packaging is defined in `pyproject.toml`.

## Commands

| Purpose | Command | Verified |
|---|---|---|
| List current source files | `find . -maxdepth 2 -type f | sort` | Yes |
| Inspect project source-of-truth | `sed -n '1,520p' GOAL.md` | Yes |
| Inspect docs/prompts/validation headings | `for f in docs/*.md prompts/*.md validation/*.md examples/*.md roadmaps/*.md; do rg -n '^(#|##|###) ' "$f"; done` | Yes |
| Inspect schema top-level properties | `for f in schemas/*.json; do jq -r 'if .properties then (.title // input_filename), (.properties|keys[]) else (.title // input_filename) end' "$f"; done` | Yes |
| Run tests | `python3 -m pytest -q` | Yes |
| Validate synthetic cases | `PYTHONPATH=src python3 -m sentinel_workbench.validate data/cases` | Yes: `validated=7 errors=0` |
| Validate static role/EvidenceFlow inputs | `PYTHONPATH=src python3 -m sentinel_workbench.static_inputs --static-inputs data/static_inputs/static_inputs.json --case-dir data/cases` | Yes: `static_inputs cases=7 errors=0` |
| Prepare constructed input | `PYTHONPATH=src python3 -m sentinel_workbench.constructed_intake --input data/constructed_inputs/constructed_demo_case.txt --out data/prepared_inputs/constructed_demo_case --episode-id constructed_demo_case --title "Constructed demo case"` | Yes: `status=prepared` |
| Approve constructed input | `PYTHONPATH=src python3 -m sentinel_workbench.approval --prepared-dir data/prepared_inputs/constructed_demo_case --reviewer-id reviewer_demo --approval-note "Demo structured episode reviewed for local deterministic workflow."` | Yes: `status=approved` |
| Validate approved constructed input | `PYTHONPATH=src python3 -m sentinel_workbench.approval --validate-approved data/prepared_inputs/constructed_demo_case` | Yes: `approved_episode=constructed_demo_case status=approved` |
| Run approved constructed demo analysis | `PYTHONPATH=src python3 -m sentinel_workbench.demo_run --prepared-dir data/prepared_inputs/constructed_demo_case --static-inputs data/static_inputs/static_inputs.json --out data/prepared_inputs/constructed_demo_case/analysis` | Yes |
| Generate receipts | `PYTHONPATH=src python3 -m sentinel_workbench.receipts --case-dir data/cases --static-inputs data/static_inputs/static_inputs.json --out data/receipts` | Yes: `receipts=7 out=data/receipts` |
| Export ED schema | `PYTHONPATH=src python3 -m sentinel_workbench.schema_export schemas/ed_decision_episode.schema.json` | Yes |
| Generate evaluation report | `PYTHONPATH=src python3 -m sentinel_workbench.evaluate --case-dir data/cases --out validation/reports/latest.json --receipt-dir data/receipts` | Yes: `cases=7 future_leakage_failures=0` |
| Generate reviewer workbench | `PYTHONPATH=src python3 -m sentinel_workbench.workbench --case-dir data/cases --receipt-dir data/receipts --report validation/reports/latest.json --out data/workbench/index.html` | Yes: `workbench=data/workbench/index.html cases=7` |
| Start local demo app | `PYTHONPATH=src python3 -m sentinel_workbench.local_app --host 127.0.0.1 --port 8765` | Verified by HTTP test on ephemeral local port |
| Editable install dry-run | `python3 -m pip install -e . --dry-run --no-deps` | Yes: would install `sentinel-workbench-0.1.0` |
| Check repository status | `git status --short --branch` | Yes |
| Whitespace diff check | `git diff --check` | Yes |

## Entry Points

Current runtime entry points:

- `sentinel_workbench.models`: ED disposition replay Pydantic models.
- `sentinel_workbench.approval`: reviewer approval gate for prepared constructed input, including approved episode loading, manifest validation, and hash-chained trace validation.
- `sentinel_workbench.demo_run`: deterministic analysis runner for approved prepared input, with workflow artifact hashes, receipt generation, and review HTML output.
- `sentinel_workbench.ensemble`: static role/EvidenceFlow normalization into bounded ensemble contributions and rejected-input tracking.
- `sentinel_workbench.case_library`: required case-pattern coverage summary.
- `sentinel_workbench.constructed_intake`: constructed/deidentified-style text preparation command that emits redacted input, redaction report, and draft episode artifacts.
- `sentinel_workbench.graph`: deterministic node groups, lanes, preventability-opportunity proxy, and posture taxonomy output.
- `sentinel_workbench.loader`: JSON fixture loading and safety preflight.
- `sentinel_workbench.node_audit`: deterministic node audit bundle, node evidence, node estimates, and node-audit completeness summary.
- `sentinel_workbench.replay`: current-time replay view and blocked future fact reporting.
- `sentinel_workbench.redaction`: deterministic redaction floor and redaction report schema.
- `sentinel_workbench.receipts`: deterministic JSON and Markdown receipt generation with node audit and ensemble contribution methodology.
- `sentinel_workbench.workbench`: static offline reviewer workbench generation with graph, receipt, node-audit, and ensemble-contribution panels.
- `sentinel_workbench.local_app`: local stdlib HTTP demo for paste, prepare, review/edit, approve, run, and review output.
- `sentinel_workbench.safety`: forbidden phrase, named institution, secret, and PHI-pattern scanner.
- `sentinel_workbench.schema_export`: ED JSON Schema export command.
- `sentinel_workbench.static_inputs`: static role-output and EvidenceFlow template validation.
- `sentinel_workbench.validate`: deterministic fixture validation command.
- `sentinel_workbench.evaluate`: deterministic evaluation report command.
- `docs/18_deterministic_poc_status.md`: implemented/deferred/pre-real-use status boundary.
- `docs/19_repository_publishing.md`: GitHub remote, branch, and pre-push verification notes.
- `docs/20_emex_admsve_reuse_evaluation.md`: reuse evaluation for EMEX and AdmSVE donor patterns.

Current planning entry points:

- `GOAL.md`: authoritative objective, phase plan, safety constraints, and proof-of-done.
- `README.md`: broad handoff package overview.
- `roadmaps/01_short_term_poc_roadmap.md`: generic POC milestone plan.
- `roadmaps/04_phase_0_ed_disposition_implementation_plan.md`: ED disposition replay scope-lock plan.
- `docs/11_data_model_notes.md`: generic current data-model notes.
- `schemas/*.json`: current generic schema drafts.
- `prompts/*.md`: current prompt/dotflow contract drafts.
- `validation/*.md`: current validation strategy drafts.

## Major Folders

- `docs/`: product, methodology, architecture, requirements, UI, API, data model, security, and build epics.
- `schemas/`: JSON Schema drafts for current generic handoff objects.
- `prompts/`: role-agent, EvidenceFlow, and normalizer prompt contracts.
- `roadmaps/`: short-term, long-term, decision-tree, and ED-specific Phase 0 planning.
- `validation/`: metrics, case replay validation, and human review planning.
- `examples/`: synthetic case templates, minimal case ideas, and illustrative receipt shape.
- `src/sentinel_workbench/`: Phase 1 deterministic Python package.
- `data/cases/`: Phase 1 synthetic fixture seed set.
- `data/constructed_inputs/`: safe constructed text inputs for Phase B demo preparation.
- `data/prepared_inputs/`: generated redacted input, redaction reports, draft episodes, approved episodes, approval manifests, approval traces, and constructed-demo analysis output.
- `data/static_inputs/`: Phase 4 static role-output and EvidenceFlow templates plus invalid rejection fixtures.
- `data/receipts/`: deterministic JSON and Markdown receipts.
- `data/workbench/`: generated static reviewer workbench HTML.
- `tests/`: Phase 1 pytest coverage.

## Existing Patterns To Preserve

- Governance workbench framing, not bedside clinical advice.
- Synthetic/deidentified-style fixtures only.
- Graph computes final posture; prompts and dotflows produce structured inputs only.
- Unknown, weak, or AI-derived facts are represented explicitly instead of being silently treated as verified.
- Reconstructable receipts are core artifacts, not an afterthought.
- Future facts must be blocked from current-time replay.
- Optional LLM mode is deferred until static deterministic paths pass.
- Constructed/deidentified text must pass deterministic redaction and residual-risk checks before it can become a draft episode.
- Draft constructed episodes are reviewer-editable artifacts, not approved graph inputs.
- Approved constructed episodes require `approval_manifest.json`, `approval_trace.json`, hash checks, and trace-chain validation.
- Local app runs must use the same approval and receipt path as CLI runs.
- Raw pasted text should not be written into prepared review artifacts; only hashes, redacted text, structured episodes, approval artifacts, receipts, and review HTML should persist.
- Every current graph metric should have a schema-backed node audit before receipt or workbench rendering claims methodology transparency.
- Static role and EvidenceFlow inputs do not decide final posture; they become bounded, inspectable contributions only when they map to deterministic graph nodes.
- Methodology transparency claims must be visible in generated artifacts, not only in code or evaluation summaries.

## Reference Patterns Inspected

- `../OE_dotflows.md`: balanced admission/non-inpatient comparison sections, response-to-therapy field needs, home-plan feasibility questions, information that would change discussion, and forbidden disposition wording.
- `../OE_dotflows2.md`: patient-safety expert framing and error-correction emphasis, treated as reference only because the tone is too broad for direct POC output.
- `../finESS`: local-first app discipline, explicit verification commands, environment preflight pattern, and honest non-advice boundaries.
- `../clinclaw-firewall`: fail-closed clinical safety boundaries, hash-chained traces, receipts, most-restrictive-wins posture, synthetic-only demos, and local pytest verification.
- `../AdmSVE`: local app pattern, deterministic redaction floor, intake extraction, trace, tiered provenance output, metrics, and reporting.
- `../EMEX`: artifact-first prepare/ingest workflow, conservative prose ingestion, packet building, leakage reporting, and static demo flow.

## Tests and Verification

Current tests cover:

- schema validation tests,
- fixture loader valid/invalid tests,
- future-leakage guard tests,
- forbidden phrase scanner tests,
- secret/PHI pattern scanner tests,
- module command tests for schema export and fixture validation.
- seven required GOAL.md case patterns.
- T4 future-fact blocking from all T0-T3 replay views.
- required GOAL.md graph metrics.
- separate commission, omission, and therapy-response lanes.
- deterministic evaluation report generation.
- static role-output and EvidenceFlow validation before optional LLM mode.
- JSON and Markdown receipt completeness across all seven cases.
- static reviewer workbench panel coverage, receipt export links, visible POC warning, and forbidden-phrase screening.
- explicit status documentation for implemented, deferred, pre-real-use, and not-claimed boundaries.
- deterministic redaction of PHI-like spans.
- residual PHI-risk block/quarantine behavior.
- constructed text to valid draft `DecisionEpisode` generation.
- redaction report schema export and constructed-intake console-script registration.
- reviewer approval artifact generation and validation.
- unapproved draft rejection through `load_approved_episode`.
- approval manifest and trace schema export.
- node audit schema export and node-audit completeness reporting.
- weak AI-derived evidence is marked weak and limitation-bearing in node audits.
- ensemble contribution schema export and completeness reporting.
- unsupported static node targets are rejected with reasons.
- receipt JSON and Markdown expose node audits, ranges, medians, distributions, evidence refs, sensitivity notes, ensemble contribution dispositions, and rejected ensemble inputs.
- static workbench exposes node audit methodology and ensemble contribution panels.
- approved constructed-demo analysis writes receipt JSON, receipt Markdown, and review HTML.
- local HTTP app prepare/approve/run path is covered by an ephemeral-port integration test.

Receipt completeness and explicit automated validation categories are tracked in `validation/reports/latest.json`. The generated reviewer workbench is `data/workbench/index.html`.

## Likely Files For Current Task

- `GOAL.md`
- `README.md`
- `roadmaps/04_phase_0_ed_disposition_implementation_plan.md`
- `REPO_MAP.md`
- `RISK_NOTES.md`
- `PROGRESS.md`
- `DECISIONS.md`
- `docs/11_data_model_notes.md`
- `schemas/*.json`
- `validation/*.md`
- `src/sentinel_workbench/*.py`
- `data/cases/*.json`
- `data/workbench/index.html`
- `docs/18_deterministic_poc_status.md`
- `docs/19_repository_publishing.md`
- `docs/20_emex_admsve_reuse_evaluation.md`
- `src/sentinel_workbench/redaction.py`
- `src/sentinel_workbench/constructed_intake.py`
- `src/sentinel_workbench/approval.py`
- `src/sentinel_workbench/demo_run.py`
- `src/sentinel_workbench/ensemble.py`
- `src/sentinel_workbench/local_app.py`
- `src/sentinel_workbench/node_audit.py`
- `data/constructed_inputs/*.txt`
- `data/prepared_inputs/**/*.json`
- `data/prepared_inputs/**/*.txt`
- `tests/test_phase1_models.py`
- `tests/test_phase2_case_library.py`
- `tests/test_phase3_prudence_graph.py`
- `tests/test_phase3_evaluation_report.py`
- `tests/test_phase4_static_inputs.py`
- `tests/test_phase6_receipts.py`
- `tests/test_phase7_workbench.py`
- `tests/test_phase_b_constructed_intake.py`
- `tests/test_phase_c_reviewer_approval.py`
- `tests/test_phase_d_node_audit.py`
- `tests/test_phase_e_ensemble_contributions.py`
- `tests/test_phase_g_local_demo_app.py`
- `tests/test_full_poc_documentation.py`

## Unknowns

- Whether the stdlib local app should later be replaced with a fuller FastAPI/frontend implementation.
- Exact scoring constants for future graph versions remain intentionally provisional until static role/EvidenceFlow inputs and receipt review exist.
