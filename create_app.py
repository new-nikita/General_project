import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from backend.core.config import BASE_DIR, settings
from backend.core.models import db_helper
from backend.core.redis.client import redis_helper
from backend.utils.save_images import BASE_STATIC_DIR

os.makedirs(BASE_STATIC_DIR, exist_ok=True)

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
    try:
        await redis_helper.init()
    except Exception as error:
        logger.warning("Redis недоступен при старте: %s", error)
    yield  # Здесь приложение работает
    logger.info("Конец работы приложения")
    await redis_helper.close()
    await db_helper.dispose()  # закрываем все подключения к бд.


def create_app() -> FastAPI:
    """Фабрика для создания экземпляра FastAPI приложения.

    :return: FastAPI: Настроенный экземпляр приложения
    """
    application = FastAPI(lifespan=lifespan)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.mount(
        "/media",
        StaticFiles(directory="client_files"),
        name="media",
    )

    return application
