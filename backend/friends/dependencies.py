from typing import Optional, Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, Form


from backend.users.schemas.profile_schemas import ProfileUpdate
from backend.core.common_dependencies import get_db_session
from backend.friends.friends_repository import FriendsRepository
from backend.friends.services import FriendsService


async def get_friends_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> FriendsRepository:
    """
    Создает и возвращает экземпляр FriendsRepository.

    FriendsRepository предоставляет методы для взаимодействия с таблицей связкой друзей
    в базе данных. Этот метод внедряет зависимость через FastAPI.

    :param session: Асинхронная сессия базы данных, предоставленная `get_db_session`.
    :returns: FriendsRepository: Экземпляр репозитория для работы со связкой друзей.
    """
    return FriendsRepository(session=session)


async def get_friends_service(
    repository: Annotated[FriendsService, Depends(get_friends_repository)],
) -> FriendsService:
    """
    Создает и возвращает экземпляр UserService.

    FriendsRepository предоставляет бизнес-логику для работы с пользователями.
    Он использует UserRepository для выполнения операций с базой данных.

    :param repository: Экземпляр репозитория, предоставленный `get_friends_repository`.
    :returns: FriendsRepository: Экземпляр сервиса для работы с пользователями.
    """
    return FriendsService(repository=repository)
