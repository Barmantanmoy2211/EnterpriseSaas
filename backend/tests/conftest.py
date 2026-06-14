import asyncio

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings


async def _mongo_available() -> bool:
    try:
        client = AsyncIOMotorClient(settings.mongodb_uri, serverSelectionTimeoutMS=2000)
        await client.admin.command("ping")
        client.close()
        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def mongo_available():
    return asyncio.run(_mongo_available())


@pytest_asyncio.fixture
async def client(mongo_available):
    if not mongo_available:
        pytest.skip("MongoDB not available")
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
