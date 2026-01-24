from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    Column,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.orm import backref, relationship, Mapped, mapped_column

from .base import Base
from backend.core.models.user import User
from backend.core.enums.follow_status import FollowStatus


class Friendship(Base):
    """Класс связка"""

    __tablename__ = "friendship"

    id = None

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
        default=FollowStatus.PENDING.value,
    )

    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="initiated_friendships",
    )
    friend: Mapped["User"] = relationship(
        "User",
        foreign_keys=[friend_id],
        back_populates="received_friendships",
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "friend_id",
            name="uq_friendship_pair",
        ),
        CheckConstraint(
            "user_id != friend_id",
            name="check_no_self_friendship",
        ),
    )
