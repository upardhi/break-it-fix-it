"""Helpers to run an agent once from Python (used by rehearse.py and the live tests)."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_env() -> None:
    """Read KEY=VALUE lines from .env in the project folder (without overriding real env vars)."""
    env = ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def has_api_key() -> bool:
    load_env()
    return bool(os.environ.get("GOOGLE_API_KEY")) or os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "").upper() in ("1", "TRUE")


async def run_once(agent, messages: str | list[str]) -> dict:
    """Send one or more user messages in a fresh session. Returns reply, tool calls and final state."""
    from google.adk.agents.run_config import RunConfig
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types

    if isinstance(messages, str):
        messages = [messages]
    service = InMemorySessionService()
    runner = Runner(agent=agent, app_name="rehearse", session_service=service)
    session = await service.create_session(app_name="rehearse", user_id="presenter")

    calls, results, replies = [], [], []
    for message in messages:
        text = []
        async for event in runner.run_async(
            user_id="presenter",
            session_id=session.id,
            new_message=types.Content(role="user", parts=[types.Part(text=message)]),
            run_config=RunConfig(max_llm_calls=10),  # no runaway loops
        ):
            for call in event.get_function_calls():
                calls.append((call.name, dict(call.args or {})))
            for resp in event.get_function_responses():
                results.append((resp.name, resp.response))
            if event.is_final_response() and event.content and event.content.parts:
                text += [p.text for p in event.content.parts if getattr(p, "text", None)]
        replies.append("\n".join(text))

    final = await service.get_session(app_name="rehearse", user_id="presenter", session_id=session.id)
    return {"replies": replies, "reply": replies[-1], "calls": calls, "results": results, "state": dict(final.state)}
