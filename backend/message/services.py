from typing import Dict, List

from backend.message.repository import MessageRepository
from backend.core.models import User, Dialog, Message
from backend.core.config import ChatMessage


class MessageService:
    """
    Сервис для работы с сообщениями.
    Предоставляет методы для создания чата, обновления в реальном времени.
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

    async def get_dialog_messages(
        self,
        dialog_id: int,
        viewer_id: int,
        companion_id: int,
        limit: int = 50,
    ) -> List[Dict]:
        messages = await self.repository.get_dialog_messages(dialog_id, limit)
        viewer_last_read = await self.repository.get_last_read_message_id(
            dialog_id,
            viewer_id,
        )
        companion_last_read = await self.repository.get_last_read_message_id(
            dialog_id,
            companion_id,
        )

        items: List[Dict] = []
        for message in messages:
            is_mine = message.sender_id == viewer_id
            is_read_by_me = (
                not is_mine
                and viewer_last_read is not None
                and message.id <= viewer_last_read
            )
            is_read_by_companion = (
                is_mine
                and companion_last_read is not None
                and message.id <= companion_last_read
            )
            items.append(
                {
                    "id": message.id,
                    "dialog_id": message.dialog_id,
                    "sender_id": message.sender_id,
                    "text": message.text,
                    "created_at": (
                        message.created_at.isoformat()
                        if message.created_at
                        else None
                    ),
                    "is_read_by_me": is_read_by_me,
                    "is_read_by_companion": is_read_by_companion,
                }
            )
        return items

    async def mark_dialog_as_read(self, dialog_id: int, user_id: int) -> int | None:
        return await self.repository.mark_dialog_as_read(dialog_id, user_id)

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
