from typing import Any, List

from mypy.checker import and_conditional_maps
from pydantic import EmailStr
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.core.base_repository import BaseRepository
from backend.core.models import User, Friendship
from backend.core.enums.follow_status import FollowStatus
from backend.exceptions.message_exceptions import FriendException
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

    async def get_friendship(
        self,
        current_user_id: int,
        your_user_id: int,
    ) -> Friendship | None:
        result = await self.session.execute(
            select(Friendship).where(
                or_(
                    and_(
                        Friendship.user_id == current_user_id,
                        Friendship.friend_id == your_user_id,
                    ),
                    and_(
                        Friendship.user_id == your_user_id,
                        Friendship.friend_id == current_user_id,
                    ),
                )
            )
        )

        return result.scalars().first()

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

    async def friend_add(self, current_user_id: int, your_user_id: int) -> None:
        """Отправляет запрос на дружбу

        :param current_user_id: Объект пользователя.
        :param your_user_id: ID друга
        :return: None
        """
        if current_user_id == your_user_id:
            raise FriendException("Нельзя добавить себя")

        user_id = min(current_user_id, your_user_id)
        friend_id = max(current_user_id, your_user_id)

        friendship = await self.get_friendship(
            user_id,
            friend_id,
        )

        if friendship:
            if friendship.status == FollowStatus.PENDING:
                raise FriendException("Заявка уже отправлена")
            if friendship.status == FollowStatus.ACCEPTED:
                raise FriendException("Вы уже друзья")
            if friendship.status == FollowStatus.BLOCKED:
                raise FriendException("Пользователь заблокирован")

        self.session.add(
            Friendship(
                user_id=user_id,
                friend_id=friend_id,
                status=FollowStatus.PENDING.value,
            )
        )
        await self.session.commit()

    async def friend_accept(
        self,
        current_user_id: int,
        from_user_id: int,
    ) -> None:
        """
        Метод принятия заявки

        :param current_user_id: тот, кто принимает заявку
        :param from_user_id: тот, кто её отправил
        """
        query = select(Friendship).where(
            Friendship.user_id == from_user_id,
            Friendship.friend_id == current_user_id,
            Friendship.status == FollowStatus.PENDING,
        )

        result = await self.session.execute(query)
        friendship = result.scalar_one_or_none()

        if not friendship:
            raise FriendException("Заявка не найдена")

        friendship.status = FollowStatus.ACCEPTED
        await self.session.commit()

    async def friend_reject(
        self,
        current_user_id: int,
        from_user_id: int,
    ) -> None:
        """
        Метод отклонения заявки

        :param current_user_id: тот, кто отклоняет заявку
        :param from_user_id: тот, кто её отправил
        :return:
        """
        query = select(Friendship).where(
            Friendship.user_id == from_user_id,
            Friendship.friend_id == current_user_id,
            Friendship.status == FollowStatus.PENDING,
        )

        result = await self.session.execute(query)
        friendship = result.scalar_one_or_none()

        if not friendship:
            raise FriendException("Заявка не найдена")

        friendship.status = FollowStatus.REJECTED
        await self.session.commit()
