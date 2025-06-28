from fastapi import HTTPException


class InvalidTokenError(HTTPException):
    """Исключение для невалидного токена в запросе."""

    def __init__(self) -> None:
        super().__init__(status_code=401, detail="Invalid token")
