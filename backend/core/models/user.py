from typing import TYPE_CHECKING
from passlib.context import CryptContext

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .profile import Profile

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    """Класс пользователя, которого определяет система."""

    username: Mapped[str] = mapped_column(String(40), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    profile: Mapped["Profile"] = relationship(back_populates="user")

    def __init__(self, password: str, **kwargs):
        """Автоматически хеширует пароль при создании."""
        super().__init__(**kwargs)
        self._set_password(password)

    def _set_password(self, password: str):
        """Хеширует и устанавливает пароль."""
        self.hashed_password = self._generate_password(password)

    @staticmethod
    def _generate_password(password: str) -> str:
        """Генерирует хеш пароля."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Проверяет, соответствует ли введенный пароль хэшированному."""
        return pwd_context.verify(plain_password, hashed_password)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, username={self.username!r})"

    def __repr__(self) -> str:
        return str(self)
