from typing import TYPE_CHECKING

from sqlalchemy import String, Boolean, CheckConstraint
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from pydantic import EmailStr

from .base import Base
from .mixins import TimestampsMixin

if TYPE_CHECKING:
    from .profile import Profile
    from .post import Post
    from .like import LikePost
    from .comment import Comment
    from .friends import Friendship
    from .followers import Follower


class User(TimestampsMixin, Base):
    """Класс пользователя, которого определяет система."""

    __table_args__ = (
        CheckConstraint(
            "username != ''",
            name="check_username_not_empty",
        ),
        CheckConstraint(
            "hashed_password != ''",
            name="check_password_not_empty",
        ),
        CheckConstraint("email != ''", name="check_email_not_empty"),
    )

    username: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    hashed_password: Mapped[str]
    email: Mapped[EmailStr] = mapped_column(String(100), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    posts: Mapped[list["Post"]] = relationship(
        "Post",
        back_populates="author",
    )
    profile: Mapped["Profile"] = relationship(
        back_populates="user",
        lazy="selectin",
    )
    likes: Mapped[list["LikePost"]] = relationship(
        "LikePost",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    comments: Mapped[list["Comment"] | None] = relationship(
        "Comment",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    # Кого я добавил в друзья
    initiated_friendships: Mapped[list["Friendship"]] = relationship(
        "Friendship",
        foreign_keys="Friendship.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    # Кто добавил меня в друзья
    received_friendships: Mapped[list["Friendship"]] = relationship(
        "Friendship",
        foreign_keys="Friendship.friend_id",
        back_populates="friend",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # На кого я подписался
    followings: Mapped[list["Follower"]] = relationship(
        "Follower",
        foreign_keys="Follower.follower_id",
        back_populates="follower",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    # Кто подписался на меня
    followers: Mapped[list["Follower"]] = relationship(
        "Follower",
        foreign_keys="Follower.following_id",
        back_populates="following",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Прокси: список друзей (User), а не объектов Friend
    my_friends: AssociationProxy[list["User"]] = association_proxy(
        "initiated_friendships",
        "friend",
    )
    my_followers: AssociationProxy[list["User"]] = association_proxy(
        "followers",
        "following",
    )
    followed: AssociationProxy[list["User"]] = association_proxy(
        "followings",
        "follower",
    )

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, username={self.username!r})"

    def __repr__(self) -> str:
        return str(self)
