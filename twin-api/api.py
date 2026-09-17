"""FastAPI wrapper for Landon's digital twin — SSE chat + session reset.

Deploy this always-on service (Railway / Render / Fly / Modal). Gradio is not
on the production path.
"""

from __future__ import annotations

import asyncio
import json
import os
import time
import uuid
from collections import defaultdict, deque
from typing import Deque

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from twin import chat, clear_history

load_dotenv(override=True)

app = FastAPI(title="Landon Nguyen Digital Twin API", version="1.0.0")

# Comma-separated portfolio origins, e.g.
# https://landonnguyen.vercel.app,http://localhost:3000
_raw_origins = os.getenv(
    "PORTFOLIO_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
)
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()]

RATE_LIMIT_PER_MIN = int(os.getenv("TWIN_RATE_LIMIT_PER_MIN", "20"))
OPTIONAL_API_SECRET = os.getenv("TWIN_API_SECRET", "").strip()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Session-Id", "X-Twin-Secret", "Authorization"],
)

# Simple sliding-window rate limit keyed by client IP + session
_rate_buckets: dict[str, Deque[float]] = defaultdict(deque)
_rate_lock = asyncio.Lock()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str | None = Field(default=None, max_length=128)


class ResetRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=128)


class SessionResponse(BaseModel):
    session_id: str


def _client_key(request: Request, session_id: str) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    ip = forwarded.split(",")[0].strip() if forwarded else (
        request.client.host if request.client else "unknown"
    )
    return f"{ip}:{session_id}"


async def _enforce_rate_limit(request: Request, session_id: str) -> None:
    key = _client_key(request, session_id)
    now = time.monotonic()
    window = 60.0
    async with _rate_lock:
        bucket = _rate_buckets[key]
        while bucket and now - bucket[0] > window:
            bucket.popleft()
        if len(bucket) >= RATE_LIMIT_PER_MIN:
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again shortly.")
        bucket.append(now)


def _check_optional_secret(request: Request) -> None:
    if not OPTIONAL_API_SECRET:
        return
    provided = (
        request.headers.get("x-twin-secret")
        or request.headers.get("authorization", "").removeprefix("Bearer ").strip()
    )
    if provided != OPTIONAL_API_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")


def _normalize_session_id(raw: str | None) -> str:
    sid = (raw or "").strip()
    if not sid:
        return str(uuid.uuid4())
    # Keep ids filesystem-/sqlite-safe
    safe = "".join(c for c in sid if c.isalnum() or c in "-_")[:128]
    return safe or str(uuid.uuid4())


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "digital-twin"}


@app.post("/session", response_model=SessionResponse)
async def create_session() -> SessionResponse:
    return SessionResponse(session_id=str(uuid.uuid4()))


@app.post("/chat/reset")
async def reset_chat(body: ResetRequest, request: Request) -> dict[str, str]:
    _check_optional_secret(request)
    session_id = _normalize_session_id(body.session_id)
    await clear_history(session_id)
    return {"status": "cleared", "session_id": session_id}


@app.post("/chat/stream")
async def chat_stream(body: ChatRequest, request: Request) -> StreamingResponse:
    _check_optional_secret(request)
    message = body.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message required")

    session_id = _normalize_session_id(body.session_id)
    await _enforce_rate_limit(request, session_id)

    async def event_generator():
        # Announce session so the client can persist it
        yield f"event: session\ndata: {json.dumps({'session_id': session_id})}\n\n"
        try:
            async for delta in chat(message, session_id):
                yield f"event: token\ndata: {json.dumps({'delta': delta})}\n\n"
            yield f"event: done\ndata: {json.dumps({'ok': True})}\n\n"
        except Exception as exc:  # noqa: BLE001
            yield f"event: error\ndata: {json.dumps({'error': str(exc)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "X-Session-Id": session_id,
        },
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=False)
