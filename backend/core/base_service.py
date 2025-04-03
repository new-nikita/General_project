from abc import abstractmethod
from typing import Any, TypeVar, Sequence

T = TypeVar("T")

# TODO возможно не делать или сделать, но не абстрактным


class BaseService([T]):
    """
    Абстрактный базовый сервис для выполнения CRUD-операций.
    Предоставляет универсальные методы для работы с данными через репозиторий.
    """

    def __init__(self, repository):
        """
        Инициализация базового сервиса.

        :param repository: Экземпляр репозитория, который предоставляет доступ к данным.
        """
        self.repository = repository

    @abstractmethod
    async def get_by_id(self, id_: int) -> T | None:
        """
        Возвращает объект по его ID.

        :param id_: ID объекта.
        :return: Объект или None, если объект не найден.
        """
        pass

    @abstractmethod
    async def get_all(self) -> Sequence[T]:
        """
        Возвращает коллекцию всех объектов.

        :return: Список объектов.
        """
        pass

    @abstractmethod
    async def create(self, data: dict[str, Any]) -> T:
        """
        Создает новый объект.

        :param data: Словарь с данными для создания объекта.
        :return: Созданный объект.
        """
        pass

    @abstractmethod
    async def update(self, id_: int, data: dict[str, Any]) -> T | None:
        """
        Обновляет объект по его ID.

        :param id_: ID объекта для обновления.
        :param data: Словарь с новыми данными.
        :return: Обновленный объект или None, если объект не найден.
        """
        pass

    @abstractmethod
    async def delete(self, id_: int) -> bool:
        """
        Удаляет объект по его ID.

        :param id_: ID объекта для удаления.
        :return: True, если объект удален, иначе False.
        """
        pass
