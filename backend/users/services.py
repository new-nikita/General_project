import logging
from fastapi import HTTPException, Depends
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import User, db_helper
from users.schemas import UserCreate, UserUpdate
from .password_helper import PasswordHelper

logger = logging.getLogger(__name__)


# TODO вынести логику в UserRepository
class UserService:
    """
    Сервис для работы с пользователями.
    Предоставляет методы для создания, обновления и получения пользователей.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Инициализация сервиса с сессией базы данных.

        :param session: Асинхронная сессия SQLAlchemy.
        """
        self.session: AsyncSession = session

    async def create_user_and_added_in_db(self, dto_user: UserCreate) -> User:
        """
        Создает нового пользователя и сохраняет его в базе данных.

        :param dto_user: DTO с данными для создания пользователя.
        :return: Созданный объект пользователя.
        :raises HTTPException: Если пользователь с таким email или username уже существует.
        """

        await self._check_data(dto_user)
        user = await self.create_user(dto_user)

        try:
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except IntegrityError as e:
            logger.error(f"Ошибка при создании пользователя: {e}")
            await self.session.rollback()
            raise HTTPException(
                status_code=500, detail="Не удалось создать пользователя."
            )

    @staticmethod
    async def create_user(dto_user: UserCreate) -> User:
        """
        Создает новый объект пользователя с хешированным паролем.

        :param dto_user: DTO с данными для создания пользователя.
        :return: Объект пользователя.
        """
        hashed_password = PasswordHelper.generate_password(str(dto_user.password))
        return User(
            username=dto_user.username,
            email=dto_user.email,
            hashed_password=hashed_password,
        )

    async def _check_user_exists_by_email(self, email: EmailStr) -> bool:
        """
        Проверяет, существует ли пользователь с указанным email.

        :param email: Email для проверки.
        :return: True, если пользователь существует, иначе False.
        """
        result = await self.session.execute(
            select(User).where(User.email == email).limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def _check_user_exists_by_username(self, username: str) -> bool:
        """
        Проверяет, существует ли пользователь с указанным username.

        :param username: Username для проверки.
        :return: True, если пользователь существует, иначе False.
        """
        result = await self.session.execute(
            select(User).where(User.username == username).limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def _check_data(self, dto_user: UserCreate) -> None:
        """
        Проверяет, что пользователь с указанным email и username не существует.

        :param dto_user: DTO с данными для создания пользователя.
        :raises HTTPException: Если пользователь с таким email или username уже существует.
        """
        if await self._check_user_exists_by_email(email=dto_user.email):
            raise HTTPException(
                status_code=400, detail="Пользователь с таким email уже существует."
            )

        if await self._check_user_exists_by_username(username=dto_user.username):
            raise HTTPException(
                status_code=400, detail="Пользователь с таким username уже существует."
            )

    async def update_user(self, user_id: int, update_data: UserUpdate) -> User | None:
        """
        Обновляет данные существующего пользователя.

        :param user_id: ID пользователя, которого нужно обновить.
        :param update_data: DTO с новыми данными пользователя.
        :return: Обновленный объект пользователя или None, если пользователь не найден.
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None

        if update_data.password:
            user.hashed_password = PasswordHelper.generate_password(
                update_data.password.get_secret_value()
            )
        if update_data.username:
            user.username = update_data.username
        if update_data.email:
            user.email = update_data.email

        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Возвращает пользователя по его ID.

        :param user_id: ID пользователя.
        :return: Объект пользователя или None, если пользователь не найден.
        """
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Возвращает пользователя по его имени пользователя (username).

        :param username: Имя пользователя.
        :return: Объект пользователя или None, если пользователь не найден.
        """
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()


async def get_db_session() -> AsyncSession:
    async for session in db_helper.session_getter():
        yield session


async def get_service(session: AsyncSession = Depends(get_db_session)) -> UserService:
    """
    Возвращает экземпляр UserService с текущей сессией базы данных.
    """
    return UserService(session)
