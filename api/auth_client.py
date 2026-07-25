from __future__ import annotations

import requests

from api.base_client import BaseClient

"""Auth - CreateToken
Creates a new auth token to use for access to the PUT and DELETE /booking"""


class AuthClient(BaseClient):
    PATH = "/auth"

    def create_token(self, username: str, password: str) -> requests.Response:
        """POST /auth -> ``{"token": "abc123"}``. """
        return self._post(
            self.PATH,
            json={"username": username, "password": password},
        )
