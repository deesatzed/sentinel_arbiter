# GOAL.md

## Outcome

Build Sentinel as a local, synthetic-data governance workbench for replaying Emergency Department disposition decisions and evaluating whether the decision posture was warranted at the point of disposition, given only what was known then.

The first POC is intentionally narrow:

- focus on ED admission vs discharge or non-inpatient alternative decision points,
- evaluate warrant, uncertainty, omission risk, commission risk, therapy response, follow-up reliability, and preventability opportunity,
- produce committee-ready receipts,
- avoid making disposition orders or patient-specific medical recommendations.

Sentinel should remain a governance and review workbench, not a bedside alert system, clinical advice engine, diagnosis recommender, or autonomous ED disposition agent.

## Raw Idea

Use the existing Sentinel handoff package as the target build surface, adapt useful structure from `OE_dotflows.md` and `OE_dotflows2.md`, borrow local workbench and verification discipline from `finESS`, borrow fail-closed artifact/trace/receipt patterns from `clinclaw-firewall`, and construct the project in phases.

## Task Type

Safety/provenance-sensitive, multi-phase implementation program.

The first implementation pass must be discovery-first and scaffold-first. Do not implement real clinical recommendation logic before the data model, safety boundaries, provenance model, synthetic cases, validation harness, and receipt expectations are explicit and tested.

## Proof Of Done For Phase 0

Phase 0 is complete only when all of the following are true:

1. Inspect the target folder and source examples:
   - `sentinel_codex_handoff/README.md`
   - `sentinel_codex_handoff/docs/*.md`
   - `sentinel_codex_handoff/schemas/*.json`
   - `sentinel_codex_handoff/prompts/*.md`
   - `sentinel_codex_handoff/validation/*.md`
   - `../OE_dotflows.md`
   - `../OE_dotflows2.md`
   - selected reusable patterns from `../finESS`
   - selected reusable patterns from `../clinclaw-firewall`
2. Create or update a phase implementation plan that defines:
   - data model changes for ED disposition replay,
   - commission and omission evaluation nodes,
   - therapy-response and offered-therapy fields,
   - preventability-opportunity proxy metrics,
   - prompt/dotflow registry shape,
   - receipt requirements,
   - test strategy.
3. Confirm no named clinical site, employer, institution, real patient data, PHI, credentials, private keys, or proprietary data are added.
4. Run `git diff --check` from the nearest git repository if one exists, or document that `sentinel_codex_handoff` is not currently its own git repository.
5. Provide a final changed-file summary, verification summary, assumptions, and remaining risks.

## Full POC Proof Of Done

The ED disposition replay POC is complete only when all of the following are true:

1. A local project exists under `sentinel_codex_handoff` with installable dependencies and no required external services for the deterministic path.
2. Synthetic ED disposition replay cases exist and cover at least:
   - material missing input before disposition,
   - therapy offered with documented improvement,
   - therapy offered with nonresponse or unclear response,
   - therapy plausibly indicated but not considered,
   - discharge/home-plan feasibility problem,
   - admission or observation with limited added value,
   - AI-derived or weakly sourced fact driving the decision.
3. Each case has explicit timepoints:
   - `T0_triage`
   - `T1_initial_workup`
   - `T2_post_treatment_reassessment`
   - `T3_disposition_decision`
   - optional hidden `T4_follow_up_or_outcome`
4. Replay prevents hidden future facts from entering current-time evaluation.
5. Static role outputs and static EvidenceFlow outputs validate against schemas before any LLM-backed prompt mode is enabled.
6. Commission and omission lanes are represented as first-class node groups.
7. Therapy response is represented as a first-class node group.
8. The graph computes:
   - information sufficiency,
   - material gap strength,
   - harm clock,
   - information clock,
   - recoverability,
   - future correction opportunity,
   - decision weight,
   - AI-provenance risk,
   - commission risk,
   - omission risk,
   - therapy-response relevance,
   - next-best-information ranking,
   - preventability-opportunity score,
   - final posture.
9. Final posture is one of the Sentinel posture categories, not an admit/discharge recommendation.
10. Every run emits a reconstructable receipt containing:
    - input hashes,
    - timepoint id,
    - prompt/dotflow versions,
    - model versions if any,
    - evidence versions if any,
    - node values,
    - rejected or downgraded findings,
    - role disagreement map,
    - final posture,
    - decision weight,
    - preventability-opportunity explanation,
    - signature placeholder.
11. A human-readable Markdown or HTML receipt explains:
    - what was known,
    - what was missing,
    - what would have changed the discussion,
    - what admission might add,
    - what discharge or non-inpatient alternatives might add,
    - commission concerns,
    - omission concerns,
    - therapy-response concerns,
    - why the graph selected the posture.
12. Automated validation reports:
    - schema validity,
    - future leakage failures,
    - expected posture agreement,
    - omission detection,
    - commission warning detection,
    - therapy-response integration,
    - next-best-information usefulness,
    - receipt completeness,
    - forbidden phrase violations.
13. The project documents what is implemented, what is deferred, and what would be required before any real clinical, prospective, or production use.
14. Full local verification commands pass and `git diff --check` is clean.

## Scope

Allowed target folder:

- `sentinel_codex_handoff/`

Reference-only inputs unless explicitly copied into the target with provenance notes:

- `../OE_dotflows.md`
- `../OE_dotflows2.md`
- `../finESS/`
- `../clinclaw-firewall/`

Primary build artifacts to create or update in the target:

- `GOAL.md`
- `README.md`
- `docs/`
- `schemas/`
- `prompts/`
- `roadmaps/`
- `validation/`
- future project source files under the target folder only
- future synthetic fixtures under the target folder only
- future tests under the target folder only

Do not modify source repos `finESS` or `clinclaw-firewall` unless a later explicit goal says to do so.

## Safety / Provenance

- Use synthetic, deidentified-style, or public-style examples only.
- Do not add real patient data, PHI, credentials, private keys, proprietary benchmark data, or named clinical institutions.
- Do not create a tool that tells clinicians to admit, discharge, prescribe, diagnose, order, or clear a patient.
- Do not use phrases that imply a disposition recommendation, including:
  - safe to discharge
  - unsafe to discharge
  - should admit
  - should discharge
  - medically cleared
  - appropriate for discharge
  - inappropriate for discharge
  - recommended pathway
  - preferred pathway
- Keep the output framed as governance review, shared-decision support framing, warrant analysis, and committee-ready evidence.
- Do not invent outcome rates, length-of-stay estimates, complication rates, mortality rates, or clinical thresholds.
- If evidence is unavailable or not directly applicable, state that clearly.
- Separate implemented deterministic behavior from future LLM, OpenEvidence, live evidence, or prospective deployment behavior.
- Every LLM or dotflow output must be treated as structured input, not final judgment.
- The graph computes posture. Prompts do not decide final posture.
- Unknown provenance, unverified AI-derived facts, and unsupported prompt claims must not be treated as verified.
- Any useful but risky idea should be documented as deferred rather than partially implemented.

## Constraints

- Build the first milestone local, offline, deterministic, and reproducible.
- Start with static role outputs and static EvidenceFlow outputs before adding live LLM or OpenEvidence calls.
- Preserve the current Sentinel handoff thesis unless a documented decision changes it.
- Keep ED disposition replay as the first POC wedge. Broader Sentinel domains are deferred.
- Prefer additive changes over broad rewrites of existing planning docs.
- Do not add heavy dependencies without documenting why they are necessary.
- Do not weaken validation, schema checks, future-leakage checks, or provenance requirements to make tests pass.
- Do not make claims of clinical outcome improvement in the POC.
- Do not claim production readiness, clinical safety validation, regulatory compliance, or real-world harm prevention.

## Phase Plan

### Phase 0 - Scope Lock And Build Plan

Purpose: convert the broad Sentinel handoff into an ED disposition replay POC plan.

Deliverables:

- phase implementation plan,
- ED disposition data model delta,
- prompt/dotflow registry proposal,
- commission/omission node proposal,
- therapy-response node proposal,
- validation matrix,
- risk and non-scope notes.

Acceptance criteria:

- plan names every phase,
- all safety constraints are preserved,
- future expansion is documented but deferred,
- no real clinical logic is implemented beyond inert scaffold if needed.

### Phase 1 - Project Skeleton And Core Schemas

Purpose: create the local deterministic project substrate.

Deliverables:

- installable project skeleton,
- Pydantic or equivalent schema models,
- JSON schema export,
- fixture loader,
- validation utilities,
- no-secrets environment template.

Acceptance criteria:

- valid synthetic fixtures pass,
- invalid fixtures fail clearly,
- no named institution or PHI patterns are present.

### Phase 2 - ED Replay Cases And Future-Leakage Guard

Purpose: make point-in-time replay concrete.

Deliverables:

- synthetic ED cases with T0-T4 timepoints,
- current-time replay service,
- hidden-future-fact guard,
- expected output labels.

Acceptance criteria:

- T4 facts never enter T0-T3 analysis,
- each case has disposition-relevant uncertainty,
- each case includes outcome labels only for retrospective evaluation.

### Phase 3 - Information State, Therapy Response, Commission, And Omission Nodes

Purpose: represent the core ED disposition warrant problem.

Deliverables:

- information bucket classifier,
- therapy-response classifier,
- offered-therapy and not-considered-therapy representation,
- commission-risk nodes,
- omission-risk nodes,
- preventability-opportunity proxy calculation.

Acceptance criteria:

- material missing inputs are detected,
- low-value missing inputs are not escalated by default,
- therapy nonresponse or undocumented response changes node values,
- commission and omission concerns are visible separately.

### Phase 4 - Static EvidenceFlows And Role Outputs

Purpose: convert OE-style dotflows into versioned, schema-validated structured inputs.

Deliverables:

- dotflow or prompt manifest format,
- static role-assessment fixtures,
- static EvidenceFlow fixtures,
- schema validation,
- rejection rules for malformed, generic, future-leaking, or final-verdict outputs.

Acceptance criteria:

- static outputs run for every case,
- invalid outputs fail,
- role outputs map only to allowed nodes,
- no role agent emits final disposition recommendation language.

### Phase 5 - Node Normalizer And Prudence Graph

Purpose: compute Sentinel posture from typed nodes.

Deliverables:

- node normalizer,
- disagreement map,
- deterministic graph v0.1,
- final posture calculation,
- decision weight calculation,
- next-best-information ranking,
- sensitivity or node-inspection output.

Acceptance criteria:

- same node inputs yield same posture,
- unsupported findings cannot dominate final posture,
- posture changes can be traced to node changes,
- low decision weight suppresses unnecessary high-burden information gathering.

### Phase 6 - Receipts, Traceability, And Evaluation Harness

Purpose: make outputs auditable and measurable.

Deliverables:

- JSON receipt builder,
- Markdown or HTML receipt renderer,
- input hashing,
- version fields,
- signature placeholder,
- evaluation report generator,
- forbidden-phrase checker.

Acceptance criteria:

- every run emits valid receipt,
- receipt is reloadable,
- receipt completeness metrics pass,
- forbidden disposition language is caught,
- evaluation report is generated from synthetic cases.

### Phase 7 - Reviewer Workbench UI

Purpose: make the POC usable by a governance reviewer.

Deliverables:

- case library,
- timeline replay,
- information gap panel,
- therapy-response panel,
- commission/omission panel,
- provenance panel,
- two-clock panel,
- next-best-input panel,
- graph inspector,
- receipt viewer/export,
- evaluation dashboard.

Acceptance criteria:

- reviewer can inspect a case without reading raw JSON,
- UI displays posture without recommending admit or discharge,
- receipt export works,
- POC warnings are visible.

### Phase 8 - Optional LLM Prompt Mode And Model-Swap Evaluation

Purpose: add LLM-backed role/dotflow execution only after deterministic path works.

Deliverables:

- model-disabled default mode,
- prompt registry,
- model adapter interface,
- prompt version tracking,
- model version tracking,
- model-swap evaluation,
- prompt-ablation evaluation.

Acceptance criteria:

- deterministic static mode remains fully functional,
- LLM failures degrade gracefully,
- schema-invalid model outputs are rejected or retried,
- role-output instability and graph-posture instability are measured separately.

## Prompt And Dotflow Strategy

Treat prompts like versioned executable contracts.

Each prompt or dotflow should define:

- `prompt_id`
- `version`
- `role_name` or `flow_type`
- allowed input fields
- forbidden input fields
- required output schema
- allowed node targets
- forbidden output claims
- model configuration if applicable
- fixture coverage
- expected failure cases
- changelog

Development order:

1. static fixtures,
2. prompt contract manifests,
3. schema validation,
4. deterministic graph tests,
5. optional model runner,
6. model-swap tests,
7. prompt-version regression tests.

## Evaluation Metrics

Primary POC metrics:

- schema validity rate,
- future leakage failures,
- graph determinism,
- receipt completeness,
- node traceability,
- material gap recall,
- gap precision,
- low-value gap suppression,
- therapy-response integration accuracy,
- omission detection rate,
- commission warning detection rate,
- next-best-input actionability,
- forbidden phrase violation count,
- expert/reviewer posture agreement,
- review time per case.

Do not report actual clinical harm prevention. Report preventability opportunity as a proxy only.

## Iteration Policy

Before editing:

1. inspect relevant project source-of-truth docs,
2. inspect the current target folder,
3. identify the smallest phase-aligned change,
4. document assumptions in progress notes if the phase spans multiple turns.

Work in small batches:

1. write or update tests/fixtures first when behavior changes,
2. implement the smallest code path,
3. run nearest verification,
4. fix failures before expanding scope,
5. update docs only after behavior is verified.

If a phase reveals a better scope boundary, document the proposed change before implementing it.

## Stop Conditions

Pause and summarize instead of continuing if:

- real PHI, patient data, credentials, proprietary benchmark data, or named institution data is required,
- clinical evidence or legal/compliance interpretation is required before proceeding,
- a change would turn Sentinel into a disposition recommendation tool,
- a change would create patient-facing clinical advice,
- a change would bypass graph judgment and let prompts decide final posture,
- a required dependency needs network access or paid credentials for the deterministic path,
- the same verification failure persists after three distinct repair attempts,
- the next step requires a product decision not specified in this goal.

## Complete

Mark a phase complete only when its proof items pass using actual command output or direct artifact inspection.

Mark the full ED disposition replay POC complete only when the full POC proof items pass, local verification succeeds, receipts are generated from all synthetic cases, and the final report clearly separates:

- implemented deterministic behavior,
- optional LLM/prompt behavior,
- deferred OpenEvidence/live evidence integration,
- deferred real clinical deployment,
- remaining safety, validation, and governance risks.
