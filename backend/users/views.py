import logging

from typing import Annotated, Optional

from fastapi import (
    APIRouter,
    Request,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
    Form,
)
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from posts.dependencies import get_post_service
from posts.services import PostService
from users.dependencies import get_user_service
from users.schemas.profile_schemas import ProfileUpdate
from users.services import UserService
from auth.authorization import (
    get_current_user_from_cookie,
)
from core.config import settings
from core.models import User
from core.common_dependencies import get_db_session
from utils.save_images import upload_image

logging.basicConfig(level=logging.INFO, format=settings.logging.log_format)

router = APIRouter(
    prefix="/profile",
    tags=["Profile"],
)


async def get_update_form(
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    middle_name: Optional[str] = Form(None),
    birth_date: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    phone_number: Optional[str] = Form(None),
    country: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    street: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
) -> ProfileUpdate:
    return ProfileUpdate(
        first_name=first_name,
        last_name=last_name,
        middle_name=middle_name,
        birth_date=birth_date,
        gender=gender,
        phone_number=phone_number,
        country=country,
        city=city,
        street=street,
        bio=bio,
    )


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
    return settings.templates.template_dir.TemplateResponse(
        "users/profile.html",
        {
            "request": request,
            "user": profile_user,
            "is_own_profile": is_own_profile,
            "current_user": current_user,
            "posts": posts,
        },
    )


@router.post("/avatar")
async def upload_avatar(
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    avatar: UploadFile = File(...),
) -> JSONResponse:
    try:
        image_url = await upload_image(
            user_id=current_user.id,
            image_file=avatar,
            content_path="users/avatars",
        )

        current_user.profile.avatar = image_url
        await session.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Аватар успешно обновлен", "avatar_url": image_url},
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Ошибка при загрузке аватара: {str(e)}"
        )


@router.post("/avatar/remove")
async def remove_avatar(
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> JSONResponse:
    default_avatar = "/static/profiles_avatar/дефолтный_аватар.jpg"
    current_user.profile.avatar = default_avatar
    await session.commit()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"new_avatar": default_avatar, "message": "Аватар удален"},
    )


@router.get("/edit/{profile_id}", response_class=HTMLResponse)
async def edit_profile(
    request: Request,
    profile_id: int,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> HTMLResponse:
    profile_user = await user_service.repository.get_by_id(profile_id)
    checkout_profile_owner(profile_user.id, current_user.id)

    profile_data = ProfileUpdate.model_validate(
        profile_user.profile, from_attributes=True
    ).model_dump(exclude_unset=True)

    return settings.templates.template_dir.TemplateResponse(
        "users/profile-edit.html",
        {
            "request": request,
            "user": profile_user,
            "current_user": current_user,
            "profile_data": profile_data,
        },
    )


@router.post("/edit/{profile_id}")
async def save_profile_data(
    profile_id: int,
    new_profile_data: Annotated[ProfileUpdate, Depends(get_update_form)],
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> JSONResponse:
    profile_user = await user_service.repository.get_by_id(profile_id)
    checkout_profile_owner(profile_user.id, current_user.id)
    await user_service.repository.update_profile(
        user=profile_user,
        dto_profile=new_profile_data,
    )
    # TODO либо найти как правильно распаковывать, либо делать делать зависимость как регистрации

    response = JSONResponse(
        status_code=status.HTTP_202_ACCEPTED, content={"message": "OK"}
    )
    return response


def checkout_profile_owner(profile_id: int | None, current_user_id: int | None) -> None:
    if profile_id is None or current_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    if profile_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Это профиль чужого пользователя.",
        )
