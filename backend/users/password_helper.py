import re
import logging
from typing import Union, ClassVar

from passlib.context import CryptContext


logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class ErrorMessages:
    EMPTY_PASSWORD = "Пароль не может быть пустым"
    PASSWORD_TOO_LONG = "Пароль слишком длинный (максимум {max_length} символов)"
    PASSWORD_TOO_SHORT = "Пароль слишком короткий (минимум {min_length} символов)"
    INVALID_CREDENTIALS = "Неверные учетные данные"
    PASSWORD_TYPE_ERROR = "Пароль должен быть строкой или bytes"
    HASH_TYPE_ERROR = "Хэш должен быть строкой или bytes"
    WEAK_PASSWORD = (
        "Пароль должен содержать:\n"
        "- Минимум 8 символов\n"
        "- Заглавные и строчные буквы\n"
        "- Цифры\n"
        "- Специальные символы"
    )


class PasswordVerificationError(Exception):
    """Ошибка проверки пароля."""

    def __init__(
        self, message: str = ErrorMessages.INVALID_CREDENTIALS, status_code: int = 400
    ):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class PasswordHelper:
    """Класс для безопасной работы с паролями."""

    # Конфигурация
    MAX_PASSWORD_LENGTH: int = 72  # Ограничение bcrypt
    PWD_CONTEXT: ClassVar[CryptContext] = CryptContext(
        schemes=["bcrypt"], deprecated="auto"
    )
    MIN_PASSWORD_LENGTH: int = 8

    # Регулярные выражения для валидации пароля
    PASSWORD_PATTERN: ClassVar[re.Pattern] = re.compile(
        r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    )

    @classmethod
    def validate_password(cls, password: str) -> None:
        """Проверяет сложность пароля."""
        if not password:
            raise ValueError(ErrorMessages.EMPTY_PASSWORD)

        if len(password) > cls.MAX_PASSWORD_LENGTH:
            raise ValueError(
                ErrorMessages.PASSWORD_TOO_LONG.format(
                    max_length=cls.MAX_PASSWORD_LENGTH
                )
            )
        if len(password) < cls.MIN_PASSWORD_LENGTH:
            raise ValueError(
                ErrorMessages.PASSWORD_TOO_SHORT.format(
                    min_length=cls.MIN_PASSWORD_LENGTH
                )
            )

        if not cls.PASSWORD_PATTERN.fullmatch(password):
            raise ValueError(ErrorMessages.WEAK_PASSWORD)

    @classmethod
    def generate_password(cls, password: str) -> str:
        """
        Генерирует хеш пароля.

        :param password: Пароль для хеширования
        :return: Хэшированный пароль
        :raise ValueError: Если пароль не соответствует требованиям
        """
        cls.validate_password(password)
        return cls.PWD_CONTEXT.hash(password)

    @classmethod
    def verify_password(
        cls,
        plain_password: Union[str, bytes],
        hashed_password: Union[str, bytes],
    ) -> bool:
        """
        Безопасно проверяет пароль с защитой от timing-атак.

        :param plain_password: Введенный пароль
        :param hashed_password: Хэш для проверки
        :return bool: True если пароль верный
        """
        return cls.PWD_CONTEXT.verify(plain_password, hashed_password)
