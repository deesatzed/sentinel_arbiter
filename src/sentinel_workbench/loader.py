from __future__ import annotations

import json
from pathlib import Path

from .models import DecisionEpisode
from .safety import scan_forbidden_content


def load_episode(path: str | Path) -> DecisionEpisode:
    episode_path = Path(path)
    with episode_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    findings = scan_forbidden_content(payload, allow_safety_rule_lists=False)
    if findings:
        formatted = "; ".join(f"{finding.category}:{finding.value}" for finding in findings)
        raise ValueError(f"forbidden content in {episode_path}: {formatted}")

    return DecisionEpisode.model_validate(payload)


def load_case_library(case_dir: str | Path) -> list[DecisionEpisode]:
    path = Path(case_dir)
    episodes: list[DecisionEpisode] = []
    for fixture in sorted(path.glob("*.json")):
        if fixture.name.startswith("invalid_"):
            continue
        episodes.append(load_episode(fixture))
    return episodes
