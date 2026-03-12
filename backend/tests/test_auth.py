from httpx import AsyncClient

from tests.conftest import create_test_user, get_auth_header


async def test_register_user(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "new@example.com",
            "password": "StrongPassword123!",
            "role": "brand",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@example.com"
    assert data["role"] == "brand"
    assert "id" in data


async def test_register_duplicate_email(client: AsyncClient) -> None:
    await create_test_user(client, email="dup@example.com")
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "dup@example.com",
            "password": "StrongPassword123!",
        },
    )
    assert response.status_code == 400


async def test_login_success(client: AsyncClient) -> None:
    await create_test_user(client)
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "TestPassword123!"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(client: AsyncClient) -> None:
    await create_test_user(client)
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "WrongPassword!"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 400


async def test_login_nonexistent_user(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "nobody@example.com", "password": "NoPassword!"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 400


async def test_authenticated_request(client: AsyncClient) -> None:
    await create_test_user(client)
    headers = await get_auth_header(client)
    response = await client.get("/health", headers=headers)
    assert response.status_code == 200


async def test_register_default_role_is_influencer(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "influencer@example.com",
            "password": "StrongPassword123!",
        },
    )
    assert response.status_code == 201
    assert response.json()["role"] == "influencer"


async def test_register_with_full_name(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "named@example.com",
            "password": "StrongPassword123!",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 201
    assert response.json()["full_name"] == "Test User"
