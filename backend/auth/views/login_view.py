import logging
from datetime import date
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Request,
    Response,
    Form,
)
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import EmailStr

from auth.redis_client import RedisClient
from auth.tokens_service import TokenService
from auth.token_cookie_service import TokenCookieService
from core.config import settings
from core.models import User

from users.dependencies import get_user_service
from users.services import UserService

from auth.authorization import (
    authenticate_user,
    get_current_user_from_cookie,
)


logging.basicConfig(
    format=settings.logging.log_format, level=settings.logging.log_level_value
)
logger = logging.getLogger(__name__)
# TODO добавить количество попыток входа и хранить кол-во попыток, например в redis

router = APIRouter()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

templates = Jinja2Templates(directory=settings.template_dir / "users")


@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    # current_user: User = Depends(
    #     get_current_user_from_cookie),  # Получение текущего пользователя
):
    """
    Отображает страницу входа с формой.

    :param request: Запрос для передачи в шаблон.
    :param current_user: Текущий авторизованный пользователь.
    :return: HTML-страница с формой входа.
    """
    return templates.TemplateResponse(
        "login.html",  # Имя HTML-шаблона
        {
            "request": request,
            "current_user": None,
        },
    )


@router.post("/login", response_class=HTMLResponse)
async def login(
    response: Response,
    service: Annotated[UserService, Depends(get_user_service)],
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    """
    Аутентифицирует пользователя и перенаправляет на профиль.

    :param response:
    :param request: Запрос для передачи в шаблон.
    :param username: Имя пользователя из формы.
    :param password: Пароль из формы.
    :param service: Сервис для работы с пользователями.
    :return: HTML-страница после успешной аутентификации.
    :raises HTTPException: 401 при неверных данных или 500 при внутренней ошибке.
    """
    try:
        user = await authenticate_user(service, username, password)

        access_token = TokenService.create_access_token({"sub": user.username})
        refresh_token = TokenService.create_refresh_token({"sub": user.username})

        logger.info(f"User {user.username} successfully authenticated")

        redirect = RedirectResponse(
            url=f"/profile/{user.id}",
            status_code=303,
        )
        redirect.set_cookie("access-token", access_token, domain="my-vk")
        redirect.set_cookie("refresh-token", refresh_token)
        return redirect

    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Неверное имя пользователя или пароль."},
        )


@router.get("/logout")
async def logout():
    """
    Выходит из системы, удаляя токены из HTTP-Only cookies.

    :param response: Ответ FastAPI.
    :return: Сообщение об успешном выходе.
    """
    redirect_response = RedirectResponse(status_code=303, url="/login")
    redirect_response.delete_cookie("access-token")
    redirect_response.delete_cookie("refresh-token")
    return redirect_response
