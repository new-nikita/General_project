from passlib.context import CryptContext

pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordHelper:
    """Класс для работы с паролями."""

    @staticmethod
    def generate_password(password: str) -> str:
        """Генерирует хеш пароля."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Проверяет, соответствует ли введенный пароль хэшированному."""
        return pwd_context.verify(plain_password, hashed_password)
