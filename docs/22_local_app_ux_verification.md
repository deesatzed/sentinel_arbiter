# 22 - Local App UX Render Verification

Mode: `stdlib_http_rendered_html`
All pass: True

This report is the deterministic rendered-HTML verification artifact for the local stdlib demo app. It exercises the HTTP landing, pre-process, and process-result pages and checks required user-visible stages plus basic layout-breakage guards.

Browser screenshot capture: `captured_separately`. Reason: Deterministic stdlib HTTP rendered-HTML verification is paired with Chrome DevTools evidence in validation/reports/browser_ux_verification.json for browser_ux_remediation_v1.

## Checked Surfaces

- landing page
- pre-process/intake/methodology page
- process result/deeper-dive page

## Checks

| Check | Pass |
|---|---:|
| `landing_has_first_screen_choice` | True |
| `landing_has_responsive_viewport_and_grid` | True |
| `prepare_has_node_audit_before_process` | True |
| `prepare_has_ensemble_before_process` | True |
| `prepare_has_structured_intake_review` | True |
| `prepare_has_methodology_explorer` | True |
| `prepare_has_grouped_ensemble_contributions` | True |
| `prepare_has_checkpoint_controls` | True |
| `result_has_summary_first` | True |
| `result_has_plain_language_summary_cards` | True |
| `result_has_deeper_dive_links` | True |
| `result_has_model_comparison_skip_panel` | True |
| `result_has_validation_and_trace` | True |
| `layout_breakage_guards_present` | True |
| `forbidden_phrase_findings` | True |

## Evidence

- `review_question_selection`: Landing page renders both A/B review choices and sample-case selection before Pre-process.
- `structured_intake`: Pre-process page renders redaction status, structured clinical sections, and advanced JSON fallback.
- `node_audit_methodology`: Pre-process page renders a Methodology Explorer before Process.
- `ensemble_contributions`: Pre-process page renders grouped Ensemble Contributions before Process.
- `clinician_summary`: Result page renders Clinician Summary and summary cards before deeper structured details.
- `deeper_dive`: Result page links methodology, node evidence, ensemble, receipts, trace hashes, validation, and optional model comparison.
- `model_comparison`: Result page labels OpenRouter as skipped/comparison-only unless artifacts are generated separately.
- `layout`: Viewport, responsive grids, fixed table layout, and overflow-wrap guards are present.

## Browser UX Remediation Evidence

- `browser_ux_verification.json`: expected `overallPass=true`, `passCount=23`, `failCount=0` for `browser_ux_remediation_v1`.
- Sample selection: selected synthetic sample cases remain active when the default textarea text is browser-normalized.
- Input precedence: use the selected sample case as the starting point; edited pasted text takes precedence over the sample; uploaded files are used when the text box is empty.
- Receipt artifacts: Receipt JSON and Receipt Markdown links use the local `/artifacts/` route and return HTTP 200 in browser verification.
- Artifact route safety: traversal probes for `../` and encoded traversal return non-OK responses.
