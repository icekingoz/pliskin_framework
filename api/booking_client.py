from __future__ import annotations

from typing import Any

import requests

from api.base_client import BaseClient


class BookingClient(BaseClient):
    """Classic CRUD client for the ``/booking`` endpoint."""

    PATH = "/booking"

    # -- helpers -------------------------------------------------------------
    @staticmethod
    def _auth_headers(token: str) -> dict[str, str]:
        """restful-booker takes the token as a cookie, not a Bearer header.
        A Basic auth header works too, but the cookie is what the docs show.
        """
        return {"Cookie": f"token={token}"}

    def _path_for(self, booking_id: int | str) -> str:
        return f"{self.PATH}/{booking_id}"

    # -- read ----------------------------------------------------------------
    def get_ids(self, **filters: Any) -> requests.Response:
        """GET /booking -> ``[{"bookingid": 1}, ...]``.

        Optional filters: ``firstname``, ``lastname``, ``checkin``, ``checkout``
        (dates as ``CCYY-MM-DD``).
        """
        return self._get(self.PATH, params=filters or None)

    def get(self, booking_id: int | str) -> requests.Response:
        """GET /booking/:id -> the booking body (no id echoed back)."""
        return self._get(self._path_for(booking_id))

    # -- write ---------------------------------------------------------------
    def create(self, payload: dict[str, Any]) -> requests.Response:
        """POST /booking -> ``{"bookingid": N, "booking": {...}}``. No auth."""
        return self._post(self.PATH, json=payload)

    def update(
        self, booking_id: int | str, payload: dict[str, Any], token: str
    ) -> requests.Response:
        """PUT /booking/:id -- full replacement, every field required."""
        return self._put(
            self._path_for(booking_id),
            json=payload,
            headers=self._auth_headers(token),
        )

    def partial_update(
        self, booking_id: int | str, payload: dict[str, Any], token: str
    ) -> requests.Response:
        """PATCH /booking/:id -- send only the fields you want changed."""
        return self._patch(
            self._path_for(booking_id),
            json=payload,
            headers=self._auth_headers(token),
        )

    def delete(self, booking_id: int | str, token: str) -> requests.Response:
        """DELETE /booking/:id -> 201 Created (not 200, not 204)."""
        return self._delete(
            self._path_for(booking_id),
            headers=self._auth_headers(token),
        )
