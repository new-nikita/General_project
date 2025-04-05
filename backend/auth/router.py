import logging
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Request,
    Response,
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.exc import DBAPIError

from core.config import settings
from core.models import User

from users.dependencies import get_user_service
from users.schemas import UserCreate, UserResponse
from users.services import UserService
from users.tokens import (
    create_access_token,
    create_refresh_token,
    set_access_token_to_cookie,
    set_refresh_token_to_cookie,
)
from auth.authorization import (
    authenticate_user,
    get_current_user_from_cookie,
)


logging.basicConfig(
    format=settings.logging.log_format, level=settings.logging.log_level_value
)
logger = logging.getLogger(__name__)
# TODO добавить количество попыток входа и хранить кол-во попыток, например в redis

router = APIRouter(tags=["Auth"])


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

templates = Jinja2Templates(directory=settings.template_dir)


def handle_error(
    message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
):
    """
    Обрабатывает ошибки и выбрасывает HTTPException.

    :param message: Сообщение об ошибке.
    :param status_code: Код состояния HTTP.
    :raises HTTPException: Исключение с указанным сообщением и кодом.
    """
    logger.error(message)
    raise HTTPException(status_code=status_code, detail=message)


@router.get("/hello", response_class=HTMLResponse)
async def index(
    request: Request, current_user: User = Depends(get_current_user_from_cookie)
):
    """
    Отображает главную страницу с приветствием.

    :param request: Запрос FastAPI.
    :param current_user: Текущий авторизованный пользователь.
    :return: HTML-страница с приветствием.
    """
    return templates.TemplateResponse(
        "index.html", {"request": request, "user": current_user}
    )


@router.post("/login", response_class=Response)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: Annotated[UserService, Depends(get_user_service)],
    response: Response,
):
    """
    Аутентифицирует пользователя и устанавливает JWT-токены в HTTP-Only cookies.

    :param form_data: Форма с данными пользователя (username, password).
    :param service: Сервис для работы с пользователями.
    :return: Ответ с установленными HTTP-Only cookies.
    :raises HTTPException: 401 при неверных данных или 500 при внутренней ошибке.
    """
    user = await authenticate_user(service, form_data.username, form_data.password)

    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    logger.info(f"User {user.username} successfully authenticated")

    response = Response(content="Authentication successful", media_type="text/plain")
    set_access_token_to_cookie(access_token, response)
    set_refresh_token_to_cookie(refresh_token, response)
    return response


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
)
async def register_user(
    user_data: UserCreate,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    """
    Регистрирует нового пользователя.

    :param user_data: Данные для создания нового пользователя.
    :param service: Сервис для работы с пользователями.
    :return: Созданный пользователь.
    :raises HTTPException: 422 при невалидных данных, 503 при ошибках базы данных, 500 при других ошибках.
    """
    try:
        user = await service.create_user_and_added_in_db(user_data)
        return UserResponse.model_validate(user)

    except DBAPIError as e:
        logger.error(f"Ошибка базы данных: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ошибка подключения к базе данных",
        )

    except ValueError as e:
        logger.warning(f"Невалидные данные: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )

    except Exception as e:
        logger.critical(f"Непредвиденная ошибка: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера",
        )


@router.post(
    "/logout",
    summary="Выход пользователя из системы",
    description="""
    Выходит из системы, удаляя JWT-токен из HTTP-Only cookie.

    После выхода пользователь больше не сможет получить доступ к защищенным ресурсам.
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "Успешный выход из системы",
            "content": {"text/plain": {"example": "Logout successful"}},
        },
    },
)
async def logout(
    response: Response,
):
    """
    Выходит из системы, удаляя токены из HTTP-Only cookies.

    :param response: Ответ FastAPI.
    :return: Сообщение об успешном выходе.
    """
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Successfully logged out"}


@router.get(
    "/users",
    response_model=list[UserResponse],
    summary="Получить всех пользователей",
)
async def get_users(
    service: Annotated[UserService, Depends(get_user_service)],
) -> list[UserResponse]:
    """
    Получает список всех пользователей.

    :param service: Сервис для работы с пользователями.
    :return: Список пользователей.
    """
    users_db = await service.repository.get_all()
    return [UserResponse.model_validate(user) for user in users_db]


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
)
async def get_user(
    user_id: int, service: Annotated[UserService, Depends(get_user_service)]
) -> UserResponse:
    """
    Получает пользователя по его ID.

    :param user_id: ID пользователя.
    :param service: Сервис для работы с пользователями.
    :return: Пользователь.
    :raises HTTPException: 404 если пользователь не найден.
    """
    user = await service.repository.get_by_id(user_id)
    if not user:
        raise handle_error(status_code=404, message="User not found")
    return UserResponse.model_validate(user)
