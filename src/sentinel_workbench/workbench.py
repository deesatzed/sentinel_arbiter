from __future__ import annotations

import argparse
import html
import json
import os
from pathlib import Path

from pydantic import Field

from .graph import compute_prudence_graph
from .loader import load_case_library
from .models import DecisionEpisode, RequiredTimepoint, StrictModel, TimelineState
from .receipts import build_receipt
from .replay import build_replay_view


class WorkbenchGenerationResult(StrictModel):
    output_path: Path
    case_count: int
    receipt_json_links: list[str] = Field(default_factory=list)
    receipt_markdown_links: list[str] = Field(default_factory=list)


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def rel_link(path: Path, output_path: Path) -> str:
    return Path(os.path.relpath(path, output_path.parent)).as_posix()


def load_report(report_path: str | Path) -> dict[str, object]:
    path = Path(report_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def state_for_timepoint(episode: DecisionEpisode, timepoint: RequiredTimepoint) -> TimelineState:
    return next(state for state in episode.timepoints if state.timepoint_id == timepoint)


def list_items(items: list[str], *, empty: str) -> str:
    if not items:
        return f"<li>{esc(empty)}</li>"
    return "".join(f"<li>{esc(item)}</li>" for item in items)


def metric_row(name: str, value: object) -> str:
    return f"<tr><th>{esc(name)}</th><td>{esc(value)}</td></tr>"


def render_case_library(episodes: list[DecisionEpisode], receipt_dir: Path, output_path: Path) -> tuple[str, list[str], list[str]]:
    rows: list[str] = []
    json_links: list[str] = []
    markdown_links: list[str] = []
    for episode in episodes:
        graph = compute_prudence_graph(episode, RequiredTimepoint.T3_DISPOSITION_DECISION)
        receipt_id = f"receipt_{episode.episode_id}_T3_deterministic"
        json_path = receipt_dir / "json" / f"{receipt_id}.json"
        markdown_path = receipt_dir / "markdown" / f"{receipt_id}.md"
        json_href = rel_link(json_path, output_path)
        markdown_href = rel_link(markdown_path, output_path)
        json_links.append(json_href)
        markdown_links.append(markdown_href)
        rows.append(
            "<tr>"
            f"<td><a href=\"#case-{esc(episode.episode_id)}\">{esc(episode.episode_id)}</a></td>"
            f"<td>{esc(episode.case_syntheticity.value)}</td>"
            f"<td>{esc(episode.decision_point_type.value)}</td>"
            f"<td>{len(episode.timepoints)}</td>"
            f"<td>{esc(', '.join(pattern.value for pattern in episode.expected_outputs.covered_case_patterns))}</td>"
            f"<td>{esc(graph.final_posture.value)}</td>"
            f"<td><a href=\"{esc(json_href)}\">JSON</a> <a href=\"{esc(markdown_href)}\">Markdown</a></td>"
            "</tr>"
        )
    table = (
        '<section id="case-library" class="panel">'
        "<h2>Case Library</h2>"
        "<table><thead><tr><th>Case</th><th>Artifact</th><th>Decision Point</th>"
        "<th>Timepoints</th><th>Expected Challenge</th><th>Last Run Status</th><th>Receipt Export</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
        "</section>"
    )
    return table, json_links, markdown_links


def render_timeline_panel(episodes: list[DecisionEpisode]) -> str:
    case_blocks: list[str] = []
    for episode in episodes:
        timepoint_blocks: list[str] = []
        for state in sorted(episode.timepoints, key=lambda item: item.sequence_index):
            replay = build_replay_view(episode, state.timepoint_id)
            fact_lines = [f"{fact.fact_id}: {fact.text}" for fact in replay.available_facts]
            weak_lines = [
                f"{fact.fact_id}: {fact.text}"
                for fact in replay.available_facts
                if fact.information_bucket and fact.information_bucket.value == "known_but_weak"
            ]
            gap_lines = [f"{gap.gap_id}: {gap.description}" for gap in replay.current_state.information_gaps]
            pending_lines = [
                f"{pending.pending_id}: {pending.description}" for pending in replay.current_state.pending_information
            ]
            timepoint_blocks.append(
                '<div class="subpanel">'
                f"<h4>{esc(state.timepoint_id.value)} <span>{esc(state.time_label)}</span></h4>"
                "<div class=\"grid-4\">"
                f"<div><h5>Known facts</h5><ul>{list_items(fact_lines, empty='No current-time facts listed.')}</ul></div>"
                f"<div><h5>Known but weak</h5><ul>{list_items(weak_lines, empty='No weak fact flagged here.')}</ul></div>"
                f"<div><h5>Knowable gaps</h5><ul>{list_items(gap_lines, empty='No current gap listed.')}</ul></div>"
                f"<div><h5>Pending info</h5><ul>{list_items(pending_lines, empty='No pending item listed.')}</ul></div>"
                "</div>"
                f"<p class=\"note\">Hidden future facts blocked: {len(replay.blocked_future_fact_ids)}</p>"
                "</div>"
            )
        case_blocks.append(
            f'<article id="case-{esc(episode.episode_id)}" class="case-block">'
            f"<h3>{esc(episode.episode_id)} - {esc(episode.title)}</h3>"
            f"{''.join(timepoint_blocks)}"
            "</article>"
        )
    return (
        '<section id="timeline-replay" class="panel">'
        "<h2>Timeline Replay</h2>"
        '<p class="note">Future information is unavailable to Sentinel at each current-time replay point.</p>'
        f"{''.join(case_blocks)}"
        "</section>"
    )


def render_gap_panel(episodes: list[DecisionEpisode]) -> str:
    case_blocks: list[str] = []
    for episode in episodes:
        rows: list[str] = []
        t3 = state_for_timepoint(episode, RequiredTimepoint.T3_DISPOSITION_DECISION)
        for gap in t3.information_gaps:
            rows.append(
                "<tr>"
                f"<td>{esc(gap.description)}</td>"
                f"<td>{esc(gap.gap_type)}</td>"
                f"<td>{esc(gap.decision_relevance_prior)}</td>"
                f"<td>{esc(gap.knowability.value)}</td>"
                f"<td>{esc(gap.burden.value)}</td>"
                f"<td>{esc(gap.time_to_obtain_hours)} hours</td>"
                f"<td>{esc(gap.candidate_input_mapping or 'No mapped input')}</td>"
                "</tr>"
            )
        case_blocks.append(
            '<article class="case-block">'
            f"<h3>{esc(episode.episode_id)}</h3>"
            "<table><thead><tr><th>Gap</th><th>Bucket</th><th>Decision Relevance</th><th>Knowability</th>"
            "<th>Burden</th><th>Urgency</th><th>Status</th></tr></thead>"
            f"<tbody>{''.join(rows) or '<tr><td colspan=\"7\">No T3 information gaps listed.</td></tr>'}</tbody></table>"
            "</article>"
        )
    return (
        '<section id="information-gap-panel" class="panel">'
        "<h2>Information Gap Panel</h2>"
        f"{''.join(case_blocks)}"
        "</section>"
    )


def render_therapy_panel(episodes: list[DecisionEpisode]) -> str:
    case_blocks: list[str] = []
    for episode in episodes:
        t3 = state_for_timepoint(episode, RequiredTimepoint.T3_DISPOSITION_DECISION)
        rows: list[str] = []
        for therapy in t3.offered_therapies:
            rows.append(
                "<tr>"
                f"<td>{esc(therapy.therapy_id)}</td>"
                f"<td>{esc(therapy.therapy_category)}</td>"
                f"<td>{esc(therapy.accepted_or_received.value)}</td>"
                f"<td>{esc(therapy.response_observed.value)}</td>"
                f"<td>{esc(therapy.response_reliability.value)}</td>"
                f"<td>{esc(therapy.therapy_plausibly_indicated_but_not_considered)}</td>"
                "</tr>"
            )
        for observation in t3.therapy_response_observations:
            rows.append(
                "<tr>"
                f"<td>{esc(observation.therapy_id)}</td>"
                "<td>response_observation</td>"
                "<td>recorded</td>"
                f"<td>{esc(observation.response_observed.value)}</td>"
                f"<td>{esc(observation.reliability.value)}</td>"
                "<td>false</td>"
                "</tr>"
            )
        case_blocks.append(
            '<article class="case-block">'
            f"<h3>{esc(episode.episode_id)}</h3>"
            "<table><thead><tr><th>Therapy</th><th>Category</th><th>Received</th><th>Observed Response</th>"
            "<th>Reliability</th><th>Not Considered Flag</th></tr></thead>"
            f"<tbody>{''.join(rows) or '<tr><td colspan=\"6\">No therapy response item listed.</td></tr>'}</tbody></table>"
            "</article>"
        )
    return (
        '<section id="therapy-response-panel" class="panel">'
        "<h2>Therapy-Response Panel</h2>"
        f"{''.join(case_blocks)}"
        "</section>"
    )


def render_provenance_panel(episodes: list[DecisionEpisode]) -> str:
    case_blocks: list[str] = []
    for episode in episodes:
        t3 = state_for_timepoint(episode, RequiredTimepoint.T3_DISPOSITION_DECISION)
        rows = [
            "<tr>"
            f"<td>{esc(fact.text)}</td>"
            f"<td>{esc(fact.source_type.value)}</td>"
            f"<td>{esc(fact.verification_status.value)}</td>"
            f"<td>{esc(fact.ai_provenance_depth)}</td>"
            f"<td>{esc(', '.join(fact.source_refs) or 'No primary source ref')}</td>"
            f"<td>{esc(fact.decision_criticality)}</td>"
            "</tr>"
            for fact in t3.available_facts
        ]
        case_blocks.append(
            '<article class="case-block">'
            f"<h3>{esc(episode.episode_id)}</h3>"
            "<table><thead><tr><th>Fact</th><th>Source Type</th><th>Verified Status</th>"
            "<th>AI Depth</th><th>Primary Source</th><th>Risk Effect</th></tr></thead>"
            f"<tbody>{''.join(rows) or '<tr><td colspan=\"6\">No T3 facts listed.</td></tr>'}</tbody></table>"
            "</article>"
        )
    return (
        '<section id="provenance-panel" class="panel">'
        "<h2>Provenance Panel</h2>"
        f"{''.join(case_blocks)}"
        "</section>"
    )


def render_graph_panels(episodes: list[DecisionEpisode], receipt_dir: Path, output_path: Path) -> str:
    commission_blocks: list[str] = []
    clock_blocks: list[str] = []
    next_best_blocks: list[str] = []
    graph_blocks: list[str] = []
    node_audit_blocks: list[str] = []
    ensemble_blocks: list[str] = []
    receipt_blocks: list[str] = []
    for episode in episodes:
        graph = compute_prudence_graph(episode, RequiredTimepoint.T3_DISPOSITION_DECISION)
        receipt = build_receipt(episode, "data/static_inputs/static_inputs.json")
        receipt_id = receipt.receipt_id
        json_href = rel_link(receipt_dir / "json" / f"{receipt_id}.json", output_path)
        markdown_href = rel_link(receipt_dir / "markdown" / f"{receipt_id}.md", output_path)
        node_rows = "".join(metric_row(key, value) for key, value in graph.node_values.items())
        next_best = list_items(graph.next_best_information_ranking, empty="No current item crossed the materiality threshold.")
        receipt_rows = (
            metric_row("Final posture", receipt.final_posture)
            + metric_row("Decision weight", receipt.decision_weight)
            + metric_row("Timepoint", receipt.timepoint_id)
            + metric_row("Graph version", receipt.graph_version)
            + metric_row("Node library version", receipt.node_library_version)
            + metric_row("Signature placeholder", receipt.signature_placeholder)
            + metric_row("Input hashes", ", ".join(sorted(receipt.input_hashes.keys())))
            + metric_row("Prompt / dotflow versions", ", ".join(sorted(receipt.prompt_or_dotflow_versions.keys())))
            + metric_row("Evidence versions", ", ".join(sorted(receipt.evidence_versions.keys())))
        )
        commission_blocks.append(
            '<article class="case-block">'
            f"<h3>{esc(episode.episode_id)}</h3>"
            '<div class="grid-3">'
            f"<div><h4>Commission</h4><p>Risk score: {esc(graph.commission_lane.risk_score)}</p>"
            f"<ul>{list_items(graph.commission_lane.findings, empty='No commission-lane finding listed.')}</ul></div>"
            f"<div><h4>Omission</h4><p>Risk score: {esc(graph.omission_lane.risk_score)}</p>"
            f"<ul>{list_items(graph.omission_lane.findings, empty='No omission-lane finding listed.')}</ul></div>"
            f"<div><h4>Therapy</h4><p>Relevance score: {esc(graph.therapy_response_lane.relevance_score)}</p>"
            f"<ul>{list_items(graph.therapy_response_lane.findings, empty='No therapy-response finding listed.')}</ul></div>"
            "</div></article>"
        )
        clock_blocks.append(
            '<article class="case-block">'
            f"<h3>{esc(episode.episode_id)}</h3>"
            "<table><tbody>"
            f"{metric_row('Harm clock', graph.node_values['harm_clock'])}"
            f"{metric_row('Information clock', graph.node_values['information_clock'])}"
            f"{metric_row('Recoverability', graph.node_values['recoverability'])}"
            f"{metric_row('Future correction opportunity', graph.node_values['future_correction_opportunity'])}"
            f"{metric_row('Decision weight', graph.node_values['decision_weight'])}"
            "</tbody></table></article>"
        )
        next_best_blocks.append(
            '<article class="case-block">'
            f"<h3>{esc(episode.episode_id)}</h3><ol>{next_best}</ol></article>"
        )
        graph_blocks.append(
            '<article class="case-block">'
            f"<h3>{esc(episode.episode_id)}</h3>"
            f"<p>Final posture: <strong>{esc(graph.final_posture.value)}</strong></p>"
            f"<table><tbody>{node_rows}</tbody></table></article>"
        )
        audit_rows: list[str] = []
        for audit in receipt.node_audit_bundle.node_audits:
            estimate = audit.estimate
            evidence_refs = ", ".join(estimate.evidence_refs) or "No direct evidence refs"
            dependencies = ", ".join(audit.dependencies)
            audit_rows.append(
                "<tr>"
                f"<td>{esc(audit.node_id)}</td>"
                f"<td>{esc(dependencies)}</td>"
                f"<td>{esc(estimate.value)}</td>"
                f"<td>{esc(f'{estimate.range_min} to {estimate.range_max}')}</td>"
                f"<td>{esc(estimate.median)}</td>"
                f"<td>{esc(estimate.distribution_kind)}</td>"
                f"<td>{esc(estimate.method)}</td>"
                f"<td>{esc(evidence_refs)}</td>"
                f"<td>{esc(audit.sensitivity_note)}</td>"
                "</tr>"
            )
        node_audit_blocks.append(
            '<article class="case-block">'
            f"<h3>{esc(episode.episode_id)}</h3>"
            "<table><thead><tr><th>Node</th><th>Dependent inputs</th><th>Value</th><th>Range</th>"
            "<th>Median</th><th>Distribution</th><th>Method</th><th>Evidence refs</th><th>Sensitivity</th>"
            f"</tr></thead><tbody>{''.join(audit_rows)}</tbody></table></article>"
        )
        contribution_rows: list[str] = []
        for contribution in receipt.ensemble_contribution_bundle.contributions:
            contribution_rows.append(
                "<tr>"
                f"<td>{esc(contribution.node_id)}</td>"
                f"<td>{esc(contribution.contributor_role)}</td>"
                f"<td>{esc(contribution.proposed_value)}</td>"
                f"<td>{esc(f'{contribution.proposed_range_min} to {contribution.proposed_range_max}')}</td>"
                f"<td>{esc(contribution.disposition)}</td>"
                f"<td>{esc(contribution.disposition_reason)}</td>"
                f"<td>{esc(', '.join(contribution.evidence_refs) or 'No direct evidence refs')}</td>"
                "</tr>"
            )
        rejected_rows = [
            "<tr>"
            f"<td>{esc(rejected['contributor_role'])}</td>"
            f"<td>{esc(rejected['source_target'])}</td>"
            f"<td>{esc(rejected['disposition'])}</td>"
            f"<td>{esc(rejected['disposition_reason'])}</td>"
            "</tr>"
            for rejected in receipt.ensemble_contribution_bundle.rejected_inputs
        ]
        ensemble_blocks.append(
            '<article class="case-block">'
            f"<h3>{esc(episode.episode_id)}</h3>"
            "<h4>Normalized contributions</h4>"
            "<table><thead><tr><th>Node</th><th>Contributor</th><th>Proposed value</th><th>Range</th>"
            "<th>Disposition</th><th>Reason</th><th>Evidence refs</th></tr></thead>"
            f"<tbody>{''.join(contribution_rows)}</tbody></table>"
            "<h4>Rejected ensemble inputs</h4>"
            "<table><thead><tr><th>Contributor</th><th>Source target</th><th>Disposition</th><th>Reason</th></tr></thead>"
            f"<tbody>{''.join(rejected_rows) or '<tr><td colspan=\"4\">No rejected input listed.</td></tr>'}</tbody></table>"
            "</article>"
        )
        receipt_blocks.append(
            '<article class="case-block">'
            f"<h3>{esc(episode.episode_id)}</h3>"
            f"<p><a href=\"{esc(json_href)}\">Export JSON</a> <a href=\"{esc(markdown_href)}\">Export Markdown Summary</a></p>"
            f"<table><tbody>{receipt_rows}</tbody></table></article>"
        )
    return (
        '<section id="commission-omission-panel" class="panel">'
        f"<h2>Commission / Omission Panel</h2>{''.join(commission_blocks)}</section>"
        '<section id="two-clock-panel" class="panel">'
        f"<h2>Two-Clock Panel</h2>{''.join(clock_blocks)}</section>"
        '<section id="next-best-input-panel" class="panel">'
        f"<h2>Next-Best-Input Panel</h2>{''.join(next_best_blocks)}</section>"
        '<section id="graph-inspector" class="panel">'
        f"<h2>Graph Inspector</h2>{''.join(graph_blocks)}</section>"
        '<section id="node-audit-methodology" class="panel">'
        f"<h2>Node Audit Methodology</h2>{''.join(node_audit_blocks)}</section>"
        '<section id="ensemble-contribution-panel" class="panel">'
        f"<h2>Ensemble Contribution Panel</h2>{''.join(ensemble_blocks)}</section>"
        '<section id="receipt-viewer-export" class="panel">'
        f"<h2>Receipt Viewer / Export</h2>{''.join(receipt_blocks)}</section>"
    )


def render_evaluation_dashboard(report: dict[str, object]) -> str:
    receipt_payload = report.get("receipt_completeness", {})
    if not isinstance(receipt_payload, dict):
        receipt_payload = {}
    rows = [
        metric_row("Valid runs", report.get("valid_case_count", "unknown")),
        metric_row("Schema failures", 0 if report.get("valid_case_count") else "unknown"),
        metric_row("Future leakage blocked", report.get("future_leakage_failures", "unknown")),
        metric_row("Expected posture agreement", report.get("expected_posture_agreement", "unknown")),
        metric_row("Lane coverage", report.get("lane_coverage", "unknown")),
        metric_row("Static input validation", report.get("static_input_validation", "unknown")),
        metric_row("Receipt completeness", receipt_payload.get("complete", "unknown")),
        metric_row("Forbidden phrase violations", report.get("forbidden_phrase_violations", "unknown")),
        metric_row("Model-swap stability", "Deferred until optional LLM mode"),
    ]
    return (
        '<section id="evaluation-dashboard" class="panel">'
        "<h2>Evaluation Dashboard</h2>"
        f"<table><tbody>{''.join(rows)}</tbody></table>"
        "</section>"
    )


def render_html(
    episodes: list[DecisionEpisode],
    receipt_dir: Path,
    report: dict[str, object],
    output_path: Path,
) -> tuple[str, list[str], list[str]]:
    library, json_links, markdown_links = render_case_library(episodes, receipt_dir, output_path)
    css = """
body { margin: 0; font-family: Arial, Helvetica, sans-serif; color: #1f2933; background: #f5f7f9; }
header { background: #17212b; color: #f8fafc; padding: 24px 28px; }
header h1 { margin: 0 0 8px; font-size: 28px; letter-spacing: 0; }
main { max-width: 1320px; margin: 0 auto; padding: 20px; }
.warning { display: inline-block; margin-top: 8px; padding: 8px 10px; background: #f7c948; color: #17212b; font-weight: 700; border-radius: 4px; }
.panel { background: #ffffff; border: 1px solid #d8dee6; border-radius: 6px; padding: 16px; margin: 14px 0; }
.subpanel { border-top: 1px solid #d8dee6; padding-top: 12px; margin-top: 12px; }
.case-block { border-top: 1px solid #d8dee6; padding-top: 14px; margin-top: 14px; scroll-margin-top: 12px; }
h2 { margin: 0 0 12px; font-size: 20px; }
h3 { margin: 0 0 8px; font-size: 16px; }
h4 { margin: 0 0 8px; font-size: 15px; }
h4 span { color: #5b6776; font-weight: 400; }
h5 { margin: 0 0 6px; font-size: 13px; color: #3a4654; }
table { width: 100%; border-collapse: collapse; table-layout: fixed; }
th, td { border: 1px solid #d8dee6; padding: 8px; text-align: left; vertical-align: top; overflow-wrap: anywhere; font-size: 13px; }
th { background: #eef2f6; }
a { color: #005ea8; font-weight: 700; }
ul, ol { margin: 0; padding-left: 18px; }
li { margin: 3px 0; }
.grid-3 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
.grid-4 { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
.note { color: #4d5b6a; font-size: 13px; }
@media (max-width: 820px) {
  main { padding: 12px; }
  .grid-3, .grid-4 { grid-template-columns: 1fr; }
  th, td { font-size: 12px; }
}
"""
    html_doc = (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        "<title>Sentinel Reviewer Workbench</title>"
        f"<style>{css}</style></head><body>"
        "<header><h1>Sentinel Reviewer Workbench</h1>"
        "<p>Offline deterministic ED disposition replay governance console.</p>"
        '<div class="warning">Planning / governance POC - not for patient care.</div></header>'
        "<main>"
        f"{library}"
        f"{render_timeline_panel(episodes)}"
        f"{render_gap_panel(episodes)}"
        f"{render_therapy_panel(episodes)}"
        f"{render_graph_panels(episodes, receipt_dir, output_path)}"
        f"{render_provenance_panel(episodes)}"
        f"{render_evaluation_dashboard(report)}"
        "</main></body></html>\n"
    )
    return html_doc, json_links, markdown_links


def generate_workbench(
    case_dir: str | Path,
    receipt_dir: str | Path,
    report_path: str | Path,
    output_path: str | Path,
) -> WorkbenchGenerationResult:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    episodes = load_case_library(case_dir)
    report = load_report(report_path)
    html_doc, json_links, markdown_links = render_html(episodes, Path(receipt_dir), report, output)
    output.write_text(html_doc, encoding="utf-8")
    return WorkbenchGenerationResult(
        output_path=output,
        case_count=len(episodes),
        receipt_json_links=json_links,
        receipt_markdown_links=markdown_links,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the static Sentinel reviewer workbench.")
    parser.add_argument("--case-dir", default="data/cases")
    parser.add_argument("--receipt-dir", default="data/receipts")
    parser.add_argument("--report", default="validation/reports/latest.json")
    parser.add_argument("--out", default="data/workbench/index.html")
    args = parser.parse_args()
    result = generate_workbench(args.case_dir, args.receipt_dir, args.report, args.out)
    print(f"workbench={result.output_path} cases={result.case_count}")


if __name__ == "__main__":
    main()
