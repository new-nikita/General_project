from fastapi import HTTPException

from backend.posts.post_repository import PostRepository
from backend.posts.schemas import PostCreate
from backend.core.models import Post


class PostService:
    """
    Сервис для работы с постами.
    Предоставляет методы для создания, получения и обновления постов.
    """

    def __init__(self, repository: PostRepository):
        """
        Инициализация сервиса с репозиторием.

        :param repository: Экземпляр PostRepository.
        """
        self.repository: PostRepository = repository

    async def create_post_and_add_in_db(self, dto_post: PostCreate) -> Post:
        """
        Создает новый пост и сохраняет его в базе данных.

        :param dto_post: DTO с данными для создания поста.
        :return: Созданный объект Post.
        """
        return await self.repository.create(dto_post)

    async def get_post_by_id(self, post_id: int) -> Post:
        """
        Возвращает пост по его ID.

        :param post_id: ID поста.
        :return: Объект Post.
        :raises HTTPException: Если пост не найден.
        """
        post = await self.repository.get_post_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Пост не найден")
        return post
