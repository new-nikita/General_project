import logging
from typing import Annotated

import uuid
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Form,
)

from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import EmailStr

from backend.auth.Celery.tasks import send_confirmation_email_task
from backend.core.config import settings

from backend.auth import AsyncRedisClient
from backend.auth.authorization import get_redirect_with_authentication_user


from backend.users.dependencies import get_user_service
from backend.users.services import UserService


logging.basicConfig(
    format=settings.logging.log_format, level=settings.logging.log_level_value
)
logger = logging.getLogger(__name__)


router = APIRouter()


# Форма запроса сброса
@router.get("/forgot_password", response_class=HTMLResponse)
def request_reset_form(request: Request):
    return settings.templates.template_dir.TemplateResponse(
        "users/forgot_password.html",
        {"request": request},
    )


# Обработка запроса на сброс
@router.post("/forgot_password")
async def request_reset(
    request: Request,
    service: Annotated[UserService, Depends(get_user_service)],
    redis: Annotated[AsyncRedisClient, Depends(AsyncRedisClient)],
    email: EmailStr = Form(...),
):
    """
    Ендпоинт восстановления пароля

    :param request:
    :param email: Email пользователя
    :param service: Сервис работы с данными пользователя
    :param redis: Временное бд для отложенных задач
    :return:
    """

    try:
        await service.get_user_by_email(email)
        reset_token = str(uuid.uuid4())  # одноразовый токен

        await redis.connect()
        await redis.save_pending_disposable_token(reset_token, email)

        send_confirmation_email_task.delay(
            "reset_password",
            "message_reset_password",
            email,
            reset_token,
            str(request.base_url),
        )

        RedirectResponse(url="/further_actions", status_code=303)
        return settings.templates.template_dir.TemplateResponse(
            "info/further_actions.html",
            {"request": request},
        )

    except Exception as e:
        logger.error(f"Reset failed: {e}")
        return settings.templates.template_dir.TemplateResponse(
            "info/forgot_password.html",
            {"request": request, "error": "Пользователя с таким Email не существует."},
        )


# Ссылка сброса
@router.get("/reset_password", response_class=HTMLResponse)
async def reset_password_form(
    request: Request,
    token: str,
    redis: Annotated[AsyncRedisClient, Depends(AsyncRedisClient)],
):
    try:
        await redis.connect()
        await redis.get_pending_token(token)

        return settings.templates.template_dir.TemplateResponse(
            "users/reset_password.html",
            {"request": request, "token": token},
        )

    except HTTPException:
        logger.error(f"Reset password failed")
        raise HTTPException(status_code=400, detail="Неверный или истекший токен")


# Обработка сброса
@router.post("/reset_password")
async def reset_password(
    request: Request,
    service: Annotated[UserService, Depends(get_user_service)],
    redis: Annotated[AsyncRedisClient, Depends(AsyncRedisClient)],
    token: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
) -> RedirectResponse:
    try:
        await redis.connect()
        email = await redis.get_pending_token(token)
        user = await service.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        if new_password != confirm_password:
            raise HTTPException(status_code=400, detail="Пароли не совпадают")

        await service.change_password_by_user(user, new_password)

        redirect = await get_redirect_with_authentication_user(user)
        return redirect

    except Exception as e:
        logger.error(f"Reset password failed: %s", e)
        raise HTTPException(status_code=500, detail="Ошибка при смене пароля")
