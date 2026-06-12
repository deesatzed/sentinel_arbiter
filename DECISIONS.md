# DECISIONS.md

## Decision 2026-06-11-01 - Preserve Sentinel As Governance Workbench

Sentinel's first POC remains a governance and review workbench for ED disposition replay. It does not make admission, discharge, diagnosis, prescribing, ordering, clearance, or patient-facing treatment recommendations.

Reason: This preserves the safety boundary in `GOAL.md` and keeps the POC aligned with committee-ready warrant review rather than bedside decision automation.

## Decision 2026-06-11-02 - Use Additive ED-Specific Scope Lock

The existing broad Sentinel docs remain in place. The ED disposition replay delta is added in `roadmaps/04_phase_0_ed_disposition_implementation_plan.md` instead of rewriting the whole handoff.

Reason: The current package contains useful architecture, prompt, schema, and validation planning, but it is broader than the new ED disposition wedge. An additive Phase 0 plan reduces drift without destroying useful context.

## Decision 2026-06-11-03 - Static Deterministic Path Before LLM Mode

Phase 1 through Phase 6 must support static fixtures and deterministic validation before optional LLM prompt mode is enabled.

Reason: The goal requires schema validation, future-leakage prevention, receipt completeness, and graph judgment before live prompt execution or model-swap experiments.

## Decision 2026-06-11-04 - Commission, Omission, And Therapy Response Are First-Class

Commission concerns, omission concerns, and therapy-response concerns must be represented as distinct node groups and receipt sections.

Reason: The ED disposition replay POC explicitly evaluates omission risk, commission risk, therapy response, and preventability opportunity. Collapsing these into a single uncertainty score would weaken the method.

## Decision 2026-06-11-05 - Use Pydantic 2 For Phase 1 Models

Phase 1 uses a minimal Python package with Pydantic 2 models, pytest tests, static JSON fixtures, and local module commands for schema export and validation.

Reason: Pydantic is already available locally, exports JSON Schema cleanly, and keeps the deterministic path offline without adding a heavier framework before the graph and receipt methodology are proven.

## Decision 2026-06-11-06 - Make Synthetic Case Coverage Machine-Checkable

Each ED fixture declares `covered_case_patterns` in expected-output metadata, and the case-library validator checks that all seven GOAL.md patterns are covered.

Reason: Machine-checkable coverage prevents the POC from relying on filename or prose interpretation and makes it harder to accidentally lose a required synthetic scenario during later edits.

## Decision 2026-06-11-07 - Keep Phase 3 Graph Deterministic And Fixture-Field-Based

The first graph computes bounded node values from structured synthetic fixture fields, not from prompt prose, hidden outcome labels, or clinical evidence assumptions.

Reason: This satisfies the local deterministic path and lets tests arbitrate lane behavior before adding role outputs, EvidenceFlows, receipts, or optional LLM mode.

## Decision 2026-06-11-08 - Use Static Templates Before Per-Case Prompt Runs

Phase 4 validates static role-output and EvidenceFlow templates that expand over every synthetic case before any LLM-backed role execution exists.

Reason: This proves schema, node-target, forbidden-language, and current-time constraints without paying the duplication cost of hand-writing every per-role/per-case output before receipt rendering and role-disagreement handling exist.

## Decision 2026-06-11-09 - Emit Unsigned Deterministic POC Receipts First

Phase 6 receipts are reconstructable JSON plus Markdown review artifacts with `UNSIGNED_DETERMINISTIC_POC` placeholders, not cryptographic production signatures.

Reason: The POC needs auditable receipts before UI and optional LLM mode, but production signing, key management, and deployment controls are intentionally out of scope for the deterministic local milestone.

## Decision 2026-06-11-10 - Generate A Static Offline Reviewer Workbench First

Phase 7 uses a generated `data/workbench/index.html` file rather than a live web server or frontend framework.

Reason: The deterministic POC needs a reviewer-inspectable surface with no external services. A static artifact can expose the case library, replay panels, graph nodes, evaluation dashboard, and receipt export links while preserving the local/offline safety boundary.

## Decision 2026-06-11-11 - Keep Pre-Real-Use Boundaries In A Checked Status Document

The implemented/deferred boundary and requirements before real clinical, prospective, or production use are recorded in `docs/18_deterministic_poc_status.md` and checked by tests.

Reason: `GOAL.md` requires the project to document what is implemented, what is deferred, and what would be required before any real clinical, prospective, or production use. Treating this as a tested artifact prevents the safety boundary from drifting into informal progress notes.

## Decision 2026-06-11-12 - Initialize A Local Repository Baseline

`sentinel_codex_handoff` is now its own local git repository with no remote configured.

Reason: Full POC proof of done requires `git diff --check` to be clean. The target folder was previously outside any git repository, so a local baseline repository was needed to make that verification command meaningful inside the allowed target folder.

## Decision 2026-06-11-13 - Publish To Sentinel Arbiter GitHub Repository

The local repository uses `https://github.com/deesatzed/sentinel_arbiter.git` as `origin` and `main` as the primary branch.

Reason: The user requested this project be committed and pushed to that GitHub repository. Publishing notes are recorded in `docs/19_repository_publishing.md`.

## Decision 2026-06-11-14 - Promote The Next Milestone To A Transparent Local Demo

| ID | Date | Category | Decision | Rationale | Alternatives Considered | Status |
|---|---|---|---|---|---|---|
| 2026-06-11-14 | 2026-06-11 | Scope | Treat the completed deterministic POC as the baseline and promote the next milestone to a transparent local demo with constructed or approved deidentified input, redaction-before-intake, reviewer-approved structured episodes, node-audit methodology, ensemble transparency, upgraded receipts, and a reviewer-facing workbench or local app surface. | The user clarified that trust requires more than final posture output. Sentinel must expose chosen dependent nodes, evidence for each node, probability or score distributions, range, median, method, ensemble contribution, disagreements, accepted/rejected/downgraded findings, and sensitivity of the final posture. | Keeping the deterministic POC as the end goal was rejected because it is not yet a real input-to-review demo. Jumping directly to a FastAPI app was rejected because a live app without a tested artifact path would increase safety risk. Copying AdmSVE or EMEX wholesale was rejected because those repos solve adjacent workflows rather than Sentinel's native trust layer. | Accepted |

## Decision 2026-06-11-15 - Gate Constructed Input With Reviewer Approval Artifacts

| ID | Date | Category | Decision | Rationale | Alternatives Considered | Status |
|---|---|---|---|---|---|---|
| 2026-06-11-15 | 2026-06-11 | Workflow | Prepared constructed input must be promoted through `approved_episode.json`, `approval_manifest.json`, and `approval_trace.json` before later analysis code treats it as analysis-ready. Direct draft JSON loading through the approved-input path is rejected. | `GOAL.md` requires reviewer approval before graph execution and trace events for draft, edit, and approval. A sidecar manifest plus hash-chained trace makes the approval boundary testable without introducing a live app before the artifact path is safe. | Treating `draft_episode.json` as analysis-ready was rejected because it collapses reviewer approval into intake. Embedding approval fields directly in `DecisionEpisode` was deferred because the current ED schema is already used by synthetic fixtures and approval is workflow provenance rather than clinical episode content. | Accepted |

## Decision 2026-06-11-16 - Add Deterministic Node Audit Bundle Before Receipt/UI Upgrade

| ID | Date | Category | Decision | Rationale | Alternatives Considered | Status |
|---|---|---|---|---|---|---|
| 2026-06-11-16 | 2026-06-11 | Data Model | Add a schema-backed `NodeAuditBundle` that emits `NodeDefinition`, `NodeEvidence`, `NodeEstimate`, `EnsembleContribution`, and `NodeAudit` records for every current graph metric before integrating the methodology into receipts and the workbench. | `GOAL.md` requires dependent nodes, evidence, provenance, ranges, medians, methods, confidence, ensemble contribution shape, and sensitivity notes. A deterministic bundle lets tests prove methodology completeness before changing receipt and UI rendering. | Adding methodology text directly to receipts was deferred because it would not create a reusable schema layer. Waiting until the local app was rejected because trust artifacts need to exist before app presentation. | Accepted |

## Decision 2026-06-11-17 - Normalize Static Role And EvidenceFlow Inputs Into Bounded Contributions

| ID | Date | Category | Decision | Rationale | Alternatives Considered | Status |
|---|---|---|---|---|---|---|
| 2026-06-11-17 | 2026-06-11 | Data Model | Static role and EvidenceFlow inputs are normalized into bounded `EnsembleContribution` records only when they target deterministic graph nodes; unsupported static node targets are rejected with reasons and tracked separately. | `GOAL.md` requires ensemble contribution and disagreement to be transparent without letting prompts or prose decide final posture. Bounded contributions make role influence inspectable while preserving graph authority. | Passing static role outputs directly into graph scoring was rejected because it would blur prompt authority and deterministic graph authority. Dropping unsupported role targets silently was rejected because it would hide why static inputs did not affect graph nodes. | Accepted |

## Decision 2026-06-11-18 - Embed Methodology In Receipts And Workbench

| ID | Date | Category | Decision | Rationale | Alternatives Considered | Status |
|---|---|---|---|---|---|---|
| 2026-06-11-18 | 2026-06-11 | Artifact Surface | JSON receipts, Markdown receipts, and the static workbench render node-audit methodology and ensemble contribution details directly, including dependent inputs, evidence refs, ranges, medians, distributions, methods, sensitivity notes, accepted/downgraded contributions, and rejected ensemble inputs. | The trust layer cannot live only in code or validation reports. Reviewers need the method visible in the same artifacts they inspect when reviewing a run. | Linking only to `validation/reports/latest.json` was rejected because it would make receipt review incomplete. Rendering only aggregate graph values was rejected because it hides how each dependent node was produced. Waiting for a local app was rejected because artifact transparency should exist before app presentation. | Accepted |

## Decision 2026-06-11-19 - Use Stdlib Local Demo Before Heavier Web Stack

| ID | Date | Category | Decision | Rationale | Alternatives Considered | Status |
|---|---|---|---|---|---|---|
| 2026-06-11-19 | 2026-06-11 | Local Demo | Phase G uses a Python stdlib HTTP app for paste, redaction, editable structured episode review, approval, deterministic analysis, and output review before adopting FastAPI or a fuller frontend. | `GOAL.md` allows FastAPI or equivalent after the CLI path is tested. A stdlib server proves the app workflow without adding dependency, authentication, deployment, or frontend complexity before the safety gates and artifact workflow are stable. | Jumping directly to FastAPI was deferred because the current need is local demo proof rather than production web architecture. Keeping only CLI was rejected because the milestone asks for app-like input and review. Writing raw pasted input to repo artifacts was rejected; the app uses in-memory preparation and persists redacted/structured artifacts plus hashes. | Accepted |

## Decision 2026-06-11-20 - Reset Next Milestone To Clinician-Facing Staged UX

| ID | Date | Category | Decision | Rationale | Alternatives Considered | Status |
|---|---|---|---|---|---|---|
| 2026-06-11-20 | 2026-06-11 | UX Scope | Treat the existing deterministic local app as the substrate and make the next milestone a staged clinician-facing UX with A/B review-question selection, paste/upload, `Pre-process`, Node Audit Methodology review, `OK`/`Adjust`/`Re-check selected nodes`, Ensemble Contributions, `Process`, a concise clinician-readable governance summary, and a `Deeper Dive` audit view. | The current output is technically transparent but not yet meaningful enough for a clinician reviewer on first read. Trust requires a summary-first workflow plus method visibility before and after processing, not a raw JSON or receipt-first experience. | Keeping the existing local app unchanged was rejected because it does not match the requested reviewer journey. Jumping to optional LLM mode was rejected because the deterministic trust checkpoints and summary UX need to be proven first. Hiding methodology behind the final result was rejected because the reviewer must see and approve or re-check the node audit before processing. | Accepted |

## Decision 2026-06-11-21 - Make Final Verification A Durable Report

| ID | Date | Category | Decision | Rationale | Alternatives Considered | Status |
|---|---|---|---|---|---|---|
| 2026-06-11-21 | 2026-06-11 | Verification | Close the final GOAL.md proof item through a checked `validation/reports/final_verification.json` report generated by `sentinel_workbench.final_verification`, and require the goal audit to read that report before item 25 can pass. | The previous goal audit intentionally left item 25 pending because live command output was not durable. A structured final-verification report preserves the actual command exits for tests, schema checks, validation regeneration, and `git diff --check` without relying on a chat-only completion claim. | Leaving item 25 as manual live proof was rejected because the checked audit could never reach `all_pass=true`. Marking item 25 pass directly in the Markdown was rejected because it would not be machine-checkable. Embedding raw command logs in prose was rejected because the JSON report is easier to test and regenerate. | Accepted |

## Decision 2026-06-12-01 - Supersede The 25-Item Audit With A Remediation Audit

| ID | Date | Category | Decision | Rationale | Alternatives Considered | Status |
|---|---|---|---|---|---|---|
| 2026-06-12-01 | 2026-06-12 | Verification | Treat the previous 25-item clinician-facing staged-demo audit as completed historical evidence and replace the active `GOAL.md` audit with a ten-item completeness-scan remediation audit. | The active `GOAL.md` now targets stale documentation, final-verification hardening, rendered UX proof, OpenRouter wording, and progress-log clarity. Reusing the old 25-item audit would make the current goal appear complete without proving the new remediation work. | Keeping the 25-item audit as the active audit was rejected because it proves the prior milestone, not the current goal. Adding only prose notes was rejected because the project already relies on machine-readable validation reports. | Accepted |

## Decision 2026-06-12-02 - Use Deterministic Rendered-HTML UX Verification

| ID | Date | Category | Decision | Rationale | Alternatives Considered | Status |
|---|---|---|---|---|---|---|
| 2026-06-12-02 | 2026-06-12 | UX Verification | Add `sentinel_workbench.ux_verification` to exercise the local stdlib app through HTTP and generate JSON/Markdown rendered-HTML evidence for landing, pre-process, node audit, ensemble, result summary, deeper-dive links, validation status, trace hashes, and layout guards. | The completeness scan found HTTP/HTML test coverage but no durable rendered UX artifact. A deterministic stdlib verifier avoids adding a browser dependency while proving the required surfaces render from the actual local app routes. | Adding Playwright was deferred because the current repo has no browser dependency and the goal allows an equivalent rendered-UX artifact. Manual screenshots alone were rejected because they are harder to reproduce and validate in final verification. | Accepted |
