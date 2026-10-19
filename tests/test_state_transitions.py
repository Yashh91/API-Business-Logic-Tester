
"""Unit tests for API business workflow state transitions."""

import unittest

from api_tester.checks.state_transitions import (
    check_state_transition,
)


class TestStateTransitionCheck(unittest.TestCase):
    def setUp(self):
        self.response = {
            "ok": True,
            "status_code": 200,
            "body": {"status": "confirmed"},
        }

    def test_confirmed_allowed_transition_passes(self):
        result = check_state_transition(
            scenario_id="STATE-001",
            scenario_name="Confirm pending booking",
            initial_state="pending",
            attempted_action="confirm",
            response=self.response,
            expected_allowed=True,
            resulting_state="confirmed",
            state_change_confirmed=True,
        )

        self.assertEqual(result.status, "PASS")

    def test_forbidden_transition_that_changes_state_is_vulnerable(self):
        result = check_state_transition(
            scenario_id="STATE-002",
            scenario_name="Ship an order in a forbidden state",
            initial_state="cancelled",
            attempted_action="ship",
            response=self.response,
            expected_allowed=False,
            resulting_state="shipped",
            state_change_confirmed=True,
        )

        self.assertEqual(result.status, "VULNERABLE")
        self.assertTrue(result.remediation)

    def test_unverified_state_change_is_inconclusive(self):
        result = check_state_transition(
            scenario_id="STATE-003",
            scenario_name="Unverified transition",
            initial_state="pending",
            attempted_action="confirm",
            response=self.response,
            expected_allowed=False,
        )

        self.assertEqual(result.status, "INCONCLUSIVE")

    def test_request_error_is_inconclusive(self):
        failed_response = {
            "ok": False,
            "error": "timeout",
            "status_code": None,
            "body": None,
        }

        result = check_state_transition(
            scenario_id="STATE-004",
            scenario_name="Transition timeout",
            initial_state="pending",
            attempted_action="confirm",
            response=failed_response,
            expected_allowed=True,
        )

        self.assertEqual(result.status, "INCONCLUSIVE")

    def test_empty_initial_state_is_rejected(self):
        with self.assertRaises(ValueError):
            check_state_transition(
                scenario_id="STATE-005",
                scenario_name="Invalid scenario",
                initial_state=" ",
                attempted_action="confirm",
                response=self.response,
                expected_allowed=True,
            )


if __name__ == "__main__":
    unittest.main()
