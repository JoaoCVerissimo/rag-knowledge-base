import logging
from dataclasses import dataclass

from app.config import settings

logger = logging.getLogger(__name__)

SEPARATORS = ["\n\n", "\n", ". ", " ", ""]


@dataclass
class TextChunk:
    content: str
    chunk_index: int
    start_char: int
    end_char: int
    metadata: dict


def chunk_pages(
    pages: list,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[TextChunk]:
    """Split pages into overlapping chunks using recursive character splitting.

    Args:
        pages: List of PageContent objects with page_number and text.
        chunk_size: Maximum chunk size in characters.
        chunk_overlap: Number of overlapping characters between chunks.

    Returns:
        List of TextChunk objects.
    """
    chunk_size = chunk_size or settings.CHUNK_SIZE
    chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    # Build a single text with page metadata tracking
    full_text = ""
    page_boundaries: list[tuple[int, int, int]] = []  # (start, end, page_number)

    for page in pages:
        start = len(full_text)
        full_text += page.text + "\n\n"
        end = len(full_text)
        page_boundaries.append((start, end, page.page_number))

    if not full_text.strip():
        return []

    # Split the text
    raw_chunks = _recursive_split(full_text, chunk_size, chunk_overlap)

    # Build TextChunk objects with metadata
    chunks = []
    for i, (text, start, end) in enumerate(raw_chunks):
        # Find which page this chunk belongs to
        page_num = _find_page(start, page_boundaries)
        chunks.append(
            TextChunk(
                content=text,
                chunk_index=i,
                start_char=start,
                end_char=end,
                metadata={"page": page_num},
            )
        )

    logger.info("Created %d chunks from %d pages", len(chunks), len(pages))
    return chunks


def _recursive_split(text: str, chunk_size: int, overlap: int) -> list[tuple[str, int, int]]:
    """Split text recursively by trying separators in order.

    Returns list of (chunk_text, start_char, end_char).
    """
    if len(text) <= chunk_size:
        stripped = text.strip()
        if stripped:
            return [(stripped, 0, len(text))]
        return []

    results: list[tuple[str, int, int]] = []
    offset = 0

    for sep in SEPARATORS:
        if sep == "":
            # Last resort: hard split
            pieces = _hard_split(text, chunk_size)
        else:
            pieces = text.split(sep)

        if len(pieces) <= 1:
            continue

        # Merge small pieces to stay close to chunk_size
        current = ""
        current_start = offset

        for piece in pieces:
            candidate = current + sep + piece if current else piece
            if len(candidate) <= chunk_size:
                current = candidate
            else:
                if current.strip():
                    results.append((current.strip(), current_start, current_start + len(current)))
                # Apply overlap
                if overlap > 0 and current:
                    overlap_text = current[-overlap:]
                    current_start = current_start + len(current) - overlap
                    current = overlap_text + sep + piece
                else:
                    current_start = current_start + len(current) + len(sep)
                    current = piece

        if current.strip():
            results.append((current.strip(), current_start, current_start + len(current)))

        return results

    # Fallback: just return the whole text
    return [(text.strip(), 0, len(text))]


def _hard_split(text: str, chunk_size: int) -> list[str]:
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]


def _find_page(char_offset: int, boundaries: list[tuple[int, int, int]]) -> int:
    for start, end, page_num in boundaries:
        if start <= char_offset < end:
            return page_num
    return boundaries[-1][2] if boundaries else 1
