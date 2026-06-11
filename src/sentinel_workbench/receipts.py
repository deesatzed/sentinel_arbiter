from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from pydantic import Field

from .ensemble import EnsembleContributionBundle, build_ensemble_contribution_bundle
from .graph import PrudenceGraphResult, compute_prudence_graph
from .loader import load_case_library
from .models import DecisionEpisode, RequiredTimepoint, StrictModel
from .node_audit import NodeAuditBundle, build_node_audit_bundle
from .static_inputs import load_static_input_bundle


REQUIRED_RECEIPT_FIELDS: tuple[str, ...] = (
    "receipt_id",
    "episode_id",
    "timepoint_id",
    "run_id",
    "mode",
    "input_hashes",
    "prompt_or_dotflow_versions",
    "model_versions",
    "evidence_versions",
    "graph_version",
    "node_library_version",
    "available_fact_ids",
    "blocked_future_fact_ids",
    "node_values",
    "rejected_or_downgraded_findings",
    "role_disagreement_map",
    "commission_lane",
    "omission_lane",
    "therapy_response_lane",
    "next_best_information_ranking",
    "preventability_opportunity_score",
    "preventability_opportunity_explanation",
    "final_posture",
    "decision_weight",
    "signature_placeholder",
    "selected_review_question",
    "clinician_summary",
    "human_summary_sections",
    "node_audit_bundle",
    "ensemble_contribution_bundle",
    "methodology_summary",
    "deeper_dive_artifacts",
    "workflow_artifacts",
)


class SentinelReceipt(StrictModel):
    receipt_id: str
    episode_id: str
    timepoint_id: str
    run_id: str
    mode: str
    input_hashes: dict[str, str]
    prompt_or_dotflow_versions: dict[str, str]
    model_versions: dict[str, str] = Field(default_factory=dict)
    evidence_versions: dict[str, str] = Field(default_factory=dict)
    graph_version: str
    node_library_version: str
    available_fact_ids: list[str]
    blocked_future_fact_ids: list[str]
    node_values: dict[str, float | int]
    rejected_or_downgraded_findings: list[str]
    role_disagreement_map: dict[str, object]
    commission_lane: dict[str, object]
    omission_lane: dict[str, object]
    therapy_response_lane: dict[str, object]
    next_best_information_ranking: list[str]
    preventability_opportunity_score: float
    preventability_opportunity_explanation: str
    final_posture: str
    decision_weight: float
    signature_placeholder: str
    selected_review_question: str | None = None
    clinician_summary: str
    human_summary_sections: dict[str, list[str]]
    node_audit_bundle: NodeAuditBundle
    ensemble_contribution_bundle: EnsembleContributionBundle
    methodology_summary: dict[str, object]
    deeper_dive_artifacts: list[str]
    workflow_artifacts: dict[str, object] = Field(default_factory=dict)


def sha256_file(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def stable_hash_payload(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def fact_ids_at_t3(episode: DecisionEpisode) -> list[str]:
    facts: list[str] = []
    for state in episode.timepoints:
        if state.sequence_index <= 3 and state.timepoint_id != RequiredTimepoint.T4_FOLLOW_UP_OR_OUTCOME:
            facts.extend(fact.fact_id for fact in state.available_facts)
    return sorted(set(facts))


def blocked_future_fact_ids(episode: DecisionEpisode) -> list[str]:
    ids: set[str] = set()
    for state in episode.timepoints:
        if state.timepoint_id == RequiredTimepoint.T4_FOLLOW_UP_OR_OUTCOME or state.sequence_index > 3:
            ids.update(fact.fact_id for fact in state.available_facts)
        ids.update(fact.fact_id for fact in state.hidden_future_facts)
    return sorted(ids)


def build_human_sections(episode: DecisionEpisode, graph: PrudenceGraphResult) -> dict[str, list[str]]:
    t3 = next(state for state in episode.timepoints if state.timepoint_id == RequiredTimepoint.T3_DISPOSITION_DECISION)
    known = [fact.text for fact in t3.available_facts] or ["No current-time facts were available in this synthetic fixture."]
    missing = [gap.description for gap in t3.information_gaps] or ["No material missing inputs were represented at this timepoint."]
    would_change = graph.next_best_information_ranking or ["No next-best-information item was ranked above the materiality threshold."]
    commission = graph.commission_lane.findings or ["No commission-lane concern was raised by the deterministic graph."]
    omission = graph.omission_lane.findings or ["No omission-lane concern was raised by the deterministic graph."]
    therapy = graph.therapy_response_lane.findings or ["No therapy-response concern was raised by the deterministic graph."]
    return {
        "what_was_known": known,
        "what_was_missing": missing,
        "what_would_have_changed_the_discussion": would_change,
        "what_hospital_based_monitoring_or_treatment_might_add": [
            "The receipt records whether a hospital-based path had a specific monitoring, information, or therapy-response target in the current-time facts."
        ],
        "what_non_inpatient_alternatives_might_add": [
            "The receipt records whether support, follow-up access, return access, and recheck feasibility were represented in the current-time facts."
        ],
        "commission_concerns": commission,
        "omission_concerns": omission,
        "therapy_response_concerns": therapy,
        "why_the_graph_selected_the_posture": [
            f"The graph selected {graph.final_posture.value} from bounded node values, with decision weight {graph.node_values['decision_weight']} and preventability opportunity {graph.node_values['preventability_opportunity_score']}."
        ],
    }


def preventability_explanation(graph: PrudenceGraphResult) -> str:
    return (
        "Preventability opportunity is a proxy derived from material gap strength, decision weight, "
        "information clock, and burden modifiers. It is not a claim of clinical harm prevention."
    )


def review_question_display(review_question: str | None) -> str:
    labels = {
        "disposition_information_sufficiency": "Disposition information sufficiency",
        "ai_response_use_sufficiency": "AI response use sufficiency",
    }
    return labels.get(review_question or "", "Unspecified governance review question")


def build_clinician_summary(
    *,
    human_sections: dict[str, list[str]],
    graph: PrudenceGraphResult,
    review_question: str | None,
) -> str:
    missing = human_sections.get("what_was_missing", [])
    would_change = human_sections.get("what_would_have_changed_the_discussion", [])
    main_gap = missing[0] if missing else "The current-time record has unresolved information gaps."
    next_input = would_change[0] if would_change else "No next-best information item was ranked above the materiality threshold."
    question_text = review_question_display(review_question)
    return (
        f"For {question_text}, Sentinel found information sufficiency {graph.node_values['information_sufficiency']} "
        f"with material gap strength {graph.node_values['material_gap_strength']} and decision weight "
        f"{graph.node_values['decision_weight']}. The main driver is: {main_gap} "
        f"The most useful next review input is: {next_input} "
        "This output is governance review support, not a clinical action recommendation."
    )


def build_receipt(
    episode: DecisionEpisode,
    static_inputs_path: str | Path,
    *,
    graph_version: str = "deterministic_graph_v0.1",
    node_library_version: str = "ed_node_library_v0.1",
    workflow_artifacts: dict[str, object] | None = None,
) -> SentinelReceipt:
    graph = compute_prudence_graph(episode, RequiredTimepoint.T3_DISPOSITION_DECISION)
    static_bundle = load_static_input_bundle(static_inputs_path)
    node_audit_bundle = build_node_audit_bundle(
        episode,
        RequiredTimepoint.T3_DISPOSITION_DECISION,
        static_bundle=static_bundle,
    )
    ensemble_contribution_bundle = build_ensemble_contribution_bundle(
        episode,
        static_bundle,
        RequiredTimepoint.T3_DISPOSITION_DECISION,
    )
    prompt_versions = {
        template.role_name: static_bundle.version for template in static_bundle.role_assessment_templates
    }
    prompt_versions.update({template.flow_type: template.evidence_version for template in static_bundle.evidenceflow_templates})

    rejected_or_downgraded = []
    if graph.node_values["ai_provenance_risk"] > 0:
        rejected_or_downgraded.append("unverified_ai_derived_fact_downgraded")
    if graph.node_values["material_gap_strength"] > 0:
        rejected_or_downgraded.append("unsupported_gap_assertions_require_current_time_source")
    if blocked_future_fact_ids(episode):
        rejected_or_downgraded.append("hidden_future_facts_blocked")

    role_disagreement_map = {
        "static_role_count": len(static_bundle.role_assessment_templates),
        "graph_posture_source": "deterministic_graph",
        "notes": [
            "Static role templates are structured inputs only.",
            "The graph computes final posture.",
        ],
    }

    payload_hash = stable_hash_payload(episode.model_dump(mode="json"))
    input_hashes = {
        "episode_sha256": payload_hash,
        "static_inputs_sha256": sha256_file(static_inputs_path),
    }
    if workflow_artifacts:
        raw_input_sha256 = workflow_artifacts.get("raw_input_sha256")
        if isinstance(raw_input_sha256, str) and raw_input_sha256:
            input_hashes["raw_input_sha256"] = raw_input_sha256
    selected_review_question = None
    if workflow_artifacts and isinstance(workflow_artifacts.get("selected_review_question"), str):
        selected_review_question = str(workflow_artifacts["selected_review_question"])
    human_sections = build_human_sections(episode, graph)
    receipt_id = f"receipt_{episode.episode_id}_T3_deterministic"
    return SentinelReceipt(
        receipt_id=receipt_id,
        episode_id=episode.episode_id,
        timepoint_id=RequiredTimepoint.T3_DISPOSITION_DECISION.value,
        run_id=f"run_{episode.episode_id}_deterministic_v0_1",
        mode="replay",
        input_hashes=input_hashes,
        prompt_or_dotflow_versions=prompt_versions,
        model_versions={},
        evidence_versions={
            template.flow_type: template.evidence_version for template in static_bundle.evidenceflow_templates
        },
        graph_version=graph_version,
        node_library_version=node_library_version,
        available_fact_ids=fact_ids_at_t3(episode),
        blocked_future_fact_ids=blocked_future_fact_ids(episode),
        node_values=graph.node_values,
        rejected_or_downgraded_findings=sorted(set(rejected_or_downgraded)),
        role_disagreement_map=role_disagreement_map,
        commission_lane=graph.commission_lane.model_dump(),
        omission_lane=graph.omission_lane.model_dump(),
        therapy_response_lane=graph.therapy_response_lane.model_dump(),
        next_best_information_ranking=graph.next_best_information_ranking,
        preventability_opportunity_score=graph.node_values["preventability_opportunity_score"],
        preventability_opportunity_explanation=preventability_explanation(graph),
        final_posture=graph.final_posture.value,
        decision_weight=graph.node_values["decision_weight"],
        signature_placeholder="UNSIGNED_DETERMINISTIC_POC",
        selected_review_question=selected_review_question,
        clinician_summary=build_clinician_summary(
            human_sections=human_sections,
            graph=graph,
            review_question=selected_review_question,
        ),
        human_summary_sections=human_sections,
        node_audit_bundle=node_audit_bundle,
        ensemble_contribution_bundle=ensemble_contribution_bundle,
        methodology_summary={
            "node_audit_complete": len(node_audit_bundle.node_audits) == len(graph.node_values),
            "ensemble_contributions_visible": bool(ensemble_contribution_bundle.contributions),
            "rejected_ensemble_inputs_visible": bool(ensemble_contribution_bundle.rejected_inputs),
            "final_posture_source": "deterministic_graph_node_values",
            "trust_boundary": (
                "Static role and EvidenceFlow inputs are normalized as bounded contributions; "
                "they do not decide final posture."
            ),
        },
        deeper_dive_artifacts=[
            "human_summary_sections",
            "node_audit_bundle",
            "ensemble_contribution_bundle",
            "methodology_summary",
            "workflow_artifacts",
        ],
        workflow_artifacts=workflow_artifacts or {},
    )


def render_receipt_markdown(receipt: SentinelReceipt) -> str:
    title = f"# Sentinel Receipt - {receipt.episode_id}\n\n"
    header = (
        f"- Receipt ID: `{receipt.receipt_id}`\n"
        f"- Timepoint: `{receipt.timepoint_id}`\n"
        f"- Final posture: `{receipt.final_posture}`\n"
        f"- Decision weight: `{receipt.decision_weight}`\n"
        f"- Selected Review Question: `{review_question_display(receipt.selected_review_question)}`\n"
        f"- Signature placeholder: `{receipt.signature_placeholder}`\n\n"
    )
    section_titles = {
        "what_was_known": "What Was Known",
        "what_was_missing": "What Was Missing",
        "what_would_have_changed_the_discussion": "What Would Have Changed The Discussion",
        "what_hospital_based_monitoring_or_treatment_might_add": "What Hospital-Based Monitoring Or Treatment Might Add",
        "what_non_inpatient_alternatives_might_add": "What Non-Inpatient Alternatives Might Add",
        "commission_concerns": "Commission Concerns",
        "omission_concerns": "Omission Concerns",
        "therapy_response_concerns": "Therapy-Response Concerns",
        "why_the_graph_selected_the_posture": "Why The Graph Selected The Posture",
    }
    body: list[str] = []
    body.append("## Clinician Summary\n")
    body.append(f"{receipt.clinician_summary}\n\n")
    for key, title_text in section_titles.items():
        body.append(f"## {title_text}\n")
        for item in receipt.human_summary_sections[key]:
            body.append(f"- {item}\n")
        body.append("\n")
    body.append("## Node Audit Methodology\n")
    for audit in receipt.node_audit_bundle.node_audits:
        estimate = audit.estimate
        evidence_refs = ", ".join(estimate.evidence_refs) or "No direct evidence refs"
        dependencies = ", ".join(audit.dependencies)
        body.append(
            f"- `{audit.node_id}`: value `{estimate.value}`; Range `{estimate.range_min}` to "
            f"`{estimate.range_max}`; Median `{estimate.median}`; Distribution "
            f"`{estimate.distribution_kind}`; Method `{estimate.method}`; Dependent inputs "
            f"`{dependencies}`; Evidence refs `{evidence_refs}`; Sensitivity `{audit.sensitivity_note}`\n"
        )
    body.append("\n")
    body.append("## Ensemble Contributions\n")
    for contribution in receipt.ensemble_contribution_bundle.contributions:
        evidence_refs = ", ".join(contribution.evidence_refs) or "No direct evidence refs"
        body.append(
            f"- `{contribution.contributor_role}` to `{contribution.node_id}`: proposed "
            f"`{contribution.proposed_value}`; Range `{contribution.proposed_range_min}` to "
            f"`{contribution.proposed_range_max}`; disposition `{contribution.disposition}`; "
            f"reason `{contribution.disposition_reason}`; Evidence refs `{evidence_refs}`\n"
        )
    if receipt.ensemble_contribution_bundle.rejected_inputs:
        body.append("\nRejected ensemble inputs:\n")
        for rejected in receipt.ensemble_contribution_bundle.rejected_inputs:
            body.append(
                f"- `{rejected['contributor_role']}` target `{rejected['source_target']}`: "
                f"{rejected['disposition_reason']}\n"
            )
    body.append("\n")
    body.append("## Deeper Dive Artifacts\n")
    for artifact in receipt.deeper_dive_artifacts:
        body.append(f"- `{artifact}`\n")
    body.append("\n")
    return (title + header + "".join(body)).rstrip() + "\n"


def write_receipt(receipt: SentinelReceipt, output_dir: str | Path) -> dict[str, Path]:
    base = Path(output_dir)
    json_dir = base / "json"
    markdown_dir = base / "markdown"
    json_dir.mkdir(parents=True, exist_ok=True)
    markdown_dir.mkdir(parents=True, exist_ok=True)
    json_path = json_dir / f"{receipt.receipt_id}.json"
    markdown_path = markdown_dir / f"{receipt.receipt_id}.md"
    json_path.write_text(json.dumps(receipt.model_dump(mode="json"), indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_receipt_markdown(receipt), encoding="utf-8")
    return {"json_path": json_path, "markdown_path": markdown_path}


def generate_receipts_for_case_library(
    case_dir: str | Path,
    static_inputs_path: str | Path,
    output_dir: str | Path,
) -> list[dict[str, Path]]:
    outputs: list[dict[str, Path]] = []
    for episode in load_case_library(case_dir):
        receipt = build_receipt(episode, static_inputs_path)
        outputs.append(write_receipt(receipt, output_dir))
    return outputs


def export_receipt_schema(output_path: str | Path = "schemas/ed_sentinel_receipt.schema.json") -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(SentinelReceipt.model_json_schema(), indent=2) + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic Sentinel Workbench receipts.")
    parser.add_argument("--case-dir", default="data/cases")
    parser.add_argument("--static-inputs", default="data/static_inputs/static_inputs.json")
    parser.add_argument("--out", default="data/receipts")
    args = parser.parse_args()
    outputs = generate_receipts_for_case_library(args.case_dir, args.static_inputs, args.out)
    print(f"receipts={len(outputs)} out={args.out}")


if __name__ == "__main__":
    main()
