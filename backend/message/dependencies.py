from typing import Optional, Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, Form


from backend.users.schemas.profile_schemas import ProfileUpdate
from backend.core.common_dependencies import get_db_session
from backend.message.repository import MessageRepository
from backend.message.services import MessageService


async def get_message_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> MessageRepository:
    """
    Создает и возвращает экземпляр MessageRepository.

    FriendsRepository предоставляет методы для взаимодействия с таблицей связкой друзей
    в базе данных. Этот метод внедряет зависимость через FastAPI.

    :param session: Асинхронная сессия базы данных, предоставленная `get_db_session`.
    :returns: FriendsRepository: Экземпляр репозитория для работы со связкой друзей.
    """
    return MessageRepository(session=session)


async def get_message_service(
    repository: Annotated[MessageService, Depends(get_message_repository)],
) -> MessageService:
    """
    Создает и возвращает экземпляр MessageService.

    FriendsRepository предоставляет бизнес-логику для работы с пользователями.
    Он использует UserRepository для выполнения операций с базой данных.

    :param repository: Экземпляр репозитория, предоставленный `get_friends_repository`.
    :returns: FriendsRepository: Экземпляр сервиса для работы с пользователями.
    """
    return MessageService(repository=repository)
