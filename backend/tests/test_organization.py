import pytest
from httpx import AsyncClient


@pytest.fixture
async def auth_headers(client: AsyncClient):
    payload = {
        "tenant_name": "Org Test Corp",
        "tenant_slug": "org-test-corp",
        "email": "org@org-test.com",
        "password": "securepass123",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    token = response.json()["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_node_types_and_tree(client: AsyncClient, auth_headers):
    type_res = await client.post(
        "/api/v1/organization/node-types",
        json={
            "code": "company",
            "label": "Company",
            "is_root_allowed": True,
            "allowed_child_types": ["division"],
        },
        headers=auth_headers,
    )
    assert type_res.status_code == 201

    await client.post(
        "/api/v1/organization/node-types",
        json={
            "code": "division",
            "label": "Division",
            "is_root_allowed": False,
            "allowed_child_types": [],
        },
        headers=auth_headers,
    )

    node_res = await client.post(
        "/api/v1/organization/nodes",
        json={"node_type": "company", "name": "Acme Inc"},
        headers=auth_headers,
    )
    assert node_res.status_code == 201
    assert node_res.json()["depth"] == 0

    tree_res = await client.get("/api/v1/organization/nodes/tree", headers=auth_headers)
    assert tree_res.status_code == 200
    tree = tree_res.json()
    assert len(tree) == 1
    assert tree[0]["name"] == "Acme Inc"
