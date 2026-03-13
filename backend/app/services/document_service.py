import logging
import os
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.document import Document, DocumentStatus

logger = logging.getLogger(__name__)

ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "text/plain": "txt",
    "text/markdown": "md",
}

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".markdown"}


def get_file_type(filename: str, content_type: str | None) -> str:
    """Determine file type from extension or content type."""
    ext = Path(filename).suffix.lower()
    if ext in ALLOWED_EXTENSIONS:
        return ext.lstrip(".")
    if content_type and content_type in ALLOWED_TYPES:
        return ALLOWED_TYPES[content_type]
    raise ValueError(f"Unsupported file type: {ext} ({content_type})")


async def save_upload(
    session: AsyncSession,
    file: UploadFile,
    workspace_id: uuid.UUID,
) -> Document:
    """Save an uploaded file to disk and create a database record."""
    file_type = get_file_type(file.filename, file.content_type)

    # Create workspace upload directory
    workspace_dir = Path(settings.UPLOAD_DIR) / str(workspace_id)
    workspace_dir.mkdir(parents=True, exist_ok=True)

    # Save file with unique name
    doc_id = uuid.uuid4()
    file_ext = Path(file.filename).suffix
    file_path = workspace_dir / f"{doc_id}{file_ext}"

    content = await file.read()
    file_path.write_bytes(content)

    # Create database record
    document = Document(
        id=doc_id,
        workspace_id=workspace_id,
        filename=file.filename,
        file_path=str(file_path),
        file_type=file_type,
        file_size=len(content),
        status=DocumentStatus.PENDING,
    )
    session.add(document)
    await session.commit()
    await session.refresh(document)

    logger.info("Saved document %s (%s, %d bytes)", document.id, file_type, len(content))
    return document


async def delete_document(session: AsyncSession, document: Document) -> None:
    """Delete a document and its file from disk."""
    # Delete file
    try:
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
    except OSError:
        logger.warning("Failed to delete file: %s", document.file_path)

    await session.delete(document)
    await session.commit()
