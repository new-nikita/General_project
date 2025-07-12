from fastapi import HTTPException, status


class InvalidTokenError(HTTPException):
    """Исключение для невалидного токена в запросе."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


class NotFoundTokenWithEmailInRedis(HTTPException):
    """Класс Исключение для обработки ошибки, когда токен с email не найден в
    Redis хранилище."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Токен с email не найден в Redis хранилище",
        )
