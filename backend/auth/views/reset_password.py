import logging
from datetime import date
from typing import Annotated

import uuid
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Request,
    Response,
    Form,
)
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import EmailStr

from backend.auth.tokens_service import TokenService
from backend.auth.Celery.tasks import send_confirmation_email_task
from backend.core.config import settings

from backend.auth import AsyncRedisClient, authorization
from backend.auth.authorization import get_redirect_with_authentication_user


from backend.users.dependencies import get_user_service
from backend.users.services import UserService


logging.basicConfig(
    format=settings.logging.log_format, level=settings.logging.log_level_value
)
logger = logging.getLogger(__name__)


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

templates = Jinja2Templates(directory=settings.template_dir / "users")
templates2 = Jinja2Templates(directory=settings.template_dir / "info")


# Форма запроса сброса
@router.get("/forgot_password", response_class=HTMLResponse)
def request_reset_form(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request, "current_user": None})


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
        await redis.save_pending_email_token(reset_token, email, expires_sec=600)

        send_confirmation_email_task.delay('reset_password', email, reset_token, str(request.base_url))

        RedirectResponse(url="/further_actions", status_code=303)
        return templates2.TemplateResponse('further_actions.html', {'request': request})

    except Exception as e:
        logger.error(f"Reset failed: {e}")
        return templates.TemplateResponse(
            "forgot_password.html",
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
        email = await redis.get_pending_token(token)

        return templates.TemplateResponse("reset_password.html", {"request": request, "email": email})

    except HTTPException(status_code=400, detail="Неверный или истекший токен"):
        logger.error(f"Reset password failed")


# Обработка сброса
@router.post("/reset_password")
async def reset_password(
        email: EmailStr,
        service: Annotated[UserService, Depends(get_user_service)],
        new_password: str = Form(...),
        new_password2: str = Form(...),
):
    """
    Установление нового пароля

    :param email: Email из временной бд Redis
    :param new_password: Новый пароль
    :param new_password2: Подтверждение нового пароля
    :param service: Сервис работы с пользователями
    :return: Страницу пользователя
    """

    try:
        if new_password == new_password2:   # TODO подумать как можно это лучше сделать

            user = await service.get_user_by_email(email)
            await service.change_password_by_user(user, new_password)

            redirect = await get_redirect_with_authentication_user(user)
            return redirect

    except Exception as e:
        logger.error(f"Reset password failed: {e}")






