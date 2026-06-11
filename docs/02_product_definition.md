# 02 — Product Definition

## Name

Working name: **Sentinel Governance Workbench**
Parent architecture: ARBITER substrate

## One-line product definition

Sentinel is a governance workbench that evaluates whether an AI-assisted healthcare decision is warranted yet, based on the current information state, risk horizon, evidence support, provenance reliability, and prudent-actor expectations.

## What Sentinel is

- A shadow-mode/replay-mode governance tool.
- A decision-warrant engine.
- A structured peer-review workbench.
- A receipt generator for AI governance and quality monitoring.
- A method for ranking decision-relevant missing information.
- A way to detect reliance on unverified AI-derived evidence.
- A system that makes role disagreement visible instead of forcing false consensus.

## What Sentinel is not

- Not a diagnosis app.
- Not a medical knowledge chatbot.
- Not a clinical reference replacement.
- Not a bedside alert engine in the POC.
- Not an autonomous clinician.
- Not a generic multi-agent debate product.
- Not a validator of any one AI vendor.
- Not a narrow documentation checker.

## Target POC buyer/user

Primary POC user:

- AI governance committee
- QAPI / quality / safety group
- clinical informatics leadership
- risk / compliance reviewer
- model oversight group

Secondary later users:

- clinical department reviewers
- legal/risk teams
- peer review committees
- vendor evaluation groups
- payer/utilization governance teams

## POC job-to-be-done

When reviewing an AI-assisted decision episode, the user wants to know:

1. Was the proposed decision warranted at the time?
2. What information was known?
3. What decision-relevant gaps existed?
4. Which missing input would most change the posture?
5. How soon could harm occur if the decision was wrong?
6. Was there time to correct course later?
7. Did the decision depend on unverified AI-derived information?
8. What would different prudent standards recommend?
9. Is the output suitable for committee review?
10. Can the decision be reconstructed later?

## Core user promise

Sentinel turns AI governance from policy language into decision-level evidence.

## POC scope

The POC must support:

- Synthetic/deidentified-style replay cases.
- Multiple artifact types through adapters.
- Information-state partitioning.
- Risk horizon and two-clock comparison.
- Decision weight calculation.
- AI-provenance depth tracking.
- Next-best-information ranking.
- Role-agent structured assessments.
- Graph-based posture computation.
- Signed receipt generation.
- Workbench UI for reviewing results.

## POC non-scope

The POC does not need:

- EHR integration.
- Live patient data.
- Automated ordering.
- Clinical deployment.
- Billing integration.
- Legal discovery export.
- Full guideline corpus.
- Full clinical specialty coverage.
- Final regulatory interpretation.

## POC success statement

The POC succeeds if a knowledgeable governance reviewer can inspect a case and say:

> This gives me a clearer, more auditable view of whether an AI-assisted decision was warranted than a normal AI output, model score, or free-text review.
