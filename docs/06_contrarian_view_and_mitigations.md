# 06 — Contrarian View and Mitigations

This document attacks each major choice. If a concern cannot be mitigated, it becomes a kill criterion or pivot trigger.

## 1. Existing need: AI governance evidence

### Contrarian view

Governance teams may not want decision-level evidence. They may want checklists, vendor attestations, and policy binders because those are cheaper and less politically risky.

### Why it may not fix existing issues

If governance remains procedural, Sentinel may produce artifacts nobody is required to use. The product could be scientifically better but commercially ignored.

### Mitigation

Position the POC as a committee-ready artifact generator mapped to known governance categories: monitoring, transparency, risk controls, lifecycle versioning, and review evidence. Do not sell it as an abstract safety platform. Validate with 3-5 governance/risk/quality stakeholders before writing production code.

### Build implication

The POC must output an audit-ready receipt and summary report, not just internal scores.

---

## 2. Sentinel-first instead of Tribunal-first

### Contrarian view

Prospective review is harder to prove because there may be no outcome yet. Retrospective reconstruction may be more dramatic and easier to demonstrate.

### Why it may not fix existing issues

A prospective system may generate alerts but not prove that anything would have changed. Users may ignore it.

### Mitigation

Build Sentinel in replay/shadow mode. It evaluates staged cases as if prospective, but experts can still judge whether its posture and next-best-input recommendations were reasonable. The receipts become future Tribunal material.

### Build implication

Use replay cases with hidden future states and timepoint-by-timepoint evaluation.

---

## 3. Governance Workbench rather than bedside alerting

### Contrarian view

Governance workbenches are less urgent than clinical workflow tools. Committees may meet monthly; bedside risk happens now.

### Why it may not fix existing issues

It may create after-the-fact dashboards rather than preventing harm.

### Mitigation

The POC is a safe first mode, not the end state. Design all outputs as Sentinel receipts that can later run in live pre-action mode. Use the workbench to validate precision, thresholds, and actionability before live deployment.

### Build implication

Architect `mode = replay | shadow | live`, but implement only replay/shadow in POC.

---

## 4. Prudence calculus instead of disease knowledge

### Contrarian view

Healthcare users may expect clinical expertise, not abstract decision theory. If the system avoids content, it may appear superficial.

### Why it may not fix existing issues

Bad content inputs produce bad warrant outputs. The calculus cannot know which missing facts matter without clinical evidence or parameters.

### Mitigation

Separate content from method. EvidenceFlows provide clinical content, result distributions, and guideline dependencies. The prudence calculus decides how much that information matters now.

### Build implication

POC EvidenceFlows must return structured result distributions, not generic guideline summaries.

---

## 5. Role agents

### Contrarian view

Role agents may hallucinate authority, duplicate each other, or produce theater. A swarm can look impressive while adding no measurable value.

### Why it may not fix existing issues

If agents merely produce prose, the system remains black-box AI checking AI.

### Mitigation

Each role agent has a narrow output contract. The graph ignores prose except as explanation. Role utility is measured by incremental improvement in gap detection, next-best-input ranking, and expert agreement.

### Build implication

Build ablation tests: graph with no role agents, graph with each role, graph with all roles.

---

## 6. Agent-to-node conversion

### Contrarian view

This seam may be impossible to make rigorous. Agents may not reliably provide calibrated values for graph nodes.

### Why it may not fix existing issues

If node values are just hidden prose judgments turned into numbers, transparency is fake.

### Mitigation

Use strict schemas, allowed finding types, source references, calibration priors, rejection rules, and sensitivity analysis. Label unsupported estimates as Tier 3/4 and prevent them from dominating high-stakes verdicts.

### Build implication

Implement schema validation before graph execution. Include tests where malformed or unsupported outputs are rejected.

---

## 7. Belief network / graph verdict

### Contrarian view

The graph may be arbitrary. Stakeholders may challenge weights, thresholds, and formulas.

### Why it may not fix existing issues

A transparent but poorly calibrated graph is still wrong. It could produce false precision.

### Mitigation

Make weights visible, versioned, tiered, and adjustable. In POC, present outputs as distributions and decision postures, not absolute truth. Use expert calibration and sensitivity analysis.

### Build implication

Add node inspector and sensitivity view to UI.

---

## 8. AI-provenance depth

### Contrarian view

Current systems may not preserve enough provenance metadata. Once AI-generated text is signed or copied, source lineage may be lost.

### Why it may not fix existing issues

If provenance cannot be captured, the module may be theoretical.

### Mitigation

For POC, capture provenance prospectively in synthetic/replay cases. Support explicit provenance when available and unknown-provenance risk flags when absent. Treat missing provenance as a governance finding.

### Build implication

Implement `provenance_status = verified | ai_derived | human_reported | structured | unknown`. Unknown should not silently become trusted.

---

## 9. Next-best-information

### Contrarian view

This is data-hungry and may be the hardest module. Ranking missing inputs requires result distributions, likelihoods, and management implications.

### Why it may not fix existing issues

If recommendations are vague, overly broad, or defensive, users will ignore them.

### Mitigation

Start with small curated cases where candidate inputs and result distributions are explicit. Require every recommendation to include decision relevance, burden, expected posture shift, and urgency. Reject generic “obtain more history/labs” outputs.

### Build implication

POC cases must include ground-truth candidate-input tables.

---

## 10. OpenEvidence-style EvidenceFlows

### Contrarian view

External evidence tools may not return the result distributions needed for VOI. They may produce narrative answers rather than graph-ready inputs.

### Why it may not fix existing issues

If evidence retrieval cannot feed structured nodes, it becomes a medical search layer, not Sentinel.

### Mitigation

Use external evidence as a benchmark/source lane but build internal EvidenceFlow contracts requiring structured fields. Manual curation is acceptable in POC.

### Build implication

Implement EvidenceFlow adapters, not hard dependency on one evidence vendor.

---

## 11. Receipts

### Contrarian view

Receipts may be technically elegant but not valued by users until there is a dispute, audit, or incident.

### Why it may not fix existing issues

If the receipt is buried, it becomes overhead.

### Mitigation

Make receipts the core workbench artifact: human-readable summary plus machine-readable hash/provenance details. Include exportable committee report.

### Build implication

Every POC run must create both JSON receipt and readable report.

---

## 12. Human baseline measurement

### Contrarian view

Organizations may resist measuring humans because it creates political and liability discomfort.

### Why it may not fix existing issues

Without human baseline, AI performance remains judged against perfection, and value claims are weak.

### Mitigation

POC uses expert panel comparison and synthetic seeded cases, not clinician surveillance. Later, offer aggregate deidentified baseline metrics.

### Build implication

Evaluation plan must include panel agreement and seeded-case detection.

---

## 13. Real-time deployment later

### Contrarian view

A live Sentinel could cause alert fatigue, workflow disruption, or liability if ignored.

### Why it may not fix existing issues

If it fires too often, it becomes another ignored alert system.

### Mitigation

Do not build live alerts until shadow precision is acceptable. Use decision weight and VOI gating to suppress low-value alerts.

### Build implication

POC metrics must include unnecessary inquiry rate and actionability rate.

---

## 14. Universal method claim

### Contrarian view

“Universal” systems often become vague and fail to solve concrete problems.

### Why it may not fix existing issues

If the first POC is too abstract, no buyer sees their pain solved.

### Mitigation

Use healthcare AI governance as the first concrete wedge, with multiple artifact types to prove generality without becoming abstract.

### Build implication

POC uses 3-5 healthcare decision episodes across different artifact classes, all flowing through the same core.
