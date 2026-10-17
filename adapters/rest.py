
"""REST API adapter for the business logic testing framework."""

from typing import Any

from api_tester.api_client import APIClient


class RESTAdapter:
    """Provide a consistent interface for REST API requests."""

    def __init__(
        self,
        base_url: str,
        headers: dict[str, str] | None = None,
        timeout: float = 10.0,
        verify_tls: bool = True,
    ) -> None:
        self.client = APIClient(
            base_url=base_url,
            headers=headers,
            timeout=timeout,
            verify_tls=verify_tls,
        )

    def send(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: Any = None,
    ) -> dict[str, Any]:
        """Send one configured REST request."""
        return self.client.request(
            method,
            path,
            params=params,
            json=json_body,
        )

    def close(self) -> None:
        """Release the underlying HTTP client."""
        self.client.close()

    def __enter__(self) -> "RESTAdapter":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
