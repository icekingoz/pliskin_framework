"""Base class shared by every service client."""

from __future__ import annotations

from typing import Any

import requests

DEFAULT_TIMEOUT_SECONDS = 15.0


class BaseClient:
    def __init__(
        self,
        base_url: str,
        session: requests.Session | None = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        # An injected Session lets the whole suite share one connection pool.
        self.session = session or requests.Session()
        self.timeout = timeout

    # -- transport -----------------------------------------------------------
    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        """Single choke point for every call -- handy place to add logging."""
        kwargs.setdefault("timeout", self.timeout)
        return self.session.request(method, self._url(path), **kwargs)

    def _get(self, path: str, **kwargs: Any) -> requests.Response:
        return self._request("GET", path, **kwargs)

    def _post(self, path: str, **kwargs: Any) -> requests.Response:
        return self._request("POST", path, **kwargs)

    def _put(self, path: str, **kwargs: Any) -> requests.Response:
        return self._request("PUT", path, **kwargs)

    def _patch(self, path: str, **kwargs: Any) -> requests.Response:
        return self._request("PATCH", path, **kwargs)

    def _delete(self, path: str, **kwargs: Any) -> requests.Response:
        return self._request("DELETE", path, **kwargs)
