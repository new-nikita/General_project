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

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from pydantic import EmailStr, ValidationError

from backend.auth import (
    AsyncRedisClient,
    TokenService
)

from backend.core.config import settings
from backend.core.models import User

from backend.users.dependencies import get_user_service
from backend.users.schemas.register_schema import RegisterForm
from backend.users.schemas.users_schemas import ProfileCreate, UserCreate
from backend.users.services import UserService

from backend.auth.Celery.tasks import send_confirmation_email_task
from backend.auth.authorization import (
    get_current_user_from_cookie,
    get_redirect_with_authentication_user
)

from backend.utils.save_images import upload_image


logging.basicConfig(
    format=settings.logging.log_format, level=settings.logging.log_level_value
)
logger = logging.getLogger(__name__)

router = APIRouter()

templates = Jinja2Templates(directory=settings.template_dir / "users")
templates2 = Jinja2Templates(directory=settings.template_dir / "info")


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

@router.get("/initial_register", response_class=HTMLResponse)
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

    return templates.TemplateResponse(
        "initial_register.html",
        {
            "request": request,
            "current_user": current_user,
            "form_data": {},
            "errors": {},
        },
    )


@router.post("/initial_register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    redis: Annotated[AsyncRedisClient, Depends(AsyncRedisClient)],
    email: EmailStr = Form(...),
) -> Response:

    temporary_user_token = TokenService.create_refresh_token({'sub': email})

    try:
        await redis.connect()
        await redis.save_pending_email_token(temporary_user_token, email)

        # Отправка письма через Celery
        send_confirmation_email_task.delay('register', 'initial_message', email, temporary_user_token, str(request.base_url))

        RedirectResponse(url="/further_actions", status_code=303)
        return templates2.TemplateResponse('further_actions.html', {'request': request})

    except Exception as e:
        logger.error(f"Ошибка при регистрации: {e}", exc_info=True)

        return templates.TemplateResponse(
            "initial_message.html",
            {
                "request": request,
                "current_user": None,
                "form_data": email,
                "errors": {"": "Произошла ошибка при регистрации"},
            },
            status_code=500,
        )

@router.get("/register", response_class=HTMLResponse)
async def get_register_page(
    request: Request,
    token: Optional[str] = None,
    current_user: Annotated[
        Optional[User], Depends(get_current_user_from_cookie)
    ] = None,
) -> Response:
    if current_user:
        return RedirectResponse(url="/", status_code=303)

    form_data = {}

    if token:
        try:
            payload = TokenService.decode_and_validate_token(token)
            email = payload.get("sub")
            if email:
                form_data["email"] = email
        except Exception as e:
            logger.warning(f"Ошибка при декодировании токена: {e}")

    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "current_user": current_user,
            "form_data": form_data,
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
                content_path="users_files/avatars",
            )
            # Обновляем аватар пользователя
            user.profile.avatar = avatar_url
            await service.repository.session.commit()  # Фиксируем изменения

        logger.info(f"New user registered: {user.username}")

        redirect = await get_redirect_with_authentication_user(user)
        return redirect


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
