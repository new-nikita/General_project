import logging
from typing import Awaitable, Callable

from fastapi import Request, HTTPException, status
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from auth.tokens_service import TokenService
from auth.token_cookie_service import TokenCookieService

logger = logging.getLogger(__name__)


class TokenRefreshMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        """
        Middleware для автоматического обновления Access Token.

        :param app: ASGI-приложение.
        """
        super().__init__(app)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """
        Обрабатывает запросы и обновляет Access Token при необходимости.

        :param request: Входящий HTTP-запрос.
        :param call_next: Следующая функция middleware в цепочке.
        :return: HTTP-ответ.
        """
        try:
            new_access_token = await self._try_refresh_token(request)
        except HTTPException as e:
            logger.warning(f"Ошибка аутентификации: {e.detail}")
            return self._unauthorized_response(
                message="If you fake the token again, I'll figure you out by IP.",
                status_code=e.status_code,
                delete_refresh_token=True,
            )
        except Exception as e:
            logger.error(
                f"Внутренняя ошибка при обновлении токена: {str(e)}", exc_info=True
            )
            return self._unauthorized_response(
                message="Internal server error during token refresh",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                delete_refresh_token=True,
            )

        if new_access_token:
            request.state.new_access_token = new_access_token

        response = await call_next(request)
        if hasattr(request.state, "new_access_token"):
            TokenCookieService.set_access_token_to_cookie(
                request.state.new_access_token, response
            )
            logger.info("Access Token успешно обновлен и установлен в куки")

        response.headers["WWW-Authenticate"] = "Bearer"
        return response

    @classmethod
    async def _try_refresh_token(cls, request: Request) -> str | None:
        """
        Проверяет валидность access_token, и при необходимости обновляет его через refresh_token.

        :param request: Текущий запрос.
        :return: Новый access_token или None, если обновление не требуется.
        """
        access_token = request.cookies.get("access-token")
        refresh_token = request.cookies.get("refresh-token")

        if access_token and TokenService.is_token_valid(access_token):
            return

        if not refresh_token:
            return

        try:
            new_access_token = TokenService.refresh_access_token(refresh_token)
            if client := f"{request.client.host}:{request.client.port}":
                logger.info(f"Access Token успешно обновлён для клиента: {client}")
            return new_access_token
        except HTTPException as e:
            logger.warning(f"Ошибка при обновлении токена: {e.detail}")
            raise e
        except Exception as e:
            logger.error(
                "Неизвестная ошибка при обновлении токена: %s", str(e), exc_info=True
            )
            raise

    @classmethod
    def _unauthorized_response(
        cls, message: str, status_code: int, delete_refresh_token: bool
    ) -> Response:
        """
        Формирует ответ с ошибкой авторизации и очищает куки при необходимости.

        :param message: Сообщение об ошибке.
        :param status_code: HTTP-статус ответа.
        :param delete_refresh_token: Удалить ли refresh_token из кук.
        :return: HTTP-ответ.
        """
        response = Response(content=message, status_code=status_code)
        response.delete_cookie("access-token")
        if delete_refresh_token:
            response.delete_cookie("refresh-token")
        return response
