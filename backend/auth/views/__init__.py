import logging

from fastapi import (
    APIRouter,
    Depends,
    Request,
)
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from core.config import settings
from core.models import User

from auth.authorization import (
    get_current_user_from_cookie,
)
from auth.views.login_view import router as login_router
from auth.views.register_view import router as register_router


logging.basicConfig(
    format=settings.logging.log_format, level=settings.logging.log_level_value
)
logger = logging.getLogger(__name__)
# TODO добавить количество попыток входа и хранить кол-во попыток, например в redis

router = APIRouter(tags=["Auth"])
router.include_router(login_router)
router.include_router(register_router)


templates = Jinja2Templates(directory=settings.template_dir)


@router.get("/", response_class=HTMLResponse)
async def index(
    request: Request, current_user: User = Depends(get_current_user_from_cookie)
):
    """
    Отображает главную страницу с приветствием.

    :param request: Запрос FastAPI.
    :param current_user: Текущий авторизованный пользователь.
    :return: HTML-страница с приветствием.
    """
    return templates.TemplateResponse(
        "index.html", {"request": request, "user": current_user}
    )
