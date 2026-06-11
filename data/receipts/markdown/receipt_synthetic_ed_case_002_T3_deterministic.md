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
