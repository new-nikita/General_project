import logging

from fastapi.responses import Response

from backend.core.config import settings
from backend.core.models import User
from backend.auth.tokens_service import TokenService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TokenCookieService:
    @classmethod
    def set_access_token_to_cookie(
        cls,
        access_token: str,
        response: Response,
    ) -> None:
        """Добавление access_token в cookie"""

        response.set_cookie(
            key="access-token",
            value=access_token,
            httponly=True,
            samesite="lax",
            max_age=settings.jwt.access_token_expire_minutes * 60,
        )

    @classmethod
    def set_refresh_token_to_cookie(
        cls, refresh_token: str, response: Response
    ) -> None:
        """Добавление refresh_token в cookie"""

        response.set_cookie(
            key="refresh-token",
            value=refresh_token,
            httponly=True,
            samesite="lax",
            secure=True,
            max_age=settings.jwt.refresh_token_expire_days * 24 * 60 * 60,
        )

    @classmethod
    async def set_auth_cookies(cls, response: Response, user: User) -> None:
        payload = {
            "sub": str(user.id),  # всегда user_id
            "username": user.username,  # доп поле
        }

        access_token = TokenService.create_access_token(payload)
        refresh_token = TokenService.create_refresh_token(payload)

        cls.set_access_token_to_cookie(access_token, response)
        cls.set_refresh_token_to_cookie(refresh_token, response)
