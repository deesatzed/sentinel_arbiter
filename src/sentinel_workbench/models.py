from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RequiredTimepoint(StrEnum):
    T0_TRIAGE = "T0_triage"
    T1_INITIAL_WORKUP = "T1_initial_workup"
    T2_POST_TREATMENT_REASSESSMENT = "T2_post_treatment_reassessment"
    T3_DISPOSITION_DECISION = "T3_disposition_decision"
    T4_FOLLOW_UP_OR_OUTCOME = "T4_follow_up_or_outcome"


REQUIRED_CURRENT_TIMEPOINTS = (
    RequiredTimepoint.T0_TRIAGE,
    RequiredTimepoint.T1_INITIAL_WORKUP,
    RequiredTimepoint.T2_POST_TREATMENT_REASSESSMENT,
    RequiredTimepoint.T3_DISPOSITION_DECISION,
)


class DecisionPointType(StrEnum):
    ADMISSION_VS_NON_INPATIENT_ALTERNATIVE = "admission_vs_non_inpatient_alternative"
    OBSERVATION_VS_HOME_PLAN = "observation_vs_home_plan"
    CONTINUED_ED_MANAGEMENT_VS_DISPOSITION = "continued_ed_management_vs_disposition"
    OTHER_ED_DISPOSITION_REVIEW = "other_ed_disposition_review"


class CaseSyntheticity(StrEnum):
    SYNTHETIC = "synthetic"
    DEIDENTIFIED_STYLE_SYNTHETIC = "deidentified_style_synthetic"


class ActorType(StrEnum):
    HUMAN = "human"
    AI = "ai"
    SYSTEM = "system"
    PATIENT = "patient"
    OTHER = "other"


class SourceType(StrEnum):
    PRIMARY_PATIENT_STATEMENT = "primary_patient_statement"
    PRIMARY_OBSERVATION = "primary_observation"
    STRUCTURED_DATA = "structured_data"
    HUMAN_AUTHORED_NOTE = "human_authored_note"
    AI_GENERATED_TEXT = "ai_generated_text"
    AI_SUMMARY_OF_TEXT = "ai_summary_of_text"
    AI_INFERENCE = "ai_inference"
    EXTERNAL_EVIDENCE = "external_evidence"
    UNKNOWN = "unknown"


class VerificationStatus(StrEnum):
    VERIFIED_PRIMARY = "verified_primary"
    VERIFIED_DETERMINISTIC = "verified_deterministic"
    VERIFIED_HUMAN = "verified_human"
    UNVERIFIED_AI_DERIVED = "unverified_ai_derived"
    UNVERIFIED_HUMAN_REPORTED = "unverified_human_reported"
    UNKNOWN_PROVENANCE = "unknown_provenance"
    CONFLICTING = "conflicting"
    STALE = "stale"


class InformationBucket(StrEnum):
    KNOWN = "known"
    KNOWN_BUT_WEAK = "known_but_weak"
    KNOWABLE_BUT_UNKNOWN = "knowable_but_unknown"
    PENDING = "pending"
    UNKNOWABLE_NOW = "unknowable_now"


class Burden(StrEnum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class Knowability(StrEnum):
    KNOWABLE_NOW = "knowable_now"
    KNOWABLE_LATER = "knowable_later"
    PENDING = "pending"
    UNKNOWABLE_NOW = "unknowable_now"


class PlanCategory(StrEnum):
    HOSPITAL_BASED_MONITORING_OR_TREATMENT = "hospital_based_monitoring_or_treatment"
    NON_INPATIENT_PLAN = "non_inpatient_plan"
    OBSERVATION_OR_RECHECK_PLAN = "observation_or_recheck_plan"
    DEFER_PENDING_INFORMATION = "defer_pending_information"
    UNCLEAR = "unclear"


class Assertiveness(StrEnum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    DEFINITIVE = "definitive"


class TherapyReceiptStatus(StrEnum):
    YES = "yes"
    NO = "no"
    PARTIAL = "partial"
    UNKNOWN = "unknown"


class TherapyResponse(StrEnum):
    IMPROVED = "improved"
    NO_CLEAR_CHANGE = "no_clear_change"
    WORSE = "worse"
    NOT_REASSESSED = "not_reassessed"
    UNKNOWN = "unknown"


class Reliability(StrEnum):
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    UNKNOWN = "unknown"


class AccessStatus(StrEnum):
    CLEAR = "clear"
    UNCLEAR = "unclear"
    LIMITED = "limited"
    UNKNOWN = "unknown"


class Posture(StrEnum):
    PROCEED = "PROCEED"
    PROCEED_WITH_UNCERTAINTY_DISCLOSURE = "PROCEED_WITH_UNCERTAINTY_DISCLOSURE"
    PROCEED_WITH_SAFETY_NET_OR_RECHECK = "PROCEED_WITH_SAFETY_NET_OR_RECHECK"
    OBTAIN_SPECIFIC_INFORMATION_FIRST = "OBTAIN_SPECIFIC_INFORMATION_FIRST"
    PAUSE_AND_ESCALATE = "PAUSE_AND_ESCALATE"
    DO_NOT_PROCEED = "DO_NOT_PROCEED"
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"
    INDETERMINATE = "INDETERMINATE"


class CasePattern(StrEnum):
    MATERIAL_MISSING_INPUT = "material_missing_input_before_disposition"
    THERAPY_DOCUMENTED_IMPROVEMENT = "therapy_offered_documented_improvement"
    THERAPY_NONRESPONSE_OR_UNCLEAR = "therapy_offered_nonresponse_or_unclear_response"
    THERAPY_PLAUSIBLY_INDICATED_NOT_CONSIDERED = "therapy_plausibly_indicated_but_not_considered"
    HOME_PLAN_FEASIBILITY_PROBLEM = "discharge_home_plan_feasibility_problem"
    LIMITED_ADDED_VALUE = "admission_or_observation_limited_added_value"
    AI_DERIVED_OR_WEAK_FACT = "ai_derived_or_weakly_sourced_fact_driving_decision"


class Actor(StrictModel):
    actor_id: str
    actor_type: ActorType
    role: str | None = None


class Fact(StrictModel):
    fact_id: str
    text: str
    source_type: SourceType
    verification_status: VerificationStatus
    information_bucket: InformationBucket | None = None
    decision_criticality: float = Field(default=0.0, ge=0, le=1)
    ai_provenance_depth: int = Field(default=0, ge=0)
    source_refs: list[str] = Field(default_factory=list)


class InformationGap(StrictModel):
    gap_id: str
    description: str
    gap_type: str
    knowability: Knowability
    time_to_obtain_hours: float = Field(ge=0)
    burden: Burden
    decision_relevance_prior: float = Field(ge=0, le=1)
    candidate_input_mapping: str | None = None


class PendingInfo(StrictModel):
    pending_id: str
    description: str
    expected_time_hours: float = Field(ge=0)


class ProposedDispositionPosture(StrictModel):
    posture_under_review_id: str
    stated_plan_category: PlanCategory
    assertiveness: Assertiveness
    source_actor: str
    rationale_available_at_time: str
    known_constraints: list[str] = Field(default_factory=list)


class OfferedTherapy(StrictModel):
    therapy_id: str
    therapy_category: str
    offered_at_timepoint: RequiredTimepoint
    accepted_or_received: TherapyReceiptStatus
    response_observed: TherapyResponse
    response_timepoint: RequiredTimepoint | None = None
    response_source_refs: list[str] = Field(default_factory=list)
    response_reliability: Reliability = Reliability.UNKNOWN
    therapy_plausibly_indicated_but_not_considered: bool = False
    not_considered_rationale: str | None = None


class TherapyResponseObservation(StrictModel):
    observation_id: str
    therapy_id: str
    response_observed: TherapyResponse
    observed_at_timepoint: RequiredTimepoint
    source_refs: list[str] = Field(default_factory=list)
    reliability: Reliability = Reliability.UNKNOWN


class FollowUpFeasibility(StrictModel):
    follow_up_access: AccessStatus = AccessStatus.UNKNOWN
    home_support: AccessStatus = AccessStatus.UNKNOWN
    return_access: AccessStatus = AccessStatus.UNKNOWN
    barrier_facts: list[str] = Field(default_factory=list)
    barrier_source_refs: list[str] = Field(default_factory=list)
    barrier_reliability: Reliability = Reliability.UNKNOWN


class TimelineState(StrictModel):
    timepoint_id: RequiredTimepoint
    sequence_index: int = Field(ge=0)
    time_label: str
    available_facts: list[Fact] = Field(default_factory=list)
    information_gaps: list[InformationGap] = Field(default_factory=list)
    pending_information: list[PendingInfo] = Field(default_factory=list)
    offered_therapies: list[OfferedTherapy] = Field(default_factory=list)
    therapy_response_observations: list[TherapyResponseObservation] = Field(default_factory=list)
    proposed_disposition_posture_under_review: ProposedDispositionPosture
    follow_up_feasibility: FollowUpFeasibility = Field(default_factory=FollowUpFeasibility)
    hidden_future_facts: list[Fact] = Field(default_factory=list)


class ExpectedOutputs(StrictModel):
    expected_final_posture: Posture
    covered_case_patterns: list[CasePattern] = Field(min_length=1)
    expected_material_gaps: list[str] = Field(default_factory=list)
    expected_omission_flags: list[str] = Field(default_factory=list)
    expected_commission_flags: list[str] = Field(default_factory=list)
    expected_therapy_response_flags: list[str] = Field(default_factory=list)
    expected_next_best_information: list[str] = Field(default_factory=list)
    expected_future_leakage_blocked: bool = True


class DecisionEpisode(StrictModel):
    episode_id: str
    title: str
    domain: Literal["emergency_department_disposition_replay"]
    decision_point_type: DecisionPointType
    case_syntheticity: CaseSyntheticity
    governance_question: str
    forbidden_use_notice: str
    description: str
    actors: list[Actor] = Field(default_factory=list)
    timepoints: list[TimelineState] = Field(min_length=1)
    expected_outputs: ExpectedOutputs

    @model_validator(mode="after")
    def require_current_timepoints(self) -> "DecisionEpisode":
        present = {state.timepoint_id for state in self.timepoints}
        missing = [timepoint.value for timepoint in REQUIRED_CURRENT_TIMEPOINTS if timepoint not in present]
        if missing:
            raise ValueError(f"missing required timepoints: {', '.join(missing)}")
        return self
