# 15 — Codex Build Epics

This document converts the POC roadmap into Codex-ready epics and tasks. Codex should implement one epic at a time and run tests after each epic.

## Epic 1 — Repository skeleton

### Goal

Create a clean POC repository structure.

### Tasks

- Create Python project skeleton.
- Add package directory `sentinel_workbench`.
- Add `tests/` directory.
- Add `data/cases/` for synthetic case fixtures.
- Add `data/evidenceflows/` for static POC EvidenceFlow results.
- Add `data/receipts/` for generated receipts.
- Add `docs/` directory in repo with copied methodology docs.
- Add `.env.example` but no secrets.
- Add basic README with POC warning.

### Acceptance criteria

- Project installs locally.
- Test runner works.
- No named clinical site appears anywhere.

## Epic 2 — Pydantic data models

### Goal

Implement schemas as Pydantic models.

### Tasks

- Implement DecisionEpisode models.
- Implement RoleAssessment model.
- Implement EvidenceFlowResult model.
- Implement SentinelReceipt model.
- Export JSON schemas.
- Add validation tests.

### Acceptance criteria

- Valid sample cases pass.
- Invalid cases fail with clear errors.
- JSON schemas match planning files.

## Epic 3 — Case replay engine

### Goal

Load and evaluate synthetic cases one timepoint at a time.

### Tasks

- Implement case loader.
- Implement timepoint selector.
- Implement hidden future fact guard.
- Implement replay service.

### Acceptance criteria

- Future facts are not visible during current-time run.
- Test confirms future leakage prevention.

## Epic 4 — Information partition and provenance service

### Goal

Classify facts and compute AI-provenance depth.

### Tasks

- Implement information bucket classifier.
- Implement provenance depth calculator.
- Implement known-but-weak downgrade logic.
- Add warnings for unverified AI-derived decision-critical facts.

### Acceptance criteria

- Synthetic case provenance warnings match expected outputs.
- Unknown provenance is not treated as verified.

## Epic 5 — Static EvidenceFlow engine

### Goal

Load static/manual EvidenceFlow outputs for POC.

### Tasks

- Implement EvidenceFlow loader.
- Validate EvidenceFlowResult schema.
- Attach EvidenceFlow results to timepoints.
- Support next-best-input candidate table.

### Acceptance criteria

- Each POC case has structured candidate inputs.
- Generic or missing candidate fields fail validation.

## Epic 6 — Role-agent service

### Goal

Support role outputs in stub/static mode first, then optional LLM mode.

### Tasks

- Implement role contract registry.
- Implement static role assessment loader.
- Implement schema validation.
- Implement optional LLM adapter behind interface.
- Add retry/reject flow for malformed outputs.

### Acceptance criteria

- Static role outputs run for all POC cases.
- Invalid role outputs are rejected.
- LLM mode can be disabled entirely.

## Epic 7 — Node normalizer

### Goal

Convert role and EvidenceFlow outputs into graph nodes.

### Tasks

- Implement finding-type to node mapping.
- Implement confidence normalization.
- Implement evidence tier weights.
- Implement unsupported finding downgrade.
- Implement disagreement map creation.

### Acceptance criteria

- Same node inputs yield same graph results.
- Unsupported findings cannot dominate final posture.
- Disagreements appear in receipt.

## Epic 8 — Prudence graph v0.1

### Goal

Compute decision warrant posture.

### Tasks

- Implement graph nodes:
  - information_sufficiency,
  - material_gap_strength,
  - harm_clock,
  - information_clock,
  - recoverability,
  - future_correction_opportunity,
  - decision_weight,
  - ai_provenance_risk,
  - next_best_input_rank,
  - final_posture.
- Implement deterministic scoring first.
- Add optional Monte Carlo mode later.
- Add sensitivity inspection.

### Acceptance criteria

- All cases produce expected posture category or documented disagreement.
- Decision weight responds correctly to harm/information clocks.
- Low decision weight suppresses unnecessary high-burden input gathering.

## Epic 9 — Receipt service

### Goal

Create reconstructable JSON and human-readable receipts.

### Tasks

- Implement receipt builder.
- Add input hashing.
- Add version fields.
- Add HMAC placeholder signing.
- Add Markdown summary export.
- Add receipt reload.

### Acceptance criteria

- Every run emits valid receipt.
- Receipt is reloadable and displayed in UI.
- Receipt includes graph and prompt/model/evidence versions.

## Epic 10 — Workbench UI

### Goal

Make the methodology inspectable.

### Tasks

- Build case library page.
- Build timeline page.
- Build gap map page.
- Build provenance panel.
- Build two-clock panel.
- Build next-best-input panel.
- Build role disagreement panel.
- Build graph inspector.
- Build receipt viewer.

### Acceptance criteria

- Non-developer reviewer can inspect a case.
- Export works.
- POC warning visible.

## Epic 11 — Evaluation harness

### Goal

Measure POC performance.

### Tasks

- Implement golden expected outputs.
- Implement metric runner.
- Implement model-swap placeholder.
- Implement role ablation placeholder.
- Generate evaluation report.

### Acceptance criteria

- Evaluation report created.
- Metrics include schema validity, leakage, gap detection, next-best-input actionability, receipt completeness.

## Epic 12 — POC demo package

### Goal

Prepare final demo artifacts.

### Tasks

- Add 5 cases.
- Add demo script.
- Add sample receipts.
- Add evaluation report.
- Add stakeholder feedback form.

### Acceptance criteria

- Demo can run locally from clean install.
- No live data required.
- No named institution appears.
