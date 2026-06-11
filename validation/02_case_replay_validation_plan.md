# 02 — Case Replay Validation Plan

## Purpose

Build synthetic/deidentified-style cases that test methodology rather than medical trivia.

## Required case properties

Each case should include:

- staged timeline,
- proposed AI-assisted action/conclusion,
- known facts,
- weak known facts,
- knowable gaps,
- pending information,
- hidden future facts,
- candidate next inputs,
- expected posture at each timepoint,
- expected decision weight,
- provenance flags,
- role disagreement pattern.

## Case design principles

1. A case should have at least one material information gap.
2. A case should have at least one low-value gap that should not be escalated.
3. At least one case should show high harm clock faster than information clock.
4. At least one case should show information clock faster than harm clock.
5. At least one case should depend on unverified AI-derived evidence.
6. At least one case should show prudent layperson concern exceeding provider concern.
7. At least one case should show prudent AI should defer or disclose uncertainty.

## Expected output labels

For each timepoint, define:

```text
expected_posture
expected_decision_weight_category
expected_material_gaps
expected_next_best_input
expected_ai_provenance_warning
expected_role_disagreement_pattern
```

## Validation modes

### Deterministic mode

Uses static role outputs and static EvidenceFlow results. This tests graph and UI.

### LLM mode

Uses dynamic role-agent outputs. This tests agent reliability and normalizer.

### Model-swap mode

Runs different LLMs or prompt versions through same cases. This tests stability.

## Initial case count

Minimum POC: 5 cases.
Better POC: 10 cases.
Post-POC calibration: 50+ cases.
