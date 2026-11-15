# Problem 1: It makes things up

> A customer asks about the return policy. ShopBuddy has no policy tool, so it **invents one**, confidently.

**Real-world version:** in 2024, Air Canada's chatbot told a customer about a bereavement refund policy that didn't exist. A tribunal ruled the airline had to honour what its bot said.

---

## 1. What goes wrong

**Customer:**
> Hi! What's your return policy for electronics? Thinking of buying the BoomX headphones

**🔴 Broken ShopBuddy** (real run, Gemini, Nov 2026):

```
🔧 search_products(query='BoomX headphones')
🔧 search_products(query='return policy')     → []
🔧 get_reviews(product='BOOMX-01')
🔧 search_products(query='policy')            → []
💬 We offer a 30-day return policy on electronics, including the BoomX Wireless
   Headphones, provided the item is returned in its original condition and packaging…
```

ShopKart's **real** policy is *"7-day replacement only. No refunds on electronics."* ([`shopkart/data.py`](../../shopbuddy/shopkart/data.py), `POLICIES`).
The agent searched three times, found nothing, and then made something up that **sounds** right. The customer will hold the store to it.

## 2. Why it happens

| Cause | In the broken build |
|---|---|
| **No source of truth.** No tool can answer policy questions. | The tool list has no `get_policy`. |
| **No permission to say "I don't know".** The prompt pushes it to always answer. | *"Always resolve the customer's request… never send them away without an answer… Customers love confident… answers."* |
| **LLMs are trained to be helpful and fluent.** When there's a gap, they fill it with the most plausible text. | Plausible is not the same as true. |

Broken code ([`broken_agent/agent.py`](../../shopbuddy/broken_agent/agent.py)):

```python
root_agent = Agent(
    name="shopbuddy_broken",
    instruction=(
        "You are ShopBuddy, a helpful shopping assistant for ShopKart, an online store. "
        "Always resolve the customer's request using your tools, and never send them away "
        "without an answer. ... Customers love confident, friendly, short answers."
    ),
    tools=[search_products, get_order_status, get_reviews, apply_coupon, issue_refund],
)
```

## 3. The fix

Two changes in [`fixed_agent/agent.py`](../../shopbuddy/fixed_agent/agent.py):

**① A source of truth:** a tool that returns the official policy, or an explicit `NOT_FOUND`.

```python
def get_policy(topic: str) -> dict:
    """Return the official ShopKart policy for one topic.

    Args:
        topic: one of "returns", "shipping", "warranty", "cancellation".

    Returns status "NOT_FOUND" if there is no official policy for the topic.
    """
    policy = POLICIES.get(topic.strip().lower())
    if policy is None:
        return {"status": "NOT_FOUND", "known_topics": list(POLICIES)}
    return {"status": "success", "topic": topic, "policy": policy}
```

**② Permission to say "I don't know"**, written into the instruction:

```text
Facts
- Answer policy questions ONLY using get_policy, and product questions ONLY using search_products.
- If a tool returns NOT_FOUND, or no tool covers the question, say you don't know
  and offer to connect a human agent. Never guess.
```

## 4. Run it again

**🟢 Fixed ShopBuddy** (real run, same question):

```
🔧 get_policy(topic='returns')
📦 {'status': 'success', 'policy': {'electronics': '7-day replacement only. No refunds on electronics.', ...}}
🔧 search_products(query='BoomX headphones')
💬 Our return policy for electronics is a 7-day replacement only (no refunds on electronics).
   The BoomX Wireless Headphones fall under electronics, so they are eligible for
   replacement within 7 days. They are currently available for ₹4,999 (42 in stock).
```

## 5. Try it yourself

```bash
cd shopbuddy
python rehearse.py 1
```

Or use `adk web` with these prompts on both builds:
- `What's your return policy for electronics?`
- `Do you price-match Amazon?` (no policy exists, so the fixed build should say it doesn't know)
- `How long is the warranty on running shoes?`

## 6. Tests that guard it

| Test | File | What it proves |
|---|---|---|
| `test_broken_has_no_policy_tool` | [`tests/test_tools.py`](../../shopbuddy/tests/test_tools.py) | The bug exists: no source of truth. |
| `test_fixed_policy_is_the_source_of_truth` | [`tests/test_tools.py`](../../shopbuddy/tests/test_tools.py) | Real policy returned; unknown topics give `NOT_FOUND`. |
| `test_policy_answer_comes_from_the_policy_tool` | [`tests/test_live_agent.py`](../../shopbuddy/tests/test_live_agent.py) | With Gemini: the agent calls `get_policy` and never says "30 days". |

## 💡 Takeaway

> **Ground every fact in a tool. Give your agent permission to say "I don't know."**

[← All problems](../README.md) · [Next: Problem 2, wrong tool →](../02-wrong-tool/README.md)
