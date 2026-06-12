# Sentinel Governance Workbench — Codex Handoff Package

Version: 0.1
Date: 2026-06-11
Status: Deterministic ED replay POC with constructed-input preparation, reviewer approval artifacts, node-audit methodology, ensemble contribution normalization, transparent receipt/workbench rendering, and a local stdlib demo app. No production clinical use implied.

Repository: https://github.com/deesatzed/sentinel_arbiter.git

## Product thesis

Sentinel is a governance workbench for AI-assisted healthcare decisions. It does **not** try to be a medical reference tool, a diagnosis app, or a generic multi-agent debate system. It evaluates whether a proposed AI/human decision is **warranted yet** given:

1. what is known now,
2. what is missing but knowable,
3. how soon harm could occur if the decision is wrong,
4. whether there will be future opportunities to correct course,
5. whether the supporting information is trustworthy or AI-derived,
6. which next input would most improve preventability or decision confidence,
7. what a prudent layperson, prudent provider, and prudent healthcare AI would be expected to do.

The POC should demonstrate a **shadow-mode/replay-mode Sentinel Governance Workbench** that creates committee-ready evidence for AI governance, monitoring, auditability, and lifecycle assurance.

The current next milestone is a transparent local demo: constructed or governance-approved deidentified text is redacted first, converted into a reviewer-editable draft episode, approved by a reviewer, then analyzed with node-level evidence, ranges, medians, ensemble contribution, and reconstructable receipts.

## Current need being addressed

Healthcare organizations now face a concrete need to show responsible AI governance, safeguards, monitoring, transparency, quality controls, and lifecycle management. Sentinel is designed as a practical evidence generator for that need, not as a speculative future use case.

Relevant external anchors are listed in `docs/01_existing_needs_and_problem_fit.md`.

## Non-negotiable constraints

- Do **not** use any named clinical site, employer, or institution in generated code, docs, demos, sample data, comments, logs, tests, screenshots, or filenames.
- Build with synthetic, deidentified-style, or public-style replay cases only.
- Do not make the POC a narrow note checker, ambient workflow checker, or single-use clinical tool.
- The language model may extract, structure, and role-assess. It must **not** be the final judge.
- Agents produce structured fields. The graph computes the verdict.
- Output must be explainable enough for a committee, QAPI/quality review group, governance committee, or risk reviewer.
- Every run must emit a reconstructable receipt.

## Folder map

```text
sentinel_codex_handoff/
  .env.example
  .gitignore
  GOAL.md
  README.md
  DECISIONS.md
  PROGRESS.md
  REPO_MAP.md
  RISK_NOTES.md
  pyproject.toml
  data/
    constructed_inputs/
      constructed_demo_case.txt
    cases/
      invalid_missing_timepoint_case.json
      valid_ai_weak_fact_case.json
      valid_home_plan_feasibility_case.json
      valid_limited_added_value_case.json
      valid_low_value_gap_suppression_case.json
      valid_material_gap_case.json
      valid_therapy_improvement_case.json
      valid_therapy_not_considered_case.json
    static_inputs/
      static_inputs.json
      invalid_final_verdict_role.json
      invalid_unknown_node_target.json
    receipts/
      json/
      markdown/
    prepared_inputs/
      constructed_demo_case/
        analysis/
          receipts/
          review.html
        approval_manifest.json
        approval_trace.json
        approved_episode.json
        draft_episode.json
        redacted_input.txt
        redaction_report.json
    workbench/
      index.html
  docs/
    00_hard_decisions.md
    01_existing_needs_and_problem_fit.md
    02_product_definition.md
    03_methodology_prudence_calculus.md
    04_architecture.md
    05_agent_to_node_conversion.md
    06_contrarian_view_and_mitigations.md
    07_requirements.md
    08_user_stories.md
    09_ui_workbench_spec.md
    10_api_contract.md
    11_data_model_notes.md
    12_security_privacy_governance.md
    13_kill_criteria.md
    14_glossary.md
    15_codex_build_epics.md
    16_repo_structure_and_work_packages.md
    17_model_and_framework_strategy.md
    18_deterministic_poc_status.md
    19_repository_publishing.md
    21_goal_completion_audit.md
  roadmaps/
    01_short_term_poc_roadmap.md
    02_long_term_roadmap_after_poc.md
    03_decision_tree_after_poc_results.md
    04_phase_0_ed_disposition_implementation_plan.md
  validation/
    01_metrics_and_evaluation_plan.md
    02_case_replay_validation_plan.md
    03_human_review_panel_plan.md
    reports/
      latest.json
  schemas/
    decision_episode.schema.json
    ed_decision_episode.schema.json
    role_assessment.schema.json
    evidenceflow_result.schema.json
    sentinel_receipt.schema.json
    approval_manifest.schema.json
    approval_trace.schema.json
    ed_sentinel_receipt.schema.json
    ensemble_contribution.schema.json
    node_audit.schema.json
    redaction_report.schema.json
    static_role_assessment.schema.json
    static_evidenceflow_result.schema.json
    static_input_bundle.schema.json
  src/
    sentinel_workbench/
      approval.py
      ensemble.py
      demo_run.py
      models.py
      case_library.py
      constructed_intake.py
      graph.py
      loader.py
      node_audit.py
      replay.py
      redaction.py
      receipts.py
      safety.py
      schema_export.py
      static_inputs.py
      validate.py
      evaluate.py
      workbench.py
      local_app.py
  tests/
    test_phase1_models.py
    test_phase2_case_library.py
    test_phase3_prudence_graph.py
    test_phase3_evaluation_report.py
    test_phase4_static_inputs.py
    test_phase6_receipts.py
    test_phase7_workbench.py
    test_phase_b_constructed_intake.py
    test_phase_c_reviewer_approval.py
    test_phase_d_node_audit.py
    test_phase_e_ensemble_contributions.py
    test_phase_g_local_demo_app.py
    test_full_poc_documentation.py
  prompts/
    01_role_agent_prompt_contracts.md
    02_evidenceflow_prompt_contracts.md
    03_synthesizer_prompt_contract.md
  examples/
    01_synthetic_case_templates.md
    02_minimal_poc_case_set.md
    03_sample_receipt_shape.md
```

## Recommended first Codex task

Ask Codex to read `GOAL.md`, this README, `DECISIONS.md`, `PROGRESS.md`, `REPO_MAP.md`, `RISK_NOTES.md`, `docs/20_emex_admsve_reuse_evaluation.md`, and the JSON schemas. Then continue from an end-to-end proof-of-done audit against `GOAL.md`, using the current CLI, local app, receipts, workbench, and validation-report artifacts as the safety baseline.

## Constructed input preparation

The first Phase B command prepares constructed or governance-approved deidentified text for reviewer-controlled analysis:

```bash
PYTHONPATH=src python3 -m sentinel_workbench.constructed_intake \
  --input data/constructed_inputs/constructed_demo_case.txt \
  --out data/prepared_inputs/constructed_demo_case \
  --episode-id constructed_demo_case \
  --title "Constructed demo case"
```

The command writes:

- `redacted_input.txt`
- `redaction_report.json`
- `draft_episode.json`

The draft episode is not yet a reviewer-approved analysis input. It is an editable structured artifact that must be reviewed before the graph run.

## Reviewer approval

Phase C adds an artifact gate for prepared constructed input:

```bash
PYTHONPATH=src python3 -m sentinel_workbench.approval \
  --prepared-dir data/prepared_inputs/constructed_demo_case \
  --reviewer-id reviewer_demo \
  --approval-note "Demo structured episode reviewed for local deterministic workflow."

PYTHONPATH=src python3 -m sentinel_workbench.approval \
  --validate-approved data/prepared_inputs/constructed_demo_case
```

Approval writes:

- `approved_episode.json`
- `approval_manifest.json`
- `approval_trace.json`

`load_approved_episode()` refuses direct draft JSON paths. Constructed input must pass through this approval artifact gate before later analysis commands should treat it as analysis-ready.

## Approved demo run

Phase G adds an approved-run command for a prepared constructed input:

```bash
PYTHONPATH=src python3 -m sentinel_workbench.demo_run \
  --prepared-dir data/prepared_inputs/constructed_demo_case \
  --static-inputs data/static_inputs/static_inputs.json \
  --out data/prepared_inputs/constructed_demo_case/analysis
```

The command validates approval artifacts, runs deterministic Sentinel analysis, and writes:

- `analysis/receipts/json/receipt_constructed_demo_case_T3_deterministic.json`
- `analysis/receipts/markdown/receipt_constructed_demo_case_T3_deterministic.md`
- `analysis/review.html`

The constructed-demo receipt includes redaction and approval trace hashes without copying raw input text into the review artifacts. Receipts also persist the selected review question, clinician-facing governance summary, and a deeper-dive artifact index covering human summary sections, node audit, ensemble contribution, methodology summary, and workflow artifacts.

## Local demo app

The first app-like surface uses Python stdlib only:

```bash
PYTHONPATH=src python3 -m sentinel_workbench.local_app --host 127.0.0.1 --port 8765
```

Then open:

```text
http://127.0.0.1:8765
```

The local app now starts with the staged reviewer flow from `GOAL.md`: choose either Disposition Information Sufficiency or AI Response Use Sufficiency, paste constructed/deidentified-style text or upload a local text file, click `Pre-process`, review Node Audit Methodology and Ensemble Contributions, choose `OK`, `Adjust`, or `Re-check Selected Nodes`, confirm any methodology-changing checkpoint, click `Process`, then read a clinician-facing summary before opening the deeper-dive artifacts. The default app workspace is `.sentinel_local_demo/`, which is gitignored.

Adjustment and re-check checkpoints are saved separately from generated facts in `node_audit_review_manifest.json`. The deterministic graph remains the final posture authority.

## OpenRouter model comparison

The OpenRouter integration is an implemented comparison harness, not app authority. Deterministic Sentinel remains the authority; comparison-only model artifacts are saved locally for review and are not used as final graph judgment.

Current boundary:

- implemented comparison harness: `sentinel_workbench.openrouter_compare`,
- comparison-only model artifacts: written under gitignored `artifacts/model_comparison/`,
- app-integrated LLM mode remains deferred,
- formal model-swap evaluation remains deferred.

Configure local `.env` values without committing secrets:

```text
OPENROUTER_API_KEY=...
MODEL_1=...
MODEL_2=...
```

Run the limited constructed challenge case:

```bash
PYTHONPATH=src python3 -m sentinel_workbench.openrouter_compare \
  --input data/model_comparison/challenging_constructed_case.txt \
  --out artifacts/model_comparison/challenging_case \
  --review-question disposition_information_sufficiency
```

The report is written to `artifacts/model_comparison/challenging_case/comparison_report.md`. The `artifacts/` directory is gitignored because it can contain raw model responses.

## Validation report coverage

`validation/reports/latest.json` now includes explicit proof payloads for:

- `redaction_gating`
- `node_audit_completeness`
- `ensemble_contribution_completeness`
- `receipt_completeness`
- `workbench_completeness`
- `local_app_completeness`

`receipt_completeness` now checks generated JSON and Markdown receipts for clinician summaries, selected-review-question support, and deeper-dive artifact sections. These are in addition to schema validity, future leakage, expected posture agreement, lane coverage, fixture category checks, static input validation, and forbidden phrase checks.

## Node audit methodology

Phase D adds schema-backed node methodology objects for every current graph metric:

- `NodeDefinition`
- `NodeEvidence`
- `NodeEstimate`
- `EnsembleContribution`
- `NodeAudit`

`validation/reports/latest.json` now includes `node_audit_completeness`. The current deterministic node audits expose dependencies, evidence refs, value, range, median, distribution kind, confidence, method, and sensitivity notes. Receipts and the static workbench now render these audit details directly.

## Ensemble contribution normalization

Phase E normalizes static role and EvidenceFlow inputs into bounded `EnsembleContribution` records. Contributions are accepted or downgraded with reasons when they map to deterministic graph nodes. Static targets outside the graph are rejected with reasons and tracked separately.

`validation/reports/latest.json` now includes `ensemble_contribution_completeness`. The graph still computes final posture; static roles and EvidenceFlows remain inspectable structured inputs.

## Transparent receipts and workbench

Phase F renders the trust layer directly into reviewer artifacts:

- JSON receipts include `node_audit_bundle`, `ensemble_contribution_bundle`, and `methodology_summary`.
- Markdown receipts include node methodology, dependent inputs, ranges, medians, distributions, evidence refs, sensitivity notes, accepted/downgraded contributions, and rejected ensemble inputs.
- The static workbench includes `node-audit-methodology` and `ensemble-contribution-panel` sections for every synthetic case.

The generated static workbench remains offline at `data/workbench/index.html`.

## Current local verification

```bash
python3 -m pytest -q
PYTHONPATH=src python3 -m sentinel_workbench.validate data/cases
PYTHONPATH=src python3 -m sentinel_workbench.static_inputs --static-inputs data/static_inputs/static_inputs.json --case-dir data/cases
PYTHONPATH=src python3 -m sentinel_workbench.constructed_intake --input data/constructed_inputs/constructed_demo_case.txt --out data/prepared_inputs/constructed_demo_case --episode-id constructed_demo_case --title "Constructed demo case"
PYTHONPATH=src python3 -m sentinel_workbench.approval --prepared-dir data/prepared_inputs/constructed_demo_case --reviewer-id reviewer_demo --approval-note "Demo structured episode reviewed for local deterministic workflow."
PYTHONPATH=src python3 -m sentinel_workbench.approval --validate-approved data/prepared_inputs/constructed_demo_case
PYTHONPATH=src python3 -m sentinel_workbench.demo_run --prepared-dir data/prepared_inputs/constructed_demo_case --static-inputs data/static_inputs/static_inputs.json --out data/prepared_inputs/constructed_demo_case/analysis --review-question disposition_information_sufficiency
PYTHONPATH=src python3 -m sentinel_workbench.receipts --case-dir data/cases --static-inputs data/static_inputs/static_inputs.json --out data/receipts
PYTHONPATH=src python3 -m sentinel_workbench.schema_export schemas/ed_decision_episode.schema.json
PYTHONPATH=src python3 -m sentinel_workbench.evaluate --case-dir data/cases --out validation/reports/latest.json --receipt-dir data/receipts
PYTHONPATH=src python3 -m sentinel_workbench.workbench --case-dir data/cases --receipt-dir data/receipts --report validation/reports/latest.json --out data/workbench/index.html
PYTHONPATH=src python3 -m sentinel_workbench.ux_verification
PYTHONPATH=src python3 -m sentinel_workbench.final_verification
PYTHONPATH=src python3 -m sentinel_workbench.goal_audit --out-json validation/reports/goal_completion_audit.json --out-markdown docs/21_goal_completion_audit.md
PYTHONPATH=src python3 -m sentinel_workbench.local_app --host 127.0.0.1 --port 8765
python3 -m pip install -e . --dry-run --no-deps
```

The generated reviewer workbench is a static offline file at `data/workbench/index.html`.

Implemented/deferred boundaries and requirements before real clinical, prospective, or production use are summarized in `docs/18_deterministic_poc_status.md`.

Repository publishing notes are in `docs/19_repository_publishing.md`.

The requirement-by-requirement transparent-demo completion audit is saved in `docs/21_goal_completion_audit.md`, with machine-readable output in `validation/reports/goal_completion_audit.json`.

The prior clinician-facing staged-demo audit reached 25/25 and is evidenced by `validation/reports/final_verification.json`. The current audit now maps the completeness-scan remediation `GOAL.md` and supersedes the prior 25-item milestone audit.
