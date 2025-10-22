from typing import Annotated, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from backend.core.config import settings
from backend.core.models import User
from backend.auth.authorization import get_current_user_from_cookie
from backend.friends.services import FriendsService
from backend.friends.dependencies import get_friends_service
from backend.users.services import UserService
from backend.users.dependencies import get_user_service
from backend.exceptions.message_exceptions import SomeExpectedException


router = APIRouter(
    prefix="/friends",
)


class FriendSearchFilters(BaseModel):
    query: Optional[str] = Field(default="", alias="query")
    username: Optional[str] = None
    gender: Optional[str] = None
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    city: Optional[str] = None
    country: Optional[str] = None
    online: Optional[str] = None
    friend_status: Optional[str] = None


@router.get("", response_class=HTMLResponse)
async def get_friends(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    friend_service: Annotated[FriendsService, Depends(get_friends_service)],
    tab: str = "friends",
):
    """Отображает список друзей

    :param request: Запрос FastAPI.
    :param tab: Флаг отображение друзей по статусам заявки.
    :param current_user: Текущий авторизованный пользователь.
    :param friend_service: Сервис для работы с друзьями.
    :return: HTML-страница профиля пользователя.
    :raises HTTPException: 404 если пользователь с указанным ID не найден.
    """

    error_message = None

    try:
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized: user not authenticated",
            )
        else:
            if tab == "friends":
                data = await friend_service.get_friends_friends(current_user.id)
            elif tab == "pending":
                data = await friend_service.get_pending_friends(current_user.id)

    except SomeExpectedException as e:
        error_message = e.detail
    except Exception:
        error_message = "Произошла непредвиденная ошибка. Попробуйте позже."

    return settings.templates.template_dir.TemplateResponse(
        "users/friends.html",
        {
            "request": request,
            "current_user": current_user,
            "tab": tab,
            "data": data,
            "error_message": error_message,
        },
    )


@router.get("/search", response_class=HTMLResponse)
async def get_search_for_friends_username(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    username: str | None = None,
):
    """Отображает поиск друзей по имени.

    :param request: Запрос FastAPI.
    :param username: Username искомого пользователя.
    :param current_user: Текущий авторизованный пользователь.
    :param user_service: Сервис работы с пользователя.
    :return: HTML-страница со списком подходящих пользователей.
    :raises.
    """
    users = []
    error_message = None

    if username:
        try:
            users = await user_service.search_users_by_username(
                username,
                current_user.id,
            )

        except SomeExpectedException as e:
            error_message = e.detail
        except Exception:
            error_message = "Произошла непредвиденная ошибка. Попробуйте позже."

    return settings.templates.template_dir.TemplateResponse(
        "users/search_for_friends_username.html",
        {
            "request": request,
            "current_user": current_user,
            "users": users,
            "error_message": error_message,
        },
    )


@router.post("/add", response_class=HTMLResponse)
async def add_friends(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    friend_service: Annotated[FriendsService, Depends(get_friends_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    username: str | None = None,
): ...


#     # TODO
#     #  Сделать отображение всех друзей по фильтрам ///
#     #  Сделать прокидку фильтров через эндпоинт или еще как нибудь
#     #  Добавить в сервис и репозиторий поиск по фильтрам
#     #  Реализовать функционал отправки заявки и ее принятия
