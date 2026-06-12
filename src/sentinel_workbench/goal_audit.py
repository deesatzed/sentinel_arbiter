from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


GOAL_PROOF_ITEMS: tuple[str, ...] = (
    "Chrome DevTools browser workflow passes 23/23 and saves a durable browser UX report.",
    "Sample-case selection works in the normal reviewer path without manually clearing default text.",
    "Landing input UX makes sample, pasted text, and uploaded file precedence clear.",
    "Receipt JSON and Markdown links work in the live local browser and artifact serving blocks traversal.",
    "Result-page Deeper Dive remains navigable and summary-first.",
    "Node audit OK, Adjust, and Re-check behavior remains functional and traceable.",
    "Safety and provenance boundaries remain intact.",
    "Regression tests cover the two browser-discovered failures.",
    "Documentation and status artifacts describe the remediated browser behavior.",
    "Final local verification commands pass.",
)


def generate_goal_completion_audit(
    *,
    output_json: str | Path = "validation/reports/goal_completion_audit.json",
    output_markdown: str | Path = "docs/21_goal_completion_audit.md",
    evaluation_report_path: str | Path = "validation/reports/latest.json",
    final_verification_path: str | Path = "validation/reports/final_verification.json",
    ux_verification_path: str | Path = "validation/reports/ux_render_verification.json",
    browser_verification_path: str | Path = "validation/reports/browser_ux_verification.json",
    goal_path: str | Path = "GOAL.md",
    status_doc_path: str | Path = "docs/18_deterministic_poc_status.md",
    readme_path: str | Path = "README.md",
    progress_path: str | Path = "PROGRESS.md",
    tests_path: str | Path = "tests/test_goal_completion_audit.py",
    local_app_tests_path: str | Path = "tests/test_phase_g_local_demo_app.py",
    release_checklist_path: str | Path = "RELEASE_CHECKLIST.md",
    decisions_path: str | Path = "DECISIONS.md",
    local_app_source_path: str | Path = "src/sentinel_workbench/local_app.py",
    demo_run_source_path: str | Path = "src/sentinel_workbench/demo_run.py",
) -> dict[str, object]:
    _read_json(evaluation_report_path)
    final_verification = _read_json_if_present(final_verification_path)
    ux_verification = _read_json_if_present(ux_verification_path)
    browser_verification = _read_json_if_present(browser_verification_path)
    goal_text = _read_text(goal_path)
    status_text = _read_text(status_doc_path)
    readme_text = _read_text(readme_path)
    progress_text = _read_text(progress_path)
    tests_text = _read_text(tests_path)
    local_app_tests = _read_text(local_app_tests_path)
    release_checklist = _read_text(release_checklist_path)
    decisions_text = _read_text(decisions_path)
    local_app_source = _read_text(local_app_source_path)
    demo_run_source = _read_text(demo_run_source_path)

    items = _build_items(
        goal_text=goal_text,
        status_text=status_text,
        readme_text=readme_text,
        progress_text=progress_text,
        tests_text=tests_text,
        local_app_tests=local_app_tests,
        release_checklist=release_checklist,
        decisions_text=decisions_text,
        local_app_source=local_app_source,
        demo_run_source=demo_run_source,
        final_verification=final_verification,
        ux_verification=ux_verification,
        browser_verification=browser_verification,
        final_verification_path=str(final_verification_path),
        ux_verification_path=str(ux_verification_path),
        browser_verification_path=str(browser_verification_path),
    )
    pass_count = sum(1 for item in items if item["verdict"] == "PASS")
    payload = {
        "report_type": "goal_completion_audit",
        "goal_file": str(goal_path),
        "goal_shape": "browser_ux_remediation_v1",
        "supersedes_goal_shape": "clinician_review_console_v1",
        "proof_item_count": len(items),
        "pass_count": pass_count,
        "all_pass": pass_count == len(items),
        "items": items,
    }
    json_path = Path(output_json)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    markdown_path = Path(output_markdown)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(_render_markdown(payload), encoding="utf-8")
    return payload


def _build_items(
    *,
    goal_text: str,
    status_text: str,
    readme_text: str,
    progress_text: str,
    tests_text: str,
    local_app_tests: str,
    release_checklist: str,
    decisions_text: str,
    local_app_source: str,
    demo_run_source: str,
    final_verification: dict[str, Any],
    ux_verification: dict[str, Any],
    browser_verification: dict[str, Any],
    final_verification_path: str,
    ux_verification_path: str,
    browser_verification_path: str,
) -> list[dict[str, object]]:
    checks: tuple[tuple[bool, str, str], ...] = (
        (
            _browser_verification_complete(browser_verification),
            browser_verification_path,
            "Browser UX verification records 23 passing workflow checks, zero failures, screenshots, and blocked traversal evidence.",
        ),
        (
            "test_local_demo_sample_selection_overrides_default_textarea_in_browser_form" in local_app_tests
            and "_is_default_constructed_text" in local_app_source
            and _browser_result_pass(browser_verification, "sample case preprocess workflow"),
            "src/sentinel_workbench/local_app.py, tests/test_phase_g_local_demo_app.py, validation/reports/browser_ux_verification.json",
            "Browser-style sample selection now records sample_case mode and renders the selected synthetic sample.",
        ),
        (
            "Edited pasted text takes precedence over the sample" in local_app_source
            and "use the selected sample case" in (readme_text + status_text).lower()
            and _browser_result_pass(browser_verification, "landing_desktop: landing essentials"),
            "src/sentinel_workbench/local_app.py, README.md, docs/18_deterministic_poc_status.md",
            "Landing copy explains sample, pasted text, and upload precedence.",
        ),
        (
            "test_local_demo_serves_result_receipt_links_and_blocks_traversal" in local_app_tests
            and "_resolve_local_artifact" in local_app_source
            and '"/artifacts/' in demo_run_source
            and _receipt_link_checks_pass(browser_verification)
            and _artifact_traversal_blocked(browser_verification),
            "src/sentinel_workbench/local_app.py, src/sentinel_workbench/demo_run.py, tests/test_phase_g_local_demo_app.py",
            "Receipt JSON/Markdown links use a scoped artifact route and traversal probes return non-OK responses.",
        ),
        (
            _ux_verification_complete(ux_verification)
            and _browser_result_pass(browser_verification, "sample_result: result/deeper-dive content")
            and _browser_result_pass(browser_verification, "sample result: anchor #methodology")
            and _browser_result_pass(browser_verification, "sample result: anchor #ensemble-contributions"),
            f"{ux_verification_path}, {browser_verification_path}",
            "Deeper Dive navigation and summary-first result checks remain green in rendered and browser verification.",
        ),
        (
            _browser_result_pass(browser_verification, "adjust without confirmation is blocked")
            and _browser_result_pass(browser_verification, "adjust_confirmed_result: result/deeper-dive content")
            and _browser_result_pass(browser_verification, "recheck_result: result/deeper-dive content")
            and _browser_result_pass(browser_verification, "recheck trace visible in result hashes")
            and "graph_authority_preserved" in local_app_source,
            "src/sentinel_workbench/local_app.py, validation/reports/browser_ux_verification.json",
            "OK, Adjust, and Re-check workflow behavior remains traceable and graph authority stays separate.",
        ),
        (
            _safety_inspection_clean(readme_text, status_text, progress_text, release_checklist)
            and "OpenRouter remains comparison-only" in goal_text,
            "GOAL.md, README.md, docs/, PROGRESS.md, RELEASE_CHECKLIST.md",
            "Local deterministic governance-review boundaries and comparison-only model boundaries remain documented.",
        ),
        (
            _tests_cover_browser_goal(local_app_tests, tests_text),
            "tests/test_phase_g_local_demo_app.py, tests/test_goal_completion_audit.py",
            "Regression tests cover sample precedence, live receipt links, traversal blocking, and durable browser report shape.",
        ),
        (
            _docs_cover_browser_remediation(readme_text, status_text, progress_text, decisions_text, release_checklist),
            "README.md, docs/18_deterministic_poc_status.md, PROGRESS.md, DECISIONS.md, RELEASE_CHECKLIST.md",
            "Docs and progress artifacts describe corrected sample input semantics, artifact links, browser verification, and readiness impact.",
        ),
        (
            _final_verification_complete(final_verification),
            final_verification_path,
            "Final verification report records passing pytest, validation commands, UX verification, JSON syntax, pip dry-run, and git diff checks.",
        ),
    )

    items: list[dict[str, object]] = []
    for index, (passed, evidence_key, evidence) in enumerate(checks, start=1):
        items.append(
            {
                "id": index,
                "requirement": GOAL_PROOF_ITEMS[index - 1],
                "verdict": "PASS" if passed else "PENDING",
                "evidence_key": evidence_key,
                "evidence": evidence,
            }
        )
    return items


def _browser_verification_complete(report: dict[str, Any]) -> bool:
    return (
        report.get("reportType") == "browser_ux_verification"
        and report.get("goalShape") == "browser_ux_remediation_v1"
        and report.get("overallPass") is True
        and report.get("passCount") == 23
        and report.get("failCount") == 0
        and report.get("expectedPassCount") == 23
        and len(report.get("screenshots", [])) >= 4
        and _artifact_traversal_blocked(report)
    )


def _browser_result_pass(report: dict[str, Any], name: str) -> bool:
    results = report.get("results")
    if not isinstance(results, list):
        return False
    return any(_dict(item).get("name") == name and _dict(item).get("pass") is True for item in results)


def _receipt_link_checks_pass(report: dict[str, Any]) -> bool:
    results = report.get("results")
    if not isinstance(results, list):
        return False
    receipt_checks = [
        _dict(item)
        for item in results
        if str(_dict(item).get("name", "")).endswith(": receipt artifact links fetch")
    ]
    if len(receipt_checks) < 5:
        return False
    return all(item.get("pass") is True for item in receipt_checks)


def _artifact_traversal_blocked(report: dict[str, Any]) -> bool:
    traversal = _dict(report.get("artifactRouteTraversal")).get("traversal")
    if not isinstance(traversal, list) or not traversal:
        return False
    return all(_dict(item).get("ok") is False for item in traversal)


def _ux_verification_complete(report: dict[str, Any]) -> bool:
    checks = _dict(report.get("checks"))
    required = (
        "landing_has_first_screen_choice",
        "landing_has_responsive_viewport_and_grid",
        "prepare_has_node_audit_before_process",
        "prepare_has_ensemble_before_process",
        "prepare_has_structured_intake_review",
        "prepare_has_methodology_explorer",
        "prepare_has_grouped_ensemble_contributions",
        "prepare_has_checkpoint_controls",
        "result_has_summary_first",
        "result_has_plain_language_summary_cards",
        "result_has_deeper_dive_links",
        "result_has_model_comparison_skip_panel",
        "result_has_validation_and_trace",
        "layout_breakage_guards_present",
        "forbidden_phrase_findings",
    )
    return (
        report.get("report_type") == "local_app_ux_render_verification"
        and report.get("all_pass") is True
        and all(checks.get(item) is True for item in required)
    )


def _final_verification_complete(report: dict[str, Any]) -> bool:
    required_checks = (
        "pytest_passed",
        "case_validation_passed",
        "static_input_validation_passed",
        "evaluation_report_regenerated",
        "ux_verification_passed",
        "pip_dry_run_passed",
        "json_syntax_checks_passed",
        "git_diff_check_passed",
    )
    commands = report.get("commands")
    return (
        report.get("report_type") == "final_verification"
        and report.get("scope") == "GOAL.md browser UX remediation v1"
        and report.get("all_pass") is True
        and all(report.get(key) is True for key in required_checks)
        and isinstance(commands, list)
        and bool(commands)
        and all(_dict(command).get("exit_code") == 0 for command in commands)
        and "bootstrap" not in json.dumps(report)
    )


def _tests_cover_browser_goal(local_app_tests: str, tests_text: str) -> bool:
    required_local = (
        "test_local_demo_sample_selection_overrides_default_textarea_in_browser_form",
        "test_local_demo_serves_result_receipt_links_and_blocks_traversal",
        "test_local_demo_accepts_uploaded_constructed_text_file_for_preprocess",
        "test_local_demo_records_adjustment_and_recheck_manifest_before_processing",
        "scan_forbidden_content",
    )
    required_audit = (
        "browser_ux_remediation_v1",
        "test_browser_ux_verification_artifact_closes_failed_17_of_23_run",
    )
    return all(item in local_app_tests for item in required_local) and all(item in tests_text for item in required_audit)


def _docs_cover_browser_remediation(
    readme_text: str,
    status_text: str,
    progress_text: str,
    decisions_text: str,
    release_checklist: str,
) -> bool:
    docs = "\n".join((readme_text, status_text, progress_text, decisions_text, release_checklist))
    docs_lower = docs.lower()
    required = (
        "browser_ux_remediation_v1",
        "23/23",
        "/artifacts/",
        "browser_ux_verification.json",
        "Receipt JSON",
        "Receipt Markdown",
    )
    return all(item in docs for item in required) and "edited pasted text takes precedence over the sample" in docs_lower


def _safety_inspection_clean(*texts: str) -> bool:
    combined = "\n".join(texts)
    boundaries = (
        "not for patient care",
        "governance review support",
        "not production",
    )
    forbidden = (
        "safe to discharge",
        "unsafe to discharge",
        "should admit",
        "should discharge",
        "medically cleared",
        "appropriate for discharge",
        "inappropriate for discharge",
        "recommended pathway",
        "preferred pathway",
        "sk-or-",
    )
    return all(item in combined for item in boundaries) and all(item not in combined for item in forbidden)


def _render_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# 21 - GOAL.md Completion Audit",
        "",
        "Current audit maps the `browser_ux_remediation_v1` `GOAL.md`. The prior clinician-review-console audit is superseded by this ten-item browser-UX remediation audit.",
        "",
        f"Goal shape: `{payload['goal_shape']}`",
        f"Supersedes: `{payload['supersedes_goal_shape']}`",
        f"Proof items: {payload['proof_item_count']}",
        f"Pass count: {payload['pass_count']}",
        f"All pass: {payload['all_pass']}",
        "",
        "Sentinel remains a local deterministic governance-review POC. This audit does not claim clinical safety, production readiness, regulatory compliance, PHI readiness, or clinical outcome benefit.",
        "",
        "## Browser UX Remediation Proof Of Done",
        "",
        "| # | Requirement | Verdict | Evidence Surface | Evidence |",
        "|---:|---|---|---|---|",
    ]
    for item in payload["items"]:
        lines.append(
            f"| {item['id']} | {item['requirement']} | {item['verdict']} | "
            f"`{item['evidence_key']}` | {item['evidence']} |"
        )
    lines.extend(
        [
            "",
            "## Verification Commands",
            "",
            "```bash",
            ".venv/bin/python -m pytest -q",
            "PYTHONPATH=src .venv/bin/python -m sentinel_workbench.validate data/cases",
            "PYTHONPATH=src .venv/bin/python -m sentinel_workbench.static_inputs --static-inputs data/static_inputs/static_inputs.json --case-dir data/cases",
            "PYTHONPATH=src .venv/bin/python -m sentinel_workbench.evaluate --case-dir data/cases --out validation/reports/latest.json --receipt-dir data/receipts",
            "PYTHONPATH=src .venv/bin/python -m sentinel_workbench.ux_verification",
            "PATH=\"$PWD/.venv/bin:$PATH\" PYTHONPATH=src .venv/bin/python -m sentinel_workbench.final_verification",
            "PATH=\"$PWD/.venv/bin:$PATH\" PYTHONPATH=src .venv/bin/python -m sentinel_workbench.goal_audit --out-json validation/reports/goal_completion_audit.json --out-markdown docs/21_goal_completion_audit.md",
            ".venv/bin/python -m pip install -e . --dry-run --no-deps",
            "git diff --check",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def _read_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _read_json_if_present(path: str | Path) -> dict[str, Any]:
    candidate = Path(path)
    if not candidate.exists():
        return {}
    return _read_json(candidate)


def _read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def _dict(value: object) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the current GOAL.md completion audit.")
    parser.add_argument("--out-json", default="validation/reports/goal_completion_audit.json")
    parser.add_argument("--out-markdown", default="docs/21_goal_completion_audit.md")
    parser.add_argument("--evaluation-report", default="validation/reports/latest.json")
    parser.add_argument("--final-verification", default="validation/reports/final_verification.json")
    parser.add_argument("--ux-verification", default="validation/reports/ux_render_verification.json")
    parser.add_argument("--browser-verification", default="validation/reports/browser_ux_verification.json")
    parser.add_argument("--goal", default="GOAL.md")
    parser.add_argument("--status-doc", default="docs/18_deterministic_poc_status.md")
    args = parser.parse_args()
    payload = generate_goal_completion_audit(
        output_json=args.out_json,
        output_markdown=args.out_markdown,
        evaluation_report_path=args.evaluation_report,
        final_verification_path=args.final_verification,
        ux_verification_path=args.ux_verification,
        browser_verification_path=args.browser_verification,
        goal_path=args.goal,
        status_doc_path=args.status_doc,
    )
    print(f"goal_audit_items={payload['proof_item_count']} pass_count={payload['pass_count']}")


if __name__ == "__main__":
    main()
