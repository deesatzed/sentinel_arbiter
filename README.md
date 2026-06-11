# Sentinel Governance Workbench — Codex Handoff Package

Version: 0.1
Date: 2026-06-11
Status: Deterministic ED replay POC with static reviewer workbench and status boundary. No production clinical use implied.

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
    ed_sentinel_receipt.schema.json
    static_role_assessment.schema.json
    static_evidenceflow_result.schema.json
    static_input_bundle.schema.json
  src/
    sentinel_workbench/
      models.py
      case_library.py
      graph.py
      loader.py
      replay.py
      receipts.py
      safety.py
      schema_export.py
      static_inputs.py
      validate.py
      evaluate.py
      workbench.py
  tests/
    test_phase1_models.py
    test_phase2_case_library.py
    test_phase3_prudence_graph.py
    test_phase3_evaluation_report.py
    test_phase4_static_inputs.py
    test_phase6_receipts.py
    test_phase7_workbench.py
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

Ask Codex to read `GOAL.md`, this README, `DECISIONS.md`, `PROGRESS.md`, `REPO_MAP.md`, `RISK_NOTES.md`, `docs/00_hard_decisions.md`, `roadmaps/01_short_term_poc_roadmap.md`, `roadmaps/04_phase_0_ed_disposition_implementation_plan.md`, `docs/03_methodology_prudence_calculus.md`, `docs/05_agent_to_node_conversion.md`, and the JSON schemas. Then start Phase 1 with schema and fixture tests before writing graph or clinical logic.

## Current local verification

```bash
python3 -m pytest -q
PYTHONPATH=src python3 -m sentinel_workbench.validate data/cases
PYTHONPATH=src python3 -m sentinel_workbench.static_inputs --static-inputs data/static_inputs/static_inputs.json --case-dir data/cases
PYTHONPATH=src python3 -m sentinel_workbench.receipts --case-dir data/cases --static-inputs data/static_inputs/static_inputs.json --out data/receipts
PYTHONPATH=src python3 -m sentinel_workbench.schema_export schemas/ed_decision_episode.schema.json
PYTHONPATH=src python3 -m sentinel_workbench.evaluate --case-dir data/cases --out validation/reports/latest.json --receipt-dir data/receipts
PYTHONPATH=src python3 -m sentinel_workbench.workbench --case-dir data/cases --receipt-dir data/receipts --report validation/reports/latest.json --out data/workbench/index.html
python3 -m pip install -e . --dry-run --no-deps
```

The generated reviewer workbench is a static offline file at `data/workbench/index.html`.

Implemented/deferred boundaries and requirements before real clinical, prospective, or production use are summarized in `docs/18_deterministic_poc_status.md`.

Repository publishing notes are in `docs/19_repository_publishing.md`.
