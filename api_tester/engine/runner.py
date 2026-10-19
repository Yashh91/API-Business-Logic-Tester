
"""Execute configured API scenarios and collect their results."""

import re
from typing import Any

from adapters.rest import RESTAdapter
from api_tester.checks.authorization import (
    check_authorization_response,
)
from api_tester.checks.input_validation import (
    check_input_validation,
)
from api_tester.engine.scenario import Scenario, ScenarioResult


PLACEHOLDER_PATTERN = re.compile(r"\{[^{}]+\}")


def build_scenario(data: dict[str, Any]) -> Scenario:
    """Convert one configuration mapping into a validated scenario."""
    return Scenario(
        scenario_id=data["scenario_id"],
        name=data["name"],
        description=data.get("description", data["name"]),
        check_type=data["check_type"],
        request_method=data["request_method"],
        request_path=data["request_path"],
        expected_status_codes=data.get("expected_status_codes", []),
        request_params=data.get("request_params", {}),
        request_body=data.get("request_body", {}),
        enabled=data.get("enabled", True),
    )


def run_scenario(
    scenario: Scenario,
    adapter: RESTAdapter,
) -> ScenarioResult:
    """Execute a supported scenario and evaluate its response."""

    if not scenario.enabled:
        return ScenarioResult(
            scenario_id=scenario.scenario_id,
            name=scenario.name,
            status="NOT_TESTED",
            summary="Scenario is disabled in the configuration.",
        )

    if PLACEHOLDER_PATTERN.search(scenario.request_path):
        return ScenarioResult(
            scenario_id=scenario.scenario_id,
            name=scenario.name,
            status="NOT_TESTED",
            summary=(
                "The request path contains unresolved placeholders. "
                "Supply authorized test resource IDs before running it."
            ),
        )

    supported_checks = {"authorization", "input_validation"}

    if scenario.check_type not in supported_checks:
        return ScenarioResult(
            scenario_id=scenario.scenario_id,
            name=scenario.name,
            status="NOT_TESTED",
            summary=(
                f"The '{scenario.check_type}' check requires additional "
                "workflow or resource-state verification that the current "
                "runner does not implement yet."
            ),
        )

    response = adapter.send(
        scenario.request_method,
        scenario.request_path,
        params=scenario.request_params or None,
        json_body=scenario.request_body or None,
    )

    if scenario.check_type == "authorization":
        return check_authorization_response(
            scenario_id=scenario.scenario_id,
            scenario_name=scenario.name,
            response=response,
            expected_denial_codes=(
                scenario.expected_status_codes or [401, 403]
            ),
        )

    if scenario.check_type == "input_validation":
        return check_input_validation(
            scenario_id=scenario.scenario_id,
            scenario_name=scenario.name,
            response=response,
            expected_rejection_codes=(
                scenario.expected_status_codes or [400, 422]
            ),
            input_description=scenario.description,
        )

    return ScenarioResult(
        scenario_id=scenario.scenario_id,
        name=scenario.name,
        status="NOT_TESTED",
        summary="No compatible check handler was found.",
    )


def run_scenarios(
    scenario_configs: list[dict[str, Any]],
    adapter: RESTAdapter,
) -> list[ScenarioResult]:
    """Run configured scenarios and return their individual results."""
    results: list[ScenarioResult] = []

    for scenario_config in scenario_configs:
        try:
            scenario = build_scenario(scenario_config)
            result = run_scenario(scenario, adapter)
        except (KeyError, TypeError, ValueError) as exc:
            scenario_id = str(
                scenario_config.get("scenario_id", "UNKNOWN")
            )
            scenario_name = str(
                scenario_config.get("name", "Invalid scenario")
            )

            result = ScenarioResult(
                scenario_id=scenario_id,
                name=scenario_name,
                status="INCONCLUSIVE",
                summary=f"Scenario configuration error: {exc}",
            )

        results.append(result)

    return results
