
"""Data model for API Business Logic Tester reports."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from api_tester.engine.scenario import ScenarioResult


@dataclass
class TestReport:
    """Represent one API security assessment."""

    target_name: str
    base_url: str
    results: list[ScenarioResult] = field(default_factory=list)
    started_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.target_name.strip():
            raise ValueError("target_name cannot be empty.")

        if not self.base_url.strip():
            raise ValueError("base_url cannot be empty.")

    @property
    def summary(self) -> dict[str, int]:
        """Calculate status totals from actual scenario results."""
        counts = {
            "total": len(self.results),
            "pass": 0,
            "vulnerable": 0,
            "inconclusive": 0,
            "not_tested": 0,
        }

        for result in self.results:
            status_key = result.status.lower()

            if status_key in counts:
                counts[status_key] += 1

        return counts

    def add_result(self, result: ScenarioResult) -> None:
        """Add the result of a scenario that was actually evaluated."""
        if not isinstance(result, ScenarioResult):
            raise TypeError("result must be a ScenarioResult instance.")

        self.results.append(result)

    def to_dict(self) -> dict[str, Any]:
        """Convert the report to JSON-serializable data."""
        return {
            "report_type": "API Business Logic Security Assessment",
            "target": {
                "name": self.target_name,
                "base_url": self.base_url,
            },
            "started_at": self.started_at,
            "summary": self.summary,
            "metadata": self.metadata,
            "results": [
                {
                    "scenario_id": result.scenario_id,
                    "name": result.name,
                    "status": result.status,
                    "summary": result.summary,
                    "observed_status_code": result.observed_status_code,
                    "evidence": result.evidence,
                    "remediation": result.remediation,
                }
                for result in self.results
            ],
        }
