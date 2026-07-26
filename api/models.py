"""Request builders for the ``/booking`` resource. Called models.py because of convention."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any
from uuid import uuid4


def build_booking(
    checkin: date | None = None,
    nights: int = 3,
    **overrides: Any,
) -> dict[str, Any]:
    """Return a valid, unique booking payload.

    Args:
        checkin: First night. Defaults to tomorrow.
        nights: Length of stay, used to derive ``checkout``.
        **overrides: Any top-level field to replace, e.g. ``totalprice=999``.

    Example:
        >>> build_booking(totalprice=250, additionalneeds="Late checkout")
    """
    checkin = checkin or date.today() + timedelta(days=1)
    checkout = checkin + timedelta(days=nights)

    payload: dict[str, Any] = {
        "firstname": "Snake",
        "lastname": f"Pliskin-{uuid4().hex[:8]}",
        "totalprice": 111,
        "depositpaid": True,
        "bookingdates": {
            "checkin": checkin.isoformat(),
            "checkout": checkout.isoformat(),
        },
        "additionalneeds": "Breakfast",
    }
    payload.update(overrides)
    return payload
