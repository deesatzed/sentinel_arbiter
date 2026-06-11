# 01 — Short-Term POC Roadmap

## POC name

Sentinel Governance Workbench POC

For the ED disposition replay wedge, treat `roadmaps/04_phase_0_ed_disposition_implementation_plan.md` as the Phase 0 scope-lock delta for this broader roadmap.

## POC objective

Demonstrate that Sentinel can evaluate AI-assisted healthcare decision episodes in replay/shadow mode and produce credible, inspectable, committee-ready receipts that show:

1. whether the decision was warranted yet,
2. what information gaps mattered,
3. what next input would most improve the decision,
4. how urgent the decision was,
5. whether decision-critical facts were AI-derived or unverified,
6. how prudent layperson, prudent provider, and prudent healthcare AI thresholds agreed or disagreed.

## POC build length

Suggested: 4-6 focused build weeks.

If time is compressed, build Milestones 1-4 only and use static/manual EvidenceFlow outputs.

---

# Milestone 0 — Preparation and scope lock

## Deliverables

- Confirm hard decisions in `docs/00_hard_decisions.md`.
- Confirm no named institution appears anywhere.
- Select POC stack.
- Select 5 synthetic/replay cases.
- Freeze v0.1 schemas.

## Acceptance criteria

- Repository created.
- Docs loaded.
- Test suite placeholder exists.
- POC cases drafted.
- No live data dependency.

## Contrarian concern

Planning can become the product.

## Mitigation

Time-box this milestone. Exit when schemas and 5 cases are sufficient, not perfect.

---

# Milestone 1 — Data model and replay engine

## Build

- Pydantic models for:
  - DecisionEpisode,
  - TimelineState,
  - Fact,
  - InformationGap,
  - ProposedAction,
  - RoleAssessment,
  - EvidenceFlowResult,
  - SentinelReceipt.
- Loader for JSON case files.
- Replay timepoint selector.
- Future-information guard.

## Acceptance criteria

- 5 cases load.
- Each case has at least 3 timepoints.
- Current timepoint hides future facts.
- Invalid schema fails loudly.

## Metrics

- Case load success rate.
- Schema validity rate.
- Future leakage failures.

---

# Milestone 2 — Information partition and provenance depth

## Build

- InformationPartitionService.
- AIProvenanceService.
- Fact trust scoring.
- Known vs known-but-weak vs knowable-but-unknown vs pending vs unknowable-now display.

## Acceptance criteria

- Each fact gets bucketed.
- Each decision-critical fact gets provenance category.
- Unverified AI depth is computed or marked unknown.
- High decision-criticality + unverified AI depth triggers warning.

## Metrics

- Bucket classification completeness.
- AI-provenance detection coverage.
- Unknown provenance rate.

## Contrarian concern

Provenance depth may be unavailable in real systems.

## Mitigation

POC supports explicit provenance and unknown-provenance risk flag. Missing provenance itself becomes a governance finding.

---

# Milestone 3 — EvidenceFlow stubs and next-best-input tables

## Build

- EvidenceFlowResult model.
- Manual/static EvidenceFlow stub loader.
- Next-best-input candidate table per case.
- Result-distribution fields for each candidate input.

## Acceptance criteria

- Each case has 3-7 candidate inputs.
- Each candidate includes possible result categories, approximate probabilities, posture effects, burden, and time-to-obtain.
- Generic recommendations are not allowed.

## Metrics

- Candidate input completeness.
- Missing result-distribution rate.
- Actionability score placeholder.

## Contrarian concern

Result distributions are hard and evidence-dependent.

## Mitigation

Start curated. Later add external evidence retrieval and model-generated candidate distributions after output format is proven.

---

# Milestone 4 — Role-agent structured outputs

## Build

- Role prompt contracts.
- RoleAgentService with stub/mock mode and LLM mode.
- Schema validation and rejection.
- Initial role set:
  - prudent layperson,
  - prudent provider,
  - prudent healthcare AI,
  - duty-to-inquire,
  - risk horizon,
  - red team,
  - defense,
  - synthesizer/normalizer.

## Acceptance criteria

- Role outputs validate against schema.
- Malformed output is rejected or retried.
- Role output includes node targets.
- Role disagreement is captured.

## Metrics

- Schema-valid role output rate.
- Rejection rate.
- Role disagreement count.
- Unsupported assertion count.

## Contrarian concern

Agent swarm may be theater.

## Mitigation

All roles must produce node-targeted structured fields. Add ablation tests later.

---

# Milestone 5 — Agent-to-node normalizer

## Build

- Mapping from RoleAssessment findings to graph nodes.
- Evidence tier weighting.
- Confidence normalization.
- Future fact leakage rejection.
- Unsupported assertion downgrade.

## Acceptance criteria

- Same node inputs produce same graph result regardless of prose.
- Unsupported evidence cannot drive high-stakes posture.
- Future facts are blocked.
- Node inspector can show source role and evidence tier.

## Metrics

- Normalization success rate.
- Downgraded findings count.
- Future leakage attempts blocked.

---

# Milestone 6 — Prudence graph v0.1

## Build

Graph computes:

- information sufficiency,
- duty-to-inquire strength,
- AI-provenance risk,
- harm clock,
- information clock,
- recoverability,
- future correction opportunity,
- decision weight,
- next-best-input ranking,
- final posture.

Start deterministic, then add Monte Carlo mode if time permits.

## Acceptance criteria

- All POC cases produce final posture.
- Decision weight is visible.
- Next-best-input ranking is visible.
- Graph node values are inspectable.
- Changing a node changes output predictably.

## Metrics

- Receipt completion rate.
- Graph determinism.
- Sensitivity rank availability.

---

# Milestone 7 — Receipt generator

## Build

- SentinelReceipt JSON.
- Human-readable Markdown summary.
- Hash placeholders.
- Version fields.
- Signature placeholder.

## Acceptance criteria

- Every run emits receipt.
- Receipt contains input references, role outputs, graph version, prompt version, model version, evidence version, final posture, decision weight, and next-best inputs.
- Receipt can be reloaded and displayed.

## Metrics

- Receipt completeness.
- Rebuild success rate.

---

# Milestone 8 — Governance Workbench UI

## Build

- Case library.
- Timeline replay.
- Information gap map.
- AI-provenance panel.
- Next-best-input panel.
- Role disagreement panel.
- Graph inspector.
- Receipt viewer.
- Evaluation dashboard.

## Acceptance criteria

- Reviewer can inspect one case end-to-end without reading raw JSON.
- UI shows why posture was selected.
- Receipt export works.

## Metrics

- Case review time.
- UI task completion rate.

---

# Milestone 9 — Evaluation harness

## Build

- Golden expected output files for cases.
- Automated metrics runner.
- Model swap comparison placeholder.
- Role ablation placeholder.

## Acceptance criteria

- POC evaluation report generated.
- Metrics in `validation/01_metrics_and_evaluation_plan.md` are represented.

---

# POC demo script

1. Load case library.
2. Open a case with staged timeline.
3. Move to timepoint where AI-assisted decision is proposed.
4. Show information buckets.
5. Show AI-provenance warning on a decision-critical fact.
6. Show two clocks and decision weight.
7. Show next-best-input ranking.
8. Show role disagreement.
9. Show graph inspector.
10. Export receipt.
11. Explain how same receipt stream becomes future Tribunal substrate.
