import redis
import logging
from core.config import settings


logging.basicConfig(
    format=settings.logging.log_format, level=settings.logging.log_level_value
)

logger = logging.getLogger(__name__)


class RedisClient:
    """Класс для работы с токен-доступом"""

    def __init__(self, host=settings.redis.host, port=settings.redis.port, db=settings.redis.db):
        self.connect = redis.Redis(host=host, port=port, db=db)

    # сохранение клиента и его токена доступа
    def set_redis_client(self, client, token):
        """
        :param client: Id пользователя
        :param token: access токен
        """
        self.connect.set(client, token)
        logger.warning(f'REDIS: Пользователь {client}, создан')

    def set_redis_count_token(self, client, token):
        """
        :param client: Id пользователя
        :param token: access токен Нового устройства
        :return:
        """
        # Проверка на количество токенов
        if self.get_redis_client():
            ...


        self.connect.set(client, token)
        logger.warning(f'REDIS: Пользователь: {client}, авторизовался на новом устройстве')

    # получение токена по уникальному user_name клиента
    def get_redis_client(self, client):
        """
        :param client: Id пользователя
        :return: Возвращает токен пользователя
        """
        return self.connect.get(client)

    # удаление клиента
    def delete_redis_client(self, client):
        """
        :param client: Id пользователя
        :return: Удаляет пользователя по id
        """
        self.connect.delete(client)
        logger.warning(f'REDIS: Удаление пользователя: {client}')









