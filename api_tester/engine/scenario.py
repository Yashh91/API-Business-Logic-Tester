
"""Data models for API business logic test scenarios."""

from dataclasses import dataclass, field
from typing import Any, Literal


ScenarioStatus = Literal[
    "PASS",
    "VULNERABLE",
    "INCONCLUSIVE",
    "NOT_TESTED",
]


@dataclass
class Scenario:
    """Describe one configurable API security test."""

    scenario_id: str
    name: str
    description: str
    check_type: str
    request_method: str
    request_path: str
    expected_status_codes: list[int] = field(default_factory=list)
    request_params: dict[str, Any] = field(default_factory=dict)
    request_body: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True

    def __post_init__(self) -> None:
        """Validate required fields and request settings."""
        required_fields = {
            "scenario_id": self.scenario_id,
            "name": self.name,
            "description": self.description,
            "check_type": self.check_type,
            "request_method": self.request_method,
            "request_path": self.request_path,
        }

        for field_name, value in required_fields.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"'{field_name}' must be a non-empty string."
                )

        self.request_method = self.request_method.upper()

        allowed_methods = {
            "GET", "POST", "PUT", "PATCH", "DELETE"
        }
        if self.request_method not in allowed_methods:
            raise ValueError(
                f"Unsupported HTTP method: {self.request_method}"
            )

        if not self.request_path.startswith("/"):
            raise ValueError(
                "'request_path' must start with '/'."
            )

        if self.request_path.startswith("//"):
            raise ValueError(
                "'request_path' must be a relative API path."
            )

        if any(
            not isinstance(code, int) or not 100 <= code <= 599
            for code in self.expected_status_codes
        ):
            raise ValueError(
                "Expected status codes must be integers from 100 to 599."
            )


@dataclass
class ScenarioResult:
    """Store the outcome and evidence for one test scenario."""

    scenario_id: str
    name: str
    status: ScenarioStatus
    summary: str
    evidence: list[dict[str, Any]] = field(default_factory=list)
    remediation: str = ""
    observed_status_code: int | None = None

    def __post_init__(self) -> None:
        """Reject unsupported result statuses."""
        allowed_statuses = {
            "PASS",
            "VULNERABLE",
            "INCONCLUSIVE",
            "NOT_TESTED",
        }

        if self.status not in allowed_statuses:
            raise ValueError(
                f"Invalid scenario status: {self.status}"
            )

        if not self.scenario_id.strip():
            raise ValueError("'scenario_id' cannot be empty.")

        if not self.name.strip():
            raise ValueError("'name' cannot be empty.")

        if not self.summary.strip():
            raise ValueError("'summary' cannot be empty.")
