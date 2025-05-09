import logging
from typing import Annotated, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Form,
    UploadFile,
    File,
)

from fastapi.responses import HTMLResponse, RedirectResponse, Response
from pydantic import EmailStr, ValidationError

from core.config import settings
from core.models import User

from users.dependencies import get_user_service
from users.schemas.register_schema import RegisterForm

from users.schemas.users_schemas import ProfileCreate, UserCreate
from users.services import UserService


from auth.authorization import (
    get_current_user_from_cookie,
)
from utils.save_images import upload_image

logging.basicConfig(
    format=settings.logging.log_format, level=settings.logging.log_level_value
)
logger = logging.getLogger(__name__)

router = APIRouter()


async def get_register_form(
    username: str = Form(...),
    email: EmailStr = Form(...),
    password: str = Form(...),
    password2: str = Form(...),
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
    avatar: UploadFile | str | None = File(None),
) -> RegisterForm:
    return RegisterForm(
        username=username,
        email=email,
        password=password,
        password2=password2,
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
        avatar=avatar,
    )


@router.get("/register", response_class=HTMLResponse)
async def get_register_page(
    request: Request,
    current_user: Annotated[
        Optional[User], Depends(get_current_user_from_cookie)
    ] = None,
) -> Response:
    """
    Отображает страницу регистрации.

    :param request: Запрос FastAPI.
    :param current_user: Текущий пользователь (если авторизован).
    :return: HTML-страница с формой регистрации.
    """
    # Если пользователь уже авторизован, перенаправляем на главную
    if current_user:
        return RedirectResponse(url="/", status_code=303)

    return settings.templates.template_dir.TemplateResponse(
        "users/register.html",
        {
            "request": request,
            "current_user": current_user,
            "form_data": {},
            "errors": {},
        },
    )


@router.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    service: Annotated[UserService, Depends(get_user_service)],
    form_data: Annotated[RegisterForm, Depends(get_register_form)],
) -> Response:
    """Обрабатывает регистрацию нового пользователя."""
    try:
        # Сначала создаем пользователя без аватара
        profile_data = form_data.model_dump(
            exclude={"username", "password", "password2", "email", "avatar"}
        )
        profile = ProfileCreate(**profile_data)

        user_create = UserCreate(
            username=form_data.username,
            password=form_data.password,
            email=form_data.email,
            profile=profile,
        )

        # Создаем пользователя и сразу делаем flush, чтобы получить ID
        user = await service.create_user_and_added_in_db(user_create)
        await service.repository.session.flush()

        # Теперь загружаем аватар, если он был предоставлен
        if form_data.avatar and form_data.avatar.filename:
            avatar_url = await upload_image(
                user_id=user.id,
                image_file=form_data.avatar,
                content_path="users/avatars",
            )
            # Обновляем аватар пользователя
            user.profile.avatar = avatar_url
            await service.repository.session.commit()  # Фиксируем изменения

        logger.info(f"New user registered: {user.username}")

        response = RedirectResponse(url="/login", status_code=303)
        response.set_cookie(
            "register_success",
            "true",
            max_age=5,
            path="/login",
        )
        return response

    except HTTPException as e:
        logger.warning(f"Registration failed: {e.detail}")
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "form_data": form_data.model_dump(),
                "errors": {"": e.detail},
            },
            status_code=e.status_code,
        )
    except ValidationError as e:
        errors = {}
        for error in e.errors():
            field = error["loc"][-1]
            msg = error["msg"]
            errors[field] = msg

        logger.warning(f"Registration validation failed: {errors}")
        return settings.templates.template_dir.TemplateResponse(
            "users/register.html",
            {
                "request": request,
                "current_user": None,
                "form_data": form_data.model_dump(),
                "errors": errors,
            },
            status_code=400,
        )
    except Exception as e:
        await service.repository.session.rollback()
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "current_user": None,
                "form_data": form_data.model_dump(),
                "errors": {"": "Произошла ошибка при регистрации"},
            },
            status_code=500,
        )
