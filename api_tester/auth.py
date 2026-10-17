
"""Authentication helpers for authorized API testing."""

import os
from typing import Any


def build_headers(
    auth_config: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Build HTTP headers from a safe authentication configuration.

    Supported types:
      - none
      - bearer
      - api_key

    Credentials should be provided through environment variables,
    not committed to the repository.
    """
    config = auth_config or {}
    auth_type = config.get("type", "none")

    if auth_type == "none":
        return {}

    if auth_type == "bearer":
        env_name = config.get("token_env", "API_TOKEN")
        token = os.getenv(env_name)

        if not token:
            raise ValueError(
                f"Missing bearer token environment variable: {env_name}"
            )

        return {"Authorization": f"Bearer {token}"}

    if auth_type == "api_key":
        env_name = config.get("key_env", "API_KEY")
        header_name = config.get("header_name", "X-API-Key")
        api_key = os.getenv(env_name)

        if not api_key:
            raise ValueError(
                f"Missing API key environment variable: {env_name}"
            )

        if not isinstance(header_name, str) or not header_name.strip():
            raise ValueError("API key header_name must be a non-empty string.")

        if "\r" in header_name or "\n" in header_name:
            raise ValueError("Invalid API key header name.")

        return {header_name: api_key}

    raise ValueError(
        f"Unsupported authentication type: {auth_type}"
    )
