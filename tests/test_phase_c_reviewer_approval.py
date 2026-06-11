import json
from pathlib import Path
import subprocess
import sys
import tomllib

import pytest

from sentinel_workbench.approval import approve_prepared_input, load_approved_episode, validate_approved_input
from sentinel_workbench.constructed_intake import prepare_constructed_input


def _prepared_input(tmp_path: Path) -> Path:
    source = tmp_path / "constructed_input.txt"
    source.write_text(
        "\n".join(
            [
                "Adult constructed patient reports a recurrent symptom concern.",
                "Initial information is documented as not decisive.",
                "Response to supportive therapy is unclear.",
                "Return access and home support remain uncertain.",
            ]
        ),
        encoding="utf-8",
    )
    artifacts = prepare_constructed_input(
        input_path=source,
        out_dir=tmp_path / "prepared",
        episode_id="constructed_approval_case",
        title="Constructed approval case",
    )
    assert artifacts.draft_episode_path is not None
    return artifacts.out_dir


def test_load_approved_episode_rejects_unapproved_draft(tmp_path):
    prepared_dir = _prepared_input(tmp_path)

    with pytest.raises(ValueError, match="approved episode artifact required"):
        load_approved_episode(prepared_dir / "draft_episode.json")


def test_approve_prepared_input_writes_manifest_trace_and_loadable_episode(tmp_path):
    prepared_dir = _prepared_input(tmp_path)

    approval = approve_prepared_input(
        prepared_dir=prepared_dir,
        reviewer_id="reviewer_alpha",
        approval_note="Structured draft reviewed for demo use.",
    )

    assert approval.approved_episode_path.exists()
    assert approval.approval_manifest_path.exists()
    assert approval.approval_trace_path.exists()

    manifest = json.loads(approval.approval_manifest_path.read_text(encoding="utf-8"))
    assert manifest["approval_status"] == "approved"
    assert manifest["reviewer_id"] == "reviewer_alpha"
    assert manifest["episode_changed_from_draft"] is False
    assert manifest["approved_episode_sha256"]
    assert manifest["raw_input_sha256"]

    episode = load_approved_episode(prepared_dir)
    assert episode.episode_id == "constructed_approval_case"

    trace = json.loads(approval.approval_trace_path.read_text(encoding="utf-8"))
    event_types = [event["event_type"] for event in trace["events"]]
    assert event_types == ["draft_prepared", "reviewer_approved"]
    assert trace["events"][0]["prev_hash"] is None
    assert trace["events"][1]["prev_hash"] == trace["events"][0]["event_hash"]


def test_approve_prepared_input_records_reviewer_edits(tmp_path):
    prepared_dir = _prepared_input(tmp_path)
    edited_episode = tmp_path / "edited_episode.json"
    payload = json.loads((prepared_dir / "draft_episode.json").read_text(encoding="utf-8"))
    payload["title"] = "Constructed approval case with reviewer edit"
    edited_episode.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    approval = approve_prepared_input(
        prepared_dir=prepared_dir,
        reviewer_id="reviewer_beta",
        approval_note="Title edited after review.",
        approved_episode_source=edited_episode,
    )

    manifest = json.loads(approval.approval_manifest_path.read_text(encoding="utf-8"))
    assert manifest["episode_changed_from_draft"] is True
    assert manifest["approved_episode_sha256"] != manifest["draft_episode_sha256"]
    assert load_approved_episode(prepared_dir).title == "Constructed approval case with reviewer edit"


def test_validate_approved_input_refuses_missing_manifest(tmp_path):
    prepared_dir = _prepared_input(tmp_path)

    with pytest.raises(ValueError, match="approval_manifest.json"):
        validate_approved_input(prepared_dir)


def test_approval_module_command_writes_and_validates_artifacts(tmp_path):
    prepared_dir = _prepared_input(tmp_path)
    env = {"PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")}

    approve_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "sentinel_workbench.approval",
            "--prepared-dir",
            str(prepared_dir),
            "--reviewer-id",
            "reviewer_cli",
            "--approval-note",
            "CLI approval for constructed demo.",
        ],
        check=False,
        cwd=Path(__file__).resolve().parents[1],
        env=env,
        capture_output=True,
        text=True,
    )

    assert approve_result.returncode == 0
    assert "status=approved" in approve_result.stdout

    validate_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "sentinel_workbench.approval",
            "--validate-approved",
            str(prepared_dir),
        ],
        check=False,
        cwd=Path(__file__).resolve().parents[1],
        env=env,
        capture_output=True,
        text=True,
    )

    assert validate_result.returncode == 0
    assert "approved_episode=constructed_approval_case" in validate_result.stdout


def test_schema_export_includes_approval_schemas(tmp_path):
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
    manifest_schema = json.loads((tmp_path / "approval_manifest.schema.json").read_text(encoding="utf-8"))
    trace_schema = json.loads((tmp_path / "approval_trace.schema.json").read_text(encoding="utf-8"))
    assert manifest_schema["properties"]["approval_status"]["const"] == "approved"
    assert "events" in trace_schema["properties"]


def test_pyproject_exposes_approval_console_script():
    pyproject = tomllib.loads((Path(__file__).resolve().parents[1] / "pyproject.toml").read_text(encoding="utf-8"))

    assert (
        pyproject["project"]["scripts"]["sentinel-workbench-approve-constructed-input"]
        == "sentinel_workbench.approval:main"
    )
