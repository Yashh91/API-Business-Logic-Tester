
"""Local REST API for practicing business-logic security testing.

This intentionally vulnerable lab is for localhost practice only.
Do not expose it to the internet or use real customer data.
"""

import os
from typing import Any

from flask import Flask, jsonify, request

from lab.state import lab_state


app = Flask(__name__)

# Select "secure" or "vulnerable" behavior for local demonstrations.
LAB_MODE = os.getenv("LAB_MODE", "secure").lower()

if LAB_MODE not in {"secure", "vulnerable"}:
    raise ValueError("LAB_MODE must be 'secure' or 'vulnerable'.")


def current_user_id() -> str | None:
    """Resolve a synthetic test user from the lab-only header."""
    user_id = request.headers.get("X-Lab-User")

    if user_id not in {"user-1", "user-2"}:
        return None

    return user_id


def error(message: str, status: int):
    """Return a consistent JSON error response."""
    return jsonify({"error": message}), status


def can_access(owner_id: str, user_id: str | None) -> bool:
    """Check whether the synthetic caller owns a resource."""
    return user_id is not None and owner_id == user_id


@app.get("/")
def index():
    return jsonify(
        {
            "name": "API Business Logic Testing Lab",
            "mode": LAB_MODE,
            "warning": "Local synthetic test data only.",
            "endpoints": [
                "GET /api/orders/<order_id>",
                "POST /api/orders",
                "POST /api/orders/<order_id>/ship",
                "GET /api/bookings/<booking_id>",
                "POST /api/bookings",
                "POST /api/bookings/<booking_id>/confirm",
            ],
        }
    )


@app.get("/api/orders/<order_id>")
def get_order(order_id: str):
    user_id = current_user_id()

    if user_id is None:
        return error("Authentication required", 401)

    order = lab_state.get_order(order_id)

    if order is None:
        return error("Order not found", 404)

    if LAB_MODE == "secure" and not can_access(
        order["owner_id"], user_id
    ):
        return error("Forbidden", 403)

    return jsonify(order)


@app.post("/api/orders")
def create_order():
    user_id = current_user_id()

    if user_id is None:
        return error("Authentication required", 401)

    data: Any = request.get_json(silent=True)

    if not isinstance(data, dict):
        return error("A JSON object is required", 400)

    product_id = data.get("product_id")
    quantity = data.get("quantity")

    if not isinstance(product_id, str) or not product_id.strip():
        return error("product_id is required", 400)

    if product_id not in lab_state.products:
        return error("Unknown product_id", 400)

    # Reject booleans as well as non-integer or non-positive quantities.
    if (
        not isinstance(quantity, int)
        or isinstance(quantity, bool)
        or quantity <= 0
    ):
        if LAB_MODE == "secure":
            return error("quantity must be a positive integer", 422)

    order = lab_state.create_order(
        owner_id=user_id,
        product_id=product_id,
        quantity=quantity if isinstance(quantity, int) else 1,
    )

    return jsonify(order), 201


@app.post("/api/orders/<order_id>/ship")
def ship_order(order_id: str):
    user_id = current_user_id()

    if user_id is None:
        return error("Authentication required", 401)

    order = lab_state.get_order(order_id)

    if order is None:
        return error("Order not found", 404)

    if LAB_MODE == "secure":
        if not can_access(order["owner_id"], user_id):
            return error("Forbidden", 403)

        if order["status"] != "created":
            return error("Invalid order state", 409)

    updated = lab_state.update_order_status(order_id, "shipped")

    return jsonify(updated)


@app.get("/api/bookings/<booking_id>")
def get_booking(booking_id: str):
    user_id = current_user_id()

    if user_id is None:
        return error("Authentication required", 401)

    booking = lab_state.get_booking(booking_id)

    if booking is None:
        return error("Booking not found", 404)

    if LAB_MODE == "secure" and not can_access(
        booking["owner_id"], user_id
    ):
        return error("Forbidden", 403)

    return jsonify(booking)


@app.post("/api/bookings")
def create_booking():
    user_id = current_user_id()

    if user_id is None:
        return error("Authentication required", 401)

    data: Any = request.get_json(silent=True)

    if not isinstance(data, dict):
        return error("A JSON object is required", 400)

    show_id = data.get("show_id")
    seat_ids = data.get("seat_ids")

    if not isinstance(show_id, str) or not show_id.strip():
        return error("show_id is required", 400)

    if (
        not isinstance(seat_ids, list)
        or not seat_ids
        or not all(
            isinstance(seat, str) and seat.strip()
            for seat in seat_ids
        )
    ):
        return error("seat_ids must be a non-empty string list", 422)

    if LAB_MODE == "secure" and len(set(seat_ids)) != len(seat_ids):
        return error("Duplicate seats are not allowed", 422)

    if LAB_MODE == "secure":
        existing = lab_state.list_bookings()
        already_booked = {
            seat
            for booking in existing
            if booking["show_id"] == show_id
            and booking["status"] != "cancelled"
            for seat in booking["seat_ids"]
        }

        if any(seat in already_booked for seat in seat_ids):
            return error("One or more seats are already booked", 409)

    booking = lab_state.create_booking(
        owner_id=user_id,
        show_id=show_id,
        seat_ids=seat_ids,
    )

    return jsonify(booking), 201


@app.post("/api/bookings/<booking_id>/confirm")
def confirm_booking(booking_id: str):
    user_id = current_user_id()

    if user_id is None:
        return error("Authentication required", 401)

    booking = lab_state.get_booking(booking_id)

    if booking is None:
        return error("Booking not found", 404)

    if LAB_MODE == "secure":
        if not can_access(booking["owner_id"], user_id):
            return error("Forbidden", 403)

        if booking["status"] != "pending":
            return error("Booking cannot be confirmed in this state", 409)

    with lab_state._lock:
        lab_state.bookings[booking_id]["status"] = "confirmed"
        updated = dict(lab_state.bookings[booking_id])

    return jsonify(updated)


if __name__ == "__main__":
    # Local-only binding is deliberate; do not change to 0.0.0.0.
    app.run(host="127.0.0.1", port=8000, debug=False)
