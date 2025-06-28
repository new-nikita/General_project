from functools import wraps
from typing import ParamSpec, TypeVar, Callable, Awaitable

from fastapi import HTTPException
from fastapi.responses import Response

P = ParamSpec("P")
R = TypeVar("R", bound="TokenRefreshMiddleware")


def handle_token_errors(
    func: Callable[P, Awaitable[Response]],
) -> Callable[P, Awaitable[Response]]:
    """
    Декоратор для обработки ошибок аутентификации в middleware.

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
    async def wrapper(self: R, *args: P.args, **kwargs: P.kwargs) -> Response:
        """
        Обертка для обработки ошибок в middleware.
        :param self: Это текущий объект middleware (TokenRefreshMiddleware).
        """
        try:
            return await func(self, *args, **kwargs)
        except HTTPException as http_exception:
            return self._handle_auth_error(http_exception)
        except Exception as base_exception:
            return self._handle_unexpected_error(base_exception)

    return wrapper
