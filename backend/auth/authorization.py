import logging
from typing import Annotated

from fastapi import Cookie, HTTPException, status, Depends, Request, WebSocket
from fastapi.responses import Response, RedirectResponse

from backend.core.config import settings
from backend.core.models import User
from backend.users.services import UserService
from backend.users.password_helper import PasswordHelper, PasswordVerificationError
from backend.users.dependencies import get_user_service
from backend.auth.tokens_service import TokenService


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
    user = await service.get_user_by_username(username)
    if not user:
        handle_auth_error(message="Неверный username или пароль.")

    if not PasswordHelper.verify_password(password, user.hashed_password):
        handle_auth_error(
            message=str(PasswordVerificationError().message),
            status_code=PasswordVerificationError().status_code,
        )

    if not user.is_active:
        handle_auth_error(
            message="Учетная запись заблокирована, либо слишком давно не была активна.",
            status_code=status.HTTP_403_FORBIDDEN,
        )
    logger.info(f"Successful login for user: {username}")
    return user


async def get_current_user_from_cookie(
    request: Request,
    service: Annotated[UserService, Depends(get_user_service)],
    access_token: str | None = Cookie(default=None, alias="access-token"),
) -> User | Response | None:
    """
    Получает текущего пользователя по JWT-токену из cookies.

    :param request: Запрос FastAPI.
    :param access_token: JWT-токен доступа из cookies.
    :param service: Сервис для работы с пользователями.
    :return: Текущий пользователь.
    """
    if hasattr(request.state, "new_access_token"):
        access_token = request.state.new_access_token

    if not access_token:
        return

    try:
        payload: dict = TokenService.decode_and_validate_token(access_token)
    except HTTPException as e:
        return Response(status_code=e.status_code, content={"message": e.detail})

    username: str = payload.get("sub")
    user: User = await get_user_by_username_from_service(username, service)
    return user


async def get_current_user_ws(
    websocket: WebSocket,
    service: Annotated[UserService, Depends(get_user_service)],
) -> User | None:

    access_token = websocket.cookies.get("access-token")

    if not access_token:
        return None

    payload = TokenService.decode_and_validate_token(access_token)
    username = payload.get("sub")

    return await get_user_by_username_from_service(username, service)


async def get_user_by_username_from_service(
    username: str, service: UserService
) -> User:
    """
    Получает пользователя из сервиса по имени пользователя.

    :param username: Имя пользователя.
    :param service: Сервис для работы с пользователями.
    :return: Пользователь.
    :raises HTTPException: 401 если пользователь не найден.
    """
    user = await service.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
