"""Happy-path CRUD lifecycle for /booking."""

from __future__ import annotations

from typing import Any

import pytest

from api.booking_client import BookingClient
from api.models import build_booking

pytestmark = pytest.mark.api


def test_create_booking_returns_id_and_echoes_the_payload(
    booking_client: BookingClient, booking_payload: dict[str, Any], auth_token: str
) -> None:
    response = booking_client.create(booking_payload)

    assert response.status_code == 200
    body = response.json()

    assert isinstance(body["bookingid"], int)
    # The API should hand back exactly what it was given.
    assert body["booking"] == booking_payload

    booking_client.delete(body["bookingid"], auth_token)


@pytest.mark.smoke
def test_created_booking_can_be_retrieved_by_id(
    booking_client: BookingClient, created_booking: tuple[int, dict[str, Any]]
) -> None:
    booking_id, payload = created_booking

    response = booking_client.get(booking_id)

    assert response.status_code == 200
    # GET returns the booking body only
    assert response.json() == payload


def test_put_replaces_every_field(
    booking_client: BookingClient,
    created_booking: tuple[int, dict[str, Any]],
    auth_token: str,
) -> None:
    booking_id, _ = created_booking
    updated = build_booking(
        firstname="Updated",
        totalprice=999,
        depositpaid=False,
        additionalneeds="Late checkout",
    )

    response = booking_client.update(booking_id, updated, auth_token)

    assert response.status_code == 200
    assert response.json() == updated

    # Confirm it persisted rather than trusting the response body alone.
    assert booking_client.get(booking_id).json() == updated


def test_patch_changes_only_the_fields_sent(
    booking_client: BookingClient,
    created_booking: tuple[int, dict[str, Any]],
    auth_token: str,
) -> None:
    booking_id, original = created_booking

    response = booking_client.partial_update(
        booking_id, {"firstname": "Patched"}, auth_token
    )

    assert response.status_code == 200
    body = response.json()

    assert body["firstname"] == "Patched"
    # The point of PATCH: everything else survives untouched.
    assert body["lastname"] == original["lastname"]
    assert body["totalprice"] == original["totalprice"]
    assert body["bookingdates"] == original["bookingdates"]


def test_delete_removes_the_booking(
    booking_client: BookingClient, booking_payload: dict[str, Any], auth_token: str
) -> None:
    # Creates its own booking rather than using `created_booking`, because the fixture's teardown would hide it.
    booking_id = booking_client.create(booking_payload).json()["bookingid"]

    response = booking_client.delete(booking_id, auth_token)

    # 201 Created for a delete. weird but documented.
    assert response.status_code == 201
    # The delete only counts if the booking is actually gone.
    assert booking_client.get(booking_id).status_code == 404
