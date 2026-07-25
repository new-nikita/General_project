import asyncio
from typing import AsyncGenerator

import fakeredis
import pytest_asyncio
from asgi_lifespan import LifespanManager
from fakeredis.aioredis import FakeRedis
from httpx import ASGITransport, AsyncClient
from fakeredis.aioredis import FakeRedis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.pool import NullPool

from backend.auth.stores.email_token_store import EmailTokenRedisStore
from backend.core.config import settings
from backend.core.models import Base
from backend.core.models.db_helper import DatabaseHelper
from backend.core.redis.client import redis_helper
from main import main_app


@pytest_asyncio.fixture(scope="function")
async def event_loop() -> AsyncGenerator[asyncio.AbstractEventLoop, None]:
    """Фикстура, предоставляющая цикл событий для тестирования."""
    print("Запуск цикла событий для уровня тестирования function")
    loop = asyncio.get_event_loop_policy().new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def db_helper() -> DatabaseHelper:
    """Фикстура, предоставляющая экземпляр `DatabaseHelper`, настроенный для
    тестовой БД.

    Использует NullPool для предотвращения проблем с соединениями между
    тестами.
    """
    return DatabaseHelper(
        url=str(settings.db.url),
        echo=settings.db.echo,
        echo_pool=settings.db.echo_pool,
        pool_size=settings.db.pool_size,
        max_overflow=settings.db.max_overflow,
        poolclass=NullPool,
    )


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database(db_helper: DatabaseHelper) -> AsyncGenerator[None, None]:
    """Асинхронная фикстура для настройки тестовой базы данных.

    Перед запуском тестов создаются все таблицы. После выполнения тестов
    — удаляются.
    """
    assert settings.db.MODE == "TEST"
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield  # тут все действия с базой

    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_helper_for_get_session() -> DatabaseHelper:
    """Фикстура, предоставляющая экземпляр `DatabaseHelper`, настроенный для
    тестовой БД.

    Использует NullPool для предотвращения проблем с соединениями между
    тестами.
    """
    return DatabaseHelper(
        url=str(settings.db.url),
        echo=settings.db.echo,
        echo_pool=settings.db.echo_pool,
        pool_size=settings.db.pool_size,
        max_overflow=settings.db.max_overflow,
        poolclass=NullPool,
    )


@pytest_asyncio.fixture(scope="function")
async def db_session(
    db_helper_for_get_session: DatabaseHelper,
) -> AsyncGenerator[AsyncSession, None]:
    """Фикстура, предоставляющая сессию БД для каждого теста.

    Каждая сессия открывается отдельно и корректно закрывается после
    использования.
    """
    async for session in db_helper_for_get_session.session_getter():
        yield session


@pytest_asyncio.fixture(scope="function")
async def async_client(
    fake_redis_client: FakeRedis,
) -> AsyncGenerator[AsyncClient, None]:
    """Фикстура, предоставляющая HTTP клиент для тестирования API.

    Использует ASGITransport для тестирования FastAPI приложения.
    """
    await redis_helper.init(fake_redis_client)
    async with LifespanManager(main_app):
        async with AsyncClient(
            transport=ASGITransport(app=main_app),
            base_url="http://testserver",
        ) as client:
            yield client
    await redis_helper.close()


@pytest_asyncio.fixture
async def fake_redis_client() -> AsyncGenerator[FakeRedis, None]:
    """Фикстура, предоставляющая фейковый Redis клиент для тестирования."""
    client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield client
    await client.flushall()
    await client.close()


@pytest_asyncio.fixture
async def redis_test_client(
    fake_redis_client: FakeRedis,
) -> AsyncGenerator[EmailTokenRedisStore, None]:
    """Фикстура, предоставляющая Redis store для тестирования."""
    yield EmailTokenRedisStore(redis=fake_redis_client)
