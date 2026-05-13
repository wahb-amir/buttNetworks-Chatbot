from __future__ import annotations

import asyncio
import hmac
import inspect
import json
import re
import time
from collections import defaultdict, deque
from typing import Any, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.core.config import settings
from app.repositories.chat_repository import (
    get_or_create_conversation,
    get_recent_messages,
    save_message,
)
from app.services.rag.pipeline import answer_with_rag

router = APIRouter(prefix="/api/v1", tags=["chat"])


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=128)
    message: str = Field(..., min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    conversation_id: str
    reply: str
    chunks: list[Any] = []


def _extract_token(
    authorization: Optional[str],
    x_internal_token: Optional[str],
) -> str | None:
    if x_internal_token:
        return x_internal_token.strip()

    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()

    return None


async def verify_internal_token(
    authorization: Optional[str] = Header(default=None),
    x_internal_token: Optional[str] = Header(default=None),
) -> str:
    token = _extract_token(authorization, x_internal_token)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing internal token.",
        )

    expected = getattr(settings, "internal_api_token", None)
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server internal token is not configured.",
        )

    if not hmac.compare_digest(token, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid internal token.",
        )

    return token


RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_MAX_REQUESTS = 30

_rate_buckets: dict[str, deque[float]] = defaultdict(deque)
_rate_lock = asyncio.Lock()


async def rate_limit(
    request: Request,
    token: str = Depends(verify_internal_token),
) -> None:
    client_ip = request.client.host if request.client else "unknown"
    bucket_key = f"{client_ip}:{token[:12]}"

    now = time.monotonic()

    async with _rate_lock:
        bucket = _rate_buckets[bucket_key]

        while bucket and (now - bucket[0]) > RATE_LIMIT_WINDOW_SECONDS:
            bucket.popleft()

        if len(bucket) >= RATE_LIMIT_MAX_REQUESTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please slow down.",
            )

        bucket.append(now)


def _sse(data: Any, event: str | None = None) -> str:
    payload = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False)
    msg = ""
    if event:
        msg += f"event: {event}\n"
    for line in payload.splitlines() or [""]:
        msg += f"data: {line}\n"
    msg += "\n"
    return msg


def _stream_chunks(text: str):
    # Word-ish chunks that preserve spaces, so the UI feels like real streaming.
    return re.findall(r"\S+\s*", text)


@router.post("/chat", response_model=ChatResponse)
async def website_chat(
    payload: ChatRequest,
    _: None = Depends(rate_limit),
):
    """
    Non-streaming fallback endpoint.
    """
    session_id = payload.session_id.strip()
    text = payload.message.strip()

    try:
        conversation = get_or_create_conversation(session_id)
        conversation_id = str(conversation["id"])

        save_message(
            conversation_id=conversation_id,
            role="user",
            content=text,
        )

        history = get_recent_messages(conversation_id, limit=8)

        result = answer_with_rag(query=text, chat_history=history)
        if inspect.isawaitable(result):
            reply, chunks = await result
        else:
            reply, chunks = result

        save_message(
            conversation_id=conversation_id,
            role="assistant",
            content=reply,
        )

        return ChatResponse(
            conversation_id=conversation_id,
            reply=reply,
            chunks=chunks or [],
        )

    except HTTPException:
        raise
    except Exception as e:
        if settings.app_env == "dev":
            print(f"❌ [CHAT API ERROR] {e}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="I’m having trouble processing that right now. Please try again later.",
        )


@router.post("/chat/stream")
async def website_chat_stream(
    payload: ChatRequest,
    _: None = Depends(rate_limit),
):
    """
    Streaming SSE endpoint for the website chatbot.
    The frontend should call this through the Next.js proxy.
    """
    session_id = payload.session_id.strip()
    text = payload.message.strip()

    try:
        conversation = get_or_create_conversation(session_id)
        conversation_id = str(conversation["id"])

        save_message(
            conversation_id=conversation_id,
            role="user",
            content=text,
        )

        history = get_recent_messages(conversation_id, limit=8)

        result = answer_with_rag(query=text, chat_history=history)
        if inspect.isawaitable(result):
            reply, chunks = await result
        else:
            reply, chunks = result

        save_message(
            conversation_id=conversation_id,
            role="assistant",
            content=reply,
        )

    except HTTPException:
        raise
    except Exception as e:
        if settings.app_env == "dev":
            print(f"❌ [CHAT STREAM ERROR] {e}")

        async def error_stream():
            yield _sse({"error": "I’m having trouble processing that right now."}, event="error")
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            error_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache, no-transform",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    async def event_stream():
        yield _sse({"conversation_id": conversation_id}, event="meta")

        streamed_text = ""
        for chunk in _stream_chunks(reply):
            streamed_text += chunk
            yield _sse({"type": "token", "token": chunk}, event="token")
            await asyncio.sleep(0.01)

        yield _sse(
            {
                "conversation_id": conversation_id,
                "reply": reply,
                "chunks": chunks or [],
            },
            event="done",
        )
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )