from typing import Dict

from backend.message.repository import MessageRepository
from backend.core.models import User


class MessageService:
    """
    Сервис для работы с друзьями.
    Предоставляет методы для добавления, обновления и получения друзей.
    """

    def __init__(self, repository: MessageRepository) -> None:
        """
        Инициализация сервиса с репозиторием.

        :param repository: Экземпляр UserRepository.
        """
        self.repository: MessageRepository = repository

    async def save_history_message(self, message: Dict) -> None:
        """
        Сохраняет историю сообщений пользователей

        :param message: История сообщения
        :return: None
        """
        return await self.repository.save_history_message()
