import logging

from passlib.context import CryptContext
from passlib.exc import UnknownHashError

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordVerificationError(Exception):
    pass


class PasswordHelper:
    """Класс для работы с паролями."""

    @staticmethod
    def generate_password(password: str) -> str:
        """Генерирует хеш пароля."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Проверяет, соответствует ли введенный пароль хэшированному."""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except (ValueError, TypeError, UnknownHashError) as e:
            logger.error(f"Password verification failed: {str(e)}")
            raise PasswordVerificationError from e
