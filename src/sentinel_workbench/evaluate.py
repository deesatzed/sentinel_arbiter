from __future__ import annotations

import argparse
import json
from pathlib import Path

from pydantic import Field

from .graph import compute_prudence_graph
from .loader import load_case_library
from .models import RequiredTimepoint, StrictModel
from .node_audit import summarize_node_audit_completeness
from .replay import build_replay_view
from .safety import scan_forbidden_content
from .static_inputs import load_static_input_bundle, validate_static_inputs


class EvaluationReport(StrictModel):
    valid_case_count: int
    future_leakage_failures: int
    forbidden_phrase_violations: int
    expected_posture_agreement: dict[str, int]
    lane_coverage: dict[str, int]
    receipt_completeness: str
    automated_validation: dict[str, dict[str, object]] = Field(default_factory=dict)
    case_results: list[dict[str, object]] = Field(default_factory=list)


def receipt_completeness_payload(episodes: list, receipt_dir: str | Path) -> dict[str, object]:
    base = Path(receipt_dir)
    json_dir = base / "json"
    markdown_dir = base / "markdown"
    expected_ids = {f"receipt_{episode.episode_id}_T3_deterministic" for episode in episodes}
    json_ids = {path.stem for path in json_dir.glob("*.json")} if json_dir.exists() else set()
    markdown_ids = {path.stem for path in markdown_dir.glob("*.md")} if markdown_dir.exists() else set()
    return {
        "complete": expected_ids.issubset(json_ids) and expected_ids.issubset(markdown_ids),
        "expected_receipts": len(expected_ids),
        "json_receipts": len(expected_ids & json_ids),
        "markdown_receipts": len(expected_ids & markdown_ids),
        "missing_json": sorted(expected_ids - json_ids),
        "missing_markdown": sorted(expected_ids - markdown_ids),
    }


def expected_flag_matched(expected: str, detected: list[str], category: str) -> bool:
    if expected in detected:
        return True
    if category == "therapy_response_integration":
        if expected == "therapy_nonresponse_relevance":
            return any(
                token in finding
                for finding in detected
                for token in ("no_clear_change", "worse", "not_reassessed", "unknown")
            )
        if expected == "therapy_response_observed":
            return any("documented_improvement" in finding for finding in detected)
        if expected == "plausibly_indicated_therapy_not_considered":
            return any("not_considered" in finding for finding in detected)
    return False


def summarize_expected_matches(items: list[tuple[str, list[str], list[str]]], category: str) -> dict[str, object]:
    expected = 0
    matched = 0
    missing: list[str] = []
    for episode_id, expected_items, detected_items in items:
        for expected_item in expected_items:
            expected += 1
            if expected_flag_matched(expected_item, detected_items, category):
                matched += 1
            else:
                missing.append(f"{episode_id}:{expected_item}")
    return {
        "expected": expected,
        "matched": matched,
        "missing": missing,
    }


def generate_evaluation_report(
    case_dir: str | Path,
    output_path: str | Path,
    *,
    receipt_dir: str | Path = "data/receipts",
) -> EvaluationReport:
    case_path = Path(case_dir)
    episodes = load_case_library(case_path)
    case_results: list[dict[str, object]] = []
    future_leakage_failures = 0
    posture_agreements = 0
    commission_lane_cases = 0
    omission_lane_cases = 0
    therapy_response_lane_cases = 0
    omission_detection_items: list[tuple[str, list[str], list[str]]] = []
    commission_detection_items: list[tuple[str, list[str], list[str]]] = []
    therapy_detection_items: list[tuple[str, list[str], list[str]]] = []
    next_best_items: list[tuple[str, list[str], list[str]]] = []

    for episode in episodes:
        graph = compute_prudence_graph(episode, RequiredTimepoint.T3_DISPOSITION_DECISION)
        t4_fact_ids = {
            fact.fact_id
            for state in episode.timepoints
            if state.timepoint_id == RequiredTimepoint.T4_FOLLOW_UP_OR_OUTCOME
            for fact in state.available_facts
        }
        leaked_timepoints: list[str] = []
        for timepoint in (
            RequiredTimepoint.T0_TRIAGE,
            RequiredTimepoint.T1_INITIAL_WORKUP,
            RequiredTimepoint.T2_POST_TREATMENT_REASSESSMENT,
            RequiredTimepoint.T3_DISPOSITION_DECISION,
        ):
            replay = build_replay_view(episode, timepoint)
            replay_fact_ids = {fact.fact_id for fact in replay.available_facts}
            if not t4_fact_ids.isdisjoint(replay_fact_ids):
                leaked_timepoints.append(timepoint.value)
        if leaked_timepoints:
            future_leakage_failures += 1

        expected_match = graph.final_posture == episode.expected_outputs.expected_final_posture
        posture_agreements += int(expected_match)
        commission_lane_cases += int(graph.commission_lane.risk_score > 0)
        omission_lane_cases += int(graph.omission_lane.risk_score > 0)
        therapy_response_lane_cases += int(graph.therapy_response_lane.relevance_score > 0)
        omission_detection_items.append(
            (
                episode.episode_id,
                episode.expected_outputs.expected_omission_flags,
                graph.omission_lane.findings,
            )
        )
        commission_detection_items.append(
            (
                episode.episode_id,
                episode.expected_outputs.expected_commission_flags,
                graph.commission_lane.findings,
            )
        )
        therapy_detection_items.append(
            (
                episode.episode_id,
                episode.expected_outputs.expected_therapy_response_flags,
                graph.therapy_response_lane.findings,
            )
        )
        next_best_items.append(
            (
                episode.episode_id,
                episode.expected_outputs.expected_next_best_information,
                graph.next_best_information_ranking,
            )
        )

        case_results.append(
            {
                "episode_id": episode.episode_id,
                "timepoint_id": graph.timepoint_id.value,
                "final_posture": graph.final_posture.value,
                "expected_final_posture": episode.expected_outputs.expected_final_posture.value,
                "expected_posture_match": expected_match,
                "node_values": graph.node_values,
                "commission_lane": graph.commission_lane.model_dump(),
                "omission_lane": graph.omission_lane.model_dump(),
                "therapy_response_lane": graph.therapy_response_lane.model_dump(),
                "next_best_information_ranking": graph.next_best_information_ranking,
                "leaked_timepoints": leaked_timepoints,
            }
        )

    findings = scan_forbidden_content(
        [fixture.read_text(encoding="utf-8") for fixture in sorted(case_path.glob("*.json")) if not fixture.name.startswith("invalid_")],
        allow_safety_rule_lists=False,
    )
    static_path = Path("data/static_inputs/static_inputs.json")
    static_payload: dict[str, object]
    if static_path.exists():
        static_bundle = load_static_input_bundle(static_path)
        static_summary = validate_static_inputs(static_bundle, episodes)
        static_payload = {
            "role_template_count": len(static_bundle.role_assessment_templates),
            "evidenceflow_template_count": len(static_bundle.evidenceflow_templates),
            "errors": static_summary.errors,
        }
    else:
        static_payload = {
            "role_template_count": 0,
            "evidenceflow_template_count": 0,
            "errors": ["static_input_bundle_missing"],
        }
    automated_validation = {
        "omission_detection": summarize_expected_matches(omission_detection_items, "omission_detection"),
        "commission_warning_detection": summarize_expected_matches(
            commission_detection_items,
            "commission_warning_detection",
        ),
        "therapy_response_integration": summarize_expected_matches(
            therapy_detection_items,
            "therapy_response_integration",
        ),
        "next_best_information_usefulness": summarize_expected_matches(
            next_best_items,
            "next_best_information_usefulness",
        ),
    }
    report = EvaluationReport(
        valid_case_count=len(episodes),
        future_leakage_failures=future_leakage_failures,
        forbidden_phrase_violations=len(findings),
        expected_posture_agreement={"matched": posture_agreements, "total": len(episodes)},
        lane_coverage={
            "commission_lane_cases": commission_lane_cases,
            "omission_lane_cases": omission_lane_cases,
            "therapy_response_lane_cases": therapy_response_lane_cases,
        },
        receipt_completeness="implemented",
        automated_validation=automated_validation,
        case_results=case_results,
    )

    payload = {
        "valid_case_count": report.valid_case_count,
        "schema_validity": {"valid_cases": report.valid_case_count, "invalid_cases_skipped": True},
        "future_leakage_failures": report.future_leakage_failures,
        "forbidden_phrase_violations": report.forbidden_phrase_violations,
        "expected_posture_agreement": report.expected_posture_agreement,
        "lane_coverage": report.lane_coverage,
        "automated_validation": report.automated_validation,
        "static_input_validation": static_payload,
        "node_audit_completeness": summarize_node_audit_completeness(episodes),
        "receipt_completeness": receipt_completeness_payload(episodes, receipt_dir),
        "case_results": report.case_results,
    }
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Sentinel Workbench deterministic evaluation report.")
    parser.add_argument("--case-dir", default="data/cases")
    parser.add_argument("--out", default="validation/reports/latest.json")
    parser.add_argument("--receipt-dir", default="data/receipts")
    args = parser.parse_args()
    report = generate_evaluation_report(args.case_dir, args.out, receipt_dir=args.receipt_dir)
    print(f"cases={report.valid_case_count} future_leakage_failures={report.future_leakage_failures} out={args.out}")


if __name__ == "__main__":
    main()
