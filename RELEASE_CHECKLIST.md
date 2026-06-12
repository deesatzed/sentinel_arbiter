# RELEASE_CHECKLIST.md

## Release Scope

Local-only Sentinel clinician-review demo for synthetic and constructed/deidentified-style inputs. Scope includes the stdlib local reviewer console, deterministic preprocessing, methodology explorer, grouped ensemble contribution review, summary-first result page, deeper-dive artifacts, rendered-HTML UX verification, and optional OpenRouter comparison status.

This is not a production release, clinical-use release, PHI-ready release, or regulatory release.

## Go / No-Go Decision

Conditional Go for local deterministic demo use with synthetic or constructed/deidentified-style data only.

No-Go for real clinical, prospective, PHI, production, patient-facing, or autonomous clinical decision use.

## Checklist

| Area | Status | Evidence | Notes |
|---|---|---|---|
| Build | PASS | `python3 -m pip install -e . --dry-run --no-deps` | Local package metadata is installable without pulling dependencies in dry-run mode. |
| Tests | PASS | `python3 -m pytest -q` | Must be rerun before claiming final goal completion. |
| Lint/Typecheck | PARTIAL | `git diff --check` | No dedicated lint/typecheck tool is configured. |
| Security | CONDITIONAL | `.env` is gitignored; secret grep required by `GOAL.md` | No auth, network hardening, or production controls. |
| Privacy | CONDITIONAL | Redaction and residual-risk gates; raw input not copied into review artifacts | Not PHI-ready; use constructed/deidentified-style text only. |
| Environment Variables | PASS FOR LOCAL DEMO | Deterministic path requires no secrets | OpenRouter comparison needs local `.env`; secrets must not be committed or printed. |
| Documentation | IN PROGRESS | `README.md`, `docs/18_deterministic_poc_status.md`, `docs/22_local_app_ux_verification.md` | README explains run/use/interpretation boundaries. |
| Error Handling | PARTIAL | HTTP validation errors and quarantine path | Local demo handles common validation failures; not production-grade. |
| Logging | PARTIAL | Artifact hashes, approval traces, manifests, receipts | No centralized production logging. |
| Rollback | PASS FOR LOCAL DEMO | Git history and generated artifact paths | Revert app/docs changes and regenerate reports if needed. |

## Known Blockers

- Not approved for real clinical, prospective, patient-facing, or production use.
- No reviewer authentication or multi-user session model.
- No PHI retention, access-control, audit, or deletion policy.
- No production signing or key management.
- No clinical calibration of scoring constants.
- No formal human-factors study.
- Browser screenshot capture is not yet required if deterministic rendered-HTML verification passes.

## Accepted Risks

- The local demo uses deterministic fixture-field logic, not clinically calibrated evidence.
- Structured clinical sections are reviewer-facing aids; the advanced JSON remains the canonical structured payload for this milestone.
- OpenRouter model output is comparison-only and may be absent or skipped.
- Local artifacts may contain redacted constructed text and should stay out of production systems.

## Required Fixes Before Release

For local demo completion:

- Keep all `GOAL.md` proof commands passing.
- Keep `validation/reports/ux_render_verification.json` all-pass for the console UX.
- Keep the safety-boundary and no-secret grep checks clean.
- Regenerate `docs/21_goal_completion_audit.md` and `validation/reports/goal_completion_audit.json` for `clinician_review_console_v1`.

Before any real clinical/prospective/production release:

- Institutional governance approval.
- Privacy/security architecture and PHI policy.
- Authentication, access control, retention, and audit logs.
- Clinical safety validation with qualified reviewers.
- Regulatory analysis.
- Prospective validation protocol with stop rules.
- Bias, subgroup, and failure-mode analysis.
- Incident response, rollback, and monitoring procedures.

## Rollback Plan

1. Stop the local app process.
2. Preserve any local artifacts needed for audit.
3. Revert the local app/docs/report changes in git.
4. Regenerate deterministic reports from the last known-good commit.
5. Re-run `python3 -m pytest -q`, `PYTHONPATH=src python3 -m sentinel_workbench.ux_verification`, and `git diff --check`.
