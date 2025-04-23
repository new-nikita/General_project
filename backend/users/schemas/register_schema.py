import datetime
import re
from datetime import date, datetime
from typing import Optional

from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    constr,
    field_validator,
    model_validator,
    ValidationError,
)


class RegisterForm(BaseModel):
    username: constr(min_length=3, max_length=20) = Field(
        ...,
        description="Username must be between 3 and 20 characters "
        "and can only contain letters, numbers, and underscores",
    )
    password: str = Field(
        ..., min_length=8, description="Password must contain at least 8 characters"
    )
    password2: str = Field(..., description="Confirm password")
    email: EmailStr = Field(..., max_length=100)

    # Profile fields
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    phone_number: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    street: Optional[str] = None
    bio: Optional[str] = None

    @field_validator("birth_date")
    def validate_birth_date(cls, birth_date: str | None):
        """
        Валидирует дату рождения.
        Проверяет, что дата рождения не в будущем.
        """
        if birth_date is None:
            return

        date_object: date = datetime.strptime(birth_date, "%Y-%m-%d").date()
        if date_object.year > date.today().year - 14:
            raise ValidationError("Минимальный возраст регистрации - 14 лет.")
        if date_object.year < 1900:
            raise ValidationError("Дата рождения не может быть раньше 1900 года.")
        return date_object

    @field_validator("phone_number")
    def validate_phone_number(cls, value: str | None) -> str | None:
        """
        Валидирует и форматирует номер телефона.
        Если номер начинается с '8', преобразует его в формат '+7'.
        """
        if not value:
            return ""

        # Удаляем пробелы, дефисы и скобки из номера
        cleaned_value = re.sub(r"[^\d]", "", value)

        # Проверяем длину номера (например, 11 цифр для РФ)
        if len(cleaned_value) != 11:
            raise ValidationError("Номер телефона должен содержать 11 цифр.")

        if cleaned_value.startswith("8"):
            formatted_number = f"+7{cleaned_value[1:]}"
        elif cleaned_value.startswith("7"):
            formatted_number = f"+{cleaned_value}"
        else:
            raise ValidationError("Номер телефона должен начинаться с '8' или '7'.")

        return formatted_number

    @model_validator(mode="after")
    def check_passwords_match(self) -> "RegisterForm":
        """
        Проверяет, совпадают ли пароли.
        """
        if self.password != self.password2:
            raise ValidationError("Пароли не совпадают.")
        return self
