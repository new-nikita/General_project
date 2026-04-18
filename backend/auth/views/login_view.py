import logging
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Response,
    Form,
    HTTPException,
)
from fastapi.responses import RedirectResponse

from backend.core.config import settings
from backend.users.dependencies import get_user_service
from backend.users.services import UserService

from backend.auth.authorization import authenticate_user
from backend.auth.token_cookie_service import TokenCookieService
from backend.auth.schemas.register_schemas import LoginRequest


logging.basicConfig(
    format=settings.logging.log_format, level=settings.logging.log_level_value
)
logger = logging.getLogger(__name__)
# TODO добавить количество попыток входа и хранить кол-во попыток, например в redis

router = APIRouter(tags=["auth"])


# @router.get("/login", tags=["auth"], response_class=HTMLResponse)
# async def login_page(
#     request: Request,
# ):
#     """
#     Отображает страницу входа с формой.
#
#     :param request: Запрос для передачи в шаблон.
#     :return: HTML-страница с формой входа.
#     """
#     return settings.templates.template_dir.TemplateResponse(
#         "users/login.html",
#         {
#             "request": request,
#         },
#     )


@router.post("/login")
async def login(
    response: Response,
    service: Annotated[UserService, Depends(get_user_service)],
    user_data: LoginRequest,
):
    """
    Аутентифицирует пользователя и перенаправляет на профиль.

    :param response:
    :param service: Сервис для работы с пользователями.
    :param user_data: Username, password введенные пользователем
    :return: JSON
    :raises HTTPException: 401 при неверных данных или 500 при внутренней ошибке.
    """
    try:
        user = await authenticate_user(
            service,
            user_data.username,
            user_data.password,
        )
        await TokenCookieService.set_auth_cookies(response, user)

        logger.info(f"User {user.username} successfully authenticated")

        return {
            "status": "ok",
            "user_id": user.id,
            "username": user.username,
        }

    except HTTPException as e:
        logger.error(f"Authentication failed: {e.detail}")
        raise e

    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# @router.get("/logout", tags=["auth"])
# async def logout():
#     """
#     Выходит из системы, удаляя токены из HTTP-Only cookies.
#
#     :param response: Ответ FastAPI.
#     :return: Сообщение об успешном выходе.
#     """
#     redirect_response = RedirectResponse(status_code=303, url="/login")
#     redirect_response.delete_cookie("access-token")
#     redirect_response.delete_cookie("refresh-token")
#     return redirect_response
