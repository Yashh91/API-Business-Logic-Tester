
"""Checks for duplicate API actions and repeated submissions."""

from typing import Any

from api_tester.engine.scenario import ScenarioResult
from api_tester.engine.evidence import redact_sensitive_data


def check_duplicate_action(
    *,
    scenario_id: str,
    scenario_name: str,
    first_response: dict[str, Any],
    second_response: dict[str, Any],
    duplicate_confirmed: bool = False,
    duplicate_evidence: dict[str, Any] | None = None,
) -> ScenarioResult:
    """Evaluate evidence from two submissions of the same logical action.

    This function does not send requests. The caller must execute
    an authorized test and supply both responses.

    Set duplicate_confirmed=True only when independent evidence
    verifies that an unintended duplicate resource was created.
    """
    if not scenario_id.strip() or not scenario_name.strip():
        raise ValueError("Scenario ID and scenario name are required.")

    responses = [first_response, second_response]

    for response in responses:
        if not isinstance(response, dict):
            raise ValueError("Each response must be a dictionary.")

        if not response.get("ok"):
            error = response.get("error", "unknown error")

            return ScenarioResult(
                scenario_id=scenario_id,
                name=scenario_name,
                status="INCONCLUSIVE",
                summary=(
                    "Both submissions could not be evaluated reliably; "
                    f"request error: {error}."
                ),
                evidence=[
                    {
                        "type": "request_error",
                        "error": str(error),
                    }
                ],
            )

        if not isinstance(response.get("status_code"), int):
            return ScenarioResult(
                scenario_id=scenario_id,
                name=scenario_name,
                status="INCONCLUSIVE",
                summary=(
                    "A submission did not contain a valid HTTP status code."
                ),
            )

    evidence: list[dict[str, Any]] = [
        {
            "type": "duplicate_action_comparison",
            "first_status_code": first_response["status_code"],
            "second_status_code": second_response["status_code"],
            "duplicate_confirmed": duplicate_confirmed,
        }
    ]

    if duplicate_evidence:
        evidence.append(
            {
                "type": "duplicate_resource_evidence",
                "details": redact_sensitive_data(duplicate_evidence),
            }
        )

    if duplicate_confirmed:
        return ScenarioResult(
            scenario_id=scenario_id,
            name=scenario_name,
            status="VULNERABLE",
            summary=(
                "Evidence confirms that repeated submissions created "
                "an unintended duplicate resource."
            ),
            evidence=evidence,
            remediation=(
                "Enforce server-side idempotency or an equivalent "
                "deduplication control. Validate action state and "
                "prevent unintended repeated resource creation."
            ),
            observed_status_code=second_response["status_code"],
        )

    return ScenarioResult(
        scenario_id=scenario_id,
        name=scenario_name,
        status="INCONCLUSIVE",
        summary=(
            "Two responses were received, but response codes alone "
            "cannot establish whether a duplicate resource was created. "
            "Compare resource IDs and server-side state in the test "
            "environment before drawing a conclusion."
        ),
        evidence=evidence,
        remediation=(
            "Where repeated submissions must not create duplicate "
            "resources, consider server-side idempotency controls "
            "and atomic state validation."
        ),
        observed_status_code=second_response["status_code"],
    )
