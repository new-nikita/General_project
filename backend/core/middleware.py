from fastapi import Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import logging

from core.config import settings
from users.tokens import refresh_access_token, decode_token


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TokenRefreshMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        """
        Middleware для автоматического обновления Access Token.

        :param app: ASGI-приложение.
        """
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Обрабатывает запросы и обновляет Access Token при необходимости.

        :param request: Входящий HTTP-запрос.
        :param call_next: Следующая функция middleware в цепочке.
        :return: HTTP-ответ.
        """
        response = await call_next(request)

        # Получаем токены из cookies
        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")

        if not access_token:
            logger.debug("Access token отсутствует")
            return response

        if not refresh_token:
            logger.debug("Refresh token отсутствует")
            return response

        try:
            # Проверяем срок действия Access Token
            if access_token.startswith("Bearer "):
                access_token = access_token[7:]  # Убираем префикс "Bearer "
            else:
                logger.warning("Access token не содержит префикс 'Bearer'")
                return response

            payload = decode_token(access_token)
            if payload.get("exp", 0) > int(time.time()):
                logger.debug("Access Token действителен")
                return response

        except ValueError as e:
            # Access Token недействителен, пробуем обновить его
            logger.warning(f"Access Token недействителен: {e}")

        try:
            # Пытаемся обновить Access Token с помощью Refresh Token
            new_access_token = refresh_access_token(refresh_token)
            response.set_cookie(
                key="access_token",
                value=f"Bearer {new_access_token}",
                httponly=True,
                samesite="lax",
                max_age=settings.jwt.access_token_expire_minutes * 60,
            )
            logger.info("Access Token успешно обновлен")

        except ValueError as e:
            logger.warning(f"Недействительный Refresh Token: {e}")
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")

        return response
