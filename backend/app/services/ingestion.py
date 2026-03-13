import logging
from dataclasses import dataclass
from pathlib import Path

import fitz  # pymupdf

logger = logging.getLogger(__name__)


@dataclass
class PageContent:
    page_number: int
    text: str


def extract_text(file_path: str, file_type: str) -> list[PageContent]:
    """Extract text from a document file.

    Returns a list of PageContent with page numbers and text.
    """
    path = Path(file_path)

    if file_type == "pdf":
        return _extract_pdf(path)
    elif file_type in ("md", "markdown"):
        return _extract_text_file(path)
    elif file_type == "txt":
        return _extract_text_file(path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")


def _extract_pdf(path: Path) -> list[PageContent]:
    pages = []
    doc = fitz.open(str(path))
    try:
        for i, page in enumerate(doc):
            text = page.get_text().strip()
            if text:
                pages.append(PageContent(page_number=i + 1, text=text))
    finally:
        doc.close()
    logger.info("Extracted %d pages from PDF: %s", len(pages), path.name)
    return pages


def _extract_text_file(path: Path) -> list[PageContent]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    return [PageContent(page_number=1, text=text)]
