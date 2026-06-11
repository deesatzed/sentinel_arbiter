# Sentinel Receipt - synthetic_ed_case_003

- Receipt ID: `receipt_synthetic_ed_case_003_T3_deterministic`
- Timepoint: `T3_disposition_decision`
- Final posture: `OBTAIN_SPECIFIC_INFORMATION_FIRST`
- Decision weight: `0.71`
- Signature placeholder: `UNSIGNED_DETERMINISTIC_POC`

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
