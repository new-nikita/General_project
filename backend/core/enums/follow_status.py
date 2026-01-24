from enum import StrEnum


class FollowStatus(StrEnum):
    """Список статусов подписки пользователя на пользователя."""

    PENDING = "pending"  #  в ожидании
    ACCEPTED = "accepted"  # принял
    REJECTED = "rejected"  #  отклонен
    BLOCKED = "blocked"  # заблокирован
