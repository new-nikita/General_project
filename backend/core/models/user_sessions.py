from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    String,
    Boolean,
    ForeignKey,
    Text,
    DateTime,
    func,
    text,
    CheckConstraint,
    Index,
)
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.types import Enum
from sqlalchemy.dialects.postgresql import INET
from pydantic import EmailStr

from .base import Base
from .mixins import CreatedAtMixin

from backend.core.enums.client_platform import ClientPlatform

if TYPE_CHECKING:
    from .profile import Profile
    from .post import Post
    from .like import LikePost
    from .comment import Comment
    from .friends import Friendship
    from .followers import Follower


class UserSession(Base, CreatedAtMixin):
    """
    Активная авторизация пользователя на одном устройстве.
    Одна строка = один refresh JWT (claim jti).
    revoked_at IS NULL → сессия активна.
    """

    __tablename__ = "user_sessions"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        comment="Владелец сессии",
    )
    device_id: Mapped[str] = mapped_column(
        String(128),
        comment="Стабильный id клиента (UUID с устройства)",
    )
    refresh_jti: Mapped[str] = mapped_column(
        String(36), unique=True, index=True, comment="Claim jti из refresh JWT"
    )
    device_name: Mapped[str | None] = mapped_column(
        String(255),
        comment="Человекочитаемое имя: : Pixel 7, Chrome",
    )
    platform: Mapped[str | None] = mapped_column(
        Enum(ClientPlatform),
        comment="ios / android / web",
    )
    ip_address: Mapped[str | None] = mapped_column(
        INET,
        comment="IP адрес при login",
    )
    user_agent: Mapped[str | None] = mapped_column(
        Text,
        comment="User-Agent при login",
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Последняя активность (login / refresh)",
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="NULL = активна; NOT NULL = logout / evict",
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Срок жизни refresh (login + N дней)",
    )

    __table_args__ = (
        CheckConstraint(
            "device_id != ''",
            name="check_device_id_not_empty",
        ),
        CheckConstraint(
            "refresh_jti != ''",
            name="check_refresh_jti_not_empty",
        ),
        Index(
            "ix_user_sessions_user_active",
            "user_id",
            last_seen_at.desc(),
            postgresql_where=text("revoked_at IS NULL"),
        ),
        Index(
            "uq_user_sessions_user_device_active",
            "user_id",
            "device_id",
            unique=True,
            postgresql_where=text("revoked_at IS NULL"),
        ),
    )

    @property
    def is_active(self) -> bool:
        return self.revoked_at is None

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return self.expires_at <= datetime.now(tz=self.expires_at.tzinfo)

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(id={self.id}, user_id={self.user_id}, device_id={self.device_id!r})"
        )

    def __repr__(self) -> str:
        return str(self)
