# 03 — Sample Receipt Shape

This is illustrative. Codex should generate real receipts from runs.

```json
{
  "receipt_id": "receipt_case_001_T1_run_001",
  "episode_id": "case_001",
  "timepoint_id": "T1",
  "mode": "replay",
  "final_posture": "OBTAIN_SPECIFIC_INFORMATION_FIRST",
  "decision_weight": 0.78,
  "decision_weight_explanation": "Potential harm is near-term, recoverability is limited, and future correction opportunity is low unless a specific missing input is obtained now.",
  "information_state_summary": {
    "known_count": 4,
    "known_but_weak_count": 1,
    "knowable_but_unknown_count": 3,
    "pending_count": 1,
    "unknowable_now_count": 0,
    "material_gap_ids": ["gap_critical_1"]
  },
  "ai_provenance_warnings": [
    {
      "fact_id": "fact_summary_derived_1",
      "unverified_ai_depth": 2,
      "decision_criticality": 0.85,
      "recommendation": "Confirm from primary source before relying on this fact."
    }
  ],
  "next_best_inputs": [
    {
      "input_id": "input_1",
      "description": "Specific missing input that determines whether the proposed action is warranted.",
      "expected_posture_shift": 0.72,
      "burden": "low",
      "time_to_obtain_hours": 0.1,
      "recommendation": "Obtain before proceeding."
    }
  ],
  "role_disagreement_map": {
    "summary": "Prudent layperson and prudent healthcare AI thresholds exceed provider threshold; disagreement localizes to salient-danger recognition and missing confirmation.",
    "roles": {
      "prudent_layperson": "elevated concern",
      "prudent_provider": "moderate concern",
      "prudent_healthcare_ai": "defer until missing input confirmed"
    }
  },
  "graph_nodes": [
    {"node_name": "decision_weight", "value": 0.78, "confidence": 0.7, "evidence_tier": "tier_2"},
    {"node_name": "gap_decision_relevance", "value": 0.82, "confidence": 0.75, "evidence_tier": "tier_2"},
    {"node_name": "ai_provenance_risk", "value": 0.65, "confidence": 0.8, "evidence_tier": "tier_2"}
  ],
  "versions": {
    "graph_version": "0.1.0",
    "node_library_version": "0.1.0",
    "prompt_versions": {
      "prudent_ai": "0.1.0",
      "duty_to_inquire": "0.1.0"
    },
    "model_versions": {
      "default_role_model": "placeholder"
    },
    "evidence_versions": {
      "manual_poc_evidence": "0.1.0"
    }
  },
  "signature": "placeholder_hmac_signature",
  "created_at": "2026-06-11T00:00:00Z"
}
```
