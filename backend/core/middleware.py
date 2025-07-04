import logging
from typing import Callable, Awaitable

from fastapi import Request, HTTPException, status
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from backend.auth.tokens_service import TokenService
from backend.auth.token_cookie_service import TokenCookieService
from backend.exceptions.custom_token_exceptions import InvalidTokenError
from backend.core.decorators.handle_errors import handle_token_errors

logger = logging.getLogger(__name__)


class TokenRefreshMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        """
        Middleware для автоматического обновления Access Token.

        :param app: ASGI-приложение.
        """
        super().__init__(app)

    @handle_token_errors
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """
        Метод обрабатывает входящий запрос и автоматически обновляет Access Token, если он устарел
        или вызывает ошибку, если токен недействителен.

        Последовательность действий:
        1. Проверяется наличие и валидность текущего Access Token.
        2. Если токен устарел или отсутствует, генерируется новый Access Token с помощью Refresh Token.
        3. После успешного обновления новый токен сохраняется в состоянии запроса (`request.state.new_access_token`).
        4. Далее запрос продолжает путь обработки через следующий слой middleware (call_next).
        5. Перед отправкой клиенту ответ дополняется новым Access Token в куки, если он был обновлён.

        Важно:
            Токен добавляется в куки после завершения обработки основного маршрута,
            чтобы обеспечить согласованность состояний.

            Если новый токен был сгенерирован, он временно сохраняется в `request.state.new_access_token`
            до завершения цепочки middleware, чтобы быть установленным в куки сразу — без необходимости
            повторного запроса от клиента. Это позволяет клиенту получить обновлённый токен в этом же ответе,
            и сразу видеть, что он аутентифицирован.

        :param request: Входящий HTTP-запрос.
        :param call_next: Следующая функция middleware в цепочке.
        :return: HTTP-ответ.
        """
        new_token = await self._refresh_if_needed(request)

        if new_token:
            request.state.new_access_token = new_token

        response = await call_next(request)

        self._maybe_set_new_access_token(request, response)

        return self._add_security_headers(response)

    def _maybe_set_new_access_token(self, request: Request, response: Response) -> None:
        """
        Устанавливает новый access token в куки, если он был создан.
        """
        if hasattr(request.state, "new_access_token"):
            self._set_new_access_token(response, request.state.new_access_token)

    async def _refresh_if_needed(self, request: Request) -> str | None:
        """Обновляет токен, если требуется"""
        if not request.cookies.get("refresh-token"):
            return

        if self._needs_refresh(request):
            return await self._safe_refresh(request)

    @classmethod
    def _needs_refresh(cls, request: Request) -> bool:
        """Проверяет, нуждается ли токен в обновлении"""
        access_token = request.cookies.get("access-token")
        return not access_token or not TokenService.is_token_valid(access_token)

    @classmethod
    async def _safe_refresh(cls, request: Request) -> str:
        """Безопасное обновление токена с обработкой ошибок"""
        try:
            refresh_token = request.cookies.get("refresh-token")
            return TokenService.refresh_access_token(refresh_token)
        except InvalidTokenError as e:
            logger.warning("Invalid token: %s", e)
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
        except Exception as e:
            logger.error("Refresh failed: %s", e, exc_info=True)
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Refresh failed")

    @classmethod
    def _set_new_access_token(cls, response: Response, token: str) -> None:
        """Устанавливает новый токен в куки"""
        TokenCookieService.set_access_token_to_cookie(token, response)
        logger.info("Token refreshed")

    def _handle_auth_error(self, error: HTTPException) -> Response:
        """Обрабатывает ошибки аутентификации"""
        logger.warning("Auth error: %s", error.detail)
        response = Response(
            content="If you fake the token again, I'll figure you out by IP.",
            status_code=error.status_code,
        )
        self._clear_auth_cookies(response)
        return response

    def _handle_unexpected_error(self, error: Exception) -> Response:
        """Обрабатывает непредвиденные ошибки"""
        logger.error("Unexpected error: %s", error, exc_info=True)
        response = Response(
            content="Internal server error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        self._clear_auth_cookies(response)
        return response

    @classmethod
    def _clear_auth_cookies(cls, response: Response) -> None:
        """Очищает аутентификационные куки"""
        response.delete_cookie("access-token")
        response.delete_cookie("refresh-token")

    @classmethod
    def _add_security_headers(cls, response: Response) -> Response:
        """Добавляет security-заголовки"""
        response.headers["WWW-Authenticate"] = "Bearer"
        return response
