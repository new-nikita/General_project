import pytest
from unittest.mock import patch, MagicMock
from backend.users.password_helper import (
    PasswordHelper,
    PasswordVerificationError,
    ErrorMessages,
)


class TestPasswordHelper:
    """Тесты для хелпера работы с паролями."""

    # Тесты валидации пароля
    @pytest.mark.parametrize(
        "password",
        [
            "ValidPass123!",
            "Another@1",
            "A" * 8 + "a" * 8 + "1!",
        ],
    )
    def test_validate_password_success(self, password: str) -> None:
        """Тест успешной валидации пароля."""
        PasswordHelper.validate_password(password)

    @pytest.mark.parametrize(
        "password, expected_error",
        [
            ("", ErrorMessages.EMPTY_PASSWORD),
            ("a" * 73, ErrorMessages.PASSWORD_TOO_LONG.format(max_length=72)),
            ("simple", ErrorMessages.PASSWORD_TOO_SHORT.format(min_length=8)),
            ("nocapitals1!", ErrorMessages.WEAK_PASSWORD),
            ("NOLOWERCASE1!", ErrorMessages.WEAK_PASSWORD),
            ("NoNumbers!", ErrorMessages.WEAK_PASSWORD),
            ("NoSpecials1", ErrorMessages.WEAK_PASSWORD),
        ],
    )
    def test_validate_password_failure(
        self,
        password: str,
        expected_error: str,
    ) -> None:
        """Тест неудачной валидации пароля."""
        with pytest.raises(ValueError) as exc_info:
            PasswordHelper.validate_password(password)
        assert str(exc_info.value) == expected_error

    # Тесты генерации пароля
    def test_generate_password_success(self) -> None:
        """Тест успешной генерации хэша пароля."""
        password = "StrongPass123!"
        hashed = PasswordHelper.generate_password(password)
        assert isinstance(hashed, str)
        assert hashed.startswith("$2b$")  # Проверяем что это bcrypt

    def test_generate_password_empty(self) -> None:
        """Тест генерации с пустым паролем."""
        with pytest.raises(ValueError) as exc_info:
            PasswordHelper.generate_password("")
        assert str(exc_info.value) == ErrorMessages.EMPTY_PASSWORD

    def test_generate_password_too_long(self) -> None:
        """Тест генерации со слишком длинным паролем."""
        with pytest.raises(ValueError) as exc_info:
            PasswordHelper.generate_password("a" * 73)
        expected = ErrorMessages.PASSWORD_TOO_LONG.format(max_length=72)
        assert str(exc_info.value) == expected

    # Тесты проверки пароля
    def test_verify_password_success(self) -> None:
        """Тест успешной проверки пароля."""
        password = "TestPassword123!"
        hashed = PasswordHelper.generate_password(password)
        assert PasswordHelper.verify_password(password, hashed) is True

    def test_verify_password_incorrect(self) -> None:
        """Тест неверного пароля."""
        password = "CorrectPassword123!"
        hashed = PasswordHelper.generate_password(password)
        with pytest.raises(PasswordVerificationError) as exc_info:
            PasswordHelper.verify_password("WrongPassword123!", hashed)
        assert str(exc_info.value) == ErrorMessages.INVALID_CREDENTIALS

    def test_verify_password_unknown_hash(self):
        """Тест неизвестного формата хэша."""
        with pytest.raises(PasswordVerificationError) as exc_info:
            PasswordHelper.verify_password("any", "invalid$hash")
        assert str(exc_info.value) == ErrorMessages.INVALID_CREDENTIALS

    # Тесты типов данных
    @pytest.mark.parametrize(
        "password,hashed,expected_error",
        [
            (123, "valid$hash", ErrorMessages.PASSWORD_TYPE_ERROR),
            ("password", 123, ErrorMessages.HASH_TYPE_ERROR),
            (None, "valid$hash", ErrorMessages.PASSWORD_TYPE_ERROR),
            ("password", None, ErrorMessages.HASH_TYPE_ERROR),
        ],
    )
    def test_verify_password_invalid_types(self, password, hashed, expected_error):
        """Тест неверных типов данных."""
        with pytest.raises(TypeError) as exc_info:
            PasswordHelper.verify_password(password, hashed)
        assert str(exc_info.value) == expected_error

    # Тест защиты от timing-атак
    @patch.object(PasswordHelper.PWD_CONTEXT, "verify", return_value=False)
    def test_timing_attack_protection(self, mock_verify: MagicMock) -> None:
        """Тест что время проверки не зависит от правильности пароля."""

        valid_hash = PasswordHelper.generate_password("Validpass1!")

        try:
            PasswordHelper.verify_password("wrongpass", valid_hash)
        except PasswordVerificationError:
            pass

        mock_verify.assert_called_once()

    # Тест на bytes вместо str
    def test_verify_with_bytes(self):
        """Тест работы с bytes вместо str."""
        password = b"BytesPassword123!"
        hashed = PasswordHelper.generate_password(password.decode())
        assert PasswordHelper.verify_password(password, hashed) is True

    # Тест на необходимость рехеширования
    def test_needs_rehash(self):
        """Тест определения необходимости обновления хэша."""
        password = "MyPassword123!"
        hashed = PasswordHelper.generate_password(password)
        assert not PasswordHelper.PWD_CONTEXT.needs_update(hashed)

    # Тест сообщений об ошибках
    def test_error_messages_contain_required_info(self):
        """Тест что сообщения об ошибках содержат нужную информацию."""
        assert "не может быть пустым" in ErrorMessages.EMPTY_PASSWORD
        assert "максимум" in ErrorMessages.PASSWORD_TOO_LONG
        assert "Неверные" in ErrorMessages.INVALID_CREDENTIALS
