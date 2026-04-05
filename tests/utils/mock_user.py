import pytest_asyncio

from sqlalchemy import delete

from app.models import User
from app.utils import get_password_hash

@pytest_asyncio.fixture(scope='function')
async def mock_users(db_session):
    """Фикстура для создания пользователя."""
    await db_session.execute(delete(User))
    await db_session.commit()

    users = [
        User(username="pufff2", password=get_password_hash("!23QWEasd"), email="pufff2@mail.ru"),
        User(username="pufff3", password=get_password_hash("!23QWEasd"), email="pufff3@mail.ru"),
    ]
    db_session.add_all(users)
    await db_session.commit()
    
    for user in users:
        await db_session.refresh(user)
    
    yield users
    
    await db_session.execute(delete(User))
    await db_session.commit()


@pytest_asyncio.fixture(scope='function')
async def auth_client(client, mock_users):
    """Просто возвращает строку с токеном после логина."""
    login_data = {"login": "pufff2@mail.ru", "password": "!23QWEasd"}
    response = await client.post("/api/v1/login", json=login_data)
    
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    
    yield client
    
    client.headers.pop("Authorization", None)
    