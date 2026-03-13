import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models.document import Document, DocumentStatus
from app.models.workspace import Workspace
from app.schemas.documents import DocumentResponse, DocumentStatusResponse
from app.services.document_service import delete_document, save_upload
from app.tasks.document_tasks import process_document, reindex_document

router = APIRouter(tags=["documents"])


@router.post(
    "/workspaces/{workspace_id}/documents",
    response_model=DocumentResponse,
    status_code=201,
)
async def upload_document(
    workspace_id: uuid.UUID,
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
):
    """Upload a document for processing."""
    # Verify workspace exists
    workspace = await db.get(Workspace, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    try:
        document = await save_upload(db, file, workspace_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Dispatch background processing task
    process_document.delay(str(document.id))

    return document


@router.get(
    "/workspaces/{workspace_id}/documents",
    response_model=list[DocumentResponse],
)
async def list_documents(
    workspace_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Document)
        .where(Document.workspace_id == workspace_id)
        .order_by(Document.created_at.desc())
    )
    return result.scalars().all()


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    document = await db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.get("/documents/{document_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(document_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    document = await db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.delete("/documents/{document_id}", status_code=204)
async def remove_document(document_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    document = await db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    await delete_document(db, document)


@router.post("/documents/{document_id}/reindex", status_code=202)
async def trigger_reindex(document_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Re-process a document: delete chunks and re-embed."""
    document = await db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    document.status = DocumentStatus.PENDING
    document.chunk_count = 0
    document.error_message = None
    await db.commit()

    reindex_document.delay(str(document_id))

    return {"message": "Reindexing started", "document_id": str(document_id)}
