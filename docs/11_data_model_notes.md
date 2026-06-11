# 11 — Data Model Notes

## Central objects

### DecisionEpisode

The unit of review. A decision episode contains artifacts, timepoints, facts, gaps, provenance, proposed actions, and expected evaluation references.

### TimelineState

A point in time where Sentinel evaluates what is known and what is proposed.

### Fact

An assertion available at a timepoint.

Required attributes:

- text,
- source type,
- reliability,
- provenance lineage,
- verification status,
- decision criticality.

### InformationGap

A missing input that may or may not matter.

Required attributes:

- gap type,
- knowability,
- burden,
- potential decision relevance,
- time to obtain,
- candidate input mapping.

### ProposedAction

The action or conclusion under review.

Examples:

- send message,
- recommend follow-up,
- escalate,
- defer,
- authorize agent action,
- accept AI recommendation.

### RoleAssessment

Structured output from a role agent.

### EvidenceFlowResult

Structured output from evidence retrieval/interpretation lane.

### GraphNode

Typed parameter used by the prudence graph.

### SentinelReceipt

Reconstructable signed output for a Sentinel run.

## Fact provenance categories

```text
PRIMARY_PATIENT_STATEMENT
PRIMARY_OBSERVATION
STRUCTURED_DATA
HUMAN_AUTHORED_NOTE
AI_GENERATED_TEXT
AI_SUMMARY_OF_TEXT
AI_INFERENCE
EXTERNAL_EVIDENCE
UNKNOWN
```

## Verification statuses

```text
VERIFIED_PRIMARY
VERIFIED_DETERMINISTIC
VERIFIED_HUMAN
UNVERIFIED_AI_DERIVED
UNVERIFIED_HUMAN_REPORTED
UNKNOWN_PROVENANCE
CONFLICTING
STALE
```

## Information buckets

```text
KNOWN
KNOWN_BUT_WEAK
KNOWABLE_BUT_UNKNOWN
PENDING
UNKNOWABLE_NOW
```

## Postures

```text
PROCEED
PROCEED_WITH_UNCERTAINTY_DISCLOSURE
PROCEED_WITH_SAFETY_NET_OR_RECHECK
OBTAIN_SPECIFIC_INFORMATION_FIRST
PAUSE_AND_ESCALATE
DO_NOT_PROCEED
HUMAN_REVIEW_REQUIRED
INDETERMINATE
```

## Evidence tiers

```text
TIER_1_EXTERNAL_GROUNDED
TIER_2_CASE_DERIVED
TIER_3_EXPERT_PRIOR
TIER_4_UNSUPPORTED_AGENT_ASSERTION
```

## Design rule

If a data field is unknown, represent it as unknown. Do not silently convert unknown to false, absent, or low-risk.
