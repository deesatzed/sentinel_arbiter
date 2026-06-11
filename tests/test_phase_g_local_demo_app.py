import json
from pathlib import Path
import threading
import tomllib
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from sentinel_workbench.approval import approve_prepared_input
from sentinel_workbench.constructed_intake import prepare_constructed_text
from sentinel_workbench.demo_run import run_approved_demo
from sentinel_workbench.local_app import create_demo_server
from sentinel_workbench.safety import scan_forbidden_content


ROOT = Path(__file__).resolve().parents[1]
STATIC_INPUTS = ROOT / "data" / "static_inputs" / "static_inputs.json"


def _constructed_text() -> str:
    return "\n".join(
        [
            "Adult constructed patient reports recurrent symptoms after initial evaluation.",
            "Initial workup is documented as not decisive in this constructed demo.",
            "Supportive therapy was offered and response is not clearly reassessed.",
            "At decision time, home support and return access remain unclear.",
        ]
    )


def _post_form(url: str, payload: dict[str, str]) -> str:
    request = Request(
        url,
        data=urlencode(payload).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urlopen(request, timeout=5) as response:
        return response.read().decode("utf-8")


def _post_form_allow_error(url: str, payload: dict[str, str]) -> str:
    try:
        return _post_form(url, payload)
    except HTTPError as exc:
        return exc.read().decode("utf-8")


def test_run_approved_demo_writes_receipts_review_html_and_workflow_refs(tmp_path):
    prepared = prepare_constructed_text(
        raw_text=_constructed_text(),
        out_dir=tmp_path / "prepared_inputs" / "constructed_run_case",
        episode_id="constructed_run_case",
        title="Constructed run case",
    )
    assert prepared.draft_episode_path is not None
    approve_prepared_input(
        prepared_dir=prepared.out_dir,
        reviewer_id="reviewer_run",
        approval_note="Reviewed structured episode for deterministic demo run.",
    )

    result = run_approved_demo(
        prepared_dir=prepared.out_dir,
        static_inputs_path=STATIC_INPUTS,
        output_dir=prepared.out_dir / "analysis",
    )

    assert result.receipt_json_path.exists()
    assert result.receipt_markdown_path.exists()
    assert result.review_html_path.exists()
    payload = json.loads(result.receipt_json_path.read_text(encoding="utf-8"))
    assert payload["workflow_artifacts"]["redaction_report_sha256"]
    assert payload["workflow_artifacts"]["approval_manifest_sha256"]
    assert payload["workflow_artifacts"]["approval_trace_sha256"]
    assert payload["input_hashes"]["raw_input_sha256"]
    assert "Adult constructed patient reports" not in json.dumps(payload)

    html = result.review_html_path.read_text(encoding="utf-8")
    assert "Redacted Input" in html
    assert "Approved Structured Episode" in html
    assert "Node Audit Methodology" in html
    assert "Ensemble Contributions" in html
    assert "Receipt JSON" in html
    assert scan_forbidden_content(html, allow_safety_rule_lists=False) == []


def test_local_demo_http_app_prepares_approves_runs_and_reviews_constructed_input(tmp_path):
    server = create_demo_server(
        host="127.0.0.1",
        port=0,
        workspace_dir=tmp_path,
        static_inputs_path=STATIC_INPUTS,
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://{server.server_address[0]}:{server.server_address[1]}"
    try:
        with urlopen(base_url, timeout=5) as response:
            index_html = response.read().decode("utf-8")
        assert "Sentinel Local Demo" in index_html
        assert "Disposition Information Sufficiency" in index_html
        assert "AI Response Use Sufficiency" in index_html
        assert "Pre-process" in index_html
        assert "Planning / governance POC - not for patient care." in index_html

        prepare_html = _post_form_allow_error(
            f"{base_url}/prepare",
            {
                "episode_id": "constructed_http_case",
                "title": "Constructed HTTP case",
                "review_question": "disposition_information_sufficiency",
                "clinical_text": _constructed_text(),
            },
        )
        prepared_dir = tmp_path / "prepared_inputs" / "constructed_http_case"
        assert "Redacted Input" in prepare_html
        assert "Editable Structured Episode" in prepare_html
        assert "Node Audit Methodology" in prepare_html
        assert "Ensemble Contributions" in prepare_html
        assert "OK" in prepare_html
        assert "Adjust" in prepare_html
        assert "Re-check Selected Nodes" in prepare_html
        assert "Are you sure?" in prepare_html
        assert (prepared_dir / "run_manifest.json").exists()
        manifest = json.loads((prepared_dir / "run_manifest.json").read_text(encoding="utf-8"))
        assert manifest["selected_review_question"] == "disposition_information_sufficiency"
        assert (prepared_dir / "redacted_input.txt").exists()
        assert (prepared_dir / "draft_episode.json").exists()
        assert not (prepared_dir / "raw_input.txt").exists()

        draft_json = (prepared_dir / "draft_episode.json").read_text(encoding="utf-8")
        review_html = _post_form(
            f"{base_url}/approve-and-run",
            {
                "prepared_dir": str(prepared_dir),
                "review_question": "disposition_information_sufficiency",
                "node_audit_checkpoint": "ok",
                "reviewer_id": "reviewer_http",
                "approval_note": "HTTP approval for constructed demo.",
                "approved_episode_json": draft_json,
            },
        )

        assert "Run Complete" in review_html
        assert "Clinician Summary" in review_html
        assert "Deeper Dive" in review_html
        assert review_html.index("Clinician Summary") < review_html.index("Approved Structured Episode")
        assert "disposition information sufficiency" in review_html.lower()
        assert "Node Audit Methodology" in review_html
        assert "Ensemble Contributions" in review_html
        assert "Receipt JSON" in review_html
        assert (prepared_dir / "approval_manifest.json").exists()
        assert (prepared_dir / "analysis" / "review.html").exists()
        receipt_json = json.loads(
            (prepared_dir / "analysis" / "receipts" / "json" / "receipt_constructed_http_case_T3_deterministic.json")
            .read_text(encoding="utf-8")
        )
        assert receipt_json["workflow_artifacts"]["selected_review_question"] == "disposition_information_sufficiency"
        assert scan_forbidden_content(review_html, allow_safety_rule_lists=False) == []
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_local_demo_requires_review_question_before_preprocess(tmp_path):
    server = create_demo_server(
        host="127.0.0.1",
        port=0,
        workspace_dir=tmp_path,
        static_inputs_path=STATIC_INPUTS,
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://{server.server_address[0]}:{server.server_address[1]}"
    try:
        prepare_html = _post_form_allow_error(
            f"{base_url}/prepare",
            {
                "episode_id": "missing_choice_case",
                "title": "Missing choice case",
                "clinical_text": _constructed_text(),
            },
        )
        assert "Validation Error" in prepare_html
        assert "review question is required" in prepare_html
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_pyproject_exposes_local_demo_console_scripts():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert (
        pyproject["project"]["scripts"]["sentinel-workbench-run-approved-demo"]
        == "sentinel_workbench.demo_run:main"
    )
    assert pyproject["project"]["scripts"]["sentinel-workbench-local-demo"] == "sentinel_workbench.local_app:main"
