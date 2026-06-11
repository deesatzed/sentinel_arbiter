from pathlib import Path

from sentinel_workbench.graph import REQUIRED_GRAPH_METRICS, compute_prudence_graph
from sentinel_workbench.loader import load_case_library
from sentinel_workbench.models import Posture, RequiredTimepoint


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "data" / "cases"


def graph_for_case(episode_id: str):
    episodes = {episode.episode_id: episode for episode in load_case_library(FIXTURE_DIR)}
    return compute_prudence_graph(episodes[episode_id], RequiredTimepoint.T3_DISPOSITION_DECISION)


def test_every_case_computes_required_goal_graph_metrics_at_disposition():
    episodes = load_case_library(FIXTURE_DIR)

    assert episodes
    for episode in episodes:
        graph = compute_prudence_graph(episode, RequiredTimepoint.T3_DISPOSITION_DECISION)

        assert set(REQUIRED_GRAPH_METRICS).issubset(graph.node_values.keys()), episode.episode_id
        assert graph.timepoint_id == RequiredTimepoint.T3_DISPOSITION_DECISION
        assert graph.final_posture in set(Posture)
        for metric in REQUIRED_GRAPH_METRICS:
            value = graph.node_values[metric]
            if isinstance(value, float):
                assert 0.0 <= value <= 1.0, f"{episode.episode_id}:{metric}:{value}"


def test_commission_omission_and_therapy_lanes_are_visible_separately():
    graph = graph_for_case("synthetic_ed_case_001")

    assert graph.omission_lane.risk_score > 0
    assert graph.commission_lane.risk_score > 0
    assert graph.therapy_response_lane.relevance_score > 0
    assert graph.omission_lane.findings
    assert graph.commission_lane.findings
    assert graph.therapy_response_lane.findings


def test_material_gap_and_ai_provenance_drive_obtain_information_posture():
    graph = graph_for_case("synthetic_ed_case_006")

    assert graph.node_values["material_gap_strength"] >= 0.85
    assert graph.node_values["ai_provenance_risk"] >= 0.85
    assert graph.node_values["omission_risk"] > 0
    assert graph.final_posture == Posture.OBTAIN_SPECIFIC_INFORMATION_FIRST
    assert graph.next_best_information_ranking[0] == "verify or downgrade AI-derived driver"


def test_documented_therapy_improvement_keeps_therapy_lane_without_omission_escalation():
    graph = graph_for_case("synthetic_ed_case_002")

    assert graph.therapy_response_lane.relevance_score > 0
    assert graph.omission_lane.risk_score == 0
    assert graph.commission_lane.risk_score == 0
    assert graph.final_posture == Posture.PROCEED_WITH_SAFETY_NET_OR_RECHECK


def test_low_value_gap_is_not_escalated_by_default():
    graph = graph_for_case("synthetic_ed_case_007")

    assert graph.node_values["material_gap_strength"] <= 0.1
    assert graph.node_values["decision_weight"] < 0.5
    assert graph.final_posture == Posture.PROCEED_WITH_UNCERTAINTY_DISCLOSURE


def test_limited_added_value_case_stays_in_commission_lane():
    graph = graph_for_case("synthetic_ed_case_004")

    assert "commission_low_added_value" in graph.commission_lane.findings
    assert graph.omission_lane.risk_score == 0
    assert graph.final_posture == Posture.PROCEED_WITH_UNCERTAINTY_DISCLOSURE
