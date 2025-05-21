from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.authorization import get_current_user_from_cookie
from backend.core.models import User
from backend.core.common_dependencies import get_db_session
from backend.likes.services import toggle_like_with_count

router = APIRouter()


@router.post("/posts/{post_id}/like/", status_code=status.HTTP_200_OK)
async def like_post(
    post_id: int,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict:
    """
    Обработчик POST-запроса для добавления или удаления лайка у поста.

    :param post_id: ID поста, который лайкает пользователь.
    :param current_user: Пользователь, отправивший запрос.
    :param session: Асинхронная сессия SQLAlchemy для работы с БД.
    :return: JSON-ответ с результатом операции:
             - success: bool
             - action: "added" или "removed"
             - likes_count: текущее количество лайков
             - liked: True/False — поставлен ли лайк сейчас
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не авторизован",
        )

    like_data = await toggle_like_with_count(
        session=session,
        user_id=current_user.id,
        post_id=post_id,
    )

    return {
        "success": like_data["success"],
        "action": like_data["action"],
        "likes_count": like_data["likes_count"],
        "liked": like_data["liked"],
    }
