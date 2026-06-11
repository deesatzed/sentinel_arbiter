# 12 — Security, Privacy, Governance

## POC data constraint

Use only synthetic or deidentified-style replay data. No live patient data. No named clinical site. No proprietary clinical documents.

## Privacy principles

- Do not store PHI in POC.
- Do not send sensitive data to external services.
- Use synthetic case ids.
- Do not include institution names in logs, prompts, sample files, or UI.

## Security principles

- Store secrets outside repository.
- Do not hard-code model API keys.
- Log model versions and prompt versions, not raw secrets.
- Receipts should include hashes, not sensitive raw content, where possible.

## Governance principles

- Every graph version is immutable once used in a receipt.
- Prompt changes create new prompt versions.
- Evidence source changes create new evidence source versions.
- Node-library changes create new node-library versions.
- Model changes are recorded and evaluated for stability.

## Clinical safety principles

- POC is not for production clinical decision-making.
- UI must show “Planning / governance POC — not for patient care.”
- No automated clinical actions.
- No live recommendations to patients.
- Human review required for high-stakes interpretations.

## Receipt integrity

POC can use placeholder HMAC signing with local key management. Longer term should support:

- tamper-evident hash chains,
- key rotation,
- signed model/prompt/graph manifests,
- receipt export audit logs.
