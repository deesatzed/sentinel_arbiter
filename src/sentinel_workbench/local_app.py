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
from .safety import scan_forbidden_content


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
                    self._send_html(_handle_prepare(fields, workspace))
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
            payload = self.rfile.read(length).decode("utf-8")
            parsed = parse_qs(payload, keep_blank_values=True)
            return {key: values[0] if values else "" for key, values in parsed.items()}

        def _send_html(self, body: str, *, status: int = 200) -> None:
            encoded = body.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

    return ThreadingHTTPServer((host, port), SentinelDemoHandler)


def _handle_prepare(fields: dict[str, str], workspace: Path) -> str:
    episode_id = _safe_episode_id(fields.get("episode_id", "constructed_demo_case"))
    title = fields.get("title", "").strip() or episode_id.replace("_", " ").title()
    clinical_text = fields.get("clinical_text", "")
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
    return _page(
        "Prepared For Reviewer",
        f"""
        <section>
          <h2>Redacted Input</h2>
          <pre>{_esc(redacted_input)}</pre>
        </section>
        <section>
          <h2>Editable Structured Episode</h2>
          <form method="post" action="/approve-and-run">
            <input type="hidden" name="prepared_dir" value="{_esc(prepared_dir)}">
            <label>Reviewer ID<input name="reviewer_id" value="reviewer_local"></label>
            <label>Approval Note<input name="approval_note" value="Local demo review completed."></label>
            <textarea name="approved_episode_json" rows="28">{_esc(draft_episode)}</textarea>
            <button type="submit">Approve And Run</button>
          </form>
        </section>
        """,
    )


def _handle_approve_and_run(fields: dict[str, str], static_inputs_path: Path) -> str:
    prepared_dir = Path(fields.get("prepared_dir", ""))
    reviewer_id = fields.get("reviewer_id", "").strip() or "reviewer_local"
    approval_note = fields.get("approval_note", "").strip() or "Local demo review completed."
    approved_episode_json = fields.get("approved_episode_json", "")
    if not prepared_dir:
        raise ValueError("prepared_dir is required")
    if not approved_episode_json.strip():
        raise ValueError("approved episode JSON is required")

    edited_episode_path = prepared_dir / "reviewer_edited_episode.json"
    payload = json.loads(approved_episode_json)
    edited_episode_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
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
    )
    return result.review_html_path.read_text(encoding="utf-8")


def _index_page() -> str:
    return _page(
        "Sentinel Local Demo",
        """
        <section>
          <h2>Constructed Input</h2>
          <form method="post" action="/prepare">
            <label>Episode ID<input name="episode_id" value="constructed_local_demo"></label>
            <label>Title<input name="title" value="Constructed local demo"></label>
            <textarea name="clinical_text" rows="14">Adult constructed patient reports recurrent symptoms after initial evaluation.
Initial workup is documented as not decisive in this constructed demo.
Supportive therapy was offered and response is not clearly reassessed.
At decision time, home support and return access remain unclear.</textarea>
            <label class="checkbox"><input type="checkbox" name="quarantine_on_residual" value="1"> Quarantine residual risk instead of blocking</label>
            <button type="submit">Prepare For Review</button>
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
    textarea {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
    button {{ margin-top: 10px; padding: 9px 12px; border: 0; border-radius: 4px; background: #005ea8; color: white; font-weight: 700; cursor: pointer; }}
    pre {{ white-space: pre-wrap; overflow-wrap: anywhere; background: #eef2f6; padding: 10px; border-radius: 4px; }}
    .warning {{ display: inline-block; margin-top: 8px; padding: 8px 10px; background: #f7c948; color: #17212b; font-weight: 700; border-radius: 4px; }}
    .checkbox {{ font-weight: 400; }}
    .checkbox input {{ width: auto; }}
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


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _esc(value: object) -> str:
    return html.escape(str(value), quote=True)


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
