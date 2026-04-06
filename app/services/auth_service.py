from abc import ABC, abstractmethod
from typing import Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.models import User
from app.repositories import AuthRepository
from app.utils import create_access_token, decode_access_token


class AuthServiceABC(ABC):
    """Интерфейс для регистрации и аутентификации"""

    @abstractmethod
    def __init__(self, session: AsyncSession):
        """Конструктор сервиса регистрации и аутентификации"""
        raise NotImplementedError
    
    @abstractmethod
    async def register(self, username: str, password: str, email: str) -> User:
        """Регистрация пользователя"""
        raise NotImplementedError

    @abstractmethod
    async def login(self, login: str, password: str) -> User:
        """Аутентификация пользователя"""
        raise NotImplementedError
    
    @abstractmethod
    async def verify(self, token: str) -> User:
        """Проверка токена"""
        raise NotImplementedError
    

class AuthService(AuthServiceABC):
    """Сервис регистрации и аутентификации"""

    def __init__(self, session: AsyncSession):
        self.repository = AuthRepository(session)

    async def register(self, username: str, password: str, email: str) -> User:
        """Регистрация пользователя"""
        new_user = await self.repository.register(username=username, password=password, email=email)
        return new_user
    
    async def login(self, login: str, password: str) -> tuple[User, str]:
        """Аутентификация пользователя"""
        user = await self.repository.login(login, password)
        token_data = {
            "sub":str(user.id),
            "email": user.email,
            "username": user.username,
            "role": user.role.value
        }  

        access_token = create_access_token(data=token_data)

        return user, access_token
    
    async def verify(self, token: str) -> dict[str, Any]:
        """Проверка токена"""
        return decode_access_token(token)
       
        
def get_auth_service(
    session: AsyncSession = Depends(get_async_session),
) -> AuthService:
    return AuthService(session)