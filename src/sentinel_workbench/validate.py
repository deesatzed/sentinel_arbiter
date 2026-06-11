from __future__ import annotations

import argparse
from pathlib import Path

from pydantic import ValidationError

from .case_library import summarize_case_library
from .loader import load_episode
from .safety import scan_forbidden_content


def validate_case_dir(case_dir: str | Path) -> tuple[int, list[str]]:
    path = Path(case_dir)
    errors: list[str] = []
    count = 0
    for fixture in sorted(path.glob("*.json")):
        if fixture.name.startswith("invalid_"):
            continue
        count += 1
        try:
            load_episode(fixture)
        except (ValidationError, ValueError) as exc:
            errors.append(f"{fixture}: {exc}")
    findings = scan_forbidden_content(
        [fixture.read_text(encoding="utf-8") for fixture in sorted(path.glob("*.json")) if not fixture.name.startswith("invalid_")],
        allow_safety_rule_lists=False,
    )
    errors.extend(f"safety:{finding.category}:{finding.value}" for finding in findings)
    summary = summarize_case_library(path)
    if summary.valid_case_count < 7:
        errors.append(f"case_library:expected_at_least_7_valid_cases:found_{summary.valid_case_count}")
    for missing in sorted(summary.missing_patterns):
        errors.append(f"case_library:missing_pattern:{missing.value}")
    return count, errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Sentinel Workbench synthetic case fixtures.")
    parser.add_argument("case_dir", nargs="?", default="data/cases")
    args = parser.parse_args()

    count, errors = validate_case_dir(args.case_dir)
    if errors:
        print(f"validated={count} errors={len(errors)}")
        for error in errors:
            print(error)
        raise SystemExit(1)
    print(f"validated={count} errors=0")


if __name__ == "__main__":
    main()
