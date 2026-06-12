from __future__ import annotations

import argparse
import html
import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

from .approval import load_approved_episode, validate_approved_input
from .receipts import SentinelReceipt, build_receipt, review_question_display, sha256_file, write_receipt
from .safety import scan_forbidden_content


@dataclass(frozen=True)
class DemoRunResult:
    prepared_dir: Path
    receipt_json_path: Path
    receipt_markdown_path: Path
    review_html_path: Path


def run_approved_demo(
    *,
    prepared_dir: str | Path,
    static_inputs_path: str | Path,
    output_dir: str | Path,
    review_question: str | None = None,
) -> DemoRunResult:
    base = Path(prepared_dir)
    manifest = validate_approved_input(base)
    episode = load_approved_episode(base)
    workflow_artifacts = _workflow_artifacts(
        base,
        manifest.raw_input_sha256,
        review_question=review_question,
    )
    receipt = build_receipt(
        episode,
        static_inputs_path,
        workflow_artifacts=workflow_artifacts,
    )

    out = Path(output_dir)
    receipt_paths = write_receipt(receipt, out / "receipts")
    review_html_path = out / "review.html"
    review_html_path.parent.mkdir(parents=True, exist_ok=True)
    review_html = render_demo_review_html(
        receipt=receipt,
        prepared_dir=base,
        receipt_json_path=receipt_paths["json_path"],
        receipt_markdown_path=receipt_paths["markdown_path"],
        review_question=review_question,
    )
    review_html = "\n".join(line.rstrip() for line in review_html.splitlines()) + "\n"
    findings = scan_forbidden_content(review_html, allow_safety_rule_lists=False)
    if findings:
        raise ValueError(f"review html forbidden content: {findings[0].phrase}")
    review_html_path.write_text(review_html, encoding="utf-8")
    return DemoRunResult(
        prepared_dir=base,
        receipt_json_path=receipt_paths["json_path"],
        receipt_markdown_path=receipt_paths["markdown_path"],
        review_html_path=review_html_path,
    )


def render_demo_review_html(
    *,
    receipt: SentinelReceipt,
    prepared_dir: Path,
    receipt_json_path: Path,
    receipt_markdown_path: Path,
    review_question: str | None = None,
) -> str:
    redacted_input = _read_optional(prepared_dir / "redacted_input.txt")
    approved_episode = json.loads((prepared_dir / "approved_episode.json").read_text(encoding="utf-8"))
    approved_episode_text = json.dumps(approved_episode, indent=2)
    receipt_json_href = _receipt_href(receipt_json_path)
    receipt_markdown_href = _receipt_href(receipt_markdown_path)
    workflow_rows = []
    for key, value in sorted(receipt.workflow_artifacts.items()):
        workflow_rows.append(
            "<tr>"
            f"<td>{_esc(key)}</td>"
            f"<td>{_esc(value)}</td>"
            "</tr>"
        )
    node_rows = []
    for audit in receipt.node_audit_bundle.node_audits:
        estimate = audit.estimate
        node_rows.append(
            "<tr>"
            f"<td>{_esc(audit.node_id)}</td>"
            f"<td>{_esc(', '.join(audit.dependencies))}</td>"
            f"<td>{_esc(estimate.value)}</td>"
            f"<td>{_esc(f'{estimate.range_min} to {estimate.range_max}')}</td>"
            f"<td>{_esc(estimate.median)}</td>"
            f"<td>{_esc(estimate.distribution_kind)}</td>"
            f"<td>{_esc(estimate.confidence)}</td>"
            f"<td>{_esc(estimate.method)}</td>"
            f"<td>{_esc(', '.join(estimate.evidence_refs) or 'No direct evidence refs')}</td>"
            f"<td>{_esc(audit.sensitivity_note)}</td>"
            "</tr>"
        )
    contribution_rows = []
    for contribution in receipt.ensemble_contribution_bundle.contributions:
        contribution_rows.append(
            "<tr>"
            f"<td>{_esc(contribution.node_id)}</td>"
            f"<td>{_esc(contribution.contributor_role)}</td>"
            f"<td>{_esc(contribution.proposed_value)}</td>"
            f"<td>{_esc(f'{contribution.proposed_range_min} to {contribution.proposed_range_max}')}</td>"
            f"<td>{_esc(contribution.disposition)}</td>"
            f"<td>{_esc(contribution.disposition_reason)}</td>"
            "</tr>"
        )
    rejected_rows = []
    for rejected in receipt.ensemble_contribution_bundle.rejected_inputs:
        rejected_rows.append(
            "<tr>"
            f"<td>{_esc(rejected['contributor_role'])}</td>"
            f"<td>{_esc(rejected['source_target'])}</td>"
            f"<td>{_esc(rejected['disposition'])}</td>"
            f"<td>{_esc(rejected['disposition_reason'])}</td>"
            "</tr>"
        )
    clinician_summary = receipt.clinician_summary
    review_question_label = review_question_display(receipt.selected_review_question)
    main_gap = _first_item(receipt.human_summary_sections.get("what_was_missing", []))
    next_input = _first_item(receipt.human_summary_sections.get("what_would_have_changed_the_discussion", []))
    driver = _plain_driver(receipt)
    node_cards = _node_methodology_cards(receipt)
    node_evidence_rows = _node_evidence_rows(receipt)
    grouped_contributions = _grouped_contribution_sections(receipt)
    model_comparison_panel = _model_comparison_panel(prepared_dir)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Sentinel Demo Review - {_esc(receipt.episode_id)}</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; color: #1f2933; background: #f5f7f9; }}
    header {{ background: #17212b; color: #f8fafc; padding: 22px 28px; }}
    main {{ max-width: 1320px; margin: 0 auto; padding: 18px; }}
    section {{ background: #ffffff; border: 1px solid #d8dee6; border-radius: 6px; padding: 14px; margin: 14px 0; }}
    .warning {{ display: inline-block; margin-top: 8px; padding: 8px 10px; background: #f7c948; color: #17212b; font-weight: 700; border-radius: 4px; }}
    pre {{ white-space: pre-wrap; overflow-wrap: anywhere; background: #eef2f6; padding: 10px; border-radius: 4px; }}
    table {{ width: 100%; border-collapse: collapse; table-layout: fixed; }}
    th, td {{ border: 1px solid #d8dee6; padding: 7px; text-align: left; vertical-align: top; overflow-wrap: anywhere; font-size: 13px; }}
    th {{ background: #eef2f6; }}
    a {{ color: #005ea8; font-weight: 700; }}
    .summary-grid, .nav-grid {{ display: grid; gap: 10px; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }}
    .summary-card, .method-card, .ensemble-card {{ border: 1px solid #d8dee6; border-radius: 6px; padding: 10px; background: #f8fafc; }}
    .summary-card strong, .muted {{ display: block; color: #52616f; margin-top: 4px; }}
    .badge {{ display: inline-block; padding: 2px 6px; border-radius: 4px; background: #e8f1fa; color: #0b4f71; font-weight: 700; }}
  </style>
</head>
<body>
  <header>
    <h1>Run Complete</h1>
    <p>Sentinel local deterministic governance review for {_esc(receipt.episode_id)}.</p>
    <div class="warning">Planning / governance POC - not for patient care.</div>
  </header>
  <main>
    <section>
      <h2>Clinician Summary</h2>
      <p><strong>Review question:</strong> {_esc(review_question_label)}</p>
      <p>{_esc(clinician_summary)}</p>
      <div class="summary-grid">
        <div class="summary-card"><h3>What this means</h3><strong>{_esc(_what_this_means(receipt))}</strong></div>
        <div class="summary-card"><h3>Main driver</h3><strong>{_esc(driver)}</strong></div>
        <div class="summary-card"><h3>Most useful next review input</h3><strong>{_esc(next_input)}</strong></div>
      </div>
      <p>This output is governance review support, not a clinical action recommendation.</p>
      <p><a href="#deeper-dive">Deeper Dive</a></p>
    </section>
    <section>
      <h2>Run Summary</h2>
      <table><tbody>
        <tr><th>Final posture</th><td>{_esc(receipt.final_posture)}</td></tr>
        <tr><th>Decision weight</th><td>{_esc(receipt.decision_weight)}</td></tr>
        <tr><th>Receipt JSON</th><td><a href="{_esc(receipt_json_href)}">{_esc(receipt_json_path)}</a></td></tr>
        <tr><th>Receipt Markdown</th><td><a href="{_esc(receipt_markdown_href)}">{_esc(receipt_markdown_path)}</a></td></tr>
        <tr><th>Signature placeholder</th><td>{_esc(receipt.signature_placeholder)}</td></tr>
      </tbody></table>
    </section>
    <section id="deeper-dive">
      <h2>Deeper Dive</h2>
      <p>Review methodology, evidence, ensemble inputs, receipt artifacts, trace hashes, validation status, and optional comparison-only model output below.</p>
      <nav class="nav-grid">
        <a href="#methodology">Methodology</a>
        <a href="#node-evidence">Node Evidence</a>
        <a href="#ensemble-contributions">Ensemble Contributions</a>
        <a href="#receipt-artifacts">Receipt Artifacts</a>
        <a href="#trace-hashes">Trace Hashes</a>
        <a href="#validation-status">Validation Status</a>
        <a href="#model-comparison">Optional Model Comparison</a>
      </nav>
    </section>
    <section id="validation-status">
      <h2>Validation Status</h2>
      <table><tbody>
        <tr><th>Local validation report</th><td>{_esc(_validation_report_status())}</td></tr>
        <tr><th>Forbidden phrase scan</th><td>Passed for this rendered review page before write.</td></tr>
      </tbody></table>
    </section>
    <section id="trace-hashes">
      <h2>Trace Hashes</h2>
      <table><thead><tr><th>Artifact</th><th>SHA-256 or value</th></tr></thead><tbody>{''.join(workflow_rows)}</tbody></table>
    </section>
    <section>
      <h2>Redacted Input</h2>
      <pre>{_esc(redacted_input)}</pre>
    </section>
    <section>
      <h2>Approved Structured Episode</h2>
      <pre>{_esc(approved_episode_text)}</pre>
    </section>
    <section id="methodology">
      <h2>Node Audit Methodology</h2>
      {node_cards}
    </section>
    <section id="node-evidence">
      <h2>Node Evidence</h2>
      <table><thead><tr><th>Node</th><th>Evidence</th><th>Quality</th><th>Limitations</th></tr></thead><tbody>{node_evidence_rows}</tbody></table>
    </section>
    <section id="ensemble-contributions">
      <h2>Ensemble Contributions</h2>
      {grouped_contributions}
      <h3>Rejected ensemble inputs</h3>
      <table><thead><tr><th>Contributor</th><th>Source target</th><th>Disposition</th><th>Reason</th></tr></thead><tbody>{''.join(rejected_rows)}</tbody></table>
    </section>
    <section id="receipt-artifacts">
      <h2>Receipt Artifacts</h2>
      <p><a href="{_esc(receipt_json_href)}">Receipt JSON</a></p>
      <p><a href="{_esc(receipt_markdown_href)}">Receipt Markdown</a></p>
    </section>
    <section id="model-comparison">
      {model_comparison_panel}
    </section>
  </main>
</body>
</html>
"""


def _workflow_artifacts(
    prepared_dir: Path,
    raw_input_sha256: str | None,
    *,
    review_question: str | None = None,
) -> dict[str, object]:
    artifacts: dict[str, object] = {
        "prepared_dir": str(prepared_dir),
        "redacted_input_sha256": sha256_file(prepared_dir / "redacted_input.txt"),
        "redaction_report_sha256": sha256_file(prepared_dir / "redaction_report.json"),
        "draft_episode_sha256": sha256_file(prepared_dir / "draft_episode.json"),
        "approved_episode_sha256": sha256_file(prepared_dir / "approved_episode.json"),
        "approval_manifest_sha256": sha256_file(prepared_dir / "approval_manifest.json"),
        "approval_trace_sha256": sha256_file(prepared_dir / "approval_trace.json"),
    }
    if raw_input_sha256:
        artifacts["raw_input_sha256"] = raw_input_sha256
    if review_question:
        artifacts["selected_review_question"] = review_question
    run_manifest = prepared_dir / "run_manifest.json"
    if run_manifest.exists():
        artifacts["run_manifest_sha256"] = sha256_file(run_manifest)
    node_audit_manifest = prepared_dir / "node_audit_review_manifest.json"
    if node_audit_manifest.exists():
        artifacts["node_audit_review_manifest_sha256"] = sha256_file(node_audit_manifest)
    return artifacts


def _read_optional(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _receipt_href(path: Path) -> str:
    if path.parent.parent.name == "receipts":
        prepared_dir = path.parent.parent.parent.parent
        return f"/artifacts/{quote(prepared_dir.name)}/receipts/{quote(path.parent.name)}/{quote(path.name)}"
    return str(path)


def _validation_report_status(path: str | Path = "validation/reports/latest.json") -> str:
    report = Path(path)
    if report.exists():
        return f"{report} available"
    return f"{report} not generated in this workspace"


def _first_item(items: list[str]) -> str:
    return items[0] if items else "No item cleared the display threshold."


def _what_this_means(receipt: SentinelReceipt) -> str:
    if receipt.final_posture == "OBTAIN_SPECIFIC_INFORMATION_FIRST":
        return "The review is mainly constrained by missing or weak information that should be inspected before relying on the posture."
    if receipt.final_posture == "PROCEED_WITH_UNCERTAINTY_DISCLOSURE":
        return "The review can be discussed with explicit uncertainty, while the deeper dive keeps the limitations visible."
    return "The deterministic review found no higher-priority information gap in this constructed local example."


def _plain_driver(receipt: SentinelReceipt) -> str:
    values = {key: float(value) for key, value in receipt.node_values.items() if isinstance(value, int | float)}
    priority = [
        ("material_gap_strength", "Unresolved material information gap"),
        ("omission_risk", "Unresolved omission concern"),
        ("commission_risk", "Overconfidence or low-added-value concern"),
        ("ai_provenance_risk", "Weak AI provenance"),
        ("therapy_response_relevance", "Unclear therapy response"),
    ]
    best_key, best_label = max(priority, key=lambda item: values.get(item[0], 0.0))
    if values.get(best_key, 0.0) <= 0:
        return "No single driver dominated the deterministic review."
    return best_label


def _node_methodology_cards(receipt: SentinelReceipt) -> str:
    cards = []
    for audit in receipt.node_audit_bundle.node_audits:
        estimate = audit.estimate
        evidence = "; ".join(item.quoted_or_structured_fact for item in audit.evidence[:3])
        weak = [item.quoted_or_structured_fact for item in audit.evidence if item.quality in {"weak", "unknown"}]
        weak_text = "; ".join(weak[:3]) if weak else "No weak direct evidence flagged for this node."
        cards.append(
            f"""
            <article class="method-card">
              <h3>{_esc(audit.node_id)}</h3>
              <p><span class="badge">Plain-English Meaning</span> {_esc(audit.definition.question)}</p>
              <p><strong>Dependent inputs</strong><span class="muted">{_esc(', '.join(audit.dependencies))}</span></p>
              <p><strong>Evidence used</strong><span class="muted">{_esc(evidence)}</span></p>
              <p><strong>Missing or weak evidence</strong><span class="muted">{_esc(weak_text)}</span></p>
              <p><strong>Estimate</strong><span class="muted">value { _esc(estimate.value) }; range {_esc(estimate.range_min)} to {_esc(estimate.range_max)}; median {_esc(estimate.median)}; distribution {_esc(estimate.distribution_kind)}; confidence {_esc(estimate.confidence)}</span></p>
              <p><strong>Method</strong><span class="muted">{_esc(estimate.method)}</span></p>
              <p><strong>Sensitivity</strong><span class="muted">{_esc(audit.sensitivity_note)}</span></p>
            </article>
            """
        )
    return "".join(cards)


def _node_evidence_rows(receipt: SentinelReceipt) -> str:
    rows = []
    for audit in receipt.node_audit_bundle.node_audits:
        for evidence in audit.evidence:
            rows.append(
                "<tr>"
                f"<td>{_esc(audit.node_id)}</td>"
                f"<td>{_esc(evidence.quoted_or_structured_fact)}</td>"
                f"<td>{_esc(evidence.quality)}</td>"
                f"<td>{_esc('; '.join(evidence.limitations) or 'None recorded')}</td>"
                "</tr>"
            )
    return "".join(rows)


def _grouped_contribution_sections(receipt: SentinelReceipt) -> str:
    by_node: dict[str, list[object]] = {}
    for contribution in receipt.ensemble_contribution_bundle.contributions:
        by_node.setdefault(contribution.node_id, []).append(contribution)
    blocks = []
    for node_id in sorted(by_node):
        contributions = by_node[node_id]
        accepted = sum(1 for item in contributions if item.disposition == "accepted")
        downgraded = sum(1 for item in contributions if item.disposition == "downgraded")
        rows = []
        for contribution in contributions:
            rows.append(
                "<tr>"
                f"<td>{_esc(contribution.contributor_role)}</td>"
                f"<td>{_esc(contribution.proposed_value)}</td>"
                f"<td>{_esc(f'{contribution.proposed_range_min} to {contribution.proposed_range_max}')}</td>"
                f"<td>{_esc(contribution.disposition)}</td>"
                f"<td>{_esc(contribution.disposition_reason)}</td>"
                "</tr>"
            )
        blocks.append(
            f"""
            <article class="ensemble-card">
              <h3>{_esc(node_id)}</h3>
              <p>{accepted} accepted contributions; {downgraded} downgraded contributions. Model and static inputs remain comparison or contribution evidence only.</p>
              <table><thead><tr><th>Contributor</th><th>Proposed value</th><th>Range</th><th>Disposition</th><th>Reason</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
            </article>
            """
        )
    return "".join(blocks)


def _model_comparison_panel(prepared_dir: Path) -> str:
    comparison_report = prepared_dir / "analysis" / "model_comparison" / "comparison_report.md"
    if comparison_report.exists():
        return (
            "<h2>Optional Model Comparison</h2>"
            "<p>OpenRouter comparison-only output is available for this run. The deterministic graph remains the authority.</p>"
            f"<p><a href=\"{_esc(comparison_report)}\">Open comparison report</a></p>"
        )
    return (
        "<h2>Optional Model Comparison</h2>"
        "<p>OpenRouter comparison skipped for this local app run. Configure `.env` and run the comparison harness to create comparison-only artifacts.</p>"
        "<p>Any model output is comparison-only; the deterministic graph remains the authority and model output does not set graph values or final posture.</p>"
    )


def _esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic analysis for an approved Sentinel prepared input.")
    parser.add_argument("--prepared-dir", required=True)
    parser.add_argument("--static-inputs", default="data/static_inputs/static_inputs.json")
    parser.add_argument("--out", required=True)
    parser.add_argument("--review-question")
    args = parser.parse_args()
    result = run_approved_demo(
        prepared_dir=args.prepared_dir,
        static_inputs_path=args.static_inputs,
        output_dir=args.out,
        review_question=args.review_question,
    )
    print(f"review={result.review_html_path} receipt={result.receipt_json_path}")


if __name__ == "__main__":
    main()
