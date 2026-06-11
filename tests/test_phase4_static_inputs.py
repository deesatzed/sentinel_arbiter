from pathlib import Path

import pytest

from sentinel_workbench.loader import load_case_library
from sentinel_workbench.static_inputs import (
    REQUIRED_FLOW_TYPES,
    REQUIRED_ROLE_NAMES,
    load_static_input_bundle,
    validate_static_inputs,
)


ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = ROOT / "data" / "cases"
STATIC_DIR = ROOT / "data" / "static_inputs"


def test_static_role_and_evidenceflow_templates_expand_for_every_case():
    episodes = load_case_library(CASE_DIR)
    bundle = load_static_input_bundle(STATIC_DIR / "static_inputs.json")
    summary = validate_static_inputs(bundle, episodes)

    assert summary.valid_case_count == 7
    assert summary.errors == []
    assert summary.role_outputs_by_case
    assert summary.evidenceflow_outputs_by_case
    for episode in episodes:
        assert summary.role_outputs_by_case[episode.episode_id] == set(REQUIRED_ROLE_NAMES)
        assert summary.evidenceflow_outputs_by_case[episode.episode_id] == set(REQUIRED_FLOW_TYPES)


def test_static_role_outputs_reject_forbidden_final_disposition_language():
    episodes = load_case_library(CASE_DIR)
    bundle = load_static_input_bundle(STATIC_DIR / "invalid_final_verdict_role.json")

    summary = validate_static_inputs(bundle, episodes)

    assert summary.errors
    assert any("forbidden_disposition_phrase" in error for error in summary.errors)


def test_static_role_outputs_reject_unknown_node_targets():
    episodes = load_case_library(CASE_DIR)
    bundle = load_static_input_bundle(STATIC_DIR / "invalid_unknown_node_target.json")

    summary = validate_static_inputs(bundle, episodes)

    assert summary.errors
    assert any("unknown_node_target" in error for error in summary.errors)
