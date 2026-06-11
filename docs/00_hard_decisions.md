# 00 — Hard Decisions

These decisions define the POC. They prevent scope creep and protect the methodology from becoming generic AI debate or a narrow clinical checker.

## Decision 1 — Build Sentinel first, not Tribunal first

**Chosen:** Sentinel prospective/shadow-mode governance workbench.
**Deferred:** Tribunal retrospective forensic mode.

Rationale: The immediate existing need is not only post-harm reconstruction. It is ongoing governance evidence: monitoring, transparency, risk controls, lifecycle tracking, and auditability for AI use. Sentinel produces live or replay receipts that later become Tribunal evidence.

## Decision 2 — POC is a governance workbench, not a bedside alert product

**Chosen:** Shadow-mode/replay-mode workbench for AI governance, quality, safety, risk, and clinical informatics review.

**Not chosen yet:** Real-time interruptive clinical alerts.

Rationale: A bedside alert product requires live integration, safety review, workflow testing, liability handling, and alert-fatigue mitigation before the methodology is proven. A governance workbench solves the existing need for AI oversight evidence while avoiding unsafe premature deployment.

## Decision 3 — Solve decision warrant, not medical knowledge

**Chosen:** Build a content-light prudence calculus that evaluates whether a decision is warranted under incomplete information.

**Not chosen:** Build a medical answer engine, diagnosis recommender, or guideline search product.

Rationale: Medical knowledge sources are swappable inputs. The durable method is the calculation over information gaps, risk horizons, provenance, next-best-input value, and prudent-actor thresholds.

## Decision 4 — Agents produce structured inputs; graph computes verdict

**Chosen:** Role agents extract and structure findings. The belief network computes the final verdict.

**Rejected:** Multi-agent debate that converges to a prose consensus.

Rationale: Generic debate is not transparent enough for committee or risk review. The rigorous seam is agent-to-node conversion. Every role assessment must map to visible fields and node values.

## Decision 5 — The first differentiated modules are AI-provenance depth and next-best-information

**Chosen POC differentiators:**

1. AI-provenance depth: measures whether decision-critical “known” facts are primary, human-confirmed, AI-derived, or unverified AI-on-AI transformations.
2. Next-best-information: ranks missing inputs by expected posture change, preventability leverage, decision weight, and burden.

**Rejected as POC center:** Simple guideline concordance alone.

Rationale: Guideline checking is necessary but commoditizable. Provenance depth and next-best-information address gaps not currently solved by ordinary evidence tools.

## Decision 6 — EvidenceFlows are inputs, not product

**Chosen:** Use OpenEvidence-style reusable evidence workflows as a bootstrap and comparator lane.

**Rejected:** Building an OpenEvidence clone or making external evidence retrieval the judge.

Rationale: EvidenceFlows feed node parameters: required variables, guideline dependencies, result distributions, and uncertainty. The final warrant verdict belongs to the transparent graph.

## Decision 7 — POC data is synthetic/deidentified-style replay data

**Chosen:** Build with synthetic and deidentified-style DecisionEpisodes.

**Rejected:** Any dependency on a named clinical site or proprietary workflow.

Rationale: The POC must be portable and institution-neutral. It should prove methodology before needing live data.

## Decision 8 — Output is posture plus decision weight, not score

**Chosen output:**

- proceed,
- proceed with uncertainty disclosure,
- proceed with safety net/recheck,
- obtain specific information first,
- pause and escalate,
- do not proceed,
- human review required.

Each posture includes a decision weight and reasoned receipt.

**Rejected:** A single safety score.

Rationale: The useful answer is what posture a prudent actor should take now and how much that posture matters given the risk horizon.

## Decision 9 — Healthcare POC, domain-general method

**Chosen:** Healthcare governance workbench as first market/use case.

**Preserved:** Domain-general prudence calculus.

Rationale: Healthcare has an existing governance need, but the core method should apply to any high-stakes decision under uncertainty by swapping EvidenceFlows, thresholds, and role libraries.

## Decision 10 — POC success is governance credibility, not clinical outcome impact

**Chosen POC success criteria:**

- The workbench produces credible, inspectable receipts.
- It correctly identifies material information gaps.
- It ranks next-best inputs in a way expert reviewers find actionable.
- It flags unverified AI-derived evidence.
- It avoids recommending irrelevant information gathering.
- It shows model output is not the final judge.

**Deferred:** Demonstrating reduced patient harm.

Rationale: Outcome impact requires prospective deployment and much larger evaluation. The POC should first prove a committee-grade evidence artifact.
