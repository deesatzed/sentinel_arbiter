# PROGRESS.md

## 2026-06-11 - Phase 0 Discovery And Scope Lock

### Completed So Far

- Read `GOAL.md`, the only project source-of-truth control file present at the start of the pass.
- Confirmed `STANDARDS.md`, `IMPLEMENT.md`, `DECISIONS.md`, `PROGRESS.md`, and `TASK_QUEUE.md` were not present before this update.
- Inspected the target handoff package:
  - `README.md`
  - `docs/*.md`
  - `schemas/*.json`
  - `prompts/*.md`
  - `validation/*.md`
  - `examples/*.md`
  - `roadmaps/*.md`
- Inspected required reference inputs:
  - `../OE_dotflows.md`
  - `../OE_dotflows2.md`
  - selected patterns from `../finESS`
  - selected patterns from `../clinclaw-firewall`
- Created `roadmaps/04_phase_0_ed_disposition_implementation_plan.md` to make the ED disposition replay delta explicit.
- Created `REPO_MAP.md` and `RISK_NOTES.md` for repo orientation and implementation risk tracking.
- Created `DECISIONS.md` to preserve the Phase 0 decisions that should govern Phase 1.
- Updated `README.md` and `roadmaps/01_short_term_poc_roadmap.md` to cross-link the ED-specific Phase 0 plan.

### Verification Evidence

- JSON syntax check passed for all files in `schemas/*.json` using `jq empty`.
- Forbidden disposition-phrase scan found no matches outside explicit safety-rule lists.
- Secret/PHI pattern scan found only policy/planning text that mentions secrets or PHI; no credential-looking values were found.
- Named-site scan found one pre-existing external governance anchor in `docs/01_existing_needs_and_problem_fit.md`: `Joint Commission`. This was not added in this pass and is not a synthetic case, employer, patient, or clinical site.
- `git status --short --branch` and `git diff --check` cannot run in this target folder because it is not inside a git repository. Sibling folders `../finESS` and `../clinclaw-firewall` are separate git repositories and were not modified.

### Current State

- Superseded by the Phase 1 section below: `sentinel_codex_handoff` now has a minimal Python package, tests, a fixture directory, and an ED-specific exported schema.
- The original generic schemas remain as planning references alongside the new ED-specific schema.
- The target folder is not currently its own git repository.

### Assumptions

- The first implementation milestone should remain local, offline, deterministic, and synthetic.
- The broad Sentinel docs should be preserved and narrowed by additive ED-specific artifacts instead of rewritten.
- Reference repos are read-only inputs for this goal unless a later explicit instruction says otherwise.
- The existing handoff's posture taxonomy remains the output vocabulary for the POC.

### Remaining Work

- Phase 7 is now represented by the static offline reviewer workbench section below.
- Phase 8: optional LLM prompt mode and model-swap evaluation remain deferred.

## 2026-06-11 - Phase 1 Skeleton And Core Schemas Started

### Completed So Far

- Added `pyproject.toml` with local package metadata and console-script entry points.
- Added `.env.example` documenting that deterministic Phase 1 needs no external services or secrets.
- Added `.gitignore` for Python and test-generated artifacts.
- Added `src/sentinel_workbench/models.py` with ED disposition replay Pydantic 2 models.
- Added `src/sentinel_workbench/loader.py` with JSON fixture loading and safety preflight.
- Added `src/sentinel_workbench/replay.py` with current-time replay view and blocked future fact reporting.
- Added `src/sentinel_workbench/safety.py` with forbidden phrase, named institution, secret-pattern, and PHI-pattern scanning.
- Added `src/sentinel_workbench/schema_export.py` and `src/sentinel_workbench/validate.py` module commands.
- Added one valid synthetic ED fixture and one invalid fixture under `data/cases/`.
- Added `tests/test_phase1_models.py` using test-first coverage for model validation, invalid fixture failure, future leakage blocking, safety scanning, schema export, and validation command behavior.
- Exported `schemas/ed_decision_episode.schema.json`.

### Verification Evidence

- Initial red test failed as expected with `ModuleNotFoundError: No module named 'sentinel_workbench'`.
- Command regression test failed before the `python -m` entrypoint fix because the schema file was not created.
- `python3 -m pytest -q` passed: `7 passed`.
- `PYTHONPATH=src python3 -m sentinel_workbench.validate data/cases` passed: `validated=1 errors=0`.
- `PYTHONPATH=src python3 -m sentinel_workbench.schema_export schemas/ed_decision_episode.schema.json` created `schemas/ed_decision_episode.schema.json`.
- `jq empty schemas/ed_decision_episode.schema.json` passed.
- Fixture/generated-artifact forbidden phrase scan returned no matches outside scanner definitions and explicit scanner tests.
- Fixture/generated-artifact secret and PHI-pattern scan returned no matches outside scanner definitions.
- `python3 -m pip install -e . --dry-run --no-deps` succeeded and reported it would install `sentinel-workbench-0.1.0`.
- `git rev-parse --show-toplevel` still fails because this target folder is not inside a git repository; `git diff --check` remains unavailable here.

### Current State

- Phase 1 core case substrate is substantially complete, but static role-output and EvidenceFlow schemas/fixtures remain.
- Core ED `DecisionEpisode` schemas, fixture loading, JSON schema export, safety preflight, and future-fact blocking exist.
- The synthetic case library now has seven valid cases covering all GOAL.md required case patterns.
- Static role-output fixtures, static EvidenceFlow fixtures, and deterministic receipt generation now exist.

## 2026-06-11 - Phase 2 Seven-Case Library And Leakage Guard

### Completed So Far

- Added `src/sentinel_workbench/case_library.py` with required GOAL.md case-pattern coverage summary.
- Added explicit `covered_case_patterns` to ED case expected outputs.
- Added six additional valid synthetic ED replay cases:
  - `valid_therapy_improvement_case.json`
  - `valid_therapy_not_considered_case.json`
  - `valid_limited_added_value_case.json`
  - `valid_home_plan_feasibility_case.json`
  - `valid_ai_weak_fact_case.json`
  - `valid_low_value_gap_suppression_case.json`
- Updated `valid_material_gap_case.json` to declare covered patterns.
- Added `tests/test_phase2_case_library.py`.
- Extended `sentinel_workbench.validate` so the case directory must have at least seven valid cases and cover every required case pattern.

### Case Pattern Coverage

- `material_missing_input_before_disposition`
- `therapy_offered_documented_improvement`
- `therapy_offered_nonresponse_or_unclear_response`
- `therapy_plausibly_indicated_but_not_considered`
- `discharge_home_plan_feasibility_problem`
- `admission_or_observation_limited_added_value`
- `ai_derived_or_weakly_sourced_fact_driving_decision`

### Verification Evidence

- Initial Phase 2 red test failed with `ModuleNotFoundError: No module named 'sentinel_workbench.case_library'`.
- `python3 -m pytest -q` passed: `9 passed`.
- `PYTHONPATH=src python3 -m sentinel_workbench.validate data/cases` passed: `validated=7 errors=0`.
- Case-library summary reported `valid_case_count= 7`, all seven required patterns covered, and no missing patterns.
- `for f in schemas/*.json data/cases/*.json; do jq empty "$f"; done` passed.
- Fixture/schema forbidden disposition-phrase scan returned no matches.
- Fixture/schema secret and PHI-pattern scan returned no matches.
- `python3 -m pip install -e . --dry-run --no-deps` succeeded and reported it would install `sentinel-workbench-0.1.0`.
- `git rev-parse --show-toplevel` still fails because this target folder is not inside a git repository; `git diff --check` remains unavailable here.

### Current State

- Phase 2 core fixture coverage is in place.
- Every valid case includes T0 through T4 timepoints.
- Tests prove T4 facts are blocked from T0 through T3 replay views.
- Expected output labels are present as fixture metadata; graph scoring does not consume hidden outcome facts or prompt outputs.

## 2026-06-11 - Phase 3 Deterministic Node Groups And Evaluation Report

### Completed So Far

- Added `src/sentinel_workbench/graph.py`.
- Added deterministic first-pass graph metrics for:
  - `information_sufficiency`
  - `material_gap_strength`
  - `harm_clock`
  - `information_clock`
  - `recoverability`
  - `future_correction_opportunity`
  - `decision_weight`
  - `ai_provenance_risk`
  - `commission_risk`
  - `omission_risk`
  - `therapy_response_relevance`
  - `next_best_information_rank`
  - `preventability_opportunity_score`
- Added first-class commission, omission, and therapy-response lanes.
- Added deterministic final posture output using the existing Sentinel posture taxonomy.
- Added `src/sentinel_workbench/evaluate.py`.
- Added `validation/reports/latest.json`.
- Added tests:
  - `tests/test_phase3_prudence_graph.py`
  - `tests/test_phase3_evaluation_report.py`

### Verification Evidence

- Initial Phase 3 red test failed with `ModuleNotFoundError: No module named 'sentinel_workbench.graph'`.
- Initial evaluation-report red test failed with `ModuleNotFoundError: No module named 'sentinel_workbench.evaluate'`.
- Regression test caught a limited-added-value case incorrectly entering the omission lane; the graph logic now keeps that as commission-lane evidence.
- `python3 -m pytest -q` passed: `16 passed`.
- `PYTHONPATH=src python3 -m sentinel_workbench.validate data/cases` passed: `validated=7 errors=0`.
- `PYTHONPATH=src python3 -m sentinel_workbench.evaluate --case-dir data/cases --out validation/reports/latest.json` reported `cases=7 future_leakage_failures=0`.
- `validation/reports/latest.json` reports expected posture agreement `matched=7`, `total=7`.
- `validation/reports/latest.json` reports lane coverage: commission `5`, omission `4`, therapy response `3`.
- `validation/reports/latest.json` now reports receipt completeness in the Phase 6 section below.

### Current State

- Phase 3 core deterministic graph substrate is in place.
- The graph is a transparent fixture-field heuristic, not a clinical evidence engine.
- Optional LLM/OpenEvidence/live evidence behavior is still deferred.

## 2026-06-11 - Phase 4 Static Role And EvidenceFlow Inputs

### Completed So Far

- Added `src/sentinel_workbench/static_inputs.py`.
- Added static role-output templates for `prudent_layperson`, `prudent_provider`, `prudent_healthcare_ai`, `duty_to_inquire`, `risk_horizon`, `red_team`, and `defense`.
- Added static EvidenceFlow templates for `guideline_dependency`, `next_best_input`, `high_risk_alternative`, and `prudent_ai_conduct`.
- Added `data/static_inputs/static_inputs.json`.
- Added invalid rejection fixtures `data/static_inputs/invalid_final_verdict_role.json` and `data/static_inputs/invalid_unknown_node_target.json`.
- Added schema export for `schemas/static_role_assessment.schema.json`, `schemas/static_evidenceflow_result.schema.json`, and `schemas/static_input_bundle.schema.json`.
- Added `tests/test_phase4_static_inputs.py`.
- Integrated static input validation into `validation/reports/latest.json`.

### Verification Evidence

- Initial Phase 4 red test failed with `ModuleNotFoundError: No module named 'sentinel_workbench.static_inputs'`.
- `python3 -m pytest -q` passed: `19 passed`.
- `PYTHONPATH=src python3 -m sentinel_workbench.static_inputs --static-inputs data/static_inputs/static_inputs.json --case-dir data/cases` passed: `static_inputs cases=7 errors=0`.
- `validation/reports/latest.json` reports static input validation errors as `[]`, role template count `7`, and EvidenceFlow template count `4`.
- Invalid final-verdict fixture is rejected by test coverage through forbidden disposition phrase scanning.
- Invalid unknown-node-target fixture is rejected by test coverage.

### Current State

- Static role-output and EvidenceFlow templates validate for all seven synthetic cases before optional LLM mode.
- Static templates are deterministic and current-time only.
- The static templates are deliberately generic across cases; later phases may replace them with per-case richer fixtures after receipt and role-disagreement surfaces exist.
- Optional LLM/OpenEvidence/live evidence behavior is still deferred.

## 2026-06-11 - Phase 6 Deterministic Receipts

### Completed So Far

- Added `src/sentinel_workbench/receipts.py`.
- Added deterministic JSON receipt generation for all seven valid synthetic cases.
- Added deterministic Markdown receipt rendering for all seven valid synthetic cases.
- Added `data/receipts/json/*.json`.
- Added `data/receipts/markdown/*.md`.
- Added `schemas/ed_sentinel_receipt.schema.json`.
- Added `tests/test_phase6_receipts.py`.
- Integrated receipt completeness into `validation/reports/latest.json`.

### Receipt Fields Covered

- `input_hashes`
- `timepoint_id`
- `prompt_or_dotflow_versions`
- `model_versions`
- `evidence_versions`
- `node_values`
- `rejected_or_downgraded_findings`
- `role_disagreement_map`
- `final_posture`
- `decision_weight`
- `preventability_opportunity_explanation`
- `signature_placeholder`

### Human-Readable Sections Covered

- What was known.
- What was missing.
- What would have changed the discussion.
- What hospital-based monitoring or treatment might add.
- What non-inpatient alternatives might add.
- Commission concerns.
- Omission concerns.
- Therapy-response concerns.
- Why the graph selected the posture.

### Verification Evidence

- Initial Phase 6 red test failed with `ModuleNotFoundError: No module named 'sentinel_workbench.receipts'`.
- `python3 -m pytest -q` passed: `22 passed`.
- `PYTHONPATH=src python3 -m sentinel_workbench.receipts --case-dir data/cases --static-inputs data/static_inputs/static_inputs.json --out data/receipts` passed: `receipts=7 out=data/receipts`.
- `validation/reports/latest.json` reports receipt completeness `complete=true`, expected receipts `7`, JSON receipts `7`, Markdown receipts `7`, no missing JSON, and no missing Markdown.
- Receipt-inclusive forbidden disposition-phrase scan returned no matches.
- Receipt-inclusive secret and PHI-pattern scan returned no matches.

### Current State

- Deterministic local replay can now generate reconstructable JSON receipts and human-readable Markdown receipts for all seven synthetic cases.

## 2026-06-11 - EMEX And AdmSVE Reuse Evaluation

### Completed So Far

- Evaluated sibling repositories `../EMEX` and `../AdmSVE` read-only as potential donors for Sentinel's next demo layer.
- Saved the evaluation in `docs/20_emex_admsve_reuse_evaluation.md`.
- Identified AdmSVE as the primary donor for a local app pattern, redaction abstraction, intake extraction, hash-chained trace, tiered provenance output, metrics, and HTML reporting.
- Identified EMEX as the secondary donor for artifact-first prepare/ingest workflow, manual companion prose ingestion, packet building, leakage reporting, and a simple static demo flow.
- Documented that Sentinel still needs a native node-audit methodology layer for node definitions, evidence, distributions, ranges, medians, ensemble contribution, disagreements, and sensitivity notes.

### Verification Evidence

- `PYTHONPATH=src uv run --no-project --with pytest python -m pytest -q` in `../EMEX` passed: `21 passed`.
- `PYTHONPATH=src:. uv run --no-project --with pytest --with fastapi --with uvicorn --with httpx python -m pytest -q` in `../AdmSVE` passed: `134 passed`.
- The first direct `python3 -m pytest -q` attempts in both sibling repos failed only because the active Homebrew Python 3.14 environment did not have `pytest` installed.

### Current State

- No source code was copied from EMEX or AdmSVE.
- The recommended next Sentinel step is to build a CLI-first constructed-text intake and node-audit layer before adding a live local app endpoint.
- Receipts are unsigned POC artifacts with `UNSIGNED_DETERMINISTIC_POC` placeholders.
- Receipts use static role/EvidenceFlow template versions and deterministic graph outputs.
- Reviewer workbench UI now exists as `data/workbench/index.html`.
- Optional LLM/OpenEvidence/live evidence behavior remains deferred.

## 2026-06-11 - Phase 7 Static Reviewer Workbench UI

### Completed So Far

- Added `src/sentinel_workbench/workbench.py`.
- Added `tests/test_phase7_workbench.py`.
- Added console-script entry point `sentinel-workbench-generate-ui`.
- Generated `data/workbench/index.html` from:
  - `data/cases/`
  - `data/receipts/`
  - `validation/reports/latest.json`
- The static UI includes:
  - case library,
  - timeline replay,
  - information gap panel,
  - therapy-response panel,
  - commission/omission panel,
  - provenance panel,
  - two-clock panel,
  - next-best-input panel,
  - graph inspector,
  - receipt viewer/export,
  - evaluation dashboard.
- The UI displays a visible POC warning: `Planning / governance POC - not for patient care.`
- Receipt links are relative from `data/workbench/index.html` to generated JSON and Markdown receipts.

### Verification Evidence

- Initial Phase 7 red test failed with `ModuleNotFoundError: No module named 'sentinel_workbench.workbench'`.
- Expanded case-level inspection test initially failed because case anchors were missing.
- `python3 -m pytest tests/test_phase7_workbench.py -q` passed: `1 passed`.
- `python3 -m pytest -q` passed: `23 passed`.
- Workbench generation passed: `workbench=data/workbench/index.html cases=7`.
- Workbench structural scan found the required panel IDs, POC warning, and receipt links.
- Workbench forbidden disposition-phrase scan returned no matches.
- Browser-control verification was attempted through the available Node path, but Playwright was not installed in that environment. No browser screenshot was produced in this pass.

### Current State

- The deterministic local POC now has a static reviewer-facing workbench artifact.
- The UI is generated from current deterministic artifacts; it is not a live clinical tool and does not call external services.
- Optional LLM/OpenEvidence/live evidence behavior remains deferred.

## 2026-06-11 - Full POC Validation Report And Status Boundary

### Completed So Far

- Updated `src/sentinel_workbench/graph.py` so current-time graph evaluation uses unresolved information gaps accumulated through the replay timepoint while still excluding hidden T4 outcome facts.
- Updated `src/sentinel_workbench/evaluate.py` to emit explicit `automated_validation` categories for:
  - omission detection,
  - commission warning detection,
  - therapy-response integration,
  - next-best-information usefulness.
- Added `tests/test_full_poc_documentation.py`.
- Extended `tests/test_phase3_evaluation_report.py` to require the explicit automated validation categories.
- Added `docs/18_deterministic_poc_status.md` to document implemented scope, deferred scope, requirements before real clinical/prospective/production use, non-claims, and local verification commands.
- Updated `README.md`, `REPO_MAP.md`, and `DECISIONS.md` to reference the status boundary.

### Verification Evidence

- Initial report-category test failed with `KeyError: 'automated_validation'`.
- Initial status-document test failed with `FileNotFoundError` for `docs/18_deterministic_poc_status.md`.
- Targeted tests passed: `python3 -m pytest tests/test_full_poc_documentation.py tests/test_phase3_evaluation_report.py -q` reported `3 passed`.
- Full tests passed: `python3 -m pytest -q` reported `25 passed`.
- Case validation passed: `validated=7 errors=0`.
- Static input validation passed: `static_inputs cases=7 errors=0`.
- Receipt generation passed: `receipts=7 out=data/receipts`.
- Evaluation report generation passed: `cases=7 future_leakage_failures=0`.
- Workbench generation passed: `workbench=data/workbench/index.html cases=7`.
- JSON syntax check passed across schemas, cases, static inputs, receipt JSON, and `validation/reports/latest.json`.
- `validation/reports/latest.json` reports automated validation expected/matched counts as:
  - omission detection `5/5`,
  - commission warning detection `6/6`,
  - therapy-response integration `3/3`,
  - next-best-information usefulness `6/6`.
- Forbidden disposition-phrase scan returned no matches across generated artifacts and current project status docs outside the authoritative goal/schema safety surfaces.
- Secret/PHI-pattern scan returned no matches across generated artifacts and current project status docs.
- Editable install dry-run succeeded and reported it would install `sentinel-workbench-0.1.0`; the global Python environment still emits a pre-existing invalid distribution warning for `~ecret-sweep`.
- Earlier `git rev-parse --show-toplevel && git diff --check` could not run because the target folder was not inside a git repository. The local repository baseline section below supersedes that caveat.

### Current State

- The report now exposes named Full POC validation categories rather than relying only on raw lane coverage.
- The project now has a checked status document separating deterministic implementation from deferred LLM/OpenEvidence/live-evidence/prospective/production work.
- Superseded by the local repository baseline section below: `git diff --check` is now available inside this target folder.

## 2026-06-11 - Local Repository Baseline For Final Verification

### Completed So Far

- Removed ignored `.DS_Store` metadata files from the target folder.
- Initialized a local git repository in `sentinel_codex_handoff`.
- Confirmed no git remote is configured.
- Normalized trailing whitespace and extra EOF blank lines found by `git diff --cached --check`.
- Updated the Markdown receipt renderer so regenerated receipt summaries end with a single newline.
- Created the initial local baseline commit: `156c844 Initial deterministic Sentinel POC`.

### Verification Evidence

- Initial staged whitespace check failed on pre-existing Markdown trailing whitespace and generated Markdown receipt EOF blanks.
- After cleanup and receipt renderer update, both `git diff --cached --check` and `git diff --check` returned cleanly.
- Initial local baseline commit was created successfully with local-only author metadata.

### Current State

- `sentinel_codex_handoff` is now a standalone local git repository on branch `master`.
- No remote is configured.
- `git diff --check` can now be used as the Full POC proof command.

## 2026-06-11 - GitHub Publishing Setup

### Completed So Far

- Confirmed the project is already a local git repository.
- Confirmed GitHub CLI is installed and authenticated for the `deesatzed` account.
- Confirmed `https://github.com/deesatzed/sentinel_arbiter.git` is reachable and has no refs returned by `git ls-remote`.
- Added `docs/19_repository_publishing.md`.
- Updated `README.md`, `REPO_MAP.md`, and `DECISIONS.md` with the GitHub publishing target.

### Current State

- Publishing target: `https://github.com/deesatzed/sentinel_arbiter.git`.
- Planned primary branch: `main`.

## 2026-06-11 - Goal Refresh For Transparent Local Demo

### Completed So Far

- Replaced `GOAL.md` with a refreshed project contract that treats the existing deterministic POC as the baseline and defines the next milestone as a transparent local demo.
- Added explicit requirements for constructed or governance-approved deidentified input, redaction-before-intake, residual-risk blocking/quarantine, reviewer-approved structured episodes, node audit methodology, ensemble transparency, upgraded receipts, and workbench/local-app review.
- Incorporated the EMEX and AdmSVE reuse findings from `docs/20_emex_admsve_reuse_evaluation.md`.
- Added `DECISIONS.md` entry `2026-06-11-14` documenting the scope promotion from deterministic framework to transparent local demo.

### Current State

- The new `GOAL.md` is now the source-of-truth contract for the next build phase.
- The next implementation should start with a CLI-first redaction and constructed-text intake path, then add reviewer approval, node audit objects, ensemble contribution handling, upgraded receipts, workbench rendering, and only then a local app endpoint.

## 2026-06-11 - Phase B Constructed Input Preparation Started

### Completed So Far

- Added `src/sentinel_workbench/redaction.py` with a deterministic stdlib redaction floor for MRN, DOB, phone, and email-like spans plus residual PHI-pattern reporting.
- Added `src/sentinel_workbench/constructed_intake.py` with a CLI-first preparation command that redacts input, writes a redaction report, and emits a reviewer-editable draft `DecisionEpisode`.
- Added `tests/test_phase_b_constructed_intake.py` covering redaction, residual-risk blocking, residual-risk quarantine, valid draft episode generation, module command behavior, schema export, and console-script registration.
- Added `schemas/redaction_report.schema.json`.
- Added `data/constructed_inputs/constructed_demo_case.txt`.
- Generated `data/prepared_inputs/constructed_demo_case/redacted_input.txt`, `redaction_report.json`, and `draft_episode.json` from the new command.
- Updated `README.md` with the constructed-input preparation workflow.

### Verification Evidence

- Initial Phase B test run failed with `ModuleNotFoundError: No module named 'sentinel_workbench.constructed_intake'`, confirming the tests covered missing behavior before implementation.
- Expanded integration tests failed until `redaction_report.schema.json` export and the `sentinel-workbench-prepare-constructed-input` console script were added.
- `python3 -m pytest tests/test_phase_b_constructed_intake.py -q` passed: `7 passed`.
- `PYTHONPATH=src python3 -m sentinel_workbench.constructed_intake --input data/constructed_inputs/constructed_demo_case.txt --out data/prepared_inputs/constructed_demo_case --episode-id constructed_demo_case --title "Constructed demo case"` passed with `status=prepared`.
- The generated draft episode loaded successfully as `constructed_demo_case` with five timepoints.

### Current State

- Phase B now has a working CLI-first path from constructed text to redacted input, redaction report, and draft structured episode.
- The draft episode is not yet reviewer-approved for analysis. Phase C still needs explicit reviewer approval artifacts, validation, and trace events before constructed input can feed the graph as a complete demo run.

## 2026-06-11 - Phase C Reviewer Approval Artifact Gate Started

### Completed So Far

- Added `src/sentinel_workbench/approval.py`.
- Added `tests/test_phase_c_reviewer_approval.py`.
- Added `sentinel-workbench-approve-constructed-input` console-script registration.
- Added `schemas/approval_manifest.schema.json` and `schemas/approval_trace.schema.json`.
- Extended `schema_export.py` to export approval schemas.
- Extended redaction reports with `input_sha256` so raw constructed input can be hashed without being copied into review artifacts.
- Generated `data/prepared_inputs/constructed_demo_case/approved_episode.json`, `approval_manifest.json`, and `approval_trace.json`.
- Updated `README.md`, `REPO_MAP.md`, and `DECISIONS.md` with the approval gate.

### Verification Evidence

- Initial Phase C test run failed with `ModuleNotFoundError: No module named 'sentinel_workbench.approval'`, confirming tests covered missing behavior before implementation.
- Added failing assertions for raw-input hashing; they failed until `input_sha256` was added to redaction reports and carried into approval manifests.
- `python3 -m pytest tests/test_phase_b_constructed_intake.py tests/test_phase_c_reviewer_approval.py -q` passed: `14 passed`.
- Approval generation passed: `status=approved out=data/prepared_inputs/constructed_demo_case`.
- Approval validation passed: `approved_episode=constructed_demo_case status=approved`.

### Current State

- Constructed input now has a CLI-first path through redaction, draft episode generation, reviewer approval, manifest validation, and hash-chained approval trace.
- Direct draft JSON is rejected by `load_approved_episode`; later constructed-input analysis should use the approved directory path.
- Phase D node audit methodology remains the next major trust-layer step.

## 2026-06-11 - Phase D Node Audit Methodology Started

### Completed So Far

- Added `src/sentinel_workbench/node_audit.py`.
- Added `tests/test_phase_d_node_audit.py`.
- Added `schemas/node_audit.schema.json`.
- Extended `schema_export.py` to export the node audit schema.
- Extended `evaluate.py` so `validation/reports/latest.json` includes `node_audit_completeness`.
- Implemented deterministic `NodeAuditBundle` generation for every current graph metric in `REQUIRED_GRAPH_METRICS`.
- Added schema-backed `NodeDefinition`, `NodeEvidence`, `NodeEstimate`, `EnsembleContribution`, and `NodeAudit` models.
- Added evidence mapping that excludes T4 future facts and marks unverified AI-derived evidence as weak with limitations.
- Added `DECISIONS.md` entry `2026-06-11-16` documenting the node-audit-before-receipt/UI decision.

### Verification Evidence

- Initial Phase D test run failed with `ModuleNotFoundError: No module named 'sentinel_workbench.node_audit'`, confirming tests covered missing behavior before implementation.
- `python3 -m pytest tests/test_phase_d_node_audit.py -q` passed: `6 passed`.
- `PYTHONPATH=src python3 -m sentinel_workbench.schema_export schemas/ed_decision_episode.schema.json` exported `schemas/node_audit.schema.json`.
- `PYTHONPATH=src python3 -m sentinel_workbench.evaluate --case-dir data/cases --out validation/reports/latest.json --receipt-dir data/receipts` passed with `cases=7 future_leakage_failures=0`.
- `validation/reports/latest.json` reports `node_audit_completeness.complete=true`, `case_count=7`, `expected_nodes_per_case=13`, and no missing or incomplete node audits.

### Current State

- Every existing deterministic graph node now has a schema-backed audit object with definition, dependencies, evidence, value, range, median, distribution kind, confidence, method, and sensitivity note.
- Ensemble contribution objects are schema-defined, but Phase E still needs static role/EvidenceFlow contribution normalization and accept/reject/downgrade logic.
- Superseded by later phases: receipts and the workbench now render the node audit methodology directly.

## 2026-06-11 - Phase E Ensemble Contribution Normalization Started

### Completed So Far

- Added `src/sentinel_workbench/ensemble.py`.
- Added `tests/test_phase_e_ensemble_contributions.py`.
- Added `schemas/ensemble_contribution.schema.json`.
- Extended `schema_export.py` to export the ensemble contribution schema.
- Extended `evaluate.py` so `validation/reports/latest.json` includes `ensemble_contribution_completeness`.
- Extended `node_audit.py` so `build_node_audit_bundle(..., static_bundle=...)` attaches normalized ensemble contributions to the matching node audits.
- Implemented static role and EvidenceFlow normalization into bounded `EnsembleContribution` records with proposed values, proposed ranges, evidence refs, rationales, dispositions, and disposition reasons.
- Implemented rejected-input tracking for static targets that are not deterministic graph nodes.
- Added `DECISIONS.md` entry `2026-06-11-17` documenting graph-node-only contribution normalization.

### Verification Evidence

- Initial Phase E test run failed with `ModuleNotFoundError: No module named 'sentinel_workbench.ensemble'`, confirming tests covered missing behavior before implementation.
- `python3 -m pytest tests/test_phase_e_ensemble_contributions.py -q` passed: `7 passed`.
- `PYTHONPATH=src python3 -m sentinel_workbench.schema_export schemas/ed_decision_episode.schema.json` exported `schemas/ensemble_contribution.schema.json`.
- `PYTHONPATH=src python3 -m sentinel_workbench.evaluate --case-dir data/cases --out validation/reports/latest.json --receipt-dir data/receipts` passed with `cases=7 future_leakage_failures=0`.
- `validation/reports/latest.json` reports `ensemble_contribution_completeness.complete=true`, `case_count=7`, `contribution_count=91`, `rejected_input_count=112`, no missing dispositions, and no invalid node targets.
- Direct smoke check for `valid_material_gap_case.json` reported `contributions=13`, `rejected=16`, and dispositions `accepted` and `downgraded`.

### Current State

- Static role and EvidenceFlow influence is now inspectable as bounded contribution records instead of implicit prose influence.
- Unsupported static targets are rejected with reasons rather than silently dropped.
- Superseded by Phase F: receipts and the workbench now render node audits and ensemble contributions directly.

## 2026-06-11 - Phase F Receipt And Workbench Methodology Rendering Started

### Completed So Far

- Extended `SentinelReceipt` with `node_audit_bundle`, `ensemble_contribution_bundle`, and `methodology_summary`.
- Updated receipt generation so every JSON receipt embeds node definitions, dependencies, evidence, estimates, ranges, medians, distributions, confidence/method fields, sensitivity notes, normalized ensemble contributions, and rejected ensemble inputs.
- Updated Markdown receipt rendering with `Node Audit Methodology` and `Ensemble Contributions` sections.
- Updated the static workbench with `node-audit-methodology` and `ensemble-contribution-panel` sections for every synthetic case.
- Regenerated receipt JSON, receipt Markdown, `schemas/ed_sentinel_receipt.schema.json`, `validation/reports/latest.json`, and `data/workbench/index.html`.
- Added tests proving receipt and workbench outputs expose dependent inputs, ranges, medians, distributions, evidence refs, sensitivity notes, accepted/downgraded contributions, and rejected ensemble inputs.

### Verification Evidence

- Initial Phase F focused test run failed because receipts lacked `node_audit_bundle` and `ensemble_contribution_bundle`, Markdown lacked `Node Audit Methodology`, and the workbench lacked `node-audit-methodology`.
- `python3 -m pytest tests/test_phase6_receipts.py tests/test_phase7_workbench.py -q` passed: `5 passed`.
- `python3 -m pytest -q` passed: `53 passed`.
- `PYTHONPATH=src python3 -m sentinel_workbench.validate data/cases` passed: `validated=7 errors=0`.
- `PYTHONPATH=src python3 -m sentinel_workbench.static_inputs --static-inputs data/static_inputs/static_inputs.json --case-dir data/cases` passed: `static_inputs cases=7 errors=0`.
- `PYTHONPATH=src python3 -m sentinel_workbench.schema_export schemas/ed_decision_episode.schema.json` passed.
- `PYTHONPATH=src python3 -m sentinel_workbench.receipts --case-dir data/cases --static-inputs data/static_inputs/static_inputs.json --out data/receipts` passed: `receipts=7 out=data/receipts`.
- `PYTHONPATH=src python3 -m sentinel_workbench.evaluate --case-dir data/cases --out validation/reports/latest.json --receipt-dir data/receipts` passed: `cases=7 future_leakage_failures=0`.
- `PYTHONPATH=src python3 -m sentinel_workbench.workbench --case-dir data/cases --receipt-dir data/receipts --report validation/reports/latest.json --out data/workbench/index.html` passed: `workbench=data/workbench/index.html cases=7`.
- JSON syntax checks with `jq empty` passed for schemas, cases, static inputs, receipts, prepared inputs, and validation reports.
- `git diff --check` passed.
- Forbidden phrase scan matched only explicit safety-rule lists, scanner tests, and invalid rejection fixtures.
- PHI/secret-pattern scan matched only deliberate synthetic redaction tests and redaction labels.
- `python3 -m pip install -e . --dry-run --no-deps` succeeded and would install `sentinel-workbench-0.1.0`; the environment still reports a pre-existing invalid `~ecret-sweep` distribution warning.

### Current State

- The transparent deterministic demo now has artifact-backed methodology review in JSON receipts, Markdown receipts, and the static workbench.
- The next major milestone is a local reviewer-edit/app surface for prepared inputs, using the existing redaction, approval, receipt, and workbench artifacts as the safety baseline.

## 2026-06-11 - Phase G Local Demo App Started

### Completed So Far

- Added `prepare_constructed_text()` so the app can process pasted constructed text in memory without writing raw pasted text into prepared review artifacts.
- Added `src/sentinel_workbench/demo_run.py` to validate an approved prepared-input directory, build a receipt with redaction and approval workflow hashes, write receipt JSON/Markdown, and render `review.html`.
- Added `src/sentinel_workbench/local_app.py`, a Python stdlib HTTP app with:
  - `GET /` input form,
  - `POST /prepare` redaction and editable structured episode review,
  - `POST /approve-and-run` reviewer approval plus deterministic analysis and review output.
- Added console scripts:
  - `sentinel-workbench-run-approved-demo`,
  - `sentinel-workbench-local-demo`.
- Added `.sentinel_local_demo/` to `.gitignore` as the default local app workspace.
- Extended `SentinelReceipt` with `workflow_artifacts` and raw-input hash propagation for approved constructed-demo runs.
- Added `tests/test_phase_g_local_demo_app.py`.
- Generated durable constructed-demo analysis artifacts under `data/prepared_inputs/constructed_demo_case/analysis/`.
- Updated README, repo map, status docs, and decision log.

### Verification Evidence

- Initial Phase G test run failed with `ImportError` for missing `prepare_constructed_text`, confirming tests covered missing behavior before implementation.
- `python3 -m pytest tests/test_phase_g_local_demo_app.py -q` passed: `3 passed`.
- `python3 -m pytest -q` passed: `56 passed`.
- `PYTHONPATH=src python3 -m sentinel_workbench.validate data/cases` passed: `validated=7 errors=0`.
- `PYTHONPATH=src python3 -m sentinel_workbench.static_inputs --static-inputs data/static_inputs/static_inputs.json --case-dir data/cases` passed: `static_inputs cases=7 errors=0`.
- `PYTHONPATH=src python3 -m sentinel_workbench.demo_run --prepared-dir data/prepared_inputs/constructed_demo_case --static-inputs data/static_inputs/static_inputs.json --out data/prepared_inputs/constructed_demo_case/analysis` passed and wrote review/receipt artifacts.
- HTTP app behavior is covered by an ephemeral local-port integration test that performs prepare, approve, run, and review.

### Current State

- A reviewer can now run a local app, paste constructed/deidentified-style text, inspect redacted text and editable structured JSON, approve the structured episode, run deterministic analysis, and review an HTML output plus receipts.
- The deterministic CLI path remains the verification baseline.
- Superseded by the validation-report coverage section below: redaction gating, workbench completeness, and local app completeness are now represented in `validation/reports/latest.json`.

## 2026-06-11 - Validation Report Proof Coverage Expanded

### Completed So Far

- Extended `src/sentinel_workbench/evaluate.py` with concrete proof payloads for:
  - `redaction_gating`,
  - `workbench_completeness`,
  - `local_app_completeness`.
- Added tests requiring those payloads to verify prepared-demo redaction status, input hashing, safe redaction, residual-risk block/quarantine behavior, no raw input copy, redacted input visibility, structured episode visibility, node methodology, ensemble contribution review, receipt links, validation status, app endpoints, console scripts, and review HTML safety.
- Regenerated `validation/reports/latest.json` and `data/workbench/index.html`.
- Updated README, repo map, and status documentation to point to the new report keys.

### Verification Evidence

- Initial focused test failed with `KeyError: 'redaction_gating'`, confirming the report lacked the required proof field before implementation.
- `python3 -m pytest tests/test_phase3_evaluation_report.py -q` passed: `3 passed`.
- `python3 -m pytest -q` passed: `57 passed`.
- `PYTHONPATH=src python3 -m sentinel_workbench.validate data/cases` passed: `validated=7 errors=0`.
- `PYTHONPATH=src python3 -m sentinel_workbench.static_inputs --static-inputs data/static_inputs/static_inputs.json --case-dir data/cases` passed: `static_inputs cases=7 errors=0`.
- JSON syntax checks with `jq empty` passed for schemas, cases, static inputs, receipts, prepared inputs, constructed-demo analysis receipts, and validation reports.
- `git diff --check` passed.
- `validation/reports/latest.json` reports `redaction_gating.complete=true`, `workbench_completeness.complete=true`, and `local_app_completeness.complete=true`.

### Current State

- GOAL.md proof item 14 is now much closer to machine-verifiable: the validation report covers schema validity, future leakage, redaction gating, expected posture agreement, omission detection, commission warning detection, therapy-response integration, next-best-information usefulness, node-audit completeness, receipt completeness, workbench completeness, and forbidden phrase violations.
- The remaining major step is a requirement-by-requirement end-to-end completion audit against `GOAL.md` before considering the active goal complete.

## 2026-06-11 - GOAL.md Completion Audit

### Completed So Far

- Added `docs/21_goal_completion_audit.md`.
- Mapped all 16 `GOAL.md` Full Demo Proof Of Done items to current repo evidence.
- Linked the audit from `README.md` and `docs/18_deterministic_poc_status.md`.
- Regenerated constructed input artifacts, approval artifacts, constructed-demo analysis artifacts, synthetic receipts, schemas, evaluation report, and static workbench in dependency order.

### Verification Evidence

- `python3 -m pytest -q` passed: `57 passed`.
- `PYTHONPATH=src python3 -m sentinel_workbench.validate data/cases` passed: `validated=7 errors=0`.
- `PYTHONPATH=src python3 -m sentinel_workbench.static_inputs --static-inputs data/static_inputs/static_inputs.json --case-dir data/cases` passed: `static_inputs cases=7 errors=0`.
- Approval validation passed: `approved_episode=constructed_demo_case status=approved`.
- `PYTHONPATH=src python3 -m sentinel_workbench.demo_run --prepared-dir data/prepared_inputs/constructed_demo_case --static-inputs data/static_inputs/static_inputs.json --out data/prepared_inputs/constructed_demo_case/analysis` passed.
- JSON syntax checks with `jq empty` passed for schemas, cases, static inputs, synthetic receipts, prepared-input JSON, constructed-demo analysis receipts, and validation reports.
- `git diff --check` passed.
- `python3 -m pip install -e . --dry-run --no-deps` succeeded and would install `sentinel-workbench-0.1.0`; the environment still reports the pre-existing invalid `~ecret-sweep` distribution warning.
- Forbidden phrase scan matched only explicit safety-rule lists, scanner tests, and invalid rejection fixtures.
- PHI-like string scan matched only deliberate synthetic redaction check strings and redaction labels.

### Current State

- The transparent local demo milestone is supported by a saved requirement-by-requirement audit.
- Future work remains possible, but the current milestone evidence supports marking the active `GOAL.md` objective complete after commit/push and clean status verification.

## 2026-06-11 - GOAL.md UX Reset For Clinician-Facing Demo

### Completed So Far

- Updated `GOAL.md` so the next milestone is a clinician-facing staged local demo rather than a raw technical output surface.
- Added the required A/B landing choice:
  - A. enough information to make a disposition decision,
  - B. enough information to use an AI-generated response.
- Added staged workflow requirements for paste/upload, `Pre-process`, Node Audit Methodology review, `OK`/`Adjust`/`Re-check selected nodes`, Ensemble Contributions, `Process`, short clinician-readable summary, and `Deeper Dive`.
- Added new proof-of-done items for selected-review-question propagation, app-flow completeness, summary completeness, reviewer adjustment/re-check traceability, and deeper-dive artifacts.
- Added Phase H, Phase I, and Phase J to make the UX rebuild, node-audit checkpoint, clinician summary, and deeper-dive view explicit.
- Added Decision 2026-06-11-20 to preserve why the milestone changed.

### Current State

- The prior transparent local demo remains the baseline substrate.
- The new active target is to build the staged clinician-facing UX over the existing deterministic pipeline without weakening redaction, reviewer approval, node audit, ensemble, receipt, or safety constraints.

## 2026-06-11 - OpenRouter Model Comparison Harness And First Run

### Completed So Far

- Added a CLI-first OpenRouter comparison harness in `src/sentinel_workbench/openrouter_compare.py`.
- Added `.env.example` placeholders for `OPENROUTER_API_KEY` and numbered `MODEL_N` values without committing local secrets.
- Added a limited constructed challenge example in `data/model_comparison/challenging_constructed_case.txt`.
- Added tests for `.env` loading, JSON extraction, node-assessment validation, prompt construction, comparison reporting, and console-script registration.
- Ran the first OpenRouter comparison with seven local `.env` models, then tightened the prompt and reran into `artifacts/model_comparison/challenging_case_v2/`.

### Verification Evidence

- `python3 -m pytest tests/test_openrouter_compare.py -q` passed: `7 passed`.
- `python3 -m pytest -q` passed: `64 passed`.
- Live comparison report written locally:
  - `artifacts/model_comparison/challenging_case_v2/comparison_report.json`
  - `artifacts/model_comparison/challenging_case_v2/comparison_report.md`

### Current State

- Deterministic Sentinel remains the authority; OpenRouter outputs are comparison artifacts only.
- On the challenge case, `deepseek/deepseek-v4-pro` and `x-ai/grok-4.3` produced valid structured outputs that aligned closely with deterministic node values.
- `qwen/qwen3.7-max` produced parseable structured output but shifted several nodes substantially and used action-oriented wording that needs stricter wording gates before app use.
- `google/gemini-3.5-flash`, `nvidia/nemotron-3-ultra-550b-a55b`, and `stepfun/step-3.7-flash` produced invalid or truncated JSON in this run.
- `anthropic/claude-haiku-latest` was rejected by OpenRouter as an invalid model ID.

## 2026-06-11 - Phase H Staged Local App UX Started

### Completed So Far

- Updated the local stdlib app first screen to require one review question before pre-processing:
  - Disposition Information Sufficiency,
  - AI Response Use Sufficiency.
- Renamed the primary input action to `Pre-process`.
- Added a pre-processing review page that shows redacted input, editable structured episode JSON, Node Audit Methodology, Ensemble Contributions, `OK`, `Adjust`, `Re-check Selected Nodes`, and an `Are you sure?` confirmation note.
- Added `run_manifest.json` for local app runs with `selected_review_question`.
- Added a node-audit checkpoint requirement before `/approve-and-run` processing.
- Added a clinician-facing summary-first result page with `Deeper Dive` before structured/raw artifacts.
- Passed the selected review question into receipt `workflow_artifacts`.
- Strengthened `local_app_completeness` in `validation/reports/latest.json` to cover review-question choice, pre-process control, node-audit checkpoint, clinician summary, and deeper-dive rendering.
- Regenerated `data/prepared_inputs/constructed_demo_case/analysis/review.html`, its JSON receipt, `validation/reports/latest.json`, and `data/workbench/index.html`.

### Verification Evidence

- `python3 -m pytest tests/test_phase_g_local_demo_app.py -q` passed: `4 passed`.
- `python3 -m pytest tests/test_phase3_evaluation_report.py::test_evaluation_report_covers_redaction_workbench_and_local_app_completeness -q` passed: `1 passed`.
- `python3 -m pytest -q` passed: `65 passed`.
- `validation/reports/latest.json` reports `local_app_completeness.complete=true`.
- Constructed-demo receipt now includes `workflow_artifacts.selected_review_question=disposition_information_sufficiency`.

### Current State

- Phase H is partially implemented and verifiable for paste-based local input.
- Full multipart file upload handling and durable adjustment/re-check trace artifacts remain future work for later Phase H/I completion.

## 2026-06-11 - Phase I Node Audit Adjustment And Re-check Trace Started

### Completed So Far

- Converted the display-only `OK`, `Adjust`, and `Re-check Selected Nodes` controls into posted checkpoint values.
- Added `selected_node_ids`, `adjustment_note`, and `confirm_adjustment` fields to the local app review form.
- Added confirmation gating: `adjust` and `recheck` checkpoints are blocked unless the reviewer confirms the methodology-changing action.
- Added `node_audit_review_manifest.json` with checkpoint status, selected node IDs, reviewer note, confirmation state, deterministic re-check results, and `graph_authority_preserved=true`.
- Added receipt propagation via `workflow_artifacts.node_audit_review_manifest_sha256`.
- Strengthened `local_app_completeness` to verify adjustment controls, manifest support, and selected-node re-check support.
- Regenerated the constructed demo through the local app path with a selected-node re-check for `material_gap_strength` and `omission_risk`.

### Verification Evidence

- `python3 -m pytest tests/test_phase_g_local_demo_app.py -q` passed: `5 passed`.
- `python3 -m pytest tests/test_phase3_evaluation_report.py::test_evaluation_report_covers_redaction_workbench_and_local_app_completeness -q` passed: `1 passed`.
- `python3 -m pytest -q` passed: `66 passed`.
- `data/prepared_inputs/constructed_demo_case/node_audit_review_manifest.json` contains `checkpoint_status=recheck`, selected nodes `material_gap_strength` and `omission_risk`, and two deterministic re-check results.
- `data/prepared_inputs/constructed_demo_case/analysis/receipts/json/receipt_constructed_demo_case_T3_deterministic.json` includes `workflow_artifacts.node_audit_review_manifest_sha256`.

### Current State

- Phase I is partially implemented for artifact-backed adjustment and selected-node re-check traceability.
- Reviewer edits to actual node estimates remain intentionally non-authoritative; the current implementation records the reviewer checkpoint and deterministic re-check values without replacing graph-derived node estimates.

## 2026-06-11 - Phase H Multipart Upload Path Added

### Completed So Far

- Converted the local app input form to `multipart/form-data`.
- Added a small stdlib multipart parser for local text-file uploads.
- Added upload-or-paste input selection: pasted text wins when present; otherwise the uploaded text file is used.
- Added `input_mode` and `uploaded_filename` to `run_manifest.json` for upload-based runs.
- Added HTTP tests that post real multipart bytes through the local stdlib server.
- Strengthened `local_app_completeness` with `multipart_file_upload_supported`.

### Verification Evidence

- `python3 -m pytest tests/test_phase_g_local_demo_app.py -q` passed: `6 passed`.
- `python3 -m pytest tests/test_phase3_evaluation_report.py::test_evaluation_report_covers_redaction_workbench_and_local_app_completeness -q` passed: `1 passed`.
- `python3 -m pytest -q` passed: `67 passed`.
- `validation/reports/latest.json` reports `local_app_completeness.multipart_file_upload_supported=true`.

### Current State

- Phase H now supports both paste input and local text-file upload for the app demo.
- Uploaded file content still passes through the same deterministic redaction, intake, node audit, ensemble, reviewer checkpoint, processing, summary, and deeper-dive path.

## 2026-06-11 - Phase J Receipt Summary And Deeper-Dive Proof Added

### Completed So Far

- Added top-level receipt fields for `selected_review_question`, `clinician_summary`, and `deeper_dive_artifacts`.
- Added shared receipt wording for review-question labels and clinician-facing governance summaries.
- Updated Markdown receipts to render `Clinician Summary`, `Selected Review Question`, and `Deeper Dive Artifacts`.
- Updated the constructed-demo HTML renderer to use the receipt's saved clinician summary instead of rebuilding summary text separately.
- Strengthened `receipt_completeness` in `validation/reports/latest.json` to inspect generated JSON and Markdown receipts for summary, selected-review-question support, and deeper-dive artifact sections.
- Regenerated `schemas/ed_sentinel_receipt.schema.json`, all case-library receipts, constructed-demo receipt/HTML, `validation/reports/latest.json`, and `data/workbench/index.html`.

### Verification Evidence

- `python3 -m pytest tests/test_phase6_receipts.py -q` passed: `5 passed`.
- `python3 -m pytest tests/test_phase3_evaluation_report.py::test_evaluation_report_covers_graph_and_validation_metrics -q` passed: `1 passed`.
- `python3 -m pytest tests/test_phase_g_local_demo_app.py -q` passed: `6 passed`.
- `python3 -m pytest -q` passed: `68 passed`.
- `git diff --check` passed.
- JSON syntax checks passed for schemas, regenerated JSON receipts, constructed-demo receipt JSON, and `validation/reports/latest.json`.
- Forbidden disposition-phrase scan found only the explicit `GOAL.md` safety list, `src/sentinel_workbench/safety.py`, and the scanner fixture in `tests/test_phase1_models.py`.
- `validation/reports/latest.json` reports `receipt_completeness.complete=true`, `clinician_summary_complete=true`, `deeper_dive_artifacts_complete=true`, `selected_review_question_field_supported=true`, `markdown_clinician_summary_complete=true`, and `markdown_deeper_dive_complete=true`.

### Current State

- Receipt artifacts now preserve the summary-first and deeper-dive trust layer instead of leaving those requirements only in the local HTML view.
- The staged demo still uses deterministic graph authority; LLM/OpenRouter outputs remain comparison artifacts only.
