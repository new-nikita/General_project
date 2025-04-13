import logging

from fastapi.responses import Response

from core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TokenCookieService:
    @classmethod
    def set_access_token_to_cookie(cls, access_token: str, response: Response) -> None:
        """Добавление access_token в cookie"""

        response.set_cookie(
            key="access-token",
            value=f"Bearer {access_token}",
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
            max_age=settings.jwt.refresh_token_expire_days * 24 * 60 * 60,
        )
