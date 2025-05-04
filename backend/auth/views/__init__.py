import logging
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Request,
)
from fastapi.responses import HTMLResponse

from core.config import settings
from core.models import User

from auth.authorization import (
    get_current_user_from_cookie,
)
from auth.views.login_view import router as login_router
from auth.views.register_view import router as register_router
from posts.services import PostService
from posts.dependencies import get_post_service

logging.basicConfig(
    format=settings.logging.log_format, level=settings.logging.log_level_value
)
logger = logging.getLogger(__name__)
# TODO добавить количество попыток входа и хранить кол-во попыток, например в redis

router = APIRouter(tags=["Auth"])
router.include_router(login_router)
router.include_router(register_router)


@router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    post_service: Annotated[PostService, Depends(get_post_service)],
):
    """
    Отображает главную страницу с приветствием.

    :param request: Запрос FastAPI.
    :param current_user: Текущий авторизованный пользователь.
    :param post_service: Сервис для работы с постами.
    :return: HTML-страница с приветствием.
    """
    posts = await post_service.repository.get_all()
    return settings.templates.template_dir.TemplateResponse(
        "index.html",
        {
            "request": request,
            "current_user": current_user,
            "posts": posts,
        },
    )
