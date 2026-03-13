import tempfile
from pathlib import Path

import pytest

from app.services.ingestion import extract_text


def test_extract_text_file():
    """Should extract text from a .txt file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Hello, this is test content.")
        f.flush()
        pages = extract_text(f.name, "txt")

    assert len(pages) == 1
    assert pages[0].text == "Hello, this is test content."
    assert pages[0].page_number == 1


def test_extract_markdown_file():
    """Should extract text from a .md file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# Heading\n\nSome markdown content.")
        f.flush()
        pages = extract_text(f.name, "md")

    assert len(pages) == 1
    assert "# Heading" in pages[0].text


def test_extract_empty_file():
    """Empty file should return no pages."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("")
        f.flush()
        pages = extract_text(f.name, "txt")

    assert len(pages) == 0


def test_unsupported_type():
    """Unsupported file type should raise ValueError."""
    with pytest.raises(ValueError, match="Unsupported file type"):
        extract_text("/tmp/test.xyz", "xyz")
