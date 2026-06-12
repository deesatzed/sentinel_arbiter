# Sentinel Receipt - synthetic_ed_case_006

- Receipt ID: `receipt_synthetic_ed_case_006_T3_deterministic`
- Timepoint: `T3_disposition_decision`
- Final posture: `OBTAIN_SPECIFIC_INFORMATION_FIRST`
- Decision weight: `0.745`
- Selected Review Question: `Unspecified governance review question`
- Signature placeholder: `UNSIGNED_DETERMINISTIC_POC`

## Clinician Summary
For Unspecified governance review question, Sentinel found that the current review record still depends on unresolved or weakly supported information before a governance reviewer should trust the posture. The main driver is: AI-derived decision driver needs verification or downgrade. The most useful next review input is: verify or downgrade AI-derived driver This output is governance review support, not a clinical action recommendation.

## What Was Known
- At decision time, the weak AI-derived fact remains decision-critical and unverified.

## What Was Missing
- AI-derived decision driver needs verification or downgrade.

## What Would Have Changed The Discussion
- verify or downgrade AI-derived driver

## What Hospital-Based Monitoring Or Treatment Might Add
- The receipt records whether a hospital-based path had a specific monitoring, information, or therapy-response target in the current-time facts.

## What Non-Inpatient Alternatives Might Add
- The receipt records whether support, follow-up access, return access, and recheck feasibility were represented in the current-time facts.

## Commission Concerns
- commission_overconfident_posture
- commission_unverified_driver

## Omission Concerns
- omission_ai_fact_verification_gap

## Therapy-Response Concerns
- No therapy-response concern was raised by the deterministic graph.

## Why The Graph Selected The Posture
- The graph selected OBTAIN_SPECIFIC_INFORMATION_FIRST from bounded node values, with decision weight 0.745 and preventability opportunity 0.5984.

## Node Audit Methodology
- `information_sufficiency`: value `0.1`; Range `0.0` to `0.2`; Median `0.1`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `current_time_information_gaps`; Evidence refs `gap:c006_gap_ai_source`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `material_gap_strength`: value `0.9`; Range `0.8` to `1.0`; Median `0.9`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `current_time_information_gaps`; Evidence refs `gap:c006_gap_ai_source`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `harm_clock`: value `0.76`; Range `0.61` to `0.91`; Median `0.76`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `current_time_information_gaps, therapy_response, ai_provenance`; Evidence refs `gap:c006_gap_ai_source, fact:c006_ai_fact`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `information_clock`: value `0.9917`; Range `0.8917` to `1.0`; Median `0.9917`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `current_time_information_gaps`; Evidence refs `gap:c006_gap_ai_source`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `recoverability`: value `0.55`; Range `0.45` to `0.65`; Median `0.55`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `current_time_information_gaps, therapy_response`; Evidence refs `gap:c006_gap_ai_source`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `future_correction_opportunity`: value `0.35`; Range `0.2` to `0.5`; Median `0.35`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `follow_up_feasibility`; Evidence refs `follow_up:synthetic_ed_case_006:T3_disposition_decision`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `decision_weight`: value `0.745`; Range `0.595` to `0.895`; Median `0.745`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `current_time_information_gaps, therapy_response, ai_provenance`; Evidence refs `gap:c006_gap_ai_source, fact:c006_ai_fact`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `ai_provenance_risk`: value `0.9`; Range `0.75` to `1.0`; Median `0.9`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `available_facts`; Evidence refs `fact:c006_ai_fact`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `commission_risk`: value `0.9`; Range `0.75` to `1.0`; Median `0.9`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `proposed_posture, current_time_information_gaps, ai_provenance`; Evidence refs `gap:c006_gap_ai_source, fact:c006_ai_fact`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `omission_risk`: value `0.9`; Range `0.75` to `1.0`; Median `0.9`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `current_time_information_gaps, follow_up_feasibility, ai_provenance`; Evidence refs `gap:c006_gap_ai_source, fact:c006_ai_fact`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `therapy_response_relevance`: value `0.0`; Range `0.0` to `0.15`; Median `0.0`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `offered_therapies, therapy_response_observations`; Evidence refs `node:therapy_response_relevance:no_direct_evidence`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `next_best_information_rank`: value `1`; Range `0.0` to `2.0`; Median `1.0`; Distribution `deterministic_count_with_neighbor_range`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `current_time_information_gaps`; Evidence refs `gap:c006_gap_ai_source`; Sensitivity `Posture sensitivity depends on whether additional gaps cross the materiality threshold.`
- `preventability_opportunity_score`: value `0.5984`; Range `0.4984` to `0.6984`; Median `0.5984`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `material_gap_strength, decision_weight, information_clock, burden_modifier`; Evidence refs `gap:c006_gap_ai_source`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`

## Ensemble Contributions
- `prudent_provider` to `information_sufficiency`: proposed `0.5`; Range `0.4` to `0.6`; disposition `accepted`; reason `Accepted static role contribution at confidence 0.7.`; Evidence refs `T3_disposition_decision`
- `duty_to_inquire` to `information_clock`: proposed `0.75`; Range `0.65` to `0.85`; disposition `accepted`; reason `Accepted static role contribution at confidence 0.75.`; Evidence refs `T3_disposition_decision`
- `risk_horizon` to `harm_clock`: proposed `0.6`; Range `0.4` to `0.8`; disposition `accepted`; reason `Accepted static role contribution at confidence 0.65.`; Evidence refs `T3_disposition_decision`
- `risk_horizon` to `information_clock`: proposed `0.6`; Range `0.4` to `0.8`; disposition `accepted`; reason `Accepted static role contribution at confidence 0.65.`; Evidence refs `T3_disposition_decision`
- `risk_horizon` to `recoverability`: proposed `0.5`; Range `0.3` to `0.7`; disposition `accepted`; reason `Accepted static role contribution at confidence 0.65.`; Evidence refs `T3_disposition_decision`
- `risk_horizon` to `future_correction_opportunity`: proposed `0.4`; Range `0.2` to `0.6`; disposition `accepted`; reason `Accepted static role contribution at confidence 0.65.`; Evidence refs `T3_disposition_decision`
- `risk_horizon` to `decision_weight`: proposed `0.6`; Range `0.4` to `0.8`; disposition `accepted`; reason `Accepted static role contribution at confidence 0.65.`; Evidence refs `T3_disposition_decision`
- `defense` to `future_correction_opportunity`: proposed `0.4`; Range `0.2` to `0.6`; disposition `downgraded`; reason `Downgraded static role contribution because confidence 0.6 is below acceptance threshold.`; Evidence refs `T3_disposition_decision`
- `evidenceflow:guideline_dependency` to `material_gap_strength`: proposed `0.4`; Range `0.2` to `0.6`; disposition `accepted`; reason `Accepted EvidenceFlow contribution at confidence 0.65.`; Evidence refs `synthetic_fixture_current_time`
- `evidenceflow:next_best_input` to `next_best_information_rank`: proposed `1`; Range `0.0` to `2.0`; disposition `accepted`; reason `EvidenceFlow candidate normalized with expected posture shift 0.6.`; Evidence refs `synthetic_ed_case_006_candidate_input_001`
- `evidenceflow:next_best_input` to `preventability_opportunity_score`: proposed `0.5`; Range `0.35` to `0.65`; disposition `accepted`; reason `EvidenceFlow candidate normalized with preventability leverage 0.5.`; Evidence refs `synthetic_ed_case_006_candidate_input_001`
- `evidenceflow:high_risk_alternative` to `harm_clock`: proposed `0.5`; Range `0.3` to `0.7`; disposition `downgraded`; reason `Downgraded EvidenceFlow contribution because confidence 0.6 is below acceptance threshold.`; Evidence refs `synthetic_fixture_current_time`
- `evidenceflow:prudent_ai_conduct` to `ai_provenance_risk`: proposed `0.5`; Range `0.4` to `0.6`; disposition `accepted`; reason `Accepted EvidenceFlow contribution at confidence 0.75.`; Evidence refs `synthetic_fixture_current_time`

Rejected ensemble inputs:
- `prudent_layperson` target `prudent_layperson_threshold`: Target is not a deterministic graph node for Phase E normalization.
- `prudent_layperson` target `safety_net_need`: Target is not a deterministic graph node for Phase E normalization.
- `prudent_provider` target `prudent_provider_threshold`: Target is not a deterministic graph node for Phase E normalization.
- `prudent_provider` target `over_action_risk`: Target is not a deterministic graph node for Phase E normalization.
- `prudent_provider` target `under_action_risk`: Target is not a deterministic graph node for Phase E normalization.
- `prudent_healthcare_ai` target `prudent_ai_threshold`: Target is not a deterministic graph node for Phase E normalization.
- `prudent_healthcare_ai` target `uncertainty_disclosure_need`: Target is not a deterministic graph node for Phase E normalization.
- `prudent_healthcare_ai` target `primary_source_confirmation_need`: Target is not a deterministic graph node for Phase E normalization.
- `prudent_healthcare_ai` target `ai_provenance_warning`: Target is not a deterministic graph node for Phase E normalization.
- `duty_to_inquire` target `material_gap_present`: Target is not a deterministic graph node for Phase E normalization.
- `duty_to_inquire` target `gap_decision_relevance`: Target is not a deterministic graph node for Phase E normalization.
- `red_team` target `evidence_conflict`: Target is not a deterministic graph node for Phase E normalization.
- `red_team` target `escalation_need`: Target is not a deterministic graph node for Phase E normalization.
- `red_team` target `under_action_risk`: Target is not a deterministic graph node for Phase E normalization.
- `defense` target `over_action_risk`: Target is not a deterministic graph node for Phase E normalization.
- `defense` target `safety_net_need`: Target is not a deterministic graph node for Phase E normalization.

## Deeper Dive Artifacts
- `human_summary_sections`
- `node_audit_bundle`
- `ensemble_contribution_bundle`
- `methodology_summary`
- `workflow_artifacts`
