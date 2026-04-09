from abc import ABC, abstractmethod
from datetime import datetime

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import RefreshToken



class RefreshTokenRepositoryABC(ABC):
    """Интерфейс репозитория для работы с рефреш токеном."""

    @abstractmethod
    async def get_refresh_token(self, token: str) -> RefreshToken | None:
        """Получает refresh токен"""
        raise NotImplementedError

    @abstractmethod
    async def create_refresh_token(self, user_id: str, token: str, expires_at: datetime) -> None:
        """Сохраняет refresh токен"""
        raise NotImplementedError
    
    @abstractmethod
    async def delete_refresh_token(self, refresh_token: str) -> None:
        """Удаляет рефреш токен."""
        raise NotImplementedError


class RefreshTokenRepository(RefreshTokenRepositoryABC):
    """Репозиторий для работы с рефреш токеном."""

    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session
        
    async def get_refresh_token(self, token: str) -> RefreshToken | None:
        query = select(RefreshToken).where(RefreshToken.token == token)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_refresh_token(self, user_id: str, token: str, expires_at: datetime) -> None:
        new_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        self.session.add(new_token)
        await self.session.commit()

    async def delete_refresh_token(self, refresh_token: str) -> None:   
        query = delete(RefreshToken).where(RefreshToken.token == refresh_token)
        await self.session.execute(query)
        await self.session.commit()