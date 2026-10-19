
"""Unit tests for API input validation evaluation."""

import unittest

from api_tester.checks.input_validation import (
    check_input_validation,
)


class TestInputValidationCheck(unittest.TestCase):
    def setUp(self):
        self.response = {
            "ok": True,
            "status_code": 422,
            "body": {"error": "quantity must be positive"},
        }

    def test_confirmed_rejection_passes(self):
        result = check_input_validation(
            scenario_id="INPUT-001",
            scenario_name="Reject negative quantity",
            response=self.response,
            invalid_input_rejected=True,
            input_description="Negative quantity",
        )

        self.assertEqual(result.status, "PASS")

    def test_confirmed_acceptance_of_invalid_input_is_vulnerable(self):
        response = {
            "ok": True,
            "status_code": 201,
            "body": {
                "order_id": "order-test-1",
                "quantity": -1,
            },
        }

        result = check_input_validation(
            scenario_id="INPUT-002",
            scenario_name="Negative quantity accepted",
            response=response,
            invalid_input_rejected=False,
            input_description="Negative quantity",
        )

        self.assertEqual(result.status, "VULNERABLE")
        self.assertTrue(result.remediation)

    def test_rejection_status_without_confirmation_passes(self):
        result = check_input_validation(
            scenario_id="INPUT-003",
            scenario_name="Rejection status observed",
            response=self.response,
            input_description="Invalid quantity",
        )

        self.assertEqual(result.status, "PASS")

    def test_unexpected_status_without_evidence_is_inconclusive(self):
        response = {
            "ok": True,
            "status_code": 200,
            "body": {"message": "Request processed"},
        }

        result = check_input_validation(
            scenario_id="INPUT-004",
            scenario_name="Input handling needs review",
            response=response,
            input_description="Invalid quantity",
        )

        self.assertEqual(result.status, "INCONCLUSIVE")

    def test_request_error_is_inconclusive(self):
        failed_response = {
            "ok": False,
            "error": "timeout",
            "status_code": None,
            "body": None,
        }

        result = check_input_validation(
            scenario_id="INPUT-005",
            scenario_name="Input validation timeout",
            response=failed_response,
        )

        self.assertEqual(result.status, "INCONCLUSIVE")

    def test_invalid_expected_status_code_is_rejected(self):
        with self.assertRaises(ValueError):
            check_input_validation(
                scenario_id="INPUT-006",
                scenario_name="Invalid status configuration",
                response=self.response,
                expected_rejection_codes=[999],
            )


if __name__ == "__main__":
    unittest.main()
