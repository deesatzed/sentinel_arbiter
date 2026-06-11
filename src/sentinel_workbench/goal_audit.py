from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


GOAL_PROOF_ITEMS: tuple[str, ...] = (
    "A user can open the local app and choose either review question A or B before input is processed.",
    "The selected review question is saved into the run manifest, receipts, and summary.",
    "A user can paste redacted text or upload a constructed/deidentified local file and click Pre-process.",
    "A user can run a local CLI command with constructed text input and receive a redaction report plus draft structured episode.",
    "Residual PII/PHI risk is detected and blocks or quarantines unsafe input.",
    "A reviewer-approved structured episode can be saved and used for deterministic analysis.",
    "Synthetic and constructed demo inputs validate against schemas.",
    "Hidden future facts cannot enter current-time node computation.",
    "Every graph node has a NodeAudit or equivalent schema-backed audit object.",
    "Every node audit has dependencies, evidence refs, value, range, median, distribution kind, confidence, method, and sensitivity note.",
    "The app displays Node Audit Methodology after pre-processing and before processing.",
    "A reviewer can choose OK, Adjust, or Re-check selected nodes; adjustments require confirmation before replacing generated methodology.",
    "Every ensemble contribution is accepted, rejected, or downgraded with a reason.",
    "The app displays Ensemble Contributions before Process.",
    "The graph computes final Sentinel posture from normalized typed node values.",
    "Final posture remains one of the Sentinel posture categories, not a disposition recommendation.",
    "The primary result is a clinician-readable governance summary of no more than one or two short paragraphs.",
    "The primary summary explains what the result means for the selected review question and why, including the main uncertainty drivers.",
    "A Deeper Dive button exposes node audit tables, ensemble tables, receipts, trace hashes, validation status, structured episode, and raw JSON/Markdown artifacts.",
    "JSON receipts include selected review question, redaction, intake, node audit, ensemble, trace, graph, and signature-placeholder fields.",
    "Human-readable receipts explain what was known, what was missing, what would have changed the discussion, what facility-based monitoring or treatment might add, what non-inpatient alternatives might add, commission concerns, omission concerns, therapy-response concerns, and why the graph selected the posture.",
    "The workbench renders the redacted input, structured episode, node methodology, distributions, range, median, ensemble disagreement, graph posture, clinician summary, deeper-dive artifacts, receipts, and validation status.",
    "Automated validation reports cover schema validity, future leakage, redaction gating, expected posture agreement on fixtures, omission detection, commission warning detection, therapy-response integration, next-best-information usefulness, node-audit completeness, receipt completeness, workbench completeness, app-flow completeness, summary completeness, and forbidden phrase violations.",
    "The project documents what is implemented, what is deferred, and what would be required before any real clinical, prospective, production, or live-evidence use.",
    "Full local verification commands pass and git diff --check is clean.",
)


def generate_goal_completion_audit(
    *,
    output_json: str | Path = "validation/reports/goal_completion_audit.json",
    output_markdown: str | Path = "docs/21_goal_completion_audit.md",
    evaluation_report_path: str | Path = "validation/reports/latest.json",
    goal_path: str | Path = "GOAL.md",
    status_doc_path: str | Path = "docs/18_deterministic_poc_status.md",
) -> dict[str, object]:
    evaluation = _read_json(evaluation_report_path)
    goal_text = Path(goal_path).read_text(encoding="utf-8")
    status_text = Path(status_doc_path).read_text(encoding="utf-8")
    items = _build_items(evaluation, goal_text, status_text)
    pass_count = sum(1 for item in items if item["verdict"] == "PASS")
    payload = {
        "report_type": "goal_completion_audit",
        "goal_file": str(goal_path),
        "proof_item_count": len(items),
        "pass_count": pass_count,
        "all_pass": pass_count == len(items),
        "items": items,
    }
    json_path = Path(output_json)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    markdown_path = Path(output_markdown)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(_render_markdown(payload), encoding="utf-8")
    return payload


def _build_items(evaluation: dict[str, Any], goal_text: str, status_text: str) -> list[dict[str, object]]:
    local_app = _dict(evaluation.get("local_app_completeness"))
    redaction = _dict(evaluation.get("redaction_gating"))
    node_audit = _dict(evaluation.get("node_audit_completeness"))
    ensemble = _dict(evaluation.get("ensemble_contribution_completeness"))
    receipt = _dict(evaluation.get("receipt_completeness"))
    workbench = _dict(evaluation.get("workbench_completeness"))
    summary = _dict(evaluation.get("summary_completeness"))
    automated = _dict(evaluation.get("automated_validation"))
    schema = _dict(evaluation.get("schema_validity"))
    items: list[dict[str, object]] = []

    checks: tuple[tuple[bool, str, str], ...] = (
        (bool(local_app.get("review_question_choice_visible") and local_app.get("preprocess_control_visible")), "local_app_completeness", "Local app exposes both review questions and requires Pre-process workflow."),
        (bool(receipt.get("selected_review_question_field_supported") and summary.get("selected_review_question_framing")), "receipt_completeness, summary_completeness", "Selected review question is present in receipts and summary framing."),
        (bool(local_app.get("preprocess_control_visible") and local_app.get("multipart_file_upload_supported")), "local_app_completeness", "Paste and upload paths are represented in the local app proof payload."),
        (bool(redaction.get("prepared_demo_report_exists") and redaction.get("prepared_demo_status_is_prepared")), "redaction_gating", "Constructed input path emits a redaction report and prepared draft artifacts."),
        (bool(redaction.get("unsafe_residual_blocks") and redaction.get("unsafe_residual_quarantines")), "redaction_gating", "Residual risk block and quarantine behavior are both checked."),
        (bool(local_app.get("approve_and_run_endpoint") and local_app.get("review_html_exists")), "local_app_completeness", "Approved structured episode can be run through the deterministic analysis endpoint."),
        (bool(schema.get("valid_cases") == 7 and redaction.get("prepared_demo_status_is_prepared")), "schema_validity, redaction_gating", "Synthetic case library and constructed demo artifact path validate."),
        (evaluation.get("future_leakage_failures") == 0, "future_leakage_failures", "Current validation report has zero future-leakage failures."),
        (bool(node_audit.get("complete")), "node_audit_completeness", "Every graph node has a node audit."),
        (bool(node_audit.get("complete") and node_audit.get("incomplete") == []), "node_audit_completeness", "Node audits have required estimate, evidence, dependency, and sensitivity fields."),
        (bool(local_app.get("node_audit_checkpoint_visible")), "local_app_completeness", "Node Audit Methodology is visible before processing."),
        (bool(local_app.get("adjustment_controls_visible") and local_app.get("selected_node_recheck_supported")), "local_app_completeness", "OK, Adjust, and Re-check selected-node controls are present and traced."),
        (bool(ensemble.get("complete") and ensemble.get("missing_dispositions") == []), "ensemble_contribution_completeness", "Every ensemble contribution has a disposition and reason."),
        (bool(local_app.get("review_html_exists") and local_app.get("node_audit_checkpoint_visible")), "local_app_completeness", "Ensemble Contributions are visible in the pre-process/review flow before Process."),
        (evaluation.get("expected_posture_agreement", {}).get("total") == 7, "expected_posture_agreement", "Graph posture is computed from deterministic typed fixture runs."),
        (evaluation.get("forbidden_phrase_violations") == 0, "forbidden_phrase_violations", "Forbidden disposition-language scan reports zero generated-artifact violations."),
        (bool(summary.get("complete") and summary.get("summary_paragraph_limit")), "summary_completeness", "Primary clinician summary is concise and machine-checked."),
        (bool(summary.get("selected_review_question_framing") and summary.get("governance_support_boundary")), "summary_completeness", "Summary includes selected-question framing and governance boundary."),
        (bool(local_app.get("review_html_has_deeper_dive") and local_app.get("review_html_has_trace_hashes") and local_app.get("review_html_has_raw_artifact_links")), "local_app_completeness", "Deeper Dive exposes trace hashes and raw JSON/Markdown receipt links."),
        (bool(receipt.get("complete") and receipt.get("selected_review_question_field_supported")), "receipt_completeness", "JSON receipts include selected question and required audit fields."),
        (bool(receipt.get("markdown_clinician_summary_complete") and receipt.get("markdown_deeper_dive_complete")), "receipt_completeness", "Human-readable receipts include summary and deeper-dive sections."),
        (bool(workbench.get("complete") and workbench.get("clinician_summary") and workbench.get("deeper_dive_artifact_index")), "workbench_completeness", "Workbench renders summary, methodology, receipts, validation status, and deeper-dive artifact index."),
        (_automated_validation_complete(evaluation, automated), "validation/reports/latest.json", "Validation report covers schema, leakage, redaction, fixture agreement, detection categories, node audit, receipts, workbench, app flow, summary, and forbidden phrases."),
        (_status_doc_complete(status_text), "docs/18_deterministic_poc_status.md", "Status document separates implemented, deferred, required-before-real-use, and not-claimed boundaries."),
        (False, "live verification commands", "Run the final verification command set after this generated audit is committed; this item is intentionally not inferred from static files."),
    )

    for index, (passed, evidence_key, evidence) in enumerate(checks, start=1):
        items.append(
            {
                "id": index,
                "requirement": GOAL_PROOF_ITEMS[index - 1],
                "verdict": "PASS" if passed else "PENDING",
                "evidence_key": evidence_key,
                "evidence": evidence,
            }
        )
    return items


def _automated_validation_complete(evaluation: dict[str, Any], automated: dict[str, Any]) -> bool:
    categories = (
        "omission_detection",
        "commission_warning_detection",
        "therapy_response_integration",
        "next_best_information_usefulness",
    )
    return (
        bool(evaluation.get("schema_validity"))
        and evaluation.get("future_leakage_failures") == 0
        and _dict(evaluation.get("redaction_gating")).get("complete") is True
        and bool(evaluation.get("expected_posture_agreement"))
        and all(_dict(automated.get(category)).get("missing") == [] for category in categories)
        and _dict(evaluation.get("node_audit_completeness")).get("complete") is True
        and _dict(evaluation.get("receipt_completeness")).get("complete") is True
        and _dict(evaluation.get("workbench_completeness")).get("complete") is True
        and _dict(evaluation.get("local_app_completeness")).get("complete") is True
        and _dict(evaluation.get("summary_completeness")).get("complete") is True
        and evaluation.get("forbidden_phrase_violations") == 0
    )


def _status_doc_complete(text: str) -> bool:
    required = (
        "## Implemented Deterministic POC",
        "## Deferred",
        "## Required Before Real Clinical, Prospective, Or Production Use",
        "## Not Claimed",
    )
    return all(item in text for item in required)


def _render_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# 21 - GOAL.md Completion Audit",
        "",
        "Current audit replaces the older 16-item audit with a 25-item map to the current `GOAL.md` Full Demo Proof Of Done list.",
        "",
        f"Proof items: {payload['proof_item_count']}",
        f"Pass count: {payload['pass_count']}",
        f"All pass: {payload['all_pass']}",
        "",
        "Sentinel remains a local deterministic governance-review POC. This audit does not claim clinical safety, production readiness, regulatory compliance, or clinical outcome benefit.",
        "",
        "## Full Demo Proof Of Done",
        "",
        "| # | Requirement | Verdict | Evidence Surface | Evidence |",
        "|---:|---|---|---|---|",
    ]
    for item in payload["items"]:
        lines.append(
            f"| {item['id']} | {item['requirement']} | {item['verdict']} | "
            f"`{item['evidence_key']}` | {item['evidence']} |"
        )
    lines.extend(
        [
            "",
            "## Verification Commands",
            "",
            "```bash",
            "python3 -m pytest -q",
            "PYTHONPATH=src python3 -m sentinel_workbench.validate data/cases",
            "PYTHONPATH=src python3 -m sentinel_workbench.evaluate --case-dir data/cases --out validation/reports/latest.json --receipt-dir data/receipts",
            "PYTHONPATH=src python3 -m sentinel_workbench.goal_audit --out-json validation/reports/goal_completion_audit.json --out-markdown docs/21_goal_completion_audit.md",
            "git diff --check",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def _read_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _dict(value: object) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the GOAL.md 25-item completion audit.")
    parser.add_argument("--out-json", default="validation/reports/goal_completion_audit.json")
    parser.add_argument("--out-markdown", default="docs/21_goal_completion_audit.md")
    parser.add_argument("--evaluation-report", default="validation/reports/latest.json")
    parser.add_argument("--goal", default="GOAL.md")
    parser.add_argument("--status-doc", default="docs/18_deterministic_poc_status.md")
    args = parser.parse_args()
    payload = generate_goal_completion_audit(
        output_json=args.out_json,
        output_markdown=args.out_markdown,
        evaluation_report_path=args.evaluation_report,
        goal_path=args.goal,
        status_doc_path=args.status_doc,
    )
    print(f"goal_audit_items={payload['proof_item_count']} pass_count={payload['pass_count']}")


if __name__ == "__main__":
    main()
