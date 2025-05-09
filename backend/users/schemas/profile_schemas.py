import re
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, field_validator, model_validator


class ProfileBase(BaseModel):
    """
    Базовая схема профиля пользователя.
    Содержит общие поля и проверки для создания и обновления профиля.
    """

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None

    birth_date: Optional[date] | str = None
    gender: Optional[str] = None

    phone_number: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    street: Optional[str] = None

    bio: Optional[str] = None

    @field_validator("birth_date")
    def validate_birth_date(cls, birth_date: Optional[date | str]) -> Optional[date]:
        """
        Проверяет значение birth_date и проверяет возраст.

        Преобразует строку в объект date.
        Проверяет:
            - Возраст не меньше 14 лет
            - Год рождения не раньше 1900
            - Дата не в будущем

        :param birth_date: Дата рождения в виде строки или объекта date.
        :return: Объект date или None.
        :raises ValueError: Если дата не соответствует требованиям.
        """
        if not birth_date:
            return

        if isinstance(birth_date, date):
            birth_date_str = birth_date.strftime("%Y-%m-%d")
        else:
            birth_date_str = birth_date

        try:
            date_object = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
        except ValueError as e:
            raise ValueError(
                f"Неверный формат даты: {birth_date}. Используйте YYYY-MM-DD."
            ) from e

        today = date.today()
        age = today.year - date_object.year

        if date_object > today:
            raise ValueError("Дата рождения не может быть в будущем.")

        if date_object.year < 1900:
            raise ValueError("Дата рождения не может быть раньше 1900 года.")

        if age < 14:
            raise ValueError("Минимальный возраст регистрации — 14 лет.")

        return date_object

    @model_validator(mode="after")
    def validate_phone_number(self) -> "ProfileBase":
        """
        Валидирует номер телефона:
            - Удаляет лишние символы
            - Проверяет длину (11 цифр)
            - Форматирует под '+7...' если начинается с '8' или '7'

        :return: self
        :raises ValueError: Если номер не прошёл валидацию.
        """
        value = self.phone_number
        if not value:
            return self

        cleaned_value = re.sub(r"[^\d]", "", value)

        if len(cleaned_value) != 11:
            raise ValueError("Номер телефона должен содержать 11 цифр.")

        if cleaned_value.startswith("8"):
            formatted_number = f"+7{cleaned_value[1:]}"
        elif cleaned_value.startswith("7"):
            formatted_number = f"+{cleaned_value}"
        else:
            raise ValueError("Номер телефона должен начинаться с '8' или '7'.")

        # Сохраняем уже отформатированный номер
        object.__setattr__(self, "phone_number", formatted_number)
        return self


class ProfileCreate(ProfileBase):
    """
    Схема для создания профиля пользователя.
    Все поля необязательны.
    """

    pass


class ProfileUpdate(ProfileBase):
    """
    Схема для обновления профиля пользователя.
    Все поля необязательны.
    """

    pass
