from datetime import date, timedelta
from typing import Optional

from faker import Faker

from backend.users.schemas.profile_schemas import ProfileCreate

fake = Faker("ru_RU")


def create_profile_create_data(
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    middle_name: Optional[str] = None,
    birth_date: Optional[date] = None,
    gender: Optional[str] = None,
    phone_number: Optional[str] = None,
    country: Optional[str] = None,
    city: Optional[str] = None,
    street: Optional[str] = None,
    bio: Optional[str] = None,
) -> ProfileCreate:
    """
    Генерирует случайные данные для ProfileCreate.
    Можно переопределять любые поля.
    """

    return ProfileCreate(
        first_name=first_name or fake.first_name(),
        last_name=last_name or fake.last_name(),
        middle_name=middle_name or fake.first_name(),
        birth_date=birth_date or date.today() - timedelta(days=365 * 18),
        gender=gender or fake.random_element(elements=("Мужчина", "Женщина")),
        phone_number=phone_number or fake.phone_number(),
        country=country or fake.country(),
        city=city or fake.city(),
        street=street or fake.street_address(),
        bio=bio or fake.text(max_nb_chars=200),
    )


def create_profile_create_none_fields(
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    middle_name: Optional[str] = None,
    birth_date: Optional[date] = None,
    gender: Optional[str] = None,
    phone_number: Optional[str] = None,
    country: Optional[str] = None,
    city: Optional[str] = None,
    street: Optional[str] = None,
    bio: Optional[str] = None,
) -> ProfileCreate:
    """
    Генерирует случайные данные для ProfileCreate.
    Можно переопределять любые поля.
    """

    return ProfileCreate(
        first_name=None if first_name is None else (first_name or fake.first_name()),
        last_name=None if last_name is None else (last_name or fake.last_name()),
        middle_name=None if middle_name is None else (middle_name or fake.first_name()),
        birth_date=(
            None
            if birth_date is None
            else (birth_date or date.today() - timedelta(days=365 * 18))
        ),
        gender=(
            None
            if gender is None
            else (gender or fake.random_element(elements=("Мужчина", "Женщина")))
        ),
        phone_number=(
            None if phone_number is None else (phone_number or fake.phone_number())
        ),
        country=None if country is None else (country or fake.country()),
        city=None if city is None else (city or fake.city()),
        street=None if street is None else (street or fake.street_address()),
        bio=None if bio is None else (bio or fake.text(max_nb_chars=200)),
    )
