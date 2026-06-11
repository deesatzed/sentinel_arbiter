# Sentinel Receipt - synthetic_ed_case_006

- Receipt ID: `receipt_synthetic_ed_case_006_T3_deterministic`
- Timepoint: `T3_disposition_decision`
- Final posture: `OBTAIN_SPECIFIC_INFORMATION_FIRST`
- Decision weight: `0.745`
- Signature placeholder: `UNSIGNED_DETERMINISTIC_POC`

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
