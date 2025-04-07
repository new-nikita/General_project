from datetime import datetime

from sqlalchemy import String, Text, Date
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import UserRelationMixin


class Profile(UserRelationMixin, Base):
    """Профиль пользователя с расширенными настройками."""

    _user_id_unique = True
    _user_back_populates = "profile"

    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(50))

    birth_date: Mapped[datetime | None] = mapped_column(Date)
    gender: Mapped[str | None]

    phone_number: Mapped[str | None] = mapped_column(String(20))
    country: Mapped[str | None] = mapped_column(String(50))
    city: Mapped[str | None] = mapped_column(String(50))
    street: Mapped[str | None] = mapped_column(String(100))

    bio: Mapped[str | None] = mapped_column(Text())
    avatar: Mapped[str] = mapped_column(Text(), server_default="фото")

    @property
    def full_name(self) -> str:
        """Возвращает полное имя пользователя."""
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return " ".join(parts)
