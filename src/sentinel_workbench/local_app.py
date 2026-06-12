from __future__ import annotations

import argparse
import html
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .approval import approve_prepared_input
from .constructed_intake import prepare_constructed_text
from .demo_run import run_approved_demo
from .ensemble import build_ensemble_contribution_bundle
from .graph import REQUIRED_GRAPH_METRICS
from .loader import load_episode
from .models import DecisionEpisode, RequiredTimepoint
from .node_audit import build_node_audit_bundle
from .safety import scan_forbidden_content
from .static_inputs import load_static_input_bundle


REVIEW_QUESTION_LABELS = {
    "disposition_information_sufficiency": "Disposition Information Sufficiency",
    "ai_response_use_sufficiency": "AI Response Use Sufficiency",
}

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONSTRUCTED_TEXT = "\n".join(
    [
        "Adult constructed patient reports recurrent symptoms after initial evaluation.",
        "Initial workup is documented as not decisive in this constructed demo.",
        "Supportive therapy was offered and response is not clearly reassessed.",
        "At decision time, home support and return access remain unclear.",
    ]
)


def create_demo_server(
    *,
    host: str,
    port: int,
    workspace_dir: str | Path = ".sentinel_local_demo",
    static_inputs_path: str | Path = "data/static_inputs/static_inputs.json",
) -> ThreadingHTTPServer:
    workspace = Path(workspace_dir)
    static_inputs = Path(static_inputs_path)
    workspace.mkdir(parents=True, exist_ok=True)

    class SentinelDemoHandler(BaseHTTPRequestHandler):
        server_version = "SentinelLocalDemo/0.1"

        def do_GET(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            if path in {"/", "/index.html"}:
                self._send_html(_index_page())
                return
            self.send_error(404, "Not found")

        def do_POST(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            fields = self._read_form()
            try:
                if path == "/prepare":
                    self._send_html(_handle_prepare(fields, workspace, static_inputs))
                    return
                if path == "/approve-and-run":
                    self._send_html(_handle_approve_and_run(fields, static_inputs))
                    return
                self.send_error(404, "Not found")
            except Exception as exc:  # pragma: no cover - exercised as HTTP 400 behavior in manual use.
                self._send_html(_error_page(str(exc)), status=400)

        def log_message(self, format: str, *args: object) -> None:
            return

        def _read_form(self) -> dict[str, str]:
            length = int(self.headers.get("Content-Length", "0"))
            payload = self.rfile.read(length)
            content_type = self.headers.get("Content-Type", "")
            if content_type.startswith("multipart/form-data"):
                return _parse_multipart_form(payload, content_type)
            payload = payload.decode("utf-8")
            parsed = parse_qs(payload, keep_blank_values=True)
            return {key: ",".join(values) if len(values) > 1 else (values[0] if values else "") for key, values in parsed.items()}

        def _send_html(self, body: str, *, status: int = 200) -> None:
            encoded = body.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

    return ThreadingHTTPServer((host, port), SentinelDemoHandler)


def _handle_prepare(fields: dict[str, str], workspace: Path, static_inputs_path: Path) -> str:
    episode_id = _safe_episode_id(fields.get("episode_id", "constructed_demo_case"))
    title = fields.get("title", "").strip() or episode_id.replace("_", " ").title()
    review_question = _require_review_question(fields.get("review_question", ""))
    clinical_text, input_mode, uploaded_filename = _clinical_text_from_fields(fields)
    sample_case = fields.get("sample_case", "")
    if sample_case and (not clinical_text.strip() or clinical_text.strip() == DEFAULT_CONSTRUCTED_TEXT):
        clinical_text, sample_title = _sample_case_text(sample_case)
        input_mode = "sample_case"
        if not fields.get("title", "").strip():
            title = sample_title
        if fields.get("episode_id", "") in {"", "constructed_local_demo"}:
            episode_id = _safe_episode_id(sample_case)
    if not clinical_text.strip():
        raise ValueError("constructed input text is required")
    prepared_dir = workspace / "prepared_inputs" / episode_id
    artifacts = prepare_constructed_text(
        raw_text=clinical_text,
        out_dir=prepared_dir,
        episode_id=episode_id,
        title=title,
        quarantine_on_residual=bool(fields.get("quarantine_on_residual")),
    )
    if artifacts.quarantined or artifacts.draft_episode_path is None:
        report = _read_text(artifacts.redaction_report_path)
        return _page(
            "Input Quarantined",
            f"""
            <section>
              <h2>Residual Risk Report</h2>
              <pre>{_esc(report)}</pre>
            </section>
            """,
        )

    redacted_input = _read_text(artifacts.redacted_input_path)
    draft_episode = _read_text(artifacts.draft_episode_path)
    run_manifest = {
        "selected_review_question": review_question,
        "selected_review_question_label": REVIEW_QUESTION_LABELS[review_question],
        "episode_id": episode_id,
        "stage": "preprocessed",
        "node_audit_checkpoint_required": True,
        "input_mode": input_mode,
        "sample_case": sample_case,
    }
    if uploaded_filename:
        run_manifest["uploaded_filename"] = uploaded_filename
    (prepared_dir / "run_manifest.json").write_text(json.dumps(run_manifest, indent=2) + "\n", encoding="utf-8")
    episode = load_episode(artifacts.draft_episode_path)
    static_bundle = load_static_input_bundle(static_inputs_path)
    clinical_sections = _structured_episode_editor(episode)
    node_cards = _node_audit_methodology_cards(episode, static_bundle)
    ensemble_groups = _ensemble_contribution_groups(episode, static_bundle)
    return _page(
        "Pre-processed For Reviewer",
        f"""
        <section>
          <h2>Selected Review Question</h2>
          <p>{_esc(REVIEW_QUESTION_LABELS[review_question])}</p>
        </section>
        <section>
          <h2>Intake Review</h2>
          <div class="status-grid">
            <div><strong>Redaction Status</strong><span>Prepared; residual-risk gate passed for this local demo run.</span></div>
            <div><strong>Input Mode</strong><span>{_esc(input_mode)}</span></div>
            <div><strong>Reviewer Boundary</strong><span>Local demo only; not production and not for patient care.</span></div>
          </div>
          <h3>Redacted Input</h3>
          <pre>{_esc(redacted_input)}</pre>
        </section>
        <section>
          <h2>Structured Clinical Sections</h2>
          <p><strong>Editable Structured Episode</strong></p>
          <p>Inferred from constructed text for local review. Edit the advanced JSON only when a field must be corrected before processing.</p>
          {clinical_sections}
        </section>
        <section>
          <h2>Node Audit Methodology</h2>
          <h3>Methodology Explorer</h3>
          <p>Review each node's plain-English meaning, dependent inputs, evidence used, missing or weak evidence, estimate, confidence, method, and sensitivity before processing.</p>
          {node_cards}
        </section>
        <section>
          <h2>Ensemble Contributions</h2>
          <h3>Grouped Ensemble Contributions</h3>
          {ensemble_groups}
        </section>
        <section>
          <h2>Process Review</h2>
          <form method="post" action="/approve-and-run">
            <input type="hidden" name="prepared_dir" value="{_esc(prepared_dir)}">
            <input type="hidden" name="review_question" value="{_esc(review_question)}">
            <fieldset>
              <legend>Node Audit Checkpoint</legend>
              <label class="checkbox"><input type="radio" name="node_audit_checkpoint" value="ok" checked> OK</label>
              <label class="checkbox"><input type="radio" name="node_audit_checkpoint" value="adjust"> Adjust</label>
              <label class="checkbox"><input type="radio" name="node_audit_checkpoint" value="recheck"> Re-check Selected Nodes</label>
            </fieldset>
            <p class="confirm">Are you sure? Methodology-changing adjustments must be confirmed and traced before replacing generated methodology.</p>
            <fieldset>
              <legend>Reviewer Action: select nodes to adjust or re-check</legend>
              {_node_checkbox_controls()}
            </fieldset>
            <label>Adjustment or re-check note<input name="adjustment_note" value="No methodology adjustment requested."></label>
            <label class="checkbox"><input type="checkbox" name="confirm_adjustment" value="1"> Confirm methodology-changing adjustment or selected-node re-check</label>
            <label>Reviewer ID<input name="reviewer_id" value="reviewer_local"></label>
            <label>Approval Note<input name="approval_note" value="Local demo review completed."></label>
            <details>
              <summary>Advanced JSON Edit</summary>
              <textarea name="approved_episode_json" rows="28">{_esc(draft_episode)}</textarea>
            </details>
            <button type="submit">Process</button>
          </form>
        </section>
        """,
    )


def _handle_approve_and_run(fields: dict[str, str], static_inputs_path: Path) -> str:
    prepared_dir = Path(fields.get("prepared_dir", ""))
    review_question = _review_question_from_fields_or_manifest(fields, prepared_dir)
    checkpoint = fields.get("node_audit_checkpoint", "")
    selected_node_ids = _parse_selected_node_ids(fields.get("selected_node_ids", ""))
    adjustment_note = fields.get("adjustment_note", "").strip()
    confirmed = fields.get("confirm_adjustment") == "1"
    reviewer_id = fields.get("reviewer_id", "").strip() or "reviewer_local"
    approval_note = fields.get("approval_note", "").strip() or "Local demo review completed."
    approved_episode_json = fields.get("approved_episode_json", "")
    if not prepared_dir:
        raise ValueError("prepared_dir is required")
    if not approved_episode_json.strip():
        raise ValueError("approved episode JSON is required")
    if checkpoint not in {"ok", "adjust", "recheck"}:
        raise ValueError("node audit checkpoint must be completed before processing")
    if checkpoint in {"adjust", "recheck"} and not confirmed:
        raise ValueError("methodology adjustments require confirmation before processing")

    edited_episode_path = prepared_dir / "reviewer_edited_episode.json"
    payload = json.loads(approved_episode_json)
    edited_episode_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    _write_node_audit_review_manifest(
        prepared_dir=prepared_dir,
        edited_episode_path=edited_episode_path,
        static_inputs_path=static_inputs_path,
        checkpoint=checkpoint,
        selected_node_ids=selected_node_ids,
        adjustment_note=adjustment_note,
        confirmed=confirmed,
        reviewer_id=reviewer_id,
    )
    approve_prepared_input(
        prepared_dir=prepared_dir,
        reviewer_id=reviewer_id,
        approval_note=approval_note,
        approved_episode_source=edited_episode_path,
    )
    result = run_approved_demo(
        prepared_dir=prepared_dir,
        static_inputs_path=static_inputs_path,
        output_dir=prepared_dir / "analysis",
        review_question=review_question,
    )
    return result.review_html_path.read_text(encoding="utf-8")


def _index_page() -> str:
    sample_options = _sample_case_options()
    return _page(
        "Sentinel Local Demo",
        f"""
        <section>
          <h2>Choose Review Question</h2>
          <p>Local demo only. This reviewer console is not production, not PHI-ready, and not for patient care.</p>
          <p>Select one governance review question before pre-processing input.</p>
          <form method="post" action="/prepare" enctype="multipart/form-data">
            <div class="choice-grid">
              <label class="choice"><input type="radio" name="review_question" value="disposition_information_sufficiency" required> <strong>A - Disposition Information Sufficiency</strong><span>Is there enough information to make a disposition decision?</span></label>
              <label class="choice"><input type="radio" name="review_question" value="ai_response_use_sufficiency" required> <strong>B - AI Response Use Sufficiency</strong><span>Is there enough information to use this AI-generated response?</span></label>
            </div>
            <h2>Input</h2>
            <label>Sample Case<select name="sample_case">{sample_options}</select></label>
            <label>Episode ID<input name="episode_id" value="constructed_local_demo"></label>
            <label>Title<input name="title" value="Constructed local demo"></label>
            <label>Local file upload<input type="file" name="clinical_file"></label>
            <textarea name="clinical_text" rows="14">{_esc(DEFAULT_CONSTRUCTED_TEXT)}</textarea>
            <label class="checkbox"><input type="checkbox" name="quarantine_on_residual" value="1"> Quarantine residual risk instead of blocking</label>
            <button type="submit">Pre-process</button>
          </form>
        </section>
        """,
    )


def _page(title: str, body: str) -> str:
    doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{_esc(title)}</title>
  <style>
    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: #f5f7f9; color: #1f2933; }}
    header {{ background: #17212b; color: #f8fafc; padding: 22px 28px; }}
    main {{ max-width: 1100px; margin: 0 auto; padding: 18px; }}
    section {{ background: #ffffff; border: 1px solid #d8dee6; border-radius: 6px; padding: 14px; margin: 14px 0; }}
    label {{ display: block; font-weight: 700; margin: 10px 0; }}
    input, textarea {{ width: 100%; box-sizing: border-box; margin-top: 5px; padding: 8px; border: 1px solid #a7b2bf; border-radius: 4px; font: inherit; }}
    select {{ width: 100%; box-sizing: border-box; margin-top: 5px; padding: 8px; border: 1px solid #a7b2bf; border-radius: 4px; font: inherit; }}
    input[type="radio"], input[type="checkbox"] {{ width: auto; }}
    textarea {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
    button {{ margin-top: 10px; padding: 9px 12px; border: 0; border-radius: 4px; background: #005ea8; color: white; font-weight: 700; cursor: pointer; }}
    pre {{ white-space: pre-wrap; overflow-wrap: anywhere; background: #eef2f6; padding: 10px; border-radius: 4px; }}
    table {{ width: 100%; border-collapse: collapse; table-layout: fixed; }}
    th, td {{ border: 1px solid #d8dee6; padding: 7px; text-align: left; vertical-align: top; overflow-wrap: anywhere; font-size: 13px; }}
    th {{ background: #eef2f6; }}
    .warning {{ display: inline-block; margin-top: 8px; padding: 8px 10px; background: #f7c948; color: #17212b; font-weight: 700; border-radius: 4px; }}
    .checkbox {{ font-weight: 400; }}
    .checkbox input {{ width: auto; }}
    .choice-grid {{ display: grid; gap: 10px; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }}
    .choice {{ border: 1px solid #a7b2bf; border-radius: 6px; padding: 10px; background: #f8fafc; }}
    .choice span {{ display: block; margin-top: 4px; font-weight: 400; }}
    .segmented button {{ margin-right: 8px; background: #34495e; }}
    .confirm {{ border-left: 4px solid #f7c948; padding-left: 10px; }}
    .status-grid, .section-grid {{ display: grid; gap: 10px; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }}
    .status-grid div, .node-card, .ensemble-group, .clinical-panel {{ border: 1px solid #d8dee6; border-radius: 6px; padding: 10px; background: #f8fafc; }}
    .status-grid span, .muted {{ display: block; color: #52616f; font-weight: 400; margin-top: 4px; }}
    .node-card {{ margin: 10px 0; }}
    .node-card h4, .ensemble-group h4 {{ margin: 0 0 8px 0; }}
    .node-meta {{ display: grid; gap: 8px; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }}
    .badge {{ display: inline-block; padding: 2px 6px; border-radius: 4px; background: #e8f1fa; color: #0b4f71; font-weight: 700; }}
  </style>
</head>
<body>
  <header>
    <h1>{_esc(title)}</h1>
    <p>Local deterministic Sentinel governance review workflow.</p>
    <div class="warning">Planning / governance POC - not for patient care.</div>
  </header>
  <main>{body}</main>
</body>
</html>
"""
    findings = scan_forbidden_content(doc, allow_safety_rule_lists=False)
    if findings:
        raise ValueError(f"local app html forbidden content: {findings[0].phrase}")
    return doc


def _error_page(message: str) -> str:
    return _page(
        "Request Blocked",
        f"<section><h2>Validation Error</h2><pre>{_esc(message)}</pre></section>",
    )


def _safe_episode_id(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_\\-]+", "_", value.strip())
    cleaned = cleaned.strip("_-")
    if not cleaned:
        raise ValueError("episode_id is required")
    return cleaned[:80]


def _require_review_question(value: str) -> str:
    if value not in REVIEW_QUESTION_LABELS:
        raise ValueError("review question is required before pre-processing")
    return value


def _clinical_text_from_fields(fields: dict[str, str]) -> tuple[str, str, str | None]:
    pasted = fields.get("clinical_text", "")
    uploaded = fields.get("clinical_file", "")
    uploaded_filename = fields.get("clinical_file__filename") or None
    if pasted.strip():
        return pasted, "pasted_text", uploaded_filename
    if uploaded.strip():
        return uploaded, "uploaded_file", uploaded_filename
    return "", "missing", uploaded_filename


def _sample_case_options() -> str:
    options = ['<option value="constructed_demo_case">constructed_demo_case - constructed local demo</option>']
    case_dir = ROOT / "data" / "cases"
    for path in sorted(case_dir.glob("valid_*.json")):
        try:
            episode = load_episode(path)
        except Exception:
            continue
        options.append(f'<option value="{_esc(episode.episode_id)}">{_esc(episode.episode_id)} - {_esc(episode.title)}</option>')
    return "".join(options)


def _sample_case_text(sample_case: str) -> tuple[str, str]:
    if sample_case == "constructed_demo_case":
        return DEFAULT_CONSTRUCTED_TEXT, "Constructed local demo"
    case_dir = ROOT / "data" / "cases"
    for path in sorted(case_dir.glob("valid_*.json")):
        episode = load_episode(path)
        if episode.episode_id == sample_case:
            lines = [episode.title, f"Governance question: {episode.governance_question}."]
            for state in episode.timepoints:
                if state.timepoint_id == RequiredTimepoint.T4_FOLLOW_UP_OR_OUTCOME:
                    continue
                lines.append(f"{state.timepoint_id.value}:")
                lines.extend(f"- {fact.text}" for fact in state.available_facts[:4])
                lines.extend(f"- Missing/unclear: {gap.description}" for gap in state.information_gaps[:3])
            return "\n".join(lines), episode.title
    return DEFAULT_CONSTRUCTED_TEXT, "Constructed local demo"


def _review_question_from_fields_or_manifest(fields: dict[str, str], prepared_dir: Path) -> str:
    value = fields.get("review_question", "")
    if value in REVIEW_QUESTION_LABELS:
        return value
    manifest_path = prepared_dir / "run_manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_value = str(manifest.get("selected_review_question", ""))
        if manifest_value in REVIEW_QUESTION_LABELS:
            return manifest_value
    raise ValueError("review question is required before processing")


def _parse_selected_node_ids(value: str) -> list[str]:
    node_ids = [item.strip() for item in value.replace("\n", ",").split(",") if item.strip()]
    invalid = [node_id for node_id in node_ids if node_id not in REQUIRED_GRAPH_METRICS]
    if invalid:
        raise ValueError(f"unknown selected node id: {invalid[0]}")
    return node_ids


def _write_node_audit_review_manifest(
    *,
    prepared_dir: Path,
    edited_episode_path: Path,
    static_inputs_path: Path,
    checkpoint: str,
    selected_node_ids: list[str],
    adjustment_note: str,
    confirmed: bool,
    reviewer_id: str,
) -> Path:
    episode = load_episode(edited_episode_path)
    static_bundle = load_static_input_bundle(static_inputs_path)
    audit_bundle = build_node_audit_bundle(episode, static_bundle=static_bundle)
    selected = set(selected_node_ids)
    recheck_results = []
    if checkpoint == "recheck":
        for audit in audit_bundle.node_audits:
            if audit.node_id in selected:
                recheck_results.append(
                    {
                        "node_id": audit.node_id,
                        "value": audit.estimate.value,
                        "range_min": audit.estimate.range_min,
                        "range_max": audit.estimate.range_max,
                        "median": audit.estimate.median,
                        "confidence": audit.estimate.confidence,
                        "method": audit.estimate.method,
                        "evidence_refs": audit.estimate.evidence_refs,
                        "sensitivity_note": audit.sensitivity_note,
                    }
                )
    manifest = {
        "manifest_type": "node_audit_review_manifest",
        "checkpoint_status": checkpoint,
        "selected_node_ids": selected_node_ids,
        "adjustment_note": adjustment_note,
        "confirmation": confirmed,
        "reviewer_id": reviewer_id,
        "recheck_results": recheck_results,
        "graph_authority_preserved": True,
        "notes": [
            "Reviewer checkpoint is recorded separately from generated facts.",
            "Re-check results recompute deterministic node audit values; they do not invent unsupported facts.",
        ],
    }
    manifest_path = prepared_dir / "node_audit_review_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest_path


def _structured_episode_editor(episode: DecisionEpisode) -> str:
    t3 = next(state for state in episode.timepoints if state.timepoint_id == RequiredTimepoint.T3_DISPOSITION_DECISION)
    facts = "\n".join(f"- {fact.text}" for fact in t3.available_facts) or "- No current-time facts represented."
    gaps = "\n".join(f"- {gap.description}" for gap in t3.information_gaps) or "- No material gaps represented."
    therapies = "\n".join(
        f"- {therapy.therapy_id}: {therapy.response_observed.value} ({therapy.response_reliability.value})"
        for therapy in t3.offered_therapies
    ) or "- No therapy response item represented."
    follow_up = t3.follow_up_feasibility
    follow_up_text = (
        f"Follow-up access: {follow_up.follow_up_access.value}\n"
        f"Home support: {follow_up.home_support.value}\n"
        f"Return access: {follow_up.return_access.value}\n"
        f"Reliability: {follow_up.barrier_reliability.value}"
    )
    return f"""
    <div class="section-grid">
      <div class="clinical-panel"><h3>Current-Time Facts</h3><textarea name="section_current_time_facts" rows="7">{_esc(facts)}</textarea></div>
      <div class="clinical-panel"><h3>Information Gaps</h3><textarea name="section_information_gaps" rows="7">{_esc(gaps)}</textarea></div>
      <div class="clinical-panel"><h3>Therapy Response</h3><textarea name="section_therapy_response" rows="7">{_esc(therapies)}</textarea></div>
      <div class="clinical-panel"><h3>Follow-up Feasibility</h3><textarea name="section_follow_up" rows="7">{_esc(follow_up_text)}</textarea></div>
    </div>
    """


def _node_audit_methodology_cards(episode: object, static_bundle: object) -> str:
    audit_bundle = build_node_audit_bundle(episode, static_bundle=static_bundle)
    cards = []
    for audit in audit_bundle.node_audits:
        estimate = audit.estimate
        evidence_used = "; ".join(item.quoted_or_structured_fact for item in audit.evidence[:3])
        weak = [item.quoted_or_structured_fact for item in audit.evidence if item.quality in {"weak", "unknown"}]
        weak_text = "; ".join(weak[:3]) if weak else "No weak direct evidence flagged for this node."
        cards.append(
            f"""
            <article class="node-card">
              <h4><label class="checkbox"><input type="checkbox" name="selected_node_ids" value="{_esc(audit.node_id)}"> {_esc(audit.node_id)}</label></h4>
              <div class="node-meta">
                <div><strong>Plain-English Meaning</strong><span class="muted">{_esc(audit.definition.question)}</span></div>
                <div><strong>Dependent Inputs</strong><span class="muted">{_esc(', '.join(audit.dependencies))}</span></div>
                <div><strong>Evidence Used</strong><span class="muted">{_esc(evidence_used)}</span></div>
                <div><strong>Missing or Weak Evidence</strong><span class="muted">{_esc(weak_text)}</span></div>
                <div><strong>Value / Range / Median</strong><span class="muted">{_esc(estimate.value)} / {_esc(estimate.range_min)} to {_esc(estimate.range_max)} / {_esc(estimate.median)}</span></div>
                <div><strong>Distribution / Confidence</strong><span class="muted">{_esc(estimate.distribution_kind)} / {_esc(estimate.confidence)}</span></div>
                <div><strong>Method</strong><span class="muted">{_esc(estimate.method)}</span></div>
                <div><strong>Sensitivity</strong><span class="muted">{_esc(audit.sensitivity_note)}</span></div>
              </div>
            </article>
            """
        )
    return "".join(cards)


def _node_checkbox_controls() -> str:
    controls = []
    for node_id in REQUIRED_GRAPH_METRICS:
        checked = " checked" if node_id in {"material_gap_strength", "omission_risk"} else ""
        controls.append(f'<label class="checkbox"><input type="checkbox" name="selected_node_ids" value="{_esc(node_id)}"{checked}> {_esc(node_id)}</label>')
    return "".join(controls)


def _ensemble_contribution_groups(episode: object, static_bundle: object) -> str:
    ensemble = build_ensemble_contribution_bundle(episode, static_bundle)
    by_node: dict[str, list[object]] = {}
    for contribution in ensemble.contributions:
        by_node.setdefault(contribution.node_id, []).append(contribution)
    groups = [
        "<p><span class=\"badge\">Accepted contributions</span> <span class=\"badge\">Downgraded contributions</span> <span class=\"badge\">Rejected or unsupported inputs</span></p>"
    ]
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
        groups.append(
            f"""
            <article class="ensemble-group">
              <h4>{_esc(node_id)}</h4>
              <p>{accepted} accepted; {downgraded} downgraded. Unsupported targets stay rejected and cannot drive graph authority.</p>
              <table><thead><tr><th>Contributor</th><th>Proposed value</th><th>Range</th><th>Disposition</th><th>Reason</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
            </article>
            """
        )
    rejected_count = len(ensemble.rejected_inputs)
    groups.append(f"<p>Rejected or unsupported inputs: {rejected_count}. They are retained for transparency but do not change deterministic graph values.</p>")
    return "".join(groups)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def _parse_multipart_form(payload: bytes, content_type: str) -> dict[str, str]:
    boundary = _multipart_boundary(content_type)
    delimiter = b"--" + boundary
    fields: dict[str, str] = {}
    for raw_part in payload.split(delimiter):
        part = raw_part.strip(b"\r\n")
        if not part or part == b"--":
            continue
        if part.endswith(b"--"):
            part = part[:-2].rstrip(b"\r\n")
        header_bytes, separator, body = part.partition(b"\r\n\r\n")
        if not separator:
            continue
        headers = header_bytes.decode("utf-8", errors="replace").split("\r\n")
        disposition = next((header for header in headers if header.lower().startswith("content-disposition:")), "")
        params = _parse_content_disposition(disposition)
        name = params.get("name")
        if not name:
            continue
        filename = params.get("filename")
        text = body.rstrip(b"\r\n").decode("utf-8", errors="replace")
        fields[name] = text
        if filename:
            fields[f"{name}__filename"] = filename
    return fields


def _multipart_boundary(content_type: str) -> bytes:
    for item in content_type.split(";"):
        item = item.strip()
        if item.startswith("boundary="):
            boundary = item.split("=", 1)[1].strip().strip('"')
            if boundary:
                return boundary.encode("utf-8")
    raise ValueError("multipart boundary missing")


def _parse_content_disposition(value: str) -> dict[str, str]:
    _, _, remainder = value.partition(":")
    params: dict[str, str] = {}
    for item in remainder.split(";"):
        item = item.strip()
        if "=" not in item:
            continue
        key, raw = item.split("=", 1)
        params[key.strip().lower()] = raw.strip().strip('"')
    return params


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local Sentinel constructed-input demo app.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--workspace-dir", default=".sentinel_local_demo")
    parser.add_argument("--static-inputs", default="data/static_inputs/static_inputs.json")
    args = parser.parse_args()
    server = create_demo_server(
        host=args.host,
        port=args.port,
        workspace_dir=args.workspace_dir,
        static_inputs_path=args.static_inputs,
    )
    print(f"sentinel local demo: http://{args.host}:{server.server_address[1]}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
