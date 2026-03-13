import logging
import os
from collections.abc import AsyncGenerator

import litellm

from app.config import settings

logger = logging.getLogger(__name__)


def _configure_litellm() -> None:
    """Set environment variables for LiteLLM based on our config."""
    if settings.OLLAMA_API_BASE:
        os.environ["OLLAMA_API_BASE"] = settings.OLLAMA_API_BASE
    if settings.OPENAI_API_KEY:
        os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
    if settings.OPENAI_API_BASE:
        os.environ["OPENAI_API_BASE"] = settings.OPENAI_API_BASE
    # Suppress litellm telemetry/logging noise
    litellm.suppress_debug_info = True


_configure_litellm()

SYSTEM_PROMPT = """You are a helpful assistant answering questions based on the provided context documents.
Always cite your sources using [1], [2], etc. corresponding to the provided context chunks.
If the context doesn't contain relevant information, say so clearly.
Do not make up information not present in the context."""


async def stream_llm_response(
    messages: list[dict],
) -> AsyncGenerator[str, None]:
    """Stream tokens from the configured LLM.

    Args:
        messages: List of message dicts with 'role' and 'content'.

    Yields:
        Individual tokens as strings.
    """
    try:
        response = await litellm.acompletion(
            model=settings.LLM_MODEL,
            messages=messages,
            stream=True,
        )
        async for part in response:
            token = part.choices[0].delta.content
            if token:
                yield token
    except Exception:
        logger.exception("LLM streaming error")
        yield "\n\n[Error: Failed to get response from LLM. Please check your LLM configuration.]"
