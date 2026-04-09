from abc import ABC, abstractmethod
from typing import Any
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.models import User
from app.repositories import AuthRepository, RefreshTokenRepository, AuthRepositoryABC, RefreshTokenRepositoryABC
from app.utils import create_access_token, decode_token, get_password_hash, verify_password, create_refresh_token
from app.config import app_settings

class AuthServiceABC(ABC):
    """Интерфейс для регистрации и аутентификации"""

    @abstractmethod
    async def register(self, username: str, password: str, email: str) -> User:
        """Регистрация пользователя"""
        raise NotImplementedError

    @abstractmethod
    async def login(self, login: str, password: str) -> tuple[User, str, str]:
        """Аутентификация пользователя"""
        raise NotImplementedError
    
    @abstractmethod
    async def verify(self, token: str) -> dict[str, Any]:
        """Проверка токена"""
        raise NotImplementedError


class AuthService(AuthServiceABC):
    """Сервис регистрации и аутентификации"""

    def __init__(self, auth_repository: AuthRepositoryABC, refresh_repository: RefreshTokenRepositoryABC):
        self.auth_repository = auth_repository
        self.refresh_repository = refresh_repository

    async def register(self, username: str, password: str, email: str) -> User:
        existing_user = await self.auth_repository.get_user_by_username_or_email(username=username, email=email)

        if existing_user:
            if existing_user.username == username:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь с таким логином уже существует")
            if existing_user.email == email:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь с таким email уже существует")
            
        hashed_password = get_password_hash(password)
        
        new_user = await self.auth_repository.create_user(username=username, password=hashed_password, email=email)

        return new_user
    
    async def login(self, login: str, password: str) -> tuple[User, str, str]:
        user = await self.auth_repository.get_user_by_login(login)

        if not user or not verify_password(password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="неверный логин или пароль")
        
        jwt_token_data = {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username,
            "role": user.role
        }  

        access_token = create_access_token(data=jwt_token_data)

        refresh_token_data = {
            "sub": str(user.id),
        }  
        refresh_token = create_refresh_token(data=refresh_token_data)

        expires_at = datetime.now(timezone.utc) + timedelta(days=app_settings.refresh_token_expire_days)
        await self.refresh_repository.create_refresh_token(user_id=user.id, token=refresh_token, expires_at=expires_at)

        return user, access_token, refresh_token
    
    async def verify(self, token: str) -> dict[str, Any]:
        return decode_token(token)
       

def get_auth_service(
    session: AsyncSession = Depends(get_async_session),
) -> AuthServiceABC:
    auth_repository = AuthRepository(session)
    refresh_repository = RefreshTokenRepository(session)

    return AuthService(auth_repository, refresh_repository)