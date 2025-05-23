from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from backend.core.common_dependencies import get_db_session
from backend.posts.post_repository import PostRepository
from backend.posts.services import PostService


async def get_post_repository(
    session: AsyncSession = Depends(get_db_session),
) -> PostRepository:
    """
    Создает и возвращает экземпляр PostRepository.

    Args:
        session (AsyncSession): Асинхронная сессия базы данных, предоставленная `get_db_session`.

    Returns:
        PostRepository: Экземпляр репозитория для работы с постами.
    """
    return PostRepository(session=session)


async def get_post_service(
    repository: PostRepository = Depends(get_post_repository),
) -> PostService:
    """
    Создаёт и возвращает экземпляр PostService.

    PostService предоставляет бизнес-логику для работы с объектами постов.
    Используется PostRepository для выполнения операций с базой данных.

    Args:
        repository (PostRepository): Экземпляр репозитория, предоставленный `get_post_repository`.

    Returns:
        PostService: Экземпляр сервиса для работы с пользователями.
    """
    return PostService(repository=repository)
