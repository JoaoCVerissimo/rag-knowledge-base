import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_workspace(client: AsyncClient):
    response = await client.post(
        "/api/v1/workspaces",
        json={"name": "Test Workspace", "description": "A test workspace"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Workspace"
    assert data["description"] == "A test workspace"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_workspaces(client: AsyncClient):
    # Create two workspaces
    await client.post("/api/v1/workspaces", json={"name": "WS 1"})
    await client.post("/api/v1/workspaces", json={"name": "WS 2"})

    response = await client.get("/api/v1/workspaces")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_workspace(client: AsyncClient):
    create_resp = await client.post("/api/v1/workspaces", json={"name": "WS"})
    ws_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/workspaces/{ws_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "WS"


@pytest.mark.asyncio
async def test_get_workspace_not_found(client: AsyncClient):
    response = await client.get(
        "/api/v1/workspaces/00000000-0000-0000-0000-000000000000"
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_workspace(client: AsyncClient):
    create_resp = await client.post("/api/v1/workspaces", json={"name": "Old"})
    ws_id = create_resp.json()["id"]

    response = await client.patch(
        f"/api/v1/workspaces/{ws_id}", json={"name": "New"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New"


@pytest.mark.asyncio
async def test_delete_workspace(client: AsyncClient):
    create_resp = await client.post("/api/v1/workspaces", json={"name": "Delete Me"})
    ws_id = create_resp.json()["id"]

    response = await client.delete(f"/api/v1/workspaces/{ws_id}")
    assert response.status_code == 204

    get_resp = await client.get(f"/api/v1/workspaces/{ws_id}")
    assert get_resp.status_code == 404
