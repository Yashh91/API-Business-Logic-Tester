
"""Evidence-based authorization checks for API responses."""

from typing import Any

from api_tester.engine.scenario import ScenarioResult
from api_tester.engine.evidence import redact_sensitive_data


def check_authorization_response(
    *,
    scenario_id: str,
    scenario_name: str,
    response: dict[str, Any],
    expected_denial_codes: list[int] | None = None,
    protected_resource_confirmed: bool = False,
) -> ScenarioResult:
    """Evaluate an authorization test response.

    Only set protected_resource_confirmed=True when independent,
    reliable evidence confirms that a protected resource was exposed
    to a caller who should not have access.
    """
    if not scenario_id.strip() or not scenario_name.strip():
        raise ValueError("Scenario ID and name are required.")

    denial_codes = expected_denial_codes or [401, 403]

    if any(
        not isinstance(code, int) or not 100 <= code <= 599
        for code in denial_codes
    ):
        raise ValueError(
            "Expected denial codes must be valid HTTP status codes."
        )

    if not response.get("ok"):
        error = str(response.get("error", "unknown error"))

        return ScenarioResult(
            scenario_id=scenario_id,
            name=scenario_name,
            status="INCONCLUSIVE",
            summary=f"Authorization could not be evaluated: {error}.",
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

    evidence = [
        {
            "type": "authorization_response",
            "status_code": status_code,
            "expected_denial_codes": denial_codes,
            "protected_resource_confirmed": protected_resource_confirmed,
            "response_body_excerpt": (
                body[:1000] if isinstance(body, str) else body
            ),
        }
    ]

    if protected_resource_confirmed:
        return ScenarioResult(
            scenario_id=scenario_id,
            name=scenario_name,
            status="VULNERABLE",
            summary=(
                "Evidence confirms that a protected resource was "
                "exposed without the required authorization."
            ),
            evidence=evidence,
            remediation=(
                "Enforce server-side authorization for every request. "
                "Verify resource ownership and permissions before "
                "returning protected data."
            ),
            observed_status_code=status_code,
        )

    if status_code in denial_codes:
        return ScenarioResult(
            scenario_id=scenario_id,
            name=scenario_name,
            status="PASS",
            summary=(
                f"The API returned HTTP {status_code}, matching "
                "the configured authorization-denial response."
            ),
            evidence=evidence,
            observed_status_code=status_code,
        )

    return ScenarioResult(
        scenario_id=scenario_id,
        name=scenario_name,
        status="INCONCLUSIVE",
        summary=(
            f"The API returned HTTP {status_code}, rather than an "
            "expected denial response. Verify the response body and "
            "resource ownership before determining whether a "
            "vulnerability exists."
        ),
        evidence=evidence,
        remediation=(
            "Review server-side access-control rules and verify that "
            "users can access only resources they are authorized to use."
        ),
        observed_status_code=status_code,
    )
