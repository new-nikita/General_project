from typing import Sequence, Any

from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base_repository import BaseRepository
from core.models import User, Profile, Post
from users.schemas.users_schemas import UserCreate
from .password_helper import PasswordHelper
from backend.users.schemas.profile_schemas import ProfileUpdate


# from .views import PostSchema


class UserRepository(BaseRepository[User]):
    """
    Репозиторий для работы с пользователями.
    Содержит методы для взаимодействия с базой данных.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Инициализация репозитория с сессией базы данных.

        :param session: Асинхронная сессия SQLAlchemy.
        """
        super().__init__(session=session, model=User)

    async def create(self, dto_user: UserCreate) -> User:
        """
        Создает нового пользователя в базе данных.

        :param dto_user: DTO с данными для создания пользователя.
        :return: Созданный объект пользователя.
        :raises IntegrityError: Если пользователь с таким email или username уже существует.
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

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Возвращает пользователя по его имени пользователя (username).

        :param username: Имя пользователя.
        :return: Объект пользователя или None, если пользователь не найден.
        """
        result = await self.session.execute(
            select(self.model).where(self.model.username == username)
        )
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: EmailStr) -> User | None:
        """
        Возвращает пользователя по его email.

        :param email: Email пользователя.
        :return: Объект пользователя или None, если пользователь не найден.
        """
        result = await self.session.execute(
            select(self.model).where(self.model.email == email)
        )
        return result.scalar_one_or_none()

    async def update(self, id_: int, data: dict[str, Any]) -> str | None: ...

    async def update_profile(
        self,
        user: User,
        dto_profile: ProfileUpdate,
    ) -> None:
        """
        Обновление данных профиля по указанным данным.
        :param user: Владелец профиля.
        :param dto_profile: Данные с формы обновления профиля.
        :return:
        """
        user.profile = Profile(**dto_profile.model_dump())
        await self.session.commit()

    async def delete(self, id_: int) -> str | None: ...

    async def update_user_avatar(self, user_id: int, avatar_url: str):
        """
        Обновляет аватар пользователя.

        :param user_id: ID пользователя.
        :param avatar_url: URL аватара.
        """
        user = await self.session.get(User, user_id)
        if not user:
            raise ValueError("User not found")

        user.profile.avatar = avatar_url
        await self.session.commit()
