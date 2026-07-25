import pytest


@pytest.mark.xfail
async def test_save_and_get_token(redis_test_client):
    token = "token123"
    email = "user@example.com"

    # Тестируем сохранение токена
    result = await redis_test_client.save_pending_email_token(token, email)
    assert result is True

    # Тестируем получение токена
    value = await redis_test_client.get_pending_token(token)
    assert value == email

    # Проверяем существование токена
    exists = await redis_test_client.token_exists(token)
    assert exists is True

    # Удаляем токен
    deleted = await redis_test_client.delete_pending_token(token)
    assert deleted is True

    # После удаления токен не должен существовать
    exists_after_delete = await redis_test_client.token_exists(token)
    assert exists_after_delete is False
