
"""Export API security assessment reports to JSON."""

import json
from pathlib import Path
from typing import Any

from api_tester.reporting.models import TestReport
from api_tester.engine.evidence import redact_sensitive_data


def export_json_report(
    report: TestReport,
    output_path: str,
) -> Path:
    """Write a sanitized assessment report to a JSON file."""

    if not isinstance(report, TestReport):
        raise TypeError("report must be a TestReport instance.")

    if not output_path.strip():
        raise ValueError("output_path cannot be empty.")

    destination = Path(output_path)

    # Create the output directory when needed.
    destination.parent.mkdir(parents=True, exist_ok=True)

    report_data: dict[str, Any] = redact_sensitive_data(
        report.to_dict()
    )

    with destination.open("w", encoding="utf-8") as file:
        json.dump(
            report_data,
            file,
            indent=2,
            ensure_ascii=False,
        )
        file.write("\n")

    return destination
