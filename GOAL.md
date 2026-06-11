# GOAL.md

## Outcome

Build Sentinel into a local, trustworthy governance workbench for replaying Emergency Department disposition decision points and reviewing whether the documented decision posture was warranted from the information available at that time.

The next milestone is no longer just a deterministic framework. It is a usable local demo where a reviewer can:

1. enter constructed, synthetic, or governance-approved deidentified clinical input,
2. run redaction and residual-risk checks before analysis,
3. convert the input into a reviewer-editable structured `DecisionEpisode`,
4. approve or revise the structured episode,
5. run deterministic Sentinel analysis,
6. inspect each dependent node, evidence item, range, median, uncertainty method, and ensemble contribution,
7. review generated JSON, Markdown, and workbench outputs,
8. understand exactly how the final Sentinel posture was produced.

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

The next milestone is the transparent local demo:

- constructed or approved deidentified input can be pasted or loaded,
- redaction happens before any intake or model-like analysis,
- residual PII/PHI risk blocks or quarantines input,
- intake extraction creates a structured draft rather than a final judgment,
- a reviewer can inspect and edit the structured case before analysis,
- every computed node exposes its dependencies and evidence,
- every node estimate includes value, range, median, distribution kind, confidence, method, and evidence references,
- static ensemble contributors produce bounded estimates and rationales,
- accepted, rejected, and downgraded findings are visible,
- graph posture is computed from typed nodes, not from prose or prompt authority,
- receipts and the workbench make the methodology transparent enough for skeptical review.

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

### 1. Input Stage

Purpose: accept constructed or approved deidentified input without letting risky text flow directly into analysis.

Requirements:

- provide a CLI path first,
- optionally provide a local app endpoint after the CLI path is tested,
- apply deterministic redaction before intake,
- emit a redaction report,
- block or quarantine residual PII/PHI patterns,
- hash the original local input without exposing it in generated review artifacts,
- preserve a redacted review copy.

### 2. Intake Stage

Purpose: convert redacted input into a structured draft case without inventing facts.

Requirements:

- create a draft `DecisionEpisode`,
- tag facts by timepoint,
- mark missing, unknown, inferred, weakly sourced, and reviewer-supplied fields,
- reject hidden future facts from current-time evaluation,
- require reviewer approval before graph execution,
- save the reviewer-approved structured episode as an artifact.

### 3. Node Audit Stage

Purpose: make every dependent node inspectable.

Requirements:

- define node dependencies explicitly,
- attach evidence references to node estimates,
- compute or assign value, range, median, distribution kind, confidence, and method,
- distinguish deterministic fixture-derived estimates from static role-derived or future LLM-derived estimates,
- record conflicts and sensitivity notes.

### 4. Ensemble Stage

Purpose: make role and EvidenceFlow influence transparent.

Requirements:

- static ensemble contributors must emit bounded proposed values and rationales,
- each contribution maps to allowed node IDs only,
- each contribution is accepted, rejected, or downgraded with a reason,
- graph posture must remain deterministic from normalized typed inputs,
- no role or prompt may decide the final posture.

### 5. Receipt Stage

Purpose: make the result reconstructable.

Requirements:

- emit JSON receipts,
- emit human-readable Markdown or HTML receipts,
- include input hashes, redaction report refs, timepoint ID, schema versions, prompt or dotflow versions, model versions if any, evidence versions if any, node audits, graph posture, decision weight, disagreement map, downgraded findings, rejected findings, and signature placeholder,
- include trace hashes for the run sequence,
- keep receipts free of raw PHI.

### 6. Workbench Stage

Purpose: make the demo usable without reading raw JSON.

Requirements:

- show redacted input and structured episode,
- show timeline replay,
- show node cards with evidence, range, median, distribution kind, confidence, and method,
- show ensemble contribution and disagreement,
- show graph posture and sensitivity notes,
- show generated receipts,
- show validation status and warnings,
- keep visible POC and non-clinical-use warnings.

### 7. Optional Companion Prose Stage

Purpose: allow future OpenEvidence-like or LLM prose to become structured evidence input without handing it authority.

Requirements:

- parse companion prose conservatively,
- treat parsed prose as evidence input only,
- flag unsafe or action-like imperative language,
- require schema validation,
- downgrade unsupported claims,
- keep deterministic mode fully functional without this stage.

## Full Demo Proof Of Done

The transparent local demo is complete only when all of the following are true:

1. A user can run a local CLI command with constructed text input and receive a redaction report plus draft structured episode.
2. Residual PII/PHI risk is detected and blocks or quarantines unsafe input.
3. A reviewer-approved structured episode can be saved and used for deterministic analysis.
4. Synthetic and constructed demo inputs validate against schemas.
5. Hidden future facts cannot enter current-time node computation.
6. Every graph node has a `NodeAudit` or equivalent schema-backed audit object.
7. Every node audit has dependencies, evidence refs, value, range, median, distribution kind, confidence, method, and sensitivity note.
8. Every ensemble contribution is accepted, rejected, or downgraded with a reason.
9. The graph computes final Sentinel posture from normalized typed node values.
10. Final posture remains one of the Sentinel posture categories, not a disposition recommendation.
11. JSON receipts include redaction, intake, node audit, ensemble, trace, graph, and signature-placeholder fields.
12. Human-readable receipts explain what was known, what was missing, what would have changed the discussion, what facility-based monitoring or treatment might add, what non-inpatient alternatives might add, commission concerns, omission concerns, therapy-response concerns, and why the graph selected the posture.
13. The workbench renders the redacted input, structured episode, node methodology, distributions, range, median, ensemble disagreement, graph posture, receipts, and validation status.
14. Automated validation reports cover schema validity, future leakage, redaction gating, expected posture agreement on fixtures, omission detection, commission warning detection, therapy-response integration, next-best-information usefulness, node-audit completeness, receipt completeness, workbench completeness, and forbidden phrase violations.
15. The project documents what is implemented, what is deferred, and what would be required before any real clinical, prospective, production, or live-evidence use.
16. Full local verification commands pass and `git diff --check` is clean.

## Phase Plan

### Phase A - Goal And Roadmap Refresh

Purpose: align the project source of truth with the new transparent-demo milestone.

Deliverables:

- refreshed `GOAL.md`,
- updated progress notes,
- optional roadmap issue/task breakdown,
- documented reuse strategy for EMEX and AdmSVE.

Acceptance criteria:

- goal explicitly covers constructed/deidentified input, redaction, intake, node audit, ensemble transparency, workbench, receipts, and safety boundaries,
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

Purpose: provide the first app-like demo surface after the CLI and artifact workflow are safe.

Deliverables:

- local FastAPI or equivalent app,
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

### Phase H - Optional Companion Prose Or LLM Mode

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

Mark the transparent local demo complete only when the full demo proof items pass, local verification succeeds, receipts and workbench artifacts are generated from both synthetic fixtures and at least one constructed text demo input, and the final status report clearly separates:

- implemented deterministic behavior,
- implemented local demo behavior,
- optional LLM/prompt behavior,
- deferred OpenEvidence/live evidence integration,
- deferred real clinical or prospective use,
- remaining safety, validation, and governance risks.
