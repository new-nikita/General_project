from typing import TYPE_CHECKING

from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from core.models.base import Base

if TYPE_CHECKING:
    from .user import User


class Like(Base):
    """Модель лайков пользователей."""

    ...
