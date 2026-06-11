# RISK_NOTES.md

## Risks

| Risk | Severity | Why It Matters | Mitigation |
|---|---|---|---|
| Disposition recommendation drift | High | The POC is about governance posture, but ED admission/disposition language can easily sound like clinical advice. | Use posture taxonomy only, run forbidden phrase checks, and keep admission/non-inpatient sections framed as what each might add rather than what to do. |
| Future leakage | High | Retrospective cases can accidentally use outcome facts that were unavailable at disposition time. | Require T0-T3/T4 separation, block hidden future facts from graph inputs, and test leakage explicitly. |
| Real data or PHI contamination | High | The goal requires synthetic and deidentified-style data only. | Keep fixtures synthetic, scan for identifiers and named institutions, and reject real case details. |
| Prompt overreach | High | Role agents or EvidenceFlows might output final clinical judgments instead of structured inputs. | Use prompt contracts with forbidden claims, schema validation, rejection rules, and graph-only final posture. |
| Weak provenance treated as verified | Medium-High | AI-derived or unsupported facts are central to the governance problem. | Preserve source lineage, verification status, AI-provenance depth, and downgrade unsupported claims. |
| Commission and omission lanes collapse together | Medium | The POC must show both missing-risk and over-action/low-value concerns. | Make both lanes first-class graph node groups and receipt sections. |
| Therapy response omitted | Medium | ED disposition replay depends on whether offered therapy was reassessed and whether response mattered. | Add offered-therapy and therapy-response fields before graph implementation. |
| Preventability metric overclaim | Medium | A proxy score could be mistaken for proven harm prevention. | Name it preventability opportunity, document inputs, avoid outcome-improvement claims, and keep limitations in receipts. |
| Planning sprawl | Medium | The handoff is already broad and could delay executable validation. | Use Phase 0 scope lock, then move to Phase 1 skeleton and tests before adding more prose. |
| No git root in target folder | Low-Medium | Git diff and staged-change verification are unavailable inside this folder. | Document the absence of a nearest git repository and run file/safety scans directly. |

## Safe Next Step

Move to Phase 1 by creating a minimal Python package, Pydantic schema models, valid/invalid synthetic fixture tests, and a future-leakage guard. Do not implement graph scoring or clinical logic until schema and fixture validation pass.
