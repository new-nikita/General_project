import logging
from typing import Annotated
from datetime import timedelta


import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.exc import DBAPIError

from core.config import settings
from core.models import User

from users.schemas import UserCreate, UserResponse
from users.services import UserService, get_service
from users.tokens import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from auth.authorization import authenticate_user, get_current_user

logging.basicConfig(
    format=settings.logging.log_format, level=settings.logging.log_level_value
)
logger = logging.getLogger(__name__)
# TODO добавить количество попыток входа и хранить кол-во попыток, например в redis

app = FastAPI(
    title="User Registration API",
    description="API для регистрации и управления пользователями",
    version="1.0.0",
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

templates = Jinja2Templates(directory=settings.template_dir)


def handle_error(
    message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
):
    """
    Обрабатывает ошибки и логирует их.

    Args:
        message (str): Сообщение об ошибке.
        status_code (int): HTTP-статус ошибки.

    Raises:
        HTTPException: Возвращает HTTP-ошибку с указанным статусом и сообщением.
    """
    logger.error(message)
    raise HTTPException(status_code=status_code, detail=message)


@app.get(
    "/hello",
    response_class=HTMLResponse,
    tags=["User"],
    summary="Приветственная страница (с cookies)",
    description="""
    Страница доступна только для авторизованных пользователей.
    Токен извлекается из HTTP-Only cookie.

    Для тестирования используйте браузер или Postman, так как Swagger не поддерживает cookies.
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "Успешный доступ к странице",
            "content": {
                "text/html": {
                    "example": "<html><body><h1>Hello, username!</h1></body></html>"
                }
            },
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Пользователь не авторизован",
            "content": {
                "application/json": {"example": {"detail": "Not authenticated"}}
            },
        },
    },
)
async def index(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """
    Приветственная страница для авторизованных пользователей.

    Args:
        request (Request): Запрос.
        current_user (User): Текущий авторизованный пользователь.

    Returns:
        HTMLResponse: Отрендеренный шаблон.
    """
    return templates.TemplateResponse(
        "index.html", {"request": request, "user": current_user.username}
    )


@app.post(
    "/login",
    tags=["User"],
    response_class=Response,
    summary="Аутентификация пользователя",
    description="""
    Аутентифицирует пользователя по имени пользователя и паролю.
    Устанавливает JWT-токен в HTTP-Only cookie.

    После успешной аутентификации токен можно использовать для доступа к защищенным ресурсам.
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "Успешная аутентификация",
            "content": {"text/plain": {"example": "Authentication successful"}},
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Неверное имя пользователя или пароль",
            "content": {
                "application/json": {
                    "example": {"detail": "Incorrect username or password"}
                }
            },
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Внутренняя ошибка сервера",
            "content": {
                "application/json": {"example": {"detail": "Internal Server Error"}}
            },
        },
    },
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: Annotated[UserService, Depends(get_service)],
):
    """
    Аутентифицирует пользователя.

    Args:
        form_data (OAuth2PasswordRequestForm): Форма с данными пользователя (username, password).
        service (UserService): Сервис для работы с пользователями.

    Returns:
        Response: Ответ с установленной HTTP-Only cookie.

    Raises:
        HTTPException: 401 при неверных данных или 500 при внутренней ошибке.
    """
    user = await authenticate_user(service, form_data.username, form_data.password)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    logger.info(f"User {user.username} successfully authenticated")

    # Установка HTTP-Only cookie
    response = Response(content="Authentication successful", media_type="text/plain")
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        samesite="lax",  # Защита от CSRF
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return response


@app.post(
    "/register",
    tags=["User"],
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    description="""
    Регистрирует нового пользователя в системе.

    Требования:
    - username: 3-20 символов
    - email: валидный email адрес
    - password: минимум 8 символов
    """,
    responses={
        status.HTTP_201_CREATED: {
            "description": "Пользователь успешно зарегистрирован",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "username": "testuser",
                        "email": "test@example.com",
                        "created_at": "2023-01-01T12:00:00Z",
                    }
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Пользователь с таким email или username уже существует",
            "content": {
                "application/json": {
                    "example": {"detail": "User with this email already exists"}
                }
            },
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Ошибка валидации входных данных",
            "content": {
                "application/json": {"example": {"detail": "Invalid input data"}}
            },
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Внутренняя ошибка сервера",
            "content": {
                "application/json": {"example": {"detail": "Internal Server Error"}}
            },
        },
    },
)
async def register_user(
    user_data: UserCreate,
    service: Annotated[UserService, Depends(get_service)],
) -> UserResponse:
    """
    Регистрация нового пользователя.

    Args:
        user_data (UserCreate): Данные для регистрации пользователя.
        service (UserService): Сервис для работы с пользователями.

    Returns:
        UserResponse: Данные зарегистрированного пользователя.

    Raises:
        HTTPException: 400 если пользователь уже существует, 422 при невалидных данных, 500 при внутренних ошибках.
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


@app.post(
    "/logout",
    tags=["User"],
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
async def logout():
    """
    Выход пользователя из системы.

    Returns:
        Response: Ответ с удаленной cookie.

    Side Effects:
        Удаляет HTTP-Only cookie с токеном.
    """
    response = Response(
        content="Logout successful",
        media_type="text/plain",
        status_code=status.HTTP_200_OK,
    )
    # Удаляем токен из cookie
    response.delete_cookie(
        key="access_token", httponly=True, secure=True, samesite="lax"
    )
    logger.info("User successfully logged out")
    return response


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
