import logging
from datetime import date
from typing import Annotated, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Form,
)

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import EmailStr, ValidationError

from core.config import settings
from core.models import User

from users.dependencies import get_user_service

from users.schemas.users_schemas import ProfileCreate, UserCreate
from users.services import UserService


from auth.authorization import (
    get_current_user_from_cookie,
)


logging.basicConfig(
    format=settings.logging.log_format, level=settings.logging.log_level_value
)
logger = logging.getLogger(__name__)

router = APIRouter()


templates = Jinja2Templates(directory=settings.template_dir / "users")


@router.get("/register", response_class=HTMLResponse)
async def get_register_page(
    request: Request,
    current_user: Annotated[
        Optional[User], Depends(get_current_user_from_cookie)
    ] = None,
):
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
    service: Annotated[UserService, Depends(get_user_service)],
    username: str = Form(...),
    password: str = Form(...),
    password2: str = Form(...),
    email: EmailStr = Form(...),
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    middle_name: Optional[str] = Form(None),
    birth_date: Optional[date] = Form(None),
    gender: Optional[str] = Form(None),
    phone_number: Optional[str] = Form(None),
    country: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    street: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
):
    """
    Обрабатывает регистрацию нового пользователя.

    :return: Редирект на страницу входа при успехе или форму с ошибками.
    """
    # Сохраняем введенные данные для повторного отображения формы при ошибке
    form_data = {
        "username": username,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "middle_name": middle_name,
        "birth_date": birth_date.isoformat() if birth_date else "",
        "gender": gender,
        "phone_number": phone_number,
        "country": country,
        "city": city,
        "street": street,
        "bio": bio,
    }

    try:
        if password != password2:
            raise HTTPException(status_code=400, detail="Пароли не совпадают")

        # Создание объекта UserCreate
        user_create = UserCreate(
            username=username,
            password=password,
            email=email,
            profile=ProfileCreate(
                first_name=first_name,
                last_name=last_name,
                birth_date=birth_date,
                gender=gender,
                phone_number=phone_number,
                country=country,
                city=city,
                street=street,
                bio=bio,
            ),
        )

        # Создание пользователя
        user = await service.create_user_and_added_in_db(user_create)
        logger.info(f"New user registered: {user.username}")

        # Перенаправление с сообщением об успехе
        response = RedirectResponse(url="/login", status_code=303)
        response.set_cookie(
            "register_success",
            "true",
            max_age=5,  # Короткое время жизни для одноразового сообщения
            path="/login",
        )
        return response

    except HTTPException as e:
        logger.warning(f"Registration failed: {e.detail}")
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "current_user": None,
                "form_data": form_data,
                "errors": {"__all__": e.detail},
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
                "form_data": form_data,
                "errors": errors,
            },
            status_code=400,
        )

    except Exception as e:
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "current_user": None,
                "form_data": form_data,
                "errors": {"": "Произошла ошибка при регистрации"},
            },
            status_code=500,
        )
