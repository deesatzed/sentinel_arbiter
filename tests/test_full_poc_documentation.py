from pathlib import Path

from sentinel_workbench.safety import scan_forbidden_content


ROOT = Path(__file__).resolve().parents[1]
STATUS_DOC = ROOT / "docs" / "18_deterministic_poc_status.md"


def test_status_document_separates_implemented_deferred_and_pre_real_use_requirements():
    text = STATUS_DOC.read_text(encoding="utf-8")

    required_headings = [
        "## Implemented Deterministic POC",
        "## Deferred",
        "## Required Before Real Clinical, Prospective, Or Production Use",
        "## Not Claimed",
        "## Local Verification",
    ]
    for heading in required_headings:
        assert heading in text

    required_terms = [
        "static role outputs",
        "static EvidenceFlow outputs",
        "optional LLM prompt mode",
        "OpenEvidence",
        "live evidence",
        "prospective deployment",
        "production signing",
        "clinical safety validation",
        "regulatory compliance",
        "data/workbench/index.html",
    ]
    for term in required_terms:
        assert term in text

    assert scan_forbidden_content(text, allow_safety_rule_lists=False) == []
