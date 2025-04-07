from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base import Base
from .tag import Tag
from .user import User

# Ассоциативная таблица для связи многие ко многим между Post и Tag
post_tags = Table(
    'post_tags',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

class Post(Base):
    """
    Модель для поста.
    """
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)

    author: Mapped["User"] = relationship("User", back_populates="posts")
    tags: Mapped[list["Tag"]] = relationship("Tag", secondary=post_tags, back_populates="posts")
