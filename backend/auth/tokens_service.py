import logging

import jwt
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status

from backend.core.config import settings
from backend.exceptions.custom_token_exceptions import InvalidTokenError

logging.basicConfig(
    format=settings.logging.log_format, level=settings.logging.log_level_value
)
logger = logging.getLogger(__name__)


class TokenService:
    @classmethod
    def create_access_token(
        cls, data: dict, expires_delta: timedelta | None = None
    ) -> str:
        """
        Создает новый Access Token.

        :param data: Данные для кодирования в токене.
        :param expires_delta: Время жизни токена.
        :return: Новый Access Token
        """
        data["type"] = "access"
        expires_delta = expires_delta or timedelta(
            minutes=settings.jwt.access_token_expire_minutes
        )
        return cls._create_jwt_token(data, expires_delta)

    @classmethod
    def refresh_access_token(cls, refresh_token: str) -> str:
        """
        Обновляет Access Token на основе Refresh Token.

        :param refresh_token: Токен обновления.
        :return: Новый Access Token.
        :raise ValueError: Если Refresh Token недействителен.
        :raise HTTPException: Если передан неверный тип токена.
        """
        payload = cls.decode_and_validate_token(refresh_token)
        if payload.get("type") == "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        username = payload.get("sub")
        if not username:
            raise ValueError("Invalid refresh token")
        # Создаем новый Access Token
        new_access_token = cls.create_access_token(data={"sub": username})
        logger.info(f"Access Token успешно обновлен для пользователя: {username}")
        return new_access_token

    @classmethod
    def create_refresh_token(cls, data: dict) -> str:
        """
        Создает новый Refresh Token.

        :param data: Данные для кодирования в токене.
        :return: Новый Refresh Token.
        """
        data["type"] = "refresh"
        expires_delta = timedelta(days=settings.jwt.refresh_token_expire_days)
        return cls._create_jwt_token(data, expires_delta)

    @classmethod
    def _create_jwt_token(cls, data: dict, expires_delta: timedelta) -> str:
        """
        Создает JWT-токен.

        :param data: Данные для кодирования в токене.
        :param expires_delta: Время жизни токена.
        :return: Новый JWT-токен.
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": int(expire.timestamp())})

        if not settings.jwt.secret_key or not settings.jwt.algorithm:
            raise ValueError(
                "SECRET_KEY и ALGORITHM должны быть настроены в конфигурации."
            )

        try:
            encoded_jwt = jwt.encode(
                to_encode, settings.jwt.secret_key, algorithm=settings.jwt.algorithm
            )
        except Exception as e:
            raise RuntimeError(f"Ошибка при создании JWT Token: {e}")

        return encoded_jwt

    @classmethod
    def decode_and_validate_token(cls, token: str) -> dict:
        """
        Декодирует и проверяет JWT-токен.

        :param token: JWT-токен.
        :return: Payload токена.
        """

        payload = cls._decode_token(token)
        return payload

    @classmethod
    def _decode_token(cls, token: str) -> dict:
        """
        Декодирует JWT-токен.

        :param token: JWT-токен.
        :return: Payload токена.
        :raises HTTPException: 401 если токен недействителен.
        """
        try:
            return jwt.decode(
                token, settings.jwt.secret_key, algorithms=[settings.jwt.algorithm]
            )
        except jwt.ExpiredSignatureError:
            logger.warning("Токен истек")
            raise HTTPException(status_code=401, detail="Token expired")

    @classmethod
    def is_token_valid(cls, token: str) -> bool:
        """
        Проверяет валидность токена.

        :param token: Токен
        :return: True если токен валидный, иначе False
        """
        try:
            cls.decode_and_validate_token(token)
            return True
        except jwt.InvalidTokenError:
            raise InvalidTokenError()
        except HTTPException:
            return False
