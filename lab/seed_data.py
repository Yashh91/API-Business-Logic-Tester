
"""Synthetic seed data and reset helpers for the local testing lab."""

from typing import Any

from lab.state import LabState, lab_state


SEED_USERS: dict[str, dict[str, Any]] = {
    "user-1": {
        "user_id": "user-1",
        "name": "Test User One",
    },
    "user-2": {
        "user_id": "user-2",
        "name": "Test User Two",
    },
}

SEED_ORDERS: list[dict[str, Any]] = [
    {
        "order_id": "order-1001",
        "owner_id": "user-1",
        "product_id": "product-101",
        "quantity": 1,
        "status": "created",
    },
    {
        "order_id": "order-1002",
        "owner_id": "user-2",
        "product_id": "product-202",
        "quantity": 2,
        "status": "created",
    },
]

SEED_BOOKINGS: list[dict[str, Any]] = [
    {
        "booking_id": "booking-1001",
        "owner_id": "user-1",
        "show_id": "show-101",
        "seat_ids": ["A1"],
        "status": "pending",
    }
]


def reset_lab(state: LabState = lab_state) -> None:
    """Reset the in-memory lab to its initial synthetic state."""
    state.reset()


def get_seed_snapshot() -> dict[str, Any]:
    """Return a copy of the documented seed-data reference."""
    return {
        "users": [dict(user) for user in SEED_USERS.values()],
        "orders": [dict(order) for order in SEED_ORDERS],
        "bookings": [
            {
                **booking,
                "seat_ids": list(booking["seat_ids"]),
            }
            for booking in SEED_BOOKINGS
        ],
    }
