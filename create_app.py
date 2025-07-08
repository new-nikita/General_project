import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from backend.core.config import BASE_DIR, settings
from backend.core.models import db_helper
from backend.utils.save_images import BASE_STATIC_DIR

os.makedirs(BASE_STATIC_DIR, exist_ok=True)

STATIC_DIR = BASE_DIR / "frontend" / "static"
logging.basicConfig(
    level=logging.INFO,
    format=settings.logging.log_format,
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Контекстный менеджер для управления жизненным циклом приложения.

    Выполняет:
    - Инициализацию ресурсов при старте
    - Корректное освобождение ресурсов при завершении
    """
    logger.info("Начало работы приложения")
    yield  # Здесь приложение работает
    logger.info("Конец работы приложения")
    await db_helper.dispose()  # закрываем все подключения к бд.


def create_app() -> FastAPI:
    """Фабрика для создания экземпляра FastAPI приложения.

    :return: FastAPI: Настроенный экземпляр приложения
    """
    application = FastAPI(lifespan=lifespan)
    application.mount(
        "/static",
        StaticFiles(directory=str(STATIC_DIR)),
        name="static",
    )
    application.mount(
        "/client_files",
        StaticFiles(directory=str(BASE_STATIC_DIR)),
        name="client_files",
    )
    return application
