from __future__ import annotations

import argparse
import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .goal_audit import generate_goal_completion_audit


@dataclass(frozen=True)
class CommandSpec:
    name: str
    command: tuple[str, ...]
    env: dict[str, str] | None = None


def run_final_verification(
    *,
    report_path: str | Path = "validation/reports/final_verification.json",
    goal_audit_json_path: str | Path = "validation/reports/goal_completion_audit.json",
    goal_audit_markdown_path: str | Path = "docs/21_goal_completion_audit.md",
    cwd: str | Path = ".",
) -> dict[str, Any]:
    root = Path(cwd).resolve()
    report_output = Path(report_path)
    command_results = [_run_command(spec, root) for spec in _verification_commands()]
    json_check = _check_json_syntax(root)

    flags = {
        "pytest_passed": _command_passed(command_results, "pytest"),
        "case_validation_passed": _command_passed(command_results, "case_validation"),
        "static_input_validation_passed": _command_passed(command_results, "static_input_validation"),
        "evaluation_report_regenerated": _command_passed(command_results, "evaluation_report"),
        "ux_verification_passed": _command_passed(command_results, "ux_render_verification"),
        "pip_dry_run_passed": _command_passed(command_results, "pip_dry_run"),
        "git_diff_check_passed": _command_passed(command_results, "git_diff_check"),
        "json_syntax_checks_passed": json_check["passed"],
    }
    all_pass = all(flags.values()) and all(command["exit_code"] == 0 for command in command_results)
    report: dict[str, Any] = {
        "report_type": "final_verification",
        "scope": "GOAL.md clinician review console v1",
        "all_pass": all_pass,
        **flags,
        "commands": command_results,
        "json_syntax": json_check,
    }

    report_output.parent.mkdir(parents=True, exist_ok=True)
    report_output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    audit_payload = generate_goal_completion_audit(
        output_json=goal_audit_json_path,
        output_markdown=goal_audit_markdown_path,
        final_verification_path=report_output,
    )
    report["goal_audit_all_pass_after_regeneration"] = audit_payload["all_pass"]
    report_output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def _verification_commands() -> tuple[CommandSpec, ...]:
    pythonpath_env = {"PYTHONPATH": "src"}
    self_verification_env = {
        "PYTHONPATH": "src",
        "SENTINEL_FINAL_VERIFICATION_RUNNING": "1",
    }
    return (
        CommandSpec("pytest", ("python3", "-m", "pytest", "-q"), self_verification_env),
        CommandSpec("case_validation", ("python3", "-m", "sentinel_workbench.validate", "data/cases"), pythonpath_env),
        CommandSpec(
            "static_input_validation",
            (
                "python3",
                "-m",
                "sentinel_workbench.static_inputs",
                "--static-inputs",
                "data/static_inputs/static_inputs.json",
                "--case-dir",
                "data/cases",
            ),
            pythonpath_env,
        ),
        CommandSpec(
            "evaluation_report",
            (
                "python3",
                "-m",
                "sentinel_workbench.evaluate",
                "--case-dir",
                "data/cases",
                "--out",
                "validation/reports/latest.json",
                "--receipt-dir",
                "data/receipts",
            ),
            pythonpath_env,
        ),
        CommandSpec(
            "ux_render_verification",
            ("python3", "-m", "sentinel_workbench.ux_verification"),
            pythonpath_env,
        ),
        CommandSpec("pip_dry_run", ("python3", "-m", "pip", "install", "-e", ".", "--dry-run", "--no-deps")),
        CommandSpec("git_diff_check", ("git", "diff", "--check")),
    )


def _run_command(spec: CommandSpec, cwd: Path) -> dict[str, Any]:
    env = os.environ.copy()
    if spec.env:
        env.update(spec.env)
    completed = subprocess.run(
        spec.command,
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "name": spec.name,
        "command": " ".join(spec.command),
        "exit_code": completed.returncode,
        "stdout_tail": _tail(completed.stdout),
        "stderr_tail": _tail(completed.stderr),
    }


def _command_passed(commands: list[dict[str, Any]], name: str) -> bool:
    return any(command["name"] == name and command["exit_code"] == 0 for command in commands)


def _check_json_syntax(root: Path) -> dict[str, Any]:
    patterns = (
        "schemas/*.json",
        "data/cases/*.json",
        "data/static_inputs/*.json",
        "data/receipts/json/*.json",
        "data/prepared_inputs/constructed_demo_case/**/*.json",
        "validation/reports/*.json",
    )
    checked: list[str] = []
    errors: list[str] = []
    for pattern in patterns:
        for path in sorted(root.glob(pattern)):
            if not path.is_file():
                continue
            checked.append(str(path.relative_to(root)))
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"{path.relative_to(root)}:{exc.lineno}:{exc.colno}:{exc.msg}")
    return {
        "passed": errors == [],
        "checked_count": len(checked),
        "errors": errors,
    }


def _tail(text: str, *, line_count: int = 20) -> str:
    lines = [line.rstrip() for line in text.splitlines() if line.rstrip()]
    return "\n".join(lines[-line_count:])


def main() -> None:
    parser = argparse.ArgumentParser(description="Run final local verification and regenerate the GOAL.md audit.")
    parser.add_argument("--report", default="validation/reports/final_verification.json")
    parser.add_argument("--goal-audit-json", default="validation/reports/goal_completion_audit.json")
    parser.add_argument("--goal-audit-markdown", default="docs/21_goal_completion_audit.md")
    args = parser.parse_args()

    report = run_final_verification(
        report_path=args.report,
        goal_audit_json_path=args.goal_audit_json,
        goal_audit_markdown_path=args.goal_audit_markdown,
    )
    print(
        "final_verification_all_pass="
        f"{report['all_pass']} goal_audit_all_pass={report['goal_audit_all_pass_after_regeneration']}"
    )
    if not report["all_pass"] or not report["goal_audit_all_pass_after_regeneration"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
