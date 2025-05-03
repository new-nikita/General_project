import time
import logging

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse, Response
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

    async def dispatch(self, request: Request, call_next) -> Response | JSONResponse:
        """
        Обрабатывает запросы и обновляет Access Token при необходимости.

        :param request: Входящий HTTP-запрос.
        :param call_next: Следующая функция middleware в цепочке.
        :return: HTTP-ответ.
        """
        access_token = request.cookies.get("access-token")
        refresh_token = request.cookies.get("refresh-token")
        new_access_token = None
        if not refresh_token:
            logger.debug("Refresh token отсутствует")

        try:
            if not access_token or not TokenService.is_token_valid(access_token):
                if refresh_token:
                    logger.debug("Access Token отсутствует или истёк")
                    new_access_token = TokenService.refresh_access_token(refresh_token)

        except ValueError as e:
            logger.warning(f"Недействительный Refresh Token: {e}")
            response = Response("Unauthorized", status_code=401)
            response.delete_cookie("access-token")
            response.delete_cookie("refresh-token")
            return response

        except HTTPException as e:
            response = Response(
                status_code=e.status_code,
                content="If you fake the token again, I'll figure you out by IP.",
            )
            response.delete_cookie("access-token")
            return response

        if new_access_token:
            request.state.new_access_token = new_access_token

        response = await call_next(request)

        # После эндпоинта обновляем куки, если был обновлён токен
        if hasattr(request.state, "new_access_token"):
            TokenCookieService.set_access_token_to_cookie(
                request.state.new_access_token, response
            )
            logger.info("Access Token успешно обновлен и установлен в ответ")

        return response
