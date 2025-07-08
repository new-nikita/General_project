import logging

import redis.asyncio as redis
from fastapi import HTTPException

from backend.core.config import settings
from backend.exceptions.token_exceptions import NotFoundTokenWithEmailInRedis

logging.basicConfig(
    format=settings.logging.log_format, level=settings.logging.log_level_value
)

logger = logging.getLogger(__name__)


class AsyncRedisClient:
    """Класс для временной работы хранения токенов при авторизации через
    ссылку."""

    def __init__(self) -> None:
        self.redis_url = (
            f"redis://{settings.redis.host}:{settings.redis.port}/{settings.redis.db}"
        )
        self.r = None

    async def connect(self) -> None:
        """Создаёт подключение к Redis."""
        try:
            self.r = redis.from_url(self.redis_url, decode_responses=True)
            compound = await self.r.ping()  # проверка на подключение
            if compound:
                logger.info("Установлено подключение к Redis")
        except Exception as e:
            logger.error("Ошибка при подключении к Redis: %s", e)
            raise

    async def save_pending_email_token(
        self,
        token: str,
        email: str,
        expires_sec: int = 1800,
    ) -> bool:
        """Добавляет в базу данных Redis сроком в (30 минут)

        :param token: Токен для авторизации пользователя (будет
            отправлен в письмо пользователю на почту в виде ссылки)
        :param email: Email переданный пользователем в Form
        :param expires_sec: Срок жизни записи в Redis (по умолчанию 30
            минут)
        :return bool:
        """
        try:
            # setex: устанавливает срок жизни записи
            await self.r.setex(token, expires_sec, email)
            logger.info("Сохранён токен: %s -> %s", email, token)
            return True
        except Exception as e:
            logger.error("Redis error (save_email): %s", e)
            return False

    async def save_pending_disposable_token(
        self,
        token: str,
        email: str,
        expires_sec: int = 600,
    ) -> bool:
        """Добавляет в базу данных Redis сроком в (30 минут)

        :param token: Токен для авторизации пользователя (будет
            отправлен в письмо пользователю на почту в виде ссылки)
        :param email: Email переданный пользователем в Form
        :param expires_sec: Срок жизни записи в Redis (по умолчанию 30
            минут)
        :return bool:
        """
        try:
            await self.r.setex(token, expires_sec, email)
            logger.info(f"Сохранён одноразовый токен: {email} -> {token}")
            return True
        except Exception as e:
            logger.error("Redis error (save_email): %s", e)
            return False

    async def get_pending_token(self, token: str) -> str | None:
        """Извлекает значение по ключу из Redis.

        :param token: Токен из ссылки отправленный пользователю на
            почту.
        :return str: Возвращает email пользователя если он найден.
        """
        try:
            val = await self.r.get(token)
            if val is not None:
                return val
            logger.info("Токен не найден: %s", token)
            raise NotFoundTokenWithEmailInRedis
        except Exception as e:
            logger.error("Redis error (get): %s", e, exc_info=True)
            raise HTTPException(status_code=500, detail="Что-то пошло не так")

    async def delete_pending_token(self, token: str) -> bool:
        """Удаляет ключ из Redis если пользователь перешел по ссылке.

        :param token: Токен из ссылки отправленный пользователю на почту
        :return: TRUE если пользователь перешел по ссылке и
            авторизовался FALSE если пользователь не найден или Redis не
            отвечает
        """
        try:
            deleted = await self.r.delete(token) > 0
            if deleted:
                logger.debug("Токен удалён: %s", token)
                return True
            else:
                logger.info("Токен не найден при удалении: %s", token)
                return False
        except Exception as e:
            logger.error("Redis error (delete): %s", e)
            return False

    async def token_exists(self, token: str) -> bool:
        """Проверяет, существует ли ключ в Redis.

        :param token: Token пользователя
        :return: Возвращает TRUE если пользователь найден FALSE если
            пользователя нет или Redis не отвечает
        """
        try:
            exists = await self.r.exists(token) == 1
            logger.info("Проверка токена: %s -> %s", token, exists)
            if exists:
                return True
            return False
        except Exception as e:
            logger.error("Redis error (exists): %s", e)
            return False
