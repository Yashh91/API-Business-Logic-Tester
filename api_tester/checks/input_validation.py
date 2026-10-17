
"""Evidence-based checks for API input validation."""

from typing import Any

from api_tester.engine.scenario import ScenarioResult
from api_tester.engine.evidence import redact_sensitive_data


def check_input_validation(
    *,
    scenario_id: str,
    scenario_name: str,
    response: dict[str, Any],
    expected_rejection_codes: list[int] | None = None,
    invalid_input_rejected: bool | None = None,
    input_description: str = "configured invalid input",
) -> ScenarioResult:
    """Evaluate how an API handled a deliberately invalid test input.

    This function evaluates a response; it does not send a request.

    Set invalid_input_rejected=True only when the response or other
    reliable evidence confirms that the invalid input was rejected.
    Set it to False only when evidence confirms the invalid input was
    accepted in a way that violates the application's requirements.
    Otherwise, leave it as None.
    """
    if not scenario_id.strip() or not scenario_name.strip():
        raise ValueError("Scenario ID and scenario name are required.")

    if not input_description.strip():
        raise ValueError("input_description cannot be empty.")

    rejection_codes = expected_rejection_codes or [400, 422]

    if any(
        not isinstance(code, int) or not 100 <= code <= 599
        for code in rejection_codes
    ):
        raise ValueError(
            "Expected rejection codes must be valid HTTP status codes."
        )

    if not response.get("ok"):
        error = str(response.get("error", "unknown error"))

        return ScenarioResult(
            scenario_id=scenario_id,
            name=scenario_name,
            status="INCONCLUSIVE",
            summary=f"Input validation could not be evaluated: {error}.",
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

    body = redact_sensitive_data(response.get("body"))

    evidence: list[dict[str, Any]] = [
        {
            "type": "input_validation",
            "input_description": input_description,
            "status_code": status_code,
            "expected_rejection_codes": rejection_codes,
            "response_body_excerpt": (
                body[:1000] if isinstance(body, str) else body
            ),
        }
    ]

    if invalid_input_rejected is True:
        return ScenarioResult(
            scenario_id=scenario_id,
            name=scenario_name,
            status="PASS",
            summary="Evidence confirms the invalid input was rejected.",
            evidence=evidence,
            observed_status_code=status_code,
        )

    if invalid_input_rejected is False:
        return ScenarioResult(
            scenario_id=scenario_id,
            name=scenario_name,
            status="VULNERABLE",
            summary=(
                "Evidence confirms the API accepted invalid input "
                "in violation of the configured application requirements."
            ),
            evidence=evidence,
            remediation=(
                "Validate input on the server using explicit type, "
                "range, format, and business-rule constraints. Reject "
                "invalid values before processing or changing state."
            ),
            observed_status_code=status_code,
        )

    if status_code in rejection_codes:
        return ScenarioResult(
            scenario_id=scenario_id,
            name=scenario_name,
            status="PASS",
            summary=(
                f"The API returned HTTP {status_code}, matching a "
                "configured input-rejection status. Verify the response "
                "to confirm the invalid input was actually rejected."
            ),
            evidence=evidence,
            observed_status_code=status_code,
        )

    return ScenarioResult(
        scenario_id=scenario_id,
        name=scenario_name,
        status="INCONCLUSIVE",
        summary=(
            f"The API returned HTTP {status_code}. The response alone "
            "does not establish whether the invalid input violated "
            "the application's business rules."
        ),
        evidence=evidence,
        remediation=(
            "Define expected input constraints and verify that the "
            "server rejects invalid values without unintended state changes."
        ),
        observed_status_code=status_code,
    )
