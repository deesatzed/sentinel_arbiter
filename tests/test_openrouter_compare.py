import json
from pathlib import Path
import tomllib

import pytest

from sentinel_workbench.graph import REQUIRED_GRAPH_METRICS
from sentinel_workbench.loader import load_episode
from sentinel_workbench.openrouter_compare import (
    ModelNodeAssessment,
    ModelRunResult,
    OpenRouterSettings,
    build_model_prompt,
    compare_model_result,
    extract_json_object,
    load_openrouter_settings,
    write_comparison_report,
)


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "data" / "cases" / "valid_ai_weak_fact_case.json"


def test_load_openrouter_settings_reads_numbered_models_without_printing_secret(tmp_path):
    env_path = tmp_path / ".env"
    env_path.write_text(
        "\n".join(
            [
                "OPENROUTER_API_KEY=sk-or-test-secret",
                "MODEL_1=openai/gpt-4.1-mini",
                "MODEL_3=anthropic/claude-sonnet-4",
                "UNRELATED=value",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    settings = load_openrouter_settings(env_path)

    assert settings.api_key == "sk-or-test-secret"
    assert settings.models == ["openai/gpt-4.1-mini", "anthropic/claude-sonnet-4"]
    assert "sk-or-test-secret" not in settings.safe_summary()
    assert "MODEL_1" in settings.safe_summary()


def test_extract_json_object_accepts_fenced_or_plain_json():
    payload = {"summary": "ok", "node_assessments": []}

    assert extract_json_object(json.dumps(payload)) == payload
    assert extract_json_object("```json\n" + json.dumps(payload) + "\n```") == payload


def test_model_node_assessment_rejects_unknown_node_and_bad_range():
    with pytest.raises(ValueError):
        ModelNodeAssessment(
            node_id="unknown_node",
            proposed_value=0.2,
            proposed_range_min=0.0,
            proposed_range_max=0.4,
            confidence=0.5,
            rationale="rationale",
            evidence_refs=[],
            limitations=[],
        )

    with pytest.raises(ValueError):
        ModelNodeAssessment(
            node_id=REQUIRED_GRAPH_METRICS[0],
            proposed_value=0.9,
            proposed_range_min=0.0,
            proposed_range_max=0.4,
            confidence=0.5,
            rationale="rationale",
            evidence_refs=[],
            limitations=[],
        )


def test_build_model_prompt_names_review_question_allowed_nodes_and_governance_boundary():
    episode = load_episode(CASE)

    prompt = build_model_prompt(
        episode=episode,
        redacted_input="Constructed redacted input with unclear reassessment and weak AI-derived claim.",
        review_question="disposition_information_sufficiency",
    )

    prompt_text = "\n".join(message["content"] for message in prompt)
    assert "disposition_information_sufficiency" in prompt_text
    assert "material_gap_strength" in prompt_text
    assert "Return only JSON" in prompt_text
    assert "not a clinical action recommendation" in prompt_text


def test_compare_model_result_flags_node_deltas_and_summary_status():
    episode = load_episode(CASE)
    model_result = ModelRunResult(
        model="test/model",
        status="success",
        latency_seconds=1.2,
        summary="The information base is limited by weak provenance and missing reassessment.",
        node_assessments=[
            ModelNodeAssessment(
                node_id="ai_provenance_risk",
                proposed_value=0.95,
                proposed_range_min=0.8,
                proposed_range_max=1.0,
                confidence=0.7,
                rationale="AI-derived claim appears material and unverified.",
                evidence_refs=["F1"],
                limitations=["Constructed case only."],
            )
        ],
        raw_response_path=None,
        errors=[],
    )

    comparison = compare_model_result(episode, model_result)

    assert comparison["model"] == "test/model"
    assert comparison["status"] == "candidate"
    assert comparison["max_abs_delta"] >= 0
    assert comparison["node_deltas"][0]["node_id"] == "ai_provenance_risk"


def test_write_comparison_report_creates_json_and_markdown(tmp_path):
    settings = OpenRouterSettings(api_key="secret", models=["test/model-a", "test/model-b"])
    results = [
        ModelRunResult(
            model="test/model-a",
            status="success",
            latency_seconds=1.0,
            summary="Structured response passed.",
            node_assessments=[],
            raw_response_path=tmp_path / "raw_a.json",
            errors=[],
        ),
        ModelRunResult(
            model="test/model-b",
            status="request_failed",
            latency_seconds=0.2,
            summary="",
            node_assessments=[],
            raw_response_path=None,
            errors=["timeout"],
        ),
    ]
    episode = load_episode(CASE)

    paths = write_comparison_report(
        out_dir=tmp_path,
        settings=settings,
        episode=episode,
        review_question="disposition_information_sufficiency",
        results=results,
    )

    payload = json.loads(paths["json"].read_text(encoding="utf-8"))
    markdown = paths["markdown"].read_text(encoding="utf-8")
    assert payload["settings"]["model_count"] == 2
    assert payload["results"][0]["model"] == "test/model-a"
    assert "test/model-a" in markdown
    assert "request_failed" in markdown
    assert "secret" not in markdown


def test_pyproject_exposes_openrouter_compare_console_script():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert (
        pyproject["project"]["scripts"]["sentinel-workbench-openrouter-compare"]
        == "sentinel_workbench.openrouter_compare:main"
    )
