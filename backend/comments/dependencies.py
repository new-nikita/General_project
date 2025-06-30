from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.comments.services import CommentService
from backend.core.common_dependencies import get_db_session


def get_comment_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
):
    """
    Создаёт и возвращает экземпляр PostService.

    :param session: Асинхронная сессия базы данных.
    :return: Экземпляр PostService.
    """
    return CommentService(session=session)
