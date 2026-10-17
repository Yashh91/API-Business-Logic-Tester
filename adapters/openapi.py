
"""Adapter for importing endpoints from OpenAPI specifications."""

from typing import Any

from api_tester.discovery import (
    discover_endpoints,
    get_server_urls,
    load_openapi,
)


class OpenAPIAdapter:
    """Load and expose endpoints documented in an OpenAPI specification."""

    def __init__(self, spec_path: str) -> None:
        self.spec_path = spec_path
        self.spec = load_openapi(spec_path)

    def get_endpoints(self) -> list[dict[str, Any]]:
        """Return documented API endpoints and operation metadata."""
        return discover_endpoints(self.spec)

    def get_server_urls(self) -> list[str]:
        """Return the HTTP(S) server URLs documented in the spec."""
        return get_server_urls(self.spec)

    def get_summary(self) -> dict[str, Any]:
        """Return a compact inventory of documented API operations."""
        endpoints = self.get_endpoints()

        methods: dict[str, int] = {}
        for endpoint in endpoints:
            method = endpoint["method"]
            methods[method] = methods.get(method, 0) + 1

        return {
            "specification": self.spec_path,
            "openapi_version": self.spec.get(
                "openapi", self.spec.get("swagger", "unknown")
            ),
            "server_urls": self.get_server_urls(),
            "endpoint_count": len(endpoints),
            "methods": methods,
            "endpoints": endpoints,
        }
