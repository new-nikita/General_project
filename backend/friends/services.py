from backend.friends.friends_repository import FriendsRepository
from backend.core.models import User, Friendship


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
        return await self.repository.get_search_for_filters(filters)

    async def friend_add(
        self,
        current_user_id: int,
        your_user_id: int,
    ) -> None:
        """Отправляет запрос на дружбу пользователю (User)

        :param current_user_id: ID пользователя.
        :param your_user_id: ID друга
        :return: None
        """
        return await self.repository.friend_add(current_user_id, your_user_id)

    async def friend_accept(
        self,
        current_user_id: int,
        from_user_id: int,
    ) -> None:
        """Принимает запрос на дружбу

        :param current_user_id: тот, кто принимает заявку
        :param from_user_id: тот, кто её отправил
        """

        return await self.repository.friend_accept(
            current_user_id,
            from_user_id,
        )

    async def friend_reject(
        self,
        current_user_id: int,
        from_user_id: int,
    ) -> None:
        """Отклоняет запрос на дружбу

        :param current_user_id: тот, кто принимает заявку
        :param from_user_id: тот, кто её отправил
        """

        return await self.repository.friend_reject(
            current_user_id,
            from_user_id,
        )
