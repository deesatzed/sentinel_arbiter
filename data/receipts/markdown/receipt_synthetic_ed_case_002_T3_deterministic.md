# Sentinel Receipt - synthetic_ed_case_002

- Receipt ID: `receipt_synthetic_ed_case_002_T3_deterministic`
- Timepoint: `T3_disposition_decision`
- Final posture: `PROCEED_WITH_SAFETY_NET_OR_RECHECK`
- Decision weight: `0.32`
- Signature placeholder: `UNSIGNED_DETERMINISTIC_POC`

## What Was Known
- At decision time, therapy response is documented and follow-up access is clear in the synthetic case.

## What Was Missing
- No material missing inputs were represented at this timepoint.

## What Would Have Changed The Discussion
- No next-best-information item was ranked above the materiality threshold.

## What Hospital-Based Monitoring Or Treatment Might Add
- The receipt records whether a hospital-based path had a specific monitoring, information, or therapy-response target in the current-time facts.

## What Non-Inpatient Alternatives Might Add
- The receipt records whether support, follow-up access, return access, and recheck feasibility were represented in the current-time facts.

## Commission Concerns
- No commission-lane concern was raised by the deterministic graph.

## Omission Concerns
- No omission-lane concern was raised by the deterministic graph.

## Therapy-Response Concerns
- c002_response:documented_improvement
- c002_therapy:documented_improvement

## Why The Graph Selected The Posture
- The graph selected PROCEED_WITH_SAFETY_NET_OR_RECHECK from bounded node values, with decision weight 0.32 and preventability opportunity 0.0.

## Node Audit Methodology
- `information_sufficiency`: value `1.0`; Range `0.85` to `1.0`; Median `1.0`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `current_time_information_gaps`; Evidence refs `node:information_sufficiency:no_direct_evidence`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `material_gap_strength`: value `0.0`; Range `0.0` to `0.15`; Median `0.0`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `current_time_information_gaps`; Evidence refs `node:material_gap_strength:no_direct_evidence`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `harm_clock`: value `0.47`; Range `0.37` to `0.57`; Median `0.47`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `current_time_information_gaps, therapy_response, ai_provenance`; Evidence refs `therapy:c002_therapy, therapy_observation:c002_response`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `information_clock`: value `1.0`; Range `0.85` to `1.0`; Median `1.0`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `current_time_information_gaps`; Evidence refs `node:information_clock:no_direct_evidence`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `recoverability`: value `0.93`; Range `0.83` to `1.0`; Median `0.93`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `current_time_information_gaps, therapy_response`; Evidence refs `therapy:c002_therapy, therapy_observation:c002_response`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `future_correction_opportunity`: value `0.8`; Range `0.7` to `0.9`; Median `0.8`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `follow_up_feasibility`; Evidence refs `follow_up:synthetic_ed_case_002:T3_disposition_decision`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `decision_weight`: value `0.32`; Range `0.22` to `0.42`; Median `0.32`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `current_time_information_gaps, therapy_response, ai_provenance`; Evidence refs `therapy:c002_therapy, therapy_observation:c002_response`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `ai_provenance_risk`: value `0.0`; Range `0.0` to `0.15`; Median `0.0`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `available_facts`; Evidence refs `node:ai_provenance_risk:no_direct_evidence`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `commission_risk`: value `0.0`; Range `0.0` to `0.15`; Median `0.0`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `proposed_posture, current_time_information_gaps, ai_provenance`; Evidence refs `node:commission_risk:no_direct_evidence`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `omission_risk`: value `0.0`; Range `0.0` to `0.15`; Median `0.0`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `current_time_information_gaps, follow_up_feasibility, ai_provenance`; Evidence refs `node:omission_risk:no_direct_evidence`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `therapy_response_relevance`: value `0.35`; Range `0.25` to `0.45`; Median `0.35`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `offered_therapies, therapy_response_observations`; Evidence refs `therapy:c002_therapy, therapy_observation:c002_response`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`
- `next_best_information_rank`: value `0`; Range `0.0` to `1.0`; Median `0.0`; Distribution `deterministic_count_with_neighbor_range`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `current_time_information_gaps`; Evidence refs `node:next_best_information_rank:no_direct_evidence`; Sensitivity `Posture sensitivity depends on whether additional gaps cross the materiality threshold.`
- `preventability_opportunity_score`: value `0.0`; Range `0.0` to `0.15`; Median `0.0`; Distribution `bounded_deterministic_interval`; Method `deterministic_fixture_field_mapping_v0.1`; Dependent inputs `material_gap_strength, decision_weight, information_clock, burden_modifier`; Evidence refs `node:preventability_opportunity_score:no_direct_evidence`; Sensitivity `Posture sensitivity should be reviewed if the estimate range crosses a graph threshold.`

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
- `evidenceflow:next_best_input` to `next_best_information_rank`: proposed `1`; Range `0.0` to `1.0`; disposition `accepted`; reason `EvidenceFlow candidate normalized with expected posture shift 0.6.`; Evidence refs `synthetic_ed_case_002_candidate_input_001`
- `evidenceflow:next_best_input` to `preventability_opportunity_score`: proposed `0.5`; Range `0.35` to `0.65`; disposition `accepted`; reason `EvidenceFlow candidate normalized with preventability leverage 0.5.`; Evidence refs `synthetic_ed_case_002_candidate_input_001`
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
