from typing import TYPE_CHECKING

from sqlalchemy import Text, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .mixins import TimestampsMixin

if TYPE_CHECKING:
    from .user import User
    from .post import Post


class Comment(TimestampsMixin, Base):
    """
    Модель комментария пользователя к посту.

    Атрибуты:
    - user_id: ID автора комментария
    - post_id: ID поста, к которому относится комментарий
    - text: текст самого комментария
    """

    __table_args__ = (
        Index("idx_comment_user_id", "user_id"),
        Index("idx_comment_post_id", "post_id"),
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    post_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="comments")
    post: Mapped["Post"] = relationship("Post", back_populates="comments")
