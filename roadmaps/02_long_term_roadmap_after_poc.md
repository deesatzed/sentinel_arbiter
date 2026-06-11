# 02 — Long-Term Roadmap After POC

The long-term roadmap depends on POC results. Do not assume all branches are valid until the POC exposes which parts work.

## Phase A — POC review and stakeholder validation

Timing: immediately after POC demo.

Goals:

- Show workbench to 3-5 AI governance/quality/risk stakeholders.
- Show methodology to 2-3 expert clinicians or informatics leaders.
- Test whether receipt output feels committee-credible.
- Identify which modules are valued: provenance, next-best-input, decision weight, role disagreement, receipt, evidence comparison.

Exit criteria:

- Clear signal that at least one buyer persona sees a real problem solved.
- List of must-have vs interesting-only features.
- Refined first production wedge.

## Phase B — Harden methodology

Build:

- More robust agent-to-node conversion.
- Calibration interface for graph parameters.
- Sensitivity analysis.
- Role ablation tests.
- Model-swap stability tests.
- EvidenceFlow result-distribution improvements.

Success criteria:

- Changing extractor model does not frequently change final posture without visible cause.
- Role agents add measurable value over graph-only baseline.
- Next-best-input recommendations are actionable and not overly defensive.

## Phase C — Expand case library and artifact adapters

Build:

- 25-50 replay cases.
- At least 5 artifact adapters.
- Case generator for synthetic scenarios.
- Domain parameter packs.

Artifact classes:

1. Clinical recommendation.
2. Patient-facing response / triage.
3. Follow-up or care-management plan.
4. Agentic action request.
5. Utilization / coverage / medical necessity rationale.
6. Summary-derived recommendation.
7. Scheduling/access recommendation.

Success criteria:

- New artifact type requires adapter changes only.
- Existing node library reused.
- Case library supports evaluation across categories.

## Phase D — EvidenceFlow integration

Build:

- External evidence source adapter.
- Internal retrieval/evidence lane.
- Evidence source comparator.
- Result-distribution extraction.
- Evidence staleness timers.

Success criteria:

- EvidenceFlow outputs graph-ready fields.
- Citation/source lineage is captured.
- Disagreement between evidence sources is visible.
- Evidence source updates are versioned.

## Phase E — Governance productization

Build:

- Organization-level dashboard.
- Review queue.
- Committee reports.
- Export packages.
- Audit trail.
- Model/version registry.
- AI-provenance census.

Success criteria:

- Governance team can review AI-assisted decisions as a program, not one case at a time.
- Reports map to monitoring, risk assessment, evidence review, transparency, and lifecycle governance.

## Phase F — Shadow-mode pilot with partner data

Precondition:

- Legal/privacy path is clear.
- Partner agrees to deidentified or internal secure deployment.
- No live clinical decision use.

Build:

- Secure ingestion.
- Local data adapters.
- Provenance capture where available.
- Human reviewer feedback loop.
- Baseline measurement.

Success criteria:

- Workbench runs on real historical or shadow data.
- Precision/recall for material gaps is measured.
- Stakeholders confirm actionability.

## Phase G — Prospective monitoring pilot

Precondition:

- Shadow precision acceptable.
- Governance stakeholders approve prospective noninterruptive monitoring.

Build:

- Near-real-time run mode.
- Review queue, not pop-up alerts.
- High decision-weight routing.
- Human-in-the-loop adjudication.

Success criteria:

- Low alert burden.
- High actionability.
- Useful human review routing.
- No unsafe automation.

## Phase H — Limited live Sentinel gate

Precondition:

- Strong validation.
- Clear governance approval.
- Defined artifact classes.
- Legal and clinical safety review.

Build:

- Pre-action warrant check for limited AI agent actions.
- Hard stops only for narrow, high-confidence failures.
- Soft flags for lower-confidence gaps.
- Receipt-based monitoring.

Success criteria:

- Live use improves process measures without unacceptable burden.
- False positives controlled.
- Human override documented.

## Phase I — Tribunal mode

Build:

- Retrospective outcome-blinded reconstruction.
- Sentinel receipt ingestion.
- Forensic timeline view.
- Root-cause analysis support.
- Peer-review artifact package.

Success criteria:

- Tribunal can reconstruct cases using Sentinel receipts.
- Hindsight leakage blocked.
- Human reviewers find reconstruction credible.

## Phase J — Cross-domain generalization

Build:

- Non-healthcare EvidenceFlow/threshold packs.
- Operational risk decision pack.
- Financial/coverage decision pack.
- Safety-critical agent action pack.

Success criteria:

- Same prudence calculus works with swapped EvidenceFlows and thresholds.
