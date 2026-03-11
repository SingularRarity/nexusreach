from httpx import AsyncClient


async def test_health_returns_200(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200


async def test_health_returns_ok_status(client: AsyncClient) -> None:
    response = await client.get("/health")
    data = response.json()
    assert data == {"status": "ok"}
