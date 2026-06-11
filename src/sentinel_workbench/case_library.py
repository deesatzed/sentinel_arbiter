from __future__ import annotations

from pathlib import Path

from pydantic import Field

from .loader import load_case_library
from .models import CasePattern, StrictModel


REQUIRED_CASE_PATTERNS: tuple[CasePattern, ...] = (
    CasePattern.MATERIAL_MISSING_INPUT,
    CasePattern.THERAPY_DOCUMENTED_IMPROVEMENT,
    CasePattern.THERAPY_NONRESPONSE_OR_UNCLEAR,
    CasePattern.THERAPY_PLAUSIBLY_INDICATED_NOT_CONSIDERED,
    CasePattern.HOME_PLAN_FEASIBILITY_PROBLEM,
    CasePattern.LIMITED_ADDED_VALUE,
    CasePattern.AI_DERIVED_OR_WEAK_FACT,
)


class CaseLibrarySummary(StrictModel):
    valid_case_count: int
    covered_patterns: set[CasePattern] = Field(default_factory=set)
    missing_patterns: set[CasePattern] = Field(default_factory=set)


def summarize_case_library(case_dir: str | Path) -> CaseLibrarySummary:
    episodes = load_case_library(case_dir)
    covered: set[CasePattern] = set()
    for episode in episodes:
        covered.update(episode.expected_outputs.covered_case_patterns)
    required = set(REQUIRED_CASE_PATTERNS)
    return CaseLibrarySummary(
        valid_case_count=len(episodes),
        covered_patterns=covered,
        missing_patterns=required - covered,
    )
