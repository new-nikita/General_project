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
from backend.auth.authorization import get_current_user_from_cookie, get_current_user_ws
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
    message_service: Annotated[MessageService, Depends(get_message_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    current_user_ws: Annotated[User, Depends(get_current_user_ws)],
    companion_id: int,
):
    """
    Отображает диалог пользователей

    :param websocket:
    :param message_service: Сервис для работы с сообщениями (зависимость).
    :param user_service: Сервис работы с пользователями.
    :param current_user_ws: Авторизованный пользователь.
    :param companion_id: Тот пользователь которому пишут
    :return:
    """

    dialog_id = await message_service.create_dialog(
        current_user_ws.id,
        companion_id,
    )

    await manager.connect(websocket, dialog_id, current_user_ws.id)

    try:
        while True:
            text = await websocket.receive_text()
            message = settings.msg(
                dialog_id=dialog_id.id,
                sender_id=current_user_ws.id,
                text=text,
                created_at=datetime.utcnow(),
            )
            await message_service.save_message(message)

            # await manager.broadcast(message, dialog_id, current_user_ws.id)

    except WebSocketDisconnect:
        manager.disconnect(dialog_id, current_user_ws.id)


@router.get(
    "/dialog/{companion_id}",
    tags=["message"],
    response_class=HTMLResponse,
)
async def dialog_page(
    request: Request,
    companion_id: int,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    user_service: Annotated[UserService, Depends(get_user_service)],
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

    return settings.templates.template_dir.TemplateResponse(
        "chat/dialog.html",
        {
            "request": request,
            "companion_id": companion_id,
            "companion": f"{companion.profile.first_name or ''} {companion.profile.last_name or ''}".strip()
            or companion.username,
            "current_user": current_user,
        },
    )


@router.get("/dialogs", tags=["message"])
async def dialogs(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    message_service: Annotated[MessageService, Depends(get_message_service)],
):
    dialogs = await message_service.get_user_dialogs(current_user.id)

    return settings.templates.template_dir.TemplateResponse(
        "chat/dialogs_list.html",
        {
            "request": request,
            "dialogs": dialogs,
            "current_user": current_user,
        },
    )
