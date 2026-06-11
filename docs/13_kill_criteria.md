# 13 — Kill Criteria and Pivot Triggers

This project should not continue blindly. The POC must test whether Sentinel is solving a real need with a credible method.

## Kill criterion 1 — The workbench is not useful to governance reviewers

Signal:

- Reviewers say the output is interesting but not usable for AI governance, monitoring, quality, or risk review.

Mitigation/pivot:

- Re-map output to specific governance controls and committee workflows.
- If still not useful, pivot to narrower risk/legal Tribunal mode.

## Kill criterion 2 — Next-best-information is vague

Signal:

- Recommendations are generic, broad, or not decision-changing.

Mitigation/pivot:

- Restrict to curated cases with explicit candidate-input tables.
- Delay open-ended next-best-input generation.
- Focus first on information-gap classification and AI-provenance warnings.

## Kill criterion 3 — Agent-to-node conversion is unreliable

Signal:

- Agents cannot consistently produce schema-valid fields.
- Node values change unpredictably based on prose.

Mitigation/pivot:

- Reduce role set.
- Use deterministic extraction and manually curated EvidenceFlow outputs.
- Treat agents as optional annotations until reliability improves.

## Kill criterion 4 — Graph weights look arbitrary and unconvincing

Signal:

- Expert reviewers reject outputs because parameters feel made up.

Mitigation/pivot:

- Make POC graph explicitly illustrative.
- Add sensitivity analysis.
- Use expert panel calibration before claims of performance.

## Kill criterion 5 — The product becomes just guideline search

Signal:

- Users focus only on evidence retrieval and ignore warrant, risk horizon, provenance, and next-best input.

Mitigation/pivot:

- De-emphasize guideline answers in UI.
- Lead with information state, decision weight, and next input.

## Kill criterion 6 — Alert fatigue appears even in replay

Signal:

- Sentinel flags too many low-value gaps.

Mitigation/pivot:

- Increase decision-relevance threshold.
- Gate next-best-information by decision weight.
- Suppress low-impact missing inputs.

## Kill criterion 7 — AI-provenance cannot be captured

Signal:

- Most facts are unknown provenance and the system cannot distinguish AI-derived from human/primary.

Mitigation/pivot:

- Treat unknown provenance as a governance finding.
- Build prospective receipt capture as the product wedge.
- Use explicit provenance in synthetic case POC.

## Kill criterion 8 — Model-swap instability dominates graph output

Signal:

- Changing the LLM changes final posture too often despite fixed graph.

Mitigation/pivot:

- Improve extractor/agent benchmarking.
- Increase human-review routing for unstable cases.
- Harden deterministic normalization.

## Kill criterion 9 — No buyer urgency

Signal:

- Stakeholders agree the method is sound but no one has budget or urgency.

Mitigation/pivot:

- Reframe as certification/evidence artifact generator.
- Explore risk/legal, payer utilization, vendor evaluation, or insurer-facing use cases.
