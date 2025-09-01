"""Вспомогательные классы для тестов."""

from dataclasses import dataclass
from typing import Protocol, TypeVar
from unittest.mock import AsyncMock

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from weblite_framework.database.models import BaseModel
from weblite_framework.repository.base import BaseRepositoryClass

T = TypeVar('T')


class SessionProtocol(Protocol):
    """Протокол для сессии."""

    def add(self, instance: object) -> None:
        """Добавляет экземпляр в сессию."""
        ...

    async def commit(self) -> None:
        """Коммитит транзакцию."""
        ...

    async def flush(self) -> None:
        """Сбрасывает изменения без коммита."""
        ...

    async def refresh(self, instance: object) -> None:
        """Обновляет экземпляр из БД."""
        ...

    async def execute(self, statement: object) -> object:
        """Выполняет SQL запрос."""
        ...

    async def rollback(self) -> None:
        """Откатывает транзакцию."""
        ...

    def begin(self) -> 'AsyncContextManagerProtocol':
        """Создает контекстный менеджер для транзакции."""
        ...


class AsyncContextManagerProtocol(Protocol):
    """Протокол для асинхронного контекстного менеджера."""

    async def __aenter__(self) -> SessionProtocol:
        """Вход в контекст."""
        ...

    async def __aexit__(
        self,
        exc_type: object,
        exc_val: object,
        exc_tb: object,
    ) -> None:
        """Выход из контекста."""
        ...


@dataclass
class TestDTO:
    """Тестовый DTO для проверки маппинга."""

    id_: int
    name: str


class TestModel(BaseModel):
    """Тестовая модель для проверки маппинга."""

    __tablename__ = 'test_models'

    id_: Mapped[int] = mapped_column(
        name='id',
        type_=Integer,
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        name='name',
        type_=String(50),
    )

    def __init__(self, id_: int = 0, name: str = '') -> None:
        """Инициализирует тестовую модель.

        Args:
            id_: Идентификатор модели.
            name: Имя модели.
        """
        super().__init__()
        self.id_ = id_
        self.name = name


class TestRepository(BaseRepositoryClass[TestDTO, TestModel]):
    """Тестовый репозиторий для проверки базового класса."""

    def _model_to_dto(self, model: TestModel) -> TestDTO:
        """Преобразует модель в DTO.

        Args:
            model: ORM модель для преобразования.

        Returns:
            TestDTO: Преобразованный DTO.
        """
        return TestDTO(id_=model.id_, name=model.name)

    def _dto_to_model(self, dto: TestDTO) -> TestModel:
        """Преобразует DTO в модель.

        Args:
            dto: DTO для преобразования.

        Returns:
            TestModel: Преобразованная модель.
        """
        model = TestModel()
        model.id_ = dto.id_
        model.name = dto.name
        return model


def initialize_invalid_class(session: AsyncMock) -> object:
    """Инициализирует неполный класс для тестирования NotImplementedError.

    Args:
        session: Мок сессии.

    Returns:
        TestInvalidRepository: Экземпляр неполного репозитория.
    """

    class TestInvalidRepository(BaseRepositoryClass[TestDTO, TestModel]):
        """Неполная реализация репозитория."""

        def _model_to_dto(self, model: TestModel) -> TestDTO:
            """Преобразует модель в DTO.

            Args:
                model: ORM модель для преобразования.

            Returns:
                TestDTO: Преобразованный DTO.
            """
            return TestDTO(id_=model.id_, name=model.name)

        # Метод _dto_to_model не переопределен - Python сам вызовет
        # NotImplementedError

    return TestInvalidRepository(session=session)  # type: ignore
