import json
from pathlib import Path
import subprocess
import sys
import tomllib

import pytest

from sentinel_workbench.constructed_intake import prepare_constructed_input
from sentinel_workbench.loader import load_episode
from sentinel_workbench.models import RequiredTimepoint
from sentinel_workbench.redaction import DeterministicRedactor


def test_deterministic_redactor_replaces_phi_like_spans():
    text = "Synthetic adult with MRN ABCD1234, DOB: 01/02/1970, phone 555-123-4567, email test@example.com."

    result = DeterministicRedactor().redact(text)

    assert "MRN ABCD1234" not in result.clean_text
    assert "01/02/1970" not in result.clean_text
    assert "555-123-4567" not in result.clean_text
    assert "test@example.com" not in result.clean_text
    assert "[REDACTED_MRN]" in result.clean_text
    assert {finding.label for finding in result.findings} >= {"MRN", "DOB", "PHONE", "EMAIL"}
    assert result.residual_findings == []


def test_prepare_constructed_input_blocks_residual_phi_when_detected(tmp_path):
    source = tmp_path / "unsafe_input.txt"
    source.write_text("Synthetic adult with SSN 123-45-6789 and MRN ABCD1234.", encoding="utf-8")

    with pytest.raises(ValueError, match="residual phi risk"):
        prepare_constructed_input(
            input_path=source,
            out_dir=tmp_path / "out",
            episode_id="constructed_blocked_case",
            title="Constructed blocked case",
            quarantine_on_residual=False,
        )


def test_prepare_constructed_input_can_quarantine_residual_phi(tmp_path):
    source = tmp_path / "unsafe_input.txt"
    source.write_text("Synthetic adult with SSN 123-45-6789 and MRN ABCD1234.", encoding="utf-8")

    artifacts = prepare_constructed_input(
        input_path=source,
        out_dir=tmp_path / "out",
        episode_id="constructed_quarantined_case",
        title="Constructed quarantined case",
        quarantine_on_residual=True,
    )

    assert artifacts.draft_episode_path is None
    assert artifacts.quarantined is True
    report = json.loads(artifacts.redaction_report_path.read_text(encoding="utf-8"))
    assert report["status"] == "quarantined"
    assert any(finding["label"] == "SSN" for finding in report["residual_findings"])


def test_prepare_constructed_input_writes_valid_draft_episode(tmp_path):
    source = tmp_path / "constructed_input.txt"
    source.write_text(
        "\n".join(
            [
                "Adult constructed patient reports recurrent symptom concern after initial evaluation.",
                "Initial workup is documented as not decisive in this constructed demo.",
                "Supportive therapy was offered and response is not clearly reassessed.",
                "At decision time, home support and return access remain unclear.",
            ]
        ),
        encoding="utf-8",
    )

    artifacts = prepare_constructed_input(
        input_path=source,
        out_dir=tmp_path / "out",
        episode_id="constructed_demo_case",
        title="Constructed demo case",
    )

    assert artifacts.quarantined is False
    assert artifacts.draft_episode_path is not None
    assert artifacts.redacted_input_path.exists()
    assert artifacts.redaction_report_path.exists()

    episode = load_episode(artifacts.draft_episode_path)
    assert episode.episode_id == "constructed_demo_case"
    assert episode.case_syntheticity == "deidentified_style_synthetic"
    assert [state.timepoint_id for state in episode.timepoints] == [
        RequiredTimepoint.T0_TRIAGE,
        RequiredTimepoint.T1_INITIAL_WORKUP,
        RequiredTimepoint.T2_POST_TREATMENT_REASSESSMENT,
        RequiredTimepoint.T3_DISPOSITION_DECISION,
        RequiredTimepoint.T4_FOLLOW_UP_OR_OUTCOME,
    ]
    assert episode.timepoints[0].available_facts[0].source_refs == ["redacted_constructed_input"]
    assert episode.expected_outputs.expected_future_leakage_blocked is True


def test_constructed_intake_module_command_writes_artifacts(tmp_path):
    source = tmp_path / "constructed_input.txt"
    source.write_text("Adult constructed patient has unclear support at the decision-time review.", encoding="utf-8")
    env = {"PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")}

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "sentinel_workbench.constructed_intake",
            "--input",
            str(source),
            "--out",
            str(tmp_path / "prepared"),
            "--episode-id",
            "constructed_cli_case",
            "--title",
            "Constructed CLI case",
        ],
        check=False,
        cwd=Path(__file__).resolve().parents[1],
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "status=prepared" in result.stdout
    assert (tmp_path / "prepared" / "draft_episode.json").exists()
    assert (tmp_path / "prepared" / "redaction_report.json").exists()


def test_schema_export_includes_redaction_report_schema(tmp_path):
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
    schema_path = tmp_path / "redaction_report.schema.json"
    assert schema_path.exists()
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert schema["properties"]["status"]["enum"] == ["prepared", "quarantined"]
    assert "residual_findings" in schema["properties"]


def test_pyproject_exposes_constructed_intake_console_script():
    pyproject = tomllib.loads((Path(__file__).resolve().parents[1] / "pyproject.toml").read_text(encoding="utf-8"))

    assert (
        pyproject["project"]["scripts"]["sentinel-workbench-prepare-constructed-input"]
        == "sentinel_workbench.constructed_intake:main"
    )
