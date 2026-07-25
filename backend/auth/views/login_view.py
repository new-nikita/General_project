import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Response, HTTPException, status
from fastapi.responses import RedirectResponse

from backend.core.config import settings
from backend.users.dependencies import get_user_service
from backend.users.services import UserService

from backend.auth.authorization import authenticate_user
from backend.auth.token_cookie_service import TokenCookieService
from backend.auth.schemas.register_schemas import LoginRequest
from backend.auth.authorization import get_current_user_from_cookie

from backend.core.models import User


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
# @router.get("/me")
# async def get_current_user(
#     current_user: Annotated[
#         Optional[User],
#         Depends(get_current_user_from_cookie),
#     ],
# ):
#     if current_user is None:
#         raise HTTPException(
#             status_code=401,
#             detail="Not authenticated",
#         )
#
#     return current_user


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
        err = str(e).lower()
        if "connection refused" in err or "connect" in err:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="База данных недоступна. Запустите PostgreSQL: docker compose up -d pg",
            )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/logout")
async def logout(response: Response):
    """Удаляет auth-cookies."""
    response.delete_cookie(
        key="access-token",
        httponly=True,
        samesite="lax",
    )

    response.delete_cookie(
        key="refresh-token",
        httponly=True,
        samesite="lax",
    )
    return {"status": "ok"}
