from abc import abstractmethod
from typing import TYPE_CHECKING, Protocol

from fastapi.responses import Response

if TYPE_CHECKING:
    from fastapi import HTTPException


class TokenRefreshErrorsHandler(Protocol):
    """Интерфейс для middleware, который будет обязан выполнять следующее
    исключения, при не ожидаемой ошибке."""

    @abstractmethod
    def _handle_auth_error(self, exception: "HTTPException") -> Response: ...

    @abstractmethod
    def _handle_unexpected_error(self, exception: Exception) -> Response: ...
