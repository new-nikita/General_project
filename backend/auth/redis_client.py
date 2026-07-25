"""Обратная совместимость. Используйте EmailTokenRedisStore."""

from backend.auth.stores.email_token_store import EmailTokenRedisStore as AsyncRedisClient

__all__ = ("AsyncRedisClient",)
