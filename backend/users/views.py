from typing import Annotated

from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from posts.dependencies import get_post_service
from posts.services import PostService
from users.dependencies import get_user_service
from users.services import UserService
from auth.authorization import (
    get_current_user_from_cookie,
)
from core.config import settings
from core.models import User


router = APIRouter(
    prefix="/profile",
    include_in_schema=False,  # Исключаем из OpenAPI документации
)

templates = Jinja2Templates(directory=settings.template_dir / "users")


@router.get("/{profile_id}", response_class=HTMLResponse)
async def get_user_profile(
    request: Request,
    profile_id: int,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    post_service: Annotated[PostService, Depends(get_post_service)],
    is_own_profile: bool = False,
) -> HTMLResponse:
    """
    Отображает страницу профиля пользователя.

    :param request: Запрос FastAPI.
    :param profile_id: ID профиля пользователя.
    :param current_user: Текущий авторизованный пользователь.
    :param user_service: Сервис для работы с пользователями.
    :param post_service: Сервис для работы с постами.
    :param is_own_profile: Флаг, указывающий, является ли профиль собственным.
    :return: HTML-страница профиля пользователя.
    :raises HTTPException: 404 если пользователь с указанным ID не найден.
    """
    profile_user = await user_service.repository.get_by_id(profile_id)
    if not profile_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {profile_id} не найден",
        )
    if current_user is not None:
        # Определяем, является ли профиль собственным
        is_own_profile = current_user.id == profile_user.id

    posts = await post_service.repository.get_all_posts_by_author_id(profile_id)
    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user": profile_user,
            "is_own_profile": is_own_profile,
            "current_user": current_user,
            "posts": posts,
        },
    )
