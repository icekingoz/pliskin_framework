"""Fixtures for the API suite only."""

from __future__ import annotations

from typing import Iterator

import pytest
import requests

from api.auth_client import AuthClient
from api.ping_client import PingClient


@pytest.fixture(scope="session")
def api_session() -> Iterator[requests.Session]:
    """One connection pool for the whole run.

    Also the single place default headers are set, so no client has to repeat
    them.
    """
    with requests.Session() as session:
        session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )
        yield session


# --- clients ----------------------------------------------------------------
@pytest.fixture
def auth_client(api_base_url: str, api_session: requests.Session) -> AuthClient:
    return AuthClient(api_base_url, api_session)


@pytest.fixture
def ping_client(api_base_url: str, api_session: requests.Session) -> PingClient:
    return PingClient(api_base_url, api_session)


# --- auth -------------------------------------------------------------------
@pytest.fixture(scope="session")
def auth_token(
    api_base_url: str,
    api_session: requests.Session,
    booker_credentials: dict[str, str],
) -> str:
    """One token per run, not per test.

    Session-scoped because the token stays valid for the whole run and
    re-authenticating before every test is pure wasted latency.

    Normally wouldn't put asserts here but if it fails the whole suite is doomed anyway.
    """
    response = AuthClient(api_base_url, api_session).create_token(**booker_credentials)
    assert response.status_code == 200, (
        f"Could not authenticate: HTTP {response.status_code} -- {response.text}"
    )

    token = response.json().get("token")
    # Bad credentials come back as 200 + {"reason": "Bad credentials"},
    # so the status code alone proves nothing.
    assert token, f"No token in auth response: {response.text}"
    return token
