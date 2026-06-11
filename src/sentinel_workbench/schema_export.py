from __future__ import annotations

import argparse
import json
from pathlib import Path

from .models import DecisionEpisode
from .approval import export_approval_schemas
from .receipts import export_receipt_schema
from .redaction import export_redaction_report_schema
from .static_inputs import export_static_input_schemas


def export_schema(output_path: str | Path = "schemas/ed_decision_episode.schema.json") -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(DecisionEpisode.model_json_schema(), indent=2) + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Export Sentinel Workbench JSON schemas.")
    parser.add_argument("output_path", nargs="?", default="schemas/ed_decision_episode.schema.json")
    args = parser.parse_args()
    path = export_schema(args.output_path)
    export_static_input_schemas(Path(args.output_path).parent)
    export_receipt_schema(Path(args.output_path).parent / "ed_sentinel_receipt.schema.json")
    export_redaction_report_schema(Path(args.output_path).parent / "redaction_report.schema.json")
    export_approval_schemas(Path(args.output_path).parent)
    print(path)


if __name__ == "__main__":
    main()
