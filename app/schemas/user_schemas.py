from uuid import UUID

from pydantic import BaseModel, EmailStr, ConfigDict, Field

from app.models import UserRole


class BaseUserSchema(BaseModel):
    """Базовая схема пользователя"""
    id: UUID
    model_config = ConfigDict(from_attributes=True)


class UserSchema(BaseUserSchema):
    """Схема пользователя."""
    username: str
    email: EmailStr
    role: UserRole = UserRole.USER
    is_active: bool = True