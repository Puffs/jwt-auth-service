from abc import ABC, abstractmethod

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


class AuthRepositoryABC(ABC):
    """Интерфейс репозитория для работы с пользователями."""

    @abstractmethod
    async def create_user(self, **user_data) -> User:
        """Создание пользователя."""
        raise NotImplementedError
    
    @abstractmethod
    async def get_user_by_login(self, login: str) -> User | None:
        """Возвращает пользователя по переданному логину"""
        raise NotImplementedError
    
    @abstractmethod
    async def get_user_by_username_or_email(self, username: str, email: str) -> User | None:
        """Возвращает пользователя по username и email"""
        raise NotImplementedError
    
    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> User | None:
        """Получает пользователя по id"""
        raise NotImplementedError

class AuthRepository(AuthRepositoryABC):
    """Репозиторий для работы с пользователями."""

    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def create_user(self, **user_data) -> User:
        new_user = User(**user_data)
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)

        return new_user
    
    async def get_user_by_username_or_email(self, username: str, email: str) -> User | None:
        query = select(User).where(or_(User.username==username, User.email==email))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_by_login(self, login: str) -> User | None:
        query = select(User).where(or_(User.username == login, User.email == login))
        result = await self.session.execute(query)
        current_user = result.scalar_one_or_none()

        return current_user
    
    async def get_user_by_id(self, user_id: str) -> User | None:
        query = select(User).where(User.id==user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()