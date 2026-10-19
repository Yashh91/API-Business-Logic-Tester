
"""Unit tests for duplicate API action evaluation."""

import unittest

from api_tester.checks.duplicate_actions import (
    check_duplicate_action,
)


class TestDuplicateActionCheck(unittest.TestCase):
    def setUp(self):
        self.first_response = {
            "ok": True,
            "status_code": 201,
            "body": {"booking_id": "booking-test-1"},
        }

        self.second_response = {
            "ok": True,
            "status_code": 201,
            "body": {"booking_id": "booking-test-2"},
        }

    def test_confirmed_duplicate_is_vulnerable(self):
        result = check_duplicate_action(
            scenario_id="DUP-001",
            scenario_name="Repeated booking submission",
            first_response=self.first_response,
            second_response=self.second_response,
            duplicate_confirmed=True,
            duplicate_evidence={
                "created_resource_ids": [
                    "booking-test-1",
                    "booking-test-2",
                ],
                "same_logical_action": True,
            },
        )

        self.assertEqual(result.status, "VULNERABLE")
        self.assertTrue(result.remediation)

    def test_two_success_responses_are_inconclusive(self):
        result = check_duplicate_action(
            scenario_id="DUP-002",
            scenario_name="Repeated submission without state evidence",
            first_response=self.first_response,
            second_response=self.second_response,
        )

        self.assertEqual(result.status, "INCONCLUSIVE")

    def test_request_error_is_inconclusive(self):
        failed_response = {
            "ok": False,
            "error": "timeout",
            "status_code": None,
            "body": None,
        }

        result = check_duplicate_action(
            scenario_id="DUP-003",
            scenario_name="Repeated submission timeout",
            first_response=self.first_response,
            second_response=failed_response,
        )

        self.assertEqual(result.status, "INCONCLUSIVE")

    def test_invalid_response_is_rejected(self):
        with self.assertRaises(ValueError):
            check_duplicate_action(
                scenario_id="DUP-004",
                scenario_name="Invalid response",
                first_response=None,
                second_response=self.second_response,
            )


if __name__ == "__main__":
    unittest.main()
