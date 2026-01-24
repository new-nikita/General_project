from fastapi import HTTPException, status


class SomeExpectedException(HTTPException):
    def __init__(self, message: str = "Произошла ошибка"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


class FriendException(Exception):
    def __init__(self, detail: str):
        self.detail = detail
