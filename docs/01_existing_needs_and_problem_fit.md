# 01 — Existing Needs and Problem Fit

Sentinel should be built only around needs that already exist. This document anchors the product to current governance pressure, transparency requirements, lifecycle assurance, and auditability.

## Need 1 — Healthcare organizations need AI governance evidence, not just policy

Joint Commission’s Responsible Use of AI in Healthcare certification recognizes organizations that demonstrate governance, safeguards, monitoring processes, and education for responsible health AI use. It explicitly focuses on organizational responsible use and governance, not certification of individual AI products or tools.

Reference:
- https://www.jointcommission.org/en-us/certification/responsible-use-of-ai-in-healthcare
- https://www.jointcommission.org/en-us/knowledge-library/news/2026-05-responsible-use-of-ai-in-healthcare-certification

**Sentinel fit:** Generates decision-level monitoring evidence and committee-ready receipts.

## Need 2 — Health systems need practical operational AI governance playbooks

CHAI announced comprehensive governance playbooks in May 2026, describing guidance across eight domains for transparent, trusted AI governance.

Reference:
- https://www.chai.org/news/coalition-for-health-ai-chai-releases-comprehensive-governance-playbooks-to

**Sentinel fit:** Converts governance into measured artifacts: information gaps, evidence sources, provenance, model versions, decision-warrant outputs, and drift signals.

## Need 3 — Transparency around predictive/AI decision support is now an explicit regulatory theme

ONC’s HTI-1 final rule advances interoperability, transparency, and use of electronic health information; its algorithm transparency provisions address predictive decision support interventions in certified health IT.

Reference:
- https://healthit.gov/regulations/hti-rules/hti-1-final-rule/
- https://www.federalregister.gov/documents/2024/01/09/2023-28857/health-data-technology-and-interoperability-certification-program-updates-algorithm-transparency-and

**Sentinel fit:** Produces local, decision-level transparency: what was considered, what was missing, what evidence was used, and why the final posture was selected.

## Need 4 — AI model lifecycle management requires explicit change and validation plans

FDA guidance on predetermined change control plans for AI-enabled device software functions reflects the broader need to support iterative AI improvement while maintaining assurance of safety and effectiveness.

Reference:
- https://www.fda.gov/regulatory-information/search-fda-guidance-documents/marketing-submission-recommendations-predetermined-change-control-plan-artificial-intelligence

**Sentinel fit:** Versioned graph, model versions, evidence staleness timers, node-library versions, and receipts preserve assurance across model changes.

## Need 5 — Agentic systems need traceability and observability

Modern agent frameworks now emphasize tracing, durable execution, state management, multi-agent orchestration, and evaluation support.

References:
- OpenAI Agents SDK: https://developers.openai.com/api/docs/guides/agents
- OpenAI tracing: https://openai.github.io/openai-agents-python/tracing/
- LangGraph: https://docs.langchain.com/oss/python/langgraph/overview
- Microsoft Agent Framework: https://learn.microsoft.com/en-us/agent-framework/overview/
- Google ADK: https://developers.googleblog.com/en/agent-development-kit-easy-to-build-multi-agent-applications/

**Sentinel fit:** Uses agent orchestration as infrastructure, but makes the durable product the schema, receipts, node graph, and evaluation harness.

## Product implication

The first customer-facing claim should be narrow and true:

> Sentinel helps healthcare AI governance teams create decision-level evidence that AI-assisted decisions were monitored for information sufficiency, risk horizon, evidence support, provenance reliability, and prudent-action warrant.

Do not claim clinical outcome improvement in the POC.
