from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from typing import Any, Literal
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from pydantic import Field, model_validator

from .approval import approve_prepared_input, load_approved_episode
from .constructed_intake import prepare_constructed_input
from .graph import REQUIRED_GRAPH_METRICS, compute_prudence_graph
from .models import DecisionEpisode, StrictModel
from .node_audit import NODE_DEFINITIONS, build_node_audit_bundle
from .safety import scan_forbidden_content


OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_TIMEOUT_SECONDS = 90
DEFAULT_MAX_TOKENS = 3000


class OpenRouterSettings(StrictModel):
    api_key: str
    models: list[str] = Field(min_length=1)

    def safe_summary(self) -> str:
        names = ", ".join(f"MODEL_{index + 1}" for index, _ in enumerate(self.models))
        return f"OpenRouter settings loaded: {len(self.models)} model(s) from {names}; API key present."


class ModelNodeAssessment(StrictModel):
    node_id: str
    proposed_value: float = Field(ge=0, le=5)
    proposed_range_min: float = Field(ge=0, le=5)
    proposed_range_max: float = Field(ge=0, le=5)
    confidence: float = Field(ge=0, le=1)
    rationale: str
    evidence_refs: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_node_and_range(self) -> "ModelNodeAssessment":
        if self.node_id not in REQUIRED_GRAPH_METRICS:
            raise ValueError(f"unknown node_id: {self.node_id}")
        if not self.proposed_range_min <= self.proposed_value <= self.proposed_range_max:
            raise ValueError("proposed_value must fall inside proposed range")
        if self.node_id != "next_best_information_rank" and self.proposed_range_max > 1:
            raise ValueError("0_to_1 node range cannot exceed 1")
        return self


class ParsedModelPayload(StrictModel):
    summary: str
    node_assessments: list[ModelNodeAssessment] = Field(default_factory=list)
    uncertainty_drivers: list[str] = Field(default_factory=list)
    evidence_gaps: list[str] = Field(default_factory=list)


class ModelRunResult(StrictModel):
    model: str
    status: Literal["success", "schema_invalid", "safety_invalid", "request_failed"]
    latency_seconds: float
    summary: str = ""
    node_assessments: list[ModelNodeAssessment] = Field(default_factory=list)
    raw_response_path: Path | None = None
    errors: list[str] = Field(default_factory=list)


def load_openrouter_settings(env_path: str | Path = ".env") -> OpenRouterSettings:
    env = _load_env_file(env_path)
    api_key = env.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is required in .env")
    numbered: list[tuple[int, str]] = []
    for key, value in env.items():
        match = re.fullmatch(r"MODEL_(\d+)", key)
        if match and value.strip():
            numbered.append((int(match.group(1)), value.strip()))
    models = [value for _, value in sorted(numbered)]
    if not models:
        raise ValueError("at least one MODEL_N value is required in .env")
    return OpenRouterSettings(api_key=api_key, models=models)


def openrouter_comparison_status(env_path: str | Path = ".env") -> dict[str, object]:
    try:
        settings = load_openrouter_settings(env_path)
    except Exception:
        return {
            "available": False,
            "status": "skipped_missing_credentials",
            "message": "OpenRouter comparison skipped because local credentials or MODEL_N settings are not available.",
            "comparison_only": True,
        }
    return {
        "available": True,
        "status": "configured",
        "message": settings.safe_summary(),
        "model_count": len(settings.models),
        "comparison_only": True,
    }


def build_model_prompt(
    *,
    episode: DecisionEpisode,
    redacted_input: str,
    review_question: str,
) -> list[dict[str, str]]:
    audit_bundle = build_node_audit_bundle(episode)
    deterministic = compute_prudence_graph(episode)
    node_context = []
    for audit in audit_bundle.node_audits:
        definition = NODE_DEFINITIONS[audit.node_id]
        node_context.append(
            {
                "node_id": audit.node_id,
                "question": definition.question,
                "scale": definition.output_scale,
                "deterministic_value": deterministic.node_values[audit.node_id],
                "deterministic_range": [audit.estimate.range_min, audit.estimate.range_max],
                "dependencies": audit.dependencies,
                "evidence_refs": [evidence.ref_id for evidence in audit.evidence],
            }
        )
    user_payload = {
        "review_question": review_question,
        "allowed_node_ids": list(REQUIRED_GRAPH_METRICS),
        "redacted_constructed_input": redacted_input,
        "structured_episode_compact": _compact_episode_context(episode),
        "deterministic_node_context": node_context,
        "required_json_shape": {
            "summary": "one or two sentences, governance review support only",
            "uncertainty_drivers": ["short driver"],
            "evidence_gaps": ["short gap"],
            "node_assessments": [
                {
                    "node_id": "one allowed node id",
                    "proposed_value": "number; 0-1 except next_best_information_rank may be 0-5",
                    "proposed_range_min": "number",
                    "proposed_range_max": "number",
                    "confidence": "number 0-1",
                    "rationale": "short explanation",
                    "evidence_refs": ["known evidence ref if available"],
                    "limitations": ["short limitation"],
                }
            ],
        },
    }
    return [
        {
            "role": "system",
            "content": (
                "You are a Sentinel governance-review model comparison worker. "
                "You assess information sufficiency and provenance for a constructed ED review example. "
                "This is not a clinical action recommendation. Do not tell a clinician what action to take. "
                "Return only JSON. Use only the allowed node IDs. Do not invent facts."
            ),
        },
        {
            "role": "user",
            "content": json.dumps(user_payload, indent=2),
        },
    ]


def run_model_comparison(
    *,
    input_path: str | Path,
    out_dir: str | Path,
    review_question: str,
    env_path: str | Path = ".env",
    title: str = "OpenRouter challenging constructed comparison",
    episode_id: str = "openrouter_challenging_constructed_case",
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Path]:
    settings = load_openrouter_settings(env_path)
    out = Path(out_dir)
    prepared_dir = out / "prepared_input"
    artifacts = prepare_constructed_input(
        input_path=input_path,
        out_dir=prepared_dir,
        episode_id=episode_id,
        title=title,
    )
    if artifacts.quarantined or artifacts.draft_episode_path is None:
        raise ValueError("constructed input was quarantined and cannot be sent to model comparison")
    approve_prepared_input(
        prepared_dir=prepared_dir,
        reviewer_id="model_compare_local",
        approval_note="Approved constructed input for bounded OpenRouter model comparison.",
    )
    episode = load_approved_episode(prepared_dir)
    redacted_input = artifacts.redacted_input_path.read_text(encoding="utf-8")
    messages = build_model_prompt(
        episode=episode,
        redacted_input=redacted_input,
        review_question=review_question,
    )
    results: list[ModelRunResult] = []
    raw_dir = out / "raw_model_responses"
    raw_dir.mkdir(parents=True, exist_ok=True)
    for index, model in enumerate(settings.models, start=1):
        raw_path = raw_dir / f"model_{index:02d}.json"
        results.append(
            call_openrouter_model(
                settings=settings,
                model=model,
                messages=messages,
                raw_response_path=raw_path,
                timeout_seconds=timeout_seconds,
            )
        )
    return write_comparison_report(
        out_dir=out,
        settings=settings,
        episode=episode,
        review_question=review_question,
        results=results,
    )


def call_openrouter_model(
    *,
    settings: OpenRouterSettings,
    model: str,
    messages: list[dict[str, str]],
    raw_response_path: Path,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> ModelRunResult:
    started = time.monotonic()
    body = {
        "model": model,
        "messages": messages,
        "temperature": 0,
        "max_tokens": DEFAULT_MAX_TOKENS,
        "response_format": {"type": "json_object"},
    }
    request = Request(
        OPENROUTER_CHAT_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {settings.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/deesatzed/sentinel_arbiter",
            "X-Title": "Sentinel Arbiter Local Model Comparison",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            raw_payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        return ModelRunResult(
            model=model,
            status="request_failed",
            latency_seconds=round(time.monotonic() - started, 3),
            errors=[f"http_{exc.code}:{_safe_error_body(exc)}"],
        )
    except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return ModelRunResult(
            model=model,
            status="request_failed",
            latency_seconds=round(time.monotonic() - started, 3),
            errors=[type(exc).__name__],
        )

    raw_response_path.write_text(json.dumps(raw_payload, indent=2) + "\n", encoding="utf-8")
    try:
        choice = raw_payload["choices"][0]
        content = choice["message"].get("content")
        if not isinstance(content, str) or not content.strip():
            finish_reason = choice.get("finish_reason", "unknown")
            raise ValueError(f"model returned no JSON content; finish_reason={finish_reason}")
        parsed = ParsedModelPayload.model_validate(extract_json_object(content))
    except Exception as exc:
        return ModelRunResult(
            model=model,
            status="schema_invalid",
            latency_seconds=round(time.monotonic() - started, 3),
            raw_response_path=raw_response_path,
            errors=[str(exc)],
        )

    safety_findings = scan_forbidden_content(parsed.model_dump(mode="json"), allow_safety_rule_lists=False)
    if safety_findings:
        return ModelRunResult(
            model=model,
            status="safety_invalid",
            latency_seconds=round(time.monotonic() - started, 3),
            summary="",
            node_assessments=[],
            raw_response_path=raw_response_path,
            errors=[f"{finding.category}:{finding.value}" for finding in safety_findings],
        )

    return ModelRunResult(
        model=model,
        status="success",
        latency_seconds=round(time.monotonic() - started, 3),
        summary=parsed.summary,
        node_assessments=parsed.node_assessments,
        raw_response_path=raw_response_path,
        errors=[],
    )


def extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?", "", stripped, flags=re.IGNORECASE).strip()
        stripped = re.sub(r"```$", "", stripped).strip()
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(stripped[start : end + 1])


def compare_model_result(episode: DecisionEpisode, result: ModelRunResult) -> dict[str, Any]:
    deterministic = compute_prudence_graph(episode).node_values
    node_deltas: list[dict[str, Any]] = []
    for assessment in result.node_assessments:
        baseline = float(deterministic[assessment.node_id])
        delta = round(float(assessment.proposed_value) - baseline, 4)
        node_deltas.append(
            {
                "node_id": assessment.node_id,
                "deterministic_value": baseline,
                "model_value": assessment.proposed_value,
                "abs_delta": abs(delta),
                "signed_delta": delta,
                "confidence": assessment.confidence,
                "rationale": assessment.rationale,
                "limitations": assessment.limitations,
            }
        )
    node_deltas.sort(key=lambda item: item["abs_delta"], reverse=True)
    max_delta = max((item["abs_delta"] for item in node_deltas), default=0.0)
    if result.status != "success":
        status = result.status
    elif not result.node_assessments:
        status = "insufficient_structured_output"
    elif max_delta <= 0.2 and len(result.node_assessments) >= 3:
        status = "strong_candidate"
    elif result.node_assessments:
        status = "candidate"
    else:
        status = "weak_candidate"
    return {
        "model": result.model,
        "status": status,
        "raw_status": result.status,
        "latency_seconds": result.latency_seconds,
        "summary": result.summary if result.status == "success" else "",
        "node_count": len(result.node_assessments),
        "max_abs_delta": max_delta,
        "node_deltas": node_deltas,
        "errors": result.errors,
    }


def write_comparison_report(
    *,
    out_dir: str | Path,
    settings: OpenRouterSettings,
    episode: DecisionEpisode,
    review_question: str,
    results: list[ModelRunResult],
) -> dict[str, Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    comparisons = [compare_model_result(episode, result) for result in results]
    payload = {
        "report_type": "openrouter_model_comparison",
        "episode_id": episode.episode_id,
        "review_question": review_question,
        "settings": {
            "model_count": len(settings.models),
            "models": settings.models,
        },
        "deterministic_graph": compute_prudence_graph(episode).model_dump(mode="json"),
        "results": [result.model_dump(mode="json") for result in results],
        "comparisons": comparisons,
    }
    json_path = out / "comparison_report.json"
    markdown_path = out / "comparison_report.md"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(_render_markdown_report(payload), encoding="utf-8")
    return {"json": json_path, "markdown": markdown_path}


def _render_markdown_report(payload: dict[str, Any]) -> str:
    lines = [
        "# OpenRouter Model Comparison",
        "",
        f"Episode: `{payload['episode_id']}`",
        f"Review question: `{payload['review_question']}`",
        "",
        "Deterministic Sentinel remains the authority. Model outputs are comparison evidence only.",
        "",
        "## Model Summary",
        "",
        "| Model | Status | Nodes | Max Delta | Latency | Errors |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for item in payload["comparisons"]:
        errors = "; ".join(item["errors"]) if item["errors"] else ""
        lines.append(
            f"| `{item['model']}` | {item['status']} | {item['node_count']} | "
            f"{item['max_abs_delta']} | {item['latency_seconds']}s | {_markdown_cell(errors)} |"
        )
    lines.extend(["", "## Candidate Interpretation", ""])
    strong = [item for item in payload["comparisons"] if item["status"] == "strong_candidate"]
    candidates = [item for item in payload["comparisons"] if item["status"] == "candidate"]
    failed = [item for item in payload["comparisons"] if item["raw_status"] != "success"]
    if strong:
        lines.append(f"Strong candidates: {', '.join('`' + item['model'] + '`' for item in strong)}.")
    if candidates:
        lines.append(f"Usable candidates needing review: {', '.join('`' + item['model'] + '`' for item in candidates)}.")
    if failed:
        lines.append(f"Failed or invalid outputs: {', '.join('`' + item['model'] + '`' for item in failed)}.")
    if not strong and not candidates:
        lines.append("No configured model produced enough validated structured node output to treat as a sufficient candidate.")
    lines.extend(["", "## Largest Node Deltas", ""])
    for item in payload["comparisons"]:
        lines.append(f"### `{item['model']}`")
        if item["raw_status"] != "success":
            lines.append(f"- Status: {item['raw_status']}")
            continue
        if item["summary"]:
            lines.append(f"- Summary: {_markdown_cell(item['summary'])}")
        for delta in item["node_deltas"][:5]:
            lines.append(
                f"- `{delta['node_id']}`: deterministic={delta['deterministic_value']}, "
                f"model={delta['model_value']}, abs_delta={delta['abs_delta']}, confidence={delta['confidence']}"
            )
    return "\n".join(lines) + "\n"


def _markdown_cell(value: str) -> str:
    return value.replace("\n", " ").replace("|", "\\|")


def _load_env_file(path: str | Path) -> dict[str, str]:
    env: dict[str, str] = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        value = value.strip().strip('"').strip("'")
        env[key.strip()] = value
    return env


def _compact_episode_context(episode: DecisionEpisode) -> dict[str, Any]:
    timepoints = []
    for state in episode.timepoints:
        timepoints.append(
            {
                "timepoint_id": state.timepoint_id,
                "facts": [
                    {
                        "fact_id": fact.fact_id,
                        "text": fact.text,
                        "source_type": fact.source_type,
                        "verification_status": fact.verification_status,
                        "decision_criticality": fact.decision_criticality,
                    }
                    for fact in state.available_facts
                ],
                "information_gaps": [
                    {
                        "gap_id": gap.gap_id,
                        "description": gap.description,
                        "gap_type": gap.gap_type,
                        "time_to_obtain_hours": gap.time_to_obtain_hours,
                        "burden": gap.burden,
                        "decision_relevance_prior": gap.decision_relevance_prior,
                        "candidate_input_mapping": gap.candidate_input_mapping,
                    }
                    for gap in state.information_gaps
                ],
                "therapy_response": [
                    {
                        "therapy_id": therapy.therapy_id,
                        "response_observed": therapy.response_observed,
                        "response_reliability": therapy.response_reliability,
                        "not_considered": therapy.therapy_plausibly_indicated_but_not_considered,
                    }
                    for therapy in state.offered_therapies
                ],
                "follow_up_feasibility": state.follow_up_feasibility.model_dump(mode="json"),
            }
        )
    return {
        "episode_id": episode.episode_id,
        "title": episode.title,
        "governance_question": episode.governance_question,
        "timepoints": timepoints,
    }


def _safe_error_body(exc: HTTPError) -> str:
    try:
        body = exc.read().decode("utf-8")
    except Exception:
        return ""
    return body[:300].replace("\n", " ")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare OpenRouter models on a bounded Sentinel constructed case.")
    parser.add_argument("--input", required=True, help="Constructed redacted text input path.")
    parser.add_argument("--out", required=True, help="Output directory for local comparison artifacts.")
    parser.add_argument("--review-question", default="disposition_information_sufficiency")
    parser.add_argument("--env", default=".env")
    parser.add_argument("--episode-id", default="openrouter_challenging_constructed_case")
    parser.add_argument("--title", default="OpenRouter challenging constructed comparison")
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    args = parser.parse_args()
    paths = run_model_comparison(
        input_path=args.input,
        out_dir=args.out,
        review_question=args.review_question,
        env_path=args.env,
        episode_id=args.episode_id,
        title=args.title,
        timeout_seconds=args.timeout_seconds,
    )
    print(f"comparison_json={paths['json']} comparison_markdown={paths['markdown']}")


if __name__ == "__main__":
    main()
