"""Тесты для базового сервиса."""

from unittest.mock import AsyncMock, Mock

import pytest
from hamcrest import assert_that, equal_to, is_

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
        класса, наследующегося от BaseServiceClass, с заглушками
        в абстрактных методах, возникает NotImplementedError
        при вызове этих методов.
        """
        session = AsyncMock()

        class InvalidService(BaseServiceClass[ServiceTestDTO, TestSchema]):
            """Класс с заглушками в абстрактных методах."""

            def _dto_to_schema(self, dto: ServiceTestDTO) -> TestSchema:
                """Заглушка, которая выбрасывает NotImplementedError."""
                raise NotImplementedError

            def _schema_to_dto(self, schema: TestSchema) -> ServiceTestDTO:
                """Заглушка, которая выбрасывает NotImplementedError."""
                raise NotImplementedError

        service = InvalidService(session=session)

        dto = ServiceTestDTO(id_=1, name='test', email='test@example.com')

        with pytest.raises(NotImplementedError):
            service._dto_to_schema(dto)

        with pytest.raises(NotImplementedError):
            schema = TestSchema(id_=1, name='test', email='test@example.com')
            service._schema_to_dto(schema)

    def test_dto_to_schema_conversion(
        self,
    ) -> None:
        """Проверка конвертации DTO в схему.

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
            actual_or_assertion=isinstance(dto, ServiceTestDTO),
            matcher=is_(True),
            reason='dto должен быть экземпляром ServiceTestDTO',
        )
        assert_that(
            actual_or_assertion=isinstance(schema, TestSchema),
            matcher=is_(True),
            reason='schema должен быть экземпляром TestSchema',
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
        """Проверка конвертации схемы в DTO.

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
            actual_or_assertion=isinstance(schema, TestSchema),
            matcher=is_(True),
            reason='schema должен быть экземпляром TestSchema',
        )
        assert_that(
            actual_or_assertion=isinstance(dto, ServiceTestDTO),
            matcher=is_(True),
            reason='dto должен быть экземпляром ServiceTestDTO',
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
        """Проверка массовой конвертации DTO в схемы.

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
        """Проверка массовой конвертации схем в DTO.

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

    async def test_is_user_has_access_when_entity_exists_and_belongs_to_user(
        self,
    ) -> None:
        """Проверка принадлежности сущности пользователю.

        Данный тест проверяет, что метод возвращает True,
        когда сущность существует и принадлежит пользователю.
        """
        session = AsyncMock()
        service = TestConcreteService(
            session=session,
        )

        mock_repository = Mock()
        mock_entity = Mock()
        mock_entity.user_id = 123

        mock_repository.get_by_id = AsyncMock(
            return_value=mock_entity,
        )

        result = await service._is_user_has_access(
            repository=mock_repository,
            entity_id=1,
            entity_field_name='user_id',
            expected_value=123,
        )

        assert_that(
            actual_or_assertion=result,
            matcher=is_(True),
        )
        mock_repository.get_by_id.assert_called_once_with(
            id_=1,
        )

    async def test_is_user_has_access_another_user_entity(
        self,
    ) -> None:
        """Проверка доступа к чужой сущности."""
        session = AsyncMock()
        service = TestConcreteService(
            session=session,
        )

        mock_repository = Mock()
        mock_entity = Mock()
        mock_entity.user_id = 456

        mock_repository.get_by_id = AsyncMock(
            return_value=mock_entity,
        )

        result = await service._is_user_has_access(
            repository=mock_repository,
            entity_id=1,
            entity_field_name='user_id',
            expected_value=123,
        )

        assert_that(
            actual_or_assertion=result,
            matcher=is_(False),
        )
        mock_repository.get_by_id.assert_called_once_with(
            id_=1,
        )

    async def test_is_user_has_access_when_entity_not_exists(
        self,
    ) -> None:
        """Проверка доступа к несуществующей сущности.

        Данный тест проверяет, что метод возвращает False,
        когда сущность не существует.
        """
        session = AsyncMock()
        service = TestConcreteService(
            session=session,
        )

        mock_repository = Mock()
        mock_repository.get_by_id = AsyncMock(
            return_value=None,
        )

        result = await service._is_user_has_access(
            repository=mock_repository,
            entity_id=999,
            entity_field_name='user_id',
            expected_value=123,
        )

        assert_that(
            actual_or_assertion=result,
            matcher=is_(False),
        )
        mock_repository.get_by_id.assert_called_once_with(
            id_=999,
        )

    async def test_is_user_has_access_with_entity_none(
        self,
    ) -> None:
        """Проверка доступа когда entity равен None.

        Данный тест проверяет, что метод возвращает False,
        когда entity равен None.
        """
        session = AsyncMock()
        service = TestConcreteService(
            session=session,
        )

        mock_repository = Mock()
        mock_repository.get_by_id = AsyncMock(
            return_value=None,
        )

        result = await service._is_user_has_access(
            repository=mock_repository,
            entity_id=1,
            entity_field_name='user_id',
            expected_value=123,
        )

        assert_that(
            actual_or_assertion=result,
            matcher=is_(False),
        )
        mock_repository.get_by_id.assert_called_once_with(
            id_=1,
        )

    async def test_is_user_has_access_entity_has_no_field_attribute(
        self,
    ) -> None:
        """Проверка доступа когда у entity нет проверяемого атрибута.

        Данный тест проверяет, что метод возвращает False,
        когда у объекта entity нет проверяемого атрибута.
        """
        session = AsyncMock()
        service = TestConcreteService(
            session=session,
        )

        mock_repository = Mock()
        mock_entity = object()

        mock_repository.get_by_id = AsyncMock(
            return_value=mock_entity,
        )

        result = await service._is_user_has_access(
            repository=mock_repository,
            entity_id=1,
            entity_field_name='user_id',
            expected_value=123,
        )

        assert_that(
            actual_or_assertion=result,
            matcher=is_(False),
        )
        mock_repository.get_by_id.assert_called_once_with(
            id_=1,
        )

    async def test_is_user_has_access_field_value_is_none(
        self,
    ) -> None:
        """Проверка когда значение поля равно None.

        Данный тест проверяет, что метод возвращает False,
        когда значение поля равно None.
        """
        session = AsyncMock()
        service = TestConcreteService(
            session=session,
        )

        mock_repository = Mock()
        mock_entity = Mock()
        mock_entity.user_id = None

        mock_repository.get_by_id = AsyncMock(
            return_value=mock_entity,
        )

        result = await service._is_user_has_access(
            repository=mock_repository,
            entity_id=1,
            entity_field_name='user_id',
            expected_value=123,
        )

        assert_that(
            actual_or_assertion=result,
            matcher=is_(False),
        )
        mock_repository.get_by_id.assert_called_once_with(
            id_=1,
        )

    async def test_is_user_has_access_with_different_field_name(
        self,
    ) -> None:
        """Проверка принадлежности с другим именем поля.

        Данный тест проверяет работу метода с произвольным именем поля.
        """
        session = AsyncMock()
        service = TestConcreteService(
            session=session,
        )

        mock_repository = Mock()
        mock_entity = Mock()
        mock_entity.owner_id = 789

        mock_repository.get_by_id = AsyncMock(
            return_value=mock_entity,
        )

        result = await service._is_user_has_access(
            repository=mock_repository,
            entity_id=1,
            entity_field_name='owner_id',
            expected_value=789,
        )

        assert_that(
            actual_or_assertion=result,
            matcher=is_(True),
        )
        mock_repository.get_by_id.assert_called_once_with(
            id_=1,
        )

    async def test_is_user_has_access_with_different_field_value_not_equal(
        self,
    ) -> None:
        """Проверка принадлежности когда значение поля не совпадает.

        Данный тест проверяет, что метод возвращает False,
        когда значение поля не совпадает с ожидаемым.
        """
        session = AsyncMock()
        service = TestConcreteService(
            session=session,
        )

        mock_repository = Mock()
        mock_entity = Mock()
        mock_entity.owner_id = 789

        mock_repository.get_by_id = AsyncMock(
            return_value=mock_entity,
        )

        result = await service._is_user_has_access(
            repository=mock_repository,
            entity_id=1,
            entity_field_name='owner_id',
            expected_value=999,
        )

        assert_that(
            actual_or_assertion=result,
            matcher=is_(False),
        )
        mock_repository.get_by_id.assert_called_once_with(
            id_=1,
        )

    async def test_is_user_has_access_repository_no_get_by_id_method(
        self,
    ) -> None:
        """Проверка когда у репозитория нет метода get_by_id.

        Данный тест проверяет, что метод возвращает False,
        когда у репозитория нет метода get_by_id.
        """
        session = AsyncMock()
        service = TestConcreteService(
            session=session,
        )

        mock_repository = Mock()

        result = await service._is_user_has_access(
            repository=mock_repository,
            entity_id=1,
            entity_field_name='user_id',
            expected_value=123,
        )

        assert_that(
            actual_or_assertion=result,
            matcher=is_(False),
        )
