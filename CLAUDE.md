# Break It, Fix It: project context for Claude

Materials for a ~45-minute talk by Umashankar P to ~30 final-year students at a Google Developer Community event. Another speaker builds an AI agent; this talk breaks it and fixes it, using **ShopBuddy**, an online-store support agent (Google ADK + Gemini). The human-facing guide is `START-HERE.md`; read it first.

## Layout
- `break-it-fix-it.html`: the presentation. A single self-contained HTML file: 26 slides, keyboard-driven (→ step, N next problem, 1–4 jump). Each problem has 4 slides: Break → Why? (quiz) → Fix (code diff) → Run it again. Fragments reveal in `data-step` order. Text with `data-edit` is editable in the browser (saved to localStorage).
- `shopbuddy/`: Python project.
  - `broken_agent/agent.py`: **bugs are deliberate**, one per problem. Don't "fix" them.
  - `fixed_agent/agent.py`: the fixes: `get_policy`, `cancel_order`, order-ID regex, refund timeout with max 2 attempts, `guard` via `before_tool_callback` (refunds above ₹5,000 need a human), coupons limited to public ≤10% in code, reviews wrapped in escaped `<review>` tags.
  - `challenge_agent/`: rules only in the prompt, so students can break it. `challenge_server.py` (FastAPI, port 8001) serves `challenge_web/index.html` (student chat) and `/board` (leaderboard).
  - `shopkart/`: fake store data (`data.py`), per-session state (`store.py`), fake payment gateway with a down-switch file (`payments.py`, toggled by `chaos.py`), `run.py` (`load_env`, `run_once` helper), `__init__.py` (MODEL from `SHOPBUDDY_MODEL`, default `gemini-flash-latest`; `truststore` injection).
  - `rehearse.py`: runs the 4 demo prompts on both agents. `try_injections.py`: tests Problem 4 attack variants.
  - `tests/test_tools.py`: 19 offline tests (no API). `tests/test_live_agent.py`: 4 live tests, skipped without a key.

## Keep these in sync
Changing a demo means updating all of: the slide in `break-it-fix-it.html`, the demo table in `START-HERE.md` §6 and `shopbuddy/README.md`, `DEMOS` in `rehearse.py`, and the data in `shopkart/data.py`. The fixed agent's approval limit is ₹5,000 in both code and slides.

## Environment gotchas (Windows)
- No `python` on PATH; use `uv` (`uv venv --python 3.12`, then `uv pip install --system-certs -r requirements.txt`).
- TLS is intercepted on this PC: uv needs `--system-certs`; Python uses `truststore` (already wired in `shopkart/__init__.py`).
- Long paths (>260 chars) silently break package installs. Keep the project at a short path such as `C:\talk`.
- Gemini key goes in `shopbuddy/.env` (never commit it). Its Google project is 587738934588 (prepaid credits plus a spend cap).
- ADK version used: google-adk 2.14.1. `ToolContext` is an alias of `google.adk.agents.context.Context`; a parameter named `tool_context` is injected and hidden from the model.

## Status (15 Nov 2026)
- Problems 1, 2, 3: verified against real Gemini. Broken agent breaks; fixed agent holds. Problem 2 is a two-turn demo (request, then `ORD-10421`), because the model always asks for the ID first.
- **Problem 4 (open):** the planted review never fooled the broken agent (0/11). Stronger attacks in `try_injections.py` are untested (spend cap hit). Next step: run `python try_injections.py`; if one works ≥2/3, put its text in `INJECTED_REVIEW_TEXT` and update the Problem 4 Break slide's review card. Otherwise reframe the slide as "it may resist; that's why the limit lives in code".
- Deck placeholders still to fill: `[Speaker name]` (Meet ShopBuddy slide), `[your link or QR here]` (challenge slide).

## Commands (from `shopbuddy/`, venv active)
- `python -m pytest tests/test_tools.py` runs offline tests.
- `python -m pytest` also runs live tests when `.env` has a key.
- `python rehearse.py [1-4]`, `python try_injections.py [name] [runs]`.
- `adk web` starts the stage demo UI on :8000. `python challenge_server.py` serves the challenge on :8001. `python chaos.py down|up` toggles the payment outage.
