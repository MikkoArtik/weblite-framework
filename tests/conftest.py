"""Фикстуры для тестов weblite-framework."""

import pytest

from tests.helpers import (
    ServiceTestDTO,
    TestDTO,
    TestModel,
    TestSchema,
    TestService,
)


@pytest.fixture(scope='function')
def test_dto() -> TestDTO:
    """Фикстура для тестового DTO."""
    return TestDTO(id_=1, name='test')


@pytest.fixture(scope='function')
def test_model() -> TestModel:
    """Фикстура для тестовой модели."""
    return TestModel(id_=1, name='test')


class TestConcreteService(TestService):
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
