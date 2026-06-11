# 05 — Agent-to-Node Conversion

## Why this document matters

This is the highest-risk seam. If role agents produce prose and that prose becomes the verdict, Sentinel becomes another opaque AI-checks-AI system.

The rule:

> Agents may identify, explain, and estimate. The graph must compute.

## Required conversion pipeline

```text
Role agent output
  ↓ schema validation
Evidence support check
  ↓
Confidence normalization
  ↓
Node mapping
  ↓
Node value constraints
  ↓
Graph execution
  ↓
Receipt storage
```

## Role assessment output minimum fields

Every role assessment must include:

```text
role_name
assessment_scope
timepoint_id
claims_or_gaps_referenced
findings[]
overall_confidence
missing_information_identified[]
uncertainty_notes[]
sources_used[]
```

Each finding must include:

```text
finding_id
finding_type
structured_value
confidence
rationale_short
source_refs
node_targets[]
```

## Finding types

Initial POC allowed finding types:

```text
INFORMATION_GAP
DECISION_RELEVANCE
HARM_CLOCK_ESTIMATE
INFORMATION_CLOCK_ESTIMATE
RECOVERABILITY_ESTIMATE
FUTURE_CORRECTION_OPPORTUNITY
AI_PROVENANCE_WARNING
PRIMARY_SOURCE_CONFIRMATION_NEED
PRUDENT_LAYPERSON_THRESHOLD
PRUDENT_PROVIDER_THRESHOLD
PRUDENT_AI_THRESHOLD
NEXT_INPUT_CANDIDATE
EVIDENCE_SUPPORT
EVIDENCE_CONFLICT
UNCERTAINTY_DISCLOSURE_NEED
ESCALATION_NEED
SAFETY_NET_NEED
```

Unknown finding types should be rejected or routed to human review.

## Node mapping table

| Finding type | Graph node target | Example structured value |
|---|---|---|
| INFORMATION_GAP | material_gap_present | true/false |
| DECISION_RELEVANCE | gap_decision_relevance | 0.0-1.0 |
| HARM_CLOCK_ESTIMATE | harm_clock_hours | numeric range |
| INFORMATION_CLOCK_ESTIMATE | information_clock_hours | numeric range |
| RECOVERABILITY_ESTIMATE | recoverability | 0.0-1.0 |
| FUTURE_CORRECTION_OPPORTUNITY | future_correction_opportunity | 0.0-1.0 |
| AI_PROVENANCE_WARNING | unverified_ai_depth | integer |
| PRIMARY_SOURCE_CONFIRMATION_NEED | primary_source_needed | true/false |
| NEXT_INPUT_CANDIDATE | candidate_input | object |
| EVIDENCE_SUPPORT | evidence_support_strength | 0.0-1.0 |
| EVIDENCE_CONFLICT | evidence_conflict_strength | 0.0-1.0 |
| ESCALATION_NEED | escalation_threshold | 0.0-1.0 |

## Confidence normalization

Agents often overstate confidence. Normalize with role-specific calibration parameters.

POC simple method:

```text
normalized_confidence = raw_confidence × role_reliability_prior × evidence_tier_weight
```

Evidence tier weights:

```text
Tier 1: externally grounded, guideline/literature/source-backed
Tier 2: derived from case data or local corpus
Tier 3: expert prior / prompt-derived estimate
Tier 4: unsupported agent assertion; cannot directly drive graph verdict
```

## Rejection rules

Reject or downgrade a finding if:

- It lacks a source reference when it claims evidence support.
- It uses future information unavailable at the timepoint.
- It contains a conclusion without a structured value.
- It bypasses the required output schema.
- It asserts a clinical fact not present in the provided evidence or EvidenceFlow result.
- It provides only generic advice.
- It recommends broad information gathering without decision relevance.

## Disagreement handling

Disagreement is not averaged away.

Example:

```text
layperson_threshold = high concern
provider_threshold = moderate concern
prudent_ai_threshold = defer pending confirmation
```

Graph output:

```text
disagreement_structure = "layperson-AI concern exceeds provider threshold"
review_implication = "case complexity localized to salient-danger vs technical-risk mismatch"
```

## Agent-to-node acceptance criteria

The POC should pass these tests:

1. Malformed role output fails validation.
2. Unsupported evidence claim is downgraded.
3. A future fact cannot enter current-time graph calculation.
4. Same structured node inputs yield same graph result regardless of agent prose.
5. Role disagreement appears in the receipt.
6. Human reviewer can trace final posture to visible node values.
