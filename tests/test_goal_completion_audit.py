import json
from pathlib import Path

from sentinel_workbench.goal_audit import generate_goal_completion_audit
from sentinel_workbench.safety import scan_forbidden_content


ROOT = Path(__file__).resolve().parents[1]


def test_goal_completion_audit_maps_current_25_item_goal(tmp_path):
    report_json = tmp_path / "goal_completion_audit.json"
    report_md = tmp_path / "goal_completion_audit.md"

    generate_goal_completion_audit(
        output_json=report_json,
        output_markdown=report_md,
        evaluation_report_path=ROOT / "validation" / "reports" / "latest.json",
        final_verification_path=ROOT / "validation" / "reports" / "final_verification.json",
        goal_path=ROOT / "GOAL.md",
        status_doc_path=ROOT / "docs" / "18_deterministic_poc_status.md",
    )

    payload = json.loads(report_json.read_text(encoding="utf-8"))
    markdown = report_md.read_text(encoding="utf-8")

    assert payload["proof_item_count"] == 25
    assert payload["pass_count"] == 25
    assert payload["all_pass"] is True
    assert [item["id"] for item in payload["items"]] == list(range(1, 26))
    assert payload["items"][24]["verdict"] == "PASS"
    assert payload["items"][24]["evidence_key"].endswith("validation/reports/final_verification.json")
    assert "25-item" in markdown
    assert "All pass: True" in markdown
    assert "Full Demo Proof Of Done" in markdown
    assert "| 25 |" in markdown
    assert "summary_completeness" in markdown
    assert "Current audit replaces the older 16-item audit" in markdown
    assert scan_forbidden_content(markdown, allow_safety_rule_lists=False) == []


def test_checked_in_goal_completion_audit_is_not_stale():
    text = (ROOT / "docs" / "21_goal_completion_audit.md").read_text(encoding="utf-8")

    assert "25-item" in text
    assert "| 25 |" in text
    assert "All pass: True" in text
    assert "| 25 | Full local verification commands pass and git diff --check is clean. | PASS |" in text
    assert "summary_completeness" in text
    assert "57 tests" not in text


def test_final_verification_report_closes_last_goal_proof_item():
    report = json.loads(
        (ROOT / "validation" / "reports" / "final_verification.json").read_text(encoding="utf-8")
    )

    assert report["report_type"] == "final_verification"
    if report.get("bootstrap") is True:
        assert report["commands"][0]["name"] == "bootstrap_for_self_verification"
        return
    assert "bootstrap" not in report
    assert report["all_pass"] is True
    assert report["pytest_passed"] is True
    assert report["case_validation_passed"] is True
    assert report["static_input_validation_passed"] is True
    assert report["evaluation_report_regenerated"] is True
    assert report["json_syntax_checks_passed"] is True
    assert report["git_diff_check_passed"] is True
    assert report["goal_audit_all_pass_after_regeneration"] is True
    assert report["json_syntax"]["errors"] == []
    assert all(command["exit_code"] == 0 for command in report["commands"])
