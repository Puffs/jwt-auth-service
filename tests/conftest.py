import asyncpg
import pytest_asyncio
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.config import db_settings, app_settings

from app.models import Base
from app.main import app
from app.db.database import get_async_session



TEST_DB_URL = (
    f'postgresql+asyncpg://{db_settings.user}'
    f':{db_settings.password}@{db_settings.host}:{db_settings.port}/{db_settings.test_db}'
)

engine = create_async_engine(TEST_DB_URL, future=True, echo=True, poolclass=NullPool)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)



@pytest_asyncio.fixture(scope='session')
async def setup_db():
    """Фикстура для создания БД и удаления ее после завершения тестов."""
    conn = None
    try:
        conn = await asyncpg.connect(
            user=db_settings.user,
            password=db_settings.password,
            host=db_settings.host,
            port=db_settings.port,
            database=db_settings.db
        )
        await conn.execute(f'CREATE DATABASE {db_settings.test_db}')
        await conn.close()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        yield engine

        conn = await asyncpg.connect(
            user=db_settings.user,
            password=db_settings.password,
            host=db_settings.host,
            port=db_settings.port,
            database=db_settings.db
        )
        await conn.execute(f'DROP DATABASE {db_settings.test_db}')
        await conn.close()
    except Exception:
        if conn:
            await conn.execute(f'DROP DATABASE {db_settings.test_db}')
            await conn.close()



@pytest_asyncio.fixture(scope='function')
async def db_session():
    """Фикстура для сессии."""
    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture(scope='function')
async def client(setup_db, db_session):
    """Фикстура для асинхронного HTTP клиента."""
    async def override_get_async_session():
        yield db_session

    app.dependency_overrides[get_async_session] = override_get_async_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url=app_settings.test_base_url) as client:
        yield client
    app.dependency_overrides.clear()