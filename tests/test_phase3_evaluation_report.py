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
    assert payload["receipt_completeness"]["clinician_summary_complete"] is True
    assert payload["receipt_completeness"]["deeper_dive_artifacts_complete"] is True
    assert payload["receipt_completeness"]["selected_review_question_field_supported"] is True
    assert payload["receipt_completeness"]["markdown_clinician_summary_complete"] is True
    assert payload["receipt_completeness"]["markdown_deeper_dive_complete"] is True
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


def test_evaluation_report_covers_redaction_workbench_and_local_app_completeness(tmp_path):
    report_path = tmp_path / "latest.json"
    receipt_dir = tmp_path / "receipts"
    generate_receipts_for_case_library(FIXTURE_DIR, Path("data/static_inputs/static_inputs.json"), receipt_dir)

    generate_evaluation_report(FIXTURE_DIR, report_path, receipt_dir=receipt_dir)
    payload = json.loads(report_path.read_text(encoding="utf-8"))

    redaction = payload["redaction_gating"]
    assert redaction["complete"] is True
    assert redaction["prepared_demo_status"] == "prepared"
    assert redaction["prepared_demo_has_input_hash"] is True
    assert redaction["safe_redaction_replaces_phi_like_spans"] is True
    assert redaction["unsafe_residual_blocks"] is True
    assert redaction["unsafe_residual_quarantines"] is True
    assert redaction["raw_input_copied_to_review_artifacts"] is False

    workbench = payload["workbench_completeness"]
    assert workbench["complete"] is True
    assert workbench["clinician_summary"] is True
    assert workbench["deeper_dive_artifact_index"] is True
    assert workbench["raw_artifact_links"] is True
    for required in [
        "redacted_input",
        "structured_episode",
        "clinician_summary",
        "deeper_dive_artifact_index",
        "raw_artifact_links",
        "node_audit_methodology",
        "ensemble_contribution_panel",
        "receipt_links",
        "validation_status",
        "poc_warning",
    ]:
        assert required not in workbench["missing"]

    local_app = payload["local_app_completeness"]
    assert local_app["complete"] is True
    assert local_app["stdlib_http_server"] is True
    assert local_app["prepare_endpoint"] is True
    assert local_app["approve_and_run_endpoint"] is True
    assert local_app["console_script_registered"] is True
    assert local_app["review_html_exists"] is True
    assert local_app["review_question_choice_visible"] is True
    assert local_app["preprocess_control_visible"] is True
    assert local_app["multipart_file_upload_supported"] is True
    assert local_app["node_audit_checkpoint_visible"] is True
    assert local_app["adjustment_controls_visible"] is True
    assert local_app["node_audit_review_manifest_supported"] is True
    assert local_app["selected_node_recheck_supported"] is True
    assert local_app["review_html_has_clinician_summary"] is True
    assert local_app["review_html_has_deeper_dive"] is True
    assert local_app["review_html_forbidden_phrase_violations"] == 0
