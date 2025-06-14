import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "url",
    [
        "/profile/1",
        "/",
        "/login",
        "/register",
    ],
)
async def test_all_views_to_status_200(async_client: AsyncClient, url: str) -> None:
    response = await async_client.get(url)
    assert response.status_code == status.HTTP_200_OK
