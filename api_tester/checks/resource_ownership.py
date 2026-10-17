
"""Checks for API resource ownership and access control."""

from typing import Any

from api_tester.engine.scenario import ScenarioResult
from api_tester.engine.evidence import redact_sensitive_data


def check_resource_ownership(
    *,
    scenario_id: str,
    scenario_name: str,
    expected_owner_id: str,
    observed_owner_id: str | None,
    response: dict[str, Any],
    ownership_mismatch_confirmed: bool = False,
) -> ScenarioResult:
    """Evaluate resource ownership using independently verified evidence.

    Use synthetic IDs or approved test-account identifiers in evidence.
    Do not treat a missing owner field as proof of a vulnerability.
    """
    required_values = {
        "scenario_id": scenario_id,
        "scenario_name": scenario_name,
        "expected_owner_id": expected_owner_id,
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
            summary=f"Resource ownership could not be evaluated: {error}.",
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
            "type": "resource_ownership",
            "expected_owner_id": expected_owner_id,
            "observed_owner_id": observed_owner_id,
            "ownership_mismatch_confirmed": ownership_mismatch_confirmed,
            "http_status_code": status_code,
            "response_body_excerpt": (
                body[:1000] if isinstance(body, str) else body
            ),
        }
    ]

    if ownership_mismatch_confirmed:
        return ScenarioResult(
            scenario_id=scenario_id,
            name=scenario_name,
            status="VULNERABLE",
            summary=(
                "Evidence confirms that the API exposed a resource "
                "owned by a different user without proper authorization."
            ),
            evidence=evidence,
            remediation=(
                "Enforce server-side resource-level authorization. "
                "Resolve the resource and verify the authenticated "
                "principal's permissions before returning its data."
            ),
            observed_status_code=status_code,
        )

    if observed_owner_id is None:
        return ScenarioResult(
            scenario_id=scenario_id,
            name=scenario_name,
            status="INCONCLUSIVE",
            summary=(
                "The resource owner could not be established from "
                "the supplied evidence."
            ),
            evidence=evidence,
            observed_status_code=status_code,
        )

    if observed_owner_id != expected_owner_id:
        return ScenarioResult(
            scenario_id=scenario_id,
            name=scenario_name,
            status="INCONCLUSIVE",
            summary=(
                "The observed owner differs from the expected owner. "
                "Verify the caller's identity, resource context, and "
                "authorization before confirming a vulnerability."
            ),
            evidence=evidence,
            observed_status_code=status_code,
        )

    return ScenarioResult(
        scenario_id=scenario_id,
        name=scenario_name,
        status="PASS",
        summary=(
            "The observed resource owner matches the expected owner."
        ),
        evidence=evidence,
        observed_status_code=status_code,
    )
