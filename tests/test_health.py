import pytest
from aiohttp.test_utils import TestClient, TestServer
from web.health import create_health_app

class FakeDB:
    async def ready(self): return True

class FakeBot:
    is_connected = True

class FakeSettings:
    pass

@pytest.mark.asyncio
async def test_health_endpoints():
    client = TestClient(TestServer(create_health_app(FakeDB(), FakeBot(), FakeSettings())))
    await client.start_server()
    try:
        response = await client.get("/health")
        assert response.status == 200
        response = await client.get("/ready")
        assert response.status == 200
    finally:
        await client.close()
