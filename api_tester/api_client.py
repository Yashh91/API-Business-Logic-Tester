
"""HTTP client for authorized API security testing."""

from typing import Any
from urllib.parse import urljoin, urlparse

import httpx


class APIClient:
    """Send controlled HTTP requests to a configured API."""

    def __init__(
        self,
        base_url: str,
        headers: dict[str, str] | None = None,
        timeout: float = 10.0,
        verify_tls: bool = True,
    ) -> None:
        parsed = urlparse(base_url)

        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.hostname
            or parsed.username
            or parsed.password
        ):
            raise ValueError("A valid HTTP(S) base URL is required.")

        if timeout <= 0:
            raise ValueError("Timeout must be greater than zero.")

        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout
        self._client = httpx.Client(
            headers=headers or {},
            timeout=timeout,
            verify=verify_tls,
            follow_redirects=False,
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
    ) -> dict[str, Any]:
        """Send one request and return structured response data."""
        if not path or urlparse(path).scheme or path.startswith("//"):
            raise ValueError("Path must be relative to the configured API.")

        url = urljoin(self.base_url, path.lstrip("/"))

        # Prevent a path from escaping the configured API origin.
        if urlparse(url).netloc != urlparse(self.base_url).netloc:
            raise ValueError("Request path points outside the API origin.")

        try:
            response = self._client.request(
                method=method.upper(),
                url=url,
                params=params,
                json=json,
            )
        except httpx.TimeoutException:
            return {
                "ok": False,
                "error": "timeout",
                "status_code": None,
                "body": None,
            }
        except httpx.RequestError as exc:
            return {
                "ok": False,
                "error": type(exc).__name__,
                "status_code": None,
                "body": None,
            }

        try:
            body = response.json()
        except ValueError:
            body = response.text[:5000]

        return {
            "ok": True,
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": body,
            "url": str(response.url),
        }

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._client.close()

    def __enter__(self) -> "APIClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
