from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.config import db_settings


dsn = (
    f'postgresql+asyncpg://'
    f'{db_settings.user}:{db_settings.password}@{db_settings.host}:{db_settings.port}/{db_settings.db}'
)
engine = create_async_engine(dsn, future=True, echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session