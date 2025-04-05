import logging

import jwt
from jwt import PyJWTError
from fastapi import Cookie, HTTPException, status, Depends, Request, Header
from fastapi.security import OAuth2PasswordBearer

from core.config import settings
from users.services import UserService
from core.models import User
from users.password_helper import PasswordHelper, PasswordVerificationError
from users.dependencies import get_user_service
from users.tokens import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

logging.basicConfig(
    format=settings.logging.log_format, level=settings.logging.log_level_value
)
logger = logging.getLogger(__name__)


def handle_auth_error(
    message: str = "Incorrect username or password",
    status_code: int = status.HTTP_401_UNAUTHORIZED,
):
    """
    Обрабатывает ошибки аутентификации.

    :param message: Сообщение об ошибке.
    :param status_code: Код состояния HTTP.
    :raises HTTPException: Исключение FastAPI с указанным сообщением и кодом.
    """
    logger.error(message)
    raise HTTPException(
        status_code=status_code, detail=message, headers={"WWW-Authenticate": "Bearer"}
    )


async def authenticate_user(service: UserService, username: str, password: str) -> User:
    """
    Аутентифицирует пользователя по имени пользователя и паролю.

    :param service: Сервис для работы с пользователями.
    :param username: Имя пользователя.
    :param password: Пароль.
    :return: Пользователь из базы данных.
    :raises HTTPException: 401 если неверные учетные данные.
    :raises HTTPException: 403 если аккаунт заблокирован.
    :raises HTTPException: 500 при внутренних ошибках сервера.
    """
    try:
        user = await service.get_user_by_username(username)
        if not user:
            logger.warning(f"Login attempt for non-existent user: {username}")
            handle_auth_error(message="Incorrect username")
        try:
            PasswordHelper.verify_password(password, user.hashed_password)
        except PasswordVerificationError as e:
            logger.warning(f"Invalid password attempt for user: {username}")
            handle_auth_error(message=str(e), status_code=status.HTTP_401_UNAUTHORIZED)
        if not user.is_active:
            logger.warning(f"Login attempt for inactive user: {username}")
            handle_auth_error("Account is disabled", status.HTTP_403_FORBIDDEN)

        logger.info(f"Successful login for user: {username}")
        return user

    except Exception as e:
        logger.critical(
            f"Authentication error for user {username}: {str(e)}", exc_info=True
        )
        handle_auth_error(
            "Internal authentication error", status.HTTP_500_INTERNAL_SERVER_ERROR
        )


async def get_current_user(
    request: Request,
    access_token: str = Cookie(None),
    refresh_token: str = Cookie(None),
    service: UserService = Depends(get_user_service),
) -> User:
    """
    Получает текущего пользователя по токенам из cookies.

    :param request: Запрос FastAPI.
    :param access_token: JWT-токен доступа из cookies.
    :param refresh_token: JWT-токен обновления из cookies.
    :param service: Сервис для работы с пользователями.
    :return: Текущий пользователь.
    :raises HTTPException: 401 если пользователь не аутентифицирован.
    """
    if not access_token and not refresh_token:
        logger.warning("Access token и Refresh token отсутствуют")
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        if access_token:
            token = (
                access_token[7:] if access_token.startswith("Bearer ") else access_token
            )
    except ValueError as e:
        logger.warning(f"Ошибка при получении текущего пользователя: {e}")
        handle_auth_error(status_code=401, message="Not authenticated")
        payload = decode_token(token)
        username = payload.get("sub")
        if username:
            user = await service.get_user_by_username(username)
            if user:
                return user

    raise HTTPException(status_code=401, detail="Not authenticated")


async def get_current_user_from_cookie(
    request: Request,
    access_token: str | None = Cookie(default=None, alias="access_token"),
    service: UserService = Depends(get_user_service),
) -> User:
    """
    Получает текущего пользователя по JWT-токену из cookies.

    :param request: Запрос FastAPI.
    :param access_token: JWT-токен доступа из cookies.
    :param service: Сервис для работы с пользователями.
    :return: Текущий пользователь.
    :raises HTTPException: 401 если токен недействителен или пользователь не найден.
    """
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Удаляем "Bearer " из начала токена
    token = access_token[7:] if access_token.startswith("Bearer ") else access_token

    try:
        payload = jwt.decode(
            token, settings.jwt.secret_key, algorithms=[settings.jwt.algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await service.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
