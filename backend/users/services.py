from fastapi import HTTPException

from users.repository import UserRepository
from users.schemas.users_schemas import UserCreate
from core.models import User


class UserService:
    """
    Сервис для работы с пользователями.
    Предоставляет методы для создания, обновления и получения пользователей.
    """

    def __init__(self, repository: UserRepository):
        """
        Инициализация сервиса с репозиторием.

        :param repository: Экземпляр UserRepository.
        """
        self.repository: UserRepository = repository

    async def create_user_and_added_in_db(self, dto_user: UserCreate) -> User:
        """
        Создает нового пользователя и сохраняет его в базе данных.

        :param dto_user: DTO с данными для создания пользователя.
        :return: Созданный объект пользователя.
        :raises HTTPException: Если пользователь с таким email или username уже существует.
        """
        if await self.repository.get_user_by_email(dto_user.email):
            raise HTTPException(
                status_code=400, detail="Пользователь с таким email уже существует."
            )

        if await self.repository.get_user_by_username(dto_user.username):
            raise HTTPException(
                status_code=400, detail="Пользователь с таким username уже существует."
            )

        return await self.repository.create(dto_user)

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Возвращает пользователя по его имени пользователя (username).

        :param username: Имя пользователя.
        :return: Объект пользователя или None, если пользователь не найден.
        """

        return await self.repository.get_user_by_username(username)
