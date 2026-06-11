# 10 — API Contract

This is a planning-level API contract for Codex. It is not implementation code.

## Core endpoints

### POST /episodes

Create a DecisionEpisode.

Request:

```json
{
  "episode": "DecisionEpisode"
}
```

Response:

```json
{
  "episode_id": "string",
  "status": "created"
}
```

### GET /episodes

List episodes.

### GET /episodes/{episode_id}

Retrieve an episode.

### POST /sentinel/run

Run Sentinel at one or more timepoints.

Request:

```json
{
  "episode_id": "string",
  "timepoint_ids": ["T0", "T1"],
  "mode": "replay",
  "config": {
    "role_set": "poc_default",
    "graph_version": "0.1.0",
    "evidenceflow_set": "poc_default",
    "deterministic": true
  }
}
```

Response:

```json
{
  "run_id": "string",
  "receipt_ids": ["string"],
  "summary": {
    "highest_decision_weight": 0.74,
    "flagged_timepoints": ["T1"],
    "final_postures": {
      "T0": "PROCEED_WITH_SAFETY_NET_OR_RECHECK",
      "T1": "OBTAIN_SPECIFIC_INFORMATION_FIRST"
    }
  }
}
```

### GET /receipts/{receipt_id}

Return SentinelReceipt.

### POST /evidenceflows/run

Run an EvidenceFlow for a timepoint.

Request:

```json
{
  "episode_id": "string",
  "timepoint_id": "string",
  "flow_type": "NEXT_BEST_INPUT",
  "candidate_inputs": []
}
```

### POST /evaluation/run

Run all POC cases through evaluation metrics.

Request:

```json
{
  "case_set": "poc_minimal",
  "graph_version": "0.1.0",
  "model_profile": "default"
}
```

Response:

```json
{
  "evaluation_id": "string",
  "metrics": {
    "receipt_completeness": 1.0,
    "schema_validity_rate": 1.0,
    "future_leakage_failures": 0,
    "next_best_input_actionability": 0.8
  }
}
```

## Internal service boundaries

Recommended internal modules:

```text
EpisodeService
TimelineService
InformationPartitionService
RoleAgentService
EvidenceFlowService
NodeNormalizerService
PrudenceGraphService
ReceiptService
EvaluationService
```

## Error handling principles

- Malformed input returns structured validation errors.
- EvidenceFlow failure lowers evidence confidence; it does not fabricate.
- Agent schema failure triggers retry once, then marks role unavailable.
- High decision weight plus missing role/evidence input routes to human review.
- Receipt generation failure blocks completion.
