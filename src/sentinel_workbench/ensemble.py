from __future__ import annotations

import json
from pathlib import Path

from pydantic import Field

from .graph import REQUIRED_GRAPH_METRICS, compute_prudence_graph
from .models import DecisionEpisode, RequiredTimepoint, StrictModel
from .node_audit import EnsembleContribution
from .static_inputs import EvidenceFlowTemplate, RoleAssessmentTemplate, StaticFinding, StaticInputBundle


class RejectedEnsembleInput(StrictModel):
    contributor_role: str
    source_target: str
    source_id: str
    disposition: str
    disposition_reason: str


class EnsembleContributionBundle(StrictModel):
    episode_id: str
    timepoint_id: RequiredTimepoint
    contribution_version: str
    contributions: list[EnsembleContribution] = Field(default_factory=list)
    rejected_inputs: list[dict[str, object]] = Field(default_factory=list)


CONTRIBUTION_VERSION = "static_ensemble_normalizer_v0.1"
GRAPH_NODE_TARGETS = frozenset(REQUIRED_GRAPH_METRICS)


ROLE_TARGET_VALUE_KEYS: dict[str, tuple[str, ...]] = {
    "information_sufficiency": ("information_sufficiency_estimate",),
    "harm_clock": ("severity_if_wrong",),
    "information_clock": ("decision_relevance_probability", "expected_posture_shift"),
    "recoverability": ("recoverability",),
    "future_correction_opportunity": ("future_correction_opportunity",),
    "decision_weight": ("expected_posture_shift", "severity_if_wrong"),
}


def build_ensemble_contribution_bundle(
    episode: DecisionEpisode,
    static_bundle: StaticInputBundle,
    timepoint_id: RequiredTimepoint | str = RequiredTimepoint.T3_DISPOSITION_DECISION,
) -> EnsembleContributionBundle:
    target_timepoint = RequiredTimepoint(timepoint_id)
    graph = compute_prudence_graph(episode, target_timepoint)
    contributions: list[EnsembleContribution] = []
    rejected_inputs: list[dict[str, object]] = []

    for role_template in static_bundle.role_assessment_templates:
        for finding in role_template.findings:
            for target in finding.node_targets:
                if target not in GRAPH_NODE_TARGETS:
                    rejected_inputs.append(
                        RejectedEnsembleInput(
                            contributor_role=role_template.role_name,
                            source_target=target,
                            source_id=finding.finding_id_template.format(episode_id=episode.episode_id),
                            disposition="rejected",
                            disposition_reason="Target is not a deterministic graph node for Phase E normalization.",
                        ).model_dump()
                    )
                    continue
                contributions.append(_role_contribution(episode, graph.node_values[target], role_template, finding, target))

    for flow_template in static_bundle.evidenceflow_templates:
        contributions.extend(_evidenceflow_contributions(episode, graph.node_values, flow_template))

    return EnsembleContributionBundle(
        episode_id=episode.episode_id,
        timepoint_id=target_timepoint,
        contribution_version=CONTRIBUTION_VERSION,
        contributions=contributions,
        rejected_inputs=rejected_inputs,
    )


def summarize_ensemble_contribution_completeness(
    episodes: list[DecisionEpisode],
    static_bundle: StaticInputBundle,
) -> dict[str, object]:
    missing_dispositions: list[str] = []
    invalid_node_targets: list[str] = []
    contribution_count = 0
    rejected_input_count = 0
    for episode in episodes:
        bundle = build_ensemble_contribution_bundle(episode, static_bundle)
        contribution_count += len(bundle.contributions)
        rejected_input_count += len(bundle.rejected_inputs)
        for contribution in bundle.contributions:
            if contribution.node_id not in GRAPH_NODE_TARGETS:
                invalid_node_targets.append(f"{episode.episode_id}:{contribution.node_id}")
            if not contribution.disposition or not contribution.disposition_reason:
                missing_dispositions.append(f"{episode.episode_id}:{contribution.node_id}:{contribution.contributor_role}")
    return {
        "complete": contribution_count > 0 and not missing_dispositions and not invalid_node_targets,
        "case_count": len(episodes),
        "contribution_count": contribution_count,
        "rejected_input_count": rejected_input_count,
        "missing_dispositions": missing_dispositions,
        "invalid_node_targets": invalid_node_targets,
    }


def export_ensemble_contribution_schema(output_path: str | Path = "schemas/ensemble_contribution.schema.json") -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(EnsembleContributionBundle.model_json_schema(), indent=2) + "\n", encoding="utf-8")
    return path


def _role_contribution(
    episode: DecisionEpisode,
    graph_value: float | int,
    template: RoleAssessmentTemplate,
    finding: StaticFinding,
    target: str,
) -> EnsembleContribution:
    proposed = _proposed_value_from_finding(finding, target, fallback=float(graph_value))
    disposition = "accepted" if finding.confidence >= 0.65 else "downgraded"
    reason = (
        f"Accepted static role contribution at confidence {finding.confidence}."
        if disposition == "accepted"
        else f"Downgraded static role contribution because confidence {finding.confidence} is below acceptance threshold."
    )
    return EnsembleContribution(
        node_id=target,
        contributor_role=template.role_name,
        proposed_value=proposed,
        proposed_range_min=max(0.0, round(proposed - _range_margin(finding.confidence), 4)),
        proposed_range_max=min(1.0, round(proposed + _range_margin(finding.confidence), 4)),
        evidence_refs=[ref.format(episode_id=episode.episode_id) for ref in finding.source_refs],
        rationale=finding.rationale_short,
        disposition=disposition,
        disposition_reason=reason,
    )


def _evidenceflow_contributions(
    episode: DecisionEpisode,
    node_values: dict[str, float | int],
    template: EvidenceFlowTemplate,
) -> list[EnsembleContribution]:
    contributions: list[EnsembleContribution] = []
    if template.flow_type == "next_best_input":
        for candidate in template.outputs.candidate_inputs:
            proposed = candidate.expected_posture_shift
            contributions.append(
                EnsembleContribution(
                    node_id="next_best_information_rank",
                    contributor_role=f"evidenceflow:{template.flow_type}",
                    proposed_value=max(1, int(round(node_values["next_best_information_rank"]))),
                    proposed_range_min=0,
                    proposed_range_max=max(1, int(round(node_values["next_best_information_rank"])) + 1),
                    evidence_refs=[candidate.input_id_template.format(episode_id=episode.episode_id)],
                    rationale=candidate.description,
                    disposition="accepted" if template.confidence >= 0.65 else "downgraded",
                    disposition_reason=f"EvidenceFlow candidate normalized with expected posture shift {proposed}.",
                )
            )
            contributions.append(
                EnsembleContribution(
                    node_id="preventability_opportunity_score",
                    contributor_role=f"evidenceflow:{template.flow_type}",
                    proposed_value=candidate.preventability_leverage,
                    proposed_range_min=max(0.0, round(candidate.preventability_leverage - 0.15, 4)),
                    proposed_range_max=min(1.0, round(candidate.preventability_leverage + 0.15, 4)),
                    evidence_refs=[candidate.input_id_template.format(episode_id=episode.episode_id)],
                    rationale=candidate.description,
                    disposition="accepted" if template.confidence >= 0.65 else "downgraded",
                    disposition_reason=f"EvidenceFlow candidate normalized with preventability leverage {candidate.preventability_leverage}.",
                )
            )
    elif template.flow_type == "guideline_dependency":
        contributions.append(_flow_strength_contribution(template, "material_gap_strength", template.outputs.evidence_conflict_strength))
    elif template.flow_type == "high_risk_alternative":
        contributions.append(_flow_strength_contribution(template, "harm_clock", template.outputs.evidence_conflict_strength))
    elif template.flow_type == "prudent_ai_conduct":
        contributions.append(_flow_strength_contribution(template, "ai_provenance_risk", template.outputs.evidence_support_strength))
    return contributions


def _flow_strength_contribution(
    template: EvidenceFlowTemplate,
    node_id: str,
    proposed_value: float,
) -> EnsembleContribution:
    disposition = "accepted" if template.confidence >= 0.65 else "downgraded"
    reason = (
        f"Accepted EvidenceFlow contribution at confidence {template.confidence}."
        if disposition == "accepted"
        else f"Downgraded EvidenceFlow contribution because confidence {template.confidence} is below acceptance threshold."
    )
    return EnsembleContribution(
        node_id=node_id,
        contributor_role=f"evidenceflow:{template.flow_type}",
        proposed_value=proposed_value,
        proposed_range_min=max(0.0, round(proposed_value - _range_margin(template.confidence), 4)),
        proposed_range_max=min(1.0, round(proposed_value + _range_margin(template.confidence), 4)),
        evidence_refs=[source for source in template.sources],
        rationale="; ".join(template.outputs.uncertainty_notes) or template.flow_type,
        disposition=disposition,
        disposition_reason=reason,
    )


def _proposed_value_from_finding(finding: StaticFinding, target: str, *, fallback: float) -> float:
    for key in ROLE_TARGET_VALUE_KEYS.get(target, ()):
        value = finding.structured_value.get(key)
        if isinstance(value, int | float):
            return max(0.0, min(1.0, float(value)))
    for value in finding.structured_value.values():
        if isinstance(value, int | float) and 0 <= value <= 1:
            return float(value)
    return max(0.0, min(1.0, fallback))


def _range_margin(confidence: float) -> float:
    return 0.1 if confidence >= 0.7 else 0.2
