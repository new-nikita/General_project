import logging
from typing import Annotated

from fastapi import (
    APIRouter,
    Request,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
)
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from backend.posts.dependencies import get_post_service
from backend.posts.services import PostService
from backend.users.dependencies import get_user_service, get_update_form
from backend.users.schemas.profile_schemas import ProfileUpdate
from backend.users.services import UserService
from backend.users.utils import checkout_profile_owner
from backend.auth.authorization import (
    get_current_user_from_cookie,
)
from backend.core.config import settings
from backend.core.models import User
from backend.utils.save_images import upload_image


logging.basicConfig(level=logging.INFO, format=settings.logging.log_format)

router = APIRouter(
    prefix="/profile",
    tags=["Profile"],
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

        current_user = await user_service.repository.get_by_id_with_likes(
            current_user.id
        )

    # Получаем посты с полной информацией о лайках
    posts = await post_service.repository.get_all_posts_by_author_id(
        profile_id, current_user.id if current_user else None
    )

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


@router.get("/edit/{profile_id}", response_class=HTMLResponse)
async def edit_profile(
    request: Request,
    profile_id: int,
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> HTMLResponse:
    """
    Отображает форму редактирования профиля пользователя.

    Проверяет, что текущий пользователь является владельцем профиля.
    Заполняет форму текущими данными профиля из БД.

    :param request: Объект запроса FastAPI/Starlette.
    :param profile_id: ID профиля, который нужно отредактировать.
    :param current_user: Текущий авторизованный пользователь (зависимость).
    :param user_service: Сервис для работы с пользователями (зависимость).

    :return: HTML-шаблон с формой редактирования профиля.

    :raises HTTPException 404: Если пользователь не найден.
    :raises HTTPException 403: Если пользователь пытается изменить чужой профиль.
    """
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
) -> RedirectResponse:
    """
    Обрабатывает отправку формы редактирования профиля.

    Проверяет, что текущий пользователь — владелец профиля.
    Обновляет данные профиля через UserService и перенаправляет на страницу профиля.

    :param profile_id: ID профиля, который нужно обновить.
    :param new_profile_data: Данные формы, полученные и валидированные через ProfileUpdate схему.
    :param current_user: Текущий авторизованный пользователь (зависимость).
    :param user_service: Сервис для работы с пользователями (зависимость).

    :return: Перенаправление на страницу профиля после успешного обновления.

    :raises HTTPException 404: Если пользователь не найден.
    :raises HTTPException 403: Если пользователь пытается изменить чужой профиль.
    :raises HTTPException 500: Если произошла ошибка при сохранении профиля в БД.
    """
    profile_user = await user_service.repository.get_by_id(profile_id)
    checkout_profile_owner(profile_user.id, current_user.id)
    await user_service.update_profile(
        user=profile_user,
        dto_profile=new_profile_data,
    )

    return RedirectResponse(url=f"/profile/{profile_user.id}", status_code=303)


@router.post("/avatar")
async def upload_avatar(
    current_user: Annotated[User, Depends(get_current_user_from_cookie)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    avatar: UploadFile = File(...),
) -> JSONResponse:
    """
    Обрабатывает загрузку нового аватара пользователя.

    :param current_user: Текущий авторизованный пользователь.
    :param user_service: Сервис для работы с пользователями.
    :param avatar: Загруженный файл изображения (формат: UploadFile).

    :return: JSON-ответ с новым URL аватара или сообщением об ошибке.

    :raises HTTPException 400: Если произошла ошибка при загрузке файла.
    """
    try:
        image_url = await upload_image(
            user_id=current_user.id,
            image_file=avatar,
            content_path="avatars",
        )
        await user_service.repository.update_user_avatar(current_user, image_url)

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
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> JSONResponse:
    """
    Удаляет текущий аватар пользователя и устанавливает дефолтный.

    :param current_user: Текущий авторизованный пользователь.
    :param user_service: Сервис для работы с пользователями.

    :return: JSON-ответ с подтверждением удаления и ссылкой на дефолтный аватар.

    :raises HTTPException 500: Если не удалось обновить аватар в БД.
    """
    default_avatar = "/client_files/avatars/дефолтный_аватар.jpg"
    await user_service.repository.delete_user_avatar(current_user)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"new_avatar": default_avatar, "message": "Аватар удален"},
    )
