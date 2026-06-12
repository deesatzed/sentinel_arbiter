# GOAL.md

## OUTCOME

Build the next Sentinel milestone: a clinician-optimized local review demo that turns the current functional deterministic POC into a usable reviewer console.

The finished milestone must let a reviewer open the local app, choose one of the two governance questions, paste or upload constructed/deidentified-style clinical text, pre-process it, review and approve or challenge the node-audit methodology, inspect ensemble contributions, run deterministic Sentinel processing, and review a concise clinician-readable result with an optional deeper-dive methodology/audit view.

The app must remain a local deterministic governance-review POC. It must not become a clinical decision system, production deployment, PHI-ready system, or LLM-authoritative workflow.

Goal shape: `clinician_review_console_v1`.

## CURRENT BASELINE

The previous milestones are complete and may be treated as the implementation baseline:

- deterministic synthetic case library,
- constructed/deidentified-style intake,
- redaction and residual-risk gating,
- reviewer approval artifacts,
- deterministic graph and posture computation,
- node audit bundle with dependencies, evidence, ranges, medians, distributions, confidence, methods, and sensitivity notes,
- ensemble contribution normalization,
- JSON and Markdown receipts,
- static offline workbench,
- stdlib local demo app,
- OpenRouter comparison harness outside app authority,
- final verification report and remediation audit.

Known current limitation: the local app is functionally staged but not yet optimized for repeated actual clinician-review use. The next build should make the UX summary-first, plain-English, inspectable, and efficient without weakening evidence transparency.

## PROOF OF DONE

This goal is complete only when all of the following are true and verified from the current worktree.

1. The local app presents a first-screen landing workflow with:
   - clear explanations of the two review choices:
     - `Disposition Information Sufficiency`: "Is there enough information to make a disposition decision?"
     - `AI Response Use Sufficiency`: "Is there enough information to use this AI-generated response?"
   - sample-case selection for at least the constructed demo case and the seven synthetic fixtures,
   - paste input and local text-file upload,
   - visible local/demo/non-patient-care boundary.

2. The pre-process step produces a reviewer-friendly intake review with:
   - redaction/residual-risk status,
   - structured episode fields displayed in editable clinical sections rather than only raw JSON,
   - raw JSON available only as an advanced/deeper edit fallback,
   - clear indication of what was inferred from text versus directly present,
   - no raw unredacted input copied into committed or generated review artifacts.

3. The Node Audit Methodology screen is redesigned as a methodology explorer, not only a dense table. For every required graph node it must show:
   - plain-English node meaning,
   - dependent inputs,
   - evidence used,
   - missing or weak evidence,
   - value, range, median, distribution, confidence, and method,
   - sensitivity note,
   - reviewer action controls.

4. The node-audit controls are functional and traceable:
   - `OK`,
   - `Adjust`,
   - `Re-check Selected Nodes`,
   - selected-node controls use checkboxes or equivalent node-level controls,
   - methodology-changing actions require confirmation,
   - all actions are saved in `node_audit_review_manifest.json` or a tested successor artifact,
   - the deterministic graph remains the source of final posture authority.

5. The Ensemble Contributions view is redesigned for reviewer use:
   - group contributions by node,
   - expose contributor role, proposed value/range, disposition, and reason,
   - distinguish accepted, downgraded, and rejected inputs,
   - summarize disagreements and unsupported targets in plain English.

6. The result screen is summary-first and clinically readable:
   - first visible result section is a clinician-facing governance summary,
   - summary is no more than two short paragraphs,
   - summary explains what the result means and why without requiring raw node IDs,
   - summary names the main missing/weak information, the strongest driver, and the most useful next review input,
   - summary preserves the boundary that this is governance review support, not clinical action advice,
   - raw scores remain available in deeper dive but are not the primary explanation.

7. A `Deeper Dive` view exists and is easy to navigate. It must include, at minimum:
   - Methodology,
   - Node Evidence,
   - Ensemble Contributions,
   - Receipt JSON/Markdown links,
   - Trace Hashes,
   - Validation Status,
   - Optional Model Comparison.

8. OpenRouter support is integrated only as a comparison panel:
   - reads local `.env` model settings without printing secrets,
   - can run the existing challenging constructed example when credentials are present,
   - gracefully skips with a clear local message when credentials are absent,
   - clearly labels model output as comparison-only,
   - never lets model output set graph values or final posture,
   - saves raw model responses only under gitignored artifacts.

9. Add or update a durable release/readiness artifact, preferably `RELEASE_CHECKLIST.md`, with:
   - release scope,
   - Go / Conditional Go / No-Go decision for local demo use,
   - build, tests, lint/typecheck, security, privacy, env vars, docs, error handling, logging, rollback,
   - known blockers,
   - accepted risks,
   - required fixes before any real clinical/prospective/production use.

10. Add or update documentation so a new user can run the demo without prior chat context:
    - local setup,
    - how to start the app,
    - how to use sample cases,
    - how to paste/upload constructed input,
    - how to interpret the summary,
    - how to open deeper dive,
    - how optional OpenRouter comparison works,
    - what is intentionally not claimed.

11. Add verification coverage for the optimized UX:
    - HTTP/app tests for the full happy path,
    - tests for redaction/residual-risk handling,
    - tests for structured editable episode sections,
    - tests for node-level action tracing,
    - tests for summary-first result content,
    - tests for deeper-dive navigation,
    - tests for OpenRouter comparison skip mode and no-secret output,
    - tests that forbidden clinical recommendation phrases are not introduced.

12. Produce a current rendered-UX verification artifact:
    - use Browser/Playwright screenshots if available,
    - otherwise use the existing deterministic rendered-HTML verifier and document why browser screenshots were unavailable,
    - verify desktop and narrow/mobile-width layout,
    - verify text does not visibly overlap,
    - verify first screen, pre-process, methodology explorer, ensemble view, result summary, deeper dive, and optional comparison panel.

13. Run and confirm all required commands exit 0:

```bash
python3 -m pytest -q
PYTHONPATH=src python3 -m sentinel_workbench.validate data/cases
PYTHONPATH=src python3 -m sentinel_workbench.static_inputs --static-inputs data/static_inputs/static_inputs.json --case-dir data/cases
PYTHONPATH=src python3 -m sentinel_workbench.evaluate --case-dir data/cases --out validation/reports/latest.json --receipt-dir data/receipts
PYTHONPATH=src python3 -m sentinel_workbench.ux_verification
PYTHONPATH=src python3 -m sentinel_workbench.final_verification
PYTHONPATH=src python3 -m sentinel_workbench.goal_audit --out-json validation/reports/goal_completion_audit.json --out-markdown docs/21_goal_completion_audit.md
python3 -m pip install -e . --dry-run --no-deps
git diff --check
```

14. Inspect and confirm:

```bash
git status --short --branch
rg -n "not for patient care|governance review support|not a clinical action recommendation|not production" README.md docs src tests data/prepared_inputs data/receipts
rg -n "safe for discharge|medical clearance|cleared for discharge|should prescribe|start medication|place an order" src data/prepared_inputs data/receipts README.md docs --glob '!src/sentinel_workbench/safety.py' --glob '!src/sentinel_workbench/goal_audit.py'
rg -n "sk-or-[A-Za-z0-9_-]{8,}|raw model response" . --glob '!artifacts/**' --glob '!.env' --glob '!tests/**' --glob '!GOAL.md' --glob '!README.md' --glob '!docs/**'
```

The first grep must show safety boundaries in user-visible documentation/artifacts. The second grep must return no unsafe clinical-action recommendations outside explicit safety-rule definitions. The third grep must return no committed OpenRouter-looking secrets or raw model response content outside ignored artifacts and tests that intentionally use fake fixtures.

## SCOPE

Modify only files needed to deliver the local clinician-review demo milestone.

Expected implementation areas:

- `src/sentinel_workbench/local_app.py`
- `src/sentinel_workbench/receipts.py`
- `src/sentinel_workbench/workbench.py`
- `src/sentinel_workbench/ux_verification.py`
- `src/sentinel_workbench/openrouter_compare.py` only for comparison-panel integration or safe skip behavior
- tests under `tests/`
- `README.md`
- `docs/18_deterministic_poc_status.md`
- `docs/21_goal_completion_audit.md`
- `docs/22_local_app_ux_verification.md` or successor UX proof artifact
- `DECISIONS.md`
- `PROGRESS.md`
- `RELEASE_CHECKLIST.md`
- validation reports regenerated by documented commands
- generated local demo artifacts under existing safe generated-artifact paths

Read/reference:

- `GOAL.md`
- `DECISIONS.md`
- `PROGRESS.md`
- `README.md`
- `docs/18_deterministic_poc_status.md`
- `docs/22_local_app_ux_verification.md`
- `tests/test_phase_g_local_demo_app.py`
- `tests/test_goal_completion_audit.py`
- `tests/test_openrouter_compare.py`
- `validation/reports/final_verification.json`
- `validation/reports/latest.json`
- `data/static_inputs/static_inputs.json`
- `data/cases/*.json`
- `data/constructed_inputs/constructed_demo_case.txt`

Do not modify:

- `.env`
- raw PHI or real clinical data
- ignored OpenRouter raw response artifacts except by running local comparison into gitignored `artifacts/`
- unrelated generated caches such as `__pycache__`, `.DS_Store`, `.pytest_cache`, or virtualenv files
- sibling repositories unless a separate goal explicitly authorizes cross-repo work

## SAFETY / PROVENANCE

- Sentinel remains a local deterministic governance-review POC using synthetic or constructed/deidentified-style inputs.
- Do not add direct clinical recommendations, diagnosis logic, prescribing logic, ordering logic, clearance language, admission/discharge instructions, or patient-specific medical advice.
- Do not claim production readiness, PHI readiness, clinical safety validation, regulatory compliance, clinical outcome benefit, or real-world harm prevention.
- Do not weaken future-leakage prevention, redaction/residual-risk gates, reviewer approval gates, forbidden-phrase scanning, receipt traceability, node-audit evidence, ensemble transparency, or graph-authority boundaries.
- OpenRouter and any other model output must remain comparison-only unless a later goal explicitly designs and validates model authority.
- Preserve a clear difference between:
  - deterministic graph authority,
  - static role/EvidenceFlow contributions,
  - reviewer actions,
  - optional model comparison.
- If a useful idea would require real PHI handling, real clinical workflow integration, production auth, external evidence retrieval, prospective validation, or regulatory analysis, document it as deferred instead of partially implementing it.

## CONSTRAINTS

- Prefer improving the existing stdlib local app unless a lightweight dependency is clearly necessary and justified in `DECISIONS.md`.
- Do not introduce a full frontend framework unless the current UX requirements cannot be met cleanly with the existing app surface.
- Keep visual design utilitarian, dense, and clinician-review oriented.
- Do not use decorative hero/marketing UI.
- Use stable responsive layout constraints so tables, labels, buttons, and summaries do not overlap on narrow or desktop screens.
- Do not put important methodology only in raw JSON.
- Preserve existing public CLI names unless a rename is required for safety and is documented.
- Preserve existing schema semantics and receipt provenance unless a test-backed update is required.
- Do not remove or weaken tests to make the goal pass.
- Keep secrets and raw model responses out of committed files.
- Keep generated reports aligned with actual command output when regenerated.

## ITERATION

1. Start by confirming `git status --short --branch` and reading the source-of-truth files listed in `AGENTS.md`.
2. Work in small batches:
   - UX information architecture and documented decision,
   - clinician-first summary rewrite,
   - structured editable intake review,
   - methodology explorer,
   - ensemble contribution redesign,
   - functional node-level action controls,
   - deeper-dive navigation,
   - optional OpenRouter comparison panel and skip state,
   - rendered UX verification,
   - release/readiness documentation and final audit.
3. Before substantial UI edits, sketch the intended screen flow in `PROGRESS.md` or a short docs/plans artifact.
4. After each batch, run the nearest relevant tests.
5. If browser verification is available, use it before final completion; otherwise document the fallback and strengthen deterministic rendered-HTML checks.
6. Record meaningful architecture, safety, dependency, or UX decisions in `DECISIONS.md`.
7. Keep `PROGRESS.md` current with completed batches, command results, and remaining risks.
8. Before completion, rerun the full proof command set and inspect the grep checks.

## STOP

Pause and report current evidence if:

- a change would require real PHI, credentials beyond local OpenRouter comparison, production deployment, or external clinical systems,
- a UX decision would materially change the product boundary from governance review support to clinical decision support,
- browser verification or local app rendering fails after one fallback attempt and deterministic HTML verification cannot cover the gap,
- OpenRouter integration would require exposing secrets, committing raw model responses, or treating model output as graph authority,
- the same verification failure persists after three distinct repair attempts,
- a new dependency or frontend framework appears necessary but would materially broaden scope,
- requested behavior conflicts with the safety/provenance constraints above.

## COMPLETE

Mark this goal complete only when every `PROOF OF DONE` item is satisfied by current command output or inspected artifacts.

Completion must include a final summary with:

- changed files,
- UX surfaces implemented,
- verification commands and results,
- safety/provenance boundaries preserved,
- intentionally deferred items,
- current git status,
- any untracked local files and why they were not touched.
