import json
import logging
import uuid
from collections.abc import AsyncGenerator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Message, MessageRole
from app.services.embedding import EmbeddingService
from app.services.llm_client import SYSTEM_PROMPT, stream_llm_response
from app.services.vector_search import ChunkResult, search_similar_chunks

logger = logging.getLogger(__name__)


async def stream_chat(
    session: AsyncSession,
    conversation_id: uuid.UUID,
    user_message: str,
    workspace_id: uuid.UUID,
    top_k: int = 5,
) -> AsyncGenerator[str, None]:
    """Execute the full RAG pipeline and stream SSE events.

    1. Save user message
    2. Embed the query
    3. Retrieve relevant chunks
    4. Build prompt with context + history
    5. Stream LLM response
    6. Save assistant message with citations
    7. Yield SSE events throughout
    """
    # Save user message
    user_msg = Message(
        conversation_id=conversation_id,
        role=MessageRole.USER,
        content=user_message,
    )
    session.add(user_msg)
    await session.commit()

    # Embed the query
    embedding_service = EmbeddingService.get_instance()
    query_embedding = embedding_service.embed_query(user_message)

    # Retrieve relevant chunks
    chunks = await search_similar_chunks(
        session=session,
        query_embedding=query_embedding,
        workspace_id=workspace_id,
        top_k=top_k,
    )

    # Build context from chunks
    context = _build_context(chunks)

    # Get conversation history (last 10 messages)
    history = await _get_history(session, conversation_id, limit=10)

    # Assemble messages for LLM
    llm_messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]
    if context:
        llm_messages.append({"role": "system", "content": f"Context:\n{context}"})
    llm_messages.extend(history)
    llm_messages.append({"role": "user", "content": user_message})

    # Stream response
    full_response = ""
    async for token in stream_llm_response(llm_messages):
        full_response += token
        yield f"event: chunk\ndata: {json.dumps({'content': token, 'type': 'text'})}\n\n"

    # Build citations
    citations = _build_citations(chunks)
    yield f"event: citations\ndata: {json.dumps({'citations': citations})}\n\n"

    # Save assistant message
    assistant_msg = Message(
        conversation_id=conversation_id,
        role=MessageRole.ASSISTANT,
        content=full_response,
        citations=citations,
    )
    session.add(assistant_msg)
    await session.commit()

    yield f"event: done\ndata: {json.dumps({'message_id': str(assistant_msg.id)})}\n\n"


def _build_context(chunks: list[ChunkResult]) -> str:
    if not chunks:
        return ""
    parts = []
    for i, chunk in enumerate(chunks):
        page = chunk.metadata.get("page", "?")
        parts.append(f"[{i + 1}] (Source: {chunk.filename}, Page {page})\n{chunk.content}")
    return "\n\n".join(parts)


def _build_citations(chunks: list[ChunkResult]) -> list[dict]:
    return [
        {
            "chunk_id": str(chunk.chunk_id),
            "document_id": str(chunk.document_id),
            "filename": chunk.filename,
            "snippet": chunk.content[:200],
        }
        for chunk in chunks
    ]


async def _get_history(
    session: AsyncSession, conversation_id: uuid.UUID, limit: int = 10
) -> list[dict]:
    stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    messages = list(reversed(result.scalars().all()))

    # Exclude the user message we just added (last one)
    if messages and messages[-1].role == MessageRole.USER:
        messages = messages[:-1]

    return [{"role": msg.role.value, "content": msg.content} for msg in messages]
