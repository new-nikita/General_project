from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr


class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(self) -> str:
        """
        Добавление всем классам наследникам название таблиц название класса в нижнем регистре,
        с добавлением 's' обозначающее множественное число.
        """
        return f"{self.__class__.__name__.lower()}s"

    id: Mapped[int] = mapped_column(primary_key=True)
