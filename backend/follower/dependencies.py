from typing import Optional, Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, Form


from backend.users.schemas.profile_schemas import ProfileUpdate
from backend.core.common_dependencies import get_db_session
from backend.follower.follower_repository import FollowersRepository
from backend.follower.services import FollowersService


async def get_followers_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> FollowersRepository:
    """
    Создает и возвращает экземпляр FriendsRepository.

    FollowersRepository предоставляет методы для взаимодействия с таблицей связкой друзей
    в базе данных. Этот метод внедряет зависимость через FastAPI.

    :param session: Асинхронная сессия базы данных, предоставленная `get_db_session`.
    :returns: FollowersRepository: Экземпляр репозитория для работы со связкой друзей.
    """
    return FollowersRepository(session=session)


async def get_followers_service(
    repository: Annotated[FollowersService, Depends(get_followers_repository)],
) -> FollowersService:
    """
    Создает и возвращает экземпляр UserService.

    FollowersRepository предоставляет бизнес-логику для работы с пользователями.
    Он использует UserRepository для выполнения операций с базой данных.

    :param repository: Экземпляр репозитория, предоставленный `get_friends_repository`.
    :returns: FollowersRepository: Экземпляр сервиса для работы с пользователями.
    """
    return FollowersService(repository=repository)
