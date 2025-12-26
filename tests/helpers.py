"""Вспомогательные классы для тестов."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, ClassVar, Dict, Optional, Protocol, TypeVar
from unittest.mock import AsyncMock, Mock

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from weblite_framework.database.models import BaseModel
from weblite_framework.repository.base import BaseRepositoryClass
from weblite_framework.services.base import BaseServiceClass

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


@dataclass
class ServiceTestDTO:
    """Тестовый DTO для проверки маппинга сервиса."""

    id_: Optional[int] = None
    name: Optional[str] = None
    email: Optional[str] = None
    resume_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __eq__(self, other: object) -> bool:
        """Проверяет равенство объектов.

        Args:
            other: Другой объект для сравнения

        Returns:
            bool: True если объекты равны, иначе False
        """
        if not isinstance(other, ServiceTestDTO):
            return False

        return all(
            [
                self.id_ == other.id_,
                self.name == other.name,
                self.email == other.email,
                self.resume_id == other.resume_id,
                self.created_at == other.created_at,
                self.updated_at == other.updated_at,
            ]
        )

    def __repr__(self) -> str:
        """Строковое представление объекта.

        Returns:
            str: Строковое представление
        """
        return (
            f'ServiceTestDTO('
            f'id_={self.id_}, '
            f'name={self.name}, '
            f'email={self.email}, '
            f'resume_id={self.resume_id}, '
            f'created_at={self.created_at}, '
            f'updated_at={self.updated_at}'
            f')'
        )


class TestSchema:
    """Тестовая Pydantic схема."""

    id_: Optional[int] = None
    name: Optional[str] = None
    email: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    __fields__: ClassVar[Dict[str, Mock]] = {
        'id_': Mock(),
        'name': Mock(),
        'email': Mock(),
        'created_at': Mock(),
        'updated_at': Mock(),
    }

    class Config:
        """Конфигурация Pydantic."""

        arbitrary_types_allowed = True

    def __init__(self, **kwargs: Any) -> None:  # noqa ANN401
        """Инициализирует тестовую схему.

        Args:
            **kwargs: Аргументы для инициализации
        """
        self.id_ = kwargs.get('id_')
        self.name = kwargs.get('name')
        self.email = kwargs.get('email')
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')

    def __eq__(self, other: object) -> bool:
        """Проверяет равенство объектов.

        Args:
            other: Другой объект для сравнения

        Returns:
            bool: True если объекты равны, иначе False
        """
        if not isinstance(
            other,
            TestSchema,
        ):
            return False

        return all(
            [
                self.id_ == other.id_,
                self.name == other.name,
                self.email == other.email,
                self.created_at == other.created_at,
                self.updated_at == other.updated_at,
            ]
        )

    def __repr__(self) -> str:
        """Строковое представление объекта.

        Returns:
            str: Строковое представление
        """
        return (
            f'TestSchema('
            f'id_={self.id_}, '
            f'name={self.name}, '
            f'email={self.email}, '
            f'created_at={self.created_at}, '
            f'updated_at={self.updated_at}'
            f')'
        )


class TestRequestSchema:
    """Тестовая RequestSchema."""

    def __init__(self, name: str, email: str) -> None:
        """Инициализирует тестовую схему запроса.

        Args:
            name: Имя
            email: Email
        """
        self.name = name
        self.email = email

    def model_dump(self) -> Dict[str, str]:
        """Конвертирует схему в словарь.

        Returns:
            Dict[str, str]: Словарь с данными схемы
        """
        return {
            'name': self.name,
            'email': self.email,
        }


class TestService(BaseServiceClass[ServiceTestDTO, TestSchema]):
    """Тестовый сервис для проверки базового класса."""

    DTO_CLASS = ServiceTestDTO
    SCHEMA_CLASS = TestSchema


class FakeTestService(TestService):
    """Реализация сервиса для тестирования."""

    def _dto_to_schema(
        self,
        dto: ServiceTestDTO,
    ) -> TestSchema:
        """Конвертирует Dataclass в PydanticSchema.

        Args:
            dto: Объект Dataclass для конвертации

        Returns:
            TestSchema: Конвертированный объект PydanticSchema
        """
        return TestSchema(
            id_=dto.id_,
            name=dto.name,
            email=dto.email,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )

    def _schema_to_dto(
        self,
        schema: TestSchema,
    ) -> ServiceTestDTO:
        """Конвертирует PydanticSchema в Dataclass.

        Args:
            schema: Объект PydanticSchema для конвертации

        Returns:
            ServiceTestDTO: Конвертированный объект Dataclass
        """
        return ServiceTestDTO(
            id_=schema.id_,
            name=schema.name,
            email=schema.email,
            created_at=schema.created_at,
            updated_at=schema.updated_at,
        )
