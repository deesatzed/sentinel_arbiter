from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import Field

from .graph import REQUIRED_GRAPH_METRICS, compute_prudence_graph, current_time_information_gaps
from .models import (
    DecisionEpisode,
    RequiredTimepoint,
    StrictModel,
    VerificationStatus,
)
from .replay import build_replay_view
from .static_inputs import StaticInputBundle


EvidenceQuality = Literal["strong", "moderate", "weak", "unknown"]
ContributionDisposition = Literal["accepted", "rejected", "downgraded"]


class NodeDefinition(StrictModel):
    id: str
    lane: str
    question: str
    dependent_inputs: list[str] = Field(min_length=1)
    output_scale: str
    version: str


class NodeEvidence(StrictModel):
    ref_id: str
    node_id: str
    source_type: str
    source_timepoint: str
    quoted_or_structured_fact: str
    provenance: str
    supports: str
    weight: float = Field(ge=0, le=1)
    quality: EvidenceQuality
    limitations: list[str] = Field(default_factory=list)


class NodeEstimate(StrictModel):
    node_id: str
    value: float | int
    range_min: float
    range_max: float
    median: float
    distribution_kind: str
    confidence: float = Field(ge=0, le=1)
    method: str
    evidence_refs: list[str] = Field(default_factory=list)


class EnsembleContribution(StrictModel):
    node_id: str
    contributor_role: str
    proposed_value: float | int
    proposed_range_min: float
    proposed_range_max: float
    evidence_refs: list[str] = Field(default_factory=list)
    rationale: str
    disposition: ContributionDisposition
    disposition_reason: str


class NodeAudit(StrictModel):
    node_id: str
    definition: NodeDefinition
    definition_version: str
    dependencies: list[str]
    evidence: list[NodeEvidence] = Field(default_factory=list)
    estimate: NodeEstimate
    ensemble_contributions: list[EnsembleContribution] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    sensitivity_note: str


class NodeAuditBundle(StrictModel):
    episode_id: str
    timepoint_id: RequiredTimepoint
    graph_version: str
    node_library_version: str
    node_audits: list[NodeAudit]


NODE_LIBRARY_VERSION = "ed_node_library_v0.2"
GRAPH_VERSION = "deterministic_graph_v0.1"


NODE_DEFINITIONS: dict[str, NodeDefinition] = {
    "information_sufficiency": NodeDefinition(
        id="information_sufficiency",
        lane="information_state",
        question="How complete is the current-time information state for governance review?",
        dependent_inputs=["current_time_information_gaps"],
        output_scale="0_to_1",
        version=NODE_LIBRARY_VERSION,
    ),
    "material_gap_strength": NodeDefinition(
        id="material_gap_strength",
        lane="information_state",
        question="How decision-relevant are unresolved current-time gaps?",
        dependent_inputs=["current_time_information_gaps"],
        output_scale="0_to_1",
        version=NODE_LIBRARY_VERSION,
    ),
    "harm_clock": NodeDefinition(
        id="harm_clock",
        lane="timing",
        question="How time-sensitive is the uncertainty posture?",
        dependent_inputs=["current_time_information_gaps", "therapy_response", "ai_provenance"],
        output_scale="0_to_1",
        version=NODE_LIBRARY_VERSION,
    ),
    "information_clock": NodeDefinition(
        id="information_clock",
        lane="timing",
        question="How quickly can useful information plausibly be obtained?",
        dependent_inputs=["current_time_information_gaps"],
        output_scale="0_to_1",
        version=NODE_LIBRARY_VERSION,
    ),
    "recoverability": NodeDefinition(
        id="recoverability",
        lane="timing",
        question="How recoverable is the decision posture if uncertainty later resolves?",
        dependent_inputs=["current_time_information_gaps", "therapy_response"],
        output_scale="0_to_1",
        version=NODE_LIBRARY_VERSION,
    ),
    "future_correction_opportunity": NodeDefinition(
        id="future_correction_opportunity",
        lane="timing",
        question="Is there a represented opportunity to correct course later?",
        dependent_inputs=["follow_up_feasibility"],
        output_scale="0_to_1",
        version=NODE_LIBRARY_VERSION,
    ),
    "decision_weight": NodeDefinition(
        id="decision_weight",
        lane="posture_weight",
        question="How much should the represented uncertainty influence posture?",
        dependent_inputs=["current_time_information_gaps", "therapy_response", "ai_provenance"],
        output_scale="0_to_1",
        version=NODE_LIBRARY_VERSION,
    ),
    "ai_provenance_risk": NodeDefinition(
        id="ai_provenance_risk",
        lane="provenance",
        question="How much does unverified AI-derived information drive the posture?",
        dependent_inputs=["available_facts"],
        output_scale="0_to_1",
        version=NODE_LIBRARY_VERSION,
    ),
    "commission_risk": NodeDefinition(
        id="commission_risk",
        lane="commission",
        question="How much risk is introduced by overconfident or low-added-value action?",
        dependent_inputs=["proposed_posture", "current_time_information_gaps", "ai_provenance"],
        output_scale="0_to_1",
        version=NODE_LIBRARY_VERSION,
    ),
    "omission_risk": NodeDefinition(
        id="omission_risk",
        lane="omission",
        question="How much risk is introduced by unresolved material missing information?",
        dependent_inputs=["current_time_information_gaps", "follow_up_feasibility", "ai_provenance"],
        output_scale="0_to_1",
        version=NODE_LIBRARY_VERSION,
    ),
    "therapy_response_relevance": NodeDefinition(
        id="therapy_response_relevance",
        lane="therapy_response",
        question="How relevant is represented therapy response or nonresponse to posture?",
        dependent_inputs=["offered_therapies", "therapy_response_observations"],
        output_scale="0_to_1",
        version=NODE_LIBRARY_VERSION,
    ),
    "next_best_information_rank": NodeDefinition(
        id="next_best_information_rank",
        lane="information_state",
        question="How many next-best information items clear the materiality threshold?",
        dependent_inputs=["current_time_information_gaps"],
        output_scale="count",
        version=NODE_LIBRARY_VERSION,
    ),
    "preventability_opportunity_score": NodeDefinition(
        id="preventability_opportunity_score",
        lane="preventability_proxy",
        question="What is the proxy opportunity for improving the governance discussion?",
        dependent_inputs=["material_gap_strength", "decision_weight", "information_clock", "burden_modifier"],
        output_scale="0_to_1",
        version=NODE_LIBRARY_VERSION,
    ),
}


def build_node_audit_bundle(
    episode: DecisionEpisode,
    timepoint_id: RequiredTimepoint | str = RequiredTimepoint.T3_DISPOSITION_DECISION,
    *,
    static_bundle: StaticInputBundle | None = None,
) -> NodeAuditBundle:
    target = RequiredTimepoint(timepoint_id)
    graph = compute_prudence_graph(episode, target)
    contributions_by_node: dict[str, list[EnsembleContribution]] = {}
    if static_bundle is not None:
        from .ensemble import build_ensemble_contribution_bundle

        ensemble = build_ensemble_contribution_bundle(episode, static_bundle, target)
        for contribution in ensemble.contributions:
            contributions_by_node.setdefault(contribution.node_id, []).append(contribution)
    audits: list[NodeAudit] = []
    for node_id in REQUIRED_GRAPH_METRICS:
        definition = NODE_DEFINITIONS[node_id]
        evidence = _evidence_for_node(episode, target, node_id)
        estimate = _estimate_for_node(node_id, graph.node_values[node_id], evidence)
        audits.append(
            NodeAudit(
                node_id=node_id,
                definition=definition,
                definition_version=definition.version,
                dependencies=definition.dependent_inputs,
                evidence=evidence,
                estimate=estimate,
                ensemble_contributions=contributions_by_node.get(node_id, []),
                conflicts=_conflicts_for_node(evidence),
                sensitivity_note=_sensitivity_note(node_id),
            )
        )
    return NodeAuditBundle(
        episode_id=episode.episode_id,
        timepoint_id=target,
        graph_version=GRAPH_VERSION,
        node_library_version=NODE_LIBRARY_VERSION,
        node_audits=audits,
    )


def summarize_node_audit_completeness(episodes: list[DecisionEpisode]) -> dict[str, object]:
    expected_nodes = set(REQUIRED_GRAPH_METRICS)
    missing: list[str] = []
    incomplete: list[str] = []
    for episode in episodes:
        bundle = build_node_audit_bundle(episode)
        audits_by_id = {audit.node_id: audit for audit in bundle.node_audits}
        for node_id in sorted(expected_nodes - set(audits_by_id)):
            missing.append(f"{episode.episode_id}:{node_id}")
        for audit in audits_by_id.values():
            if not _audit_complete(audit):
                incomplete.append(f"{episode.episode_id}:{audit.node_id}")
    return {
        "complete": not missing and not incomplete,
        "case_count": len(episodes),
        "expected_nodes_per_case": len(expected_nodes),
        "missing": missing,
        "incomplete": incomplete,
    }


def export_node_audit_schema(output_path: str | Path = "schemas/node_audit.schema.json") -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(NodeAuditBundle.model_json_schema(), indent=2) + "\n", encoding="utf-8")
    return path


def _audit_complete(audit: NodeAudit) -> bool:
    if not audit.definition.dependent_inputs or audit.dependencies != audit.definition.dependent_inputs:
        return False
    if not audit.sensitivity_note:
        return False
    if not audit.estimate.method or not audit.estimate.distribution_kind:
        return False
    if not audit.estimate.range_min <= audit.estimate.median <= audit.estimate.range_max:
        return False
    evidence_ids = {item.ref_id for item in audit.evidence}
    return set(audit.estimate.evidence_refs).issubset(evidence_ids)


def _estimate_for_node(node_id: str, value: float | int, evidence: list[NodeEvidence]) -> NodeEstimate:
    numeric_value = float(value)
    if node_id == "next_best_information_rank":
        range_min = max(0.0, numeric_value - 1.0)
        range_max = numeric_value + 1.0
        distribution_kind = "deterministic_count_with_neighbor_range"
    else:
        margin = 0.1 + (0.05 if any(item.quality in {"weak", "unknown"} for item in evidence) else 0.0)
        range_min = max(0.0, round(numeric_value - margin, 4))
        range_max = min(1.0, round(numeric_value + margin, 4))
        distribution_kind = "bounded_deterministic_interval"
    confidence = _confidence_from_evidence(evidence)
    return NodeEstimate(
        node_id=node_id,
        value=value,
        range_min=range_min,
        range_max=range_max,
        median=numeric_value,
        distribution_kind=distribution_kind,
        confidence=confidence,
        method="deterministic_fixture_field_mapping_v0.1",
        evidence_refs=[item.ref_id for item in evidence],
    )


def _confidence_from_evidence(evidence: list[NodeEvidence]) -> float:
    if not evidence:
        return 0.45
    quality_scores = {"strong": 0.9, "moderate": 0.7, "weak": 0.45, "unknown": 0.3}
    return round(sum(quality_scores[item.quality] for item in evidence) / len(evidence), 4)


def _evidence_for_node(
    episode: DecisionEpisode,
    timepoint_id: RequiredTimepoint,
    node_id: str,
) -> list[NodeEvidence]:
    replay = build_replay_view(episode, timepoint_id)
    gaps = current_time_information_gaps(episode, timepoint_id)
    evidence: list[NodeEvidence] = []

    if node_id in {
        "information_sufficiency",
        "material_gap_strength",
        "harm_clock",
        "information_clock",
        "recoverability",
        "decision_weight",
        "commission_risk",
        "omission_risk",
        "next_best_information_rank",
        "preventability_opportunity_score",
    }:
        for gap in gaps:
            evidence.append(
                NodeEvidence(
                    ref_id=f"gap:{gap.gap_id}",
                    node_id=node_id,
                    source_type="information_gap",
                    source_timepoint=_timepoint_for_gap(episode, gap.gap_id),
                    quoted_or_structured_fact=gap.description,
                    provenance="structured_gap_field",
                    supports=gap.gap_type,
                    weight=gap.decision_relevance_prior,
                    quality="moderate",
                    limitations=[],
                )
            )

    if node_id in {"ai_provenance_risk", "harm_clock", "decision_weight", "commission_risk", "omission_risk"}:
        for fact in replay.available_facts:
            if fact.verification_status == VerificationStatus.UNVERIFIED_AI_DERIVED or fact.source_type.value.startswith("ai_"):
                evidence.append(
                    NodeEvidence(
                        ref_id=f"fact:{fact.fact_id}",
                        node_id=node_id,
                        source_type=fact.source_type.value,
                        source_timepoint=_timepoint_for_fact(episode, fact.fact_id),
                        quoted_or_structured_fact=fact.text,
                        provenance=fact.verification_status.value,
                        supports="ai_provenance_risk",
                        weight=fact.decision_criticality,
                        quality="weak",
                        limitations=["Unverified AI-derived or AI-summarized evidence is downgraded."],
                    )
                )

    if node_id in {"therapy_response_relevance", "harm_clock", "recoverability", "decision_weight"}:
        for therapy in replay.current_state.offered_therapies:
            evidence.append(
                NodeEvidence(
                    ref_id=f"therapy:{therapy.therapy_id}",
                    node_id=node_id,
                    source_type="offered_therapy",
                    source_timepoint=therapy.offered_at_timepoint.value,
                    quoted_or_structured_fact=therapy.response_observed.value,
                    provenance=therapy.response_reliability.value,
                    supports="therapy_response",
                    weight=_therapy_weight(therapy.response_observed.value),
                    quality=_quality_from_reliability(therapy.response_reliability.value),
                    limitations=[] if therapy.response_source_refs else ["Therapy response source refs are limited or absent."],
                )
            )
        for observation in replay.current_state.therapy_response_observations:
            evidence.append(
                NodeEvidence(
                    ref_id=f"therapy_observation:{observation.observation_id}",
                    node_id=node_id,
                    source_type="therapy_response_observation",
                    source_timepoint=observation.observed_at_timepoint.value,
                    quoted_or_structured_fact=observation.response_observed.value,
                    provenance=observation.reliability.value,
                    supports="therapy_response",
                    weight=_therapy_weight(observation.response_observed.value),
                    quality=_quality_from_reliability(observation.reliability.value),
                    limitations=[] if observation.source_refs else ["Therapy response observation source refs are limited or absent."],
                )
            )

    if node_id == "future_correction_opportunity":
        follow_up = replay.current_state.follow_up_feasibility
        evidence.append(
            NodeEvidence(
                ref_id=f"follow_up:{episode.episode_id}:{timepoint_id.value}",
                node_id=node_id,
                source_type="follow_up_feasibility",
                source_timepoint=timepoint_id.value,
                quoted_or_structured_fact=(
                    f"follow_up_access={follow_up.follow_up_access.value}; "
                    f"home_support={follow_up.home_support.value}; return_access={follow_up.return_access.value}"
                ),
                provenance=follow_up.barrier_reliability.value,
                supports="future_correction_opportunity",
                weight=0.5,
                quality=_quality_from_reliability(follow_up.barrier_reliability.value),
                limitations=[] if follow_up.barrier_source_refs else ["Follow-up feasibility source refs are limited or absent."],
            )
        )

    if not evidence:
        evidence.append(
            NodeEvidence(
                ref_id=f"node:{node_id}:no_direct_evidence",
                node_id=node_id,
                source_type="derived_node",
                source_timepoint=timepoint_id.value,
                quoted_or_structured_fact="No direct current-time evidence item was mapped to this node.",
                provenance="deterministic_graph_derivation",
                supports=node_id,
                weight=0.0,
                quality="unknown",
                limitations=["Derived from absence or low materiality of represented current-time inputs."],
            )
        )
    return evidence


def _timepoint_for_gap(episode: DecisionEpisode, gap_id: str) -> str:
    for state in episode.timepoints:
        if state.timepoint_id == RequiredTimepoint.T4_FOLLOW_UP_OR_OUTCOME:
            continue
        if any(gap.gap_id == gap_id for gap in state.information_gaps):
            return state.timepoint_id.value
    return RequiredTimepoint.T3_DISPOSITION_DECISION.value


def _timepoint_for_fact(episode: DecisionEpisode, fact_id: str) -> str:
    for state in episode.timepoints:
        if state.timepoint_id == RequiredTimepoint.T4_FOLLOW_UP_OR_OUTCOME:
            continue
        if any(fact.fact_id == fact_id for fact in state.available_facts):
            return state.timepoint_id.value
    return RequiredTimepoint.T3_DISPOSITION_DECISION.value


def _quality_from_reliability(reliability: str) -> EvidenceQuality:
    if reliability == "high":
        return "strong"
    if reliability == "moderate":
        return "moderate"
    if reliability == "low":
        return "weak"
    return "unknown"


def _therapy_weight(response: str) -> float:
    if response == "improved":
        return 0.35
    if response in {"no_clear_change", "worse", "not_reassessed", "unknown"}:
        return 0.75
    return 0.5


def _conflicts_for_node(evidence: list[NodeEvidence]) -> list[str]:
    qualities = {item.quality for item in evidence}
    if "strong" in qualities and ("weak" in qualities or "unknown" in qualities):
        return ["mixed_evidence_quality"]
    return []


def _sensitivity_note(node_id: str) -> str:
    if node_id == "next_best_information_rank":
        return "Posture sensitivity depends on whether additional gaps cross the materiality threshold."
    return "Posture sensitivity should be reviewed if the estimate range crosses a graph threshold."
