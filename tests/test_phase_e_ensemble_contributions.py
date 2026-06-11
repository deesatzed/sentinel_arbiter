import json
from pathlib import Path
import subprocess
import sys

from sentinel_workbench.ensemble import build_ensemble_contribution_bundle, summarize_ensemble_contribution_completeness
from sentinel_workbench.graph import REQUIRED_GRAPH_METRICS
from sentinel_workbench.loader import load_case_library, load_episode
from sentinel_workbench.node_audit import build_node_audit_bundle
from sentinel_workbench.static_inputs import load_static_input_bundle


ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = ROOT / "data" / "cases"
STATIC_INPUTS = ROOT / "data" / "static_inputs" / "static_inputs.json"


def test_ensemble_contributions_map_only_to_graph_nodes_and_have_dispositions():
    episode = load_episode(CASE_DIR / "valid_material_gap_case.json")
    bundle = load_static_input_bundle(STATIC_INPUTS)

    ensemble = build_ensemble_contribution_bundle(episode, bundle)

    assert ensemble.contributions
    assert ensemble.rejected_inputs
    for contribution in ensemble.contributions:
        assert contribution.node_id in REQUIRED_GRAPH_METRICS
        assert contribution.contributor_role
        assert contribution.disposition in {"accepted", "rejected", "downgraded"}
        assert contribution.disposition_reason
        assert contribution.proposed_range_min <= contribution.proposed_value <= contribution.proposed_range_max


def test_ensemble_contributions_include_downgraded_low_confidence_static_inputs():
    episode = load_episode(CASE_DIR / "valid_material_gap_case.json")
    bundle = load_static_input_bundle(STATIC_INPUTS)

    ensemble = build_ensemble_contribution_bundle(episode, bundle)

    assert any(contribution.disposition == "downgraded" for contribution in ensemble.contributions)
    assert any("confidence" in contribution.disposition_reason.lower() for contribution in ensemble.contributions)


def test_unsupported_static_targets_are_rejected_with_reason():
    episode = load_episode(CASE_DIR / "valid_material_gap_case.json")
    bundle = load_static_input_bundle(STATIC_INPUTS)

    ensemble = build_ensemble_contribution_bundle(episode, bundle)

    assert any(item["disposition"] == "rejected" for item in ensemble.rejected_inputs)
    assert any(item["source_target"] == "prudent_layperson_threshold" for item in ensemble.rejected_inputs)
    assert all(item["disposition_reason"] for item in ensemble.rejected_inputs)


def test_node_audits_include_ensemble_contributions_when_static_bundle_supplied():
    episode = load_episode(CASE_DIR / "valid_material_gap_case.json")
    static_bundle = load_static_input_bundle(STATIC_INPUTS)

    audit_bundle = build_node_audit_bundle(episode, static_bundle=static_bundle)

    contributions = [
        contribution
        for audit in audit_bundle.node_audits
        for contribution in audit.ensemble_contributions
    ]
    assert contributions
    assert all(contribution.node_id in REQUIRED_GRAPH_METRICS for contribution in contributions)
    assert any(contribution.node_id == "information_clock" for contribution in contributions)


def test_ensemble_contribution_completeness_passes_for_case_library():
    episodes = load_case_library(CASE_DIR)
    static_bundle = load_static_input_bundle(STATIC_INPUTS)

    summary = summarize_ensemble_contribution_completeness(episodes, static_bundle)

    assert summary["complete"] is True
    assert summary["case_count"] == 7
    assert summary["contribution_count"] > 0
    assert summary["missing_dispositions"] == []
    assert summary["invalid_node_targets"] == []
    assert summary["rejected_input_count"] > 0


def test_evaluation_report_includes_ensemble_contribution_completeness(tmp_path):
    env = {"PYTHONPATH": str(ROOT / "src")}
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
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["ensemble_contribution_completeness"]["complete"] is True
    assert report["ensemble_contribution_completeness"]["case_count"] == 7


def test_schema_export_includes_ensemble_contribution_schema(tmp_path):
    env = {"PYTHONPATH": str(ROOT / "src")}

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "sentinel_workbench.schema_export",
            str(tmp_path / "ed.schema.json"),
        ],
        check=False,
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    schema = json.loads((tmp_path / "ensemble_contribution.schema.json").read_text(encoding="utf-8"))
    assert "EnsembleContributionBundle" in json.dumps(schema)
    assert "rejected_inputs" in json.dumps(schema)
