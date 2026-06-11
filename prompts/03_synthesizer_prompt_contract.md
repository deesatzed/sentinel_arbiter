# 03 — Synthesizer / Normalizer Prompt Contract

## Purpose

The synthesizer does not decide the final posture. It converts role-agent and EvidenceFlow outputs into normalized graph node proposals.

## Required behavior

- Validate allowed finding types.
- Identify duplicate findings.
- Map each finding to graph node targets.
- Normalize confidence.
- Downgrade unsupported findings.
- Flag contradictions.
- Preserve disagreement.
- Reject future leakage.

## Required output

```json
{
  "node_proposals": [
    {
      "node_name": "gap_decision_relevance",
      "value": 0.82,
      "confidence": 0.7,
      "evidence_tier": "tier_2",
      "source_roles": ["duty_to_inquire", "prudent_provider"],
      "source_refs": ["gap_1"],
      "notes": "Specific gap likely changes posture."
    }
  ],
  "rejected_findings": [],
  "disagreement_map": {},
  "future_leakage_flags": []
}
```

## Forbidden behavior

- Do not output final posture.
- Do not average disagreement away.
- Do not silently accept unsupported estimates.
- Do not invent evidence sources.
