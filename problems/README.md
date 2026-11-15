# The four ways ShopBuddy breaks, and how to fix each

ShopBuddy is the customer-support agent for **ShopKart**, a made-up online store. It can look up products, orders, policies and reviews, and it can take actions that move money: apply coupons and issue refunds.

The repo has two builds of the same agent:

| Build | File | Purpose |
|---|---|---|
| 🔴 **Broken** | [`shopbuddy/broken_agent/agent.py`](../shopbuddy/broken_agent/agent.py) | Every bug is deliberate, one per problem below. |
| 🟢 **Fixed** | [`shopbuddy/fixed_agent/agent.py`](../shopbuddy/fixed_agent/agent.py) | The same store and customers, with every fix applied. |

## The agent loop, and where it breaks

```
                 ④ poisoned data comes back in
              ┌───────────────────────────────────┐
              ▼                                   │
 Customer ─▶ Model ──②──▶ Tool call ──③──▶ Tool result
              │
              ①
              ▼
           Answer
```

| # | Problem | Where it breaks | Fix in one line |
|---|---|---|---|
| 1 | [**It makes things up**](01-makes-things-up/README.md) | Model → Answer, with no tool behind it | Give it a source of truth and permission to say "I don't know". |
| 2 | [**It picks the wrong tool**](02-wrong-tool/README.md) | Model → Tool call | Clear tool descriptions, the right tool, inputs checked in code. |
| 3 | [**It fails silently**](03-silent-failure/README.md) | Tool call → Tool result | Make errors loud and limit the retries. |
| 4 | [**A review takes control**](04-prompt-injection/README.md) | Tool result → back into the Model | Treat outside text as data; enforce rules in code; a human approves risky actions. |
| ★ | [**Student challenge**](05-student-challenge/README.md) | All of the above | Try to buy ₹4,999 headphones as cheaply as you can. |

Each problem page follows the same pattern:

1. **What goes wrong**: the demo, with a real run.
2. **Why it happens**: the root cause.
3. **The fix**: before and after code, taken from the repo.
4. **Run it again**: the fixed agent on the same input.
5. **Try it yourself**: commands and prompts.
6. **The tests that guard it**: because every bug becomes a test.

## Run any problem yourself

Setup (once): see [START-HERE.md §2](../START-HERE.md#2-one-time-setup-on-your-laptop). In short:

```bash
cd shopbuddy
python -m venv .venv
.venv\Scripts\activate          # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env          # Mac/Linux: cp .env.example .env, then add your Gemini API key
```

Then either:

- **Interactive:** `adk web`, open http://localhost:8000, choose `broken_agent` or `fixed_agent`, and watch the **Events** tab.
- **Scripted:** `python rehearse.py 1` (or 2, 3, 4) runs the problem's prompt on both builds and prints every tool call and reply.

> **LLMs are not deterministic.** The sample runs on these pages are real (Gemini, November 2026), but your run may differ. That is part of the lesson: you can't rely on the model behaving, so the important fixes live in code.

## The one-line summary

> **Rules in the prompt are suggestions. Rules in the code are laws.**
