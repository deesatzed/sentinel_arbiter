# 16 — Repository Structure and Work Packages

## Recommended repository structure

```text
sentinel-workbench/
  README.md
  pyproject.toml
  .env.example
  sentinel_workbench/
    __init__.py
    models/
      decision_episode.py
      role_assessment.py
      evidenceflow_result.py
      sentinel_receipt.py
    services/
      episode_service.py
      replay_service.py
      information_partition_service.py
      provenance_service.py
      evidenceflow_service.py
      role_agent_service.py
      node_normalizer_service.py
      prudence_graph_service.py
      receipt_service.py
      evaluation_service.py
    graph/
      nodes.py
      node_library.py
      scoring.py
      sensitivity.py
    ui/
      app.py
      pages/
    prompts/
      registry.py
      templates/
    adapters/
      base.py
      clinical_recommendation.py
      patient_facing_response.py
      care_management_plan.py
      agentic_action_request.py
    utils/
      hashing.py
      versioning.py
      validation.py
  data/
    cases/
    evidenceflows/
    role_assessments/
    receipts/
    expected_outputs/
  tests/
    test_models.py
    test_replay.py
    test_future_leakage.py
    test_information_partition.py
    test_provenance.py
    test_evidenceflows.py
    test_node_normalizer.py
    test_prudence_graph.py
    test_receipts.py
    test_evaluation.py
```

## Work package A — Core schemas

Depends on: none.

Includes:

- data models,
- validation,
- JSON fixture loading.

## Work package B — Replay + information state

Depends on: A.

Includes:

- timeline replay,
- information buckets,
- future guard.

## Work package C — Provenance + EvidenceFlows

Depends on: A, B.

Includes:

- AI-provenance depth,
- static EvidenceFlow outputs,
- candidate input tables.

## Work package D — Role outputs + normalizer

Depends on: A, B, C.

Includes:

- static role outputs,
- optional LLM role adapter,
- schema validation,
- node proposals.

## Work package E — Graph + receipts

Depends on: D.

Includes:

- prudence graph,
- posture output,
- decision weight,
- receipt generation.

## Work package F — UI + evaluation

Depends on: E.

Includes:

- workbench UI,
- metrics runner,
- demo reports.
