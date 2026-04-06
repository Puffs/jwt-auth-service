from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient
from tests.utils import mock_users, auth_client


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
    
    print(f"DEBUG RESPONSE: {response.json()}")
    assert response.status_code == status.HTTP_200_OK




    