from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.models.db_helper import db_helper


async def get_db_session() -> AsyncSession:
    """
    Возвращает асинхронную сессию базы данных.

    Использует `db_helper.session_getter` для создания новой сессии SQLAlchemy.
    Сессия автоматически закрывается после завершения использования.

    Returns:
        AsyncSession: Асинхронная сессия SQLAlchemy.
    """
    async for session in db_helper.session_getter():
        yield session
