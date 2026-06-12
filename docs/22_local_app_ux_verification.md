# 22 - Local App UX Render Verification

Mode: `stdlib_http_rendered_html`
All pass: True

This report is an equivalent rendered-HTML verification artifact for the local stdlib demo app. It exercises the HTTP landing, pre-process, and process-result pages and checks required user-visible stages plus basic layout-breakage guards.

## Checked Surfaces

- landing page
- pre-process/node-audit page
- process result/review page

## Checks

| Check | Pass |
|---|---:|
| `landing_has_first_screen_choice` | True |
| `landing_has_responsive_viewport_and_grid` | True |
| `prepare_has_node_audit_before_process` | True |
| `prepare_has_ensemble_before_process` | True |
| `prepare_has_checkpoint_controls` | True |
| `result_has_summary_first` | True |
| `result_has_deeper_dive_links` | True |
| `result_has_validation_and_trace` | True |
| `layout_breakage_guards_present` | True |
| `forbidden_phrase_findings` | True |

## Evidence

- `review_question_selection`: Landing page renders both A/B review choices before Pre-process.
- `node_audit_methodology`: Pre-process page renders Node Audit Methodology before Process.
- `ensemble_contributions`: Pre-process page renders Ensemble Contributions before Process.
- `clinician_summary`: Result page renders Clinician Summary before deeper structured details.
- `deeper_dive`: Result page links receipt JSON and Markdown artifacts and shows validation/trace sections.
- `layout`: Viewport, responsive grid, fixed table layout, and overflow-wrap guards are present.
