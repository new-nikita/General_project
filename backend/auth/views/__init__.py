import logging
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Request,
)
from fastapi.responses import HTMLResponse

from backend.core.config import settings
from backend.core.models import User

from backend.auth.authorization import (
    get_current_user_from_cookie,
)
from backend.auth.views.login_view import router as login_router
from backend.auth.views.register_view import router as register_router
from backend.auth.views.reset_password import router as forgot_router
from backend.posts.services import PostService
from backend.posts.dependencies import get_post_service


logging.basicConfig(
    format=settings.logging.log_format, level=settings.logging.log_level_value
)
logger = logging.getLogger(__name__)
# TODO добавить количество попыток входа и хранить кол-во попыток, например в redis

router = APIRouter(tags=["Auth"])
router.include_router(login_router)
router.include_router(register_router)
router.include_router(forgot_router)


@router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    post_service: Annotated[PostService, Depends(get_post_service)],
    page: int = 1,
):
    """
    Отображает главную страницу с постами, отсортированными по лайкам.

    :param request: Запрос FastAPI
    :param current_user: Текущий пользователь
    :param post_service: Сервис постов
    :param page: Номер страницы (query param ?page=1)
    :return: HTML-страница с постами
    """

    posts, total_pages = await post_service.repository.get_paginated_posts_by_likes(
        page=page, current_user_id=current_user.id if current_user is not None else None
    )

    return settings.templates.template_dir.TemplateResponse(
        "index.html",
        {
            "request": request,
            "current_user": current_user,
            "posts": posts,
            "page": page,
            "total_pages": total_pages,
        },
    )
