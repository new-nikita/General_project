from enum import StrEnum


class ClientPlatform(StrEnum):
    """Платформа клиента при авторизации."""

    IOS = "ios"
    ANDROID = "android"
    WEB = "web"
