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
from backend.auth.authorization import get_current_user_from_cookie, get_redirect_with_authentication_user

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
    # birth_date: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    # phone_number: Optional[str] = Form(None),
    country: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    street: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    # avatar: UploadFile | str | None = File(None),
) -> RegisterForm:
    return RegisterForm(
        username=username,
        email=email,
        password=password,
        password2=password2,
        first_name=first_name,
        last_name=last_name,
        middle_name=middle_name,
        # birth_date=birth_date,
        gender=gender,
        # phone_number=phone_number,
        country=country,
        city=city,
        street=street,
        bio=bio,
        # avatar=avatar,
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

    return templates.TemplateResponse(
        "register.html",
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
    form_data: Annotated[RegisterForm, Depends(get_register_form)],
    redis: Annotated[AsyncRedisClient, Depends(AsyncRedisClient)],
) -> Response:

    temporary_user_token = TokenService.create_refresh_token({'sub': form_data.username})

    data = form_data.model_dump()  # сделать сохранение хеша, а не пароля

    await redis.connect()
    await redis.save_pending_email_token(temporary_user_token, data)

    # Отправка письма через Celery
    send_confirmation_email_task.delay('confirm', form_data.email, temporary_user_token, str(request.base_url))

    RedirectResponse(url="/further_actions", status_code=303)
    return templates2.TemplateResponse('further_actions.html', {'request': request})


@router.get("/confirm", response_class=HTMLResponse)
async def confirm_email(
    token: str,
    service: Annotated[UserService, Depends(get_user_service)],
    redis: Annotated[AsyncRedisClient, Depends(AsyncRedisClient)],
    request: Request
):
    await redis.connect()
    if await redis.token_exists(token):
        data = await redis.get_pending_token(token)
        logger.info('Данные по токену найдены!')

    else:
        logger.info('Срок действия ссылки пользователя истек!')  # добавить данные пользователя

        RedirectResponse(url="/stop_time_link", status_code=303)
        return templates2.TemplateResponse('stop_time_link.html', {'request': request})

    try:
        # Тоже самое что и строчки выше
        excluded_keys = {"username", "password", "password2", "email", "avatar"}
        profile_data = {k: v for k, v in data.items() if k not in excluded_keys}
        profile = ProfileCreate(**profile_data)

        user_create = UserCreate(
            username=data['username'],
            password=data['password'],
            email=data['email'],
            profile=profile,
        )

        # Создаем пользователя и сразу делаем flush, чтобы получить ID
        user = await service.create_user_and_added_in_db(user_create)
        await service.repository.session.flush()

        # Теперь загружаем аватар, если он был предоставлен
        if data.get('avatar'):
            avatar_url = await upload_image(
                user_id=user.id,
                image_file=data['avatar'],
                content_path="users/avatars",
            )
            # Обновляем аватар пользователя
            user.profile.avatar = avatar_url
            await service.repository.session.commit()  # Фиксируем изменения

        logger.info(f"New user registered: {user.username}")

        users = await get_redirect_with_authentication_user(user)

        await redis.delete_pending_token(token)

        return users

    except HTTPException as e:
        logger.warning(f"Registration failed: {e.detail}")
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "current_user": None,
                "form_data": data,
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
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "current_user": None,
                "form_data": data,
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
                "form_data": data,
                "errors": {"": "Произошла ошибка при регистрации"},
            },
            status_code=500,
        )
