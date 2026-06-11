from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from pydantic import Field

from .loader import load_episode
from .models import DecisionEpisode, StrictModel


class ApprovalTraceEvent(StrictModel):
    sequence_index: int = Field(ge=0)
    event_type: Literal["draft_prepared", "reviewer_approved"]
    event_payload: dict[str, object]
    prev_hash: str | None = None
    event_hash: str


class ApprovalTrace(StrictModel):
    trace_id: str
    events: list[ApprovalTraceEvent] = Field(min_length=1)


class ApprovalManifest(StrictModel):
    approval_status: Literal["approved"]
    episode_id: str
    reviewer_id: str
    approval_note: str
    draft_episode_sha256: str
    approved_episode_sha256: str
    redaction_report_sha256: str
    redacted_input_sha256: str
    raw_input_sha256: str | None = None
    episode_changed_from_draft: bool
    trace_id: str
    trace_sha256: str | None = None


@dataclass(frozen=True)
class ApprovalArtifacts:
    prepared_dir: Path
    approved_episode_path: Path
    approval_manifest_path: Path
    approval_trace_path: Path


def sha256_file(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def stable_hash_payload(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def approve_prepared_input(
    *,
    prepared_dir: str | Path,
    reviewer_id: str,
    approval_note: str,
    approved_episode_source: str | Path | None = None,
) -> ApprovalArtifacts:
    base = Path(prepared_dir)
    draft_path = base / "draft_episode.json"
    redaction_report_path = base / "redaction_report.json"
    redacted_input_path = base / "redacted_input.txt"
    approved_episode_path = base / "approved_episode.json"
    approval_manifest_path = base / "approval_manifest.json"
    approval_trace_path = base / "approval_trace.json"

    _require_file(draft_path)
    _require_file(redaction_report_path)
    _require_file(redacted_input_path)
    redaction_report = _require_prepared_redaction_report(redaction_report_path)

    source_path = Path(approved_episode_source) if approved_episode_source else draft_path
    episode = load_episode(source_path)
    approved_episode_path.write_text(episode.model_dump_json(indent=2) + "\n", encoding="utf-8")

    draft_hash = sha256_file(draft_path)
    approved_hash = sha256_file(approved_episode_path)
    trace = _build_trace(
        trace_id=f"approval_trace_{episode.episode_id}",
        draft_hash=draft_hash,
        approved_hash=approved_hash,
        redaction_report_hash=sha256_file(redaction_report_path),
        reviewer_id=reviewer_id,
        approval_note=approval_note,
    )
    approval_trace_path.write_text(trace.model_dump_json(indent=2) + "\n", encoding="utf-8")

    manifest = ApprovalManifest(
        approval_status="approved",
        episode_id=episode.episode_id,
        reviewer_id=reviewer_id,
        approval_note=approval_note,
        draft_episode_sha256=draft_hash,
        approved_episode_sha256=approved_hash,
        redaction_report_sha256=sha256_file(redaction_report_path),
        redacted_input_sha256=sha256_file(redacted_input_path),
        raw_input_sha256=redaction_report.get("input_sha256"),
        episode_changed_from_draft=draft_hash != approved_hash,
        trace_id=trace.trace_id,
        trace_sha256=sha256_file(approval_trace_path),
    )
    approval_manifest_path.write_text(manifest.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return ApprovalArtifacts(
        prepared_dir=base,
        approved_episode_path=approved_episode_path,
        approval_manifest_path=approval_manifest_path,
        approval_trace_path=approval_trace_path,
    )


def validate_approved_input(prepared_dir: str | Path) -> ApprovalManifest:
    base = Path(prepared_dir)
    manifest_path = base / "approval_manifest.json"
    approved_path = base / "approved_episode.json"
    trace_path = base / "approval_trace.json"
    _require_file(manifest_path)
    _require_file(approved_path)
    _require_file(trace_path)

    manifest = ApprovalManifest.model_validate_json(manifest_path.read_text(encoding="utf-8"))
    episode = load_episode(approved_path)
    if episode.episode_id != manifest.episode_id:
        raise ValueError("approval manifest episode_id does not match approved episode")
    if sha256_file(approved_path) != manifest.approved_episode_sha256:
        raise ValueError("approved episode hash does not match approval manifest")
    if manifest.trace_sha256 and sha256_file(trace_path) != manifest.trace_sha256:
        raise ValueError("approval trace hash does not match approval manifest")
    _validate_trace(trace_path)
    return manifest


def load_approved_episode(path: str | Path) -> DecisionEpisode:
    target = Path(path)
    if target.is_file():
        raise ValueError("approved episode artifact required: pass prepared directory containing approval_manifest.json")
    validate_approved_input(target)
    return load_episode(target / "approved_episode.json")


def _require_file(path: Path) -> None:
    if not path.exists() or not path.is_file():
        raise ValueError(f"required file missing: {path.name}")


def _require_prepared_redaction_report(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("status") != "prepared":
        raise ValueError("redaction report is not prepared")
    if payload.get("residual_findings"):
        raise ValueError("redaction report contains residual findings")
    if not payload.get("input_sha256"):
        raise ValueError("redaction report missing input hash")
    return payload


def _build_trace(
    *,
    trace_id: str,
    draft_hash: str,
    approved_hash: str,
    redaction_report_hash: str,
    reviewer_id: str,
    approval_note: str,
) -> ApprovalTrace:
    events: list[ApprovalTraceEvent] = []
    first_payload = {
        "draft_episode_sha256": draft_hash,
        "redaction_report_sha256": redaction_report_hash,
    }
    first_hash = stable_hash_payload(
        {
            "sequence_index": 0,
            "event_type": "draft_prepared",
            "event_payload": first_payload,
            "prev_hash": None,
        }
    )
    events.append(
        ApprovalTraceEvent(
            sequence_index=0,
            event_type="draft_prepared",
            event_payload=first_payload,
            prev_hash=None,
            event_hash=first_hash,
        )
    )
    second_payload = {
        "approved_episode_sha256": approved_hash,
        "reviewer_id": reviewer_id,
        "approval_note": approval_note,
        "episode_changed_from_draft": draft_hash != approved_hash,
    }
    second_hash = stable_hash_payload(
        {
            "sequence_index": 1,
            "event_type": "reviewer_approved",
            "event_payload": second_payload,
            "prev_hash": first_hash,
        }
    )
    events.append(
        ApprovalTraceEvent(
            sequence_index=1,
            event_type="reviewer_approved",
            event_payload=second_payload,
            prev_hash=first_hash,
            event_hash=second_hash,
        )
    )
    return ApprovalTrace(trace_id=trace_id, events=events)


def _validate_trace(path: Path) -> ApprovalTrace:
    trace = ApprovalTrace.model_validate_json(path.read_text(encoding="utf-8"))
    previous_hash: str | None = None
    for expected_index, event in enumerate(trace.events):
        if event.sequence_index != expected_index:
            raise ValueError("approval trace sequence index mismatch")
        if event.prev_hash != previous_hash:
            raise ValueError("approval trace hash chain mismatch")
        expected_hash = stable_hash_payload(
            {
                "sequence_index": event.sequence_index,
                "event_type": event.event_type,
                "event_payload": event.event_payload,
                "prev_hash": event.prev_hash,
            }
        )
        if event.event_hash != expected_hash:
            raise ValueError("approval trace event hash mismatch")
        previous_hash = event.event_hash
    return trace


def export_approval_schemas(schema_dir: str | Path) -> list[Path]:
    base = Path(schema_dir)
    base.mkdir(parents=True, exist_ok=True)
    manifest_path = base / "approval_manifest.schema.json"
    trace_path = base / "approval_trace.schema.json"
    manifest_path.write_text(json.dumps(ApprovalManifest.model_json_schema(), indent=2) + "\n", encoding="utf-8")
    trace_path.write_text(json.dumps(ApprovalTrace.model_json_schema(), indent=2) + "\n", encoding="utf-8")
    return [manifest_path, trace_path]


def main() -> None:
    parser = argparse.ArgumentParser(description="Approve or validate prepared Sentinel constructed-input artifacts.")
    parser.add_argument("--prepared-dir", help="Prepared input directory to approve.")
    parser.add_argument("--reviewer-id")
    parser.add_argument("--approval-note", default="")
    parser.add_argument("--approved-episode-source")
    parser.add_argument("--validate-approved", help="Prepared input directory to validate.")
    args = parser.parse_args()

    if args.validate_approved:
        manifest = validate_approved_input(args.validate_approved)
        print(f"approved_episode={manifest.episode_id} status={manifest.approval_status}")
        return

    if not args.prepared_dir or not args.reviewer_id:
        parser.error("--prepared-dir and --reviewer-id are required unless --validate-approved is used")

    artifacts = approve_prepared_input(
        prepared_dir=args.prepared_dir,
        reviewer_id=args.reviewer_id,
        approval_note=args.approval_note,
        approved_episode_source=args.approved_episode_source,
    )
    print(f"status=approved out={artifacts.prepared_dir}")


if __name__ == "__main__":
    main()
