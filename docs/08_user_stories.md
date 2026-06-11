# 08 — User Stories

## Primary persona: AI governance reviewer

### Story 1 — Review a proposed AI-assisted decision

As an AI governance reviewer, I want to load a replay case and see whether the proposed action was warranted at each timepoint, so that I can evaluate whether the AI-assisted workflow has adequate monitoring.

Acceptance criteria:

- Case loads without live data.
- Timepoint selector changes visible information state.
- Future information is hidden unless explicitly in Tribunal/debug mode.
- Final posture and decision weight are visible.

### Story 2 — Inspect information gaps

As a governance reviewer, I want to see which missing facts mattered to the current decision, so that I can distinguish useful review from defensive over-investigation.

Acceptance criteria:

- Gaps are categorized as decision-relevant or low-value.
- Each relevant gap includes expected posture shift and burden.
- Low-value gaps are not escalated by default.

### Story 3 — Understand AI-derived evidence reliance

As a governance reviewer, I want to know when a decision relies on unverified AI-derived information, so that I can assess compounding error risk.

Acceptance criteria:

- Critical facts show provenance category.
- Unverified AI-depth is displayed.
- Primary-source confirmation need is flagged when decision weight is high.

### Story 4 — See what to do next

As a reviewer, I want Sentinel to identify the highest-value next input, so that the output is actionable rather than just critical.

Acceptance criteria:

- Candidate inputs are ranked.
- Each input includes expected posture shift, urgency, burden, and rationale.
- Generic recommendations are rejected or marked low quality.

### Story 5 — Export committee-ready evidence

As a committee member, I want a readable receipt and summary report, so that the review can be stored, discussed, and compared across cases.

Acceptance criteria:

- JSON receipt is exportable.
- Human-readable summary is exportable.
- Versions and source references are included.
- Role disagreement is visible.

## Secondary persona: clinical informatics builder

### Story 6 — Add a new artifact adapter

As a clinical informatics builder, I want to add a new artifact type without changing the core graph, so that the system remains general.

Acceptance criteria:

- Adapter maps input to DecisionEpisode.
- Core graph does not need modification.
- New artifact type appears in workbench.

### Story 7 — Tune node parameters

As a builder, I want to inspect and adjust node weights/thresholds, so that the system can be calibrated without rewriting prompts.

Acceptance criteria:

- Node library is versioned.
- Parameters are visible.
- Changes create a new graph version.
- Receipts reference graph version.

## Secondary persona: risk/legal reviewer

### Story 8 — Reconstruct why a case was flagged

As a risk reviewer, I want to reconstruct the full logic of a Sentinel verdict, so that I can assess defensibility and auditability.

Acceptance criteria:

- Receipt includes input hashes.
- Receipt includes prompt/model/source versions.
- Role findings and graph nodes are available.
- Final posture can be traced to visible inputs.

## Secondary persona: product evaluator

### Story 9 — Compare model versions

As a product evaluator, I want to run the same case through different extractor/agent models while holding the graph fixed, so that I can measure model-swap stability.

Acceptance criteria:

- Runs record model versions.
- Output differences are compared.
- Graph-level stability is reported.
