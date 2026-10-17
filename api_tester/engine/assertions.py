
"""Evidence-based assertions for API security test scenarios."""

from typing import Any

from api_tester.engine.scenario import Scenario, ScenarioResult


def evaluate_status_code(
    scenario: Scenario,
    response: dict[str, Any],
) -> ScenarioResult:
    """Evaluate an HTTP response against a scenario's expected status codes."""

    if not scenario.enabled:
        return ScenarioResult(
            scenario_id=scenario.scenario_id,
            name=scenario.name,
            status="NOT_TESTED",
            summary="This scenario is disabled in the configuration.",
        )

    if not response.get("ok"):
        error = response.get("error", "unknown error")

        return ScenarioResult(
            scenario_id=scenario.scenario_id,
            name=scenario.name,
            status="INCONCLUSIVE",
            summary=f"No reliable HTTP response was available: {error}.",
            evidence=[
                {
                    "type": "request_error",
                    "error": str(error),
                }
            ],
        )

    observed_status = response.get("status_code")

    if not isinstance(observed_status, int):
        return ScenarioResult(
            scenario_id=scenario.scenario_id,
            name=scenario.name,
            status="INCONCLUSIVE",
            summary="The response did not contain a valid HTTP status code.",
        )

    expected = scenario.expected_status_codes

    if not expected:
        return ScenarioResult(
            scenario_id=scenario.scenario_id,
            name=scenario.name,
            status="INCONCLUSIVE",
            summary=(
                "No expected status codes are configured; "
                "the response cannot be evaluated against an expectation."
            ),
            observed_status_code=observed_status,
            evidence=[
                {
                    "type": "http_response",
                    "observed_status_code": observed_status,
                }
            ],
        )

    if observed_status in expected:
        return ScenarioResult(
            scenario_id=scenario.scenario_id,
            name=scenario.name,
            status="PASS",
            summary=(
                f"Received expected HTTP status {observed_status}."
            ),
            observed_status_code=observed_status,
            evidence=[
                {
                    "type": "http_status_comparison",
                    "expected_status_codes": expected,
                    "observed_status_code": observed_status,
                    "matched": True,
                }
            ],
        )

    return ScenarioResult(
        scenario_id=scenario.scenario_id,
        name=scenario.name,
        status="INCONCLUSIVE",
        summary=(
            f"Expected HTTP status {expected}, "
            f"but received {observed_status}. "
            "Further investigation is required."
        ),
        observed_status_code=observed_status,
        evidence=[
            {
                "type": "http_status_comparison",
                "expected_status_codes": expected,
                "observed_status_code": observed_status,
                "matched": False,
            }
        ],
    )
