from fastapi import HTTPException, status


def checkout_profile_owner(profile_id: int | None, current_user_id: int | None) -> None:
    """
    Проверяет, что profile_id принадлежит current_user_id.

    :param profile_id: ID профиля, который пытается изменить пользователь.
    :param current_user_id: ID текущего авторизованного пользователя.

    :return: None — если всё ок.

    :raises HTTPException 404: Если один из ID равен None.
    :raises HTTPException 403: Если profile_id != current_user_id (пользователь пытается изменить чужой профиль).
    """
    if profile_id is None or current_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    if profile_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Это профиль чужого пользователя.",
        )
