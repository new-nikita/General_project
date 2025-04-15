import re

from datetime import date
from typing import Optional

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    ValidationError,
)


class ProfileCreate(BaseModel):
    """
    Схема для создания профиля пользователя.
    Все поля являются необязательными.
    """

    first_name: Optional[str]
    last_name: Optional[str]
    middle_name: Optional[str]

    birth_date: Optional[date] | str
    gender: Optional[str]

    phone_number: Optional[str]
    country: Optional[str]
    city: Optional[str]
    street: Optional[str]

    bio: Optional[str]

    @field_validator("phone_number")
    def validate_phone_number(cls, value: str | None) -> str | None:
        """
        Валидирует и форматирует номер телефона.
        Если номер начинается с '8', преобразуем его в формат '+7'.
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
