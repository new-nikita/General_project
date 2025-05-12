from typing import TYPE_CHECKING

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import EmailStr

from .base import Base
from .mixins import TimestampsMixin

if TYPE_CHECKING:
    from .profile import Profile
    from .post import Post


class User(TimestampsMixin, Base):
    """Класс пользователя, которого определяет система."""

    username: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    hashed_password: Mapped[str]
    email: Mapped[EmailStr] = mapped_column(String(100), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    posts: Mapped[list["Post"]] = relationship(
        "Post",
        back_populates="author",
    )
    profile: Mapped["Profile"] = relationship(
        back_populates="user",
        lazy="selectin",
    )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, username={self.username!r})"

    def __repr__(self) -> str:
        return str(self)
