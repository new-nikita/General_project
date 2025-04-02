import logging

import jwt
from jwt import PyJWTError
from fastapi import Cookie, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from core.config import settings
from users.services import UserService, get_service
from core.models import User
from users.password_helper import PasswordHelper, PasswordVerificationError


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

logging.basicConfig(
    format=settings.logging.log_format, level=settings.logging.log_level_value
)
logger = logging.getLogger(__name__)


def handle_auth_error(
    message: str = "Incorrect username or password",
    status_code: int = status.HTTP_401_UNAUTHORIZED,
):
    logger.error(message)
    raise HTTPException(
        status_code=status_code, detail=message, headers={"WWW-Authenticate": "Bearer"}
    )


async def authenticate_user(service: UserService, username: str, password: str) -> User:
    """
    Аутентифицирует пользователя по имени пользователя и паролю.

    Args:
        service: Сервис для работы с пользователями
        username: Имя пользователя
        password: Пароль

    Returns:
        User: пользователь из бд

    Raises:
        HTTPException: 401 если неверные учетные данные
        HTTPException: 500 при внутренних ошибках сервера
    """
    try:
        user = await service.get_user_by_username(username)

        if not user:
            logger.warning(f"Login attempt for non-existent user: {username}")
            handle_auth_error()

        if not user.is_active:
            logger.warning(f"Login attempt for inactive user: {username}")
            handle_auth_error("Account is disabled", status.HTTP_403_FORBIDDEN)

        PasswordHelper.verify_password(password, user.hashed_password)

        logger.info(f"Successful login for user: {username}")
        return user

    except PasswordVerificationError as e:
        logger.warning(f"Invalid password attempt for user: {username}")
        handle_auth_error()

    except Exception as e:
        logger.critical(
            f"Authentication error for user {username}: {str(e)}", exc_info=True
        )
        handle_auth_error(
            "Internal authentication error", status.HTTP_500_INTERNAL_SERVER_ERROR
        )


async def get_current_user(
    access_token: str = Cookie(None), service: UserService = Depends(get_service)
):
    """
    Проверяет JWT-токен из HTTP-Only cookie и возвращает текущего пользователя.

    Args:
        access_token: JWT-токен из cookie
        service: Сервис для работы с пользователями

    Returns:
        User: Текущий пользователь

    Raises:
        HTTPException: Если токен недействителен или пользователь не найден
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not access_token:
        raise credentials_exception

    try:
        # Удаляем префикс "Bearer " из токена
        token = access_token.replace("Bearer ", "")
        payload = jwt.decode(
            token, settings.jwt.secret_key, algorithms=[settings.jwt.algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception

    user = await service.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user
