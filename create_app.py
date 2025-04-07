import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from core.models import db_helper

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: \t  %(message)s \t  || %(asctime)s",
    # filename="app.log",
)
logger = logging.getLogger(__name__)

# TODO добавить все необходимые мидлваеры


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Контекстный менеджер для управления жизненным циклом приложения.

    Выполняет:
    - Инициализацию ресурсов при старте
    - Корректное освобождение ресурсов при завершении
    """
    logger.info("Начало работы приложения")
    yield  # Здесь приложение работает
    logger.info("Конец работы приложения")
    await db_helper.dispose()  # закрываем все подключения к бд.


def create_app() -> FastAPI:
    """
    Фабрика для создания экземпляра FastAPI приложения.

    :return: FastAPI: Настроенный экземпляр приложения
    """
    application = FastAPI(lifespan=lifespan)
    application.mount("/static", StaticFiles(directory="static"), name="static")
    return application
