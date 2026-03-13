import io

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_upload_document(client: AsyncClient):
    # Create workspace first
    ws_resp = await client.post("/api/v1/workspaces", json={"name": "Test WS"})
    ws_id = ws_resp.json()["id"]

    # Upload a text file
    file_content = b"This is a test document with some content."
    response = await client.post(
        f"/api/v1/workspaces/{ws_id}/documents",
        files={"file": ("test.txt", io.BytesIO(file_content), "text/plain")},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test.txt"
    assert data["file_type"] == "txt"
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_list_documents(client: AsyncClient):
    ws_resp = await client.post("/api/v1/workspaces", json={"name": "Test WS"})
    ws_id = ws_resp.json()["id"]

    # Upload two documents
    for name in ["doc1.txt", "doc2.txt"]:
        await client.post(
            f"/api/v1/workspaces/{ws_id}/documents",
            files={"file": (name, io.BytesIO(b"content"), "text/plain")},
        )

    response = await client.get(f"/api/v1/workspaces/{ws_id}/documents")
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_delete_document(client: AsyncClient):
    ws_resp = await client.post("/api/v1/workspaces", json={"name": "Test WS"})
    ws_id = ws_resp.json()["id"]

    upload_resp = await client.post(
        f"/api/v1/workspaces/{ws_id}/documents",
        files={"file": ("test.txt", io.BytesIO(b"content"), "text/plain")},
    )
    doc_id = upload_resp.json()["id"]

    response = await client.delete(f"/api/v1/documents/{doc_id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_upload_unsupported_type(client: AsyncClient):
    ws_resp = await client.post("/api/v1/workspaces", json={"name": "Test WS"})
    ws_id = ws_resp.json()["id"]

    response = await client.post(
        f"/api/v1/workspaces/{ws_id}/documents",
        files={"file": ("test.exe", io.BytesIO(b"data"), "application/octet-stream")},
    )
    assert response.status_code == 400
