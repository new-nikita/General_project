from datetime import timedelta, datetime, timezone
import logging
from typing import Any

import jwt
from fastapi import HTTPException
from jwt.exceptions import PyJWTError
from fastapi.responses import Response

from core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_refresh_token(data: dict) -> str:
    """
    Создает новый Refresh Token.

    :param data: Данные для кодирования в токене.
    :return: Новый Refresh Token.
    """
    if not settings.jwt.secret_key or not settings.jwt.algorithm:
        raise ValueError("SECRET_KEY и ALGORITHM должны быть настроены в конфигурации.")

    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.jwt.refresh_token_expire_days
    )
    data.update({"exp": expire})
    try:
        encoded_jwt = jwt.encode(
            data, settings.jwt.secret_key, algorithm=settings.jwt.algorithm
        )
    except PyJWTError as e:
        logger.error(f"Ошибка при создании Refresh Token: {e}")
        raise RuntimeError(f"Ошибка при создании Refresh Token: {e}")

    return encoded_jwt


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Создает новый Access Token.

    :param data: Данные для кодирования в токене.
    :param expires_delta: Время жизни токена.
    :return: Новый Access Token.
    """
    if not settings.jwt.secret_key or not settings.jwt.algorithm:
        raise ValueError("SECRET_KEY и ALGORITHM должны быть настроены в конфигурации.")

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.jwt.access_token_expire_minutes
        )
    to_encode.update({"exp": expire})
    try:
        encoded_jwt = jwt.encode(
            to_encode, settings.jwt.secret_key, algorithm=settings.jwt.algorithm
        )
    except PyJWTError as e:
        logger.error(f"Ошибка при создании Access Token: {e}")
        raise RuntimeError(f"Ошибка при создании Access Token: {e}")

    return encoded_jwt


def refresh_access_token(refresh_token: str) -> str:
    """
    Обновляет Access Token на основе Refresh Token.

    :param refresh_token: Токен обновления.
    :return: Новый Access Token.
    :raises ValueError: Если Refresh Token недействителен.
    """
    payload = decode_token(refresh_token)
    username = payload.get("sub")
    exp = payload.get("exp")

    if not username or (exp and exp < int(datetime.now(timezone.utc).timestamp())):
        logger.warning("Refresh Token истек или содержит некорректные данные")
        raise ValueError("Invalid refresh token")

    # Создаем новый Access Token
    new_access_token = create_access_token(data={"sub": username})
    logger.info(f"Access Token успешно обновлен для пользователя: {username}")
    return new_access_token


def decode_token(token: str) -> dict:
    """
    Декодирует JWT-токен и проверяет его срок действия.

    :param token: JWT-токен.
    :return: Payload токена.
    :raises ValueError: Если токен недействителен.
    """
    if not token:
        logger.warning("Token is None")
        raise ValueError("Token is None")

    try:
        payload = jwt.decode(
            token, settings.jwt.secret_key, algorithms=[settings.jwt.algorithm]
        )
        exp = payload.get("exp")
        if exp and exp < int(datetime.now(timezone.utc).timestamp()):
            logger.warning("Token expired")
            raise ValueError("Token expired")
        return payload
    except PyJWTError as e:
        logger.warning(f"Недействительный токен: {e}")
        raise ValueError("Invalid token")


def set_access_token_to_cookie(access_token: str, response: Response) -> None:
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        samesite="lax",
        max_age=settings.jwt.access_token_expire_minutes * 60,
    )


def set_refresh_token_to_cookie(refresh_token: str, response: Response) -> None:
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        max_age=settings.jwt.refresh_token_expire_days * 24 * 60 * 60,
    )


def decode_and_validate_token(token: str) -> dict:
    """
    Декодирует и проверяет JWT-токен.

    :param token: JWT-токен.
    :return: Payload токена.
    :raises HTTPException: 401 если токен недействителен.
    """
    payload = decode_token(token)
    validate_token(payload)
    return payload


def validate_token(
    payload: dict[str, Any],
) -> bool:
    if not payload.get("sub") or not payload.get("exp"):
        raise HTTPException(status_code=401, detail="Invalid token")
    return True
