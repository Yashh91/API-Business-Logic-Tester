
"""Helpers for collecting safe, structured API test evidence."""

from typing import Any
from urllib.parse import urlsplit


SENSITIVE_KEYS = {
    "authorization",
    "cookie",
    "set-cookie",
    "token",
    "access_token",
    "refresh_token",
    "api_key",
    "apikey",
    "password",
    "secret",
}


def redact_sensitive_data(
    value: Any,
    *,
    replacement: str = "[REDACTED]",
) -> Any:
    """Redact sensitive values in nested dictionaries and lists."""

    if isinstance(value, dict):
        sanitized = {}

        for key, item in value.items():
            if str(key).lower() in SENSITIVE_KEYS:
                sanitized[key] = replacement
            else:
                sanitized[key] = redact_sensitive_data(
                    item,
                    replacement=replacement,
                )

        return sanitized

    if isinstance(value, list):
        return [
            redact_sensitive_data(
                item,
                replacement=replacement,
            )
            for item in value
        ]

    if isinstance(value, tuple):
        return [
            redact_sensitive_data(
                item,
                replacement=replacement,
            )
            for item in value
        ]

    return value


def summarize_url(url: str | None) -> str | None:
    """Remove URL credentials, query parameters, and fragments."""

    if not url:
        return None

    parsed = urlsplit(url)

    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return "[URL OMITTED]"

    host = parsed.hostname

    if ":" in host and not host.startswith("["):
        host = f"[{host}]"

    if parsed.port:
        host = f"{host}:{parsed.port}"

    return f"{parsed.scheme}://{host}{parsed.path}"


def build_evidence(
    *,
    check_name: str,
    request_method: str,
    request_path: str,
    response: dict[str, Any],
    observation: str,
) -> dict[str, Any]:
    """Build a sanitized evidence record from one API response."""

    if not check_name.strip():
        raise ValueError("check_name cannot be empty.")

    if not request_method.strip():
        raise ValueError("request_method cannot be empty.")

    if not request_path.startswith("/") or request_path.startswith("//"):
        raise ValueError("request_path must be a relative API path.")

    if not observation.strip():
        raise ValueError("observation cannot be empty.")

    status_code = response.get("status_code")
    if not isinstance(status_code, int):
        status_code = None

    body = response.get("body")

    # Keep evidence compact and avoid accidentally storing credentials.
    sanitized_body = redact_sensitive_data(body)

    if isinstance(sanitized_body, str):
        sanitized_body = sanitized_body[:2000]

    return {
        "check_name": check_name,
        "request": {
            "method": request_method.upper(),
            "path": request_path,
        },
        "response": {
            "status_code": status_code,
            "body_excerpt": sanitized_body,
        },
        "observation": observation,
    }
