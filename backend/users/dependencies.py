from typing import Optional, Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, Form

from backend.core.common_dependencies import get_db_session
from backend.users.repository import UserRepository
from backend.users.schemas.profile_schemas import ProfileUpdate
from backend.users.services import UserService


async def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserRepository:
    """
    Создает и возвращает экземпляр UserRepository.

    UserRepository предоставляет методы для взаимодействия с таблицей пользователей
    в базе данных. Этот метод внедряет зависимость через FastAPI.

    :param session: Асинхронная сессия базы данных, предоставленная `get_db_session`.
    :returns: UserRepository: Экземпляр репозитория для работы с пользователями.
    """
    return UserRepository(session=session)


async def get_user_service(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    """
    Создает и возвращает экземпляр UserService.

    UserService предоставляет бизнес-логику для работы с пользователями.
    Он использует UserRepository для выполнения операций с базой данных.

    :param repository: Экземпляр репозитория, предоставленный `get_user_repository`.
    :returns: UserService: Экземпляр сервиса для работы с пользователями.
    """
    return UserService(repository=repository)


async def get_update_form(
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    middle_name: Optional[str] = Form(None),
    birth_date: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    phone_number: Optional[str] = Form(None),
    country: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    street: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
) -> ProfileUpdate:
    """
    Принимает данные формы редактирования профиля из запроса и возвращает объект ProfileUpdate.
    Используется как зависимость в роутах, чтобы автоматически собрать данные из формы.

    :return: Объект `ProfileUpdate` с данными из формы.
    """
    return ProfileUpdate(
        first_name=first_name,
        last_name=last_name,
        middle_name=middle_name,
        birth_date=birth_date,
        gender=gender,
        phone_number=phone_number,
        country=country,
        city=city,
        street=street,
        bio=bio,
    )
