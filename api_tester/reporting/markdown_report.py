
"""Export API security assessment reports to Markdown."""

from pathlib import Path

from api_tester.reporting.models import TestReport


def export_markdown_report(
    report: TestReport,
    output_path: str,
) -> Path:
    """Write a human-readable Markdown assessment report."""

    if not isinstance(report, TestReport):
        raise TypeError("report must be a TestReport instance.")

    if not output_path.strip():
        raise ValueError("output_path cannot be empty.")

    summary = report.summary

    lines = [
        "# API Business Logic Security Assessment",
        "",
        f"**Target:** {report.target_name}",
        f"**Base URL:** `{report.base_url}`",
        f"**Assessment started:** {report.started_at}",
        "",
        "## Summary",
        "",
        f"- Total scenarios: {summary['total']}",
        f"- Passed: {summary['pass']}",
        f"- Vulnerable: {summary['vulnerable']}",
        f"- Inconclusive: {summary['inconclusive']}",
        f"- Not tested: {summary['not_tested']}",
        "",
        "> Results reflect the evidence supplied to the framework. "
        "Review each finding before making security decisions.",
        "",
        "## Scenario Results",
        "",
    ]

    if not report.results:
        lines.extend(
            [
                "No scenario results are available.",
                "",
            ]
        )

    for result in report.results:
        lines.extend(
            [
                f"### {result.name}",
                "",
                f"- **ID:** `{result.scenario_id}`",
                f"- **Status:** `{result.status}`",
                f"- **Observed HTTP status:** "
                f"`{result.observed_status_code if result.observed_status_code is not None else 'N/A'}`",
                "",
                result.summary,
                "",
            ]
        )

        if result.evidence:
            lines.extend(["**Evidence**", ""])
            for item in result.evidence:
                # Keep evidence readable without dumping huge objects.
                lines.append(
                    f"- `{item.get('type', 'observation')}`: "
                    f"{str(item)[:1000]}"
                )
            lines.append("")

        if result.remediation:
            lines.extend(
                [
                    "**Recommended remediation**",
                    "",
                    result.remediation,
                    "",
                ]
            )

        lines.append("---")
        lines.append("")

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    return destination
