from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .safety import PHI_PATTERNS


class RedactionSchemaModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RedactionFindingRecord(RedactionSchemaModel):
    label: str
    start: int = Field(ge=0)
    end: int = Field(ge=0)
    text_hash: str


class ResidualFindingRecord(RedactionSchemaModel):
    label: str
    pattern: str


class RedactionReport(RedactionSchemaModel):
    status: Literal["prepared", "quarantined"]
    input_sha256: str
    redaction_count: int = Field(ge=0)
    findings: list[RedactionFindingRecord] = Field(default_factory=list)
    residual_findings: list[ResidualFindingRecord] = Field(default_factory=list)


@dataclass(frozen=True)
class RedactionFinding:
    label: str
    start: int
    end: int
    text_hash: str


@dataclass(frozen=True)
class ResidualFinding:
    label: str
    pattern: str


@dataclass(frozen=True)
class RedactionResult:
    clean_text: str
    findings: list[RedactionFinding] = field(default_factory=list)
    residual_findings: list[ResidualFinding] = field(default_factory=list)


@dataclass(frozen=True)
class _RedactionPattern:
    label: str
    pattern: re.Pattern[str]
    replacement: str


def _stable_short_hash(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


class DeterministicRedactor:
    """Small deterministic PII/PHI redaction floor for local demo intake."""

    _patterns = (
        _RedactionPattern("MRN", re.compile(r"\bMRN[:\s]+[A-Za-z0-9-]{4,}\b", re.IGNORECASE), "[REDACTED_MRN]"),
        _RedactionPattern("DOB", re.compile(r"\bDOB[:\s]+\d{1,2}/\d{1,2}/\d{2,4}\b", re.IGNORECASE), "[REDACTED_DOB]"),
        _RedactionPattern(
            "EMAIL",
            re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
            "[REDACTED_EMAIL]",
        ),
        _RedactionPattern(
            "PHONE",
            re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b"),
            "[REDACTED_PHONE]",
        ),
    )

    def redact(self, text: str) -> RedactionResult:
        spans: list[tuple[int, int, str, str]] = []
        for pattern in self._patterns:
            for match in pattern.pattern.finditer(text):
                spans.append((match.start(), match.end(), pattern.label, pattern.replacement))

        merged = _merge_spans(spans)
        findings = [
            RedactionFinding(label=label, start=start, end=end, text_hash=_stable_short_hash(text[start:end]))
            for start, end, label, _replacement in merged
        ]

        clean_text = text
        for start, end, _label, replacement in reversed(merged):
            clean_text = clean_text[:start] + replacement + clean_text[end:]

        residuals = [
            ResidualFinding(label=_label_for_phi_pattern(pattern.pattern), pattern=pattern.pattern)
            for pattern in PHI_PATTERNS
            if pattern.search(clean_text)
        ]
        return RedactionResult(clean_text=clean_text, findings=findings, residual_findings=residuals)


def _merge_spans(spans: list[tuple[int, int, str, str]]) -> list[tuple[int, int, str, str]]:
    ordered = sorted(spans, key=lambda span: (span[0], -(span[1] - span[0])))
    merged: list[tuple[int, int, str, str]] = []
    for span in ordered:
        start, end, _label, _replacement = span
        if merged and start < merged[-1][1]:
            continue
        merged.append(span)
    return merged


def _label_for_phi_pattern(pattern: str) -> str:
    if "3}-\\d{2}-\\d{4}" in pattern:
        return "SSN"
    if "MRN" in pattern:
        return "MRN"
    if "DOB" in pattern:
        return "DOB"
    return "PHI"


def export_redaction_report_schema(output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(RedactionReport.model_json_schema(), indent=2) + "\n", encoding="utf-8")
    return path
