import asyncio
from typing import AsyncGenerator

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.pool import NullPool

from backend.core.config import settings
from backend.core.models.db_helper import DatabaseHelper


@pytest_asyncio.fixture(scope="class")
async def event_loop() -> AsyncGenerator[asyncio.AbstractEventLoop, None]:
    """Фикстура, предоставляющая цикл событий для тестирования."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="class")
async def db_helper_class() -> DatabaseHelper:
    """Фикстура, предоставляющая экземпляр `DatabaseHelper`, для использования
    в тестах классов."""
    return DatabaseHelper(
        url=str(settings.db.url),
        echo=settings.db.echo,
        echo_pool=settings.db.echo_pool,
        pool_size=settings.db.pool_size,
        max_overflow=settings.db.max_overflow,
        poolclass=NullPool,
    )


@pytest_asyncio.fixture(scope="class")
async def db_session(
    db_helper_class: DatabaseHelper,
) -> AsyncGenerator[AsyncSession, None]:
    """Фикстура, предоставляющая сессию БД для каждого теста класса."""
    async for session in db_helper_class.session_getter():
        yield session
