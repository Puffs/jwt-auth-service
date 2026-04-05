from abc import ABC, abstractmethod

from typing import Union

from sqlalchemy import select, or_, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models import User
from app.utils import get_password_hash, verify_password


class AuthRepositoryABC(ABC):
    """Интерфейс для регистрации и аутентификации."""

    @abstractmethod
    def __init__(self, session: AsyncSession):
        """Конструктор репозитория ссылки."""
        raise NotImplementedError

    @abstractmethod
    async def register(self, user_data: dict) -> User:
        """Регистрация пользователя."""
        raise NotImplementedError
    
    @abstractmethod
    async def login(self, user_data: dict) -> User:
        """Аутентификация пользователя."""
        raise NotImplementedError


class AuthRepository(AuthRepositoryABC):
    """Репозиторий регистрации и аутентификации."""

    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def register(self, user_data: dict) -> User:
        """Регистрация пользователя."""

        username, email, password = user_data.get('username'), user_data.get('email'), user_data.get('password')
        await self._check_existing_user(username, email)

        user_data['password'] = get_password_hash(password)

        new_user = User(**user_data)
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)

        return new_user
    
    async def _check_existing_user(self, username: str, email: str) -> Union[HTTPException, None]:
        """Проверка существования пользователя."""

        query = select(User).where(
            User.username == username
            or User.email == email
        )
        result = await self.session.execute(query)
        existing_user = result.scalar_one_or_none()
        if existing_user:
            if existing_user.username == username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Пользователь с таким логином уже существует'
                )
            if existing_user.email == email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Пользователь с таким email уже существует'
                )

    async def login(self, user_data: dict) -> User:
        """Аутентификация пользователя."""

        http_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неправильный логин или пароль")
        login, password = user_data.get('login'), user_data.get('password')
        query = select(User).where(
            or_(User.username==login, User.email==login)
        )
        result = await self.session.execute(query)
        current_user = result.scalar_one_or_none()
        if not current_user:
            raise http_exception
        
        is_password_correct = verify_password(password, current_user.password)
        if not is_password_correct:
            raise http_exception
        return current_user
