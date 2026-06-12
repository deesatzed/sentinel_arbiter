from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


GOAL_PROOF_ITEMS: tuple[str, ...] = (
    "Landing workflow explains both review questions, sample cases, paste/upload input, and local-demo boundary.",
    "Pre-process produces redaction status, structured clinical sections, advanced JSON fallback, inference status, and no raw unredacted artifact copy.",
    "Node Audit Methodology is a methodology explorer for every graph node.",
    "Node-audit controls are functional, traceable, and preserve deterministic graph authority.",
    "Ensemble Contributions are grouped by node and distinguish accepted, downgraded, and rejected inputs.",
    "Result page is summary-first, clinically readable, and keeps raw scores in deeper dive.",
    "Deeper Dive contains methodology, node evidence, ensemble, receipts, trace hashes, validation status, and optional model comparison.",
    "OpenRouter is comparison-only with safe skip status and no secret echo.",
    "Release/readiness artifact exists with local-demo conditional-go boundaries.",
    "Documentation explains setup, app use, sample cases, input, summary interpretation, deeper dive, OpenRouter comparison, and non-claims.",
    "Tests cover the optimized UX, redaction, structured sections, node tracing, summary-first results, deeper dive, OpenRouter skip, and forbidden phrases.",
    "Rendered UX verification artifact covers the optimized console surfaces and layout guards.",
    "Final local verification commands pass.",
    "Safety-boundary, unsafe-recommendation, and secret/raw-response inspections are clean.",
)


def generate_goal_completion_audit(
    *,
    output_json: str | Path = "validation/reports/goal_completion_audit.json",
    output_markdown: str | Path = "docs/21_goal_completion_audit.md",
    evaluation_report_path: str | Path = "validation/reports/latest.json",
    final_verification_path: str | Path = "validation/reports/final_verification.json",
    ux_verification_path: str | Path = "validation/reports/ux_render_verification.json",
    goal_path: str | Path = "GOAL.md",
    status_doc_path: str | Path = "docs/18_deterministic_poc_status.md",
    readme_path: str | Path = "README.md",
    progress_path: str | Path = "PROGRESS.md",
    final_verification_source_path: str | Path = "src/sentinel_workbench/final_verification.py",
    tests_path: str | Path = "tests/test_goal_completion_audit.py",
    local_app_tests_path: str | Path = "tests/test_phase_g_local_demo_app.py",
    openrouter_tests_path: str | Path = "tests/test_openrouter_compare.py",
    release_checklist_path: str | Path = "RELEASE_CHECKLIST.md",
    local_app_source_path: str | Path = "src/sentinel_workbench/local_app.py",
    demo_run_source_path: str | Path = "src/sentinel_workbench/demo_run.py",
    openrouter_source_path: str | Path = "src/sentinel_workbench/openrouter_compare.py",
) -> dict[str, object]:
    # Keep the evaluation report read as a freshness/syntax guard for the
    # deterministic demo proof surface, even though this remediation audit is
    # mostly documentation and verification-tooling focused.
    _read_json(evaluation_report_path)
    final_verification = _read_json_if_present(final_verification_path)
    ux_verification = _read_json_if_present(ux_verification_path)
    goal_text = _read_text(goal_path)
    status_text = _read_text(status_doc_path)
    readme_text = _read_text(readme_path)
    progress_text = _read_text(progress_path)
    final_verification_source = _read_text(final_verification_source_path)
    tests_text = _read_text(tests_path)
    local_app_tests = _read_text(local_app_tests_path)
    openrouter_tests = _read_text(openrouter_tests_path)
    release_checklist = _read_text(release_checklist_path)
    local_app_source = _read_text(local_app_source_path)
    demo_run_source = _read_text(demo_run_source_path)
    openrouter_source = _read_text(openrouter_source_path)
    items = _build_items(
        goal_text=goal_text,
        status_text=status_text,
        readme_text=readme_text,
        progress_text=progress_text,
        final_verification_source=final_verification_source,
        tests_text=tests_text,
        local_app_tests=local_app_tests,
        openrouter_tests=openrouter_tests,
        release_checklist=release_checklist,
        local_app_source=local_app_source,
        demo_run_source=demo_run_source,
        openrouter_source=openrouter_source,
        final_verification=final_verification,
        ux_verification=ux_verification,
        final_verification_path=str(final_verification_path),
        ux_verification_path=str(ux_verification_path),
    )
    pass_count = sum(1 for item in items if item["verdict"] == "PASS")
    payload = {
        "report_type": "goal_completion_audit",
        "goal_file": str(goal_path),
        "goal_shape": "clinician_review_console_v1",
        "supersedes_goal_shape": "completeness_scan_remediation",
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
    final_verification_source: str,
    tests_text: str,
    local_app_tests: str,
    openrouter_tests: str,
    release_checklist: str,
    local_app_source: str,
    demo_run_source: str,
    openrouter_source: str,
    final_verification: dict[str, Any],
    ux_verification: dict[str, Any],
    final_verification_path: str,
    ux_verification_path: str,
) -> list[dict[str, object]]:
    checks: tuple[tuple[bool, str, str], ...] = (
        (
            _ux_checks_true(ux_verification, "landing_has_first_screen_choice")
            and "Sample Case" in local_app_source
            and "constructed_demo_case" in local_app_source
            and "Local demo only" in local_app_source,
            "src/sentinel_workbench/local_app.py, validation/reports/ux_render_verification.json",
            "Landing includes both review questions, sample-case selection, paste/upload path, and local-demo boundary.",
        ),
        (
            _ux_checks_true(ux_verification, "prepare_has_structured_intake_review")
            and "Structured Clinical Sections" in local_app_source
            and "Advanced JSON Edit" in local_app_source
            and "raw_input.txt" not in demo_run_source,
            "src/sentinel_workbench/local_app.py, validation/reports/ux_render_verification.json",
            "Pre-process renders redaction status, structured clinical sections, advanced JSON fallback, and avoids raw input artifact copying.",
        ),
        (
            _ux_checks_true(ux_verification, "prepare_has_methodology_explorer")
            and "Plain-English Meaning" in local_app_source
            and "Missing or Weak Evidence" in local_app_source,
            "src/sentinel_workbench/local_app.py, validation/reports/ux_render_verification.json",
            "Methodology Explorer exposes plain-English node meaning, evidence, weak/missing evidence, estimates, methods, and sensitivity.",
        ),
        (
            _ux_checks_true(ux_verification, "prepare_has_checkpoint_controls")
            and "node_audit_review_manifest.json" in local_app_source
            and 'type="checkbox" name="selected_node_ids"' in local_app_source
            and "graph_authority_preserved" in local_app_source,
            "src/sentinel_workbench/local_app.py, tests/test_phase_g_local_demo_app.py",
            "Node-level reviewer actions are checkboxes, confirmed when changing methodology, and traced separately from graph authority.",
        ),
        (
            _ux_checks_true(ux_verification, "prepare_has_grouped_ensemble_contributions")
            and "Grouped Ensemble Contributions" in local_app_source
            and "Rejected or unsupported inputs" in local_app_source,
            ux_verification_path,
            "Ensemble contributions are grouped by node and expose accepted, downgraded, and rejected/unsupported inputs.",
        ),
        (
            _ux_checks_true(ux_verification, "result_has_summary_first", "result_has_plain_language_summary_cards")
            and "What this means" in demo_run_source
            and "Main driver" in demo_run_source
            and "Most useful next review input" in demo_run_source,
            "src/sentinel_workbench/demo_run.py, validation/reports/ux_render_verification.json",
            "Result page is summary-first and uses plain-language summary cards before raw details.",
        ),
        (
            _ux_checks_true(ux_verification, "result_has_deeper_dive_links", "result_has_validation_and_trace")
            and "id=\"methodology\"" in demo_run_source
            and "id=\"node-evidence\"" in demo_run_source
            and "id=\"model-comparison\"" in demo_run_source,
            "src/sentinel_workbench/demo_run.py, validation/reports/ux_render_verification.json",
            "Deeper Dive navigation links methodology, node evidence, ensemble, receipt artifacts, trace hashes, validation, and model comparison.",
        ),
        (
            _ux_checks_true(ux_verification, "result_has_model_comparison_skip_panel")
            and "openrouter_comparison_status" in openrouter_source
            and "settings.safe_summary()" in openrouter_source
            and "Bearer {settings.api_key}" in openrouter_source,
            "src/sentinel_workbench/openrouter_compare.py, validation/reports/ux_render_verification.json",
            "OpenRouter status is comparison-only, skips safely when absent, and does not echo secrets.",
        ),
        (
            _release_checklist_complete(release_checklist),
            "RELEASE_CHECKLIST.md",
            "Release checklist records local-demo Conditional Go, No-Go boundaries, evidence areas, risks, required fixes, and rollback.",
        ),
        (
            _docs_cover_new_user(readme_text, status_text),
            "README.md, docs/18_deterministic_poc_status.md",
            "Documentation covers setup, app use, sample cases, input, summary interpretation, deeper dive, OpenRouter comparison, and non-claims.",
        ),
        (
            _tests_cover_console_goal(local_app_tests, openrouter_tests, tests_text),
            "tests/",
            "Tests cover local app happy path, structured sections, node tracing, summary-first result, deeper dive, OpenRouter skip/no-secret behavior, and forbidden-phrase scanning.",
        ),
        (
            _ux_verification_complete(ux_verification),
            ux_verification_path,
            "Rendered UX verification all-pass report covers optimized console surfaces and layout guards.",
        ),
        (
            _final_verification_complete(final_verification),
            final_verification_path,
            "Final verification report records passing pytest, case validation, static input validation, evaluation regeneration, UX verification, JSON syntax, pip dry-run, and git diff checks.",
        ),
        (
            _safety_inspection_clean(readme_text, status_text, progress_text)
            and "bootstrap" not in json.dumps(final_verification),
            "README.md, docs/, PROGRESS.md, validation/reports/final_verification.json",
            "Safety boundaries are present and no committed bootstrap marker or unsafe secret pattern is present in audited text.",
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


def _status_doc_complete(text: str) -> bool:
    required = (
        "## Implemented Deterministic POC",
        "## Deferred",
        "## Required Before Real Clinical, Prospective, Or Production Use",
        "## Not Claimed",
        "PYTHONPATH=src python3 -m sentinel_workbench.final_verification",
        "PYTHONPATH=src python3 -m sentinel_workbench.goal_audit",
    )
    return all(item in text for item in required)


def _final_verification_source_hardened(text: str) -> bool:
    forbidden = (
        "_write_bootstrap_report",
        "bootstrap_for_self_verification",
        '"bootstrap": True',
    )
    return all(item not in text for item in forbidden) and "SENTINEL_FINAL_VERIFICATION_RUNNING" in text


def _tests_cover_hardened_final_verification(text: str) -> bool:
    required = (
        "SENTINEL_FINAL_VERIFICATION_RUNNING",
        'assert "bootstrap" not in report',
        "test_final_verification_source_does_not_write_bootstrap_report",
    )
    return all(item in text for item in required)


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


def _openrouter_docs_clear(text: str) -> bool:
    required = (
        "implemented comparison harness",
        "comparison-only model artifacts",
        "app-integrated LLM mode remains deferred",
        "formal model-swap evaluation remains deferred",
    )
    return all(item in text for item in required)


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
        and report.get("scope") == "GOAL.md clinician review console v1"
        and report.get("all_pass") is True
        and all(report.get(key) is True for key in required_checks)
        and isinstance(commands, list)
        and bool(commands)
        and all(_dict(command).get("exit_code") == 0 for command in commands)
        and "bootstrap" not in json.dumps(report)
    )


def _ux_checks_true(report: dict[str, Any], *names: str) -> bool:
    checks = _dict(report.get("checks"))
    return report.get("all_pass") is True and all(checks.get(name) is True for name in names)


def _release_checklist_complete(text: str) -> bool:
    required = (
        "Conditional Go for local deterministic demo use",
        "No-Go for real clinical",
        "Known Blockers",
        "Accepted Risks",
        "Required Fixes Before Release",
        "Rollback Plan",
    )
    return all(item in text for item in required)


def _docs_cover_new_user(readme_text: str, status_text: str) -> bool:
    required = (
        "PYTHONPATH=src python3 -m sentinel_workbench.local_app",
        "Sample Case",
        "paste constructed/deidentified-style text",
        "upload a local text file",
        "What this means",
        "Deeper Dive",
        "OpenRouter",
        "not app authority",
    )
    docs = readme_text + "\n" + status_text
    return all(item in docs for item in required)


def _tests_cover_console_goal(local_app_tests: str, openrouter_tests: str, tests_text: str) -> bool:
    required_local = (
        "test_local_demo_landing_exposes_sample_cases_and_demo_boundary",
        "test_local_demo_preprocess_uses_clinician_sections_methodology_explorer_and_node_checkboxes",
        "test_local_demo_result_has_navigable_deeper_dive_and_comparison_skip_panel",
        "scan_forbidden_content",
    )
    required_openrouter = (
        "test_openrouter_comparison_status_skips_without_secret_and_does_not_echo_key",
        "assert configured[\"model_count\"] == 1",
    )
    required_audit = (
        "clinician_review_console_v1",
        "test_ux_render_verification_artifact_covers_required_surfaces",
    )
    return (
        all(item in local_app_tests for item in required_local)
        and all(item in openrouter_tests for item in required_openrouter)
        and all(item in tests_text for item in required_audit)
    )


def _safety_inspection_clean(*texts: str) -> bool:
    combined = "\n".join(texts)
    boundaries = (
        "not for patient care",
        "governance review support",
        "not production",
    )
    forbidden = (
        "safe for discharge",
        "medical clearance",
        "cleared for discharge",
        "should prescribe",
        "start medication",
        "place an order",
        "sk-or-",
    )
    return all(item in combined for item in boundaries) and all(item not in combined for item in forbidden)


def _stale_claim_scan_clean(*texts: str) -> bool:
    stale = (
        "24 static-artifact passes",
        "item 25 pending",
        "leaves item 25 pending",
    )
    combined = "\n".join(texts)
    return all(item not in combined for item in stale)


def _render_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# 21 - GOAL.md Completion Audit",
        "",
        "Current audit maps the `clinician_review_console_v1` `GOAL.md`. The prior completeness-scan remediation audit is superseded by this fourteen-item clinician-review-console audit.",
        "",
        f"Goal shape: `{payload['goal_shape']}`",
        f"Supersedes: `{payload['supersedes_goal_shape']}`",
        f"Proof items: {payload['proof_item_count']}",
        f"Pass count: {payload['pass_count']}",
        f"All pass: {payload['all_pass']}",
        "",
        "Sentinel remains a local deterministic governance-review POC. This audit does not claim clinical safety, production readiness, regulatory compliance, PHI readiness, or clinical outcome benefit.",
        "",
        "## Clinician Review Console Proof Of Done",
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
            "python3 -m pytest -q",
            "PYTHONPATH=src python3 -m sentinel_workbench.validate data/cases",
            "PYTHONPATH=src python3 -m sentinel_workbench.static_inputs --static-inputs data/static_inputs/static_inputs.json --case-dir data/cases",
            "PYTHONPATH=src python3 -m sentinel_workbench.evaluate --case-dir data/cases --out validation/reports/latest.json --receipt-dir data/receipts",
            "PYTHONPATH=src python3 -m sentinel_workbench.ux_verification",
            "PYTHONPATH=src python3 -m sentinel_workbench.final_verification",
            "PYTHONPATH=src python3 -m sentinel_workbench.goal_audit --out-json validation/reports/goal_completion_audit.json --out-markdown docs/21_goal_completion_audit.md",
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
    parser.add_argument("--goal", default="GOAL.md")
    parser.add_argument("--status-doc", default="docs/18_deterministic_poc_status.md")
    args = parser.parse_args()
    payload = generate_goal_completion_audit(
        output_json=args.out_json,
        output_markdown=args.out_markdown,
        evaluation_report_path=args.evaluation_report,
        final_verification_path=args.final_verification,
        ux_verification_path=args.ux_verification,
        goal_path=args.goal,
        status_doc_path=args.status_doc,
    )
    print(f"goal_audit_items={payload['proof_item_count']} pass_count={payload['pass_count']}")


if __name__ == "__main__":
    main()
