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
        goal_path=ROOT / "GOAL.md",
        status_doc_path=ROOT / "docs" / "18_deterministic_poc_status.md",
    )

    payload = json.loads(report_json.read_text(encoding="utf-8"))
    markdown = report_md.read_text(encoding="utf-8")

    assert payload["proof_item_count"] == 25
    assert [item["id"] for item in payload["items"]] == list(range(1, 26))
    assert "25-item" in markdown
    assert "Full Demo Proof Of Done" in markdown
    assert "| 25 |" in markdown
    assert "summary_completeness" in markdown
    assert "Current audit replaces the older 16-item audit" in markdown
    assert scan_forbidden_content(markdown, allow_safety_rule_lists=False) == []


def test_checked_in_goal_completion_audit_is_not_stale():
    text = (ROOT / "docs" / "21_goal_completion_audit.md").read_text(encoding="utf-8")

    assert "25-item" in text
    assert "| 25 |" in text
    assert "summary_completeness" in text
    assert "57 tests" not in text
