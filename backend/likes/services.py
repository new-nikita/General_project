from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.models.like import LikePost


async def toggle_like_with_count(
    session: AsyncSession, user_id: int, post_id: int
) -> dict:
    """
    Добавляет или удаляет лайк и возвращает обновлённое количество лайков

    :param session: Асинхронная сессия SQLAlchemy
    :param user_id: ID пользователя
    :param post_id: ID поста
    :return: Словарь с результатом операции и количеством лайков
    """

    # Проверяем, есть ли уже лайк
    stmt = select(LikePost).where(
        LikePost.user_id == user_id, LikePost.post_id == post_id
    )
    result = await session.execute(stmt)
    like: LikePost | None = result.scalars().first()

    if like:
        await session.delete(like)
        action = "removed"
    else:
        new_like = LikePost(post_id=post_id, user_id=user_id)
        session.add(new_like)
        action = "added"

    await session.commit()

    # Считаем актуальное количество лайков
    count_stmt = select(func.count()).where(LikePost.post_id == post_id)
    likes_count = (await session.execute(count_stmt)).scalar_one_or_none() or 0

    return {
        "success": True,
        "action": action,
        "likes_count": likes_count,
        "liked": action == "added",
    }
