from pathlib import Path

from sentinel_workbench.loader import load_case_library
from sentinel_workbench.safety import scan_forbidden_content
from sentinel_workbench.workbench import generate_workbench


ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = ROOT / "data" / "cases"
RECEIPT_DIR = ROOT / "data" / "receipts"
REPORT = ROOT / "validation" / "reports" / "latest.json"


def test_generate_static_reviewer_workbench_with_required_panels(tmp_path):
    output_path = tmp_path / "index.html"

    result = generate_workbench(
        case_dir=CASE_DIR,
        receipt_dir=RECEIPT_DIR,
        report_path=REPORT,
        output_path=output_path,
    )

    html = output_path.read_text(encoding="utf-8")
    required_panel_ids = [
        "case-library",
        "timeline-replay",
        "information-gap-panel",
        "therapy-response-panel",
        "commission-omission-panel",
        "provenance-panel",
        "two-clock-panel",
        "next-best-input-panel",
        "graph-inspector",
        "receipt-viewer-export",
        "evaluation-dashboard",
    ]
    for panel_id in required_panel_ids:
        assert f'id="{panel_id}"' in html

    for episode in load_case_library(CASE_DIR):
        assert episode.episode_id in html
        assert f'id="case-{episode.episode_id}"' in html

    assert result.case_count == 7
    assert result.output_path == output_path
    assert "Planning / governance POC - not for patient care." in html
    assert "receipts/json/receipt_" in html
    assert "receipts/markdown/receipt_" in html
    assert "Final posture" in html
    assert "Hidden future facts blocked" in html
    assert scan_forbidden_content(html, allow_safety_rule_lists=False) == []
