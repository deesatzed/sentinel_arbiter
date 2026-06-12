from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


GOAL_PROOF_ITEMS: tuple[str, ...] = (
    "README.md accurately states that the current goal-completion audit reports 25/25 and points to validation/reports/final_verification.json.",
    "docs/18_deterministic_poc_status.md includes final-verification and goal-audit commands while preserving safety boundaries.",
    "sentinel_workbench.final_verification no longer leaves a plausible all-pass durable report if interrupted during bootstrap/self-verification.",
    "Tests cover the hardened final-verification behavior, including the non-bootstrap committed report requirement.",
    "A rendered-UX verification artifact exists for the local staged app and covers the required workflow surfaces.",
    "PROGRESS.md has a latest-status or supersession note for older chronological entries.",
    "OpenRouter documentation distinguishes implemented comparison harness from deferred app-integrated LLM mode and formal model-swap evaluation.",
    "The goal-completion audit is updated to the new remediation goal shape and is not mistaken for the completed 25-item milestone.",
    "Final local verification commands pass.",
    "Stale status claims and committed bootstrap markers are absent from current proof artifacts.",
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
    items = _build_items(
        goal_text=goal_text,
        status_text=status_text,
        readme_text=readme_text,
        progress_text=progress_text,
        final_verification_source=final_verification_source,
        tests_text=tests_text,
        final_verification=final_verification,
        ux_verification=ux_verification,
        final_verification_path=str(final_verification_path),
        ux_verification_path=str(ux_verification_path),
    )
    pass_count = sum(1 for item in items if item["verdict"] == "PASS")
    payload = {
        "report_type": "goal_completion_audit",
        "goal_file": str(goal_path),
        "goal_shape": "completeness_scan_remediation",
        "supersedes_goal_shape": "25_item_clinician_facing_staged_demo",
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
    final_verification: dict[str, Any],
    ux_verification: dict[str, Any],
    final_verification_path: str,
    ux_verification_path: str,
) -> list[dict[str, object]]:
    checks: tuple[tuple[bool, str, str], ...] = (
        (
            "25/25" in readme_text and "validation/reports/final_verification.json" in readme_text,
            "README.md",
            "README states the completed prior milestone audit is 25/25 and links final verification evidence.",
        ),
        (
            _status_doc_complete(status_text),
            "docs/18_deterministic_poc_status.md",
            "Status document lists final-verification and goal-audit commands and keeps implemented/deferred/not-claimed boundaries.",
        ),
        (
            _final_verification_source_hardened(final_verification_source),
            "src/sentinel_workbench/final_verification.py",
            "Final verification no longer writes a fake all-pass bootstrap report to the durable report path.",
        ),
        (
            _tests_cover_hardened_final_verification(tests_text),
            "tests/test_goal_completion_audit.py",
            "Tests require a non-bootstrap committed final-verification report and allow only explicit self-verification mode during the command run.",
        ),
        (
            _ux_verification_complete(ux_verification),
            ux_verification_path,
            "UX verification report covers landing, pre-process, node audit, ensemble, result summary, deeper dive, and layout guards.",
        ),
        (
            "## Latest Status" in progress_text and "supersede earlier chronological entries" in progress_text,
            "PROGRESS.md",
            "Progress log has a latest-status note explaining that newer sections supersede older chronological pending/future-work entries.",
        ),
        (
            _openrouter_docs_clear(readme_text),
            "README.md",
            "OpenRouter docs separate the implemented comparison harness from deferred app-integrated LLM mode and formal model-swap evaluation.",
        ),
        (
            "completeness_scan_remediation" in goal_text and len(GOAL_PROOF_ITEMS) == 10,
            "GOAL.md, validation/reports/goal_completion_audit.json",
            "Current audit shape is the ten-item completeness-scan remediation goal, not the prior 25-item milestone.",
        ),
        (
            _final_verification_complete(final_verification),
            final_verification_path,
            "Final verification report records passing pytest, case validation, static input validation, evaluation regeneration, UX verification, JSON syntax, and git diff checks.",
        ),
        (
            _stale_claim_scan_clean(readme_text, status_text, progress_text) and "bootstrap" not in json.dumps(final_verification),
            "README.md, docs/, PROGRESS.md, validation/reports/final_verification.json",
            "No stale current-state pending-audit claims or committed bootstrap markers remain.",
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
        "prepare_has_checkpoint_controls",
        "result_has_summary_first",
        "result_has_deeper_dive_links",
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
        "json_syntax_checks_passed",
        "git_diff_check_passed",
    )
    commands = report.get("commands")
    return (
        report.get("report_type") == "final_verification"
        and report.get("scope") == "GOAL.md completeness-scan remediation"
        and report.get("all_pass") is True
        and all(report.get(key) is True for key in required_checks)
        and isinstance(commands, list)
        and bool(commands)
        and all(_dict(command).get("exit_code") == 0 for command in commands)
        and "bootstrap" not in json.dumps(report)
    )


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
        "Current audit maps the completeness-scan remediation `GOAL.md`. The prior 25-item clinician-facing staged-demo audit is superseded by this ten-item remediation audit.",
        "",
        f"Goal shape: `{payload['goal_shape']}`",
        f"Supersedes: `{payload['supersedes_goal_shape']}`",
        f"Proof items: {payload['proof_item_count']}",
        f"Pass count: {payload['pass_count']}",
        f"All pass: {payload['all_pass']}",
        "",
        "Sentinel remains a local deterministic governance-review POC. This audit does not claim clinical safety, production readiness, regulatory compliance, or clinical outcome benefit.",
        "",
        "## Completeness-Scan Remediation Proof Of Done",
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
