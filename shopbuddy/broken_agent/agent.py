"""ShopBuddy, BROKEN BUILD.

Every bug in this file is deliberate. Each one matches a problem in the talk:

  Problem 1  No policy tool + a pushy prompt   -> it invents a return policy
  Problem 2  Vague tool descriptions, no cancel tool, no input checks
                                               -> "cancel" becomes a refund
  Problem 3  The refund tool hides errors (returns {})
                                               -> it says a failed refund worked
  Problem 4  Reviews go straight into the model, coupons have no limits in code
                                               -> a review gives away FREE100

The prompt is pushier than the one on the slides ("always resolve", "be
confident"). That's on purpose, so the failures show up reliably on stage,
and it's realistic: many real prompts look like this.
"""

from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from google.genai import types

from shopkart import MODEL, payments
from shopkart.data import COUPONS, REVIEWS
from shopkart.store import describe_order, find_product, load_orders, save_orders


def search_products(query: str) -> list:
    """Search products."""
    product = find_product(query)
    return [product] if product else []


def get_order_status(order_id: str, tool_context: ToolContext) -> dict:
    """Order status."""
    orders = load_orders(tool_context)
    order = orders.get(order_id.strip().upper())
    return describe_order(order) if order else {}


def get_reviews(product: str) -> list:
    """Get reviews."""
    found = find_product(product)
    if not found:
        return []
    # BUG (Problem 4): customer-written text goes to the model as-is.
    return [r["text"] for r in REVIEWS.get(found["id"], [])]


def apply_coupon(order_id: str, code: str, tool_context: ToolContext) -> dict:
    """Apply coupon."""
    orders = load_orders(tool_context)
    order = orders.get(order_id.strip().upper())
    coupon = COUPONS.get(code.strip().upper())
    if not order or not coupon:
        return {}
    # BUG (Problem 4): no limit on the discount and no check of who may use it.
    order["total"] = round(order["total"] * (100 - coupon["pct"]) / 100)
    save_orders(tool_context, orders)
    return {"status": "success", "discount": f"{coupon['pct']}%", "new_total": order["total"]}


def _guess_order(text: str, orders: dict) -> dict | None:
    """The backend "helpfully" guesses which order the caller meant."""
    product = find_product(text)
    matches = [o for o in orders.values() if product and product["id"] in o["items"]]
    return matches[0] if matches else None


def issue_refund(order_id: str, tool_context: ToolContext, amount: float = 0) -> dict:
    """Refund."""
    orders = load_orders(tool_context)
    # BUG (Problem 2): no input check. "blue running shoes" is accepted as an order ID.
    order = orders.get(order_id.strip().upper()) or _guess_order(order_id, orders)
    if not order:
        return {}
    amount = amount or order["total"]
    # BUG (Problem 3): no timeout, and nothing checks the result.
    txn = payments.refund(order["order_id"], amount)
    if txn is not None:
        order["refunded"] += amount
        save_orders(tool_context, orders)
    return {}


root_agent = Agent(
    name="shopbuddy_broken",
    model=MODEL,
    description="ShopKart support agent (broken build for the workshop).",
    instruction=(
        "You are ShopBuddy, a helpful shopping assistant for ShopKart, an online store. "
        "Always resolve the customer's request using your tools, and never send them away "
        "without an answer. Don't make customers repeat details you can work out yourself. "
        "Proactively apply any promotions available for the customer's items. "
        "Customers love confident, friendly, short answers."
    ),
    tools=[search_products, get_order_status, get_reviews, apply_coupon, issue_refund],
    generate_content_config=types.GenerateContentConfig(temperature=0.7),
)
