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


def get_redis_client() -> AsyncRedisClient:
    return AsyncRedisClient()


@router.post(
    "/initial_register",
    tags=["auth"],
    response_model=MessageResponse,
)
async def initial_register_user(
    request: Request,
    data: InitialRegisterRequest,
    redis: Annotated[AsyncRedisClient, Depends(get_redis_client)],
):
    """Отправляет письмо с подтверждением регистрации на указанный email.

    :param data: Email
    :param redis: Объект для работы с Redis.
    :return: JSON.
    """
    try:
        temporary_user_token = TokenService.create_refresh_token({"sub": data.email})
        await redis.connect()
        await redis.save_pending_email_token(temporary_user_token, data.email)

        # Отправка письма через Celery
        send_confirmation_email_task.delay(
            "register",
            "initial_message",
            data.email,
            temporary_user_token,
            str(request.base_url),
            data.client,
        )

        return {"message": "Confirmation email sent"}

    except Exception:
        raise HTTPException(status_code=500, detail="Registration init failed")


@router.get(
    "/register/confirm",
    tags=["auth"],
    response_model=MessageResponse,
)
async def confirm_registration_token(
    token: str,
    redis: Annotated[AsyncRedisClient, Depends(get_redis_client)],
):
    """Проверяет токен из письма и возвращает подтверждённый email."""
    try:
        payload = TokenService.decode_and_validate_token(token)
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=400, detail="Invalid token")

        await redis.connect()
        if not await redis.token_exists(token):
            raise HTTPException(
                status_code=400,
                detail="Link expired or already used",
            )

        stored_email = await redis.get_pending_token(token)
        if stored_email != email:
            raise HTTPException(status_code=400, detail="Invalid token")

        return {"message": "Email confirmed", "email": email}
    except HTTPException:
        raise
    except Exception as e:
        logger.warning("Registration token confirm failed: %s", e)
        raise HTTPException(status_code=400, detail="Invalid or expired token")


@router.post("/register", tags=["auth"], response_model=MessageResponse)
async def register_user(
    response: Response,
    form_data: RegisterRequest,
    service: Annotated[UserService, Depends(get_user_service)],
):
    """Обрабатывает регистрацию нового пользователя."""
    try:
        # Сначала создаем пользователя без аватара
        profile_data = form_data.model_dump(
            exclude={"username", "password", "password2", "email", "avatar"}
        )
        if not profile_data.get("first_name"):
            profile_data["first_name"] = form_data.first_name or form_data.username
        if not profile_data.get("last_name"):
            profile_data["last_name"] = form_data.last_name or ""
        profile = ProfileCreate(**profile_data)

        user_create = UserCreate(
            username=form_data.username,
            password=form_data.password,
            email=form_data.email,
            profile=profile,
        )

        # Создаем пользователя и сразу делаем flush, чтобы получить ID
        user = await service.create_user_and_added_in_db(user_create)
        await service.repository.session.commit()

        logger.info(f"New user registered: {user.username}")

        await TokenCookieService.set_auth_cookies(response, user)

        return {
            "message": "User registered successfully",
            "user_id": user.id,
        }

    except ValueError as e:
        await service.repository.session.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        await service.repository.session.rollback()
        logger.exception("Registration failed: %s", e)
        raise HTTPException(status_code=500, detail="Registration failed")
