
"""Discover documented endpoints from an OpenAPI specification."""

import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml


SUPPORTED_METHODS = {
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "head",
    "options",
}


def load_openapi(spec_path: str) -> dict[str, Any]:
    """Load an OpenAPI JSON or YAML file."""
    path = Path(spec_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"OpenAPI specification not found: {spec_path}"
        )

    try:
        content = path.read_text(encoding="utf-8")

        if path.suffix.lower() == ".json":
            spec = json.loads(content)
        else:
            spec = yaml.safe_load(content)
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise ValueError(f"Could not parse OpenAPI file: {exc}") from exc

    if not isinstance(spec, dict):
        raise ValueError("OpenAPI specification must be an object.")

    if not isinstance(spec.get("paths"), dict):
        raise ValueError("OpenAPI specification has no valid 'paths' map.")

    if not (
        str(spec.get("openapi", "")).startswith("3.")
        or str(spec.get("swagger", "")) == "2.0"
    ):
        raise ValueError("Expected an OpenAPI 3.x or Swagger 2.0 document.")

    return spec


def discover_endpoints(
    spec: dict[str, Any],
) -> list[dict[str, Any]]:
    """Extract documented paths, methods, and operation metadata."""
    paths = spec.get("paths")

    if not isinstance(paths, dict):
        raise ValueError("Specification must contain a 'paths' map.")

    endpoints = []

    for path, path_item in paths.items():
        if not isinstance(path, str) or not path.startswith("/"):
            continue

        if not isinstance(path_item, dict):
            continue

        for method, operation in path_item.items():
            method = method.lower()

            if method not in SUPPORTED_METHODS:
                continue

            if not isinstance(operation, dict):
                operation = {}

            endpoints.append(
                {
                    "path": path,
                    "method": method.upper(),
                    "operation_id": operation.get("operationId"),
                    "summary": operation.get("summary", ""),
                    "tags": operation.get("tags", []),
                    "parameters": operation.get("parameters", []),
                    "security": operation.get(
                        "security", spec.get("security", [])
                    ),
                }
            )

    return endpoints


def get_server_urls(spec: dict[str, Any]) -> list[str]:
    """Return valid absolute HTTP(S) server URLs from the specification."""
    urls = []

    # OpenAPI 3.x uses a servers list.
    servers = spec.get("servers", [])

    # Swagger 2.0 uses host, schemes, and basePath.
    if not servers and spec.get("swagger") == "2.0":
        host = spec.get("host")
        schemes = spec.get("schemes", ["https"])
        base_path = spec.get("basePath", "")

        if host:
            servers = [
                {"url": f"{scheme}://{host}{base_path}"}
                for scheme in schemes
            ]

    if not isinstance(servers, list):
        return urls

    for server in servers:
        if not isinstance(server, dict):
            continue

        url = server.get("url")

        if not isinstance(url, str):
            continue

        parsed = urlparse(url)

        if (
            parsed.scheme in {"http", "https"}
            and parsed.hostname
            and not parsed.username
            and not parsed.password
        ):
            urls.append(url.rstrip("/"))

    return urls
