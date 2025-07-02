import pytest
from unittest.mock import AsyncMock
from httpx import AsyncClient



@pytest.mark.asyncio
async def test_reset_password_form_simplified(async_client: AsyncClient, monkeypatch):

    # Мокаем Redis
    mock_redis = AsyncMock()
    mock_redis.get_pending_token.return_value = "user@example.com"
    monkeypatch.setattr("backend.auth.routes.reset_password.AsyncRedisClient", lambda: mock_redis)

    response = await async_client.get("/reset_password?token=valid-token")

    assert response.status_code == 200
    assert "reset" in response.text.lower()



