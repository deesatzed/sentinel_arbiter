import json
from pathlib import Path

from sentinel_workbench.loader import load_case_library
from sentinel_workbench.receipts import (
    REQUIRED_RECEIPT_FIELDS,
    build_receipt,
    generate_receipts_for_case_library,
    render_receipt_markdown,
)
from sentinel_workbench.safety import scan_forbidden_content


ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = ROOT / "data" / "cases"
STATIC_INPUTS = ROOT / "data" / "static_inputs" / "static_inputs.json"


def test_receipt_contains_required_reconstructable_fields():
    episode = load_case_library(CASE_DIR)[0]

    receipt = build_receipt(episode, STATIC_INPUTS)
    payload = receipt.model_dump(mode="json")

    assert set(REQUIRED_RECEIPT_FIELDS).issubset(payload.keys())
    assert receipt.input_hashes["episode_sha256"]
    assert receipt.input_hashes["static_inputs_sha256"]
    assert receipt.timepoint_id == "T3_disposition_decision"
    assert receipt.node_values
    assert receipt.final_posture
    assert receipt.decision_weight == receipt.node_values["decision_weight"]
    assert receipt.preventability_opportunity_explanation
    assert receipt.signature_placeholder == "UNSIGNED_DETERMINISTIC_POC"


def test_receipt_exposes_node_audit_methodology_and_ensemble_dispositions():
    episode = load_case_library(CASE_DIR)[0]

    receipt = build_receipt(episode, STATIC_INPUTS)
    payload = receipt.model_dump(mode="json")

    assert "node_audit_bundle" in payload
    assert "ensemble_contribution_bundle" in payload
    assert "methodology_summary" in payload
    assert payload["methodology_summary"]["node_audit_complete"] is True
    assert payload["methodology_summary"]["ensemble_contributions_visible"] is True

    audits = payload["node_audit_bundle"]["node_audits"]
    assert len(audits) == len(payload["node_values"])
    for audit in audits:
        estimate = audit["estimate"]
        assert audit["definition"]["dependent_inputs"]
        assert audit["evidence"]
        assert estimate["range_min"] <= estimate["median"] <= estimate["range_max"]
        assert estimate["distribution_kind"]
        assert estimate["method"]
        assert set(estimate["evidence_refs"]).issubset({item["ref_id"] for item in audit["evidence"]})
        assert audit["sensitivity_note"]

    assert payload["ensemble_contribution_bundle"]["contributions"]
    dispositions = {
        contribution["disposition"]
        for contribution in payload["ensemble_contribution_bundle"]["contributions"]
    }
    assert "accepted" in dispositions
    assert "downgraded" in dispositions
    assert payload["ensemble_contribution_bundle"]["rejected_inputs"]


def test_markdown_receipt_has_required_human_readable_sections_without_forbidden_phrases():
    episode = load_case_library(CASE_DIR)[0]
    receipt = build_receipt(episode, STATIC_INPUTS)

    markdown = render_receipt_markdown(receipt)

    required_sections = [
        "What Was Known",
        "What Was Missing",
        "What Would Have Changed The Discussion",
        "What Hospital-Based Monitoring Or Treatment Might Add",
        "What Non-Inpatient Alternatives Might Add",
        "Commission Concerns",
        "Omission Concerns",
        "Therapy-Response Concerns",
        "Why The Graph Selected The Posture",
    ]
    for section in required_sections:
        assert f"## {section}" in markdown
    assert "## Node Audit Methodology" in markdown
    assert "Distribution" in markdown
    assert "Median" in markdown
    assert "Range" in markdown
    assert "Evidence refs" in markdown
    assert "## Ensemble Contributions" in markdown
    assert "accepted" in markdown
    assert "downgraded" in markdown
    assert "Rejected ensemble inputs" in markdown
    assert scan_forbidden_content(markdown, allow_safety_rule_lists=False) == []


def test_generate_receipts_for_all_valid_cases(tmp_path):
    outputs = generate_receipts_for_case_library(CASE_DIR, STATIC_INPUTS, tmp_path)

    assert len(outputs) == 7
    for output in outputs:
        json_path = output["json_path"]
        md_path = output["markdown_path"]
        assert json_path.exists()
        assert md_path.exists()
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        assert set(REQUIRED_RECEIPT_FIELDS).issubset(payload.keys())
        assert scan_forbidden_content(md_path.read_text(encoding="utf-8"), allow_safety_rule_lists=False) == []
