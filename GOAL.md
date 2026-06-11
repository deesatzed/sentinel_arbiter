# GOAL.md

## Outcome

Build Sentinel into a local, trustworthy governance workbench where a reviewer can paste or upload redacted clinical-style input, choose the review question, inspect the methodology before analysis, run the ensemble, and receive a concise clinician-readable governance summary with a deeper audit trail available on demand.

The next milestone is no longer just a deterministic framework or a raw artifact demo. It is a clinician-facing staged local app where a reviewer can:

1. choose one of two review questions:
   - A. Is there enough information to make a disposition decision?
   - B. Is there enough information to use this AI-generated response?
2. paste redacted text or upload a constructed or governance-approved deidentified file,
3. click `Pre-process` to run redaction, intake, timepoint extraction, and residual-risk checks before analysis,
4. review the generated Node Audit Methodology before graph execution,
5. accept the methodology or adjust and re-check one or more nodes with an explicit confirmation step,
6. review Ensemble Contributions before final processing,
7. click `Process` and see the deterministic ensemble analysis run,
8. receive a usable clinician-facing summary that explains what the result means and why in no more than one or two short paragraphs,
9. open a `Deeper Dive` view for node evidence, ranges, medians, distributions, ensemble disagreements, trace receipts, validation status, and raw structured artifacts.

Sentinel remains a governance and review workbench. It must not become a bedside alert system, autonomous disposition agent, diagnosis recommender, prescribing tool, ordering tool, clearance tool, patient-facing advice product, or clinical outcome-claim engine.

## Current Baseline

The repository already contains a deterministic ED disposition replay POC with:

- an installable local Python package,
- seven synthetic ED replay cases,
- explicit T0 through T4 timepoints,
- future-leakage prevention,
- deterministic graph nodes,
- first-class commission, omission, and therapy-response lanes,
- static role and EvidenceFlow inputs,
- JSON and Markdown receipts,
- a generated static reviewer workbench at `data/workbench/index.html`,
- validation reports under `validation/reports/`,
- safety and pre-real-use boundary documentation.

The new work must build on that baseline instead of replacing it.

## Next Milestone

The next milestone is the clinician-facing staged local demo:

- constructed or approved deidentified input can be pasted or loaded,
- the landing page explains and enforces review question A or B before input is analyzed,
- redaction happens before any intake or model-like analysis,
- residual PII/PHI risk blocks or quarantines input,
- intake extraction creates a structured draft rather than a final judgment,
- a reviewer can inspect and edit the structured case and Node Audit Methodology before analysis,
- the reviewer can approve, adjust, or re-check selected nodes before processing,
- Ensemble Contributions are shown before final graph execution,
- every computed node exposes its dependencies and evidence,
- every node estimate includes value, range, median, distribution kind, confidence, method, and evidence references,
- static ensemble contributors produce bounded estimates and rationales,
- accepted, rejected, and downgraded findings are visible,
- graph posture is computed from typed nodes, not from prose or prompt authority,
- the first result is a concise, clinically usable governance summary rather than raw JSON,
- a deeper-dive view exposes the full methodology, receipts, and validation artifacts for skeptical review.

## Clinician-Facing UX Contract

The app's first screen must be the real review workflow, not a generic landing page or marketing page.

The first screen must explain two choices in plain language:

- `A - Disposition Information Sufficiency`: review whether the available information is enough to support a documented disposition decision discussion.
- `B - AI Response Use Sufficiency`: review whether the available information is enough to trust or use an AI-generated clinical response as governance-reviewed input.

The selected choice must follow the run:

- it must be saved in the run manifest and receipts,
- it must influence the wording of the clinician-facing summary,
- it must not bypass the same redaction, reviewer approval, node audit, ensemble, and receipt requirements,
- it must not create direct clinical action instructions.

The reviewer journey must be staged:

1. `Choose`: select review question A or B.
2. `Input`: paste redacted text or upload a local constructed/deidentified file.
3. `Pre-process`: run redaction, residual-risk checks, structured intake, timepoint extraction, and draft node methodology.
4. `Node Audit`: show dependent nodes, evidence, missing inputs, probability or score distribution, range, median, method, confidence, and limitations.
5. `Review`: allow `OK`, `Adjust`, or `Re-check selected nodes`. Any adjustment must show an `Are you sure?` confirmation before replacing generated methodology.
6. `Ensemble`: show role and EvidenceFlow contributions, accepted/downgraded/rejected status, disagreement, and rationale.
7. `Process`: run deterministic graph analysis only after the reviewer checkpoint.
8. `Summary`: show a short clinician-readable governance interpretation first.
9. `Deeper Dive`: show complete audit tables, receipts, trace hashes, validation report, structured episode, and raw JSON/Markdown artifacts.

The summary result must be written for clinician review:

- no raw JSON as the first visible answer,
- no unexplained internal node names as the first visible answer,
- no more than one or two short paragraphs,
- explicitly state what the result means for the selected review question,
- briefly name the main uncertainty drivers and evidence gaps,
- state that the output is governance review support, not a clinical action recommendation.

## Source Of Truth

Before coding, read these project files if present:

1. `GOAL.md`
2. `STANDARDS.md`
3. `IMPLEMENT.md`
4. `DECISIONS.md`
5. `PROGRESS.md`
6. `TASK_QUEUE.md`

Treat these files as project source of truth. If implementation behavior and these files diverge, update the docs or implementation so the divergence is explicit and tested.

## Reference Repositories

The sibling repositories `../EMEX` and `../AdmSVE` are reference-only donors unless code is intentionally copied into Sentinel with provenance notes and tests.

AdmSVE is the primary donor for:

- local FastAPI app pattern,
- redaction abstraction and deterministic redaction floor,
- intake extraction with deterministic fallback,
- redaction-before-analysis workflow,
- hash-chained trace,
- tiered provenance output,
- metrics and report surfaces.

EMEX is the secondary donor for:

- artifact-first prepare/ingest workflow,
- manual companion-mode prose ingestion,
- packet building,
- leakage reporting,
- conservative parsing,
- static HTML demo flow.

Do not borrow directly:

- admission-status semantics,
- ED engagement suggestion semantics,
- criteria/proprietary threshold proxies,
- output that could be read as an action instruction,
- live external LLM or evidence-service behavior before Sentinel's local redaction, reviewer-edit, trace, and receipt boundaries are tested.

The current reuse evaluation is saved in `docs/20_emex_admsve_reuse_evaluation.md`.

## Core Safety Boundary

Allowed input for this milestone:

- synthetic clinical input,
- constructed clinical input,
- deidentified-style examples,
- governance-approved deidentified examples only after redaction and policy gates exist.

Disallowed input:

- raw PHI,
- real patient charts,
- credentials,
- private keys,
- proprietary benchmark data,
- named clinical institution data unless already public and explicitly appropriate,
- any sensitive material that cannot be safely committed to the repository.

Sentinel must not tell clinicians to admit, discharge, diagnose, prescribe, order, clear, or choose a patient-specific clinical action.

Do not use phrases that imply a disposition recommendation, including:

- safe to discharge
- unsafe to discharge
- should admit
- should discharge
- medically cleared
- appropriate for discharge
- inappropriate for discharge
- recommended pathway
- preferred pathway

Keep generated outputs framed as governance review, retrospective warrant analysis, documentation-integrity review, shared-decision support framing, and committee-ready evidence.

## Methodology And Trust Layer

The central trust requirement is that a reviewer can see how Sentinel got from input to output.

Every analysis run must be explainable through these native Sentinel objects or their schema equivalents:

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

The workbench and receipts must expose:

- chosen dependent nodes,
- evidence for each node,
- source provenance for each evidence item,
- probability or score distribution per node,
- range and median per node,
- method used to estimate each node,
- ensemble contribution and disagreement per node,
- accepted, rejected, or downgraded findings,
- sensitivity of final posture to uncertain nodes.

## Required Demo Workflow

### 1. Landing And Choice Stage

Purpose: orient the reviewer to the exact governance question before any input is processed.

Requirements:

- show the two review choices as the first meaningful interaction,
- require exactly one selected choice before `Pre-process` is enabled,
- explain each choice in plain language without clinical recommendation language,
- persist the selected choice into the run manifest, receipt, and summary,
- keep visible POC and non-clinical-use warnings without making them the whole page.

### 2. Input Stage

Purpose: accept constructed or approved deidentified input without letting risky text flow directly into analysis.

Requirements:

- provide a local app paste/upload path as the primary demo path,
- keep the deterministic CLI path as the authoritative verification path,
- accept pasted redacted text and local file upload,
- apply deterministic redaction before intake,
- emit a redaction report,
- block or quarantine residual PII/PHI patterns,
- hash the original local input without exposing it in generated review artifacts,
- preserve a redacted review copy.

### 3. Pre-process And Intake Stage

Purpose: convert redacted input into a structured draft case without inventing facts.

Requirements:

- expose a `Pre-process` control in the app,
- run redaction, residual-risk checking, intake extraction, timepoint tagging, and draft node-methodology construction before analysis,
- create a draft `DecisionEpisode`,
- tag facts by timepoint,
- mark missing, unknown, inferred, weakly sourced, and reviewer-supplied fields,
- reject hidden future facts from current-time evaluation,
- require reviewer approval or confirmation before graph execution,
- save the reviewer-approved structured episode as an artifact.

### 4. Node Audit Stage

Purpose: make every dependent node inspectable.

Requirements:

- display the Node Audit Methodology immediately after pre-processing and before final processing,
- define node dependencies explicitly,
- attach evidence references to node estimates,
- compute or assign value, range, median, distribution kind, confidence, and method,
- distinguish deterministic fixture-derived estimates from static role-derived or future LLM-derived estimates,
- record conflicts and sensitivity notes,
- allow a reviewer to approve the methodology, adjust reviewer-editable fields, or request re-check for selected nodes,
- require an `Are you sure?` confirmation before accepting reviewer adjustments that change node inputs, evidence disposition, or estimates.

### 5. Ensemble Stage

Purpose: make role and EvidenceFlow influence transparent.

Requirements:

- display Ensemble Contributions before the reviewer clicks `Process`,
- static ensemble contributors must emit bounded proposed values and rationales,
- each contribution maps to allowed node IDs only,
- each contribution is accepted, rejected, or downgraded with a reason,
- disagreements must be visible in plain language and in audit tables,
- graph posture must remain deterministic from normalized typed inputs,
- no role or prompt may decide the final posture.

### 6. Process And Summary Stage

Purpose: make the result understandable to a clinician reviewer before exposing detailed audit artifacts.

Requirements:

- provide a visible `Process` control after the reviewer has seen Node Audit Methodology and Ensemble Contributions,
- show progress or step status while the deterministic pipeline runs,
- show the summary result first,
- keep the summary to one or two short paragraphs,
- state what the result means for the selected review question,
- explain the main reasons and uncertainty drivers,
- avoid raw JSON, unexplained internal labels, and disposition recommendation language in the primary summary,
- provide a clear `Deeper Dive` button for complete methodology.

### 7. Receipt Stage

Purpose: make the result reconstructable.

Requirements:

- emit JSON receipts,
- emit human-readable Markdown or HTML receipts,
- include input hashes, redaction report refs, timepoint ID, schema versions, prompt or dotflow versions, model versions if any, evidence versions if any, node audits, graph posture, decision weight, disagreement map, downgraded findings, rejected findings, and signature placeholder,
- include trace hashes for the run sequence,
- keep receipts free of raw PHI.

### 8. Workbench And Deeper Dive Stage

Purpose: make the demo usable without reading raw JSON.

Requirements:

- use the app as the first review surface,
- show redacted input and structured episode,
- show timeline replay,
- show node cards with evidence, range, median, distribution kind, confidence, and method,
- show ensemble contribution and disagreement,
- show graph posture and sensitivity notes,
- show generated receipts,
- show validation status and warnings,
- allow the reviewer to open raw structured artifacts only from the deeper-dive view,
- keep visible POC and non-clinical-use warnings.

### 9. Optional Companion Prose Stage

Purpose: allow future OpenEvidence-like or LLM prose to become structured evidence input without handing it authority.

Requirements:

- parse companion prose conservatively,
- treat parsed prose as evidence input only,
- flag unsafe or action-like imperative language,
- require schema validation,
- downgrade unsupported claims,
- keep deterministic mode fully functional without this stage.

## Full Demo Proof Of Done

The clinician-facing staged local demo is complete only when all of the following are true:

1. A user can open the local app and choose either review question A or B before input is processed.
2. The selected review question is saved into the run manifest, receipts, and summary.
3. A user can paste redacted text or upload a constructed/deidentified local file and click `Pre-process`.
4. A user can run a local CLI command with constructed text input and receive a redaction report plus draft structured episode.
5. Residual PII/PHI risk is detected and blocks or quarantines unsafe input.
6. A reviewer-approved structured episode can be saved and used for deterministic analysis.
7. Synthetic and constructed demo inputs validate against schemas.
8. Hidden future facts cannot enter current-time node computation.
9. Every graph node has a `NodeAudit` or equivalent schema-backed audit object.
10. Every node audit has dependencies, evidence refs, value, range, median, distribution kind, confidence, method, and sensitivity note.
11. The app displays Node Audit Methodology after pre-processing and before processing.
12. A reviewer can choose `OK`, `Adjust`, or `Re-check selected nodes`; adjustments require confirmation before replacing generated methodology.
13. Every ensemble contribution is accepted, rejected, or downgraded with a reason.
14. The app displays Ensemble Contributions before `Process`.
15. The graph computes final Sentinel posture from normalized typed node values.
16. Final posture remains one of the Sentinel posture categories, not a disposition recommendation.
17. The primary result is a clinician-readable governance summary of no more than one or two short paragraphs.
18. The primary summary explains what the result means for the selected review question and why, including the main uncertainty drivers.
19. A `Deeper Dive` button exposes node audit tables, ensemble tables, receipts, trace hashes, validation status, structured episode, and raw JSON/Markdown artifacts.
20. JSON receipts include selected review question, redaction, intake, node audit, ensemble, trace, graph, and signature-placeholder fields.
21. Human-readable receipts explain what was known, what was missing, what would have changed the discussion, what facility-based monitoring or treatment might add, what non-inpatient alternatives might add, commission concerns, omission concerns, therapy-response concerns, and why the graph selected the posture.
22. The workbench renders the redacted input, structured episode, node methodology, distributions, range, median, ensemble disagreement, graph posture, clinician summary, deeper-dive artifacts, receipts, and validation status.
23. Automated validation reports cover schema validity, future leakage, redaction gating, expected posture agreement on fixtures, omission detection, commission warning detection, therapy-response integration, next-best-information usefulness, node-audit completeness, receipt completeness, workbench completeness, app-flow completeness, summary completeness, and forbidden phrase violations.
24. The project documents what is implemented, what is deferred, and what would be required before any real clinical, prospective, production, or live-evidence use.
25. Full local verification commands pass and `git diff --check` is clean.

## Phase Plan

### Phase A - Goal And Roadmap Refresh

Purpose: align the project source of truth with the new clinician-facing staged-demo milestone.

Deliverables:

- refreshed `GOAL.md`,
- updated progress notes,
- optional roadmap issue/task breakdown,
- documented reuse strategy for EMEX and AdmSVE.

Acceptance criteria:

- goal explicitly covers constructed/deidentified input, A/B review choice, redaction, intake, node audit, ensemble transparency, summary-first UX, deeper dive, workbench, receipts, and safety boundaries,
- current deterministic POC is preserved as the baseline.

### Phase B - Redaction And Constructed-Input Intake

Purpose: create a safe path from text input to structured draft episode.

Deliverables:

- `sentinel_workbench.redaction` module,
- deterministic redaction floor,
- residual-risk checker,
- redaction report schema,
- constructed-text intake command,
- draft episode artifact.

Acceptance criteria:

- redaction runs before intake,
- unsafe residual patterns block or quarantine input,
- safe constructed text can produce a draft `DecisionEpisode`,
- tests cover pass, block, and quarantine cases.

### Phase C - Reviewer Approval And Artifact Workflow

Purpose: make structured input reviewer-controlled before analysis.

Deliverables:

- reviewer-editable draft artifact,
- reviewer-approved episode artifact,
- validation command for approved episodes,
- trace events for draft, edit, and approval.

Acceptance criteria:

- analysis refuses unapproved draft input,
- reviewer edits are traceable,
- approved episodes validate against schema,
- raw input is not copied into receipts.

### Phase D - Node Audit Methodology

Purpose: implement the native trust layer.

Deliverables:

- `NodeDefinition`,
- `NodeEvidence`,
- `NodeEstimate`,
- `EnsembleContribution`,
- `NodeAudit`,
- schema exports,
- node audit builder,
- validation coverage.

Acceptance criteria:

- every existing graph node emits a node audit,
- ranges and medians are present,
- evidence refs resolve,
- unsupported evidence cannot dominate a node,
- sensitivity notes are visible.

### Phase E - Ensemble Transparency

Purpose: convert static role and EvidenceFlow influence into inspectable bounded contributions.

Deliverables:

- ensemble contribution normalization,
- accept/reject/downgrade logic,
- role disagreement map by node,
- tests for malformed or unsupported contributions.

Acceptance criteria:

- every contribution maps to allowed node IDs,
- every contribution receives a disposition and reason,
- graph posture remains deterministic,
- prompts or prose cannot directly choose final posture.

### Phase F - Receipts And Workbench Upgrade

Purpose: make methodology visible to reviewers.

Deliverables:

- receipt schema updates,
- Markdown receipt updates,
- workbench node-audit panels,
- methodology/distribution views,
- validation report updates.

Acceptance criteria:

- receipts include node audit and ensemble audit,
- workbench renders evidence, range, median, confidence, method, and disagreement,
- generated artifacts remain local and free of raw PHI,
- forbidden phrase checks pass.

### Phase G - Local App Demo

Purpose: preserve the current local app as the safe app substrate after the CLI and artifact workflow are safe.

Deliverables:

- local stdlib, FastAPI, or equivalent app,
- input/redaction endpoint,
- intake endpoint,
- reviewer approval endpoint or local form workflow,
- analysis endpoint,
- receipt/workbench endpoint,
- startup command in README.

Acceptance criteria:

- a reviewer can run the app locally,
- constructed input can be entered and processed,
- output can be reviewed in the workbench,
- the deterministic CLI remains the authoritative verification path,
- no external service is required.

### Phase H - Clinician-Facing Staged UX Rebuild

Purpose: turn the technical local demo into the staged clinician-facing workflow described in the UX contract.

Deliverables:

- first-screen review-question selector for A and B,
- plain-language explanation for both review choices,
- paste/upload input panel,
- `Pre-process` button and pre-process status,
- staged app state machine for `Choose`, `Input`, `Pre-process`, `Node Audit`, `Ensemble`, `Process`, `Summary`, and `Deeper Dive`,
- run manifest field for the selected review question,
- README startup and demo instructions.

Acceptance criteria:

- the app cannot pre-process input until A or B is selected,
- the selected review question follows the run into generated artifacts,
- the first user-visible workflow is the real demo, not a static report page,
- existing CLI and receipt tests continue to pass.

### Phase I - Reviewer Node Audit Adjustment And Re-check Loop

Purpose: make the pre-analysis trust checkpoint interactive enough to support reviewer trust without letting it bypass provenance.

Deliverables:

- Node Audit Methodology review screen,
- `OK`, `Adjust`, and `Re-check selected nodes` controls,
- confirmation prompt for methodology-changing adjustments,
- adjustment manifest or trace events,
- re-check result display for selected nodes,
- tests for approve, adjust-confirm, adjust-cancel, and re-check flows.

Acceptance criteria:

- graph processing refuses to run before the node-audit checkpoint is satisfied,
- reviewer adjustments are recorded separately from generated facts,
- re-checks do not invent unsupported facts,
- adjustments and re-checks remain visible in receipts or deeper-dive artifacts.

### Phase J - Clinician Summary And Deeper Dive

Purpose: make the result meaningful on first read while preserving full transparency for skeptical review.

Deliverables:

- clinician-readable summary renderer,
- selected-review-question-specific summary framing,
- concise uncertainty-driver extraction,
- visible `Deeper Dive` button,
- deeper-dive view for node tables, ensemble tables, receipts, trace hashes, validation report, structured episode, and raw artifacts,
- summary completeness validation.

Acceptance criteria:

- the first visible result is not raw JSON,
- the summary is no more than one or two short paragraphs,
- the summary explains what the result means and why for the selected review question,
- the deeper-dive view contains every methodology artifact needed to reconstruct the run,
- forbidden phrase and non-clinical-use checks pass.

### Phase K - Optional Companion Prose Or LLM Mode

Purpose: add model or outside-prose support only after the local deterministic transparency layer is complete.

Deliverables:

- model-disabled default mode,
- prompt/dotflow registry,
- model adapter interface,
- companion prose parser,
- schema validation and retry/reject behavior,
- model-swap and prompt-ablation evaluation.

Acceptance criteria:

- deterministic mode remains fully functional,
- model outputs are never final judgments,
- invalid model outputs are rejected, retried, or downgraded,
- output instability and graph-posture instability are measured separately.

## Evaluation Metrics

Primary demo metrics:

- redaction block/quarantine accuracy on synthetic test strings,
- residual PII/PHI violation count,
- structured intake validity rate,
- reviewer approval validation rate,
- future leakage failures,
- graph determinism,
- node-audit completeness,
- evidence-reference resolution rate,
- range/median completeness,
- ensemble contribution disposition completeness,
- disagreement traceability,
- receipt completeness,
- workbench completeness,
- app-flow completeness,
- selected-review-question propagation,
- node-audit checkpoint completion,
- reviewer adjustment and re-check traceability,
- clinician-summary completeness,
- deeper-dive artifact completeness,
- omission detection on fixtures,
- commission warning detection on fixtures,
- therapy-response integration on fixtures,
- next-best-information usefulness on fixtures,
- forbidden phrase violation count,
- review time per case during manual trials.

Do not report actual clinical harm prevention, outcome improvement, mortality reduction, complication reduction, length-of-stay reduction, or regulatory compliance. Report preventability opportunity as a proxy only.

## Prompt And Dotflow Strategy

Prompts and dotflows are versioned executable contracts, not authorities.

Each prompt or dotflow must define:

- `prompt_id`,
- `version`,
- `role_name` or `flow_type`,
- allowed input fields,
- forbidden input fields,
- required output schema,
- allowed node targets,
- forbidden output claims,
- model configuration if applicable,
- fixture coverage,
- expected failure cases,
- changelog.

Development order:

1. static fixtures,
2. prompt contract manifests,
3. schema validation,
4. deterministic graph tests,
5. optional model runner,
6. model-swap tests,
7. prompt-version regression tests.

## Constraints

- Keep the deterministic local path fully offline and reproducible.
- Prefer additive changes over broad rewrites.
- Do not weaken validation, schema checks, redaction gates, future-leakage checks, or provenance requirements to make tests pass.
- Do not add heavy dependencies without documenting why they are necessary.
- Do not make claims of clinical validation, clinical safety, production readiness, regulatory compliance, or real-world harm prevention.
- Separate implemented deterministic behavior from optional LLM, OpenEvidence, live evidence, prospective, or production behavior.
- Treat unknown provenance, unverified AI-derived facts, and unsupported prompt claims as weak or downgraded evidence.
- Keep source repositories outside `sentinel_codex_handoff/` read-only unless a later explicit task says otherwise.

## Iteration Policy

Before editing:

1. inspect relevant project source-of-truth docs,
2. inspect the current target folder,
3. identify the smallest phase-aligned change,
4. document assumptions in progress notes if the phase spans multiple turns.

Work in small batches:

1. write or update tests and fixtures first when behavior changes,
2. implement the smallest code path,
3. run nearest verification,
4. fix failures before expanding scope,
5. update docs after behavior is verified,
6. commit and push only scoped, verified changes when publishing is requested or clearly beneficial.

## Stop Conditions

Pause and summarize instead of continuing if:

- raw PHI, real patient data, credentials, proprietary benchmark data, or named institution data is required,
- clinical evidence interpretation, legal review, compliance review, IRB/QI approval, BAA status, or institutional approval is required before proceeding,
- a change would turn Sentinel into a disposition recommendation tool,
- a change would create patient-facing clinical advice,
- a change would bypass graph judgment and let prompts decide final posture,
- a required dependency needs network access or paid credentials for the deterministic path,
- the same verification failure persists after three distinct repair attempts,
- the next step requires a product decision not specified in this goal.

## Completion Rule

Mark a phase complete only when its proof items pass using actual command output or direct artifact inspection.

Mark the clinician-facing staged local demo complete only when the full demo proof items pass, local verification succeeds, the app demonstrates the A/B review-question path from input through summary and deeper dive, receipts and workbench artifacts are generated from both synthetic fixtures and at least one constructed text demo input, and the final status report clearly separates:

- implemented deterministic behavior,
- implemented local demo behavior,
- optional LLM/prompt behavior,
- deferred OpenEvidence/live evidence integration,
- deferred real clinical or prospective use,
- remaining safety, validation, and governance risks.
