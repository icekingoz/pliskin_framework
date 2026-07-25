from __future__ import annotations

import pytest

from api.auth_client import AuthClient

pytestmark = [pytest.mark.api, pytest.mark.smoke]


def test_valid_credentials_return_a_token(
    auth_client: AuthClient, booker_credentials: dict[str, str]
) -> None:
    response = auth_client.create_token(**booker_credentials)

    assert response.status_code == 200

    body = response.json()
    # The real assertion. A 200 here is worth nothing on its own: the API
    # answers bad credentials with 200 and {"reason": "Bad credentials"},
    # so only the presence of a token proves authentication succeeded.
    assert "token" in body, f"Expected a token, got: {body}"
    assert isinstance(body["token"], str)
    assert body["token"]
