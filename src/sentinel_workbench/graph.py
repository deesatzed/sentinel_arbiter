from __future__ import annotations

from pydantic import Field

from .models import (
    AccessStatus,
    DecisionEpisode,
    InformationGap,
    InformationBucket,
    PlanCategory,
    Posture,
    RequiredTimepoint,
    StrictModel,
    TherapyResponse,
    VerificationStatus,
)
from .replay import build_replay_view


REQUIRED_GRAPH_METRICS: tuple[str, ...] = (
    "information_sufficiency",
    "material_gap_strength",
    "harm_clock",
    "information_clock",
    "recoverability",
    "future_correction_opportunity",
    "decision_weight",
    "ai_provenance_risk",
    "commission_risk",
    "omission_risk",
    "therapy_response_relevance",
    "next_best_information_rank",
    "preventability_opportunity_score",
)


class GraphLane(StrictModel):
    risk_score: float = Field(ge=0, le=1)
    relevance_score: float = Field(default=0, ge=0, le=1)
    findings: list[str] = Field(default_factory=list)


class PrudenceGraphResult(StrictModel):
    episode_id: str
    timepoint_id: RequiredTimepoint
    node_values: dict[str, float | int]
    commission_lane: GraphLane
    omission_lane: GraphLane
    therapy_response_lane: GraphLane
    next_best_information_ranking: list[str]
    final_posture: Posture


def clamp(value: float) -> float:
    return max(0.0, min(1.0, round(value, 4)))


def max_or_zero(values: list[float]) -> float:
    return max(values) if values else 0.0


def current_time_information_gaps(
    episode: DecisionEpisode,
    timepoint_id: RequiredTimepoint | str,
) -> list[InformationGap]:
    target = RequiredTimepoint(timepoint_id)
    target_sequence = next(state.sequence_index for state in episode.timepoints if state.timepoint_id == target)
    gaps_by_id: dict[str, InformationGap] = {}
    for state in sorted(episode.timepoints, key=lambda item: item.sequence_index):
        if state.sequence_index > target_sequence or state.timepoint_id == RequiredTimepoint.T4_FOLLOW_UP_OR_OUTCOME:
            continue
        for gap in state.information_gaps:
            gaps_by_id[gap.gap_id] = gap
    return list(gaps_by_id.values())


def compute_prudence_graph(
    episode: DecisionEpisode,
    timepoint_id: RequiredTimepoint | str = RequiredTimepoint.T3_DISPOSITION_DECISION,
) -> PrudenceGraphResult:
    replay = build_replay_view(episode, timepoint_id)
    state = replay.current_state
    current_gaps = current_time_information_gaps(episode, replay.timepoint_id)

    gap_relevances = [gap.decision_relevance_prior for gap in current_gaps]
    material_gap_strength = clamp(max_or_zero(gap_relevances))

    low_value_only = bool(current_gaps) and all(
        gap.decision_relevance_prior <= 0.2 for gap in current_gaps
    )
    high_value_gap_count = sum(1 for gap in current_gaps if gap.decision_relevance_prior >= 0.7)
    information_sufficiency = clamp(1.0 - material_gap_strength)

    facts = replay.available_facts
    weak_ai_facts = [
        fact
        for fact in facts
        if fact.verification_status == VerificationStatus.UNVERIFIED_AI_DERIVED
        or fact.source_type.value.startswith("ai_")
    ]
    ai_provenance_risk = clamp(
        max_or_zero([fact.decision_criticality for fact in weak_ai_facts])
    )

    therapy_findings: list[str] = []
    therapy_scores: list[float] = []
    for therapy in state.offered_therapies:
        if therapy.response_observed == TherapyResponse.IMPROVED:
            therapy_findings.append(f"{therapy.therapy_id}:documented_improvement")
            therapy_scores.append(0.35)
        elif therapy.response_observed in {
            TherapyResponse.NO_CLEAR_CHANGE,
            TherapyResponse.WORSE,
            TherapyResponse.NOT_REASSESSED,
            TherapyResponse.UNKNOWN,
        }:
            therapy_findings.append(f"{therapy.therapy_id}:{therapy.response_observed.value}")
            therapy_scores.append(0.75)
        if therapy.therapy_plausibly_indicated_but_not_considered:
            therapy_findings.append(f"{therapy.therapy_id}:not_considered")
            therapy_scores.append(0.9)

    for observation in state.therapy_response_observations:
        if observation.response_observed == TherapyResponse.IMPROVED:
            therapy_findings.append(f"{observation.observation_id}:documented_improvement")
            therapy_scores.append(0.35)
        elif observation.response_observed in {TherapyResponse.NO_CLEAR_CHANGE, TherapyResponse.WORSE}:
            therapy_findings.append(f"{observation.observation_id}:{observation.response_observed.value}")
            therapy_scores.append(0.75)

    therapy_response_relevance = clamp(max_or_zero(therapy_scores))

    commission_only_gap = bool(current_gaps) and all(
        gap.gap_type == "limited_added_value" for gap in current_gaps
    )
    omission_findings: list[str] = []
    for gap in current_gaps:
        if gap.decision_relevance_prior < 0.7:
            continue
        if gap.gap_type == "home_plan_feasibility":
            omission_findings.append("omission_home_plan_feasibility_gap")
        elif gap.gap_type == "ai_fact_verification":
            omission_findings.append("omission_ai_fact_verification_gap")
        elif gap.gap_type == "therapy_response":
            omission_findings.append("omission_unassessed_response")
        elif gap.gap_type == "limited_added_value":
            continue
        else:
            omission_findings.append("omission_material_gap")
    if state.follow_up_feasibility.home_support in {AccessStatus.UNCLEAR, AccessStatus.LIMITED}:
        omission_findings.append("omission_home_plan_feasibility_gap")
    omission_risk = clamp(max(material_gap_strength if omission_findings else 0.0, ai_provenance_risk))

    commission_findings: list[str] = []
    if state.proposed_disposition_posture_under_review.assertiveness.value in {"high", "definitive"} and (
        material_gap_strength >= 0.7 or ai_provenance_risk >= 0.7
    ):
        commission_findings.append("commission_overconfident_posture")
    if state.proposed_disposition_posture_under_review.stated_plan_category == PlanCategory.HOSPITAL_BASED_MONITORING_OR_TREATMENT:
        if any(gap.gap_type == "limited_added_value" for gap in current_gaps):
            commission_findings.append("commission_low_added_value")
            commission_findings.append("commission_added_burden")
    if ai_provenance_risk >= 0.7:
        commission_findings.append("commission_unverified_driver")
    commission_risk = clamp(
        max(
            0.0,
            0.75 if "commission_overconfident_posture" in commission_findings else 0.0,
            0.7 if "commission_low_added_value" in commission_findings else 0.0,
            ai_provenance_risk if "commission_unverified_driver" in commission_findings else 0.0,
        )
    )

    information_clock = clamp(1.0 - min(max_or_zero([gap.time_to_obtain_hours for gap in current_gaps]) / 24.0, 1.0))
    harm_clock = clamp(0.4 + (0.3 * material_gap_strength) + (0.2 * therapy_response_relevance) + (0.1 * ai_provenance_risk))
    recoverability = clamp(1.0 - (0.5 * material_gap_strength) - (0.2 * therapy_response_relevance))
    future_correction_opportunity = clamp(
        0.8
        if state.follow_up_feasibility.follow_up_access == AccessStatus.CLEAR
        else 0.35
        if state.follow_up_feasibility.follow_up_access in {AccessStatus.UNCLEAR, AccessStatus.UNKNOWN}
        else 0.2
    )

    if low_value_only:
        decision_weight = clamp(0.25 + (0.2 * ai_provenance_risk))
    else:
        decision_weight = clamp(
            0.25
            + (0.35 * material_gap_strength)
            + (0.2 * therapy_response_relevance)
            + (0.2 * ai_provenance_risk)
        )

    burden_modifier = clamp(
        1.0
        - max_or_zero(
            [
                0.1 if gap.burden.value == "low" else 0.25 if gap.burden.value == "moderate" else 0.5
                for gap in current_gaps
            ]
        )
    )
    preventability_opportunity_score = clamp(
        material_gap_strength * decision_weight * information_clock * burden_modifier
    )

    next_best_information = [
        gap.candidate_input_mapping or gap.description
        for gap in sorted(current_gaps, key=lambda item: item.decision_relevance_prior, reverse=True)
        if gap.decision_relevance_prior >= 0.5
    ]

    if low_value_only:
        final_posture = Posture.PROCEED_WITH_UNCERTAINTY_DISCLOSURE
    elif commission_only_gap and commission_risk >= 0.65:
        final_posture = Posture.PROCEED_WITH_UNCERTAINTY_DISCLOSURE
    elif material_gap_strength >= 0.75 or ai_provenance_risk >= 0.75 or any(
        "not_considered" in finding or "not_reassessed" in finding for finding in therapy_findings
    ):
        final_posture = Posture.OBTAIN_SPECIFIC_INFORMATION_FIRST
    elif commission_risk >= 0.65:
        final_posture = Posture.PROCEED_WITH_UNCERTAINTY_DISCLOSURE
    elif therapy_response_relevance > 0 and not omission_findings:
        final_posture = Posture.PROCEED_WITH_SAFETY_NET_OR_RECHECK
    else:
        final_posture = Posture.INDETERMINATE if high_value_gap_count == 0 else Posture.OBTAIN_SPECIFIC_INFORMATION_FIRST

    node_values: dict[str, float | int] = {
        "information_sufficiency": information_sufficiency,
        "material_gap_strength": material_gap_strength,
        "harm_clock": harm_clock,
        "information_clock": information_clock,
        "recoverability": recoverability,
        "future_correction_opportunity": future_correction_opportunity,
        "decision_weight": decision_weight,
        "ai_provenance_risk": ai_provenance_risk,
        "commission_risk": commission_risk,
        "omission_risk": omission_risk,
        "therapy_response_relevance": therapy_response_relevance,
        "next_best_information_rank": len(next_best_information),
        "preventability_opportunity_score": preventability_opportunity_score,
    }

    return PrudenceGraphResult(
        episode_id=episode.episode_id,
        timepoint_id=replay.timepoint_id,
        node_values=node_values,
        commission_lane=GraphLane(risk_score=commission_risk, findings=sorted(set(commission_findings))),
        omission_lane=GraphLane(risk_score=omission_risk, findings=sorted(set(omission_findings))),
        therapy_response_lane=GraphLane(
            risk_score=therapy_response_relevance,
            relevance_score=therapy_response_relevance,
            findings=sorted(set(therapy_findings)),
        ),
        next_best_information_ranking=next_best_information,
        final_posture=final_posture,
    )
