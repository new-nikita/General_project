from typing import Any, List

from mypy.checker import and_conditional_maps
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.core.base_repository import BaseRepository
from backend.core.models import User, Friendship
from backend.users.password_helper import PasswordHelper
from backend.users.schemas.profile_schemas import ProfileUpdate
from backend.users.schemas.users_schemas import UserCreate


class FriendsRepository(BaseRepository[Friendship]):
    """Репозиторий для работы с друзьями.

    Содержит методы для взаимодействия с базой данных.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория с сессией базы данных.

        :param session: Асинхронная сессия SQLAlchemy.
        """
        super().__init__(session=session, model=Friendship)

    async def get_friends_friends(self, user_id: int) -> list[User]:
        result = await self.session.execute(
            select(User)
            .join(Friendship, Friendship.friend_id == User.id)
            .where(Friendship.user_id == user_id)
            .where(Friendship.status == "friends")
        )
        return result.scalars().all()

    async def get_pending_friends(self, user_id: int) -> list[User]:
        result = await self.session.execute(
            select(User)
            .join(Friendship, Friendship.friend_id == User.id)
            .where(Friendship.user_id == user_id)
            .where(Friendship.status == "pending")
        )
        return result.scalars().all()

    async def get_search_for_filters(self, filters: dict) -> list[User] | None:
        conditions = []

        for key, value in filters.items():
            field = getattr(self.model, key, None)
            if field is None or value is None:
                continue

            # Пример для строк - поиск по подстроке без учета регистра
            if isinstance(value, str) and key in [
                "username",
                "query",
                "city",
                "country",
            ]:
                conditions.append(field.ilike(f"%{value}%"))
            # Пример для возрастных фильтров (если ключи с префиксом)
            elif key == "age_min":
                conditions.append(getattr(self.model, "age") >= value)
            elif key == "age_max":
                conditions.append(getattr(self.model, "age") <= value)
            else:
                # Точное сравнение для остальных фильтров
                conditions.append(field == value)

        stmt = select(self.model)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        result = await self.session.execute(stmt)
        return result.scalars().all()
