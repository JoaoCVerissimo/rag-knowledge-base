import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import Chunk
from app.models.document import Document, DocumentStatus


@dataclass
class ChunkResult:
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    filename: str
    content: str
    score: float
    metadata: dict


async def search_similar_chunks(
    session: AsyncSession,
    query_embedding: list[float],
    workspace_id: uuid.UUID,
    top_k: int = 5,
    threshold: float = 0.0,
) -> list[ChunkResult]:
    """Search for chunks similar to the query embedding within a workspace."""
    distance = Chunk.embedding.cosine_distance(query_embedding)
    score_expr = (1 - distance).label("score")

    stmt = (
        select(Chunk, Document.filename, score_expr)
        .join(Document, Chunk.document_id == Document.id)
        .where(Document.workspace_id == workspace_id)
        .where(Document.status == DocumentStatus.READY)
        .order_by(distance)
        .limit(top_k)
    )

    result = await session.execute(stmt)
    rows = result.all()

    results = []
    for chunk, filename, score in rows:
        if score >= threshold:
            results.append(
                ChunkResult(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    filename=filename,
                    content=chunk.content,
                    score=float(score),
                    metadata=chunk.metadata_ or {},
                )
            )

    return results
