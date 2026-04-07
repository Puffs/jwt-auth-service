from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient
from tests.utils import mock_users, auth_client

from app.models import RefreshToken


async def test_register(
    db_session: AsyncSession,
    client: AsyncClient,
):
    """Тест регистрации пользователя."""
    response = await client.post("/api/v1/register" , json={"username":"pufff", "password":"!23QWEasd", "email":"pufff@mail.ru"})

    assert response.status_code == status.HTTP_201_CREATED


    
async def test_login(
    db_session: AsyncSession,
    client: AsyncClient,
    mock_users: list,
):
    """Тест аутентификации пользователя."""
    response = await client.post("/api/v1/login" , data={"username":"pufff2@mail.ru", "password":"!23QWEasd"})

    assert response.status_code == status.HTTP_200_OK


async def test_verify(
    auth_client
):
    """Тест проверки пользователя."""
    response = await auth_client.get("/api/v1/verify")
    assert response.status_code == status.HTTP_200_OK



async def test_refresh_token_rotation(
    client: AsyncClient,
    mock_users: list,  
):
    """Тест refresh токена."""
    user_email = mock_users[0].email
    login_response = await client.post(
        "/api/v1/login", 
        data={"username": user_email, "password": "!23QWEasd"}
    )
    
    assert login_response.status_code == status.HTTP_200_OK
    login_data = login_response.json()
    
    old_access_token = login_data["access_token"]
    old_refresh_token = login_data["refresh_token"]

    refresh_response = await client.post(
        "/api/v1/refresh",
        json={"refresh_token": old_refresh_token}
    )

    assert refresh_response.status_code == status.HTTP_200_OK
    
    new_data = refresh_response.json()
    new_access_token = new_data["access_token"]
    new_refresh_token = new_data["refresh_token"]

    assert new_access_token != old_access_token
    assert new_refresh_token != old_refresh_token

    repeat_refresh_response = await client.post(
        "/api/v1/refresh",
        json={"refresh_token": old_refresh_token}
    )
    assert repeat_refresh_response.status_code == status.HTTP_401_UNAUTHORIZED

    verify_response = await client.get(
        "/api/v1/verify",
        headers={"Authorization": f"Bearer {new_access_token}"}
    )
    assert verify_response.status_code == status.HTTP_200_OK

    