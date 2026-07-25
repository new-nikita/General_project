from typing import List, Dict
from datetime import datetime

from mypy.checker import and_conditional_maps
from pydantic import EmailStr
from sqlalchemy import select, and_, or_, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.core.base_repository import BaseRepository
from backend.core.config import ChatMessage
from backend.core.models import (
    User,
    Dialog,
    DialogParticipant,
    Message,
    MessageRead,
)

from backend.core.enums.follow_status import FollowStatus
from backend.exceptions.message_exceptions import FriendException
from backend.users.password_helper import PasswordHelper
from backend.users.schemas.profile_schemas import ProfileUpdate
from backend.users.schemas.users_schemas import UserCreate


class MessageRepository(BaseRepository[User]):
    """Репозиторий для работы с сообщениями.

    Содержит методы для взаимодействия с базой данных.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация репозитория с сессией базы данных.

        :param session: Асинхронная сессия SQLAlchemy.
        """
        super().__init__(session=session, model=User)

    async def create_dialog(
        self,
        current_user: int,
        companion_id: int,
    ) -> Dialog:

        user1_id, user2_id = sorted([current_user, companion_id])
        # Проверяем, есть ли уже такой диалог
        result = await self.session.execute(
            select(Dialog)
            .where(Dialog.user1_id == user1_id)
            .where(Dialog.user2_id == user2_id)
        )
        dialog = result.scalar_one_or_none()
        if dialog:
            return dialog  # возвращаем существующий диалог

        # Создаём новый
        dialog = Dialog(user1_id=user1_id, user2_id=user2_id, is_group=False)
        self.session.add(dialog)
        await self.session.flush()  # чтобы получить dialog.id

        # Добавляем участников
        self.session.add_all(
            [
                DialogParticipant(
                    dialog_id=dialog.id, user_id=user1_id, joined_at=datetime.utcnow()
                ),
                DialogParticipant(
                    dialog_id=dialog.id, user_id=user2_id, joined_at=datetime.utcnow()
                ),
            ]
        )
        await self.session.commit()
        return dialog

    async def get_dialog_messages(self, dialog_id: int, limit: int = 50):
        result = await self.session.execute(
            select(Message)
            .where(Message.dialog_id == dialog_id)
            .order_by(Message.id.desc())
            .limit(limit)
        )
        messages = list(result.scalars().all())
        return list(reversed(messages))

    async def get_last_read_message_id(
        self,
        dialog_id: int,
        user_id: int,
    ) -> int | None:
        result = await self.session.execute(
            select(DialogParticipant.last_read_message_id).where(
                DialogParticipant.dialog_id == dialog_id,
                DialogParticipant.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_user_dialogs(self, current_user_id: int) -> List[Dict]:
        """Список диалогов: собеседник, последнее сообщение, непрочитанные."""
        result = await self.session.execute(
            select(Dialog, DialogParticipant)
            .join(
                DialogParticipant,
                DialogParticipant.dialog_id == Dialog.id,
            )
            .where(DialogParticipant.user_id == current_user_id)
            .options(selectinload(Dialog.last_message))
            .order_by(Dialog.updated_at.desc())
        )
        rows = result.all()
        items: List[Dict] = []

        for dialog, participant in rows:
            companion_id = (
                dialog.user2_id
                if dialog.user1_id == current_user_id
                else dialog.user1_id
            )
            user_result = await self.session.execute(
                select(User).where(User.id == companion_id)
            )
            companion = user_result.scalar_one_or_none()
            if not companion:
                continue

            last_text = ""
            last_sender_id = None
            if dialog.last_message:
                last_text = dialog.last_message.text or ""
                last_sender_id = dialog.last_message.sender_id

            items.append(
                {
                    "dialog_id": dialog.id,
                    "user_id": companion.id,
                    "username": companion.username,
                    "last_message": last_text,
                    "unread_count": participant.unread_count or 0,
                    "last_message_sender_id": last_sender_id,
                }
            )

        return items

    async def save_message(self, chat_message: ChatMessage) -> Message:

        message = Message(
            dialog_id=chat_message.dialog_id,
            sender_id=chat_message.sender_id,
            text=chat_message.text,
            created_at=chat_message.created_at,
            updated_at=datetime.utcnow(),
        )
        self.session.add(message)
        await self.session.flush()  # чтобы получить message.id

        # Обновляем last_message_id в диалоге
        await self.session.execute(
            update(Dialog)
            .where(Dialog.id == chat_message.dialog_id)
            .values(
                last_message_id=message.id,
                updated_at=datetime.utcnow(),
            )
        )

        await self.session.execute(
            update(DialogParticipant)
            .where(DialogParticipant.dialog_id == chat_message.dialog_id)
            .where(DialogParticipant.user_id != chat_message.sender_id)
            .values(unread_count=DialogParticipant.unread_count + 1)
        )

        await self.session.commit()
        return message

    async def mark_dialog_as_read(
        self,
        dialog_id: int,
        user_id: int,
    ) -> int | None:
        participant_result = await self.session.execute(
            select(DialogParticipant).where(
                DialogParticipant.dialog_id == dialog_id,
                DialogParticipant.user_id == user_id,
            )
        )
        participant = participant_result.scalar_one_or_none()
        if not participant:
            return None

        max_id_result = await self.session.execute(
            select(func.max(Message.id)).where(Message.dialog_id == dialog_id)
        )
        max_message_id = max_id_result.scalar_one_or_none()
        if not max_message_id:
            participant.unread_count = 0
            await self.session.commit()
            return None

        participant.unread_count = 0
        participant.last_read_message_id = max_message_id
        await self.session.commit()
        return max_message_id

    async def mark_message_read(self, user_id: int, message_id: int):
        read = MessageRead(
            user_id=user_id, message_id=message_id, read_at=datetime.utcnow()
        )
        self.session.add(read)
        await self.session.commit()

    async def get_history_messages(self, current_user_id: int) -> List[Dict]:
        """
        Возвращает диалоги пользователя

        :param current_user_id:
        :return: Список диалогов
        """
        result = await self.session.execute(
            select(Dialog)
            .join(DialogParticipant)
            .where(DialogParticipant.user_id == current_user_id)
            .order_by(Dialog.updated_at.desc())
        )
        return result.scalars().all()
