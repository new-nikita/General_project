from typing import Any

from pydantic import EmailStr
from sqlalchemy import select, or_
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from backend.core.base_repository import BaseRepository
from backend.core.models import Friendship, LikePost, Post, Profile, User
from backend.users.password_helper import PasswordHelper
from backend.users.schemas.profile_schemas import ProfileUpdate
from backend.users.schemas.users_schemas import UserCreate
from backend.core.enums.follow_status import FollowStatus


class UserRepository(BaseRepository[User]):
    """Репозиторий для работы с пользователями.

    Содержит методы для взаимодействия с базой данных.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория с сессией базы данных.

        :param session: Асинхронная сессия SQLAlchemy.
        """
        super().__init__(session=session, model=User)

    async def get_by_id_with_likes(self, id_: int) -> User:
        """Получает пользователя по ID вместе с его лайками."""
        stmt = (
            select(self.model)
            .options(selectinload(self.model.likes))
            .where(self.model.id == id_)
        )

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_profile_user_by_id(self, id_: int) -> User:
        """Пользователь для профиля: лайки с постами, друзья с данными."""
        stmt = (
            select(self.model)
            .options(
                selectinload(User.profile),
                selectinload(User.likes)
                .selectinload(LikePost.post)
                .selectinload(Post.likes),
                selectinload(User.initiated_friendships)
                .selectinload(Friendship.friend)
                .selectinload(User.profile),
                selectinload(User.received_friendships)
                .selectinload(Friendship.user)
                .selectinload(User.profile),
            )
            .where(self.model.id == id_)
        )

        try:
            result = await self.session.execute(stmt)
            return result.scalar_one()
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Объект {self.model.__name__} с ID {id_} не найден",
            )

    async def create(self, dto_user: UserCreate) -> User:
        """Создает нового пользователя в базе данных.

        :param dto_user: DTO с данными для создания пользователя.
        :return: Созданный объект пользователя.
        :raises IntegrityError: Если пользователь с таким email или
            username уже существует.
        """
        hashed_password = PasswordHelper.generate_password(dto_user.password)
        user = User(
            username=dto_user.username,
            email=dto_user.email,
            hashed_password=hashed_password,
        )
        if dto_user.profile:
            profile = Profile(**dto_user.profile.model_dump())
            user.profile = profile

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Возвращает пользователя по его id пользователя (user_id).

        :param user_id: ID пользователя.
        :return: Объект пользователя или None, если пользователь не найден.
        """
        result = await self.session.execute(
            select(self.model)
            .options(
                selectinload(User.profile),
                selectinload(User.likes),
            )
            .where(self.model.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """Возвращает пользователя по его имени пользователя (username).

        :param username: Имя пользователя.
        :return: Объект пользователя или None, если пользователь не
            найден.
        """
        result = await self.session.execute(
            select(self.model)
            .options(
                selectinload(User.profile),
                selectinload(User.likes),
            )
            .where(self.model.username == username)
        )
        return result.scalar_one_or_none()

    async def search_users_by_username(
        self,
        username: str,
        your_id: int,
    ) -> list[User] | None:
        """Возвращает список пользователей по имени пользователя (username).

        :param username: Имя пользователя.
        :param your_id: Id пользователя.
        :return: Список объектов пользователей или None, если пользователи не
            найдены.
        """
        result = await self.session.execute(
            select(self.model)
            .options(selectinload(User.likes))
            .where(
                self.model.username.ilike(f"%{username}%"),
                self.model.id != your_id,
            )
            # частичное, регистронезависимое совпадение
        )
        return result.scalars().all()  # возвращаем список пользователей

    async def get_all_users(self, current_user_id: int) -> list[dict]:
        """
        Возвращает всех пользователей кроме текущего с флагами дружбы:
        - is_friend: True, если уже друзья
        - friend_request_sent: True, если текущий пользователь отправил заявку
        """

        stmt = (
            select(User, Friendship.status, Friendship.user_id.label("initiator_id"))
            .outerjoin(
                Friendship,
                or_(
                    # текущий пользователь инициатор
                    (Friendship.user_id == current_user_id)
                    & (Friendship.friend_id == User.id),
                    # другой пользователь инициатор
                    (Friendship.friend_id == current_user_id)
                    & (Friendship.user_id == User.id),
                ),
            )
            .where(User.id != current_user_id)
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        # Формируем список пользователей с нужными флагами
        users = []
        for user, status, initiator_id in rows:
            users.append(
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "is_active": user.is_active,
                    "is_friend": status == FollowStatus.ACCEPTED,
                    "friend_request_sent": status == FollowStatus.PENDING
                    and initiator_id == current_user_id,
                }
            )

        return users

    async def get_user_by_email(self, email: EmailStr) -> User | None:
        """Возвращает пользователя по его email.

        :param email: Email пользователя.
        :return: Объект пользователя или None, если пользователь не
            найден.
        """
        result = await self.session.execute(
            select(self.model).where(self.model.email == email)
        )
        return result.scalar_one_or_none()

    async def change_password_by_user(
        self, user: User, new_password: str
    ) -> User | None:
        """Обновляет пароль пользователя.

        :param user: Объект пользователя.
        :param new_password: Новый пароль от пользователя
        :return: Объект пользователя или None, если пользователь не
            найден.
        """
        hashed_password = PasswordHelper.generate_password(new_password)
        user.hashed_password = hashed_password
        await self.session.commit()

    async def update(self, id_: int, data: dict[str, Any]) -> str | None: ...

    async def update_profile(
        self,
        user: User,
        dto_profile: ProfileUpdate,
    ) -> None:
        """Обновляет профиль пользователя.

        Если профиля нет — создаёт его. Если есть — обновляет только
        указанные поля.
        :param user: Пользователь, чей профиль нужно обновить.
        :param dto_profile: Данные для обновления профиля.
        """
        if not user.profile:
            # Профиля нет — создаём новый и привязываем к пользователю
            profile_data = dto_profile.model_dump(exclude_unset=True)
            user.profile = Profile(user_id=user.id, **profile_data)
        else:
            # Профиль существует — обновляем только переданные поля
            profile_data = dto_profile.model_dump(exclude_unset=True)
            for key, value in profile_data.items():
                setattr(user.profile, key, value)

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

    async def delete(self, id_: int) -> str | None: ...

    async def update_user_avatar(self, user: User, avatar_url: str):
        """Обновляет аватар пользователя.

        :param user: Пользователь.
        :param avatar_url: URL аватара.
        """
        user.profile.avatar = avatar_url
        await self.session.commit()

    async def delete_user_avatar(
        self,
        user: User,
        default_avatar: str = "/client_files/avatars/дефолтный_аватар.jpg",
    ) -> str | None:
        """Удаляет аватар пользователя.

        :param user: Пользователь.
        :param default_avatar: URL дефолтного аватара.
        """
        if not user.profile.avatar or not user:
            return

        user.profile.avatar = default_avatar
        await self.session.commit()
        return default_avatar
