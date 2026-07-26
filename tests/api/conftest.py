"""Fixtures for the API suite only."""

from __future__ import annotations

from typing import Iterator, Any

import pytest
import requests

from api.auth_client import AuthClient
from api.ping_client import PingClient
from api.booking_client import BookingClient

from api.models import build_booking
from support.reporting import attach_text

# --- request/response recording ---------------------------------------------
# Headers whose values must never reach a published report.
_REDACT = {"cookie", "authorization", "set-cookie"}
_MAX_BODY_CHARS = 2_000

# Every HTTP exchange made during the current test. 
_EXCHANGES: list[str] = []


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

@pytest.fixture(autouse=True)
def _isolate_exchanges() -> Iterator[None]:
    """Each test's failure report should show that test's traffic, not the run's."""
    _EXCHANGES.clear()
    yield



# --- clients ----------------------------------------------------------------
@pytest.fixture
def auth_client(api_base_url: str, api_session: requests.Session) -> AuthClient:
    return AuthClient(api_base_url, api_session)


@pytest.fixture
def ping_client(api_base_url: str, api_session: requests.Session) -> PingClient:
    return PingClient(api_base_url, api_session)

@pytest.fixture
def booking_client(api_base_url: str, api_session: requests.Session) -> BookingClient:
    return BookingClient(api_base_url, api_session)


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

# --- test data --------------------------------------------------------------
@pytest.fixture
def booking_payload() -> dict[str, Any]:
    """A valid, unique payload. Nothing has been sent to the API yet."""
    return build_booking()


@pytest.fixture
def created_booking(
    booking_client: BookingClient,
    booking_payload: dict[str, Any],
    auth_token: str,
) -> Iterator[tuple[int, dict[str, Any]]]:
    """A booking that exists on the server, cleaned up afterwards.

    Yields ``(booking_id, payload)``.

    The teardown is the point of this fixture: it is what lets you run the
    suite twice in a row and get the same result. Deliberately tolerant --
    a test that already deleted the booking should not fail in teardown.
    """
    response = booking_client.create(booking_payload)
    assert response.status_code == 200, (
        f"Setup failed to create a booking: HTTP {response.status_code} -- {response.text}"
    )
    booking_id = response.json()["bookingid"]

    yield booking_id, booking_payload

    booking_client.delete(booking_id, auth_token)


# --- failure capture --------------------------------------------------------
@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    """Attach the full HTTP conversation whenever an API test fails.

    The API-side equivalent of a screenshot. ``assert response.status_code == 200``
    tells you a test failed; this tells you what was sent and what came back.
    """
    report = yield

    if report.when == "call" and report.failed and _EXCHANGES:
        attach_text(
            f"http-exchanges-{item.name}",
            "\n\n".join(_EXCHANGES),
            item=item,
            report=report,
        )

    return report

