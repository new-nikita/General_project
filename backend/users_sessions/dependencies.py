from typing import Optional, Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from backend.core.common_dependencies import get_db_session
from backend.users_sessions.user_sessions_repository import UserSessionsRepository
from backend.users_sessions.services import UserSessionsService


async def get_user_sessions_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserSessionsRepository:
    """
    Создает и возвращает экземпляр UserSessionsRepository.

    UserSessionsRepository предоставляет методы для взаимодействия с таблицей пользователей
    в базе данных. Этот метод внедряет зависимость через FastAPI.

    :param session: Асинхронная сессия базы данных, предоставленная `get_db_session`.
    :returns: UserSessionsRepository: Экземпляр репозитория для работы с пользователями.
    """
    return UserSessionsRepository(session=session)


async def get_user_sessions_service(
    repository: Annotated[
        UserSessionsRepository, Depends(get_user_sessions_repository)
    ],
) -> UserSessionsService:
    """
    Создает и возвращает экземпляр UserSessionsService.

    UserSessionsService предоставляет бизнес-логику для работы с пользователями.
    Он использует UserSessionsRepository для выполнения операций с базой данных.

    :param repository: Экземпляр репозитория, предоставленный `get_user_repository`.
    :returns: UserSessionsService: Экземпляр сервиса для работы с пользователями.
    """
    return UserSessionsService(repository=repository)
