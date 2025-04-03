import logging
from typing import TypeVar, Type, Any, Optional, Sequence

from sqlalchemy import select, update, delete, Select, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from fastapi import HTTPException, status


T = TypeVar("T")

logger = logging.getLogger(__name__)


class BaseRepository[T]:
    """
    Абстрактный базовый репозиторий для выполнения CRUD-операций.
    Предоставляет универсальные методы для работы с моделями SQLAlchemy.
    """

    def __init__(self, session: AsyncSession, model: Type[T]):
        """
        Инициализация базового репозитория.

        :param session: Асинхронная сессия SQLAlchemy.
        :param model: Класс модели SQLAlchemy.
        """
        self.session = session
        self.model = model

    async def get_by_id(self, id_: int) -> T:
        """
        Возвращает объект по его ID.

        :param id_: ID объекта.
        :return: Объект модели.
        :raises HTTPException: Если объект не найден или произошла ошибка базы данных.
        """
        stmt: Select = select(self.model).where(self.model.id == id_)
        try:
            result: Result = await self.session.execute(stmt)
            return result.scalar_one()
        except NoResultFound:
            logger.warning(f"Объект {self.model.__name__} с ID {id_} не найден")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Объект {self.model.__name__} с ID {id_} не найден",
            )
        except SQLAlchemyError as error:
            logger.error(
                "Ошибка при получении {self.model.__name__} с ID {id_}: %s",
                str(error),
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка базы данных",
            )

    async def get_all(self) -> Sequence[T]:
        """
        Возвращает все объекты модели.

        :return: Список объектов модели.
        :raises HTTPException: Если произошла ошибка базы данных.
        """
        stmt = select(self.model)
        try:
            result = await self.session.execute(stmt)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(
                f"Ошибка при получении всех объектов {self.model.__name__}: {str(e)}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка базы данных",
            )

    async def create(self, data: dict[str, Any]) -> T:
        """
        Создает новый объект в базе данных.

        :param data: Словарь с данными для создания объекта.
        :return: Созданный объект модели.
        :raises HTTPException: Если произошла ошибка базы данных.
        """
        instance = self.model(**data)
        try:
            self.session.add(instance)
            await self.session.commit()
            await self.session.refresh(instance)
        except SQLAlchemyError as e:
            logger.error(
                f"Ошибка при создании объекта {self.model.__name__}: {str(e)}",
                exc_info=True,
            )
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка базы данных",
            )
        return instance

    async def update(self, id_: int, data: dict[str, Any]) -> Optional[T]:
        """
        Обновляет объект по его ID.

        :param id_: ID объекта для обновления.
        :param data: Словарь с новыми данными.
        :return: Обновленный объект модели или None, если объект не найден.
        :raises HTTPException: Если произошла ошибка базы данных.
        """
        stmt = (
            update(self.model)
            .where(self.model.id == id_)
            .values(**data)
            .returning(self.model)
        )
        try:
            result = await self.session.execute(stmt)
            await self.session.commit()
            updated_obj = result.scalar_one_or_none()
            if updated_obj is None:
                logger.warning(
                    f"Объект {self.model.__name__} с ID {id_} не найден для обновления"
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Объект {self.model.__name__} с ID {id_} не найден",
                )
            return updated_obj
        except SQLAlchemyError as e:
            logger.error(
                f"Ошибка при обновлении объекта {self.model.__name__} с ID {id_}: {str(e)}",
                exc_info=True,
            )
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка базы данных",
            )

    async def delete(self, id_: int) -> bool:
        """
        Удаляет объект по его ID.

        :param id_: ID объекта для удаления.
        :return: True, если объект удален, иначе False.
        :raises HTTPException: Если произошла ошибка базы данных.
        """
        stmt = delete(self.model).where(self.model.id == id_)
        try:
            result = await self.session.execute(stmt)
            await self.session.commit()
            if result.rowcount == 0:
                logger.warning(
                    f"Объект {self.model.__name__} с ID {id_} не найден для удаления"
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Объект {self.model.__name__} с ID {id_} не найден",
                )
            return True
        except SQLAlchemyError as e:
            logger.error(
                f"Ошибка при удалении объекта {self.model.__name__} с ID {id_}: {str(e)}",
                exc_info=True,
            )
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка базы данных",
            )
