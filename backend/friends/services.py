from backend.friends.friends_repository import FriendsRepository
from backend.core.models import User


class FriendsService:
    """
    Сервис для работы с друзьями.
    Предоставляет методы для добавления, обновления и получения друзей.
    """

    def __init__(self, repository: FriendsRepository) -> None:
        """
        Инициализация сервиса с репозиторием.

        :param repository: Экземпляр UserRepository.
        """
        self.repository: FriendsRepository = repository

    async def get_friends_friends(self, user_id: int) -> list[User]:
        """Возвращает подтвержденных друзей.

        :param user_id: Id пользователя.
        :return: Возвращает список подтвержденных друзей.
        """
        return await self.repository.get_friends_friends(user_id)

    async def get_pending_friends(self, user_id: int) -> list[User]:
        """Возвращает неподтвержденных друзей.

        :param user_id: Id пользователя.
        :return: Возвращает список неподтвержденных друзей.
        """
        return await self.repository.get_pending_friends(user_id)

    async def get_search_for_filters(
        self,
        user: User,
        filters: dict,
    ) -> list[User] | None:
        """Возвращает список пользователей по фильтрам

        :param user: Объект пользователя.
        :param filters: Фильтры поиска
        :return: Список объектов пользователей или None, если пользователи не найдены.
        """
        return await self.repository.get_search_for_filters(user, filters)
