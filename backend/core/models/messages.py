from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import ForeignKey, Index, BigInteger, Identity
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import Base
from .mixins import TimestampsMixin, SoftDeleteMixin, EditedMixin

if TYPE_CHECKING:
    from .dialogs import Dialog


class Message(
    SoftDeleteMixin,
    EditedMixin,
    TimestampsMixin,
    Base,
):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    # dialog_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("dialogs.id"))

    dialog_id: Mapped[int] = mapped_column(
        ForeignKey("dialogs.id", ondelete="CASCADE"),
        index=True,
    )

    sender_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )

    text: Mapped[str]

    # --- relationships ---

    dialog: Mapped["Dialog"] = relationship(
        back_populates="messages",
        foreign_keys=[dialog_id],
    )

    __table_args__ = (
        Index(
            "idx_messages_dialog_id_id",
            "dialog_id",
            "id",
        ),
    )

    def __repr__(self):
        return f"Message(id={self.id}, dialog_id={self.dialog_id})"


class MessageRead(Base):
    """
    Кто прочитал сообщение
    """

    __tablename__ = "message_reads"

    id = None

    message_id: Mapped[int] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE"),
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    read_at: Mapped[datetime]
