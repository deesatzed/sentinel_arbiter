# 02 — EvidenceFlow Prompt Contracts

EvidenceFlows are reusable evidence tasks. They are not the final judge.

## Universal EvidenceFlow rules

1. Use only current-time information.
2. Return structured fields.
3. Cite or reference evidence sources when available.
4. Identify required variables and missing variables.
5. Estimate uncertainty.
6. Do not return only narrative summaries.
7. When asked for next-best-input, return result distributions and posture implications.

## EvidenceFlow 1 — Guideline Dependency

### Question

What variables or conditions are required to judge whether the proposed action is evidence-aligned?

### Required output

- relevant evidence concepts,
- required variables,
- missing variables,
- evidence support strength,
- evidence conflict strength,
- exceptions,
- uncertainty notes,
- source references.

## EvidenceFlow 2 — Next-Best-Input / Result Distribution

### Question

What missing input would most change the decision posture or reduce preventable risk?

### Required output for each candidate input

- description,
- category,
- burden,
- time to obtain,
- possible result labels,
- probability estimate for each result,
- posture effect for each result,
- preventability effect,
- expected posture shift,
- whether obtain-now is justified given decision weight.

### Anti-generic rule

Reject outputs like:

- “get more history,”
- “order labs,”
- “do more evaluation,”
- “consider specialist input,”

unless specific, decision-relevant, and linked to posture change.

## EvidenceFlow 3 — High-Risk Alternative

### Question

What serious alternatives or failure modes must remain on the table given the current information?

### Required output

- alternative risk,
- minimum information needed to reduce concern,
- harm clock estimate,
- preventability if caught,
- whether safety-net is adequate.

## EvidenceFlow 4 — Prudent AI Conduct

### Question

What should a responsible healthcare AI say or not say given incomplete information and stakes?

### Required output

- answer allowed: yes/no/with_limits,
- required uncertainty disclosure,
- missing information disclosure,
- escalation or human review need,
- assertiveness limit,
- source/provenance warning.
