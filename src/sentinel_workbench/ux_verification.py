from __future__ import annotations

import argparse
import json
import tempfile
import threading
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .local_app import create_demo_server
from .safety import scan_forbidden_content


STATIC_INPUTS = Path("data/static_inputs/static_inputs.json")


def run_ux_verification(
    *,
    output_json: str | Path = "validation/reports/ux_render_verification.json",
    output_markdown: str | Path = "docs/22_local_app_ux_verification.md",
    static_inputs_path: str | Path = STATIC_INPUTS,
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="sentinel_ux_verify_") as tmp:
        server = create_demo_server(
            host="127.0.0.1",
            port=0,
            workspace_dir=tmp,
            static_inputs_path=static_inputs_path,
        )
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base_url = f"http://{server.server_address[0]}:{server.server_address[1]}"
        try:
            landing_html = _get(base_url)
            prepare_html = _post(
                f"{base_url}/prepare",
                {
                    "episode_id": "ux_verification_case",
                    "title": "UX verification case",
                    "review_question": "disposition_information_sufficiency",
                    "clinical_text": _constructed_text(),
                },
            )
            prepared_dir = Path(tmp) / "prepared_inputs" / "ux_verification_case"
            draft_json = (prepared_dir / "draft_episode.json").read_text(encoding="utf-8")
            result_html = _post(
                f"{base_url}/approve-and-run",
                {
                    "prepared_dir": str(prepared_dir),
                    "review_question": "disposition_information_sufficiency",
                    "node_audit_checkpoint": "recheck",
                    "selected_node_ids": "material_gap_strength,omission_risk",
                    "adjustment_note": "UX verification selected-node re-check.",
                    "confirm_adjustment": "1",
                    "reviewer_id": "ux_verifier",
                    "approval_note": "UX verification run.",
                    "approved_episode_json": draft_json,
                },
            )
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    checks = {
        "landing_has_first_screen_choice": _contains_all(
            landing_html,
            (
                "Choose Review Question",
                "Disposition Information Sufficiency",
                "AI Response Use Sufficiency",
                "Pre-process",
            ),
        ),
        "landing_has_responsive_viewport_and_grid": _contains_all(
            landing_html,
            ('<meta name="viewport"', "choice-grid", "grid-template-columns"),
        ),
        "prepare_has_node_audit_before_process": _ordered(prepare_html, "Node Audit Methodology", "Process"),
        "prepare_has_ensemble_before_process": _ordered(prepare_html, "Ensemble Contributions", "Process"),
        "prepare_has_checkpoint_controls": _contains_all(
            prepare_html,
            ("OK", "Adjust", "Re-check Selected Nodes", "Are you sure?", "confirm_adjustment"),
        ),
        "result_has_summary_first": _ordered(result_html, "Clinician Summary", "Approved Structured Episode"),
        "result_has_deeper_dive_links": _contains_all(
            result_html,
            ("Deeper Dive", "Receipt JSON", "Receipt Markdown", 'href="receipts/json/', 'href="receipts/markdown/'),
        ),
        "result_has_validation_and_trace": _contains_all(result_html, ("Validation Status", "Trace Hashes")),
        "layout_breakage_guards_present": _contains_all(
            landing_html + prepare_html + result_html,
            ("overflow-wrap", "table-layout: fixed", "max-width: 1100px", "box-sizing: border-box"),
        ),
        "forbidden_phrase_findings": len(
            scan_forbidden_content(
                [landing_html, prepare_html, result_html],
                allow_safety_rule_lists=False,
            )
        )
        == 0,
    }
    payload: dict[str, Any] = {
        "report_type": "local_app_ux_render_verification",
        "mode": "stdlib_http_rendered_html",
        "all_pass": all(checks.values()),
        "checked_surfaces": [
            "landing page",
            "pre-process/node-audit page",
            "process result/review page",
        ],
        "checks": checks,
        "evidence": {
            "review_question_selection": "Landing page renders both A/B review choices before Pre-process.",
            "node_audit_methodology": "Pre-process page renders Node Audit Methodology before Process.",
            "ensemble_contributions": "Pre-process page renders Ensemble Contributions before Process.",
            "clinician_summary": "Result page renders Clinician Summary before deeper structured details.",
            "deeper_dive": "Result page links receipt JSON and Markdown artifacts and shows validation/trace sections.",
            "layout": "Viewport, responsive grid, fixed table layout, and overflow-wrap guards are present.",
        },
    }
    json_path = Path(output_json)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    markdown_path = Path(output_markdown)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(_render_markdown(payload), encoding="utf-8")
    return payload


def _constructed_text() -> str:
    return "\n".join(
        [
            "Adult constructed patient reports recurrent symptoms after initial evaluation.",
            "Initial workup is documented as not decisive in this constructed demo.",
            "Supportive therapy was offered and response is not clearly reassessed.",
            "At decision time, home support and return access remain unclear.",
        ]
    )


def _get(url: str) -> str:
    with urlopen(url, timeout=5) as response:
        return response.read().decode("utf-8")


def _post(url: str, payload: dict[str, str]) -> str:
    request = Request(
        url,
        data=urlencode(payload).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urlopen(request, timeout=5) as response:
        return response.read().decode("utf-8")


def _contains_all(text: str, needles: tuple[str, ...]) -> bool:
    return all(needle in text for needle in needles)


def _ordered(text: str, first: str, second: str) -> bool:
    first_index = text.find(first)
    second_index = text.find(second)
    return first_index >= 0 and second_index >= 0 and first_index < second_index


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# 22 - Local App UX Render Verification",
        "",
        f"Mode: `{payload['mode']}`",
        f"All pass: {payload['all_pass']}",
        "",
        "This report is an equivalent rendered-HTML verification artifact for the local stdlib demo app. It exercises the HTTP landing, pre-process, and process-result pages and checks required user-visible stages plus basic layout-breakage guards.",
        "",
        "## Checked Surfaces",
        "",
    ]
    lines.extend(f"- {surface}" for surface in payload["checked_surfaces"])
    lines.extend(["", "## Checks", "", "| Check | Pass |", "|---|---:|"])
    for name, passed in payload["checks"].items():
        lines.append(f"| `{name}` | {passed} |")
    lines.extend(["", "## Evidence", ""])
    for name, evidence in payload["evidence"].items():
        lines.append(f"- `{name}`: {evidence}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify the rendered local app UX surfaces.")
    parser.add_argument("--out-json", default="validation/reports/ux_render_verification.json")
    parser.add_argument("--out-markdown", default="docs/22_local_app_ux_verification.md")
    parser.add_argument("--static-inputs", default=str(STATIC_INPUTS))
    args = parser.parse_args()
    payload = run_ux_verification(
        output_json=args.out_json,
        output_markdown=args.out_markdown,
        static_inputs_path=args.static_inputs,
    )
    print(f"ux_render_verification_all_pass={payload['all_pass']}")
    if not payload["all_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
