from uuid import uuid4
from datetime import datetime
from typing import List, TYPE_CHECKING
import enum

from sqlalchemy import func, text, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum as sqlalchemy_Enum

from .base import Base


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"

class User(Base):
    """Модель пользователя."""

    __tablename__ = 'user'

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text('gen_random_uuid()'),
    )
    username: Mapped[str] = mapped_column(String, doc='Логин', unique=True)
    password: Mapped[str] = mapped_column(String, doc='Пароль')
    email: Mapped[str] = mapped_column(String, doc='Email', unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text('true'))
    role: Mapped[str] = mapped_column(sqlalchemy_Enum(UserRole), default=UserRole.USER, server_default=text("'USER'"))
    created_at: Mapped[datetime] = mapped_column(DateTime, doc='Время регистрации', server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())