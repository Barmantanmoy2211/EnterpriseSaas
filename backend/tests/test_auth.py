import pytest
from httpx import AsyncClient


@pytest.fixture
async def registered_tenant(client: AsyncClient):
    payload = {
        "tenant_name": "Test Corp",
        "tenant_slug": "test-corp-auth",
        "email": "admin@test-corp-auth.com",
        "password": "securepass123",
        "first_name": "Admin",
        "last_name": "User",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 200
    return response.json()


@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient, registered_tenant):
    assert registered_tenant["user"]["email"] == "admin@test-corp-auth.com"
    assert "access_token" in registered_tenant["tokens"]

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@test-corp-auth.com",
            "password": "securepass123",
            "tenant_slug": "test-corp-auth",
        },
    )
    assert login_response.status_code == 200
    assert login_response.json()["tokens"]["access_token"]


@pytest.mark.asyncio
async def test_me_endpoint(client: AsyncClient, registered_tenant):
    token = registered_tenant["tokens"]["access_token"]
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "admin@test-corp-auth.com"


@pytest.mark.asyncio
async def test_tenant_isolation(client: AsyncClient):
    tenant_a = {
        "tenant_name": "Tenant A",
        "tenant_slug": "tenant-a-iso",
        "email": "admin@tenant-a.com",
        "password": "securepass123",
    }
    tenant_b = {
        "tenant_name": "Tenant B",
        "tenant_slug": "tenant-b-iso",
        "email": "admin@tenant-b.com",
        "password": "securepass123",
    }
    res_a = await client.post("/api/v1/auth/register", json=tenant_a)
    res_b = await client.post("/api/v1/auth/register", json=tenant_b)
    token_a = res_a.json()["tokens"]["access_token"]
    token_b = res_b.json()["tokens"]["access_token"]

    me_a = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token_a}"})
    me_b = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token_b}"})

    assert me_a.json()["tenant_id"] != me_b.json()["tenant_id"]
