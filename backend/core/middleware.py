import time
import logging

from fastapi import Request
from fastapi.responses import Response, RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from auth.tokens_service import TokenService
from auth.token_cookie_service import TokenCookieService

logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s] %(message)s")
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

        if not refresh_token:
            logger.debug("Refresh token отсутствует")
            return response

        try:
            """удалить и проверить с токен сервис"""
            # Если Access Token отсутствует или истек, пробуем обновить его
            if not access_token or not self.is_token_valid(access_token):
                logger.debug("Access Token отсутствует или недействителен")
                new_access_token = TokenService.refresh_access_token(refresh_token)
                TokenCookieService.set_access_token_to_cookie(new_access_token, response)
                logger.info("Access Token успешно обновлен")

        except ValueError as e:
            # Refresh Token недействителен - очищаем куки
            logger.warning(f"Недействительный Refresh Token: {e}")
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")

            # Перенаправляем пользователя на страницу входа
            # return RedirectResponse(url="/login", status_code=303)
            # TODO сделать перенаправление на страницу аутентификации, когда она появится

        return response

    # TODO избавиться от метода, так как е
    def is_token_valid(self, token: str) -> bool:
        """
        Проверяет, действителен ли Access Token.

        :param token: Access Token.
        :return: True если токен действителен, иначе False.
        """
        if token.startswith("Bearer "):
            token = token[7:]  # Убираем префикс "Bearer "
        else:
            logger.warning("Access token не содержит префикс 'Bearer'")
            return False

        try:
            payload = TokenService.decode_and_validate_token(token)
            exp_time = payload.get("exp")

            return exp_time and exp_time > int(time.time())
        except ValueError:
            logger.warning("Ошибка при декодировании Access Token")
            return False
