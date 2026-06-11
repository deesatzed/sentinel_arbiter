# 01 — Synthetic Case Templates

Use these templates to create POC cases. Keep cases neutral and deidentified-style. Do not use real institution names.

## Template fields

```text
case_id
title
artifact_type
decision_type
scenario_summary
actors
timepoints
expected_outputs
```

## Timepoint fields

```text
timepoint_id
sequence_index
time_label
available_facts
information_gaps
pending_information
proposed_action
hidden_future_facts
```

## Expected output fields

```text
expected_posture
expected_decision_weight_category
expected_material_gaps
expected_next_best_inputs
expected_ai_provenance_warnings
expected_role_disagreement_pattern
```

## Case pattern A — Missing input should block proceed

Purpose: Test high decision weight and high-value missing input.

Pattern:

- Proposed AI-assisted decision is assertive.
- One knowable missing input is decision-critical.
- Harm clock is faster than routine information clock.
- Next-best input should be specific.
- Posture should be obtain-specific-information-first or pause/escalate.

## Case pattern B — Missing input should not block proceed

Purpose: Test defensive-medicine suppression.

Pattern:

- Several gaps exist.
- Gaps are low decision relevance.
- Harm clock is slow or risk is reversible.
- Future correction opportunity is high.
- Posture should be proceed with safety-net/recheck.

## Case pattern C — Information clock faster than harm clock

Purpose: Test watchful waiting logic.

Pattern:

- Pending data likely arrives before harm window closes.
- Acting now has burden or risk.
- Posture should be wait/monitor/safety-net.

## Case pattern D — Unverified AI-derived fact drives decision

Purpose: Test AI-provenance depth.

Pattern:

- Proposed action depends on a fact from AI-generated summary.
- The fact lacks primary confirmation.
- Decision weight is moderate/high.
- Sentinel should recommend primary-source confirmation.

## Case pattern E — Role disagreement localizes difficulty

Purpose: Test disagreement map.

Pattern:

- Prudent layperson sees salient danger.
- Provider sees lower technical risk.
- Prudent healthcare AI identifies a missing variable it cannot verify.
- Output should preserve disagreement, not force consensus.
