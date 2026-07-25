import logging
from typing import Annotated, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from pydantic import EmailStr, ValidationError

from backend.auth.authorization import get_current_user_from_cookie
from backend.auth.Celery.tasks import send_confirmation_email_task
from backend.auth.redis_client import AsyncRedisClient
from backend.auth.tokens_service import TokenService
from backend.auth.token_cookie_service import TokenCookieService
from backend.auth.schemas.register_schemas import (
    MessageResponse,
    InitialRegisterRequest,
    RegisterRequest,
)
from backend.core.config import settings
from backend.core.models import User
from backend.users.dependencies import get_user_service
from backend.users.schemas.register_schema import RegisterForm
from backend.users.schemas.users_schemas import ProfileCreate, UserCreate
from backend.users.services import UserService
from backend.utils.save_images import upload_image

logging.basicConfig(
    format=settings.logging.log_format, level=settings.logging.log_level_value
)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/initial_register",
    tags=["auth"],
    response_class=HTMLResponse,
)
async def get_initial_register_page(
    request: Request,
    current_user: Annotated[
        Optional[User], Depends(get_current_user_from_cookie)
    ] = None,
) -> Response:
    """Возвращает данные пользователя, если он уже авторизован

    :param request: Запрос FastAPI.
    :param current_user: Текущий пользователь (если авторизован).
    :return: JSON-данные пользователя (если авторизован).
    """
    # Если пользователь уже авторизован, перенаправляем на главную
    if current_user:
        return current_user
    else:
        return


@router.get("/register", tags=["auth"], response_class=HTMLResponse)
async def get_register_page(
    request: Request,
    token: Optional[str] = None,
    current_user: Annotated[
        Optional[User], Depends(get_current_user_from_cookie)
    ] = None,
) -> Response:
    """Отображает страницу регистрации нового пользователя.

    А также принимает токен для подтверждения регистрации по email. Если
    токен не указан, то отображается форма для ввода данных, в которой
    не возможно ввести email.
    :param request: Запрос FastAPI.
    :param token: Токен подтверждения регистрации.
    :param current_user: Пользователь, если он уже авторизован.
    :return: HTML-страница с формой регистрации.
    """
    if current_user:
        return current_user
    form_data = {}
    if token:
        try:
            payload = TokenService.decode_and_validate_token(token)
            email = payload.get("sub")
            if email:
                form_data["email"] = email
        except Exception as e:
            logger.warning(f"Ошибка при декодировании токена: {e}")
