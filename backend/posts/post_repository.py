from typing import Optional, Sequence

from sqlalchemy import select, delete, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.base_repository import BaseRepository
from backend.core.models import Post
from backend.posts.schemas import PostCreate, PostUpdate
from backend.core.models import LikePost


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
        try:
            new_post = Post(
                content=dto_post.content,
                author_id=dto_post.author_id,
                image=dto_post.image,
            )

            self.session.add(new_post)
            await self.session.commit()
            await self.session.refresh(new_post)

        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ValueError(f"Ошибка при создании поста: {str(e)}")

        except Exception as e:
            await self.session.rollback()
            raise ValueError(f"Неизвестная ошибка при обновлении поста: {str(e)}")

        else:
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

    async def update(self, post: Post, update_data: PostUpdate) -> Optional[Post]:
        """
        Обновляет пост по ID с данными из DTO.

        :param post: Поста для обновления
        :param update_data: Данные для обновления
        :return: Обновлённый пост или None, если пост не найден
        :raise ValueError: Если произошла ошибка при обновлении
        """
        try:
            data_dict = update_data.model_dump(exclude_unset=True)
            for field, value in data_dict.items():
                setattr(post, field, value)

            await self.session.commit()
            await self.session.refresh(post)
            return post

        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ValueError(f"Ошибка базы данных при обновлении поста: {str(e)}")
        except Exception as e:
            await self.session.rollback()
            raise ValueError(f"Неизвестная ошибка при обновлении поста: {str(e)}")

    async def delete(self, post: Post) -> bool:
        """
        Удаляет пост по его ID.

        :param post: Удаляемый пост.
        :return: True, если удалено, иначе False
        """
        await self.session.execute(delete(self.model).where(self.model.id == post.id))
        await self.session.commit()
        return True

    async def get_all_posts_by_author_id(
        self,
        author_id: int,
        current_user_id: Optional[int] = None,
    ) -> Sequence[Post]:
        """
        Возвращает все посты пользователя с информацией о лайках.

        :param author_id: ID автора
        :param current_user_id: ID текущего пользователя (опционально)
        :return: список постов с дополнительной информацией о лайках
        """
        stmt = (
            select(self.model)
            .outerjoin(self.model.likes)
            .options(selectinload(self.model.likes))
            .where(self.model.author_id == author_id)
            .group_by(self.model.id)
            .order_by(self.model.created_at.desc())
        )

        result = await self.session.execute(stmt)
        posts = result.scalars().all()

        for post in posts:
            self._enrich_post_with_likes(post, current_user_id)
        return posts

    async def remove_image(self, post: Post) -> Optional[dict]:
        """
        Убирает изображение у поста.

        :param post: Пост
        :return: данные с результатом операции
        """
        post.image = None
        try:
            await self.session.commit()
            return {"success": True, "message": "Изображение удалено"}
        except SQLAlchemyError as e:
            await self.session.rollback()
            return {
                "success": False,
                "message": f"Ошибка при удалении изображения: {e}",
            }

    async def get_paginated_posts_by_likes(
        self,
        page: int = 1,
        limit: int = 10,
        current_user_id: int | None = None,
    ) -> tuple[Sequence[Post], int]:
        """
        Получает страницу постов, отсортированных по количеству лайков.

        :param page: Номер страницы (начинается с 1)
        :param limit: Количество постов на странице
        :param current_user_id: ID авторизованного пользователя или None
        :return: Кортеж из:
            - Список постов для текущей страницы
            - Общее количество страниц
        """

        offset_val = (page - 1) * limit

        stmt = (
            select(self.model)
            .outerjoin(self.model.likes)
            .options(selectinload(self.model.likes))
            .group_by(self.model.id)
            .order_by(func.count(LikePost.id).desc(), self.model.created_at.desc())
            .offset(offset_val)
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        posts = result.scalars().all()

        for post in posts:
            self._enrich_post_with_likes(post, current_user_id)

        total_count = await self.session.scalar(
            select(func.count(self.model.id)).select_from(self.model)
        )

        total_pages = (total_count + limit - 1) // limit  # округление вверх

        return posts, total_pages

    @classmethod
    def _enrich_post_with_likes(
        cls,
        post: Post,
        current_user_id: Optional[int] = None,
    ) -> Post:
        """Добавляет информацию о лайках к посту:
        - количество лайков
        - проверка лайкнул ли текущий пользователь
        - ids всех пользователей, которым понравился этот пост.
        """
        post.likes_count = len(post.likes)
        post.is_liked_by_current = (
            any(like.user_id == current_user_id for like in post.likes)
            if current_user_id
            else False
        )
        post.liked_user_ids = {like.user_id for like in post.likes}
        return post
