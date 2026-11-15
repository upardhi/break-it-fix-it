"""Per-chat copies of the store, so one rehearsal doesn't affect the next.

Each chat session starts with a fresh copy of the orders. Changes (coupons,
refunds, cancellations) are saved in that session's state only. Start a new
session in `adk web` to reset everything.
"""

import copy

from .data import ORDERS, PRODUCTS


def load_orders(tool_context) -> dict:
    if tool_context is None:
        return copy.deepcopy(ORDERS)
    orders = tool_context.state.get("orders")
    if orders is None:
        orders = copy.deepcopy(ORDERS)
    return orders


def save_orders(tool_context, orders: dict) -> None:
    if tool_context is not None:
        tool_context.state["orders"] = orders


def find_product(text: str) -> dict | None:
    """Match a product by ID or by words in its name."""
    if not text:
        return None
    key = text.strip().upper()
    if key in PRODUCTS:
        return PRODUCTS[key]
    words = [w for w in text.lower().replace("-", " ").split() if len(w) > 2]
    best, best_score = None, 0
    for product in PRODUCTS.values():
        name = product["name"].lower()
        score = sum(1 for w in words if w in name)
        if score > best_score:
            best, best_score = product, score
    return best


def describe_order(order: dict) -> dict:
    return {
        **order,
        "item_names": [PRODUCTS[p]["name"] for p in order["items"] if p in PRODUCTS],
    }
