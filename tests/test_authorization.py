
"""Unit tests for API authorization response evaluation."""

import unittest

from api_tester.checks.authorization import (
    check_authorization_response,
)


class TestAuthorizationCheck(unittest.TestCase):
    def setUp(self):
        self.base_response = {
            "ok": True,
            "status_code": 403,
            "body": {"error": "Forbidden"},
        }

    def test_expected_denial_passes(self):
        result = check_authorization_response(
            scenario_id="AUTH-001",
            scenario_name="Protected resource access",
            response=self.base_response,
        )

        self.assertEqual(result.status, "PASS")
        self.assertEqual(result.observed_status_code, 403)

    def test_confirmed_unauthorized_exposure_is_vulnerable(self):
        response = {
            "ok": True,
            "status_code": 200,
            "body": {
                "order_id": "order-test-1",
                "owner_id": "user-test-1",
            },
        }

        result = check_authorization_response(
            scenario_id="AUTH-002",
            scenario_name="Cross-user resource access",
            response=response,
            protected_resource_confirmed=True,
        )

        self.assertEqual(result.status, "VULNERABLE")
        self.assertTrue(result.remediation)

    def test_unexpected_status_is_inconclusive_without_proof(self):
        response = {
            "ok": True,
            "status_code": 200,
            "body": {"message": "Request completed"},
        }

        result = check_authorization_response(
            scenario_id="AUTH-003",
            scenario_name="Authorization needs review",
            response=response,
        )

        self.assertEqual(result.status, "INCONCLUSIVE")

    def test_request_error_is_inconclusive(self):
        response = {
            "ok": False,
            "error": "timeout",
            "status_code": None,
            "body": None,
        }

        result = check_authorization_response(
            scenario_id="AUTH-004",
            scenario_name="Authorization timeout",
            response=response,
        )

        self.assertEqual(result.status, "INCONCLUSIVE")

    def test_invalid_denial_status_code_is_rejected(self):
        with self.assertRaises(ValueError):
            check_authorization_response(
                scenario_id="AUTH-005",
                scenario_name="Invalid configuration",
                response=self.base_response,
                expected_denial_codes=[999],
            )


if __name__ == "__main__":
    unittest.main()
