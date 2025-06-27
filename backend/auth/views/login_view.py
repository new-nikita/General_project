import logging
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Request,
    Response,
    Form,
    HTTPException,
)
from fastapi.responses import HTMLResponse, RedirectResponse

from backend.core.config import settings
from backend.users.dependencies import get_user_service
from backend.users.services import UserService

from backend.auth.authorization import (
    authenticate_user,
    get_redirect_with_authentication_user,
)


logging.basicConfig(
    format=settings.logging.log_format, level=settings.logging.log_level_value
)
logger = logging.getLogger(__name__)
# TODO добавить количество попыток входа и хранить кол-во попыток, например в redis

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
):
    """
    Отображает страницу входа с формой.

    :param request: Запрос для передачи в шаблон.
    :return: HTML-страница с формой входа.
    """
    return settings.templates.template_dir.TemplateResponse(
        "users/login.html",
        {
            "request": request,
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
        # Аутентификация пользователя
        user = await authenticate_user(service, username, password)

        redirect = await get_redirect_with_authentication_user(user)
        logger.info(f"User {user.username} successfully authenticated")
        return redirect

    except HTTPException as e:
        logger.error(f"Authentication failed: {e}")
        return settings.templates.template_dir.TemplateResponse(
            "users/login.html",
            {
                "request": request,
                "error": e.detail,
            },
            status_code=e.status_code,
        )
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        return settings.templates.template_dir.TemplateResponse(
            "users/login.html",
            {
                "request": request,
                "error": str(e),
            },
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
