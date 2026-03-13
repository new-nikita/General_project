from typing import Dict, List

from backend.message.repository import MessageRepository
from backend.core.models import User, Dialog, Message
from backend.core.config import ChatMessage


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

    async def create_dialog(
        self,
        current_user: int,
        companion_id: int,
    ) -> Dialog:
        """
        Создает диалог пользователей

        :param current_user:
        :param companion_id:
        :return:
        """
        return await self.repository.create_dialog(current_user, companion_id)

    async def get_dialog_messages(self, dialog_id: int, limit: int = 50):
        """
        Возвращает историю сообщений диалога

        :param dialog_id:
        :param limit:
        :return:
        """
        return self.repository.get_dialog_messages(dialog_id, limit)

    async def save_message(self, chat_message: ChatMessage) -> Message:
        """
        Сохраняет сообщения диалога

        :param dialog_id:
        :param sender_id:
        :param text:
        :return:
        """
        return await self.repository.save_message(chat_message)

    async def mark_message_read(self, user_id: int, message_id: int):
        """
        Помечает статус сообщения (прочитан или нет)

        :param user_id:
        :param message_id:
        :return:
        """
        return await self.repository.mark_message_read(user_id, message_id)

    async def get_history_messages(self, current_user_id: int) -> List[Dict]:
        """
        Возвращает диалоги пользователя

        :param current_user_id:
        :return: Список диалогов
        """
        return await self.repository.get_history_messages(current_user_id)

    async def get_user_dialogs(self, current_user_id: int) -> List[Dict]:
        """
        Возвращает диалоги пользователя

        :param current_user_id:
        :return:
        """
        return await self.repository.get_user_dialogs(current_user_id)
