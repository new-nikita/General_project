from enum import StrEnum


class ProfileVisibility(StrEnum):
    """Список категории приватности профиля"""

    public = "public"
    friends = "friends"
    private = "private"
