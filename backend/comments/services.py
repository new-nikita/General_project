from typing import Optional, Sequence

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.comments.schemas import CommentRead
from backend.core.models import Post, User
from backend.core.models.comment import Comment


class CommentService:
    """Сервис для работы с комментариями."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_comment(
        self,
        user_id: int,
        post_id: int,
        text: str,
        parent_id: Optional[int] = None,
    ):
        # Проверка существования поста
        post = await self.session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        # Если это ответ на комментарий
        if parent_id:
            parent_comment = await self.session.get(Comment, parent_id)
            if not parent_comment:
                raise HTTPException(status_code=404, detail="Parent comment not found")

            # Проверяем, что родительский комментарий не является ответом
            if parent_comment.parent_id is not None:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot reply to a reply. Only direct comments to posts are allowed",
                )

            # Проверяем, что комментарий и пост совпадают
            if parent_comment.post_id != post_id:
                raise HTTPException(
                    status_code=400,
                    detail="Parent comment does not belong to this post",
                )

        comment = Comment(
            user_id=user_id, post_id=post_id, parent_id=parent_id, text=text
        )
        self.session.add(comment)
        await self.session.commit()
        await self.session.refresh(comment)
        return comment

    async def get_comments_for_post(
        self,
        post_id: int,
        limit: int = 3,
        offset: int = 0,
    ):
        stmt = (
            select(Comment)
            .options(selectinload(Comment.user))
            .where(Comment.post_id == post_id)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        comments = result.scalars().all()
        return comments

    async def get_paginated_comments(
        self,
        post_id: int,
        offset: int = 0,
        limit: int = 3,
    ) -> tuple[Sequence[Comment], bool]:
        """
        Получение комментариев для поста с пагинацией.
        С добавлением проверки наличия следующих комментариев.
        :param post_id:
        :param offset:
        :param limit:
        :return:
        """
        # TODO добавить сортировку по дате или количеству лайков
        statement = (
            select(Comment)
            .where(Comment.post_id == post_id)
            .options(selectinload(Comment.user).selectinload(User.profile))
            .order_by(Comment.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(statement)
        comments = result.scalars().all()

        # Проверяем наличие следующих комментариев
        statement_for_has_more = (
            select(Comment.id)
            .where(Comment.post_id == post_id)
            .offset(offset + limit)
            .limit(1)
        )
        result = await self.session.execute(statement_for_has_more)
        has_more = result.scalars().first() is not None

        return comments, has_more
