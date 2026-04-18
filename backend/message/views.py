import logging
from typing import Annotated, Dict
import random
from datetime import datetime

from fastapi import (
    APIRouter,
    Request,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)

from backend.message.services import MessageService
from backend.message.utils import manager
from backend.message.dependencies import get_message_service
from backend.users.dependencies import get_user_service
from backend.users.services import UserService
from backend.auth.authorization import get_current_user_from_cookie, get_current_user_ws
from backend.core.config import settings
from backend.core.models import User


logging.basicConfig(level=logging.INFO, format=settings.logging.log_format)

router = APIRouter(prefix="/messages", tags=["messages"])


@router.websocket("/dialog/{companion_id}")
@router.websocket("/ws/{companion_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    message_service: Annotated[MessageService, Depends(get_message_service)],
    current_user: Annotated[User, Depends(get_current_user_ws)],
    companion_id: int,
):
    dialog = await message_service.create_dialog(
        current_user.id,
        companion_id,
    )

    await manager.connect(websocket, dialog.id, current_user.id)

    try:
        while True:
            text = await websocket.receive_text()

            message = settings.msg(
                dialog_id=dialog.id,
                sender_id=current_user.id,
                text=text,
                created_at=datetime.utcnow(),
            )

            saved_message = await message_service.save_message(message)

            # ВАЖНО — отправляем всем
            await manager.broadcast(
                {
                    "type": "message",
                    "id": saved_message.id,
                    "text": saved_message.text,
                    "sender_id": saved_message.sender_id,
                    "created_at": saved_message.created_at.isoformat(),
                },
                dialog.id,
            )

    except WebSocketDisconnect:
        manager.disconnect(dialog.id, current_user.id)


@router.get("/dialog/{companion_id}")
async def get_dialog(
    request: Request,
    companion_id: int,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    message_service: Annotated[MessageService, Depends(get_message_service)],
):
    """Отображает страницу диалога

    :param request: Request.
    :param companion_id: id чата.
    :param current_user: Авторизованный пользователь.
    :param user_service: Сервис для работы с пользователями.
    :return:
    """

    companion = await user_service.get_user_by_id(companion_id)
    if not companion:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    dialog = await message_service.create_dialog(current_user.id, companion.id)

    message = await message_service.get_dialog_messages(dialog.id)

    return {"items": message}


@router.get("/dialogs")
async def get_dialogs(
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    message_service: Annotated[MessageService, Depends(get_message_service)],
):
    dialogs = await message_service.get_user_dialogs(current_user.id)

    return {"items": dialogs}
