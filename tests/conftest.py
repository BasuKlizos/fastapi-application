import os
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

# Indicate that we're in testing mode
os.environ["TESTING"] = "1"

@pytest_asyncio.fixture(scope="module")
async def async_client():
    """Fixture to provide an HTTPX client for API testing."""
    async with AsyncClient(
        transport=ASGITransport(app), base_url="http://test"
    ) as client:
        yield client