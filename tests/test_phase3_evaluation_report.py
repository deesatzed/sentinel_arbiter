import json
from pathlib import Path

from sentinel_workbench.evaluate import generate_evaluation_report
from sentinel_workbench.receipts import generate_receipts_for_case_library


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "data" / "cases"


def test_evaluation_report_covers_graph_and_validation_metrics(tmp_path):
    report_path = tmp_path / "latest.json"
    receipt_dir = tmp_path / "receipts"
    generate_receipts_for_case_library(FIXTURE_DIR, Path("data/static_inputs/static_inputs.json"), receipt_dir)

    report = generate_evaluation_report(FIXTURE_DIR, report_path, receipt_dir=receipt_dir)
    payload = json.loads(report_path.read_text(encoding="utf-8"))

    assert report.valid_case_count == 7
    assert payload["valid_case_count"] == 7
    assert payload["schema_validity"]["valid_cases"] == 7
    assert payload["future_leakage_failures"] == 0
    assert payload["receipt_completeness"]["complete"] is True
    assert payload["receipt_completeness"]["json_receipts"] == 7
    assert payload["receipt_completeness"]["markdown_receipts"] == 7
    assert payload["lane_coverage"]["commission_lane_cases"] > 0
    assert payload["lane_coverage"]["omission_lane_cases"] > 0
    assert payload["lane_coverage"]["therapy_response_lane_cases"] > 0
    assert payload["expected_posture_agreement"]["total"] == 7
    assert payload["forbidden_phrase_violations"] == 0
    assert payload["static_input_validation"]["errors"] == []
    assert payload["static_input_validation"]["role_template_count"] == 7
    assert payload["static_input_validation"]["evidenceflow_template_count"] == 4
    assert len(payload["case_results"]) == 7


def test_evaluation_report_explicitly_scores_goal_required_validation_categories(tmp_path):
    report_path = tmp_path / "latest.json"
    receipt_dir = tmp_path / "receipts"
    generate_receipts_for_case_library(FIXTURE_DIR, Path("data/static_inputs/static_inputs.json"), receipt_dir)

    generate_evaluation_report(FIXTURE_DIR, report_path, receipt_dir=receipt_dir)
    payload = json.loads(report_path.read_text(encoding="utf-8"))

    automated = payload["automated_validation"]
    required_categories = [
        "omission_detection",
        "commission_warning_detection",
        "therapy_response_integration",
        "next_best_information_usefulness",
    ]
    for category in required_categories:
        assert automated[category]["expected"] > 0
        assert automated[category]["missing"] == []
        assert automated[category]["matched"] == automated[category]["expected"]
