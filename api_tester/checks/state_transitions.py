
"""Checks for invalid API business workflow state transitions."""

from typing import Any

from api_tester.engine.scenario import ScenarioResult
from api_tester.engine.evidence import redact_sensitive_data


def check_state_transition(
    *,
    scenario_id: str,
    scenario_name: str,
    initial_state: str,
    attempted_action: str,
    response: dict[str, Any],
    expected_allowed: bool,
    resulting_state: str | None = None,
    state_change_confirmed: bool = False,
) -> ScenarioResult:
    """Evaluate an action against expected business workflow rules.

    The caller must supply states observed in an authorized test
    environment. This function does not send requests or retrieve
    application state by itself.
    """
    required_values = {
        "scenario_id": scenario_id,
        "scenario_name": scenario_name,
        "initial_state": initial_state,
        "attempted_action": attempted_action,
    }

    for field_name, value in required_values.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"{field_name} must be a non-empty string."
            )

    if not response.get("ok"):
        error = str(response.get("error", "unknown error"))

        return ScenarioResult(
            scenario_id=scenario_id,
            name=scenario_name,
            status="INCONCLUSIVE",
            summary=f"The state transition could not be evaluated: {error}.",
            evidence=[{"type": "request_error", "error": error}],
        )

    status_code = response.get("status_code")

    if not isinstance(status_code, int):
        return ScenarioResult(
            scenario_id=scenario_id,
            name=scenario_name,
            status="INCONCLUSIVE",
            summary="The response has no valid HTTP status code.",
        )

    observed_state = resulting_state
    body = redact_sensitive_data(response.get("body"))

    evidence: list[dict[str, Any]] = [
        {
            "type": "state_transition",
            "initial_state": initial_state,
            "attempted_action": attempted_action,
            "expected_allowed": expected_allowed,
            "http_status_code": status_code,
            "resulting_state": observed_state,
            "state_change_confirmed": state_change_confirmed,
            "response_body_excerpt": (
                body[:1000] if isinstance(body, str) else body
            ),
        }
    ]

    if expected_allowed:
        if state_change_confirmed:
            return ScenarioResult(
                scenario_id=scenario_id,
                name=scenario_name,
                status="PASS",
                summary=(
                    "The expected state transition was confirmed."
                ),
                evidence=evidence,
                observed_status_code=status_code,
            )

        return ScenarioResult(
            scenario_id=scenario_id,
            name=scenario_name,
            status="INCONCLUSIVE",
            summary=(
                "The action was expected to be allowed, but the "
                "resulting state has not been independently verified."
            ),
            evidence=evidence,
            observed_status_code=status_code,
        )

    if state_change_confirmed:
        return ScenarioResult(
            scenario_id=scenario_id,
            name=scenario_name,
            status="VULNERABLE",
            summary=(
                "Evidence confirms that an action expected to be "
                "forbidden changed the application's state."
            ),
            evidence=evidence,
            remediation=(
                "Enforce allowed state transitions on the server. "
                "Validate the current state and authorization atomically "
                "before applying each state-changing operation."
            ),
            observed_status_code=status_code,
        )

    return ScenarioResult(
        scenario_id=scenario_id,
        name=scenario_name,
        status="INCONCLUSIVE",
        summary=(
            "The action was expected to be forbidden, but evidence "
            "does not yet confirm whether the application state changed."
        ),
        evidence=evidence,
        remediation=(
            "Define valid workflow transitions and verify that "
            "forbidden actions leave application state unchanged."
        ),
        observed_status_code=status_code,
    )
