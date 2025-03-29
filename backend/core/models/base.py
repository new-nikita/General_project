from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import mapped_column

from core.config import CONVENTION
from utils.case_converter import camel_case_to_snake_case


class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""

    __abstract__ = True
    metadata = MetaData(
        naming_convention=CONVENTION,
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Добавление всем классам наследникам название таблиц названием класса в нижнем регистре.
        """
        return f"{camel_case_to_snake_case(cls.__name__)}s"

    id: Mapped[int] = mapped_column(primary_key=True)
