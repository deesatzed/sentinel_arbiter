from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any


FORBIDDEN_DISPOSITION_PHRASES = (
    "safe to discharge",
    "unsafe to discharge",
    "should admit",
    "should discharge",
    "medically cleared",
    "appropriate for discharge",
    "inappropriate for discharge",
    "recommended pathway",
    "preferred pathway",
)

NAMED_INSTITUTION_PATTERNS = (
    "Massachusetts General Hospital",
    "Mayo Clinic",
    "Cleveland Clinic",
    "Kaiser Permanente",
    "Johns Hopkins",
    "Stanford Health",
    "UCLA Health",
    "UCSF Health",
    "Mount Sinai",
    "Cedars-Sinai",
    "Brigham and Women's",
    "Beth Israel",
)

SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
)

PHI_PATTERNS = (
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    re.compile(r"\bMRN[:\s]+[A-Za-z0-9-]{4,}\b", re.IGNORECASE),
    re.compile(r"\bDOB[:\s]+\d{1,2}/\d{1,2}/\d{2,4}\b", re.IGNORECASE),
)


@dataclass(frozen=True)
class SafetyFinding:
    category: str
    value: str


def iter_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from iter_strings(item)
    elif isinstance(value, list | tuple | set):
        for item in value:
            yield from iter_strings(item)


def scan_forbidden_content(payload: Any, *, allow_safety_rule_lists: bool) -> list[SafetyFinding]:
    findings: list[SafetyFinding] = []
    for text in iter_strings(payload):
        lowered = text.lower()
        for phrase in FORBIDDEN_DISPOSITION_PHRASES:
            if phrase in lowered and not allow_safety_rule_lists:
                findings.append(SafetyFinding("forbidden_disposition_phrase", phrase))
        for name in NAMED_INSTITUTION_PATTERNS:
            if name.lower() in lowered:
                findings.append(SafetyFinding("named_institution", name))
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(SafetyFinding("secret_pattern", pattern.pattern))
        for pattern in PHI_PATTERNS:
            if pattern.search(text):
                findings.append(SafetyFinding("phi_pattern", pattern.pattern))
    return findings
