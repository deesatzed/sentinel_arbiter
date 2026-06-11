# DECISIONS.md

## Decision 2026-06-11-01 - Preserve Sentinel As Governance Workbench

Sentinel's first POC remains a governance and review workbench for ED disposition replay. It does not make admission, discharge, diagnosis, prescribing, ordering, clearance, or patient-facing treatment recommendations.

Reason: This preserves the safety boundary in `GOAL.md` and keeps the POC aligned with committee-ready warrant review rather than bedside decision automation.

## Decision 2026-06-11-02 - Use Additive ED-Specific Scope Lock

The existing broad Sentinel docs remain in place. The ED disposition replay delta is added in `roadmaps/04_phase_0_ed_disposition_implementation_plan.md` instead of rewriting the whole handoff.

Reason: The current package contains useful architecture, prompt, schema, and validation planning, but it is broader than the new ED disposition wedge. An additive Phase 0 plan reduces drift without destroying useful context.

## Decision 2026-06-11-03 - Static Deterministic Path Before LLM Mode

Phase 1 through Phase 6 must support static fixtures and deterministic validation before optional LLM prompt mode is enabled.

Reason: The goal requires schema validation, future-leakage prevention, receipt completeness, and graph judgment before live prompt execution or model-swap experiments.

## Decision 2026-06-11-04 - Commission, Omission, And Therapy Response Are First-Class

Commission concerns, omission concerns, and therapy-response concerns must be represented as distinct node groups and receipt sections.

Reason: The ED disposition replay POC explicitly evaluates omission risk, commission risk, therapy response, and preventability opportunity. Collapsing these into a single uncertainty score would weaken the method.

## Decision 2026-06-11-05 - Use Pydantic 2 For Phase 1 Models

Phase 1 uses a minimal Python package with Pydantic 2 models, pytest tests, static JSON fixtures, and local module commands for schema export and validation.

Reason: Pydantic is already available locally, exports JSON Schema cleanly, and keeps the deterministic path offline without adding a heavier framework before the graph and receipt methodology are proven.

## Decision 2026-06-11-06 - Make Synthetic Case Coverage Machine-Checkable

Each ED fixture declares `covered_case_patterns` in expected-output metadata, and the case-library validator checks that all seven GOAL.md patterns are covered.

Reason: Machine-checkable coverage prevents the POC from relying on filename or prose interpretation and makes it harder to accidentally lose a required synthetic scenario during later edits.

## Decision 2026-06-11-07 - Keep Phase 3 Graph Deterministic And Fixture-Field-Based

The first graph computes bounded node values from structured synthetic fixture fields, not from prompt prose, hidden outcome labels, or clinical evidence assumptions.

Reason: This satisfies the local deterministic path and lets tests arbitrate lane behavior before adding role outputs, EvidenceFlows, receipts, or optional LLM mode.

## Decision 2026-06-11-08 - Use Static Templates Before Per-Case Prompt Runs

Phase 4 validates static role-output and EvidenceFlow templates that expand over every synthetic case before any LLM-backed role execution exists.

Reason: This proves schema, node-target, forbidden-language, and current-time constraints without paying the duplication cost of hand-writing every per-role/per-case output before receipt rendering and role-disagreement handling exist.

## Decision 2026-06-11-09 - Emit Unsigned Deterministic POC Receipts First

Phase 6 receipts are reconstructable JSON plus Markdown review artifacts with `UNSIGNED_DETERMINISTIC_POC` placeholders, not cryptographic production signatures.

Reason: The POC needs auditable receipts before UI and optional LLM mode, but production signing, key management, and deployment controls are intentionally out of scope for the deterministic local milestone.

## Decision 2026-06-11-10 - Generate A Static Offline Reviewer Workbench First

Phase 7 uses a generated `data/workbench/index.html` file rather than a live web server or frontend framework.

Reason: The deterministic POC needs a reviewer-inspectable surface with no external services. A static artifact can expose the case library, replay panels, graph nodes, evaluation dashboard, and receipt export links while preserving the local/offline safety boundary.

## Decision 2026-06-11-11 - Keep Pre-Real-Use Boundaries In A Checked Status Document

The implemented/deferred boundary and requirements before real clinical, prospective, or production use are recorded in `docs/18_deterministic_poc_status.md` and checked by tests.

Reason: `GOAL.md` requires the project to document what is implemented, what is deferred, and what would be required before any real clinical, prospective, or production use. Treating this as a tested artifact prevents the safety boundary from drifting into informal progress notes.
