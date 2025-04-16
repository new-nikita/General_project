import redis
import logging
from core.config import settings


logging.basicConfig(
    format=settings.logging.log_format, level=settings.logging.log_level_value
)

logger = logging.getLogger(__name__)


class RedisClient:
    def __init__(self, host=settings.redis.host, port=settings.redis.port, db=settings.redis.db):
        self.connect = redis.Redis(host=host, port=port, db=db)

    # сохранение клиента и его токена доступа
    def set_redis_client(self, client, token):
        self.connect.set(client, token)

    def set_redis_count_token(self, client, token):
        self.connect.set(client, token)

    # получение токена по уникальному user_name клиента
    def get_redis_client(self, client):
        return self.connect.get(client)

    # удаление клиента
    def delete_redis_client(self, client):
        self.connect.delete(client)









