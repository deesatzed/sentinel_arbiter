# GOAL.md

## OUTCOME

Fix the browser-discovered local app UX failures so the Sentinel clinician-review console passes the full Chrome DevTools workflow suite at **23/23** and remains a local deterministic governance-review POC.

The prior `clinician_review_console_v1` milestone is the implementation baseline. This goal is a focused remediation pass for the live-browser test run that passed 17 of 23 checks and exposed two real user-facing issues:

1. selecting a sample case can be ignored when the default textarea content is still present, so the app records `input_mode=pasted_text` instead of `sample_case`;
2. result pages display Receipt JSON and Receipt Markdown links, but those links return `404` in the live local app.

Goal shape: `browser_ux_remediation_v1`.

## CURRENT BASELINE

Verified baseline from the current repo and browser run:

- local app starts on `http://127.0.0.1:8770`;
- Chrome DevTools can drive the app through `http://127.0.0.1:9223`;
- landing, paste input, file upload, redaction/intake review, structured clinical sections, Methodology Explorer, grouped Ensemble Contributions, OK processing, blocked unconfirmed adjustment, confirmed adjustment, confirmed re-check, result summary, Deeper Dive anchors, OpenRouter skip panel, residual-risk quarantine, and desktop/mobile no-horizontal-overflow checks passed;
- confirmed re-check writes `node_audit_review_manifest.json` with selected nodes, re-check results, and `graph_authority_preserved=true`;
- confirmed upload writes `run_manifest.json` with `input_mode=uploaded_file` and the uploaded filename;
- focused sample-selector check proved that clearing the textarea lets the selected sample run as `sample_case`, but the normal reviewer path of selecting a sample and clicking `Pre-process` processes the default textarea instead;
- receipt artifact links are present in the result HTML, but browser fetches return `404` because the stdlib local server does not serve those generated artifact paths.

Browser evidence artifacts from the discovery run:

- `/tmp/sentinel_full_ux_browser_report_1781272352874.json`
- `/tmp/sentinel_sample_selector_focus_sample_focus_1781272436443.json`

These `/tmp` artifacts are evidence for this goal's starting point, not committed project artifacts.

## PROOF OF DONE

This goal is complete only when all items below are true and verified from the current worktree.

1. The full browser workflow suite passes **23/23** against the live local app.
   - Re-run a Chrome DevTools browser automation script covering the same feature surface as the failed run.
   - Save a fresh JSON report under a durable project path such as `validation/reports/browser_ux_verification.json`.
   - The report must include `overallPass: true`, `passCount: 23`, `failCount: 0`, and screenshots or screenshot paths for desktop/mobile landing, preprocess, result, and failure-prone flows.

2. Sample-case selection works in the normal reviewer path.
   - Selecting any synthetic sample case and clicking `Pre-process` without manually clearing the default textarea must process that selected sample.
   - The resulting `run_manifest.json` must record:
     - `input_mode: "sample_case"`;
     - the selected `sample_case`;
     - the selected review question.
   - The pre-process page must visibly reflect the selected sample content or title, not the default constructed demo text.
   - Paste input must still work when the reviewer intentionally chooses/pastes custom text.
   - File upload must still work and record `input_mode: "uploaded_file"`.

3. The landing input UX makes input precedence unambiguous.
   - The reviewer must be able to tell whether the app will use the selected sample, pasted text, or uploaded file.
   - If the fix uses JavaScript to load sample text into the textarea, it must degrade safely when JavaScript is unavailable.
   - If the fix uses explicit input-mode controls, the default mode must be obvious and tests must prove each mode.
   - The app must not silently prefer stale default pasted text over an explicitly selected sample.

4. Receipt artifact links work in the live browser.
   - Result-page Receipt JSON and Receipt Markdown links must return HTTP 200 when clicked or fetched from the browser.
   - Served artifacts must be limited to generated local demo artifacts under the configured workspace/output directories.
   - Path traversal attempts such as `../`, absolute paths outside the workspace, or encoded traversal variants must be blocked with a non-200 response.
   - Content types should be appropriate enough for browser use, for example JSON for receipt JSON, Markdown or text for receipt Markdown, and HTML only for app pages.

5. Result-page Deeper Dive remains navigable and transparent.
   - The result page still exposes Methodology, Node Evidence, Ensemble Contributions, Receipt Artifacts, Trace Hashes, Validation Status, and Optional Model Comparison.
   - Anchor links still work after any receipt-route or link changes.
   - The first visible result content remains the clinician-facing governance summary, not raw JSON or raw node tables.

6. Node audit action behavior remains intact.
   - `OK` processing works.
   - `Adjust` without confirmation is blocked.
   - confirmed `Adjust` is traced and processes.
   - confirmed `Re-check Selected Nodes` writes selected-node re-check results.
   - reviewer actions remain separate from deterministic graph authority.

7. Safety and provenance boundaries remain intact.
   - No direct clinical recommendation, diagnosis, prescribing, ordering, clearance, admission, discharge, or patient-specific medical advice language is introduced.
   - The app remains local, deterministic, constructed/synthetic-data oriented, and not PHI-ready.
   - OpenRouter remains comparison-only and cannot set graph values or final posture.
   - Raw model responses and secrets remain out of committed files.
   - Raw unredacted input must not be copied into committed files or non-gitignored generated reports.

8. Regression tests cover the two browser-discovered failures.
   - Add or update HTTP/app tests proving selected sample cases override stale default textarea content or otherwise follow explicit input-mode semantics.
   - Add or update tests proving receipt JSON and Markdown links are fetchable from the local app.
   - Add path-traversal tests for the artifact-serving route.
   - Keep existing tests for paste, upload, node actions, deeper dive, OpenRouter skip, and forbidden phrases passing.

9. Documentation and status artifacts are updated.
   - Update `README.md` and/or `docs/18_deterministic_poc_status.md` to explain the corrected sample/paste/upload behavior and receipt-link behavior.
   - Update `PROGRESS.md` with the browser remediation result and command evidence.
   - Add a `DECISIONS.md` entry if the fix changes input precedence semantics, adds an artifact-serving route, or adds browser automation as a durable verification path.
   - Update `RELEASE_CHECKLIST.md` if the browser failure changes local-demo readiness status or accepted risks.

10. Final verification passes.

```bash
.venv/bin/python -m pytest -q
PYTHONPATH=src .venv/bin/python -m sentinel_workbench.validate data/cases
PYTHONPATH=src .venv/bin/python -m sentinel_workbench.static_inputs --static-inputs data/static_inputs/static_inputs.json --case-dir data/cases
PYTHONPATH=src .venv/bin/python -m sentinel_workbench.evaluate --case-dir data/cases --out validation/reports/latest.json --receipt-dir data/receipts
PYTHONPATH=src .venv/bin/python -m sentinel_workbench.ux_verification
PATH="$PWD/.venv/bin:$PATH" PYTHONPATH=src .venv/bin/python -m sentinel_workbench.final_verification
PATH="$PWD/.venv/bin:$PATH" PYTHONPATH=src .venv/bin/python -m sentinel_workbench.goal_audit --out-json validation/reports/goal_completion_audit.json --out-markdown docs/21_goal_completion_audit.md
.venv/bin/python -m pip install -e . --dry-run --no-deps
git diff --check
```

Also inspect:

```bash
git status --short --branch
rg -n "not for patient care|governance review support|not a clinical action recommendation|not production" README.md docs src tests data/prepared_inputs data/receipts
rg -n "safe for discharge|medical clearance|cleared for discharge|should prescribe|start medication|place an order" src data/prepared_inputs data/receipts README.md docs --glob '!src/sentinel_workbench/safety.py' --glob '!src/sentinel_workbench/goal_audit.py'
rg -n "sk-or-[A-Za-z0-9_-]{8,}|raw model response" . --glob '!artifacts/**' --glob '!.env' --glob '!tests/**' --glob '!GOAL.md' --glob '!README.md' --glob '!docs/**'
```

The first grep must show safety boundaries in user-visible documentation/artifacts. The second grep must return no unsafe clinical-action recommendations outside explicit safety-rule definitions. The third grep must return no committed OpenRouter-looking secrets or raw model response content outside ignored artifacts and tests that intentionally use fake fixtures.

## SCOPE

Modify only files needed to remediate the live-browser UX failures and preserve the existing clinician-review console behavior.

Expected implementation areas:

- `src/sentinel_workbench/local_app.py`
- `src/sentinel_workbench/demo_run.py` only if receipt link generation must change
- `src/sentinel_workbench/ux_verification.py`
- tests under `tests/`
- a browser verification helper if needed, preferably under `scripts/` or `validation/`
- `README.md`
- `docs/18_deterministic_poc_status.md`
- `docs/21_goal_completion_audit.md`
- `docs/22_local_app_ux_verification.md` or successor browser UX proof artifact
- `DECISIONS.md`
- `PROGRESS.md`
- `RELEASE_CHECKLIST.md`
- regenerated validation reports under `validation/reports/`

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
- `/tmp/sentinel_full_ux_browser_report_1781272352874.json` if still present
- `/tmp/sentinel_sample_selector_focus_sample_focus_1781272436443.json` if still present

Do not modify:

- `.env`
- real PHI or real clinical data
- ignored OpenRouter raw response artifacts except by running local comparison into gitignored `artifacts/`
- unrelated generated caches such as `__pycache__`, `.DS_Store`, `.pytest_cache`, or virtualenv files
- sibling repositories unless a separate goal explicitly authorizes cross-repo work

## SAFETY / PROVENANCE

- Sentinel remains a local deterministic governance-review POC using synthetic or constructed/deidentified-style inputs.
- Do not add direct clinical recommendations, diagnosis logic, prescribing logic, ordering logic, clearance language, admission/discharge instructions, or patient-specific medical advice.
- Do not claim production readiness, PHI readiness, clinical safety validation, regulatory compliance, clinical outcome benefit, or real-world harm prevention.
- Do not weaken future-leakage prevention, redaction/residual-risk gates, reviewer approval gates, forbidden-phrase scanning, receipt traceability, node-audit evidence, ensemble transparency, or graph-authority boundaries.
- OpenRouter and any other model output must remain comparison-only unless a later goal explicitly designs and validates model authority.
- Preserve a clear difference between deterministic graph authority, static role/EvidenceFlow contributions, reviewer actions, optional model comparison, and artifact serving.
- Artifact serving must be read-only, local-demo scoped, path-traversal resistant, and limited to generated review artifacts.
- If a useful idea would require real PHI handling, real clinical workflow integration, production auth, external evidence retrieval, prospective validation, or regulatory analysis, document it as deferred instead of partially implementing it.

## CONSTRAINTS

- Prefer improving the existing stdlib local app.
- Do not introduce a full frontend framework.
- Do not add browser automation as a runtime app dependency.
- If a verification-only dependency or script is introduced, justify it in `DECISIONS.md` and keep it out of production/runtime app behavior.
- Keep visual design utilitarian, dense, and clinician-review oriented.
- Use stable responsive layout constraints so tables, labels, buttons, and summaries do not overlap on narrow or desktop screens.
- Preserve existing public CLI names unless a rename is required for safety and is documented.
- Preserve existing schema semantics and receipt provenance unless a test-backed update is required.
- Do not remove or weaken tests to make the goal pass.
- Keep secrets and raw model responses out of committed files.
- Keep generated reports aligned with actual command output when regenerated.

## ITERATION

1. Start by confirming `git status --short --branch` and reading the source-of-truth files listed in `AGENTS.md`.
2. Reproduce or inspect the two browser failures before editing:
   - selected sample ignored because default textarea wins;
   - receipt links fetch as `404`.
3. Work in small batches:
   - sample/paste/upload input-mode semantics;
   - receipt artifact serving and path safety;
   - HTTP/app regression tests;
   - browser verification artifact;
   - docs/status/audit refresh.
4. After each batch, run the nearest relevant tests.
5. If browser verification is available, use it before final completion and save the report under `validation/reports/`.
6. Record meaningful architecture, safety, dependency, or UX decisions in `DECISIONS.md`.
7. Keep `PROGRESS.md` current with completed batches, command results, and remaining risks.
8. Before completion, rerun the full proof command set and inspect the grep checks.

## STOP

Pause and report current evidence if:

- a change would require real PHI, credentials beyond local OpenRouter comparison, production deployment, or external clinical systems;
- the same browser failure persists after three distinct repair attempts;
- fixing receipt links would require serving files outside the local demo workspace;
- a proposed fix would make sample, paste, or upload behavior ambiguous;
- a proposed fix would weaken redaction, approval, receipt, or graph-authority boundaries;
- the implementation requires adding a full frontend framework or broad route system not justified by this focused remediation;
- required verification cannot run in the local environment.

## COMPLETE

Mark this goal complete only when:

- the browser workflow report records 23/23 passing checks;
- pytest and all documented validation commands exit 0;
- sample, paste, upload, receipt links, node actions, Deeper Dive, OpenRouter skip, and quarantine paths are all verified;
- safety/secret/unsafe-phrase inspections pass;
- `git diff --check` is clean;
- `PROGRESS.md`, `DECISIONS.md` if needed, documentation, and validation reports reflect the actual completed state.
