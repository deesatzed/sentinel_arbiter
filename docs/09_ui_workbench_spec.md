# 09 — UI Workbench Spec

## UI purpose

The UI should make the methodology visible. It is not a chat UI. It is a governance review console.

## Page 1 — Case Library

Displays available synthetic/replay cases.

Fields:

- case id,
- artifact type,
- decision type,
- number of timepoints,
- expected challenge,
- last run status,
- receipt count.

Actions:

- open case,
- run Sentinel,
- view receipts,
- export report.

## Page 2 — Timeline Replay

Displays timepoint slider.

At each timepoint:

- known facts,
- known-but-weak facts,
- knowable gaps,
- pending info,
- proposed action,
- hidden future facts indicator.

Must clearly label that future information is unavailable to Sentinel at that timepoint.

## Page 3 — Information Gap Map

Displays gaps and relevance.

Columns:

- gap,
- bucket,
- decision relevance,
- expected posture shift,
- knowability,
- burden,
- urgency,
- status.

## Page 4 — Two-Clock / Risk Horizon Panel

Displays:

- harm clock,
- information clock,
- recoverability,
- future correction opportunity,
- decision weight,
- interpretation.

Example interpretation:

> Information likely arrives before harm window closes; proceed with recheck is more prudent than immediate escalation.

## Page 5 — AI-Provenance Panel

Displays decision-critical facts and source lineage.

Columns:

- fact,
- source type,
- verified status,
- unverified AI depth,
- primary source available,
- risk effect,
- confirmation recommendation.

## Page 6 — Next-Best-Input Panel

Displays ranked candidate inputs.

Columns:

- input,
- category,
- expected posture shift,
- preventability leverage,
- acquisition burden,
- time to obtain,
- decision weight gate result,
- recommendation.

## Page 7 — Role Review Panel

Displays role assessments.

Sections:

- prudent layperson,
- prudent provider,
- prudent healthcare AI,
- duty-to-inquire,
- risk horizon,
- evidence flow,
- red team,
- defense.

Should show structured outputs first, prose rationale second.

## Page 8 — Graph Inspector

Displays graph nodes and contribution to final posture.

Fields:

- node name,
- value,
- confidence,
- provenance tier,
- source role,
- sensitivity rank,
- version.

## Page 9 — Receipt Viewer

Displays:

- final posture,
- decision weight,
- timepoint,
- input hashes,
- prompt versions,
- model versions,
- evidence versions,
- graph version,
- node library version,
- signature placeholder.

Actions:

- export JSON,
- export Markdown summary,
- compare receipt runs.

## Page 10 — Evaluation Dashboard

Displays POC metrics:

- valid runs,
- schema failures,
- future leakage blocked,
- gap detection rate,
- next-best-input actionability,
- model-swap stability,
- receipt completeness.
