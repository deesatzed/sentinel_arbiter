# 01 — Metrics and Evaluation Plan

## POC evaluation goal

Evaluate whether Sentinel produces credible, actionable, reproducible governance evidence.

Do not claim clinical outcome improvement in POC.

## Metric family 1 — Method validity

| Metric | Definition | POC target |
|---|---|---|
| Schema validity rate | Percent of role/evidence/receipt outputs passing schema | ≥ 95% |
| Future leakage failures | Future facts entering current-time evaluation | 0 |
| Graph determinism | Same node inputs yield same posture | 100% |
| Receipt completeness | Required receipt fields present | ≥ 95% |
| Node traceability | Final posture can be traced to node inputs | ≥ 95% |

## Metric family 2 — Information-gap quality

| Metric | Definition | POC target |
|---|---|---|
| Critical gap detection | Known important gaps correctly flagged in synthetic cases | ≥ 80% |
| Gap precision | Flagged gaps that are decision-relevant | ≥ 70% |
| Low-value gap suppression | Known low-value gaps not escalated | ≥ 70% |
| Knowability accuracy | Correct known/knowable/pending/unknowable classification | ≥ 80% |
| Timepoint correctness | Gap status changes correctly across timeline | ≥ 90% |

## Metric family 3 — Next-best-information value

| Metric | Definition | POC target |
|---|---|---|
| Candidate actionability | Recommended input is specific and obtainable | ≥ 80% |
| Expected posture-shift alignment | Recommended input matches expected case design | ≥ 70% |
| Burden gating | High-burden input not recommended when decision weight low | ≥ 80% |
| Urgency alignment | Input urgency matches harm/information clock | ≥ 80% |
| Generic recommendation rate | Vague recommendations among top-ranked inputs | ≤ 10% |

## Metric family 4 — Risk-horizon quality

| Metric | Definition | POC target |
|---|---|---|
| Harm clock classification | Correct immediate/near/intermediate/long classification | ≥ 80% |
| Information clock classification | Correct time-to-information category | ≥ 80% |
| Decision weight calibration | High-risk/no-checkpoint cases produce high weight; deferred/reversible cases produce lower weight | qualitative in POC |
| Over-escalation rate | Low decision-weight cases escalated unnecessarily | ≤ 20% |

## Metric family 5 — AI-provenance quality

| Metric | Definition | POC target |
|---|---|---|
| Provenance classification | Correct source category for facts | ≥ 90% in synthetic cases |
| AI-depth computation | Correct unverified AI-depth | ≥ 90% in synthetic cases |
| Primary confirmation trigger | High-weight decisions relying on unverified AI facts trigger warning | ≥ 90% |
| Unknown provenance handling | Unknown provenance not treated as verified | 100% |

## Metric family 6 — Role-agent value

| Metric | Definition | POC target |
|---|---|---|
| Role schema success | Role outputs validate | ≥ 90% |
| Unsupported assertion downgrade | Unsupported role claims downgraded | ≥ 95% |
| Disagreement capture | Role disagreements visible in receipt | ≥ 95% |
| Ablation value | Adding role set improves detection/actionability vs graph-only baseline | exploratory |

## Metric family 7 — Governance value

| Metric | Definition | POC target |
|---|---|---|
| Committee readability | Human reviewers can understand receipt summary | qualitative |
| Audit reconstructability | Reviewer can reconstruct final posture from receipt | ≥ 90% |
| Review time | Time to inspect one case | establish baseline |
| Stakeholder value rating | Governance/risk/quality reviewers rate usefulness | target ≥ 4/5 |

## Evaluation phases

### Phase 1 — Automated validation

Run all cases through test suite.

Outputs:

- schema pass/fail,
- receipt completeness,
- future leakage checks,
- expected posture match,
- next-best-input match.

### Phase 2 — Expert review

Have reviewers inspect 5 cases.

Questions:

1. Was the posture reasonable?
2. Were the material gaps correctly identified?
3. Was the next-best input actionable?
4. Was the provenance warning useful?
5. Was the receipt committee-ready?

### Phase 3 — Model-swap test

Run same cases with different model configurations for role agents/extraction.

Measure:

- role output variation,
- graph posture variation,
- receipt stability,
- reason for divergences.

### Phase 4 — Ablation test

Compare:

1. graph only,
2. graph + EvidenceFlows,
3. graph + role agents,
4. full Sentinel.

Purpose:

Prove the role swarm adds value or remove roles that do not.
