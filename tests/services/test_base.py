"""Тесты для базового сервиса."""

from unittest.mock import AsyncMock

import pytest
from hamcrest import assert_that, equal_to, instance_of, is_

from tests.conftest import TestConcreteService
from tests.helpers import ServiceTestDTO, TestSchema
from weblite_framework.services.base import BaseServiceClass


class TestBaseServiceClass:
    """Класс тестов базового сервиса."""

    def test_initialization(
        self,
    ) -> None:
        """Проверка инициализации базового сервиса.

        Данный тест проверяет корректное присвоение сессии
        при создании экземпляра сервиса.
        """
        session = AsyncMock()
        service = TestConcreteService(
            session=session,
        )

        assert_that(
            actual_or_assertion=service._session,
            matcher=equal_to(obj=session),
        )

    def test_abstract_methods_not_implemented(
        self,
    ) -> None:
        """Проверка, что абстрактные методы не реализованы.

        Данный тест проверяет, что BaseServiceClass является абстрактным.
        """
        import inspect

        assert_that(
            actual_or_assertion=inspect.isabstract(BaseServiceClass),
            matcher=is_(True),
        )
        assert_that(
            actual_or_assertion=hasattr(
                BaseServiceClass,
                '__abstractmethods__',
            ),
            matcher=is_(True),
        )
        assert_that(
            actual_or_assertion=len(BaseServiceClass.__abstractmethods__),
            matcher=equal_to(obj=2),
        )

    def test_concrete_class_without_abstract_methods(
        self,
    ) -> None:
        """Проверка создания класса без абстрактных методов.

        Данный тест проверяет, что при попытке создать экземпляр
        класса, просто наследующегося от BaseServiceClass,
        без переопределения абстрактных методов, возникает TypeError.
        """
        session = AsyncMock()

        with pytest.raises(TypeError):

            class InvalidService(BaseServiceClass[ServiceTestDTO, TestSchema]):
                pass

            InvalidService(session=session)  # type: ignore

    def test_dto_to_schema_conversion(
        self,
    ) -> None:
        """Проверка конвертации Dataclass в PydanticSchema.

        Данный тест проверяет корректность работы метода _dto_to_schema.
        """
        session = AsyncMock()
        service = TestConcreteService(
            session=session,
        )

        dto = ServiceTestDTO(
            id_=1,
            name='Test Name',
            email='test@example.com',
        )

        schema = service._dto_to_schema(dto=dto)

        assert_that(
            actual_or_assertion=schema,
            matcher=instance_of(atype=TestSchema),
        )
        assert_that(
            actual_or_assertion=schema.id_,
            matcher=equal_to(obj=dto.id_),
        )
        assert_that(
            actual_or_assertion=schema.name,
            matcher=equal_to(obj=dto.name),
        )
        assert_that(
            actual_or_assertion=schema.email,
            matcher=equal_to(obj=dto.email),
        )

    def test_schema_to_dto_conversion(
        self,
    ) -> None:
        """Проверка конвертации PydanticSchema в Dataclass.

        Данный тест проверяет корректность работы метода _schema_to_dto.
        """
        session = AsyncMock()
        service = TestConcreteService(
            session=session,
        )

        schema = TestSchema(
            id_=2,
            name='Another Name',
            email='another@example.com',
        )

        dto = service._schema_to_dto(schema=schema)

        assert_that(
            actual_or_assertion=dto,
            matcher=instance_of(atype=ServiceTestDTO),
        )
        assert_that(
            actual_or_assertion=dto.id_,
            matcher=equal_to(obj=schema.id_),
        )
        assert_that(
            actual_or_assertion=dto.name,
            matcher=equal_to(obj=schema.name),
        )
        assert_that(
            actual_or_assertion=dto.email,
            matcher=equal_to(obj=schema.email),
        )

    def test_bulk_dto_to_schema_conversion(
        self,
    ) -> None:
        """Проверка массовой конвертации Dataclass в PydanticSchema.

        Данный тест проверяет корректность работы метода _bulk_dto_to_schema.
        """
        session = AsyncMock()
        service = TestConcreteService(
            session=session,
        )

        dtos = [
            ServiceTestDTO(
                id_=1,
                name='First',
                email='first@example.com',
            ),
            ServiceTestDTO(
                id_=2,
                name='Second',
                email='second@example.com',
            ),
            ServiceTestDTO(
                id_=3,
                name='Third',
                email='third@example.com',
            ),
        ]

        schemas = service._bulk_dto_to_schema(dtos=dtos)

        assert_that(
            actual_or_assertion=len(schemas),
            matcher=equal_to(obj=len(dtos)),
        )

        for i, (dto, schema) in enumerate(
            zip(dtos, schemas, strict=False),
        ):
            assert_that(
                actual_or_assertion=schema.id_,
                matcher=equal_to(obj=dto.id_),
                reason=f'DTO {i} id mismatch',
            )
            assert_that(
                actual_or_assertion=schema.name,
                matcher=equal_to(obj=dto.name),
                reason=f'DTO {i} name mismatch',
            )
            assert_that(
                actual_or_assertion=schema.email,
                matcher=equal_to(obj=dto.email),
                reason=f'DTO {i} email mismatch',
            )

    def test_bulk_schema_to_dto_conversion(
        self,
    ) -> None:
        """Проверка массовой конвертации PydanticSchema в Dataclass.

        Данный тест проверяет корректность работы метода _bulk_schema_to_dto.
        """
        session = AsyncMock()
        service = TestConcreteService(
            session=session,
        )

        schemas = [
            TestSchema(
                id_=1,
                name='First',
                email='first@example.com',
            ),
            TestSchema(
                id_=2,
                name='Second',
                email='second@example.com',
            ),
            TestSchema(
                id_=3,
                name='Third',
                email='third@example.com',
            ),
        ]

        dtos = service._bulk_schema_to_dto(schemas=schemas)

        assert_that(
            actual_or_assertion=len(dtos),
            matcher=equal_to(obj=len(schemas)),
        )

        for i, (schema, dto) in enumerate(
            zip(schemas, dtos, strict=False),
        ):
            assert_that(
                actual_or_assertion=dto.id_,
                matcher=equal_to(obj=schema.id_),
                reason=f'Schema {i} id mismatch',
            )
            assert_that(
                actual_or_assertion=dto.name,
                matcher=equal_to(obj=schema.name),
                reason=f'Schema {i} name mismatch',
            )
            assert_that(
                actual_or_assertion=dto.email,
                matcher=equal_to(obj=schema.email),
                reason=f'Schema {i} email mismatch',
            )
