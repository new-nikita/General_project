import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.models import User


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "url",
    [
        "/profile/",
        "/",
        "/login",
        "/register",
        "/initial_register",
        "/forgot_password",
    ],
)
async def test_all_views_to_status_200(
    async_client: AsyncClient,
    url: str,
    db_session: AsyncSession,
) -> None:
    """Тестирует все роуты на статус 200."""
    if url == "/profile/":
        user = User(username="test", hashed_password="test", email="test@test.com")
        db_session.add(user)  # TODO: сделать нормальные моки
        await db_session.commit()
        user_id = user.id
        response = await async_client.get(f"{url}{user_id}")
        await db_session.delete(user)
        await db_session.commit()
        assert response.status_code == status.HTTP_200_OK
        await db_session.close()
    else:
        response = await async_client.get(url)
        assert response.status_code == status.HTTP_200_OK
