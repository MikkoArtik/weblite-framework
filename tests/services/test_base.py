"""Модуль для тестов базового сервиса."""

from datetime import datetime, timezone
from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest
from hamcrest import (
    assert_that,
    calling,
    equal_to,
    has_length,
    has_property,
    instance_of,
    is_not,
    none,
    not_none,
    raises,
)

from tests.helpers import (
    ServiceTestDTO,
    TestRequestSchema,
    TestSchema,
    TestService,
)
from weblite_framework.exceptions.repository import RepositoryException
from weblite_framework.services import BaseServiceClass


class TestBaseService:
    """Тесты базового класса BaseService."""

    def test_dto_to_schema_excludes_resume_id(self) -> None:
        """Проверяет, что resume_id исключается из схемы."""
        dt = datetime.now(tz=timezone.utc)
        dto = ServiceTestDTO(
            id_=1,
            name='John',
            email='john@test.com',
            resume_id=999,
            created_at=dt,
            updated_at=dt,
        )

        service = TestService(session=AsyncMock())
        result = service._dto_to_schema(dto)

        assert_that(
            actual_or_assertion=result,
            matcher=has_property('id_', equal_to(1)),
        )
        assert_that(
            actual_or_assertion=result,
            matcher=has_property('name', equal_to('John')),
        )
        assert_that(
            actual_or_assertion=result,
            matcher=has_property('email', equal_to('john@test.com')),
        )
        assert_that(
            actual_or_assertion=result,
            matcher=has_property('created_at', equal_to(dt)),
        )
        assert_that(
            actual_or_assertion=result,
            matcher=has_property('updated_at', equal_to(dt)),
        )
        assert_that(
            actual_or_assertion=cast(object, result),
            matcher=is_not(has_property('resume_id')),  # type: ignore
        )

    def test_dto_to_schema_with_missing_fields(self) -> None:
        """Проверяет работу с DTO где часть полей отсутствует."""
        dto = ServiceTestDTO(id_=2, name='Alice', resume_id=100)

        service = TestService(session=AsyncMock())
        result = service._dto_to_schema(dto)

        assert_that(
            actual_or_assertion=result,
            matcher=has_property('id_', equal_to(2)),
        )
        assert_that(
            actual_or_assertion=result,
            matcher=has_property('name', equal_to('Alice')),
        )
        assert_that(
            actual_or_assertion=cast(object, result),
            matcher=has_property('email', none()),  # type: ignore
        )
        assert_that(
            actual_or_assertion=cast(object, result),
            matcher=has_property('created_at', none()),  # type: ignore
        )
        assert_that(
            actual_or_assertion=cast(object, result),
            matcher=has_property('updated_at', none()),  # type: ignore
        )

    def test_dto_to_schema_with_all_none(self) -> None:
        """Проверяет работу с DTO где все поля None."""
        dto = ServiceTestDTO()
        service = TestService(session=AsyncMock())
        result = service._dto_to_schema(dto)

        assert_that(actual_or_assertion=result.id_, matcher=none())
        assert_that(actual_or_assertion=result.name, matcher=none())
        assert_that(actual_or_assertion=result.email, matcher=none())
        assert_that(actual_or_assertion=result.created_at, matcher=none())
        assert_that(actual_or_assertion=result.updated_at, matcher=none())

    def test_bulk_dto_to_schema_multiple_items(self) -> None:
        """Проверяет массовую конвертацию нескольких DTO."""
        dt = datetime.now(tz=timezone.utc)
        dtos = [
            ServiceTestDTO(
                id_=1, name='User1', email='u1@test.com', created_at=dt
            ),
            ServiceTestDTO(
                id_=2, name='User2', email='u2@test.com', created_at=dt
            ),
            ServiceTestDTO(
                id_=3, name='User3', email='u3@test.com', created_at=dt
            ),
        ]

        service = TestService(session=AsyncMock())
        results = service._bulk_dto_to_schema(dtos)

        assert_that(actual_or_assertion=results, matcher=has_length(3))
        assert_that(
            actual_or_assertion=results[0],
            matcher=has_property('name', equal_to('User1')),
        )
        assert_that(
            actual_or_assertion=results[1],
            matcher=has_property('name', equal_to('User2')),
        )
        assert_that(
            actual_or_assertion=results[2],
            matcher=has_property('name', equal_to('User3')),
        )

    def test_bulk_dto_to_schema_empty_list(self) -> None:
        """Проверяет массовую конвертацию пустого списка."""
        service = TestService(session=AsyncMock())
        results = service._bulk_dto_to_schema([])

        assert_that(actual_or_assertion=results, matcher=equal_to([]))
        assert_that(actual_or_assertion=results, matcher=has_length(0))

    def test_bulk_dto_to_schema_single_item(self) -> None:
        """Проверяет массовую конвертацию одного элемента."""
        dto = ServiceTestDTO(id_=1, name='Single', email='single@test.com')

        service = TestService(session=AsyncMock())
        results = service._bulk_dto_to_schema([dto])

        assert_that(actual_or_assertion=results, matcher=has_length(1))
        assert_that(
            actual_or_assertion=results[0],
            matcher=has_property('name', equal_to('Single')),
        )

    def test_schema_to_dto_with_additional_fields(self) -> None:
        """Проверяет конвертацию RequestSchema в DTO с доп. полями."""
        schema = TestRequestSchema(name='John', email='john@test.com')
        service = TestService(session=AsyncMock())

        result = service._schema_to_dto(
            schema,
            id_=1,
            resume_id=999,
            created_at=None,
            updated_at=None,
        )

        assert_that(
            actual_or_assertion=result,
            matcher=instance_of(ServiceTestDTO),
        )
        assert_that(
            actual_or_assertion=result,
            matcher=has_property('id_', equal_to(1)),
        )
        assert_that(
            actual_or_assertion=result,
            matcher=has_property('name', equal_to('John')),
        )
        assert_that(
            actual_or_assertion=result,
            matcher=has_property('email', equal_to('john@test.com')),
        )
        assert_that(
            actual_or_assertion=result,
            matcher=has_property('resume_id', equal_to(999)),
        )

    def test_schema_to_dto_without_additional_fields(self) -> None:
        """Проверяет конвертацию RequestSchema в DTO без доп. полей."""
        schema = TestRequestSchema(name='Jane', email='jane@test.com')
        service = TestService(session=AsyncMock())
        result = service._schema_to_dto(schema)

        assert_that(actual_or_assertion=result.id_, matcher=none())
        assert_that(
            actual_or_assertion=result.name,
            matcher=equal_to('Jane'),
        )
        assert_that(
            actual_or_assertion=result.email,
            matcher=equal_to('jane@test.com'),
        )
        assert_that(actual_or_assertion=result.resume_id, matcher=none())

    def test_schema_to_dto_overrides_schema_fields(self) -> None:
        """Проверяет что дополнительные поля переопределяют схему."""
        schema = TestRequestSchema(name='Original', email='original@test.com')
        service = TestService(session=AsyncMock())

        result = service._schema_to_dto(schema, name='Overridden', id_=100)

        assert_that(
            actual_or_assertion=result.name,
            matcher=equal_to('Overridden'),
        )
        assert_that(
            actual_or_assertion=result.email,
            matcher=equal_to('original@test.com'),
        )
        assert_that(
            actual_or_assertion=result.id_,
            matcher=equal_to(100),
        )

    def test_bulk_schema_to_dto_multiple_items(self) -> None:
        """Проверяет массовую конвертацию нескольких RequestSchema."""
        schemas = [
            TestRequestSchema(name='User1', email='u1@test.com'),
            TestRequestSchema(name='User2', email='u2@test.com'),
            TestRequestSchema(name='User3', email='u3@test.com'),
        ]
        service = TestService(session=AsyncMock())

        results = service._bulk_schema_to_dto(
            schemas,
            id_=None,
            resume_id=100,
            created_at=datetime.now(tz=timezone.utc),
        )

        assert_that(actual_or_assertion=results, matcher=has_length(3))
        assert_that(
            actual_or_assertion=results[0],
            matcher=has_property('name', equal_to('User1')),
        )
        assert_that(
            actual_or_assertion=results[0],
            matcher=has_property('resume_id', equal_to(100)),
        )
        assert_that(
            actual_or_assertion=results[1],
            matcher=has_property('name', equal_to('User2')),
        )
        assert_that(
            actual_or_assertion=results[2],
            matcher=has_property('name', equal_to('User3')),
        )

    def test_bulk_schema_to_dto_empty_list(self) -> None:
        """Проверяет массовую конвертацию пустого списка."""
        service = TestService(session=AsyncMock())
        results = service._bulk_schema_to_dto([], id_=None)

        assert_that(actual_or_assertion=results, matcher=equal_to([]))
        assert_that(actual_or_assertion=results, matcher=has_length(0))

    async def test_is_user_has_access_success(self) -> None:
        """Проверяет успешную проверку доступа."""
        resume_repo = Mock()
        resume_repo.get_by_id = AsyncMock(return_value=Mock(id=1, user_id=100))

        service = TestService(session=AsyncMock(), resume_repo=resume_repo)
        result = await service._is_user_has_access(resume_id=1, user_id=100)

        assert_that(actual_or_assertion=result, matcher=equal_to(True))
        resume_repo.get_by_id.assert_awaited_once_with(id_=1)

    async def test_is_user_has_access_resume_not_found(self) -> None:
        """Проверяет проверку доступа когда резюме не найдено."""
        resume_repo = Mock()
        resume_repo.get_by_id = AsyncMock(return_value=None)

        service = TestService(session=AsyncMock(), resume_repo=resume_repo)
        result = await service._is_user_has_access(resume_id=999, user_id=100)

        assert_that(actual_or_assertion=result, matcher=equal_to(False))

    async def test_is_user_has_access_wrong_user(self) -> None:
        """Проверяет проверку доступа когда пользователь не владелец."""
        resume_repo = Mock()
        resume_repo.get_by_id = AsyncMock(return_value=Mock(id=1, user_id=100))

        service = TestService(session=AsyncMock(), resume_repo=resume_repo)
        result = await service._is_user_has_access(resume_id=1, user_id=200)

        assert_that(actual_or_assertion=result, matcher=equal_to(False))

    async def test_is_user_has_access_without_resume_repo(self) -> None:
        """Проверяет поведение когда _resume_repo не установлен."""
        service = TestService(session=AsyncMock())
        service._resume_repo = None

        with pytest.raises(
            RepositoryException,
            match='.*Репозиторий резюме не инициализирован.*',
        ):
            await service._is_user_has_access(resume_id=1, user_id=100)

    async def test_full_conversion_cycle(self) -> None:
        """Проверяет полный цикл: RequestSchema → DTO → ResponseSchema."""
        service = TestService(session=AsyncMock())
        request_schema = TestRequestSchema(
            name='Integration Test',
            email='test@integration.com',
        )

        dto = service._schema_to_dto(
            request_schema,
            id_=1,
            resume_id=999,
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )

        response_schema = service._dto_to_schema(dto)

        assert_that(
            actual_or_assertion=dto.name,
            matcher=equal_to('Integration Test'),
        )
        assert_that(
            actual_or_assertion=dto.email,
            matcher=equal_to('test@integration.com'),
        )
        assert_that(
            actual_or_assertion=dto.resume_id,
            matcher=equal_to(999),
        )

        assert_that(
            actual_or_assertion=response_schema.name,
            matcher=equal_to('Integration Test'),
        )
        assert_that(
            actual_or_assertion=response_schema.email,
            matcher=equal_to('test@integration.com'),
        )
        assert_that(
            actual_or_assertion=cast(object, response_schema),
            matcher=is_not(has_property('resume_id')),  # type: ignore
        )

    def test_bulk_conversion_cycle(self) -> None:
        """Проверяет полный цикл массовой конвертации."""
        service = TestService(session=AsyncMock())
        request_schemas = [
            TestRequestSchema(name='User1', email='u1@test.com'),
            TestRequestSchema(name='User2', email='u2@test.com'),
        ]

        dtos = service._bulk_schema_to_dto(
            request_schemas,
            id_=None,
            resume_id=100,
        )

        response_schemas = service._bulk_dto_to_schema(dtos)

        assert_that(
            actual_or_assertion=response_schemas,
            matcher=has_length(2),
        )
        assert_that(
            actual_or_assertion=response_schemas[0].name,
            matcher=equal_to('User1'),
        )
        assert_that(
            actual_or_assertion=response_schemas[1].name,
            matcher=equal_to('User2'),
        )
        assert_that(
            actual_or_assertion=cast(object, response_schemas[0]),
            matcher=is_not(has_property('resume_id')),  # type: ignore
        )
        assert_that(
            actual_or_assertion=cast(object, response_schemas[1]),
            matcher=is_not(has_property('resume_id')),  # type: ignore
        )

    def test_valid_service_with_correct_classes(self) -> None:
        """Проверяет создание валидного сервиса с правильными классами."""

        class ValidService(TestService):
            pass

        service = ValidService(session=AsyncMock())

        assert_that(
            actual_or_assertion=service.DTO_CLASS,
            matcher=equal_to(ServiceTestDTO),
        )
        assert_that(
            actual_or_assertion=service.SCHEMA_CLASS,
            matcher=equal_to(TestSchema),
        )
        assert_that(actual_or_assertion=service._session, matcher=not_none())

    def test_valid_service_with_direct_classes(self) -> None:
        """Проверяет создание валидного сервиса с прямым указанием классов."""

        class ValidService(BaseServiceClass[ServiceTestDTO, TestSchema]):
            DTO_CLASS = ServiceTestDTO
            SCHEMA_CLASS = TestSchema

        service = ValidService(session=AsyncMock())

        assert_that(
            actual_or_assertion=service.DTO_CLASS,
            matcher=equal_to(ServiceTestDTO),
        )
        assert_that(
            actual_or_assertion=service.SCHEMA_CLASS,
            matcher=equal_to(TestSchema),
        )
        assert_that(actual_or_assertion=service._session, matcher=not_none())

    def test_schema_to_dto_with_invalid_schema(self) -> None:
        """Проверяет обработку схемы без model_dump."""

        class InvalidSchema:
            name: str = ''
            email: str = ''

        service = TestService(session=AsyncMock())

        assert_that(
            calling(service._schema_to_dto).with_args(InvalidSchema()),
            raises(
                RepositoryException,
                pattern='.*Схема должна иметь метод model_dump.*',
            ),
        )

    def test_service_creation_without_classes(self) -> None:
        """Проверяет создание сервиса без определения классов."""

        class InvalidService(BaseServiceClass):  # type: ignore
            pass

        service = InvalidService(session=AsyncMock())

        assert_that(
            actual_or_assertion=service,
            matcher=instance_of(InvalidService),
        )
        assert_that(
            actual_or_assertion=service,
            matcher=instance_of(BaseServiceClass),
        )

        dto_class = getattr(service, 'DTO_CLASS', None)
        schema_class = getattr(service, 'SCHEMA_CLASS', None)

        assert_that(actual_or_assertion=dto_class, matcher=none())
        assert_that(actual_or_assertion=schema_class, matcher=none())
        assert_that(actual_or_assertion=service._session, matcher=not_none())

    def test_service_with_partial_classes(self) -> None:
        """Проверяет создание сервиса только с одним из классов."""

        class PartialService(BaseServiceClass[ServiceTestDTO, TestSchema]):
            DTO_CLASS = ServiceTestDTO

        service = PartialService(session=AsyncMock())

        assert_that(
            actual_or_assertion=service.DTO_CLASS,
            matcher=equal_to(ServiceTestDTO),
        )

        schema_class = getattr(service, 'SCHEMA_CLASS', None)
        assert_that(actual_or_assertion=schema_class, matcher=none())

    def test_service_creation_with_wrong_dto_class(self) -> None:
        """Проверяет создание сервиса с неправильным DTO_CLASS."""
        from tests.helpers import TestDTO as RepositoryTestDTO

        class WrongService(BaseServiceClass[ServiceTestDTO, TestSchema]):
            DTO_CLASS = RepositoryTestDTO  # type: ignore[assignment]
            SCHEMA_CLASS = TestSchema

        service = WrongService(session=AsyncMock())

        assert_that(
            actual_or_assertion=service.DTO_CLASS,
            matcher=equal_to(RepositoryTestDTO),
        )
        assert_that(
            actual_or_assertion=service.SCHEMA_CLASS,
            matcher=equal_to(TestSchema),
        )

    def test_dto_class_attribute_exists(self) -> None:
        """Проверяет, что у сервиса есть атрибут DTO_CLASS."""
        service = TestService(session=AsyncMock())

        assert_that(
            actual_or_assertion=service,
            matcher=has_property('DTO_CLASS'),
        )
        assert_that(
            actual_or_assertion=service,
            matcher=has_property('SCHEMA_CLASS'),
        )
        assert_that(
            actual_or_assertion=service.DTO_CLASS,
            matcher=equal_to(ServiceTestDTO),
        )
        assert_that(
            actual_or_assertion=service.SCHEMA_CLASS,
            matcher=equal_to(TestSchema),
        )

    def test_service_instance_creation(self) -> None:
        """Проверяет базовое создание экземпляра сервиса."""
        session = AsyncMock()
        service = TestService(session=session)

        assert_that(
            actual_or_assertion=service,
            matcher=instance_of(TestService),
        )
        assert_that(
            actual_or_assertion=service,
            matcher=instance_of(BaseServiceClass),
        )
        assert_that(
            actual_or_assertion=service._session,
            matcher=equal_to(session),
        )
        assert_that(actual_or_assertion=service._resume_repo, matcher=none())

    def test_service_instance_creation_with_resume_repo(self) -> None:
        """Проверяет создание экземпляра сервиса с resume_repo."""
        session = AsyncMock()
        resume_repo = Mock()
        service = TestService(session=session, resume_repo=resume_repo)

        assert_that(
            actual_or_assertion=service._session,
            matcher=equal_to(session),
        )
        assert_that(
            actual_or_assertion=service._resume_repo,
            matcher=equal_to(resume_repo),
        )
