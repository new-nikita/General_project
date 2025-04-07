from sqlalchemy import select
from typing import Optional, Any

from core.base_repository import BaseRepository
from core.models import Post, Tag
from sqlalchemy.ext.asyncio import AsyncSession

from posts.schemas import PostCreate


class PostRepository(BaseRepository[Post]):
    """
    Репозиторий для работы с постами.
    """

    def __init__(self, session: AsyncSession):
        """
        Метод для инициализации репозитория.
        :param session: асинхронная сессия SQLAlchemy
        """
        super().__init__(session=session, model=Post)

    async def create(self, dto_post: PostCreate) -> Post:
        """
        Создает объект поста в БД
        :param dto_post: DTO с данными для создания поста
        :return: объект поста
        """
        new_post = Post(
            title=dto_post.title,
            content=dto_post.content,
            is_published=dto_post.is_published,
            author_id=dto_post.author_id
        )
        if dto_post.tags:
            tag_objects = list()
            for tag_name in dto_post.tags:
                # TODO сделать отдельный репозиторий для Tag
                tag = Tag(name=tag_name)
                tag_objects.append(tag)

            new_post.tags = tag_objects

        self.session.add(new_post)
        await self.session.commit()
        await self.session.refresh(new_post)
        return new_post

    async def get_post_by_id(self, post_id: int) -> Optional[Post]:
        """
        Возвращает пост по его ID.

        :param post_id: ID поста.
        :return: Объект Post или None, если пост не найден.
        """
        result = await self.session.execute(
            select(self.model).where(self.model.id == post_id)
        )
        return result.scalar_one_or_none()

    async def update(self, id_: int, data: dict[str, Any]) -> str | None:
        ...

    async def delete(self, id_: int) -> str | None:
        ...
