from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from core.common_dependencies import get_db_session
from users.repository import UserRepository
from users.services import UserService


async def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
) -> UserRepository:
    """
    Создает и возвращает экземпляр UserRepository.

    UserRepository предоставляет методы для взаимодействия с таблицей пользователей
    в базе данных. Этот метод внедряет зависимость через FastAPI.

    Args:
        session (AsyncSession): Асинхронная сессия базы данных, предоставленная `get_db_session`.

    Returns:
        UserRepository: Экземпляр репозитория для работы с пользователями.
    """
    return UserRepository(session=session)


async def get_user_service(
    repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    """
    Создает и возвращает экземпляр UserService.

    UserService предоставляет бизнес-логику для работы с пользователями.
    Он использует UserRepository для выполнения операций с базой данных.

    Args:
        repository (UserRepository): Экземпляр репозитория, предоставленный `get_user_repository`.

    Returns:
        UserService: Экземпляр сервиса для работы с пользователями.
    """
    return UserService(repository=repository)
