from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Enum

from backend.core.enums.follow_status import FollowStatus

from .base import Base
from .mixins import TimestampsMixin


if TYPE_CHECKING:
    from .user import User


class Follower(Base, TimestampsMixin):
    """Модель подписки на другого пользователя."""

    __table_args__ = (
        UniqueConstraint("follower_id", "following_id", name="follower_relation"),
        CheckConstraint("follower_id != following_id", name="check_follower"),
    )

    follower_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        primary_key=True,
        comment="Пользователь, который подписывается",
    )
    following_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        primary_key=True,
        comment="Пользователь, на которого подписаны",
    )

    status: Mapped[Enum] = mapped_column(
        Enum(FollowStatus),
        default=FollowStatus.PENDING,
        nullable=False,
        comment="Статус подписки",
    )

    # Кто подписался
    follower: Mapped["User"] = relationship(
        "User",
        foreign_keys=[follower_id],
        back_populates="followings",
    )

    # На кого подписан
    following: Mapped["User"] = relationship(
        "User",
        foreign_keys=[following_id],
        back_populates="followers",
    )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.follower_id} -> {self.following_id}"

    def __repr__(self) -> str:
        return str(self)
