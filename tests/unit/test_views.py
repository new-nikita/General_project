import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "url",
    [
        "/profile/100",
        "/",
        "/login",
        "/register",
        "/initial_register",
        "/forgot_password",
        "/reset_password",
    ],
)
async def test_all_views_to_status_200(async_client: AsyncClient, url: str) -> None:
    response = await async_client.get(url)
    assert response.status_code == status.HTTP_200_OK
