from functools import wraps
from typing import (
    Awaitable,
    Callable,
    ParamSpec,
    cast,
)

from fastapi import HTTPException
from fastapi.responses import Response

from backend.interfaces.error_handler_middleware_protocol import (
    TokenRefreshErrorsHandler,
)

P = ParamSpec("P")


def handle_token_errors(
    func: Callable[P, Awaitable[Response]],
) -> Callable[P, Awaitable[Response]]:
    """Декоратор для обработки ошибок аутентификации в middleware.

    Этот декоратор оборачивает асинхронную функцию и обрабатывает
    исключения, связанные с аутентификацией. Он перехватывает
    следующие типы исключений:
    - HTTPException: ошибки аутентификации, которые возвращают
      соответствующий ответ с кодом состояния.
    - Exception: любые другие исключения, которые обрабатываются
      как внутренние ошибки сервера.

    :param func: Асинхронная функция, которую нужно обернуть.
    :return: Обернутая функция с обработкой ошибок.
    """

    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Response:
        """Обертка для обработки ошибок в middleware.

        `self` - это экземпляр TokenRefreshMiddleware, который
        обязан выполнять интерфейс TokenRefreshErrorsHandler'а
        с обработками ошибок и возвратом ответов клиенту.

        Функция cast из модуля typing не создает никаких объектов
         - это исключительно подсказка для статического анализа типов (mypy)
        """
        try:
            response: Response = await func(*args, **kwargs)
            return response
        except HTTPException as http_exception:
            # Важно! на самом деле тут не TokenRefreshErrorsHandler,
            # а TokenRefreshMiddleware
            self = cast(TokenRefreshErrorsHandler, args[0])
            return self._handle_auth_error(http_exception)
        except Exception as base_exception:
            self = cast(TokenRefreshErrorsHandler, args[0])
            return self._handle_unexpected_error(base_exception)

    return wrapper
