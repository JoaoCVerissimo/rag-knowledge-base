from app.services.chunker import chunk_pages
from app.services.ingestion import PageContent


def test_single_page_short_text():
    """Short text should produce a single chunk."""
    pages = [PageContent(page_number=1, text="Hello world")]
    chunks = chunk_pages(pages, chunk_size=512, chunk_overlap=64)
    assert len(chunks) == 1
    assert chunks[0].content == "Hello world"
    assert chunks[0].chunk_index == 0
    assert chunks[0].metadata["page"] == 1


def test_long_text_produces_multiple_chunks():
    """Text longer than chunk_size should produce multiple chunks."""
    text = "word " * 200  # ~1000 chars
    pages = [PageContent(page_number=1, text=text)]
    chunks = chunk_pages(pages, chunk_size=100, chunk_overlap=20)
    assert len(chunks) > 1
    for i, chunk in enumerate(chunks):
        assert chunk.chunk_index == i


def test_multiple_pages():
    """Chunks from multiple pages should have correct page metadata."""
    pages = [
        PageContent(page_number=1, text="First page content."),
        PageContent(page_number=2, text="Second page content."),
    ]
    chunks = chunk_pages(pages, chunk_size=512, chunk_overlap=0)
    assert len(chunks) >= 1
    # First chunk should reference page 1
    assert chunks[0].metadata["page"] == 1


def test_empty_text():
    """Empty pages should produce no chunks."""
    pages = [PageContent(page_number=1, text="")]
    chunks = chunk_pages(pages, chunk_size=512, chunk_overlap=64)
    assert len(chunks) == 0


def test_paragraph_splitting():
    """Text with paragraphs should split on paragraph boundaries."""
    text = (
        "Paragraph one with content.\n\n"
        "Paragraph two with content.\n\n"
        "Paragraph three with content."
    )
    pages = [PageContent(page_number=1, text=text)]
    chunks = chunk_pages(pages, chunk_size=50, chunk_overlap=0)
    assert len(chunks) >= 2
