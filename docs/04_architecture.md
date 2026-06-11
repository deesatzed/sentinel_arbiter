# 04 — Architecture

## Architectural stance

Sentinel is built as a stable decision-warrant substrate with swappable models, swappable evidence sources, and thin artifact adapters.

The architecture must preserve this boundary:

> Agents and LLMs structure inputs. The graph computes the verdict.

## High-level components

```text
Artifact Adapter
  ↓
DecisionEpisode Builder
  ↓
TimelineState Constructor
  ↓
Information Partition Engine
  ↓
Role Agent Swarm
  ↓
EvidenceFlow Engine
  ↓
Agent-to-Node Normalizer
  ↓
Prudence Graph / Monte Carlo Engine
  ↓
Posture + Decision Weight
  ↓
Receipt Generator
  ↓
Governance Workbench UI
```

## Component 1 — Artifact Adapter

Purpose: Convert different AI-assisted output types into a common DecisionEpisode.

POC adapters:

1. Clinical recommendation adapter.
2. Patient-facing response/triage adapter.
3. Care-management/follow-up plan adapter.
4. Agentic action request adapter.

The adapter should not contain domain logic. It should normalize input.

## Component 2 — DecisionEpisode Builder

Builds the central case object:

- episode id,
- actor list,
- artifact list,
- proposed decision/action,
- timeline states,
- facts,
- gaps,
- provenance sources,
- expected review mode.

## Component 3 — TimelineState Constructor

For POC replay mode, the timeline is explicit. Each state represents what is known at that step.

Key outputs:

- known facts,
- weak known facts,
- knowable unknowns,
- pending information,
- unknowable uncertainty,
- proposed action at that time.

## Component 4 — Information Partition Engine

Classifies every fact or gap into the five information buckets.

Must preserve:

- fact reliability,
- provenance category,
- AI-provenance depth,
- potential decision relevance,
- whether fact is pending or obtainable.

## Component 5 — Role Agent Swarm

Runs structured role assessments.

Initial POC roles:

- Prudent Layperson Agent
- Prudent Provider Agent
- Prudent Healthcare AI Agent
- Duty-to-Inquire Agent
- Risk Horizon Agent
- EvidenceFlow Agent
- Red Team Agent
- Defense Agent
- Graph Synthesizer / Normalizer

Each agent must return JSON conforming to `schemas/role_assessment.schema.json` or a role-specific extension.

## Component 6 — EvidenceFlow Engine

Runs reusable evidence tasks. It can be stubbed with manually curated evidence for POC or wired to external/reference systems later.

POC EvidenceFlows:

1. Guideline dependency flow.
2. Next-best-input/result-distribution flow.
3. Prudent AI conduct flow.
4. High-risk alternative flow.

## Component 7 — Agent-to-Node Normalizer

Critical rigor layer.

Purpose: Convert role assessments and EvidenceFlow outputs into graph nodes with typed values, confidence, provenance tier, and uncertainty distribution.

This layer must reject malformed, unsupported, or overconfident agent outputs.

## Component 8 — Prudence Graph

Computes:

- information sufficiency,
- duty-to-inquire strength,
- AI-provenance risk,
- risk horizon,
- decision weight,
- next-best-information ranking,
- prudence-standard thresholds,
- disagreement map,
- final posture.

Graph should support deterministic and stochastic operation:

- deterministic mode for POC debugging,
- Monte Carlo mode for uncertainty propagation.

## Component 9 — Receipt Generator

Creates reconstructable SentinelReceipt.

Receipt includes:

- input hashes,
- prompt versions,
- model versions,
- evidence source versions,
- graph version,
- node library version,
- role outputs,
- final posture,
- decision weight,
- signature.

## Component 10 — Governance Workbench UI

POC UI pages:

1. Case library.
2. Timeline replay.
3. Information-gap map.
4. Risk horizon/two-clock panel.
5. AI-provenance depth panel.
6. Next-best-input ranking panel.
7. Role disagreement panel.
8. Graph node inspector.
9. Receipt viewer/export.
10. Evaluation dashboard.

## Recommended POC technical stack

This is a recommendation, not a requirement.

Backend:

- Python
- FastAPI
- Pydantic v2
- JSON schema export
- SQLite for local POC persistence
- NetworkX or simple custom DAG for graph representation
- NumPy/SciPy for Monte Carlo if needed

Agent orchestration:

- Start simple with explicit orchestrator functions.
- Keep role agent contracts framework-neutral.
- Later ports can use OpenAI Agents SDK, LangGraph, Microsoft Agent Framework, or Google ADK.

Frontend:

- Streamlit for fastest POC, or Next.js if aiming for product-quality UI.
- For Codex POC, Streamlit is acceptable if speed matters.

Testing:

- pytest
- snapshot tests for receipts
- schema validation tests
- deterministic replay tests
- golden-case tests

## Why not start with full agent framework?

Contrarian reason: framework complexity can mask methodology failures.

POC should prove the hard part:

- structured outputs,
- node conversion,
- graph verdict,
- receipts,
- evaluation.

Once that works, agent orchestration can be upgraded.
