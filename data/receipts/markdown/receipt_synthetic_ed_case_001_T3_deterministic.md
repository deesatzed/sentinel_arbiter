# Sentinel Receipt - synthetic_ed_case_001

- Receipt ID: `receipt_synthetic_ed_case_001_T3_deterministic`
- Timepoint: `T3_disposition_decision`
- Final posture: `OBTAIN_SPECIFIC_INFORMATION_FIRST`
- Decision weight: `0.875`
- Signature placeholder: `UNSIGNED_DETERMINISTIC_POC`

## What Was Known
- At the decision time, home support and recheck access remain unclear in this synthetic case.

## What Was Missing
- Home-plan feasibility remains unresolved at the decision point.

## What Would Have Changed The Discussion
- confirm support and return access
- verify source statement behind AI summary
- document observed response to therapy

## What Hospital-Based Monitoring Or Treatment Might Add
- The receipt records whether a hospital-based path had a specific monitoring, information, or therapy-response target in the current-time facts.

## What Non-Inpatient Alternatives Might Add
- The receipt records whether support, follow-up access, return access, and recheck feasibility were represented in the current-time facts.

## Commission Concerns
- commission_overconfident_posture
- commission_unverified_driver

## Omission Concerns
- omission_ai_fact_verification_gap
- omission_home_plan_feasibility_gap
- omission_unassessed_response

## Therapy-Response Concerns
- therapy_response_obs_001:no_clear_change
- therapy_supportive_001:no_clear_change

## Why The Graph Selected The Posture
- The graph selected OBTAIN_SPECIFIC_INFORMATION_FIRST from bounded node values, with decision weight 0.875 and preventability opportunity 0.7014.
