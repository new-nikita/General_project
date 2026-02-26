from typing import Any, List, Dict

from mypy.checker import and_conditional_maps
from pydantic import EmailStr
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.core.base_repository import BaseRepository
from backend.core.models import User
from backend.core.enums.follow_status import FollowStatus
from backend.exceptions.message_exceptions import FriendException
from backend.users.password_helper import PasswordHelper
from backend.users.schemas.profile_schemas import ProfileUpdate
from backend.users.schemas.users_schemas import UserCreate


class MessageRepository(BaseRepository[User]):
    """Репозиторий для работы с друзьями.

    Содержит методы для взаимодействия с базой данных.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория с сессией базы данных.

        :param session: Асинхронная сессия SQLAlchemy.
        """
        super().__init__(session=session, model=User)

    async def save_history_message(self, message: Dict) -> None:
        """
        Сохраняет историю сообщений пользователей

        :param message: История сообщения
        :return: None
        """
        return
