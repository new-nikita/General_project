from sqlalchemy import ForeignKey, Integer, String, Column
from sqlalchemy.orm import backref, relationship, Mapped, mapped_column

from .base import Base
from backend.core.models.user import User


class Friendship(Base):
    """Класс связка"""

    __tablename__ = "friendship"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        primary_key=True,
    )
    friend_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        primary_key=True,
    )
    # Статус дружбы
    status: Mapped[str] = mapped_column(
        String(20),
        default="Pending",
    )

    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="friendships",
    )
    friend: Mapped["User"] = relationship(
        "User",
        foreign_keys=[friend_id],
    )
