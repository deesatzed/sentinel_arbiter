# 07 — Requirements

## Functional requirements

### FR-001 DecisionEpisode ingestion

The system shall ingest a DecisionEpisode containing artifacts, timeline states, facts, gaps, proposed decisions, and source provenance.

### FR-002 Replay timepoint evaluation

The system shall evaluate a DecisionEpisode at a specified timepoint without using future information.

### FR-003 Information partitioning

The system shall classify inputs into known, known-but-weak, knowable-but-unknown, pending, and unknowable-now categories.

### FR-004 AI-provenance depth

The system shall track unverified AI-provenance depth for each decision-critical fact when provenance is available, and shall flag unknown provenance when not available.

### FR-005 Role-agent structured assessments

The system shall run a configured set of role agents and require each to return schema-valid structured outputs.

### FR-006 EvidenceFlow execution

The system shall run at least two EvidenceFlows:

1. guideline/dependency flow,
2. next-best-input/result-distribution flow.

### FR-007 Agent-to-node normalization

The system shall map role findings into graph nodes using a deterministic normalizer with validation and rejection rules.

### FR-008 Prudence graph execution

The system shall calculate decision weight, information sufficiency, duty-to-inquire strength, AI-provenance risk, next-best-input ranking, and final posture.

### FR-009 Disagreement preservation

The system shall preserve role disagreement in the output and receipt.

### FR-010 Receipt generation

The system shall generate a machine-readable SentinelReceipt and a human-readable review summary for every run.

### FR-011 Workbench UI

The system shall provide a UI to inspect timeline state, information gaps, role assessments, graph nodes, evidence flow results, next-best-input ranking, and receipt.

### FR-012 Evaluation harness

The system shall run cases against expected outputs and calculate POC metrics.

## Non-functional requirements

### NFR-001 Institution-neutral

No named clinical site, employer, or institution may appear in generated sample data, logs, UI, or test fixtures.

### NFR-002 Deterministic reproducibility

Given the same inputs, model outputs, graph version, and parameters, the system must reproduce the same receipt.

### NFR-003 Versioning

All prompts, models, graph versions, node-library versions, and evidence sources must be versioned.

### NFR-004 Explainability

A reviewer must be able to trace the final posture back to node inputs and source references.

### NFR-005 Privacy-preserving POC

POC must use synthetic/deidentified-style data only.

### NFR-006 Framework neutrality

Role-agent contracts must not depend on one orchestration framework.

### NFR-007 Graceful degradation

If evidence retrieval fails, the system should mark uncertainty and lower confidence rather than fabricate.

### NFR-008 Human review routing

High uncertainty, unsupported evidence, high decision weight, or unverified AI-derived critical facts should trigger human review routing.

## POC acceptance criteria

1. At least 5 replay cases run end-to-end.
2. At least 3 artifact types use the same core graph.
3. Every run emits a valid SentinelReceipt.
4. The UI displays information state, risk horizon, next-best input, and provenance depth.
5. Role outputs are schema-valid or rejected.
6. Future facts are blocked from current-time evaluation.
7. Final posture is computed from graph nodes, not directly from agent prose.
8. Evaluation report includes gap detection, next-best-input actionability, and expert-panel agreement placeholders.
