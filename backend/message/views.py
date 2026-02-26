import logging
from typing import Annotated, Dict
import random
from datetime import datetime

from fastapi import (
    APIRouter,
    Request,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
    WebSocket,
    WebSocketDisconnect,
    Form,
)
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.testing import exclude

from backend.message.services import MessageService
from backend.message.utils import manager
from backend.message.dependencies import get_message_service
from backend.posts.dependencies import get_post_service
from backend.posts.services import PostService
from backend.users.dependencies import get_user_service, get_update_form
from backend.users.schemas.profile_schemas import ProfileUpdate
from backend.users.services import UserService
from backend.users.utils import checkout_profile_owner
from backend.auth.authorization import (
    get_current_user_from_cookie,
)
from backend.core.config import settings, DEFAULT_PATH_TO_AVATAR
from backend.core.models import User
from backend.utils.save_images import upload_image


logging.basicConfig(level=logging.INFO, format=settings.logging.log_format)

router = APIRouter(
    prefix="/ws/chat",
)


@router.websocket("/dialog/{companion_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    message_service: Annotated[MessageService, Depends(get_message_service)],
    companion_id: int,
):
    """
    Отображает диалог пользователей

    :param websocket:
    :param current_user: Текущий авторизованный пользователь (зависимость).
    :param user_service: Сервис для работы с пользователями (зависимость).
    :param message_service: Сервис для работы с сообщениями (зависимость).
    :param companion_id: Тот пользователь которому пишут
    :return:
    """

    dialog_id = await manager.get_or_create_dialog(current_user.id, companion_id)
    await manager.connect(websocket, dialog_id, current_user.id)

    try:
        while True:
            data = await websocket.receive_json()
            message = settings.msg(
                dialog_id=dialog_id,
                sender_id=current_user.id,
                text=data["text"],
                created_at=datetime.utcnow(),
            )
            await message_service.save_history_message(message.dict())

            await manager.broadcast(message, dialog_id, current_user.id)

    except WebSocketDisconnect:
        manager.disconnect(dialog_id, current_user.id)


@router.get("/dialog_page/{companion_id}", response_class=HTMLResponse)
async def dialog_page(
    request: Request,
    companion_id: int,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
):
    return settings.templates.template_dir.TemplateResponse(
        "chat/dialog.html",
        {
            "request": request,
            "companion_id": companion_id,
        },
    )


@router.post("/join_chat", response_class=HTMLResponse)
async def join_chat(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    username: str = Form(...),
    room_id: int = Form(...),
):
    """


    :param request:
    :param current_user:
    :param user_service:
    :param username:
    :param room_id:
    :return:
    """
    return settings.templates.template_dir.TemplateResponse(
        "users/profile.html",
        {
            "request": request,
            "room_id": room_id,
            "username": username,
            "user_id": user_id,
        },
    )
