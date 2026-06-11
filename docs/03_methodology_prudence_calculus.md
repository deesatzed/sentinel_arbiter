# 03 — Methodology: The Prudence Calculus

## Purpose

The prudence calculus is the content-light core of Sentinel. It does not know medicine by itself. It consumes clinical/evidence inputs from EvidenceFlows and structured case data, then calculates whether the current decision is warranted.

## Core question

At time T, with information state K(T), proposed action A, and risk structure R:

> What posture should a prudent actor take, and how much does that posture matter right now?

## Inputs

- DecisionEpisode
- Current TimelineState
- ProposedAction or ProposedConclusion
- Known facts
- Knowable-but-unknown gaps
- Pending information
- Unknowable uncertainty
- Provenance lineage for each key fact
- EvidenceFlow outputs
- Role-agent structured assessments
- Node-library parameters

## Piece 1 — Information state

Every relevant fact or gap is partitioned into:

1. **Known** — available now and reliable enough to use.
2. **Known but weak** — available but stale, conflicting, indirect, AI-derived, or low-confidence.
3. **Knowable but unknown** — obtainable before acting if sought.
4. **Pending** — already requested or naturally emerging on its own clock.
5. **Unknowable now** — irreducible or impractical to obtain in the current decision window.

The duty to inquire applies only to **knowable-but-unknown** facts that are **decision-relevant**.

## Piece 2 — Decision-relevance filter

For each gap G:

> Would knowing G likely change the decision posture?

If no, G is noise.
If yes, G becomes a candidate for duty-to-inquire and next-best-information ranking.

Proposed POC fields:

```text
gap_id
decision_relevance_probability: 0.0-1.0
expected_posture_shift: distribution over posture changes
decision_dependency: low | moderate | high | critical
```

## Piece 3 — Two-clock model

Sentinel compares:

- **Harm clock:** how soon preventable harm could occur if current posture is wrong.
- **Information clock:** how soon decision-relevant information could arrive or be obtained.

Basic rule:

```text
if information_clock < harm_clock:
    wait / monitor / safety-net may be prudent
else:
    act / escalate / accelerate information gathering may be prudent
```

## Piece 4 — Decision weight

Decision weight is not risk. It measures how much getting the current decision right matters now.

Conceptual formula:

```text
decision_weight ∝ severity × probability_wrong × (1 - recoverability) × (1 - future_correction_opportunity)
```

Interpretation:

- High severity, high probability of wrongness, irreversible harm, and no future checkpoint → high decision weight.
- Reversible harm, dense monitoring, and future correction opportunity → lower immediate decision weight.

## Piece 5 — AI-provenance depth

Known facts are not equally trustworthy. Sentinel tracks provenance depth since last verification.

Definitions:

- `ai_provenance_depth = number of unverified AI transformations since last primary or verified source`
- `verification_reset = human confirmation, deterministic cross-check, source transcript confirmation, or structured-data confirmation`

Risk concept:

```text
clean_probability ≈ (1 - epsilon) ^ unverified_ai_depth
```

The POC does not need to claim a precise epsilon. It should surface depth and allow sensitivity testing.

## Piece 6 — Next-best-information / preventability leverage

For each candidate input X:

```text
preventability_leverage(X) =
    P(X changes posture)
  × severity_if_wrong
  × imminence_weight
  × preventability_if_caught
  × decision_dependency
  - burden_cost_delay(X)
```

But the actual action threshold is gated by decision weight:

```text
obtain_now if expected_warrant_change(X) × decision_weight > burden(X)
```

This prevents the system from recommending every possible input.

## Piece 7 — Three prudence standards

Each standard is a threshold function, not a vote.

### Prudent layperson

Floor for salient-danger recognition.

Sensitive to:

- obvious danger,
- patient-facing urgency,
- red flags,
- communication clarity,
- access barriers.

Blind to:

- subtle technical risk,
- complex guideline nuance.

### Prudent provider

Expert standard for reasonable clinical process.

Sensitive to:

- technical risk,
- minimum safe evaluation,
- uncertainty management,
- reasonable escalation,
- overtesting vs undertesting.

Failure modes:

- defensive inflation,
- normalized deviance.

### Prudent healthcare AI

Novel standard based on AI-specific capabilities and limits.

Obligations:

- disclose uncertainty,
- identify decision-relevant gaps,
- avoid false certainty,
- flag missing primary evidence,
- surface AI-derived evidence dependence,
- match assertiveness to warrant and stakes,
- escalate or defer when stakes exceed warrant,
- preserve human accountability.

## Output

Sentinel returns:

1. recommended posture,
2. decision weight,
3. decision-relevant gaps,
4. next-best inputs,
5. AI-provenance warnings,
6. prudence-standard disagreement map,
7. receipt.

## Posture taxonomy

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

## Key anti-patterns

- Treating any risk as a reason to stop.
- Treating any missing information as required.
- Treating guideline search as final judgment.
- Averaging role-agent opinions into a single consensus.
- Allowing agent prose to bypass the graph.
- Emitting a score without an action posture.
