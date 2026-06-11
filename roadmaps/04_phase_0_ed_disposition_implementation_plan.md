# 04 - Phase 0 ED Disposition Replay Implementation Plan

Date: 2026-06-11

Status: Phase 0 scope-lock artifact. No clinical recommendation logic is implemented here.

## Purpose

This plan narrows the existing Sentinel Governance Workbench handoff into the first POC wedge: local, synthetic Emergency Department disposition replay. The workbench evaluates whether the decision posture was warranted at the point of disposition using only the facts available at that timepoint.

Sentinel remains a governance and review workbench. It must not issue admission, discharge, diagnosis, treatment, ordering, prescribing, or clearance instructions.

## Discovery Evidence

Phase 0 inspection covered the required target artifacts:

- `README.md`
- `docs/*.md`
- `schemas/*.json`
- `prompts/*.md`
- `validation/*.md`
- `examples/*.md`
- `roadmaps/*.md`

Reference-only inputs inspected:

- `../OE_dotflows.md`
- `../OE_dotflows2.md`
- selected workbench and verification patterns from `../finESS`
- selected fail-closed receipt, trace, and safety-boundary patterns from `../clinclaw-firewall`

The reference repos were not modified.

## Phase Alignment

Existing handoff docs are useful but broad. Phase 0 adds the ED-specific delta needed before Phase 1 project skeleton work.

Use this file as the bridge between:

- the generic product handoff in `docs/`,
- the broad milestone plan in `roadmaps/01_short_term_poc_roadmap.md`,
- the full ED disposition replay proof surface in `GOAL.md`.

## Data Model Delta

Phase 1 schemas should extend the current generic `DecisionEpisode` model with ED disposition replay fields.

### DecisionEpisode

Add or require these POC-level fields:

- `domain`: fixed to `emergency_department_disposition_replay` for the first POC.
- `decision_point_type`: one of `admission_vs_non_inpatient_alternative`, `observation_vs_home_plan`, `continued_ed_management_vs_disposition`, or `other_ed_disposition_review`.
- `case_syntheticity`: fixed to `synthetic` or `deidentified_style_synthetic`.
- `governance_question`: plain-language statement of the warrant question.
- `forbidden_use_notice`: explicit local-review-only warning.

### TimelineState

Require these timepoints for every full POC case:

- `T0_triage`
- `T1_initial_workup`
- `T2_post_treatment_reassessment`
- `T3_disposition_decision`
- optional hidden `T4_follow_up_or_outcome`

At each timepoint, separate:

- `available_facts`
- `pending_information`
- `information_gaps`
- `offered_therapies`
- `therapy_response_observations`
- `proposed_disposition_posture_under_review`
- `hidden_future_facts`

The replay service must expose only facts at or before the selected timepoint. `T4_follow_up_or_outcome` is allowed only for retrospective evaluation labels and must be blocked from graph inputs.

### Proposed Disposition Posture Under Review

Replace generic action framing with a neutral review object:

- `posture_under_review_id`
- `stated_plan_category`: `hospital_based_monitoring_or_treatment`, `non_inpatient_plan`, `observation_or_recheck_plan`, `defer_pending_information`, or `unclear`
- `assertiveness`
- `source_actor`
- `rationale_available_at_time`
- `known_constraints`

This object is not Sentinel's output. It is the decision posture being reviewed.

### Offered Therapy And Response

Add first-class therapy fields:

- `therapy_id`
- `therapy_category`
- `offered_at_timepoint`
- `accepted_or_received`: `yes`, `no`, `partial`, or `unknown`
- `response_observed`: `improved`, `no_clear_change`, `worse`, `not_reassessed`, or `unknown`
- `response_timepoint`
- `response_source_refs`
- `response_reliability`
- `therapy_plausibly_indicated_but_not_considered`: boolean
- `not_considered_rationale`

Do not infer effectiveness thresholds. Unknown response remains unknown.

### Follow-Up Reliability And Home-Plan Feasibility

Represent feasibility as governance context, not advice:

- `follow_up_access`: `clear`, `unclear`, `limited`, or `unknown`
- `home_support`: `clear`, `unclear`, `limited`, or `unknown`
- `return_access`: `clear`, `unclear`, `limited`, or `unknown`
- `barrier_facts`
- `barrier_source_refs`
- `barrier_reliability`

### Expected Evaluation Labels

Synthetic fixtures should include expected labels used only by tests:

- `expected_final_posture`
- `expected_material_gaps`
- `expected_omission_flags`
- `expected_commission_flags`
- `expected_therapy_response_flags`
- `expected_next_best_information`
- `expected_future_leakage_blocked`

## Required Synthetic Case Set

The full POC case library must cover at least these seven patterns:

1. Material missing input before disposition.
2. Therapy offered with documented improvement.
3. Therapy offered with nonresponse or unclear response.
4. Therapy plausibly indicated but not considered.
5. Discharge or home-plan feasibility problem.
6. Admission or observation with limited added value.
7. AI-derived or weakly sourced fact driving the decision.

Each case must use synthetic, deidentified-style details only and must avoid named clinical sites, employers, institutions, real patients, credentials, private keys, and proprietary data.

## Node Groups

Phase 3 and Phase 5 should treat the following as first-class node groups.

### Information State Nodes

- `information_sufficiency`
- `material_gap_strength`
- `gap_knowability`
- `gap_burden`
- `next_best_information_rank`

### Time And Recoverability Nodes

- `harm_clock`
- `information_clock`
- `recoverability`
- `future_correction_opportunity`
- `decision_weight`

### AI Provenance Nodes

- `ai_provenance_risk`
- `unknown_provenance_risk`
- `unsupported_claim_strength`
- `weak_source_dependency`

### Therapy Response Nodes

- `therapy_offered_relevance`
- `therapy_response_observed`
- `therapy_nonresponse_relevance`
- `therapy_not_reassessed_risk`
- `plausibly_indicated_therapy_not_considered`

### Omission Lane

Omission nodes capture review concerns about missing evaluation, missing reassessment, missing feasibility information, or unsupported reliance on unknowns:

- `omission_material_gap`
- `omission_unassessed_response`
- `omission_home_plan_feasibility_gap`
- `omission_ai_fact_verification_gap`
- `omission_follow_up_reliability_gap`

### Commission Lane

Commission nodes capture review concerns that the posture under review may add low-value burden, unnecessary escalation, avoidable resource use, or unsupported downstream action:

- `commission_added_burden`
- `commission_low_added_value`
- `commission_unverified_driver`
- `commission_overconfident_posture`
- `commission_alternative_not_compared`

The graph should preserve commission and omission lanes separately in receipts. A case may have both.

## Preventability-Opportunity Proxy Metrics

Do not report clinical harm prevention. Report only proxy opportunity metrics:

- `material_gap_strength`
- `probability_gap_changes_posture`
- `time_to_obtain_hours`
- `burden`
- `harm_clock`
- `information_clock`
- `recoverability`
- `future_correction_opportunity`
- `source_reliability`
- `therapy_response_relevance`

Initial deterministic proxy:

```text
preventability_opportunity =
  material_gap_strength
  * probability_gap_changes_posture
  * decision_weight
  * recoverability_modifier
  * information_clock_modifier
  * burden_modifier
```

All modifiers must be documented, bounded, and visible in the graph inspector. Unknown inputs must lower confidence instead of being converted to favorable assumptions.

## Prompt And Dotflow Registry Shape

Borrow the section discipline from `../OE_dotflows.md` but convert each prompt or dotflow into a versioned contract. Do not let a prompt decide final posture.

Registry fields:

- `contract_id`
- `version`
- `contract_type`: `role_prompt`, `evidenceflow`, `normalizer`, or `renderer`
- `domain`
- `allowed_timepoints`
- `allowed_inputs`
- `forbidden_inputs`
- `required_output_schema`
- `allowed_node_targets`
- `forbidden_output_claims`
- `fixture_coverage`
- `expected_failure_cases`
- `changelog`

Initial contracts:

- `ed_role_prudent_layperson_v0`
- `ed_role_prudent_provider_v0`
- `ed_role_prudent_healthcare_ai_v0`
- `ed_role_duty_to_inquire_v0`
- `ed_role_risk_horizon_v0`
- `ed_evidenceflow_admission_non_inpatient_comparison_v0`
- `ed_evidenceflow_next_best_information_v0`
- `ed_evidenceflow_therapy_response_v0`
- `ed_evidenceflow_home_plan_feasibility_v0`
- `ed_normalizer_node_mapper_v0`

Each contract must reject hidden future facts, generic advice, final disposition orders, and unsupported claims.

## Receipt Requirements

Every deterministic run must emit a machine-readable receipt and a human-readable Markdown or HTML receipt.

Machine-readable receipt fields:

- `receipt_id`
- `episode_id`
- `timepoint_id`
- `run_id`
- `mode`
- `input_hashes`
- `prompt_or_dotflow_versions`
- `model_versions`
- `evidence_versions`
- `graph_version`
- `node_library_version`
- `available_fact_ids`
- `blocked_future_fact_ids`
- `node_values`
- `rejected_or_downgraded_findings`
- `role_disagreement_map`
- `commission_lane`
- `omission_lane`
- `therapy_response_lane`
- `next_best_information_ranking`
- `preventability_opportunity_score`
- `preventability_opportunity_explanation`
- `final_posture`
- `decision_weight`
- `signature_placeholder`

Human-readable receipt sections:

- What was known at the timepoint.
- What was missing or weakly sourced.
- What would have changed the discussion.
- What hospital-based monitoring or treatment might add.
- What non-inpatient alternatives might add.
- Commission concerns.
- Omission concerns.
- Therapy-response concerns.
- Why the graph selected the posture.
- What was rejected, downgraded, or blocked as future leakage.

Use neutral governance language. Do not include disposition recommendation phrases.

## Validation And Test Strategy

Phase 1 should start with validation tests before implementation code.

Minimum automated checks:

- JSON schema validity for cases, role outputs, EvidenceFlow outputs, and receipts.
- Fixture loader rejects malformed cases clearly.
- Required timepoints are present.
- `T4_follow_up_or_outcome` facts are blocked from `T0` through `T3` evaluation.
- Static role outputs validate before optional LLM mode exists.
- Static EvidenceFlow outputs validate before optional LLM mode exists.
- Commission lane appears in graph node output.
- Omission lane appears in graph node output.
- Therapy-response lane appears in graph node output.
- Preventability-opportunity score is bounded and explainable.
- Expected posture labels are used only for tests and reports, not graph inputs.
- Receipts include required hashes, versions, node values, downgraded findings, and signature placeholder.
- Forbidden phrase scanner fails on prohibited disposition language outside explicit safety-rule lists.
- Secret and PHI-pattern scanner reports no hits in fixtures, docs, prompts, schemas, generated receipts, or tests.

Recommended command shape after Phase 1 skeleton exists:

```bash
python -m pytest
python -m sentinel_workbench.validate data/cases
python -m sentinel_workbench.evaluate --mode deterministic --out validation/reports/latest.json
git diff --check
```

## Phase Sequence

1. Phase 1: project skeleton, Pydantic models, schema export, fixture loader, validation utilities, `.env.example`.
2. Phase 2: seven synthetic ED replay cases, required timepoints, hidden-future-fact guard.
3. Phase 3: information state, therapy response, commission, omission, and preventability-opportunity nodes.
4. Phase 4: static prompt/dotflow registry, static role outputs, static EvidenceFlow outputs, schema rejection rules.
5. Phase 5: node normalizer, deterministic prudence graph, final posture and decision weight.
6. Phase 6: JSON and human-readable receipts, evaluation report, forbidden phrase checks.
7. Phase 7: governance reviewer workbench UI.
8. Phase 8: optional LLM prompt mode and model-swap evaluation only after deterministic path passes.

## Non-Scope For The First POC

- Real clinical data or PHI.
- Named hospitals, health systems, clinics, employers, or institutions.
- Live evidence retrieval.
- OpenEvidence API integration.
- Bedside alerts.
- Patient-facing advice.
- Disposition, diagnosis, prescription, order, or clearance recommendations.
- Production deployment.
- Regulatory, clinical safety, or outcome-improvement claims.

## Safe Next Step

Proceed to Phase 1 only after this Phase 0 plan, `REPO_MAP.md`, `RISK_NOTES.md`, and `PROGRESS.md` are present and verification confirms that the target folder remains synthetic, local, and institution-neutral.
