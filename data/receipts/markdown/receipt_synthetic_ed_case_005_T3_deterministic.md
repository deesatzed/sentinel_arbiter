# Sentinel Receipt - synthetic_ed_case_005

- Receipt ID: `receipt_synthetic_ed_case_005_T3_deterministic`
- Timepoint: `T3_disposition_decision`
- Final posture: `OBTAIN_SPECIFIC_INFORMATION_FIRST`
- Decision weight: `0.565`
- Signature placeholder: `UNSIGNED_DETERMINISTIC_POC`

## What Was Known
- At decision time, home support and return access are still not established.

## What Was Missing
- Home-plan feasibility is unresolved.

## What Would Have Changed The Discussion
- clarify support, follow-up, and return access

## What Hospital-Based Monitoring Or Treatment Might Add
- The receipt records whether a hospital-based path had a specific monitoring, information, or therapy-response target in the current-time facts.

## What Non-Inpatient Alternatives Might Add
- The receipt records whether support, follow-up access, return access, and recheck feasibility were represented in the current-time facts.

## Commission Concerns
- commission_overconfident_posture

## Omission Concerns
- omission_home_plan_feasibility_gap

## Therapy-Response Concerns
- No therapy-response concern was raised by the deterministic graph.

## Why The Graph Selected The Posture
- The graph selected OBTAIN_SPECIFIC_INFORMATION_FIRST from bounded node values, with decision weight 0.565 and preventability opportunity 0.4539.
