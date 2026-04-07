from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.models import User
from app.repositories import AuthRepository, RefreshTokenRepository
from app.utils import create_access_token, decode_token, create_refresh_token
from app.config import app_settings


class RefreshTokenServiceABC(ABC):
    """Интерфейс для работы с refresh токеном"""

    @abstractmethod
    def __init__(self, session: AsyncSession):
        pass
    
    @abstractmethod
    async def refresh(self, refresh_token: str) -> tuple[User, str, str]:
        """Обновление токена"""
        raise NotImplementedError


class RefreshTokenService(RefreshTokenServiceABC):
    """Сервис для работы с refresh токеном"""

    def __init__(self, session: AsyncSession):
        self.auth_repository = AuthRepository(session)
        self.refresh_repository = RefreshTokenRepository(session)

    async def refresh(self, refresh_token: str) -> tuple[User, str, str]:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный тип токена")

        refresh_token_db = await self.refresh_repository.get_refresh_token(refresh_token)
        if not refresh_token_db:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Сессия не найдена или уже использована")

        user = await self.auth_repository.get_user_by_id(payload.get("sub"))
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")

        await self.refresh_repository.delete_refresh_token(refresh_token)

        new_access = create_access_token(data={
            "sub": str(user.id), 
            "email": user.email,
            "username": user.username, 
            "role": user.role
        })
        new_refresh = create_refresh_token(data={"sub": str(user.id)})

        expires_at = datetime.now(timezone.utc) + timedelta(days=app_settings.refresh_token_expire_days)
        await self.refresh_repository.create_refresh_token(
            user_id=user.id, 
            token=new_refresh, 
            expires_at=expires_at
        )
        return user, new_access, new_refresh



def get_refresh_token_service(
    session: AsyncSession = Depends(get_async_session),
) -> RefreshTokenService:
    return RefreshTokenService(session)