import asyncio
from asyncio import AbstractEventLoop
from typing import AsyncGenerator, Generator, Any

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.pool import NullPool

from backend.core.config import settings
from backend.core.models import Base
from backend.core.models.db_helper import DatabaseHelper
from main import main_app


@pytest.fixture(scope="function")
def event_loop() -> Generator[AbstractEventLoop, Any, None]:
    """
    Фикстура для создания и управления event loop'ом на уровне сессии.
    Убеждается, что все асинхронные тесты используют один и тот же event loop.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="function", autouse=True)
def db_helper() -> DatabaseHelper:
    """
    Фикстура, предоставляющая экземпляр `DatabaseHelper`, настроенный для тестовой БД.
    Использует NullPool для предотвращения проблем с соединениями между тестами.
    """
    return DatabaseHelper(
        url=str(settings.db.url),
        echo=settings.db.echo,
        echo_pool=settings.db.echo_pool,
        pool_size=settings.db.pool_size,
        max_overflow=settings.db.max_overflow,
        poolclass=NullPool,
    )


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_test_database(db_helper: DatabaseHelper) -> AsyncGenerator[None, None]:
    """
    Асинхронная фикстура для настройки тестовой базы данных.
    Перед запуском тестов создаются все таблицы. После выполнения тестов — удаляются.
    """
    assert settings.db.MODE == "TEST"
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield  # тут все действия с базой

    # async with db_helper.engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def db_session(db_helper: DatabaseHelper) -> AsyncGenerator[AsyncSession, None]:
    """
    Фикстура, предоставляющая сессию БД для каждого теста.
    Каждая сессия открывается отдельно и корректно закрывается после использования.
    """
    async for session in db_helper.session_getter():
        yield session
        await session.close()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Фикстура, предоставляющая HTTP клиент для тестирования API.
    Использует ASGITransport для тестирования FastAPI приложения.
    """
    async with LifespanManager(main_app):
        async with AsyncClient(
            transport=ASGITransport(app=main_app),
            base_url="http://testserver",
        ) as client:
            yield client
