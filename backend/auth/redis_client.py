import redis.asyncio as redis
import logging
import json
from backend.core.config import settings
from typing import Optional

logging.basicConfig(
    format=settings.logging.log_format, level=settings.logging.log_level_value
)

logger = logging.getLogger(__name__)


class AsyncRedisClient:
    """Класс для временной работы хранения токенов при авторизации через ссылку"""

    def __init__(self):
        self.redis_url = f"redis://{settings.redis.host}:{settings.redis.port}/0"
        self.r = None

    async def connect(self):
        """Создаёт подключение к Redis"""
        try:
            self.r = redis.from_url(self.redis_url, decode_responses=True)
            logger.info("Установлено подключение к Redis")
        except Exception as e:
            logger.error(f"Ошибка при подключении к Redis: {e}")
            raise

    async def save_pending_email_token(
        self, data, token: str, expires_sec: int = 1800
    ) -> bool:
        """
        :param token: Токен для авторизации пользователя (будет отправлен в письмо пользователю на почту в виде ссылки)
        :param email: Email переданный пользователем в Form
        :param expires_sec: Срок жизни записи в Redis (по умолчанию 30 минут)
        :return:
        """
        try:

            await self.r.setex(token, expires_sec, json.dumps(data))
            """
            setex: устанавливает срок жизни записи 
            """
            logger.info(f"Сохранён токен: {data["username"]} -> {token}")
            return True
        except Exception as e:
            logger.error(f"Redis error (save): {e}")
            return False

    async def get_pending_token(self, token: str) -> Optional[dict]:
        """
        Извлекает значение по ключу из Redis
        :param token: токен из ссылки отправленный пользователю на почту
        :return: возвращает значения по Токену
        """
        try:
            val = await self.r.get(token)
            if val:
                logger.info(f"Токен получен: {token}")
                return json.loads(val)
            logger.info(f"Токен не найден: {token}")
            return

        except Exception as e:
            logger.error(f"Redis error (get): {e}")
            return

    async def delete_pending_token(self, token: str) -> bool:
        """
        Удаляет ключ из Redis если пользователь перешел по ссылке
        :param token: Токен из ссылки отправленный пользователю на почту
        :return: TRUE если пользователь перешел по ссылке и авторизовался
                FALSE если пользователь не найден или Redis не отвечает
        """
        try:
            deleted = await self.r.delete(token) > 0
            if deleted:
                logger.debug(f"Токен удалён: {token}")
                return True
            else:
                logger.info(f"Токен не найден при удалении: {token}")
                return False
        except Exception as e:
            logger.error(f"Redis error (delete): {e}")
            return False

    async def token_exists(self, token: str) -> bool:
        """
        Проверяет, существует ли ключ в Redis
        :param token: Token пользователя
        :return: Возвращает TRUE если пользователь найден
                             FALSE если пользователя нет или Redis не отвечает
        """
        try:
            exists = await self.r.exists(token) == 1
            logger.debug(f"Проверка токена: {token} -> {exists}")
            if exists:
                return True
        except Exception as e:
            logger.error(f"Redis error (exists): {e}")
            return False
