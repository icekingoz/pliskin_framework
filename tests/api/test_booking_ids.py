"""Listing and filtering booking ids via GET /booking."""

from __future__ import annotations

from typing import Any

import pytest

from api.booking_client import BookingClient

pytestmark = pytest.mark.api


def _ids(response: Any) -> list[int]:
    return [item["bookingid"] for item in response.json()]


def test_all_ids_includes_our_booking(
    booking_client: BookingClient, created_booking: tuple[int, dict[str, Any]]
) -> None:
    booking_id, _ = created_booking

    response = booking_client.get_ids()

    assert response.status_code == 200
    #Other people are creating and deleting bookings all time time, 
    # so any assertion on the total is guaranteed to flake.
    assert booking_id in _ids(response)


def test_filtering_by_name_finds_our_booking(
    booking_client: BookingClient, created_booking: tuple[int, dict[str, Any]]
) -> None:
    booking_id, payload = created_booking

    response = booking_client.get_ids(
        firstname=payload["firstname"], lastname=payload["lastname"]
    )

    assert response.status_code == 200
    # The builder gives every booking a unique lastname, so this filter should
    # match exactly one row -- ours.
    assert _ids(response) == [booking_id]
