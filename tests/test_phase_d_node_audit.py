import json
from pathlib import Path
import subprocess
import sys

from sentinel_workbench.graph import REQUIRED_GRAPH_METRICS, compute_prudence_graph
from sentinel_workbench.loader import load_episode, load_case_library
from sentinel_workbench.node_audit import build_node_audit_bundle, summarize_node_audit_completeness


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "data" / "cases"


def test_node_audit_bundle_covers_every_graph_metric_with_methodology_fields():
    episode = load_episode(FIXTURE_DIR / "valid_material_gap_case.json")
    graph = compute_prudence_graph(episode)

    bundle = build_node_audit_bundle(episode)
    audits_by_id = {audit.node_id: audit for audit in bundle.node_audits}

    assert set(audits_by_id) == set(REQUIRED_GRAPH_METRICS)
    for node_id in REQUIRED_GRAPH_METRICS:
        audit = audits_by_id[node_id]
        assert audit.definition.id == node_id
        assert audit.definition.version
        assert audit.definition.dependent_inputs
        assert audit.dependencies == audit.definition.dependent_inputs
        assert audit.estimate.node_id == node_id
        assert audit.estimate.value == graph.node_values[node_id]
        assert audit.estimate.range_min <= audit.estimate.median <= audit.estimate.range_max
        assert audit.estimate.method
        assert audit.estimate.distribution_kind
        assert 0 <= audit.estimate.confidence <= 1
        assert audit.sensitivity_note


def test_node_audit_evidence_refs_resolve_to_evidence_items():
    episode = load_episode(FIXTURE_DIR / "valid_material_gap_case.json")

    bundle = build_node_audit_bundle(episode)

    for audit in bundle.node_audits:
        evidence_ids = {item.ref_id for item in audit.evidence}
        assert set(audit.estimate.evidence_refs).issubset(evidence_ids), audit.node_id
        for evidence in audit.evidence:
            assert evidence.node_id == audit.node_id
            assert evidence.source_timepoint != "T4_follow_up_or_outcome"
            assert evidence.quoted_or_structured_fact
            assert 0 <= evidence.weight <= 1
            assert evidence.quality in {"strong", "moderate", "weak", "unknown"}


def test_weak_ai_evidence_is_limited_and_not_treated_as_strong():
    episode = load_episode(FIXTURE_DIR / "valid_ai_weak_fact_case.json")

    bundle = build_node_audit_bundle(episode)
    audit = next(item for item in bundle.node_audits if item.node_id == "ai_provenance_risk")

    assert audit.estimate.value > 0
    assert audit.evidence
    assert any(evidence.quality == "weak" for evidence in audit.evidence)
    assert all(evidence.quality != "strong" for evidence in audit.evidence)
    assert any("unverified" in limitation.lower() for evidence in audit.evidence for limitation in evidence.limitations)


def test_node_audit_completeness_summary_passes_for_case_library():
    episodes = load_case_library(FIXTURE_DIR)

    summary = summarize_node_audit_completeness(episodes)

    assert summary["complete"] is True
    assert summary["case_count"] == 7
    assert summary["expected_nodes_per_case"] == len(REQUIRED_GRAPH_METRICS)
    assert summary["missing"] == []


def test_schema_export_includes_node_audit_schema(tmp_path):
    env = {"PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")}

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "sentinel_workbench.schema_export",
            str(tmp_path / "ed.schema.json"),
        ],
        check=False,
        cwd=Path(__file__).resolve().parents[1],
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    schema_path = tmp_path / "node_audit.schema.json"
    assert schema_path.exists()
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert "NodeAudit" in json.dumps(schema)
    assert "NodeEstimate" in json.dumps(schema)


def test_evaluation_report_includes_node_audit_completeness(tmp_path):
    env = {"PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")}
    output = tmp_path / "report.json"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "sentinel_workbench.evaluate",
            "--case-dir",
            "data/cases",
            "--out",
            str(output),
            "--receipt-dir",
            "data/receipts",
        ],
        check=False,
        cwd=Path(__file__).resolve().parents[1],
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["node_audit_completeness"]["complete"] is True
    assert report["node_audit_completeness"]["expected_nodes_per_case"] == len(REQUIRED_GRAPH_METRICS)
