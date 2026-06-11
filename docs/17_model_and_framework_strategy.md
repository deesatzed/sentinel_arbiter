# 17 — Model and Framework Strategy

## Principle

The durable product is not the agent framework. The durable product is:

- DecisionEpisode schema,
- prudence calculus,
- role contracts,
- EvidenceFlow contracts,
- node library,
- graph calculations,
- receipts,
- validation harness.

## POC strategy

Start with explicit Python orchestration and static role outputs. Add LLM calls behind interfaces only after deterministic pathway works.

## Why

If the first build begins with a complex multi-agent framework, failures will be hard to diagnose. The POC must prove the graph and receipt methodology before orchestration complexity.

## Framework-neutral agent interface

Every agent implementation should expose:

```text
run(input: RoleAgentInput) -> RoleAssessment
```

Every EvidenceFlow implementation should expose:

```text
run(input: EvidenceFlowInput) -> EvidenceFlowResult
```

## Later framework options

- OpenAI Agents SDK: useful for model/tool orchestration and tracing.
- LangGraph: useful for durable, stateful, long-running workflows and human-in-the-loop review.
- Microsoft Agent Framework: useful for enterprise multi-agent orchestration and telemetry.
- Google ADK: useful for graph-style multi-agent workflows and evaluation.

## Model-swap requirement

The same case should be runnable with:

- static role outputs,
- model A,
- model B,
- model A with prompt version change.

The receipt must record model and prompt versions.

## Evaluation requirement

Model changes should be judged at two levels:

1. role-output stability,
2. graph-level posture stability.

If role outputs vary but graph posture stays stable, the method is robust.

If graph posture changes, receipt should show which node shifted.
