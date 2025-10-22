from backend.follower.follower_repository import FollowersRepository
from backend.core.models import User


class FollowersService:
    """
    Сервис для работы с друзьями.
    Предоставляет методы для добавления, обновления и получения друзей.
    """

    def __init__(self, repository: FollowersRepository) -> None:
        """
        Инициализация сервиса с репозиторием.

        :param repository: Экземпляр UserRepository.
        """
        self.repository: FollowersRepository = repository
