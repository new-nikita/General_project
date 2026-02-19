from typing import Annotated, Optional
import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
    Form,
)
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field


from backend.core.config import settings
from backend.core.models import User
from backend.auth.authorization import get_current_user_from_cookie
from backend.friends.services import FriendsService
from backend.friends.dependencies import get_friends_service
from backend.users.services import UserService
from backend.users.dependencies import get_user_service
from backend.exceptions.message_exceptions import (
    SomeExpectedException,
    FriendException,
)


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
):
    """Отображает поиск друзей.

    :param request: Запрос FastAPI.
    :param current_user: Текущий авторизованный пользователь.
    :param user_service: Сервис работы с пользователя.
    :return: HTML-страница со списком подходящих пользователей.
    :raises.
    """
    users = []
    error_message = None

    try:
        users = await user_service.get_all_users(current_user.id)

    except SomeExpectedException as e:
        error_message = e.detail
    except Exception:
        error_message = "Произошла непредвиденная ошибка. Попробуйте позже."

    return settings.templates.template_dir.TemplateResponse(
        "users/search_friends.html",
        {
            "request": request,
            "current_user": current_user,
            "users": users,
            "error_message": error_message,
        },
    )


@router.post("/add")
async def add_friends(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    friend_service: Annotated[FriendsService, Depends(get_friends_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    username: str = Form(..., min_length=1),
):

    friend_user = await user_service.get_user_by_username(username)
    if not friend_user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "success": False,
                "message": "Пользователь не найден",
            },
        )
    try:
        await friend_service.friend_add(current_user.id, friend_user.id)
        return JSONResponse(
            {
                "success": True,
                "message": "Запрос отправлен",
            }
        )

    except FriendException as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "message": e.detail,
            },
        )


@router.post("/accept", response_class=HTMLResponse)
async def accept_friend(
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    friend_service: Annotated[FriendsService, Depends(get_friends_service)],
    from_user_id: int = Form(...),
):
    try:
        await friend_service.friend_accept(
            current_user_id=current_user.id,
            from_user_id=from_user_id,
        )
        return JSONResponse(
            {
                "success": True,
                "message": "Запрос отправлен",
            }
        )

    except SomeExpectedException as e:
        return JSONResponse(
            {
                "success": False,
                "message": e.detail,
            }
        )


@router.post("/reject")
async def reject_friend(
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    friend_service: Annotated[FriendsService, Depends(get_friends_service)],
    from_user_id: int = Form(...),
):
    try:
        await friend_service.friend_reject(
            current_user_id=current_user.id,
            from_user_id=from_user_id,
        )
        return JSONResponse(
            {
                "success": True,
                "message": "Запрос отправлен",
            }
        )
    except SomeExpectedException as e:
        return JSONResponse(
            {
                "success": False,
                "message": e.detail,
            }
        )


# TODO
#  Дописать
#  Дописать условие проверку, отправлена заявка уже или нет( и если оправлена то при обновлении страницы не сбрасывалась кнопка
#  А то запрос можно отправить повторно
