import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status

from backend.auth.Celery.tasks import send_confirmation_email_task
from backend.auth.dependencies import get_email_token_store
from backend.auth.stores.email_token_store import EmailTokenRedisStore
from backend.auth.schemas.reset_password_schema import (
    MessageResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)

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


# @router.get(
#     "/forgot_password",
#     tags=["auth"],
#     response_class=HTMLResponse,
# )
# def request_reset_form(request: Request):
#     """Форма запроса сброса пароля."""
#     return settings.templates.template_dir.TemplateResponse(
#         "users/forgot_password.html",
#         {"request": request},
#     )


# Обработка запроса на сброс
@router.post(
    "/forgot_password",
    response_model=MessageResponse,
    tags=["auth"],
)
async def request_reset(
    request: Request,
    data: ForgotPasswordRequest,
    service: Annotated[UserService, Depends(get_user_service)],
    redis: Annotated[EmailTokenRedisStore, Depends(get_email_token_store)],
):
    """Ендпоинт восстановления пароля.

    :param request: Запрос FastAPI
    :param service: Сервис работы с данными пользователя
    :param redis: Временное бд для отложенных задач
    :return: JSON
    """

    try:
        await service.get_user_by_email(data.email)
        reset_token = str(uuid.uuid4())  # одноразовый токен

        await redis.save_pending_disposable_token(reset_token, data.email)

        send_confirmation_email_task.delay(
            "reset_password",
            "message_reset_password",
            data.email,
            reset_token,
            str(request.base_url),
        )

        return {
            "message": "Ссылка для сброса пароля отправлена",
            "success": True,
        }

    except Exception as e:
        logger.error("Reset failed: %s", e)
    raise HTTPException(status_code=500, detail="Не удалось отправить email")


# @router.get("/reset_password", tags=["auth"], response_class=HTMLResponse)
# async def reset_password_form(
#     request: Request,
#     token: str,
#     redis: Annotated[EmailTokenRedisStore, Depends(get_email_token_store)],
# ) -> HTMLResponse:
#     """Страница сброса пароля."""
#     try:
#         await redis.connect()
#         await redis.get_pending_token(token)
#
#         return settings.templates.template_dir.TemplateResponse(
#             "users/reset_password.html",
#             {"request": request, "token": token},
#         )
#
#     except HTTPException:
#         logger.error("Reset password failed")
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Неверный или истекший токен",
#         )


# Обработка сброса
@router.post("/reset_password", tags=["auth"])
async def reset_password(
    data: ResetPasswordRequest,
    service: Annotated[UserService, Depends(get_user_service)],
    redis: Annotated[EmailTokenRedisStore, Depends(get_email_token_store)],
):
    try:
        if data.new_password != data.confirm_password:
            raise HTTPException(status_code=400, detail="Пароли не совпадают")

        email = await redis.get_pending_token(data.token)
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
        await service.change_password_by_user(user, data.new_password)

        return {"message": "Пароль успешно изменен", "success": True}

    except Exception as e:
        logger.error("Reset password failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при смене пароля",
        )
