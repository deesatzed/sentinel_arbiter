from __future__ import annotations

import argparse
import html
import json
from dataclasses import dataclass
from pathlib import Path

from .approval import load_approved_episode, validate_approved_input
from .receipts import SentinelReceipt, build_receipt, sha256_file, write_receipt
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
) -> DemoRunResult:
    base = Path(prepared_dir)
    manifest = validate_approved_input(base)
    episode = load_approved_episode(base)
    workflow_artifacts = _workflow_artifacts(base, manifest.raw_input_sha256)
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
    )
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
) -> str:
    redacted_input = _read_optional(prepared_dir / "redacted_input.txt")
    approved_episode = json.loads((prepared_dir / "approved_episode.json").read_text(encoding="utf-8"))
    approved_episode_text = json.dumps(approved_episode, indent=2)
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
      <h2>Run Summary</h2>
      <table><tbody>
        <tr><th>Final posture</th><td>{_esc(receipt.final_posture)}</td></tr>
        <tr><th>Decision weight</th><td>{_esc(receipt.decision_weight)}</td></tr>
        <tr><th>Receipt JSON</th><td>{_esc(receipt_json_path)}</td></tr>
        <tr><th>Receipt Markdown</th><td>{_esc(receipt_markdown_path)}</td></tr>
        <tr><th>Signature placeholder</th><td>{_esc(receipt.signature_placeholder)}</td></tr>
      </tbody></table>
    </section>
    <section>
      <h2>Redacted Input</h2>
      <pre>{_esc(redacted_input)}</pre>
    </section>
    <section>
      <h2>Approved Structured Episode</h2>
      <pre>{_esc(approved_episode_text)}</pre>
    </section>
    <section>
      <h2>Node Audit Methodology</h2>
      <table><thead><tr><th>Node</th><th>Dependent inputs</th><th>Value</th><th>Range</th><th>Median</th><th>Distribution</th><th>Confidence</th><th>Method</th><th>Evidence refs</th><th>Sensitivity</th></tr></thead><tbody>{''.join(node_rows)}</tbody></table>
    </section>
    <section>
      <h2>Ensemble Contributions</h2>
      <table><thead><tr><th>Node</th><th>Contributor</th><th>Proposed value</th><th>Range</th><th>Disposition</th><th>Reason</th></tr></thead><tbody>{''.join(contribution_rows)}</tbody></table>
      <h3>Rejected ensemble inputs</h3>
      <table><thead><tr><th>Contributor</th><th>Source target</th><th>Disposition</th><th>Reason</th></tr></thead><tbody>{''.join(rejected_rows)}</tbody></table>
    </section>
  </main>
</body>
</html>
"""


def _workflow_artifacts(prepared_dir: Path, raw_input_sha256: str | None) -> dict[str, object]:
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
    return artifacts


def _read_optional(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic analysis for an approved Sentinel prepared input.")
    parser.add_argument("--prepared-dir", required=True)
    parser.add_argument("--static-inputs", default="data/static_inputs/static_inputs.json")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = run_approved_demo(
        prepared_dir=args.prepared_dir,
        static_inputs_path=args.static_inputs,
        output_dir=args.out,
    )
    print(f"review={result.review_html_path} receipt={result.receipt_json_path}")


if __name__ == "__main__":
    main()
