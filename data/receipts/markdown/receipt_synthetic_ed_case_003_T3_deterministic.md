# Sentinel Receipt - synthetic_ed_case_003

- Receipt ID: `receipt_synthetic_ed_case_003_T3_deterministic`
- Timepoint: `T3_disposition_decision`
- Final posture: `OBTAIN_SPECIFIC_INFORMATION_FIRST`
- Decision weight: `0.71`
- Selected Review Question: `Unspecified governance review question`
- Signature placeholder: `UNSIGNED_DETERMINISTIC_POC`

## Clinician Summary
For Unspecified governance review question, Sentinel found that the current review record still depends on unresolved or weakly supported information before a governance reviewer should trust the posture. The main driver is: Therapy-response lane remains unexamined. The most useful next review input is: explain whether therapy-response observation would change review posture This output is governance review support, not a clinical action recommendation.

## What Was Known
- At decision time, the record has no therapy-response observation and no explanation for why the lane was not used.

## What Was Missing
- Therapy-response lane remains unexamined.

## What Would Have Changed The Discussion
- explain whether therapy-response observation would change review posture
- capture response observation if clinically available

## What Hospital-Based Monitoring Or Treatment Might Add
- The receipt records whether a hospital-based path had a specific monitoring, information, or therapy-response target in the current-time facts.

## What Non-Inpatient Alternatives Might Add
- The receipt records whether support, follow-up access, return access, and recheck feasibility were represented in the current-time facts.

## Commission Concerns
- commission_overconfident_posture

## Omission Concerns
- omission_unassessed_response

## Therapy-Response Concerns
- c003_therapy_not_considered:not_considered
- c003_therapy_not_considered:unknown

## Why The Graph Selected The Posture
- The graph selected OBTAIN_SPECIFIC_INFORMATION_FIRST from bounded node values, with decision weight 0.71 and preventability opportunity 0.4171.

## Node Audit Methodology
- `information_sufficiency`: value `0.2`; Range `0.1` to `0.3`; Median `0.2`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `current_time_information_gaps`; Evidence refs `gap:c003_gap_therapy_considered, gap:c003_gap_response_absent`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `material_gap_strength`: value `0.8`; Range `0.7` to `0.9`; Median `0.8`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `current_time_information_gaps`; Evidence refs `gap:c003_gap_therapy_considered, gap:c003_gap_response_absent`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `harm_clock`: value `0.82`; Range `0.67` to `0.97`; Median `0.82`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `current_time_information_gaps, therapy_response, ai_provenance`; Evidence refs `gap:c003_gap_therapy_considered, gap:c003_gap_response_absent, therapy:c003_therapy_not_considered`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `information_clock`: value `0.9792`; Range `0.8792` to `1.0`; Median `0.9792`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `current_time_information_gaps`; Evidence refs `gap:c003_gap_therapy_considered, gap:c003_gap_response_absent`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `recoverability`: value `0.42`; Range `0.27` to `0.57`; Median `0.42`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `current_time_information_gaps, therapy_response`; Evidence refs `gap:c003_gap_therapy_considered, gap:c003_gap_response_absent, therapy:c003_therapy_not_considered`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `future_correction_opportunity`: value `0.35`; Range `0.2` to `0.5`; Median `0.35`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `follow_up_feasibility`; Evidence refs `follow_up:synthetic_ed_case_003:T3_disposition_decision`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `decision_weight`: value `0.71`; Range `0.56` to `0.86`; Median `0.71`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `current_time_information_gaps, therapy_response, ai_provenance`; Evidence refs `gap:c003_gap_therapy_considered, gap:c003_gap_response_absent, therapy:c003_therapy_not_considered`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `ai_provenance_risk`: value `0.0`; Range `0.0` to `0.15`; Median `0.0`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `available_facts`; Evidence refs `node:ai_provenance_risk:no_direct_evidence`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `commission_risk`: value `0.75`; Range `0.65` to `0.85`; Median `0.75`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `proposed_posture, current_time_information_gaps, ai_provenance`; Evidence refs `gap:c003_gap_therapy_considered, gap:c003_gap_response_absent`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `omission_risk`: value `0.8`; Range `0.7` to `0.9`; Median `0.8`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `current_time_information_gaps, follow_up_feasibility, ai_provenance`; Evidence refs `gap:c003_gap_therapy_considered, gap:c003_gap_response_absent`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `therapy_response_relevance`: value `0.9`; Range `0.75` to `1.0`; Median `0.9`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `offered_therapies, therapy_response_observations`; Evidence refs `therapy:c003_therapy_not_considered`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `next_best_information_rank`: value `2`; Range `1.0` to `3.0`; Median `2.0`; Distribution `deterministic_count_with_neighbor_range`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `current_time_information_gaps`; Evidence refs `gap:c003_gap_therapy_considered, gap:c003_gap_response_absent`; Sensitivity `Posture sensitivity depends on whether additional gaps cross the materiality threshold.`
- `preventability_opportunity_score`: value `0.4171`; Range `0.3171` to `0.5171`; Median `0.4171`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `material_gap_strength, decision_weight, information_clock, burden_modifier`; Evidence refs `gap:c003_gap_therapy_considered, gap:c003_gap_response_absent`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`

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
- `evidenceflow:next_best_input` to `next_best_information_rank`: proposed `2`; Range `0.0` to `3.0`; disposition `accepted`; reason `EvidenceFlow candidate normalized with expected posture shift 0.6.`; Evidence refs `synthetic_ed_case_003_candidate_input_001`
- `evidenceflow:next_best_input` to `preventability_opportunity_score`: proposed `0.5`; Range `0.35` to `0.65`; disposition `accepted`; reason `EvidenceFlow candidate normalized with preventability leverage 0.5.`; Evidence refs `synthetic_ed_case_003_candidate_input_001`
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
