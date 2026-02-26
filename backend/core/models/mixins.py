import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, func, ForeignKey
from sqlalchemy.orm import declared_attr, Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .user import User


class CreatedAtMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=datetime.datetime.now,
    )


class UpdatedAtMixin:
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class TimestampsMixin(CreatedAtMixin, UpdatedAtMixin):
    """
    Класс-миксин для добавления временных меток создания и обновления в классы.
    """


class UserRelationMixin:
    _user_id_nullable: bool = False
    _user_id_unique: bool = False
    _user_back_populates: str | None = None

    @declared_attr
    def user_id(cls) -> Mapped[int]:
        return mapped_column(
            ForeignKey("users.id"),
            unique=cls._user_id_unique,
            nullable=cls._user_id_nullable,
        )

    @declared_attr
    def user(cls) -> Mapped["User"]:
        return relationship(
            "User",
            back_populates=cls._user_back_populates,
        )


class DialogUsersMixin:
    @declared_attr
    def user1_id(cls) -> Mapped[int]:
        return mapped_column(
            ForeignKey("users.id", ondelete="CASCADE"),
            index=True,
        )

    @declared_attr
    def user2_id(cls) -> Mapped[int]:
        return mapped_column(
            ForeignKey("users.id", ondelete="CASCADE"),
            index=True,
        )

    @declared_attr
    def user1(cls) -> Mapped["User"]:
        return relationship(
            "User",
            foreign_keys=[cls.user1_id],
            lazy="selectin",
        )

    @declared_attr
    def user2(cls) -> Mapped["User"]:
        return relationship(
            "User",
            foreign_keys=[cls.user2_id],
            lazy="selectin",
        )


class SenderUsersMixin:
    _sender_nullable: bool = False

    @declared_attr
    def sender_id(cls) -> Mapped[int]:
        return mapped_column(
            ForeignKey("users.id", ondelete="CASCADE"),
            index=True,
            nullable=cls._sender_nullable,
        )

    @declared_attr
    def sender(cls) -> Mapped["User"]:
        return relationship(
            "User",
            lazy="selectin",
        )


class EditedMixin:
    """
    Показывает были ли редактирования сообщений

    :param edited_at: когда изменили
    :param is_edited: bool
    """

    edited_at: Mapped[datetime.datetime | None] = mapped_column(
        nullable=True,
        index=True,
    )

    is_edited: Mapped[bool] = mapped_column(
        default=False,
        server_default="false",
    )


class SoftDeleteMixin:
    """
    Позволяет "удалять" сообщения без физического удаления

    :param deleted_at: когда удалили
    :param is_deleted: bool
    """

    deleted_at: Mapped[datetime.datetime | None] = mapped_column(
        nullable=True,
        index=True,
    )

    is_deleted: Mapped[bool] = mapped_column(
        default=False,
        server_default="false",
        index=True,
    )


class ReadOneToOneStatusMixin:
    """
    Позволяет хранить статус прочтения в диалогах one-to-one
    """

    is_read: Mapped[bool] = mapped_column(
        default=False,
        server_default="false",
        index=True,
    )

    read_at: Mapped[datetime.datetime | None] = mapped_column(
        nullable=True,
    )


class ReadManyToManyStatusMixin:
    """
    Позволяет хранить статус прочтения в диалогах many-to-many
    НАДО ДЕДЕЛАТЬ!!!
    """

    is_read: Mapped[bool] = mapped_column(
        default=False,
        server_default="false",
        index=True,
    )

    read_at: Mapped[datetime.datetime | None] = mapped_column(
        nullable=True,
    )


class DeliveredStatusMixin:
    """
    Отдельный уровень между:
        отправлено
        доставлено
        прочитано
    """

    is_delivered: Mapped[bool] = mapped_column(
        default=False,
        server_default="false",
        index=True,
    )

    delivered_at: Mapped[datetime.datetime | None] = mapped_column(
        nullable=True,
    )


class PinnedMessageMixin:
    """
    Позволяет закреплять сообщения
    """

    is_pinned: Mapped[bool] = mapped_column(
        default=False,
        server_default="false",
        index=True,
    )

    pinned_at: Mapped[datetime.datetime | None] = mapped_column(
        nullable=True,
    )


class DialogActivityMixin:
    """
    диалог сортируется по активности: Обновляется при каждом новом сообщении.
    """

    last_activity_at: Mapped[datetime] = mapped_column(index=True)
