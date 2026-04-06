from abc import ABC, abstractmethod
from typing import Any

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.models import User
from app.repositories import AuthRepository
from app.utils import create_access_token, decode_access_token, get_password_hash, verify_password


class AuthServiceABC(ABC):
    """Интерфейс для регистрации и аутентификации"""

    @abstractmethod
    def __init__(self, session: AsyncSession):
        """Конструктор сервиса регистрации и аутентификации"""
        pass
    
    @abstractmethod
    async def register(self, username: str, password: str, email: str) -> User:
        """Регистрация пользователя"""
        raise NotImplementedError

    @abstractmethod
    async def login(self, login: str, password: str) -> tuple[User, str]:
        """Аутентификация пользователя"""
        raise NotImplementedError
    
    @abstractmethod
    async def verify(self, token: str) -> dict[str, Any]:
        """Проверка токена"""
        raise NotImplementedError
    

class AuthService(AuthServiceABC):
    """Сервис регистрации и аутентификации"""

    def __init__(self, session: AsyncSession):
        self.repository = AuthRepository(session)

    async def register(self, username: str, password: str, email: str) -> User:
        existing_user = await self.repository.get_user_by_username_or_email(username=username, email=email)

        if existing_user:
            if existing_user.username == username:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь с таким логином уже существует")
            if existing_user.email == email:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь с таким email уже существует")
            
        hashed_password = get_password_hash(password)
        
        new_user = await self.repository.create_user(username=username, password=hashed_password, email=email)

        return new_user
    
    async def login(self, login: str, password: str) -> tuple[User, str]:
        user = await self.repository.get_user_by_login(login)

        if not user or not verify_password(password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="неверный логин или пароль")
        
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username,
            "role": user.role
        }  

        access_token = create_access_token(data=token_data)

        return user, access_token
    
    async def verify(self, token: str) -> dict[str, Any]:
        return decode_access_token(token)
       
        
def get_auth_service(
    session: AsyncSession = Depends(get_async_session),
) -> AuthService:
    return AuthService(session)