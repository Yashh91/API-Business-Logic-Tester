
"""In-memory state for the local API security testing lab."""

from copy import deepcopy
from threading import RLock
from typing import Any


class LabState:
    """Store isolated sample data for local API testing."""

    def __init__(self) -> None:
        self._lock = RLock()
        self.reset()

    def reset(self) -> None:
        """Restore the lab to its initial synthetic state."""
        with self._lock:
            self.users = {
                "user-1": {
                    "user_id": "user-1",
                    "name": "Test User One",
                },
                "user-2": {
                    "user_id": "user-2",
                    "name": "Test User Two",
                },
            }

            self.orders = {
                "order-1001": {
                    "order_id": "order-1001",
                    "owner_id": "user-1",
                    "product_id": "product-101",
                    "quantity": 1,
                    "status": "created",
                },
                "order-1002": {
                    "order_id": "order-1002",
                    "owner_id": "user-2",
                    "product_id": "product-202",
                    "quantity": 2,
                    "status": "created",
                },
            }

            self.bookings = {
                "booking-1001": {
                    "booking_id": "booking-1001",
                    "owner_id": "user-1",
                    "show_id": "show-101",
                    "seat_ids": ["A1"],
                    "status": "pending",
                }
            }

            self.products = {
                "product-101": {
                    "product_id": "product-101",
                    "name": "Sample Notebook",
                    "available": True,
                },
                "product-202": {
                    "product_id": "product-202",
                    "name": "Sample Pen",
                    "available": True,
                },
            }

            self._next_order_number = 2001
            self._next_booking_number = 2001

    def get_user(self, user_id: str) -> dict[str, Any] | None:
        """Return a copy of a synthetic user record."""
        with self._lock:
            user = self.users.get(user_id)
            return deepcopy(user) if user else None

    def get_order(self, order_id: str) -> dict[str, Any] | None:
        """Return a copy of an order."""
        with self._lock:
            order = self.orders.get(order_id)
            return deepcopy(order) if order else None

    def create_order(
        self,
        *,
        owner_id: str,
        product_id: str,
        quantity: int,
    ) -> dict[str, Any]:
        """Create an order in the local lab."""
        with self._lock:
            order_id = f"order-{self._next_order_number}"
            self._next_order_number += 1

            order = {
                "order_id": order_id,
                "owner_id": owner_id,
                "product_id": product_id,
                "quantity": quantity,
                "status": "created",
            }

            self.orders[order_id] = order
            return deepcopy(order)

    def update_order_status(
        self,
        order_id: str,
        new_status: str,
    ) -> dict[str, Any] | None:
        """Update an order's status; workflow rules belong in the API."""
        with self._lock:
            order = self.orders.get(order_id)

            if order is None:
                return None

            order["status"] = new_status
            return deepcopy(order)

    def get_booking(
        self,
        booking_id: str,
    ) -> dict[str, Any] | None:
        """Return a copy of a booking."""
        with self._lock:
            booking = self.bookings.get(booking_id)
            return deepcopy(booking) if booking else None

    def create_booking(
        self,
        *,
        owner_id: str,
        show_id: str,
        seat_ids: list[str],
    ) -> dict[str, Any]:
        """Create a booking in the local lab."""
        with self._lock:
            booking_id = f"booking-{self._next_booking_number}"
            self._next_booking_number += 1

            booking = {
                "booking_id": booking_id,
                "owner_id": owner_id,
                "show_id": show_id,
                "seat_ids": list(seat_ids),
                "status": "pending",
            }

            self.bookings[booking_id] = booking
            return deepcopy(booking)

    def list_orders(self) -> list[dict[str, Any]]:
        """Return copies of all lab orders."""
        with self._lock:
            return deepcopy(list(self.orders.values()))

    def list_bookings(self) -> list[dict[str, Any]]:
        """Return copies of all lab bookings."""
        with self._lock:
            return deepcopy(list(self.bookings.values()))


lab_state = LabState()
