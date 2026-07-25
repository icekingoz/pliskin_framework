from __future__ import annotations

import pytest

from api.ping_client import PingClient

pytestmark = [pytest.mark.api, pytest.mark.smoke]


def test_ping_reports_the_api_is_up(ping_client: PingClient) -> None:
    response = ping_client.ping()

    # 201, not 200. It looks like a bug and reads like one, but it is the
    # documented behaviour so just assert what the API actually does. Changing
    # this to 200 "because that's correct" would give you a red suite against
    # a healthy service.
    assert response.status_code == 201
