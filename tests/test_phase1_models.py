import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
from pydantic import ValidationError

from sentinel_workbench.loader import load_episode
from sentinel_workbench.models import DecisionEpisode, RequiredTimepoint
from sentinel_workbench.replay import build_replay_view
from sentinel_workbench.safety import scan_forbidden_content


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "data" / "cases"


def test_valid_ed_episode_fixture_loads_with_required_timepoints():
    episode = load_episode(FIXTURE_DIR / "valid_material_gap_case.json")

    assert episode.domain == "emergency_department_disposition_replay"
    assert [state.timepoint_id for state in episode.timepoints] == [
        RequiredTimepoint.T0_TRIAGE,
        RequiredTimepoint.T1_INITIAL_WORKUP,
        RequiredTimepoint.T2_POST_TREATMENT_REASSESSMENT,
        RequiredTimepoint.T3_DISPOSITION_DECISION,
        RequiredTimepoint.T4_FOLLOW_UP_OR_OUTCOME,
    ]
    assert episode.expected_outputs.expected_future_leakage_blocked is True


def test_invalid_episode_missing_required_timepoint_fails_clearly():
    with pytest.raises(ValidationError, match="missing required timepoints"):
        load_episode(FIXTURE_DIR / "invalid_missing_timepoint_case.json")


def test_replay_view_blocks_future_facts_from_current_timepoint():
    episode = load_episode(FIXTURE_DIR / "valid_material_gap_case.json")

    replay = build_replay_view(episode, RequiredTimepoint.T3_DISPOSITION_DECISION)

    available_fact_ids = {fact.fact_id for fact in replay.available_facts}
    assert "future_outcome_fact_001" not in available_fact_ids
    assert "future_outcome_fact_001" in replay.blocked_future_fact_ids
    assert replay.timepoint_id == RequiredTimepoint.T3_DISPOSITION_DECISION


def test_safety_scan_rejects_forbidden_disposition_language():
    findings = scan_forbidden_content(
        {"note": "The test output says this patient should discharge."},
        allow_safety_rule_lists=False,
    )

    assert findings
    assert findings[0].category == "forbidden_disposition_phrase"


def test_safety_scan_rejects_named_institution_in_fixture_text():
    findings = scan_forbidden_content(
        {"note": "Synthetic example from Massachusetts General Hospital."},
        allow_safety_rule_lists=False,
    )

    assert findings
    assert findings[0].category == "named_institution"


def test_exported_json_schema_contains_ed_disposition_fields():
    schema = DecisionEpisode.model_json_schema()

    assert schema["properties"]["domain"]["const"] == "emergency_department_disposition_replay"
    assert "decision_point_type" in schema["properties"]
    assert "case_syntheticity" in schema["properties"]
    timeline_defs = json.dumps(schema["$defs"])
    assert "offered_therapies" in timeline_defs
    assert "therapy_response_observations" in timeline_defs


def test_module_commands_export_schema_and_validate_cases(tmp_path):
    env = os.environ.copy()
    src_path = Path(__file__).resolve().parents[1] / "src"
    env["PYTHONPATH"] = str(src_path)

    export_result = subprocess.run(
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

    assert export_result.returncode == 0
    assert (tmp_path / "ed.schema.json").exists()
    assert (tmp_path / "static_input_bundle.schema.json").exists()

    validate_result = subprocess.run(
        [sys.executable, "-m", "sentinel_workbench.validate", "data/cases"],
        check=False,
        cwd=Path(__file__).resolve().parents[1],
        env=env,
        capture_output=True,
        text=True,
    )

    assert validate_result.returncode == 0
    assert "validated=7 errors=0" in validate_result.stdout
