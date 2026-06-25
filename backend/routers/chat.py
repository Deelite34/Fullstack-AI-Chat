import logging
from fastapi import APIRouter
from fastapi.responses import RedirectResponse, StreamingResponse

from config.settings import Config
from schemas.chat import ChatInput
# from database.db import get_db

from services.AIService import AIServiceManager

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
    chat_message: ChatInput,
):
    """Handles received chat text, and passess it to LLM and streams generated response """
    logger.info(
        f"Received input text message to /stream endpoint: {chat_message.chat_text}"
    )

    headers = {
        "X-Accel-Buffering": "no",  # Prevent some proxies / nginx from buffering the response
        "Cache-Control": "no-transform",  # Hint proxies and intermediaries not to transform or delay the content
    }
    ai_service = AIServiceManager.get_service(Config.AIService)

    return StreamingResponse(
        ai_service.get_response(chat_message.chat_text),
        media_type="text/plain; charset=utf-8",
        headers=headers,
    )
