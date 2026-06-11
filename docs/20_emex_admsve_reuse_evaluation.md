# EMEX And AdmSVE Reuse Evaluation

Date: 2026-06-11

## Purpose

This note evaluates the sibling repositories `../EMEX` and `../AdmSVE` as reference implementations for moving Sentinel from a deterministic framework/workbench into a first real demo where constructed or approved deidentified clinical input can be entered, processed, audited, and reviewed.

This is a reuse evaluation, not a code import. EMEX and AdmSVE were inspected read-only.

## Verification Snapshot

Both sibling repositories are git repositories on `main` tracking `origin/main`.

EMEX verification:

```bash
cd /Volumes/WS4TB/Sentinel_Arbiter/EMEX
PYTHONPATH=src uv run --no-project --with pytest python -m pytest -q
```

Result: `21 passed in 0.06s`.

AdmSVE verification:

```bash
cd /Volumes/WS4TB/Sentinel_Arbiter/AdmSVE
PYTHONPATH=src:. uv run --no-project --with pytest --with fastapi --with uvicorn --with httpx python -m pytest -q
```

Result: `134 passed in 0.46s`.

The first direct `python3 -m pytest -q` attempts failed only because the active Homebrew Python 3.14 environment did not have `pytest` installed. The `uv run --no-project` verification path avoided creating project virtualenvs or lockfiles inside the sibling repositories.

## High-Level Fit

AdmSVE is the stronger primary donor for Sentinel's next demo layer. It already has a local FastAPI app, redaction-before-analysis flow, structured intake extraction, deterministic fallback behavior, status-conformance judging, integrity gating, tiered provenance output, metrics, HTML reporting, and hash-chained trace patterns.

EMEX is a strong secondary donor for a compact, artifact-first demo loop. It has a clean prepare/ingest workflow, copy-ready analysis packet generation, manual outside-prose ingestion, conservative parsing, static HTML reporting, a PI summary artifact, and a simple hash-chained trace.

Neither repo should be copied wholesale into Sentinel. Sentinel's method is different: the graph computes governance posture from node estimates, evidence, uncertainty, role disagreement, and provenance. Admission-status semantics, ED engagement suggestions, and any order-like output language must remain outside Sentinel's final output vocabulary.

## Components Worth Adapting

### From AdmSVE

1. Local demo app pattern

   Source pattern: `src/admission_engine/app/server.py`

   Adaptation for Sentinel:

   - Add a local app with endpoints for input redaction, case intake, reviewer correction, deterministic analysis run, receipt retrieval, and workbench review.
   - Keep the deterministic CLI as the authoritative verification path.
   - Treat app output as a review surface over generated artifacts, not as a bedside action tool.

2. Redaction floor and redaction abstraction

   Source pattern: `src/admission_engine/redaction/base.py`, `src/admission_engine/redaction/deterministic.py`

   Adaptation for Sentinel:

   - Reuse the `Redactor` abstraction shape, deterministic span merging, and fail-closed residual PII checks.
   - Add Sentinel-specific input gates before converting free text into a `DecisionEpisode`.
   - Keep optional model or MCP-backed redaction as a later backend, not a first-demo requirement.

3. Intake extraction with deterministic fallback

   Source pattern: `src/admission_engine/intake/extractor.py`

   Adaptation for Sentinel:

   - Convert constructed/deidentified clinical text into a draft `DecisionEpisode`.
   - Preserve a reviewer-edit step before analysis.
   - Require timepoint tagging and explicitly mark unknown, missing, inferred, and weakly sourced facts.
   - Never invent outcome facts or future facts.

4. Hash-chained trace

   Source pattern: `src/admission_engine/trace.py`

   Adaptation for Sentinel:

   - Add trace events for redaction, intake extraction, reviewer edits, node computation, ensemble contribution, rejected findings, downgraded findings, final posture, and receipt emission.
   - Keep deterministic clock injection for reproducible synthetic/demo runs.

5. Tiered, provenance-carrying output

   Source pattern: `src/admission_engine/output/tiered_output.py`

   Adaptation for Sentinel:

   - Use the tier/source/basis/supporting-evidence/strength pattern as the seed for node-level evidence cards.
   - Replace admission-status-specific fields with Sentinel node estimates, uncertainty ranges, conflicts, and graph posture explanation.

6. Metrics and HTML report surface

   Source pattern: `src/admission_engine/metrics/harness.py`, `src/admission_engine/report.py`

   Adaptation for Sentinel:

   - Extend Sentinel's current validation report into a demo dashboard with node-level auditability.
   - Add distribution calibration checks, evidence-completeness checks, leakage checks, role-disagreement checks, and receipt-completeness checks.

### From EMEX

1. Artifact-first prepare/ingest workflow

   Source pattern: `src/emex/workflow.py`

   Adaptation for Sentinel:

   - Add a two-stage demo flow:
     - `prepare-input`: redacts, validates, hashes, extracts, and emits a reviewer-editable packet.
     - `run-review`: computes nodes, ensemble contributions, graph posture, and receipts.
   - Keep every stage reconstructable from artifacts.

2. Manual companion-mode prose ingestion

   Source pattern: `src/emex/oe_output.py`

   Adaptation for Sentinel:

   - If Sentinel later supports OpenEvidence-like or LLM companion prose, parse it as evidence input only.
   - Use conservative parsing, safety flags, parse warnings, and explicit rejection of action-like imperatives.
   - Preserve a fallback path for plain Markdown or labeled text.

3. Packet builder and leakage report

   Source pattern: `src/emex/oe_packet.py`, `src/emex/contracts.py`

   Adaptation for Sentinel:

   - Build an analysis packet from the redacted current-time view, not from hidden outcomes.
   - Include input hash, leakage findings, redaction report, timepoint boundary, and schema version.

4. Static HTML demo style

   Source pattern: `web/index.html`, `src/emex/reporting.py`

   Adaptation for Sentinel:

   - Reuse the single-page, no-build demo approach if a full FastAPI app is too much for the next step.
   - Sentinel already has `data/workbench/index.html`; the more important borrow is EMEX's simple three-step flow: input, package, review.

## Components Not To Borrow Directly

- AdmSVE's admission-status semantics, predicted status, criteria labels, and case-specific status conformance fields.
- EMEX's ED engagement suggestion semantics or any output that can be read as an instruction to take a clinical action.
- Any repo-specific clinical threshold, proprietary criteria proxy, or utilization-review-specific wording.
- Any live external LLM or evidence-service mode before Sentinel has a tested redaction, reviewer-edit, trace, and receipt boundary.

## Methodology Transparency Gap

The user's trust requirement is broader than either donor repo currently implements.

AdmSVE has the best starting pieces: likelihood fields, calibration bins, tiered output, provenance, supporting evidence, and integrity suppression. EMEX has a clear artifact trace and conservative prose-ingest boundary. However, neither repo fully implements Sentinel's needed transparent node methodology:

- chosen dependent nodes,
- evidence for each node,
- source provenance for each evidence item,
- probability distribution or score distribution per node,
- range and median per node,
- method used to estimate each node,
- ensemble contribution and disagreement per node,
- accepted, rejected, or downgraded findings,
- sensitivity of final posture to uncertain nodes.

Sentinel needs a native audit layer rather than a direct transplant.

## Proposed Sentinel Audit Objects

The next demo should add these Sentinel-native objects:

```text
NodeDefinition
  id
  lane
  question
  dependent_inputs
  output_scale
  version

NodeEvidence
  ref_id
  node_id
  source_type
  source_timepoint
  quoted_or_structured_fact
  provenance
  supports
  weight
  quality
  limitations

NodeEstimate
  node_id
  value
  range_min
  range_max
  median
  distribution_kind
  confidence
  method
  evidence_refs

EnsembleContribution
  node_id
  contributor_role
  proposed_value
  proposed_range_min
  proposed_range_max
  evidence_refs
  rationale
  disposition
  disposition_reason

NodeAudit
  node_id
  definition_version
  dependencies
  evidence
  estimate
  ensemble_contributions
  conflicts
  sensitivity_note
```

This is the missing bridge from "the app ran" to "a reviewer can see why each node moved, which evidence mattered, what range was plausible, and how the ensemble affected the final posture."

## Recommended Demo Architecture

1. Input stage

   - User enters constructed or approved deidentified clinical text.
   - Sentinel applies deterministic redaction and residual-risk scanning.
   - The system blocks or quarantines risky input before analysis.

2. Intake stage

   - Text becomes a draft `DecisionEpisode`.
   - The reviewer edits timepoints, facts, missing data, therapy response, follow-up reliability, and provenance labels.
   - The reviewer must approve the structured episode before the graph runs.

3. Analysis stage

   - Current deterministic graph computes existing Sentinel nodes.
   - New node-audit objects attach evidence, range, median, method, and confidence.
   - Static ensemble roles contribute bounded estimates and rationales.
   - Conflicts are surfaced rather than hidden.

4. Review stage

   - The workbench shows the original redacted input, structured episode, node cards, distributions, role disagreement, graph posture, and receipts.
   - The output remains a governance review artifact, not a clinical order or direct patient-specific instruction.

5. Receipt stage

   - JSON and Markdown receipts include node audit, evidence refs, estimate distributions, rejected findings, downgraded findings, role disagreement, posture, and trace hashes.

## Recommended Build Order

1. Borrow AdmSVE's redaction abstraction and deterministic floor pattern into Sentinel as a new `sentinel_workbench.redaction` module.
2. Add a constructed-text intake command that emits a draft `DecisionEpisode` and a redaction report.
3. Add reviewer-editable intake artifacts before any app endpoint.
4. Add Sentinel-native node audit objects and tests for range, median, evidence refs, and ensemble contribution.
5. Extend receipts and `data/workbench/index.html` to show node methodology transparently.
6. Add a local FastAPI app only after the CLI and artifact path are verified.
7. Optionally add EMEX-style manual companion prose ingestion as evidence input, with strict parsing and downgrade rules.

## Test Strategy For The Demo

Minimum tests before calling the next demo real:

- Redaction runs before intake extraction.
- Residual PII patterns block or quarantine input.
- Constructed clinical input can become a valid `DecisionEpisode`.
- Reviewer-edited draft episodes validate against schema.
- Hidden future facts cannot enter node computation.
- Every graph node has a `NodeAudit`.
- Every `NodeAudit` has evidence refs, range, median, method, confidence, and dependency list.
- Every ensemble contribution is either accepted, rejected, or downgraded with a reason.
- The workbench renders node evidence, range, median, and role disagreement.
- Receipt JSON and Markdown include methodology details.
- Forbidden clinical-action phrasing remains absent from generated outputs.

## Bottom Line

AdmSVE should be treated as the main implementation donor for the next local app and input-processing layer. EMEX should be treated as the donor for a simple artifact-first demo workflow and conservative outside-prose ingestion.

Sentinel still needs its own methodology layer for node definitions, node evidence, distributions, ranges, medians, and ensemble audit. That layer should be built natively because it is the core trust surface the user is asking for.
