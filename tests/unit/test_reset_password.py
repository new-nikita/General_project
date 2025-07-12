import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.xfail
async def test_reset_password(
    async_client: AsyncClient,
    redis_test_client,
):
    token = "token123"
    email = "user@example.com"
    url = f"/reset_password?token={token}"

    await redis_test_client.save_pending_email_token(token, email)

    response = await async_client.get(url)
    assert response.status_code == status.HTTP_200_OK
