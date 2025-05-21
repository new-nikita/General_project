from typing import Optional, Any, Sequence

from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.base_repository import BaseRepository
from backend.core.models import Post
from backend.posts.schemas import PostCreate


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
            content=dto_post.content,
            author_id=dto_post.author_id,
            image=dto_post.image,
        )
        # if dto_post.tags:
        #     tag_objects = list()
        #     for tag_name in dto_post.tags:
        #         # TODO сделать отдельный репозиторий для Tag
        #         tag = Tag(name=tag_name)
        #         tag_objects.append(tag)
        #
        #     new_post.tags = tag_objects

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

    async def update(self, id_: int, data: dict[str, Any]) -> str | None: ...

    async def delete(self, id_: int) -> str | None:
        """
        Удаляет пост по его ID.

        :param id_: ID поста.
        :return: Сообщение об успешном удалении или None, если пост не найден.
        """
        result = await self.session.execute(
            select(self.model).where(self.model.id == id_)
        )
        post = result.scalars().first()

        if not post:
            return

        await self.session.execute(delete(self.model).where(self.model.id == id_))
        await self.session.commit()
        return "Post deleted successfully"

    async def get_all_posts_by_author_id(
        self, author_id: int, current_user_id: Optional[int] = None
    ) -> Sequence[Post]:
        """
        Возвращает все посты пользователя с информацией о лайках.

        :param author_id: ID автора постов
        :param current_user_id: ID текущего пользователя для проверки лайков
        :return: Список постов с дополнительными атрибутами:
                 - likes_count: количество лайков
                 - is_liked: поставил ли текущий пользователь лайк
        """
        # Базовый запрос
        stmt = (
            select(self.model)
            .options(selectinload(self.model.author), selectinload(self.model.likes))
            .where(self.model.author_id == author_id)
            .order_by(self.model.created_at.desc())
        )

        result = await self.session.execute(stmt)
        posts = result.scalars().all()

        # Добавляем вычисляемые поля для каждого поста
        for post in posts:
            # Количество лайков
            post.likes_count = len(post.likes)

            # Проверяем, поставил ли текущий пользователь лайк
            post.is_liked_by_current = (
                any(like.user_id == current_user_id for like in post.likes)
                if current_user_id
                else False
            )

            # Список ID пользователей, поставивших лайк (для шаблона)
            post.liked_user_ids = [like.user_id for like in post.likes]

        return posts
