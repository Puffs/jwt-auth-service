import jwt
from typing import Any
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status

from app.config import app_settings


def create_access_token(data: dict[str, Any]) -> str:
    """Создает JWT токен."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=app_settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, app_settings.secret_key, algorithm=app_settings.algorithm)

    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any]:
    """Декодирует токен."""
    try:
        return jwt.decode(token, app_settings.secret_key, algorithms=[app_settings.algorithm])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Срок действия токена истек"
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен"
        )