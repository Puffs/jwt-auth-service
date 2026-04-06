from typing import Union, Optional
from uuid import UUID

from fastapi import status, HTTPException
from pydantic import BaseModel, field_validator, EmailStr, Field
from password_validator import PasswordValidator

from .user_schemas import UserSchema


class RegistrationInputSchema(BaseModel):
    """Схема входных данных для регистрации."""
    username: str
    password: str
    email: EmailStr

    @field_validator('password')
    def validate_password(cls, password: str) -> Union[str, HTTPException]:
        password_validator = PasswordValidator()
        password_validator.min(8).max(20).has().uppercase().has().lowercase().has().digits().has().symbols()
        # password_validator.min(8).max(20)

        if password_validator.validate(password):
            return password
        
        raise ValueError("Пароль недостаточно надежен")


class RegistrationOutputSchema(UserSchema):
    """Схема выходных данных для регистрации."""
    pass


class LoginOutputSchema(UserSchema):
    """Схема выходных данных после регистрации"""
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None


class VerifyOutputSchema(UserSchema):
    """Схема выходных данных для подтверждения токена"""
    id: UUID = Field(validation_alias="sub")

