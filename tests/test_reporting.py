
"""Unit tests for JSON and Markdown assessment reports."""

import json
import tempfile
import unittest
from pathlib import Path

from api_tester.engine.scenario import ScenarioResult
from api_tester.reporting.json_report import export_json_report
from api_tester.reporting.markdown_report import export_markdown_report
from api_tester.reporting.models import TestReport


class TestReporting(unittest.TestCase):
    def setUp(self):
        self.report = TestReport(
            target_name="Local Test API",
            base_url="http://127.0.0.1:8000",
            metadata={"environment": "local-lab"},
        )

        self.report.add_result(
            ScenarioResult(
                scenario_id="AUTH-001",
                name="Protected resource access",
                status="PASS",
                summary="The expected denial response was received.",
                observed_status_code=403,
            )
        )

        self.report.add_result(
            ScenarioResult(
                scenario_id="INPUT-001",
                name="Negative quantity validation",
                status="VULNERABLE",
                summary="Invalid quantity acceptance was confirmed.",
                observed_status_code=201,
                evidence=[
                    {
                        "type": "input_validation",
                        "password": "example-secret",
                    }
                ],
                remediation="Validate quantity on the server.",
            )
        )

        self.report.add_result(
            ScenarioResult(
                scenario_id="DUP-001",
                name="Duplicate submission",
                status="INCONCLUSIVE",
                summary="Duplicate resource creation was not verified.",
            )
        )

        self.report.add_result(
            ScenarioResult(
                scenario_id="STATE-001",
                name="Unconfigured workflow check",
                status="NOT_TESTED",
                summary="This check has not been implemented by the runner.",
            )
        )

    def test_summary_counts_actual_results(self):
        self.assertEqual(
            self.report.summary,
            {
                "total": 4,
                "pass": 1,
                "vulnerable": 1,
                "inconclusive": 1,
                "not_tested": 1,
            },
        )

    def test_json_export_contains_summary_and_redacts_secrets(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "nested" / "report.json"

            export_json_report(self.report, str(output))

            self.assertTrue(output.is_file())

            data = json.loads(output.read_text(encoding="utf-8"))

            self.assertEqual(data["summary"]["total"], 4)
            self.assertEqual(data["summary"]["vulnerable"], 1)

            evidence = data["results"][1]["evidence"][0]
            self.assertEqual(evidence["password"], "[REDACTED]")

    def test_markdown_export_contains_results(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "report.md"

            export_markdown_report(self.report, str(output))

            content = output.read_text(encoding="utf-8")

            self.assertIn("# API Business Logic Security Assessment", content)
            self.assertIn("Protected resource access", content)
            self.assertIn("VULNERABLE", content)
            self.assertIn("Recommended remediation", content)
            self.assertIn("Not tested: 1", content)

    def test_empty_report_has_zero_counts(self):
        empty_report = TestReport(
            target_name="Empty Test API",
            base_url="http://127.0.0.1:8000",
        )

        self.assertEqual(empty_report.summary["total"], 0)
        self.assertEqual(empty_report.summary["vulnerable"], 0)

    def test_empty_target_name_is_rejected(self):
        with self.assertRaises(ValueError):
            TestReport(
                target_name=" ",
                base_url="http://127.0.0.1:8000",
            )


if __name__ == "__main__":
    unittest.main()
