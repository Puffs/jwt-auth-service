from passlib.context import CryptContext

from app.config import app_settings

pwd_context = CryptContext(
    schemes=[app_settings.crypt_context_schema],
    deprecated=app_settings.crypt_context_deprecated
)



def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password_original: str, password_hash: str) -> bool:
    return pwd_context.verify(password_original, password_hash)