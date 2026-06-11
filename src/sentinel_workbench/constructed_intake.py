from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from pathlib import Path

from .models import (
    ActorType,
    Assertiveness,
    Burden,
    CasePattern,
    CaseSyntheticity,
    DecisionEpisode,
    DecisionPointType,
    ExpectedOutputs,
    Fact,
    FollowUpFeasibility,
    InformationBucket,
    InformationGap,
    Knowability,
    PlanCategory,
    Posture,
    ProposedDispositionPosture,
    RequiredTimepoint,
    SourceType,
    TimelineState,
    VerificationStatus,
    Actor,
)
from .redaction import DeterministicRedactor, RedactionResult
from .redaction import RedactionReport


@dataclass(frozen=True)
class ConstructedInputArtifacts:
    out_dir: Path
    redacted_input_path: Path
    redaction_report_path: Path
    draft_episode_path: Path | None
    quarantined: bool


def prepare_constructed_input(
    *,
    input_path: str | Path,
    out_dir: str | Path,
    episode_id: str,
    title: str,
    quarantine_on_residual: bool = False,
) -> ConstructedInputArtifacts:
    source_path = Path(input_path)
    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_text = source_path.read_text(encoding="utf-8")
    redaction = DeterministicRedactor().redact(raw_text)

    redacted_input_path = output_dir / "redacted_input.txt"
    redaction_report_path = output_dir / "redaction_report.json"
    draft_episode_path = output_dir / "draft_episode.json"

    redacted_input_path.write_text(redaction.clean_text, encoding="utf-8")

    if redaction.residual_findings:
        _write_redaction_report(redaction_report_path, redaction, status="quarantined")
        if quarantine_on_residual:
            return ConstructedInputArtifacts(
                out_dir=output_dir,
                redacted_input_path=redacted_input_path,
                redaction_report_path=redaction_report_path,
                draft_episode_path=None,
                quarantined=True,
            )
        formatted = ", ".join(finding.label for finding in redaction.residual_findings)
        raise ValueError(f"residual phi risk: {formatted}")

    episode = _build_draft_episode(episode_id=episode_id, title=title, redacted_text=redaction.clean_text)
    draft_episode_path.write_text(episode.model_dump_json(indent=2) + "\n", encoding="utf-8")
    _write_redaction_report(redaction_report_path, redaction, status="prepared")
    return ConstructedInputArtifacts(
        out_dir=output_dir,
        redacted_input_path=redacted_input_path,
        redaction_report_path=redaction_report_path,
        draft_episode_path=draft_episode_path,
        quarantined=False,
    )


def _write_redaction_report(path: Path, result: RedactionResult, *, status: str) -> None:
    report = RedactionReport(
        status=status,
        redaction_count=len(result.findings),
        findings=[asdict(finding) for finding in result.findings],
        residual_findings=[asdict(finding) for finding in result.residual_findings],
    )
    path.write_text(report.model_dump_json(indent=2) + "\n", encoding="utf-8")


def _build_draft_episode(*, episode_id: str, title: str, redacted_text: str) -> DecisionEpisode:
    actor = Actor(actor_id="reviewer_001", actor_type=ActorType.HUMAN, role="constructing reviewer")
    facts = _split_constructed_facts(redacted_text)
    return DecisionEpisode(
        episode_id=episode_id,
        title=title,
        domain="emergency_department_disposition_replay",
        decision_point_type=DecisionPointType.OTHER_ED_DISPOSITION_REVIEW,
        case_syntheticity=CaseSyntheticity.DEIDENTIFIED_STYLE_SYNTHETIC,
        governance_question="Was the disposition posture warranted at the decision time given only the information then available?",
        forbidden_use_notice="Constructed local governance review draft. Not for patient care, orders, diagnosis, treatment, or disposition instructions.",
        description="Reviewer-editable draft generated from redacted constructed input. Facts require reviewer approval before analysis.",
        actors=[actor],
        timepoints=[
            _timeline_state(
                RequiredTimepoint.T0_TRIAGE,
                0,
                "Constructed input intake",
                facts[:1],
                posture_category=PlanCategory.UNCLEAR,
                assertiveness=Assertiveness.LOW,
            ),
            _timeline_state(
                RequiredTimepoint.T1_INITIAL_WORKUP,
                1,
                "Constructed initial information",
                facts[1:2],
                posture_category=PlanCategory.UNCLEAR,
                assertiveness=Assertiveness.LOW,
            ),
            _timeline_state(
                RequiredTimepoint.T2_POST_TREATMENT_REASSESSMENT,
                2,
                "Constructed reassessment information",
                facts[2:3],
                posture_category=PlanCategory.UNCLEAR,
                assertiveness=Assertiveness.LOW,
            ),
            _timeline_state(
                RequiredTimepoint.T3_DISPOSITION_DECISION,
                3,
                "Constructed decision-time review",
                facts[3:],
                posture_category=PlanCategory.UNCLEAR,
                assertiveness=Assertiveness.LOW,
                include_gap=True,
            ),
            _timeline_state(
                RequiredTimepoint.T4_FOLLOW_UP_OR_OUTCOME,
                4,
                "Hidden follow-up placeholder",
                [
                    Fact(
                        fact_id="constructed_hidden_future_placeholder",
                        text="No outcome fact is supplied in this constructed draft.",
                        source_type=SourceType.UNKNOWN,
                        verification_status=VerificationStatus.UNKNOWN_PROVENANCE,
                        information_bucket=InformationBucket.UNKNOWABLE_NOW,
                        decision_criticality=0.0,
                        source_refs=[],
                    )
                ],
                posture_category=PlanCategory.UNCLEAR,
                assertiveness=Assertiveness.LOW,
            ),
        ],
        expected_outputs=ExpectedOutputs(
            expected_final_posture=Posture.HUMAN_REVIEW_REQUIRED,
            covered_case_patterns=[CasePattern.MATERIAL_MISSING_INPUT],
            expected_material_gaps=["constructed_review_required"],
            expected_future_leakage_blocked=True,
        ),
    )


def _split_constructed_facts(redacted_text: str) -> list[Fact]:
    chunks = [chunk.strip() for chunk in redacted_text.replace("\n", " ").split(".") if chunk.strip()]
    if not chunks:
        chunks = ["Constructed input did not contain a usable sentence and requires reviewer completion"]
    facts: list[Fact] = []
    for index, chunk in enumerate(chunks[:4], start=1):
        facts.append(
            Fact(
                fact_id=f"constructed_fact_{index:03d}",
                text=chunk + ".",
                source_type=SourceType.HUMAN_AUTHORED_NOTE,
                verification_status=VerificationStatus.UNVERIFIED_HUMAN_REPORTED,
                information_bucket=InformationBucket.KNOWN_BUT_WEAK,
                decision_criticality=0.5,
                source_refs=["redacted_constructed_input"],
            )
        )
    while len(facts) < 4:
        next_index = len(facts) + 1
        facts.append(
            Fact(
                fact_id=f"constructed_fact_{next_index:03d}",
                text="Reviewer completion required for this timepoint.",
                source_type=SourceType.UNKNOWN,
                verification_status=VerificationStatus.UNKNOWN_PROVENANCE,
                information_bucket=InformationBucket.KNOWABLE_BUT_UNKNOWN,
                decision_criticality=0.4,
                source_refs=["redacted_constructed_input"],
            )
        )
    return facts


def _timeline_state(
    timepoint: RequiredTimepoint,
    sequence_index: int,
    time_label: str,
    facts: list[Fact],
    *,
    posture_category: PlanCategory,
    assertiveness: Assertiveness,
    include_gap: bool = False,
) -> TimelineState:
    gaps = []
    if include_gap:
        gaps.append(
            InformationGap(
                gap_id="constructed_review_required",
                description="Reviewer must confirm timepoint assignment, missing inputs, therapy response, and follow-up feasibility before analysis.",
                gap_type="reviewer_approval_required",
                knowability=Knowability.KNOWABLE_NOW,
                time_to_obtain_hours=0.25,
                burden=Burden.LOW,
                decision_relevance_prior=0.8,
                candidate_input_mapping="review and approve structured episode",
            )
        )

    return TimelineState(
        timepoint_id=timepoint,
        sequence_index=sequence_index,
        time_label=time_label,
        available_facts=facts,
        information_gaps=gaps,
        pending_information=[],
        offered_therapies=[],
        therapy_response_observations=[],
        proposed_disposition_posture_under_review=ProposedDispositionPosture(
            posture_under_review_id=f"constructed_posture_{sequence_index}",
            stated_plan_category=posture_category,
            assertiveness=assertiveness,
            source_actor="reviewer_001",
            rationale_available_at_time="Draft intake placeholder pending reviewer approval.",
            known_constraints=["constructed draft", "reviewer approval required"],
        ),
        follow_up_feasibility=FollowUpFeasibility(),
        hidden_future_facts=[],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare constructed Sentinel input for reviewer-controlled analysis.")
    parser.add_argument("--input", required=True, help="Path to constructed or approved deidentified text input.")
    parser.add_argument("--out", required=True, help="Output directory for prepared artifacts.")
    parser.add_argument("--episode-id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--quarantine-on-residual", action="store_true")
    args = parser.parse_args()

    artifacts = prepare_constructed_input(
        input_path=args.input,
        out_dir=args.out,
        episode_id=args.episode_id,
        title=args.title,
        quarantine_on_residual=args.quarantine_on_residual,
    )
    status = "quarantined" if artifacts.quarantined else "prepared"
    print(f"status={status} out={artifacts.out_dir}")


if __name__ == "__main__":
    main()
