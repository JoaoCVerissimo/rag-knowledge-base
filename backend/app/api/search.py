import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models.workspace import Workspace
from app.schemas.search import SearchRequest, SearchResponse, SearchResult
from app.services.embedding import EmbeddingService
from app.services.vector_search import search_similar_chunks

router = APIRouter(tags=["search"])


@router.post(
    "/workspaces/{workspace_id}/search",
    response_model=SearchResponse,
)
async def semantic_search(
    workspace_id: uuid.UUID,
    body: SearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """Perform semantic vector search within a workspace."""
    workspace = await db.get(Workspace, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Embed the query
    embedding_service = EmbeddingService.get_instance()
    query_embedding = embedding_service.embed_query(body.query)

    # Search
    chunks = await search_similar_chunks(
        session=db,
        query_embedding=query_embedding,
        workspace_id=workspace_id,
        top_k=body.top_k,
        threshold=body.threshold,
    )

    results = [
        SearchResult(
            chunk_id=c.chunk_id,
            document_id=c.document_id,
            filename=c.filename,
            content=c.content,
            score=c.score,
            metadata=c.metadata,
        )
        for c in chunks
    ]

    return SearchResponse(results=results)
