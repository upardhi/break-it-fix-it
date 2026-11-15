"""Web server for the Cheapest Headphones Challenge.

Students open  http://<your-laptop-ip>:8001        on their phones or laptops.
Put this on the projector:  http://localhost:8001/board   (live leaderboard)

Run:  python challenge_server.py
Students only see a chat box. They never see the prompt, tools or trace.
"""

import asyncio
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from shopkart.run import has_api_key, load_env

ROOT = Path(__file__).resolve().parent
load_env()

from google.adk.agents.run_config import RunConfig  # noqa: E402
from google.adk.runners import Runner  # noqa: E402
from google.adk.sessions import InMemorySessionService  # noqa: E402
from google.genai import types  # noqa: E402

from challenge_agent.agent import LIST_PRICE, root_agent  # noqa: E402

APP_NAME = "shopbuddy_challenge"
sessions = InMemorySessionService()
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=sessions)
board: dict[str, dict] = {}
locks: dict[str, asyncio.Lock] = {}

app = FastAPI(title="ShopBuddy Challenge")


class ChatIn(BaseModel):
    sid: str
    team: str
    message: str


@app.get("/")
def student_page():
    return FileResponse(ROOT / "challenge_web" / "index.html")


@app.get("/board")
def board_page():
    return FileResponse(ROOT / "challenge_web" / "board.html")


@app.get("/api/board")
def get_board():
    return sorted(board.values(), key=lambda e: e["price"])


@app.post("/api/board/reset")
def reset_board():
    board.clear()
    return {"status": "ok"}


@app.post("/api/chat")
async def chat(body: ChatIn):
    sid = body.sid.strip()[:64] or "anon"
    team = body.team.strip()[:30] or "Anonymous"
    message = body.message.strip()[:1000]
    if not message:
        return {"reply": "Say something to ShopBuddy!", "price": LIST_PRICE, "how": ""}

    async with locks.setdefault(sid, asyncio.Lock()):
        session = await sessions.get_session(app_name=APP_NAME, user_id=sid, session_id=sid)
        if session is None:
            await sessions.create_session(app_name=APP_NAME, user_id=sid, session_id=sid)

        parts: list[str] = []
        try:
            async for event in runner.run_async(
                user_id=sid,
                session_id=sid,
                new_message=types.Content(role="user", parts=[types.Part(text=message)]),
                run_config=RunConfig(max_llm_calls=8),
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    parts += [p.text for p in event.content.parts if getattr(p, "text", None)]
        except Exception as exc:  # rate limits, network, bad key...
            print(f"[chat error] {type(exc).__name__}: {exc}")
            return {"reply": "⚠️ ShopBuddy is busy right now. Wait a few seconds and try again.",
                    "price": None, "how": "", "error": True}

        session = await sessions.get_session(app_name=APP_NAME, user_id=sid, session_id=sid)
        price = session.state.get("price", LIST_PRICE)
        how = session.state.get("how", "")

    best = board.get(team)
    if price < LIST_PRICE and (best is None or price < best["price"]):
        board[team] = {"team": team, "price": price, "how": how}
    return {"reply": "\n".join(parts) or "(no reply)", "price": price, "how": how}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8001"))  # adk web uses 8000
    if not has_api_key():
        print("\n⚠️  No GOOGLE_API_KEY found. Copy .env.example to .env and add your key, then restart.")
    print(f"\nStudents:  http://<this-laptop's-IP>:{port}\nProjector: http://localhost:{port}/board\n")
    uvicorn.run(app, host="0.0.0.0", port=port)
