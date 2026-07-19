import logging
from typing import Annotated

from sqlalchemy.orm import Session

from db import get_session
from config.settings import config
from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse, StreamingResponse
from schemas.chat import ChatInput
from services.ai_service import AIServiceManager

llm_router = APIRouter()
logger = logging.getLogger(__name__)


@llm_router.get("/", status_code=200)
async def debug_root():
    return RedirectResponse("/api/")


@llm_router.get("/api", status_code=200)
async def debug_view():
    return {"message": "backend is working"}


@llm_router.post("/api/stream", status_code=200)
async def stream_response(
    chat_message: ChatInput, session: Annotated[Session, Depends(get_session)]
):
    """Handle received chat text, pass it to LLM and stream generated response."""
    logger.info(
        "Received input text message to /stream endpoint: %s",
        chat_message.chat_text,
    )

    headers = {
        "X-Accel-Buffering": "no",  # Prevent some proxies / nginx from buffering the response
        "Cache-Control": "no-transform",  # Hint proxies and intermediaries not to transform or delay the content
    }
    ai_service = AIServiceManager.get_service(config.AIService, config)

    return StreamingResponse(
        ai_service.get_response(chat_message.chat_text),
        media_type="text/plain; charset=utf-8",
        headers=headers,
    )


@llm_router.post("/api/stream/debug", status_code=200)
async def stream_debug_response(
    chat_message: ChatInput,
    db: Annotated[Session, Depends(get_session)],
):
    """Handle received chat text, pass it to LLM and return generated response."""
    logger.info(
        "Received input text message to /stream/debug endpoint: %s",
        chat_message.chat_text,
    )

    headers = {
        "X-Accel-Buffering": "no",  # Prevent some proxies / nginx from buffering the response
        "Cache-Control": "no-transform",  # Hint proxies and intermediaries not to transform or delay the content
    }
    ai_service = AIServiceManager.get_service(config.AIService, config)

    return StreamingResponse(
        ai_service.get_response(chat_message.chat_text),
        media_type="text/plain; charset=utf-8",
        headers=headers,
    )
