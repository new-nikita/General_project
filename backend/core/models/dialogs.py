from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import ForeignKey, BigInteger, Index, CheckConstraint, Identity
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import Base
from .mixins import TimestampsMixin, DialogUsersMixin

if TYPE_CHECKING:
    from .messages import Message


class Dialog(DialogUsersMixin, TimestampsMixin, Base):
    __tablename__ = "dialogs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    title: Mapped[str | None]
    is_group: Mapped[bool] = mapped_column(
        default=False,
        server_default="false",
        index=True,
    )

    # last_message_id: Mapped[int] = mapped_column(BigInteger, nullable=True)

    last_message_id: Mapped[int | None] = mapped_column(
        ForeignKey("messages.id", ondelete="SET NULL"),
        nullable=True,
    )

    participants: Mapped[list["DialogParticipant"]] = relationship(
        back_populates="dialog",
        cascade="all, delete-orphan",
    )

    # --- relationships ---

    messages: Mapped[list["Message"]] = relationship(
        back_populates="dialog",
        cascade="all, delete-orphan",
        order_by="desc(Message.id)",
        foreign_keys="Message.dialog_id",
    )

    last_message: Mapped["Message"] = relationship(
        foreign_keys=[last_message_id],
        post_update=True,  # важно для циклической связи
    )

    __table_args__ = (
        # нельзя создать диалог с самим собой
        CheckConstraint(
            "user1_id != user2_id",
            name="ck_dialog_no_self",
        ),
        # фиксируем порядок пользователей
        CheckConstraint(
            "user1_id < user2_id",
            name="ck_dialog_user_order",
        ),
        # уникальность пары
        Index(
            "idx_dialog_users_unique",
            "user1_id",
            "user2_id",
            unique=True,
        ),
    )

    def __repr__(self):
        return (
            f"Dialog(id={self.id}, "
            f"user1={self.user1_id}, "
            f"user2={self.user2_id})"
        )


# в коде важно делать
# user1_id, user2_id = sorted([user_a_id, user_b_id])
# ИНАЧЕ СЛОВИШЬ IntegrityError


class DialogParticipant(Base):
    __tablename__ = "dialog_participants"

    id = None

    dialog_id: Mapped[int] = mapped_column(
        ForeignKey("dialogs.id", ondelete="CASCADE"),
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    joined_at: Mapped[datetime]

    last_read_message_id: Mapped[int | None] = mapped_column(
        index=True,
    )

    unread_count: Mapped[int] = mapped_column(
        default=0,
    )

    dialog: Mapped["Dialog"] = relationship(
        back_populates="participants",
    )

    user: Mapped["User"] = relationship(lazy="selectin")
