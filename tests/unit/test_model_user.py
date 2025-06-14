import pytest

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.models import User


@pytest.mark.asyncio
class TestUserModel:
    """Группа тестов для модели пользователя User."""

    async def test_create_user(self, db_session: AsyncSession) -> None:
        """Тестирование корректного создания пользователя в базе данных."""

        new_user = User(
            username="test_user",
            hashed_password="hashed_password_123",
            email="test@example.com",
        )
        db_session.add(new_user)
        await db_session.commit()

        result = await db_session.execute(
            select(User).where(User.username == "test_user")
        )
        user = result.scalars().first()

        assert user is not None
        assert user.email == "test@example.com"

        await db_session.delete(user)
        await db_session.commit()

    async def test_multiple_users(self, db_session: AsyncSession) -> None:
        """Тестирование на ошибку дублирующего username."""
        user1 = User(
            username="unique_user", hashed_password="pass1234", email="unique1@test.com"
        )
        db_session.add(user1)
        await db_session.commit()

        user2 = User(
            username="unique_user",
            hashed_password="pass1234",
            email="unique2@test.com",
        )
        db_session.add(user2)

        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()

        assert "duplicate" in str(exc_info.value).lower()

        await db_session.rollback()
        await db_session.delete(user1)
        await db_session.commit()
