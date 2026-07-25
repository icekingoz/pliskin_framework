from __future__ import annotations

import requests

from api.base_client import BaseClient
"""Ping
 Ping - HealthCheck
 A simple health check endpoint to confirm whether the API is up and running."""

class PingClient(BaseClient):
    PATH = "/ping"

    def ping(self) -> requests.Response:
        """GET /ping -> 201 Created (yes, 201 -- see the test for why)."""
        return self._get(self.PATH)
