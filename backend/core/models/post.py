from sqlalchemy import Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base import Base
from .user import User
from .mixins import TimestampsMixin


class Post(TimestampsMixin, Base):
    """
    Модель для поста.
    """

    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    author: Mapped["User"] = relationship(
        "User", back_populates="posts", lazy="selectin"
    )
    image: Mapped[str | None] = mapped_column(Text, server_default=None)
