from __future__ import annotations

from pydantic import Field

from .models import DecisionEpisode, Fact, RequiredTimepoint, StrictModel, TimelineState


class ReplayView(StrictModel):
    episode_id: str
    timepoint_id: RequiredTimepoint
    available_facts: list[Fact]
    current_state: TimelineState
    blocked_future_fact_ids: list[str] = Field(default_factory=list)


def build_replay_view(episode: DecisionEpisode, timepoint_id: RequiredTimepoint | str) -> ReplayView:
    selected_timepoint = RequiredTimepoint(timepoint_id)
    by_timepoint = {state.timepoint_id: state for state in episode.timepoints}
    if selected_timepoint not in by_timepoint:
        raise ValueError(f"timepoint not found: {selected_timepoint}")

    selected_state = by_timepoint[selected_timepoint]
    selected_index = selected_state.sequence_index
    available_facts: list[Fact] = []
    blocked_future_fact_ids: set[str] = set()

    for state in sorted(episode.timepoints, key=lambda item: item.sequence_index):
        if state.sequence_index <= selected_index and state.timepoint_id != RequiredTimepoint.T4_FOLLOW_UP_OR_OUTCOME:
            available_facts.extend(state.available_facts)
            blocked_future_fact_ids.update(fact.fact_id for fact in state.hidden_future_facts)
        else:
            blocked_future_fact_ids.update(fact.fact_id for fact in state.available_facts)
            blocked_future_fact_ids.update(fact.fact_id for fact in state.hidden_future_facts)

    return ReplayView(
        episode_id=episode.episode_id,
        timepoint_id=selected_timepoint,
        available_facts=available_facts,
        current_state=selected_state,
        blocked_future_fact_ids=sorted(blocked_future_fact_ids),
    )
