import logging

from backend.core.config import settings


logging.basicConfig(
    format=settings.logging.log_format, level=settings.logging.log_level_value
)
logger = logging.getLogger(__name__)


class TokenStore:
    _store: dict[str, str] = {}

    @classmethod
    def save(cls, jti: str, user_id: int):
        cls._store[jti] = user_id

    @classmethod
    def exists(cls, jti: str) -> bool:
        return jti in cls._store

    @classmethod
    def delete(cls, jti: str):
        cls._store.pop(jti, None)
