import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import EmailStr

from backend.auth.authorization import get_redirect_with_authentication_user
from backend.auth.Celery.tasks import send_confirmation_email_task
from backend.auth.redis_client import AsyncRedisClient
from backend.core.config import settings
from backend.users.dependencies import get_user_service
from backend.users.services import UserService

logging.basicConfig(
    format=settings.logging.log_format, level=settings.logging.log_level_value
)
logger = logging.getLogger(__name__)

NOT_FOUND_USER_MESSAGE = "Пользователь с таким email не найден"
INVALID_TOKEN_MESSAGE = "Невалидный токен"

router = APIRouter()


@router.get("/forgot_password", response_class=HTMLResponse)
def request_reset_form(request: Request) -> HTMLResponse:
    """Форма запроса сброса пароля."""
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
) -> HTMLResponse:
    """Ендпоинт восстановления пароля.

    :param request: Запрос FastAPI
    :param email: Email пользователя
    :param service: Сервис работы с данными пользователя
    :param redis: Временное бд для отложенных задач
    :return: HTMLResponse
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
        logger.error("Reset failed: %s", e)
        return settings.templates.template_dir.TemplateResponse(
            "info/forgot_password.html",
            {
                "request": request,
                "error": "Пользователя с таким Email не существует.",
            },
        )


@router.get("/reset_password", response_class=HTMLResponse)
async def reset_password_form(
    request: Request,
    token: str,
    redis: Annotated[AsyncRedisClient, Depends(AsyncRedisClient)],
) -> HTMLResponse:
    """Страница сброса пароля."""
    try:
        await redis.connect()
        await redis.get_pending_token(token)

        return settings.templates.template_dir.TemplateResponse(
            "users/reset_password.html",
            {"request": request, "token": token},
        )

    except HTTPException:
        logger.error("Reset password failed")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный или истекший токен",
        )


# Обработка сброса
@router.post("/reset_password")
async def reset_password(
    service: Annotated[UserService, Depends(get_user_service)],
    redis: Annotated[AsyncRedisClient, Depends(AsyncRedisClient)],
    token: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
) -> RedirectResponse:
    try:
        if new_password != confirm_password:
            raise HTTPException(status_code=400, detail="Пароли не совпадают")

        await redis.connect()
        email = await redis.get_pending_token(token)
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=INVALID_TOKEN_MESSAGE,
            )
        user = await service.get_user_by_email(email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=NOT_FOUND_USER_MESSAGE,
            )
        await service.change_password_by_user(user, new_password)

        redirect = await get_redirect_with_authentication_user(user)
        return redirect

    except Exception as e:
        logger.error("Reset password failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при смене пароля",
        )
