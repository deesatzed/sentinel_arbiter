from pathlib import Path

from sentinel_workbench.case_library import REQUIRED_CASE_PATTERNS, summarize_case_library
from sentinel_workbench.loader import load_case_library
from sentinel_workbench.models import REQUIRED_CURRENT_TIMEPOINTS, RequiredTimepoint
from sentinel_workbench.replay import build_replay_view


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "data" / "cases"


def test_valid_case_library_covers_all_goal_required_patterns():
    summary = summarize_case_library(FIXTURE_DIR)

    assert summary.valid_case_count >= 7
    assert summary.covered_patterns == set(REQUIRED_CASE_PATTERNS)
    assert summary.missing_patterns == set()


def test_every_valid_case_has_current_timepoints_and_blocks_t4_from_t3():
    episodes = load_case_library(FIXTURE_DIR)

    assert episodes
    for episode in episodes:
        present = {state.timepoint_id for state in episode.timepoints}
        assert set(REQUIRED_CURRENT_TIMEPOINTS).issubset(present), episode.episode_id
        assert RequiredTimepoint.T4_FOLLOW_UP_OR_OUTCOME in present, episode.episode_id

        t4_fact_ids = {
            fact.fact_id
            for state in episode.timepoints
            if state.timepoint_id == RequiredTimepoint.T4_FOLLOW_UP_OR_OUTCOME
            for fact in state.available_facts
        }
        assert t4_fact_ids
        for timepoint in REQUIRED_CURRENT_TIMEPOINTS:
            replay = build_replay_view(episode, timepoint)
            replay_fact_ids = {fact.fact_id for fact in replay.available_facts}

            assert t4_fact_ids.isdisjoint(replay_fact_ids), episode.episode_id
            assert t4_fact_ids.issubset(set(replay.blocked_future_fact_ids)), episode.episode_id
