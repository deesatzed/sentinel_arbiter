from __future__ import annotations

import argparse
import json
from pathlib import Path

from pydantic import Field

from .graph import REQUIRED_GRAPH_METRICS
from .models import DecisionEpisode, RequiredTimepoint, StrictModel
from .safety import scan_forbidden_content


REQUIRED_ROLE_NAMES: tuple[str, ...] = (
    "prudent_layperson",
    "prudent_provider",
    "prudent_healthcare_ai",
    "duty_to_inquire",
    "risk_horizon",
    "red_team",
    "defense",
)

REQUIRED_FLOW_TYPES: tuple[str, ...] = (
    "guideline_dependency",
    "next_best_input",
    "high_risk_alternative",
    "prudent_ai_conduct",
)

ALLOWED_NODE_TARGETS: frozenset[str] = frozenset(
    REQUIRED_GRAPH_METRICS
    + (
        "prudent_layperson_threshold",
        "safety_net_need",
        "escalation_need",
        "prudent_provider_threshold",
        "prudent_ai_threshold",
        "uncertainty_disclosure_need",
        "primary_source_confirmation_need",
        "ai_provenance_warning",
        "material_gap_present",
        "gap_decision_relevance",
        "evidence_conflict",
        "under_action_risk",
        "over_action_risk",
    )
)


class StaticFinding(StrictModel):
    finding_id_template: str
    finding_type: str
    structured_value: dict[str, object] = Field(default_factory=dict)
    confidence: float = Field(ge=0, le=1)
    rationale_short: str
    source_refs: list[str] = Field(default_factory=list)
    node_targets: list[str] = Field(min_length=1)
    evidence_tier: str


class RoleAssessmentTemplate(StrictModel):
    assessment_id_template: str
    role_name: str
    timepoint_id: RequiredTimepoint
    assessment_scope: str
    findings: list[StaticFinding] = Field(min_length=1)
    overall_confidence: float = Field(ge=0, le=1)
    missing_information_identified: list[str] = Field(default_factory=list)
    uncertainty_notes: list[str] = Field(default_factory=list)
    sources_used: list[str] = Field(default_factory=list)


class EvidenceCandidateInput(StrictModel):
    input_id_template: str
    description: str
    input_category: str
    burden: str
    time_to_obtain_hours: float = Field(ge=0)
    result_distribution: list[dict[str, object]] = Field(default_factory=list)
    expected_posture_shift: float = Field(ge=0, le=1)
    preventability_leverage: float = Field(ge=0, le=1)


class EvidenceFlowOutputs(StrictModel):
    required_variables: list[str] = Field(default_factory=list)
    missing_variables: list[str] = Field(default_factory=list)
    candidate_inputs: list[EvidenceCandidateInput] = Field(default_factory=list)
    evidence_support_strength: float = Field(default=0, ge=0, le=1)
    evidence_conflict_strength: float = Field(default=0, ge=0, le=1)
    uncertainty_notes: list[str] = Field(default_factory=list)


class EvidenceFlowTemplate(StrictModel):
    flow_id_template: str
    flow_type: str
    timepoint_id: RequiredTimepoint
    outputs: EvidenceFlowOutputs
    confidence: float = Field(ge=0, le=1)
    sources: list[str] = Field(default_factory=list)
    evidence_version: str


class StaticInputBundle(StrictModel):
    bundle_id: str
    version: str
    applies_to: str
    role_assessment_templates: list[RoleAssessmentTemplate] = Field(default_factory=list)
    evidenceflow_templates: list[EvidenceFlowTemplate] = Field(default_factory=list)


class StaticInputValidationSummary(StrictModel):
    valid_case_count: int
    role_outputs_by_case: dict[str, set[str]] = Field(default_factory=dict)
    evidenceflow_outputs_by_case: dict[str, set[str]] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)


def load_static_input_bundle(path: str | Path) -> StaticInputBundle:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return StaticInputBundle.model_validate(payload)


def validate_static_inputs(
    bundle: StaticInputBundle,
    episodes: list[DecisionEpisode],
) -> StaticInputValidationSummary:
    errors: list[str] = []
    role_outputs_by_case: dict[str, set[str]] = {}
    evidenceflow_outputs_by_case: dict[str, set[str]] = {}

    findings = scan_forbidden_content(bundle.model_dump(mode="json"), allow_safety_rule_lists=False)
    errors.extend(f"safety:{finding.category}:{finding.value}" for finding in findings)

    for template in bundle.role_assessment_templates:
        if template.role_name not in REQUIRED_ROLE_NAMES:
            errors.append(f"role:unknown_role:{template.role_name}")
        if template.timepoint_id == RequiredTimepoint.T4_FOLLOW_UP_OR_OUTCOME:
            errors.append(f"role:future_timepoint:{template.role_name}")
        for finding in template.findings:
            for target in finding.node_targets:
                if target not in ALLOWED_NODE_TARGETS:
                    errors.append(f"role:unknown_node_target:{target}")

    for template in bundle.evidenceflow_templates:
        if template.flow_type not in REQUIRED_FLOW_TYPES:
            errors.append(f"evidenceflow:unknown_flow_type:{template.flow_type}")
        if template.timepoint_id == RequiredTimepoint.T4_FOLLOW_UP_OR_OUTCOME:
            errors.append(f"evidenceflow:future_timepoint:{template.flow_type}")
        for candidate in template.outputs.candidate_inputs:
            if not candidate.result_distribution:
                errors.append(f"evidenceflow:missing_result_distribution:{template.flow_type}")

    role_names = {template.role_name for template in bundle.role_assessment_templates}
    flow_types = {template.flow_type for template in bundle.evidenceflow_templates}
    missing_roles = set(REQUIRED_ROLE_NAMES) - role_names
    missing_flows = set(REQUIRED_FLOW_TYPES) - flow_types

    for episode in episodes:
        role_outputs_by_case[episode.episode_id] = set(role_names)
        evidenceflow_outputs_by_case[episode.episode_id] = set(flow_types)
        for role in sorted(missing_roles):
            errors.append(f"{episode.episode_id}:missing_role:{role}")
        for flow_type in sorted(missing_flows):
            errors.append(f"{episode.episode_id}:missing_evidenceflow:{flow_type}")

    return StaticInputValidationSummary(
        valid_case_count=len(episodes),
        role_outputs_by_case=role_outputs_by_case,
        evidenceflow_outputs_by_case=evidenceflow_outputs_by_case,
        errors=errors,
    )


def export_static_input_schemas(output_dir: str | Path = "schemas") -> list[Path]:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    targets = [
        (path / "static_role_assessment.schema.json", RoleAssessmentTemplate),
        (path / "static_evidenceflow_result.schema.json", EvidenceFlowTemplate),
        (path / "static_input_bundle.schema.json", StaticInputBundle),
    ]
    written: list[Path] = []
    for target_path, model in targets:
        target_path.write_text(json.dumps(model.model_json_schema(), indent=2) + "\n", encoding="utf-8")
        written.append(target_path)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Sentinel Workbench static role/EvidenceFlow inputs.")
    parser.add_argument("--static-inputs", default="data/static_inputs/static_inputs.json")
    parser.add_argument("--case-dir", default="data/cases")
    args = parser.parse_args()

    from .loader import load_case_library

    bundle = load_static_input_bundle(args.static_inputs)
    episodes = load_case_library(args.case_dir)
    summary = validate_static_inputs(bundle, episodes)
    if summary.errors:
        print(f"static_inputs cases={summary.valid_case_count} errors={len(summary.errors)}")
        for error in summary.errors:
            print(error)
        raise SystemExit(1)
    print(f"static_inputs cases={summary.valid_case_count} errors=0")


if __name__ == "__main__":
    main()
