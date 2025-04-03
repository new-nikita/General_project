from datetime import datetime, timedelta
import jwt
from jwt.exceptions import PyJWTError
from core.config import settings
import logging

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

    expire = datetime.utcnow() + timedelta(days=settings.jwt.refresh_token_expire_days)
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
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
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
    if not refresh_token:
        logger.warning("Refresh token is None")
        raise ValueError("Refresh token is None")

    try:
        # Декодируем Refresh Token
        payload = jwt.decode(
            refresh_token, settings.jwt.secret_key, algorithms=[settings.jwt.algorithm]
        )
    except PyJWTError as e:
        logger.warning(f"Недействительный Refresh Token: {e}")
        raise ValueError("Invalid refresh token")

    username = payload.get("sub")
    exp = payload.get("exp")

    if not username or (exp and exp < int(datetime.utcnow().timestamp())):
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
        if exp and exp < int(datetime.utcnow().timestamp()):
            logger.warning("Token expired")
            raise ValueError("Token expired")
        return payload
    except PyJWTError as e:
        logger.warning(f"Недействительный токен: {e}")
        raise ValueError("Invalid token")
