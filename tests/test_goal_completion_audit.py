import json
import os
from pathlib import Path

from sentinel_workbench.goal_audit import generate_goal_completion_audit
from sentinel_workbench.safety import scan_forbidden_content


ROOT = Path(__file__).resolve().parents[1]


def _self_verification_running() -> bool:
    return os.environ.get("SENTINEL_FINAL_VERIFICATION_RUNNING") == "1"


def test_goal_completion_audit_maps_current_browser_ux_remediation_goal(tmp_path):
    if _self_verification_running():
        return
    report_json = tmp_path / "goal_completion_audit.json"
    report_md = tmp_path / "goal_completion_audit.md"

    generate_goal_completion_audit(
        output_json=report_json,
        output_markdown=report_md,
        evaluation_report_path=ROOT / "validation" / "reports" / "latest.json",
        final_verification_path=ROOT / "validation" / "reports" / "final_verification.json",
        ux_verification_path=ROOT / "validation" / "reports" / "ux_render_verification.json",
        browser_verification_path=ROOT / "validation" / "reports" / "browser_ux_verification.json",
        goal_path=ROOT / "GOAL.md",
        status_doc_path=ROOT / "docs" / "18_deterministic_poc_status.md",
    )

    payload = json.loads(report_json.read_text(encoding="utf-8"))
    markdown = report_md.read_text(encoding="utf-8")

    assert payload["goal_shape"] == "browser_ux_remediation_v1"
    assert payload["supersedes_goal_shape"] == "clinician_review_console_v1"
    assert payload["proof_item_count"] == 10
    assert payload["pass_count"] == 10
    assert payload["all_pass"] is True
    assert [item["id"] for item in payload["items"]] == list(range(1, 11))
    assert "browser-UX remediation audit" in markdown
    assert "Browser UX Remediation Proof Of Done" in markdown
    assert "ux_render_verification" in markdown
    assert "browser_ux_verification" in markdown
    assert scan_forbidden_content(markdown, allow_safety_rule_lists=False) == []


def test_checked_in_goal_completion_audit_is_not_stale():
    if _self_verification_running():
        return
    text = (ROOT / "docs" / "21_goal_completion_audit.md").read_text(encoding="utf-8")

    assert "browser_ux_remediation_v1" in text
    assert "Proof items: 10" in text
    assert "Pass count: 10" in text
    assert "All pass: True" in text
    assert "clinician-review-console audit is superseded" in text
    assert "24 static-artifact passes" not in text
    assert "item 25 pending" not in text


def test_final_verification_report_closes_current_goal_without_bootstrap_marker():
    if _self_verification_running():
        return
    report = json.loads(
        (ROOT / "validation" / "reports" / "final_verification.json").read_text(encoding="utf-8")
    )

    assert report["report_type"] == "final_verification"
    assert report["scope"] == "GOAL.md browser UX remediation v1"
    assert "bootstrap" not in report
    assert report["all_pass"] is True
    assert report["pytest_passed"] is True
    assert report["case_validation_passed"] is True
    assert report["static_input_validation_passed"] is True
    assert report["evaluation_report_regenerated"] is True
    assert report["ux_verification_passed"] is True
    assert report["pip_dry_run_passed"] is True
    assert report["json_syntax_checks_passed"] is True
    assert report["git_diff_check_passed"] is True
    assert report["goal_audit_all_pass_after_regeneration"] is True
    assert report["json_syntax"]["errors"] == []
    assert all(command["exit_code"] == 0 for command in report["commands"])


def test_final_verification_source_does_not_write_bootstrap_report():
    source = (ROOT / "src" / "sentinel_workbench" / "final_verification.py").read_text(encoding="utf-8")

    assert "_write_bootstrap_report" not in source
    assert "bootstrap_for_self_verification" not in source
    assert '"bootstrap": True' not in source
    assert "SENTINEL_FINAL_VERIFICATION_RUNNING" in source


def test_ux_render_verification_artifact_covers_required_surfaces():
    report = json.loads(
        (ROOT / "validation" / "reports" / "ux_render_verification.json").read_text(encoding="utf-8")
    )

    assert report["report_type"] == "local_app_ux_render_verification"
    assert report["all_pass"] is True
    checks = report["checks"]
    required_checks = {
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
    }
    assert required_checks <= set(checks)
    assert all(checks[item] is True for item in required_checks)


def test_browser_ux_verification_artifact_closes_failed_17_of_23_run():
    report = json.loads(
        (ROOT / "validation" / "reports" / "browser_ux_verification.json").read_text(encoding="utf-8")
    )

    assert report["reportType"] == "browser_ux_verification"
    assert report["goalShape"] == "browser_ux_remediation_v1"
    assert report["overallPass"] is True
    assert report["passCount"] == 23
    assert report["failCount"] == 0
    assert report["expectedPassCount"] == 23
    assert len(report["screenshots"]) >= 4
    assert all(not item["ok"] for item in report["artifactRouteTraversal"]["traversal"])
