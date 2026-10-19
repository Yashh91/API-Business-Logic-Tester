
"""Compare secure and confirmed-vulnerable evaluator outcomes."""

import unittest

from api_tester.checks.authorization import (
    check_authorization_response,
)
from api_tester.checks.duplicate_actions import (
    check_duplicate_action,
)
from api_tester.checks.input_validation import (
    check_input_validation,
)
from api_tester.checks.state_transitions import (
    check_state_transition,
)


class TestSecureVersusVulnerable(unittest.TestCase):
    def test_authorization_denial_vs_confirmed_exposure(self):
        secure_result = check_authorization_response(
            scenario_id="AUTH-SECURE",
            scenario_name="Secure ownership enforcement",
            response={
                "ok": True,
                "status_code": 403,
                "body": {"error": "Forbidden"},
            },
        )

        vulnerable_result = check_authorization_response(
            scenario_id="AUTH-VULN",
            scenario_name="Confirmed unauthorized exposure",
            response={
                "ok": True,
                "status_code": 200,
                "body": {"order_id": "synthetic-order"},
            },
            protected_resource_confirmed=True,
        )

        self.assertEqual(secure_result.status, "PASS")
        self.assertEqual(vulnerable_result.status, "VULNERABLE")

    def test_input_rejection_vs_confirmed_invalid_acceptance(self):
        secure_result = check_input_validation(
            scenario_id="INPUT-SECURE",
            scenario_name="Reject invalid quantity",
            response={
                "ok": True,
                "status_code": 422,
                "body": {"error": "Invalid quantity"},
            },
            invalid_input_rejected=True,
        )

        vulnerable_result = check_input_validation(
            scenario_id="INPUT-VULN",
            scenario_name="Invalid quantity accepted",
            response={
                "ok": True,
                "status_code": 201,
                "body": {"quantity": -1},
            },
            invalid_input_rejected=False,
        )

        self.assertEqual(secure_result.status, "PASS")
        self.assertEqual(vulnerable_result.status, "VULNERABLE")

    def test_no_duplicate_vs_confirmed_duplicate(self):
        first = {
            "ok": True,
            "status_code": 201,
            "body": {"booking_id": "booking-1"},
        }
        second = {
            "ok": True,
            "status_code": 200,
            "body": {"booking_id": "booking-1"},
        }

        secure_result = check_duplicate_action(
            scenario_id="DUP-SECURE",
            scenario_name="Idempotent repeated action",
            first_response=first,
            second_response=second,
            duplicate_confirmed=False,
        )

        vulnerable_result = check_duplicate_action(
            scenario_id="DUP-VULN",
            scenario_name="Duplicate resources confirmed",
            first_response=first,
            second_response={
                "ok": True,
                "status_code": 201,
                "body": {"booking_id": "booking-2"},
            },
            duplicate_confirmed=True,
            duplicate_evidence={
                "created_resource_ids": ["booking-1", "booking-2"],
                "same_logical_action": True,
            },
        )

        # Without independent confirmation, the result must not
        # claim a vulnerability or assert that the API is secure.
        self.assertEqual(secure_result.status, "INCONCLUSIVE")
        self.assertEqual(vulnerable_result.status, "VULNERABLE")

    def test_forbidden_transition_without_change_vs_confirmed_change(self):
        response = {
            "ok": True,
            "status_code": 200,
            "body": {"status": "shipped"},
        }

        unverified_result = check_state_transition(
            scenario_id="STATE-UNKNOWN",
            scenario_name="Unverified forbidden transition",
            initial_state="cancelled",
            attempted_action="ship",
            response=response,
            expected_allowed=False,
            state_change_confirmed=False,
        )

        vulnerable_result = check_state_transition(
            scenario_id="STATE-VULN",
            scenario_name="Forbidden transition changed state",
            initial_state="cancelled",
            attempted_action="ship",
            response=response,
            expected_allowed=False,
            resulting_state="shipped",
            state_change_confirmed=True,
        )

        self.assertEqual(unverified_result.status, "INCONCLUSIVE")
        self.assertEqual(vulnerable_result.status, "VULNERABLE")


if __name__ == "__main__":
    unittest.main()
