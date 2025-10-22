from typing import Any, List

from mypy.checker import and_conditional_maps
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.core.base_repository import BaseRepository
from backend.core.models import User, Friendship, Follower
from backend.users.password_helper import PasswordHelper
from backend.users.schemas.profile_schemas import ProfileUpdate
from backend.users.schemas.users_schemas import UserCreate


class FollowersRepository(BaseRepository[Follower]):
    """Репозиторий для работы с друзьями.

    Содержит методы для взаимодействия с базой данных.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория с сессией базы данных.

        :param session: Асинхронная сессия SQLAlchemy.
        """
        super().__init__(session=session, model=Follower)
